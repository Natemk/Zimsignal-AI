from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from fastapi import HTTPException
from cryptography.hazmat.primitives.asymmetric import rsa

import api.dependencies as dependencies
from api.auth import oidc


@pytest.mark.asyncio
async def test_context_requires_bearer_token():
    with pytest.raises(HTTPException) as error:
        await dependencies.get_current_context(None, None)

    assert error.value.status_code == 401


@pytest.mark.asyncio
async def test_context_uses_verified_claims_and_membership(monkeypatch):
    async def verify_token(token: str) -> dict[str, str]:
        assert token == "verified-token"
        return {"sub": "user-123", "organisation_id": "org-456"}

    async def get_membership(user_id: str, organisation_id: str) -> dict:
        assert (user_id, organisation_id) == ("user-123", "org-456")
        return {
            "role": "farmer",
            "subscription": "free",
            "connected_services": ("whatsapp",),
        }

    monkeypatch.setattr(dependencies, "verify_oidc_token", verify_token)
    monkeypatch.setattr(dependencies, "get_organisation_membership", get_membership)

    context = await dependencies.get_current_context("Bearer verified-token", None)

    assert context.user_id == "user-123"
    assert context.organisation_id == "org-456"
    assert context.role == "farmer"
    assert context.subscription == "free"
    assert context.connected_services == ("whatsapp",)


@pytest.mark.asyncio
async def test_context_rejects_non_member(monkeypatch):
    async def verify_token(token: str) -> dict[str, str]:
        return {"sub": "user-123", "organisation_id": "org-456"}

    async def get_membership(user_id: str, organisation_id: str) -> None:
        return None

    monkeypatch.setattr(dependencies, "verify_oidc_token", verify_token)
    monkeypatch.setattr(dependencies, "get_organisation_membership", get_membership)

    with pytest.raises(HTTPException) as error:
        await dependencies.get_current_context("Bearer verified-token", None)

    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_selected_organisation_requires_membership(monkeypatch):
    async def verify_token(token: str) -> dict[str, str]:
        return {"sub": "user-123", "organisation_id": "org-home"}

    async def get_membership(user_id: str, organisation_id: str) -> None:
        assert (user_id, organisation_id) == ("user-123", "org-selected")
        return None

    monkeypatch.setattr(dependencies, "verify_oidc_token", verify_token)
    monkeypatch.setattr(dependencies, "get_organisation_membership", get_membership)

    with pytest.raises(HTTPException) as error:
        await dependencies.get_current_context(
            "bEaReR verified-token", "org-selected"
        )

    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_oidc_verifier_accepts_valid_signature_and_rejects_tampering(
    monkeypatch,
):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = jwt.encode(
        {
            "sub": "user-123",
            "iss": "https://identity.example.test/",
            "aud": "zimsignal-api",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
    )
    jwks_client = SimpleNamespace(
        get_signing_key_from_jwt=lambda _: SimpleNamespace(key=private_key.public_key())
    )
    monkeypatch.setattr(oidc, "_jwks_client", lambda _: jwks_client)
    monkeypatch.setenv("OIDC_ISSUER", "https://identity.example.test/")
    monkeypatch.setenv("OIDC_AUDIENCE", "zimsignal-api")
    monkeypatch.setenv("OIDC_JWKS_URL", "https://identity.example.test/.well-known/jwks.json")

    claims = await oidc.verify_oidc_token(token)
    assert claims["sub"] == "user-123"

    header, payload, signature = token.split(".")
    changed_signature = ("A" if signature[0] != "A" else "B") + signature[1:]
    with pytest.raises(HTTPException) as error:
        await oidc.verify_oidc_token(f"{header}.{payload}.{changed_signature}")

    assert error.value.status_code == 401