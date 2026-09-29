from dataclasses import dataclass
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage


@dataclass(frozen=True)
class ZimSignalContext:
    """Immutable runtime security parameters passed with every invocation."""

    user_id: str
    organisation_id: str
    role: str


class ZimSignalState(dict):
    """Mutable runtime state for LangGraph execution."""

    messages: Annotated[Sequence[BaseMessage], ...]
    active_crop: str | None
    pending_action_ids: list[str]