from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from api.dependencies import get_current_context, get_supervisor_app
from api.main import app
from orchestration.state import ZimSignalContext


class RecordingSupervisor:
    def __init__(self):
        self.calls = []

    async def ainvoke(self, state, config, context):
        self.calls.append((config["configurable"]["thread_id"], context))
        return {"messages": [AIMessage(content="test response")]}


def test_chat_requires_authentication():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 401


def test_chat_thread_is_scoped_to_authenticated_identity():
    identities = {
        "current": ZimSignalContext(
            user_id="user_alpha",
            organisation_id="org_alpha",
            role="farmer",
        )
    }
    supervisor = RecordingSupervisor()
    app.dependency_overrides[get_current_context] = lambda: identities["current"]
    app.dependency_overrides[get_supervisor_app] = lambda: supervisor

    try:
        with TestClient(app) as client:
            first = client.post(
                "/chat", json={"message": "hello", "thread_id": "same-id"}
            )
            identities["current"] = ZimSignalContext(
                user_id="user_beta",
                organisation_id="org_beta",
                role="farmer",
            )
            second = client.post(
                "/chat", json={"message": "hello", "thread_id": "same-id"}
            )

            spoofed = client.post(
                "/chat",
                json={"message": "hello", "user_id": "user_alpha"},
            )
    finally:
        app.dependency_overrides.clear()

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["thread_id"] == second.json()["thread_id"] == "same-id"
    assert supervisor.calls[0][0] == "org_alpha:user_alpha:same-id"
    assert supervisor.calls[1][0] == "org_beta:user_beta:same-id"
    assert spoofed.status_code == 422