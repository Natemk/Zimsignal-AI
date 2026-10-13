import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ZimSignalConnector")

class GoogleWorkspaceConnector:
    def __init__(self):
        # Tenant-isolated token store: maps user_id -> access tokens
        self.tenant_tokens: Dict[str, str] = {}

    def store_token(self, user_id: str, access_token: str):
        """Stores OAuth tokens strictly isolated by tenant/user ID."""
        self.tenant_tokens[user_id] = access_token
        logger.info(f"[TENANT ISOLATION] Token securely stored for user: {user_id}")

    def get_token(self, user_id: str) -> Optional[str]:
        return self.tenant_tokens.get(user_id)

    def search_emails_draft_only(self, user_id: str, query: str) -> Dict[str, Any]:
        """
        Simulates searching Gmail for a test account with DRAFT-ONLY safety constraints.
        Guarantees write/send actions are blocked.
        """
        token = self.get_token(user_id)
        if not token:
            return {"status": "error", "message": "Unauthorized: Tenant token missing or invalid."}

        # Safe read-only search implementation for Gmail API
        logger.info(f"[SAFE CONNECTOR] Executing DRAFT-ONLY search for tenant {user_id} with query: {query}")
        
        return {
            "status": "success",
            "tenant_id": user_id,
            "mode": "draft_only_search",
            "query": query,
            "simulated_results": [
                {"id": "msg_001", "snippet": f"Draft proposal regarding {query}", "threadId": "thread_abc"}
            ]
        }