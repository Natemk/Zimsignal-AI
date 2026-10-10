import os
from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from retrieval.rag_chain import query_rag_pipeline

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    target_domain: Optional[str]
    specialist_output: Optional[str]

# 1. Intent Router for 4-Domain Boundaries
def supervisor_router_node(state: AgentState) -> dict:
    last_msg = state['messages'][-1].content.lower()
    
    if any(kw in last_msg for kw in ["agri", "farming", "crop", "soil", "harvest"]):
        return {"target_domain": "agriculture"}
    elif any(kw in last_msg for kw in ["ai", "framework", "cyber", "ict", "telemetry", "research", "system"]):
        return {"target_domain": "research"}
    elif any(kw in last_msg for kw in ["commerce", "trade", "market", "finance", "transaction", "economic"]):
        return {"target_domain": "commerce"}
    elif any(kw in last_msg for kw in ["marketing", "campaign", "outreach", "public", "communication"]):
        return {"target_domain": "marketing"}
    elif any(kw in last_msg for kw in ["zimbabwe", "zimstat", "environmental", "water", "air"]):
        return {"target_domain": "research"} # Default public sector domain
    else:
        return {"target_domain": "out_of_bounds"}

# 2. Domain Specialist Nodes
def agriculture_specialist_node(state: AgentState) -> dict:
    last_msg = state['messages'][-1].content
    res = query_rag_pipeline(f"Agriculture farming telemetry: {last_msg}", source_tier_filter="primary_official")
    if not res['retrieved_chunks']:
        return {"specialist_output": "NO_EVIDENCE"}
    return {"specialist_output": f"[Agriculture Domain]\n" + "\n".join([d.page_content for d in res['retrieved_chunks']])}

def research_specialist_node(state: AgentState) -> dict:
    last_msg = state['messages'][-1].content
    res = query_rag_pipeline(f"Cyber-physical AI research: {last_msg}", source_tier_filter="primary_official")
    if not res['retrieved_chunks']:
        return {"specialist_output": "NO_EVIDENCE"}
    return {"specialist_output": f"[Research Domain]\n" + "\n".join([d.page_content for d in res['retrieved_chunks']])}

def commerce_specialist_node(state: AgentState) -> dict:
    # Stub or dedicated query for commerce domain records
    return {"specialist_output": "NO_EVIDENCE"}

def marketing_specialist_node(state: AgentState) -> dict:
    # Stub or dedicated query for marketing domain records
    return {"specialist_output": "NO_EVIDENCE"}

# 3. Supervisor Synthesizer Node with Guardrails
def supervisor_synthesizer_node(state: AgentState) -> dict:
    output = state.get("specialist_output", "NO_EVIDENCE")
    
    if output in ["NO_EVIDENCE", None]:
        final_response = "Insufficient evidence available in retrieved documents to answer this question."
    else:
        final_response = f"Supervisor Synthesized Analysis:\n\n{output}"
        
    return {"messages": [AIMessage(content=final_response)]}

# 4. Compiled Graph with Multi-Specialist Conditional Routing
def create_supervisor_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("router", supervisor_router_node)
    builder.add_node("agriculture_specialist", agriculture_specialist_node)
    builder.add_node("research_specialist", research_specialist_node)
    builder.add_node("commerce_specialist", commerce_specialist_node)
    builder.add_node("marketing_specialist", marketing_specialist_node)
    builder.add_node("supervisor", supervisor_synthesizer_node)
    
    builder.add_edge(START, "router")
    
    def route_decision(state: AgentState):
        domain = state.get("target_domain")
        return f"{domain}_specialist" if domain in ["agriculture", "research", "commerce", "marketing"] else "supervisor"
            
    builder.add_conditional_edges("router", route_decision, {
        "agriculture_specialist": "agriculture_specialist",
        "research_specialist": "research_specialist",
        "commerce_specialist": "commerce_specialist",
        "marketing_specialist": "marketing_specialist",
        "supervisor": "supervisor"
    })
    
    for spec in ["agriculture_specialist", "research_specialist", "commerce_specialist", "marketing_specialist"]:
        builder.add_edge(spec, "supervisor")
        
    builder.add_edge("supervisor", END)
    
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)