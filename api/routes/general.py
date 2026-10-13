"""General service and health routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["General"])
async def read_root():
    return {
        "service": "ZimSignal AI Supervisor API",
        "status": "online",
        "milestone": "Google OAuth & Tenant-Isolated REST Connector",
        "documentation": "/docs",
    }


@router.get("/health", tags=["General"])
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "graph": "compiled",
        "connector": "active",
    }
