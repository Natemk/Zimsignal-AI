"""Read-only workspace routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from api.dependencies import get_current_context, get_workspace_connector
from orchestration.state import ZimSignalContext
from tools.workspace import GoogleWorkspaceConnector

router = APIRouter()


class WorkspaceSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str


@router.post(
    "/workspace/search-draft",
    tags=["Acceptance Gate: Workspace Connector"],
)
async def search_workspace_draft(
    payload: WorkspaceSearchRequest,
    context: ZimSignalContext = Depends(get_current_context),
    workspace_connector: GoogleWorkspaceConnector = Depends(get_workspace_connector),
):
    """Search workspace content using the connector's draft-only policy."""
    result = workspace_connector.search_emails_draft_only(
        context.organisation_id, context.user_id, payload.query
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    return result
