import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ZimSignalConnector")

class GoogleWorkspaceConnector:
    def __init__(self):
        # Development-only store, isolated by organisation and user.
        self.tenant_tokens: Dict[tuple[str, str], str] = {}

    def store_token(self, organisation_id: str, user_id: str, access_token: str):
        """Store a development token under its organisation and user."""
        self.tenant_tokens[(organisation_id, user_id)] = access_token
        logger.info("[TENANT ISOLATION] Development token stored for a member")

    def get_token(self, organisation_id: str, user_id: str) -> Optional[str]:
        return self.tenant_tokens.get((organisation_id, user_id))

    def search_emails_draft_only(
        self, organisation_id: str, user_id: str, query: str
    ) -> Dict[str, Any]:
        """
        Simulates searching Gmail for a test account with DRAFT-ONLY safety constraints.
        Guarantees write/send actions are blocked.
        """
        token = self.get_token(organisation_id, user_id)
        if not token:
            return {"status": "error", "message": "Unauthorized: Tenant token missing or invalid."}

        # Safe read-only search implementation for Gmail API
        logger.info("[SAFE CONNECTOR] Executing simulated draft-only search")
        
        return {
            "status": "success",
            "organisation_id": organisation_id,
            "mode": "draft_only_search",
            "query": query,
            "simulated_results": [
                {"id": "msg_001", "snippet": f"Draft proposal regarding {query}", "threadId": "thread_abc"}
            ]
        }