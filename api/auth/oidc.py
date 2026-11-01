"""Provider-neutral OIDC access-token verification."""

import os
from functools import lru_cache
from typing import Any

import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError, PyJWKClient, PyJWKClientError
from starlette.concurrency import run_in_threadpool


@lru_cache(maxsize=4)
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


async def verify_oidc_token(token: str) -> dict[str, Any]:
    issuer = os.getenv("OIDC_ISSUER")
    audience = os.getenv("OIDC_AUDIENCE")
    jwks_url = os.getenv("OIDC_JWKS_URL")
    if not issuer or not audience or not jwks_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OIDC authentication is not configured.",
        )

    try:
        signing_key = await run_in_threadpool(
            _jwks_client(jwks_url).get_signing_key_from_jwt, token
        )
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except PyJWKClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve OIDC signing keys.",
        ) from exc