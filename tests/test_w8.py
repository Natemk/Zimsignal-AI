import pytest
from fastapi.testclient import TestClient
from api.dependencies import get_current_context, get_workspace_connector
from api.main import app
from orchestration.state import ZimSignalContext
from tools.workspace import GoogleWorkspaceConnector



@pytest.fixture
def authenticated_client():
    identity = {
        "context": ZimSignalContext(
            user_id="tenant_test_001",
            organisation_id="org_test_001",
            role="user",
        )
    }
    connector = GoogleWorkspaceConnector()
    app.dependency_overrides[get_current_context] = lambda: identity["context"]
    app.dependency_overrides[get_workspace_connector] = lambda: connector
    with TestClient(app) as client:
        yield client, identity
    app.dependency_overrides.clear()


def test_tenant_isolation_unauthorized_search(authenticated_client):
    """Verify that searching without a stored token fails with 401 Unauthorized."""
    client, _ = authenticated_client
    response = client.post("/workspace/search-draft", json={
        "query": "quarterly report"
    })
    assert response.status_code == 401


def test_google_token_and_search_are_member_scoped(authenticated_client):
    """Verify the real routes scope development tokens to authenticated identity."""
    client, identity = authenticated_client
    auth_response = client.post("/auth/google-token", json={
        "access_token": "ya29.mock_oauth_token_xyz"
    })
    assert auth_response.status_code == 200
    assert auth_response.json()["tenant_isolated"] is True

    identity["context"] = ZimSignalContext(
        user_id="other_user",
        organisation_id="org_test_001",
        role="user",
    )
    search_response = client.post("/workspace/search-draft", json={
        "query": "project budget"
    })
    assert search_response.status_code == 401

    identity["context"] = ZimSignalContext(
        user_id="tenant_test_001",
        organisation_id="org_test_001",
        role="user",
    )
    search_response = client.post("/workspace/search-draft", json={
        "query": "project budget"
    })
    assert search_response.status_code == 200
    data = search_response.json()
    assert data["status"] == "success"
    assert data["mode"] == "draft_only_search"
    assert data["organisation_id"] == "org_test_001"