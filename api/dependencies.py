from functools import lru_cache

from fastapi import Header, HTTPException, status

from api.auth.membership import get_organisation_membership
from api.auth.oidc import verify_oidc_token
from governance.audit import AlertDispatcher, SignalEngine
from orchestration.graph import create_supervisor_graph
from orchestration.state import ZimSignalContext
from tools.workspace import GoogleWorkspaceConnector


@lru_cache
def get_supervisor_app():
    return create_supervisor_graph()


@lru_cache
def get_signal_engine() -> SignalEngine:
    return SignalEngine()


@lru_cache
def get_alert_dispatcher() -> AlertDispatcher:
    return AlertDispatcher()


@lru_cache
def get_workspace_connector() -> GoogleWorkspaceConnector:
    return GoogleWorkspaceConnector()


async def get_current_context(
    authorization: str | None = Header(default=None),
    x_organisation_id: str | None = Header(default=None),
) -> ZimSignalContext:
    """Build trusted request context from a verified identity and membership."""
    scheme, separator, token = (authorization or "").partition(" ")
    if scheme.casefold() != "bearer" or not separator or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A bearer access token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = await verify_oidc_token(token.strip())
    user_id = claims.get("sub")
    organisation_id = x_organisation_id or claims.get("organisation_id")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The access token has no subject.",
        )
    if not isinstance(organisation_id, str) or not organisation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organisation must be selected.",
        )

    membership = await get_organisation_membership(user_id, organisation_id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organisation.",
        )
    return ZimSignalContext(
        user_id=user_id,
        organisation_id=organisation_id,
        role=membership["role"],
        subscription=membership["subscription"],
        connected_services=membership["connected_services"],
    )