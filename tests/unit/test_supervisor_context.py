import pytest
from langchain_core.messages import HumanMessage

from orchestration.graph import create_supervisor_graph
from orchestration.state import ZimSignalContext


@pytest.mark.asyncio
async def test_supervisor_accepts_whatsapp_runtime_context():
    supervisor = create_supervisor_graph()
    context = ZimSignalContext(
        user_id="user_test",
        organisation_id="org_test",
        role="farmer",
        subscription="free",
        connected_services=("whatsapp",),
    )

    result = await supervisor.ainvoke(
        {"messages": [HumanMessage(content="Hello")]},
        config={"configurable": {"thread_id": "whatsapp-context-test"}},
        context=context,
    )

    assert result["messages"][-1].content.startswith(
        "Insufficient evidence available"
    )