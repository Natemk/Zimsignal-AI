from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from retrieval.rag_chain import query_rag_pipeline

class ParallelState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    agri_context: str
    research_context: str

def agriculture_specialist(state: ParallelState) -> dict:
    last_msg = state['messages'][-1].content
    res = query_rag_pipeline(f'Agriculture farming telemetry: {last_msg}')
    context = res['formatted_prompt'] if res['retrieved_chunks'] else 'NO_EVIDENCE'
    return {'agri_context': context}

def research_specialist(state: ParallelState) -> dict:
    last_msg = state['messages'][-1].content
    res = query_rag_pipeline(f'Cyber-physical AI research: {last_msg}')
    context = res['formatted_prompt'] if res['retrieved_chunks'] else 'NO_EVIDENCE'
    return {'research_context': context}

def supervisor_synthesizer(state: ParallelState) -> dict:
    agri = state.get('agri_context', '')
    research = state.get('research_context', '')
    
    if 'NO_EVIDENCE' in agri and 'NO_EVIDENCE' in research:
        ans = 'Insufficient evidence available in retrieved documents to answer this question.'
    else:
        ans = f'Synthesized Multi-Domain Analysis:\n\n[Agriculture Evidence]\n{agri[:250]}\n\n[Research Evidence]\n{research[:250]}'
        
    return {'messages': [AIMessage(content=ans)]}

def create_parallel_supervisor_graph():
    builder = StateGraph(ParallelState)
    builder.add_node('agriculture_specialist', agriculture_specialist)
    builder.add_node('research_specialist', research_specialist)
    builder.add_node('supervisor_synthesizer', supervisor_synthesizer)

    builder.add_edge(START, 'agriculture_specialist')
    builder.add_edge(START, 'research_specialist')
    builder.add_edge('agriculture_specialist', 'supervisor_synthesizer')
    builder.add_edge('research_specialist', 'supervisor_synthesizer')
    builder.add_edge('supervisor_synthesizer', END)

    return builder.compile()

if __name__ == '__main__':
    app = create_parallel_supervisor_graph()
    res = app.invoke({'messages': [HumanMessage(content='How do telemetry standards apply to environmental and ICT frameworks?')]})
    print(res['messages'][-1].content[:400])
