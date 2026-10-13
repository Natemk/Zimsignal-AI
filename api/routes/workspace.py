"""Read-only workspace routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.dependencies import get_workspace_connector
from tools.workspace import GoogleWorkspaceConnector

router = APIRouter()


class WorkspaceSearchRequest(BaseModel):
    user_id: str
    query: str


@router.post(
    "/workspace/search-draft",
    tags=["Acceptance Gate: Workspace Connector"],
)
async def search_workspace_draft(
    payload: WorkspaceSearchRequest,
    workspace_connector: GoogleWorkspaceConnector = Depends(get_workspace_connector),
):
    """Search workspace content using the connector's draft-only policy."""
    result = workspace_connector.search_emails_draft_only(
        payload.user_id, payload.query
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    return result
