"""LangGraph assembly and in-memory checkpointer configuration."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agents.specialists.agriculture import agriculture_specialist_node
from agents.specialists.commerce import commerce_specialist_node
from agents.specialists.marketing import marketing_specialist_node
from agents.specialists.research import research_specialist_node
from agents.supervisor import supervisor_synthesizer_node
from orchestration.router import supervisor_router_node
from orchestration.state import AgentState, ZimSignalContext


def create_supervisor_graph():
    builder = StateGraph(AgentState, context_schema=ZimSignalContext)

    builder.add_node("router", supervisor_router_node)
    builder.add_node("agriculture_specialist", agriculture_specialist_node)
    builder.add_node("research_specialist", research_specialist_node)
    builder.add_node("commerce_specialist", commerce_specialist_node)
    builder.add_node("marketing_specialist", marketing_specialist_node)
    builder.add_node("supervisor", supervisor_synthesizer_node)

    builder.add_edge(START, "router")

    def route_decision(state: AgentState) -> str:
        domain = state.get("target_domain")
        if domain in ("agriculture", "research", "commerce", "marketing"):
            return f"{domain}_specialist"
        return "supervisor"

    builder.add_conditional_edges(
        "router",
        route_decision,
        {
            "agriculture_specialist": "agriculture_specialist",
            "research_specialist": "research_specialist",
            "commerce_specialist": "commerce_specialist",
            "marketing_specialist": "marketing_specialist",
            "supervisor": "supervisor",
        },
    )

    for specialist in (
        "agriculture_specialist",
        "research_specialist",
        "commerce_specialist",
        "marketing_specialist",
    ):
        builder.add_edge(specialist, "supervisor")

    builder.add_edge("supervisor", END)
    return builder.compile(checkpointer=MemorySaver())
