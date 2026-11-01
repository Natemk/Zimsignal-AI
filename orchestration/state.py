from dataclasses import dataclass
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    target_domain: str | None
    specialist_output: str | None


@dataclass(frozen=True)
class ZimSignalContext:
    """Immutable runtime security parameters passed with every invocation."""

    user_id: str
    organisation_id: str
    role: str
    subscription: str = "free"
    connected_services: tuple[str, ...] = ()


class ZimSignalState(dict):
    """Mutable runtime state for LangGraph execution."""

    messages: Annotated[Sequence[BaseMessage], ...]
    active_crop: str | None
    pending_action_ids: list[str]