"""Agent chat route."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from api.dependencies import get_signal_engine, get_supervisor_app
from governance.audit import SignalEngine

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt.")
    thread_id: Optional[str] = Field(
        "default_thread", description="Session thread ID for memory."
    )
    user_id: Optional[str] = Field(
        "user_001", description="Associated user ID for long-term profile lookup."
    )


@router.post("/chat", tags=["Agent Interaction"])
async def chat_endpoint(
    payload: ChatRequest,
    supervisor_app=Depends(get_supervisor_app),
    signal_engine: SignalEngine = Depends(get_signal_engine),
):
    try:
        user_profile = signal_engine.approved_profiles.get(payload.user_id, {})
        config = {"configurable": {"thread_id": payload.thread_id}}
        contextual_prompt = (
            f"[System Context - Approved User Profile: {user_profile}]\n"
            f"User Query: {payload.message}"
        )

        result = supervisor_app.invoke(
            {"messages": [HumanMessage(content=contextual_prompt)]},
            config=config,
        )
        return {
            "thread_id": payload.thread_id,
            "response": result["messages"][-1].content,
            "active_profile": user_profile,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Execution error: {str(exc)}"
        ) from exc
