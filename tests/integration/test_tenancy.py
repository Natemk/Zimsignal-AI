import pytest
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from api.dependencies import get_current_context
from orchestration.state import ZimSignalContext

# Mock Database Store partitioned by organisation_id
MOCK_DATABASE = {
    "org_alpha": [
        {"thread_id": "t100", "content": "Alpha confidential market data"}
    ],
    "org_beta": [
        {"thread_id": "t200", "content": "Beta confidential farm records"}
    ],
}

app = FastAPI()


@app.get("/api/threads/{thread_id}")
async def get_thread(
    thread_id: str, ctx: ZimSignalContext = Depends(get_current_context)
):
    # Enforce database multi-tenant isolation
    tenant_records = MOCK_DATABASE.get(ctx.organisation_id, [])
    for record in tenant_records:
        if record["thread_id"] == thread_id:
            return record

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Thread not found or access denied.",
    )


client = TestClient(app)


def test_cross_tenant_isolation():
    # User A (Org Alpha) requests User A's thread -> 200 OK
    headers_user_a = {
        "x-user-id": "user_a",
        "x-organisation-id": "org_alpha",
        "x-user-role": "admin",
    }
    response_a = client.get("/api/threads/t100", headers=headers_user_a)
    assert response_a.status_code == 200
    assert response_a.json()["content"] == "Alpha confidential market data"

    # User B (Org Beta) attempts to request User A's thread -> 404/403 Access Denied
    headers_user_b = {
        "x-user-id": "user_b",
        "x-organisation-id": "org_beta",
        "x-user-role": "user",
    }
    response_b = client.get("/api/threads/t100", headers=headers_user_b)
    assert response_b.status_code == 404