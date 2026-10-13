"""Marketing specialist node."""

from orchestration.state import AgentState


def marketing_specialist_node(state: AgentState) -> dict[str, str]:
    return {"specialist_output": "NO_EVIDENCE"}
