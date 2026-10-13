"""Commerce specialist node."""

from orchestration.state import AgentState


def commerce_specialist_node(state: AgentState) -> dict[str, str]:
    return {"specialist_output": "NO_EVIDENCE"}
