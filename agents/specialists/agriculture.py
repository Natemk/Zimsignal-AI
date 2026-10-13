"""Agriculture specialist node."""

from orchestration.state import AgentState


def agriculture_specialist_node(state: AgentState) -> dict[str, str]:
    from ingestion.index import query_rag_pipeline

    last_msg = state["messages"][-1].content
    result = query_rag_pipeline(
        f"Agriculture farming telemetry: {last_msg}",
        source_tier_filter="primary_official",
    )
    if not result["retrieved_chunks"]:
        return {"specialist_output": "NO_EVIDENCE"}
    evidence = "\n".join(
        document.page_content for document in result["retrieved_chunks"]
    )
    return {"specialist_output": f"[Agriculture Domain]\n{evidence}"}
