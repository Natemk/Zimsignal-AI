import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_tenant_isolation_unauthorized_search():
    """Verify that searching without a stored token fails with 401 Unauthorized."""
    response = client.post("/workspace/search-draft", json={
        "user_id": "unauthorized_user",
        "query": "quarterly report"
    })
    assert response.status_code == 401

def test_google_oauth_token_and_search_flow():
    """Verify storing an OAuth token securely and executing a draft-only search."""
    # 1. Store token for tenant
    auth_response = client.post("/auth/google-token", json={
        "user_id": "tenant_test_001",
        "access_token": "ya29.mock_oauth_token_xyz"
    })
    assert auth_response.status_code == 200
    assert auth_response.json()["tenant_isolated"] is True

    # 2. Execute draft-only search
    search_response = client.post("/workspace/search-draft", json={
        "user_id": "tenant_test_001",
        "query": "project budget"
    })
    assert search_response.status_code == 200
    data = search_response.json()
    assert data["status"] == "success"
    assert data["mode"] == "draft_only_search"
    assert data["tenant_id"] == "tenant_test_001"