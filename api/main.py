"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth.routes import router as auth_router
from api.routes.chat import router as chat_router
from api.routes.general import router as general_router
from api.routes.workspace import router as workspace_router

app = FastAPI(
    title="ZimSignal AI Supervisor & Signal API",
    version="1.3.0",
    description=(
        "Production API: Google OAuth, Tenant-Isolated Tokens, and "
        "Draft-Only Workspace Search."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(general_router)
app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(workspace_router)
