"""Supervisor response synthesis."""

from langchain_core.messages import AIMessage

from orchestration.state import AgentState


def supervisor_synthesizer_node(state: AgentState) -> dict[str, list[AIMessage]]:
    output = state.get("specialist_output", "NO_EVIDENCE")

    if output in ("NO_EVIDENCE", None):
        final_response = (
            "Insufficient evidence available in retrieved documents to answer "
            "this question."
        )
    else:
        final_response = f"Supervisor Synthesized Analysis:\n\n{output}"

    return {"messages": [AIMessage(content=final_response)]}
