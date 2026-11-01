"""Authentication-related API routes."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from api.dependencies import get_current_context, get_workspace_connector
from orchestration.state import ZimSignalContext
from tools.workspace import GoogleWorkspaceConnector

router = APIRouter()


class OAuthTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str


@router.post("/auth/google-token", tags=["Google OAuth & Tenant Isolation"])
async def store_google_token(
    payload: OAuthTokenRequest,
    context: ZimSignalContext = Depends(get_current_context),
    workspace_connector: GoogleWorkspaceConnector = Depends(get_workspace_connector),
):
    """Store a development token for the authenticated organisation member."""
    workspace_connector.store_token(
        context.organisation_id, context.user_id, payload.access_token
    )
    return {
        "status": "success",
        "message": "Development token stored for the authenticated member.",
        "tenant_isolated": True,
    }
