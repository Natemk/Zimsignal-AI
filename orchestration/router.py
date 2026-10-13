"""Deterministic domain routing for agent requests."""

from orchestration.state import AgentState


def supervisor_router_node(state: AgentState) -> dict[str, str]:
    last_msg = state["messages"][-1].content.lower()

    if any(kw in last_msg for kw in ("agri", "farming", "crop", "soil", "harvest")):
        return {"target_domain": "agriculture"}
    if any(
        kw in last_msg
        for kw in ("ai", "framework", "cyber", "ict", "telemetry", "research", "system")
    ):
        return {"target_domain": "research"}
    if any(
        kw in last_msg
        for kw in (
            "commerce",
            "trade",
            "market",
            "finance",
            "transaction",
            "economic",
        )
    ):
        return {"target_domain": "commerce"}
    if any(
        kw in last_msg
        for kw in ("marketing", "campaign", "outreach", "public", "communication")
    ):
        return {"target_domain": "marketing"}
    if any(kw in last_msg for kw in ("zimbabwe", "zimstat", "environmental", "water", "air")):
        return {"target_domain": "research"}
    return {"target_domain": "out_of_bounds"}
