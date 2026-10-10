import os
from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from retrieval.rag_chain import query_rag_pipeline

# 1. State Definition supporting parallel specialist outputs
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    agri_context: Optional[str]
    research_context: Optional[str]

# 2. Specialized Agent Nodes (Enforcing Domain Boundaries)
def agriculture_specialist_node(state: AgentState) -> dict:
    last_msg = state['messages'][-1].content
    res = query_rag_pipeline(f"Agriculture farming telemetry: {last_msg}")
    context = res['formatted_prompt'] if res['retrieved_chunks'] else "NO_EVIDENCE"
    return {"agri_context": context}

def research_specialist_node(state: AgentState) -> dict:
    last_msg = state['messages'][-1].content
    res = query_rag_pipeline(f"Cyber-physical AI research: {last_msg}")
    context = res['formatted_prompt'] if res['retrieved_chunks'] else "NO_EVIDENCE"
    return {"research_context": context}

# 3. Supervisor Synthesizer Node with Guardrails
def supervisor_synthesizer_node(state: AgentState) -> dict:
    agri = state.get("agri_context", "NO_EVIDENCE")
    research = state.get("research_context", "NO_EVIDENCE")
    
    if "NO_EVIDENCE" in agri and "NO_EVIDENCE" in research:
        final_response = "Insufficient evidence available in retrieved documents to answer this question."
    else:
        final_response = f"Supervisor Synthesized Analysis:\n\n[Agriculture Domain]\n{agri[:300]}\n\n[Research Domain]\n{research[:300]}"
        
    return {"messages": [AIMessage(content=final_response)]}

# 4. Compiled Graph with Parallel Fan-Out & Persistence
def create_supervisor_graph():
    builder = StateGraph(AgentState)
    
    # Add specialist and supervisor nodes
    builder.add_node("agriculture_specialist", agriculture_specialist_node)
    builder.add_node("research_specialist", research_specialist_node)
    builder.add_node("supervisor", supervisor_synthesizer_node)
    
    # Parallel fan-out from START to both specialists
    builder.add_edge(START, "agriculture_specialist")
    builder.add_edge(START, "research_specialist")
    
    # Convergence from specialists into supervisor
    builder.add_edge("agriculture_specialist", "supervisor")
    builder.add_edge("research_specialist", "supervisor")
    
    builder.add_edge("supervisor", END)
    
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

if __name__ == "__main__":
    app = create_supervisor_graph()
    config = {"configurable": {"thread_id": "parallel_audit_test"}}
    res = app.invoke({"messages": [HumanMessage(content="How do telemetry and AI standards apply in Zimbabwe?")]}, config=config)
    print(res["messages"][-1].content[:400])