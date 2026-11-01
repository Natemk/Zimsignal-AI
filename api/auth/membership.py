"""PostgreSQL-backed organisation membership lookup."""

import os
from typing import TypedDict

import psycopg
from fastapi import HTTPException, status


class OrganisationMembership(TypedDict):
    role: str
    subscription: str
    connected_services: tuple[str, ...]


async def get_organisation_membership(
    user_id: str, organisation_id: str
) -> OrganisationMembership | None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Membership database is not configured.",
        )
    dsn = database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    try:
        async with await psycopg.AsyncConnection.connect(dsn) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """
                    SELECT role, subscription, connected_services
                    FROM organisation_memberships
                    WHERE user_id = %s AND organisation_id = %s
                    """,
                    (user_id, organisation_id),
                )
                row = await cursor.fetchone()
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Membership database is unavailable.",
        ) from exc

    if row is None:
        return None
    return {
        "role": row[0],
        "subscription": row[1],
        "connected_services": tuple(row[2] or ()),
    }