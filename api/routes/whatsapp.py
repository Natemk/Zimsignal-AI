"""
api/routes/whatsapp.py

WhatsApp Cloud API channel for ZimSignal AI.

Flow:  Meta POST -> verify X-Hub-Signature-256 on RAW bytes -> 200 immediately
       -> background task: dedupe (Redis SET NX) -> resolve identity (wa_id -> org/user)
       -> supervisor.ainvoke(thread_id=whatsapp:{org}:{user}:{wa_id}) -> Graph API reply

Required env: WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_VERIFY_TOKEN, META_APP_SECRET,
              WHATSAPP_ACCESS_TOKEN, META_GRAPH_VERSION (optional), REDIS_URL (optional)
"""
import hashlib
import hmac
import json
import logging
import os
import time

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from api.dependencies import ZimSignalContext, get_supervisor_app

log = logging.getLogger("zimsignal.whatsapp")
router = APIRouter()

WINDOW_SECONDS = 24 * 3600


# --------------------------------------------------------------------- config
def _env(name: str) -> str:
    v = (os.getenv(name) or "").strip()
    if not v:
        raise RuntimeError(f"{name} is not set")
    return v


def _token() -> str:
    """Read at call time, so a missing/rotated token fails loudly instead of sending 'null'."""
    t = _env("WHATSAPP_ACCESS_TOKEN").strip('"').strip("'")
    return t[7:].strip() if t.lower().startswith("bearer ") else t


def _graph_url(path: str) -> str:
    return f"https://graph.facebook.com/{os.getenv('META_GRAPH_VERSION', 'v23.0')}/{path}"


# --------------------------------------------------------------------- KV: Redis with in-memory fallback
class KV:
    def __init__(self) -> None:
        self._r = None
        self._tried = False
        self._mem: dict[str, tuple[str, float]] = {}

    async def _redis(self):
        if self._tried:
            return self._r
        self._tried = True
        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                                  decode_responses=True)
            await r.ping()
            self._r = r
            log.info("Redis connected")
        except Exception as exc:  # offline fallback
            log.warning("Redis unavailable (%s); using in-memory fallback (NOT multi-worker safe)", exc)
        return self._r

    def _purge(self) -> None:
        now = time.time()
        for k in [k for k, (_, exp) in self._mem.items() if exp < now]:
            del self._mem[k]

    async def set_nx(self, key: str, ttl: int) -> bool:
        """True if the key was newly created (first time seen)."""
        r = await self._redis()
        if r:
            try:
                return bool(await r.set(key, "1", nx=True, ex=ttl))
            except Exception as exc:
                log.warning("Redis set_nx failed: %s", exc)
        self._purge()
        if key in self._mem:
            return False
        self._mem[key] = ("1", time.time() + ttl)
        return True

    async def set(self, key: str, val: str, ttl: int) -> None:
        r = await self._redis()
        if r:
            try:
                await r.set(key, val, ex=ttl)
                return
            except Exception as exc:
                log.warning("Redis set failed: %s", exc)
        self._mem[key] = (val, time.time() + ttl)

    async def get(self, key: str) -> str | None:
        r = await self._redis()
        if r:
            try:
                return await r.get(key)
            except Exception as exc:
                log.warning("Redis get failed: %s", exc)
        self._purge()
        item = self._mem.get(key)
        return item[0] if item else None


kv = KV()


# --------------------------------------------------------------------- identity / account linking
# DEV ONLY: replace with a Postgres table `whatsapp_identities(wa_id PK, org_id, user_id, linked_at)`.
_IDENTITIES: dict[str, tuple[str, str]] = {}
_dev_wa = os.getenv("DEV_WA_ID")  # your own number, digits only, e.g. 263771234567
if _dev_wa:
    _IDENTITIES[_dev_wa] = ("org_zim_01", os.getenv("DEV_USER_ID", "user_dev_01"))


async def resolve_identity(wa_id: str) -> tuple[str, str] | None:
    return _IDENTITIES.get(wa_id)


async def create_link_code(org_id: str, user_id: str) -> str:
    """Call from the authenticated web app ('Connect WhatsApp'); show the code to the user."""
    code = f"{int.from_bytes(os.urandom(3), 'big') % 1_000_000:06d}"
    await kv.set(f"wa:link:{code}", f"{org_id}|{user_id}", ttl=600)
    return code


async def try_link(wa_id: str, code: str) -> str:
    val = await kv.get(f"wa:link:{code}")
    if not val:
        return "That code is invalid or expired. Generate a new one in the ZimSignal app."
    org_id, user_id = val.split("|", 1)
    _IDENTITIES[wa_id] = (org_id, user_id)  # persist to DB in production
    return "WhatsApp linked to your ZimSignal account. Ask me anything about your farm or market."


# --------------------------------------------------------------------- webhook security
def verify_signature(raw_body: bytes, header: str | None) -> None:
    if not header or not header.startswith("sha256="):
        raise HTTPException(status_code=403, detail="missing signature")
    expected = hmac.new(_env("META_APP_SECRET").encode(), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, header.split("=", 1)[1]):
        raise HTTPException(status_code=403, detail="bad signature")


# --------------------------------------------------------------------- parsing
def parse_inbound(payload: dict):
    """Yield one dict per inbound user message. Status callbacks (sent/delivered/read) are ignored."""
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "messages":
                continue
            value = change.get("value", {})
            names = {c.get("wa_id"): (c.get("profile") or {}).get("name")
                     for c in value.get("contacts", [])}
            for m in value.get("messages", []):
                mtype = m.get("type")
                text = None
                if mtype == "text":
                    text = (m.get("text") or {}).get("body")
                elif mtype == "interactive":
                    inter = m.get("interactive") or {}
                    reply = inter.get("button_reply") or inter.get("list_reply") or {}
                    text = reply.get("title")
                wa_id = m.get("from")
                yield {"message_id": m.get("id"), "wa_id": wa_id, "type": mtype,
                       "text": text, "name": names.get(wa_id), "timestamp": m.get("timestamp")}


# --------------------------------------------------------------------- outbound
async def _post_graph(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(_graph_url(f"{_env('WHATSAPP_PHONE_NUMBER_ID')}/messages"),
                              headers={"Authorization": f"Bearer {_token()}"}, json=payload)
    if r.status_code >= 400:
        log.error("Graph send failed %s: %s", r.status_code, r.text[:500])
        r.raise_for_status()
    return r.json()


async def in_service_window(wa_id: str) -> bool:
    ts = await kv.get(f"wa:last_inbound:{wa_id}")
    return bool(ts) and (time.time() - float(ts)) < WINDOW_SECONDS


async def send_text(to: str, body: str) -> None:
    """Free-form text is only allowed within 24h of the user's last inbound message."""
    if not await in_service_window(to):
        raise RuntimeError("Outside 24h customer-service window: use send_template()")
    for i in range(0, len(body), 3800):  # WhatsApp text limit is 4096 chars
        await _post_graph({"messaging_product": "whatsapp", "to": to, "type": "text",
                           "text": {"body": body[i:i + 3800], "preview_url": False}})


async def send_template(to: str, name: str, lang: str = "en", components: list | None = None) -> None:
    """Business-initiated messages (alerts) must use an APPROVED template and user opt-in."""
    tpl: dict = {"name": name, "language": {"code": lang}}
    if components:
        tpl["components"] = components
    await _post_graph({"messaging_product": "whatsapp", "to": to, "type": "template", "template": tpl})


# --------------------------------------------------------------------- core processing
def final_text(result: dict) -> str:
    content = result["messages"][-1].content
    if isinstance(content, list):  # content blocks
        content = "".join(b.get("text", "") for b in content if isinstance(b, dict))
    return content or "I could not produce an answer."


async def process_message(msg: dict) -> None:
    wa_id, mid = msg["wa_id"], msg["message_id"]

    # 1. Idempotency: Meta retries on slow/non-200 responses
    if not await kv.set_nx(f"wa:seen:{mid}", ttl=2 * 86400):
        log.info("duplicate webhook %s ignored", mid)
        return

    # 2. Open/refresh the 24h service window
    await kv.set(f"wa:last_inbound:{wa_id}", str(time.time()), ttl=8 * 86400)

    text = (msg["text"] or "").strip()
    identity = await resolve_identity(wa_id)

    # 3. Explicit account linking (never assume phone number == web account)
    if not identity:
        if text.upper().startswith("LINK "):
            reply = await try_link(wa_id, text[5:].strip())
        else:
            reply = ("Welcome to ZimSignal AI. To link this number, open Settings > Connect "
                     "WhatsApp in the app and send: LINK <your code>")
        await send_text(wa_id, reply)
        return

    if not text:
        await send_text(wa_id, "I can only read text messages for now.")
        return

    org_id, user_id = identity
    thread_id = f"whatsapp:{org_id}:{user_id}:{wa_id}"

    # 4. Supervisor invocation. Load role/subscription/connected_services from the DB in production.
    ctx = ZimSignalContext(user_id=user_id, organisation_id=org_id, role="farmer",
                           subscription="free", connected_services=("whatsapp",))
    try:
        result = await get_supervisor_app().ainvoke(
            {"messages": [{"role": "user", "content": text}]},
            config={"configurable": {"thread_id": thread_id}},
            context=ctx,
        )
        if result.get("__interrupt__"):
            # HITL pause: approvals happen in the authenticated web app, not over WhatsApp (MVP).
            answer = "This action needs your approval. Please open ZimSignal AI to review and approve it."
        else:
            answer = final_text(result)
    except Exception:
        log.exception("supervisor failed for thread %s", thread_id)
        answer = "Sorry, something went wrong on our side. Please try again shortly."

    try:
        await send_text(wa_id, answer)
    except Exception:
        log.exception("outbound send failed for %s", wa_id)


# --------------------------------------------------------------------- routes
@router.get("/webhook/whatsapp")
async def verify_webhook(mode: str | None = Query(None, alias="hub.mode"),
                         token: str | None = Query(None, alias="hub.verify_token"),
                         challenge: str | None = Query(None, alias="hub.challenge")):
    if mode == "subscribe" and token and hmac.compare_digest(token, _env("WHATSAPP_VERIFY_TOKEN")):
        return PlainTextResponse(challenge or "")
    raise HTTPException(status_code=403, detail="verification failed")


@router.post("/webhook/whatsapp")
async def receive_webhook(request: Request, background: BackgroundTasks):
    raw = await request.body()                      # RAW bytes: signature is computed over these
    verify_signature(raw, request.headers.get("x-hub-signature-256"))
    payload = json.loads(raw)
    log.info("webhook received: %d bytes, object=%s", len(raw), payload.get("object"))
    for msg in parse_inbound(payload):
        background.add_task(process_message, msg)   # respond 200 fast; work happens after
    return {"status": "ok"}