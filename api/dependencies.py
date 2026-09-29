from fastapi import Header, HTTPException, status
from orchestration.state import ZimSignalContext


async def get_current_context(
    x_user_id: str = Header(...),
    x_organisation_id: str = Header(...),
    x_user_role: str = Header(default="user"),
) -> ZimSignalContext:
    """Extracts immutable multi-tenant identity from incoming request headers."""
    if not x_user_id or not x_organisation_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required tenant authentication headers.",
        )
    return ZimSignalContext(
        user_id=x_user_id, organisation_id=x_organisation_id, role=x_user_role
    )