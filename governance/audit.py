import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

class SignalEngine:
    def __init__(self):
        # Long-term approved profile store (backed by database in production)
        self.approved_profiles: Dict[str, Dict[str, Any]] = {
            "user_001": {"tier": "enterprise", "region": "ZW", "risk_tolerance": "moderate"}
        }
        self.audit_log: List[Dict[str, Any]] = []

    def compute_deterministic_delta(self, user_id: str, proposed_changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes a deterministic SHA-256 input hash over sorted profile parameters.
        This guarantees identical inputs always produce identical delta hashes.
        """
        current_profile = self.approved_profiles.get(user_id, {})
        serialized = json.dumps({"profile": current_profile, "updates": proposed_changes}, sort_keys=True)
        input_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        
        return {
            "user_id": user_id,
            "delta_id": f"delta_{input_hash[:10]}",
            "input_hash": input_hash,
            "parameter_changes": proposed_changes
        }

    def approve_and_commit_delta(self, user_id: str, delta_id: str, input_hash: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies an approved delta to the permanent user profile and records 
        an immutable audit log entry.
        """
        profile = self.approved_profiles.get(user_id, {})
        for k, v in changes.items():
            profile[k] = v
        self.approved_profiles[user_id] = profile

        audit_entry = {
            "audit_id": f"aud_{len(self.audit_log) + 1:04d}",
            "user_id": user_id,
            "delta_id": delta_id,
            "input_hash": input_hash,
            "changes": changes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "COMMITTED"
        }
        self.audit_log.append(audit_entry)
        return audit_entry


class AlertDispatcher:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def send_alert(self, user_id: str, message: str) -> Dict[str, Any]:
        """Dispatch and record a notification for a committed profile change."""
        alert = {
            "alert_id": f"alt_{len(self.history) + 1:04d}",
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.history.append(alert)
        return alert