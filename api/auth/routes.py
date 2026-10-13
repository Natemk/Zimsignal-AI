"""Authentication-related API routes."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.dependencies import get_workspace_connector
from tools.workspace import GoogleWorkspaceConnector

router = APIRouter()


class OAuthTokenRequest(BaseModel):
    user_id: str
    access_token: str


@router.post("/auth/google-token", tags=["Google OAuth & Tenant Isolation"])
async def store_google_token(
    payload: OAuthTokenRequest,
    workspace_connector: GoogleWorkspaceConnector = Depends(get_workspace_connector),
):
    """Store a workspace token isolated to the supplied user."""
    workspace_connector.store_token(payload.user_id, payload.access_token)
    return {
        "status": "success",
        "message": (
            "OAuth access token securely stored for tenant: "
            f"{payload.user_id}"
        ),
        "tenant_isolated": True,
    }
