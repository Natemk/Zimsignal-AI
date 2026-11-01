"""Agent chat route."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, ConfigDict, Field

from api.dependencies import get_current_context, get_signal_engine, get_supervisor_app
from governance.audit import SignalEngine
from orchestration.state import ZimSignalContext

router = APIRouter()


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., description="User prompt.")
    thread_id: str | None = Field(
        default=None, max_length=128, description="Client conversation identifier."
    )


@router.post("/chat", tags=["Agent Interaction"])
async def chat_endpoint(
    payload: ChatRequest,
    context: ZimSignalContext = Depends(get_current_context),
    supervisor_app=Depends(get_supervisor_app),
    signal_engine: SignalEngine = Depends(get_signal_engine),
):
    try:
        client_thread_id = payload.thread_id or str(uuid4())
        thread_id = (
            f"{context.organisation_id}:{context.user_id}:{client_thread_id}"
        )
        profile_key = f"{context.organisation_id}:{context.user_id}"
        user_profile = signal_engine.approved_profiles.get(profile_key, {})
        config = {"configurable": {"thread_id": thread_id}}

        result = await supervisor_app.ainvoke(
            {"messages": [HumanMessage(content=payload.message)]},
            config=config,
            context=context,
        )
        return {
            "thread_id": client_thread_id,
            "response": result["messages"][-1].content,
            "active_profile": user_profile,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Execution error: {str(exc)}"
        ) from exc
