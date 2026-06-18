"""
A1 simulator service layer.

Implements minimal in-memory policy lifecycle behavior for the A1-P flow
(NON_RT_RIC consumer -> NEAR_RT_RIC producer) while preserving existing
contract-first API semantics.
"""

from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Optional


class SimulatorA1PolicyService:
    """Stores A1 policy records in memory for simulator bootstrap evolution."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._policies: Dict[str, Dict] = {}

    def upsert_policy(
        self,
        policy_id: str,
        policy_type: str,
        source_module: str,
        target_module: str,
    ) -> Dict:
        """Create or update a policy and return the stored record."""
        with self._lock:
            now = datetime.now(timezone.utc).isoformat()
            existing = self._policies.get(policy_id)
            operation = "updated" if existing else "created"
            created_at = existing["created_at"] if existing else now

            record = {
                "policy_id": policy_id,
                "policy_type": policy_type,
                "source_module": source_module,
                "target_module": target_module,
                "created_at": created_at,
                "updated_at": now,
            }
            self._policies[policy_id] = record
            return {"operation": operation, "record": record}

    def get_policy(self, policy_id: str) -> Optional[Dict]:
        """Return a policy by ID, or None if not found."""
        with self._lock:
            policy = self._policies.get(policy_id)
            return dict(policy) if policy else None

    def list_policies(self) -> List[Dict]:
        """Return policies sorted by policy ID for deterministic responses."""
        with self._lock:
            return [
                dict(self._policies[key])
                for key in sorted(self._policies.keys())
            ]
