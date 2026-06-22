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
        self._policies_by_type: Dict[str, Dict[str, Dict]] = {}
        self._policy_types: Dict[str, Dict] = {
            "traffic_policy": {
                "policy_type_id": "traffic_policy",
                "description": "Traffic steering and load-balancing policy",
                "policy_schema": {
                    "type": "object",
                    "required": ["scope", "statements"],
                    "properties": {
                        "scope": {"type": "object"},
                        "statements": {"type": "array"},
                    },
                },
                "status_schema": {
                    "type": "object",
                    "required": ["enforcement_status"],
                    "properties": {
                        "enforcement_status": {"type": "string"},
                        "feedback": {"type": "array"},
                    },
                },
            },
            "qos_policy": {
                "policy_type_id": "qos_policy",
                "description": "QoS objectives for latency/throughput profiles",
                "policy_schema": {
                    "type": "object",
                    "required": ["scope", "statements"],
                    "properties": {
                        "scope": {"type": "object"},
                        "statements": {"type": "array"},
                    },
                },
                "status_schema": {
                    "type": "object",
                    "required": ["enforcement_status"],
                    "properties": {
                        "enforcement_status": {"type": "string"},
                        "feedback": {"type": "array"},
                    },
                },
            },
            "slice_policy": {
                "policy_type_id": "slice_policy",
                "description": "RAN slice selection and admission policy",
                "policy_schema": {
                    "type": "object",
                    "required": ["scope", "statements"],
                    "properties": {
                        "scope": {"type": "object"},
                        "statements": {"type": "array"},
                    },
                },
                "status_schema": {
                    "type": "object",
                    "required": ["enforcement_status"],
                    "properties": {
                        "enforcement_status": {"type": "string"},
                        "feedback": {"type": "array"},
                    },
                },
            },
        }

    def list_policy_types(self) -> List[Dict]:
        """Return policy type descriptors sorted by ID."""
        with self._lock:
            return [
                dict(self._policy_types[key])
                for key in sorted(self._policy_types.keys())
            ]

    def get_policy_type(self, policy_type_id: str) -> Optional[Dict]:
        """Return one policy type descriptor, or None if unsupported."""
        with self._lock:
            policy_type = self._policy_types.get(policy_type_id)
            return dict(policy_type) if policy_type else None

    def is_supported_policy_type(self, policy_type_id: str) -> bool:
        """Check whether a policy type is currently supported."""
        with self._lock:
            return policy_type_id in self._policy_types

    def upsert_policy(
        self,
        policy_id: str,
        policy_type_id: str,
        policy_object: Dict,
        source_module: str,
        target_module: str,
        notification_destination: Optional[str] = None,
    ) -> Dict:
        """Create or update a policy and return the stored record."""
        if not self.is_supported_policy_type(policy_type_id):
            raise ValueError(f"Unsupported policyTypeId: {policy_type_id}")

        with self._lock:
            policies_for_type = self._policies_by_type.setdefault(policy_type_id, {})
            now = datetime.now(timezone.utc).isoformat()
            existing = policies_for_type.get(policy_id)
            operation = "updated" if existing else "created"
            created_at = existing["created_at"] if existing else now
            status_feedback = existing["policy_status"]["feedback"] if existing else []

            record = {
                "policy_id": policy_id,
                "policy_type_id": policy_type_id,
                "policy_object": dict(policy_object),
                "source_module": source_module,
                "target_module": target_module,
                "notification_destination": notification_destination,
                "callback_subscription": {
                    "subscribed": bool(notification_destination),
                    "destination": notification_destination,
                },
                "policy_status": {
                    "policy_type_id": policy_type_id,
                    "policy_id": policy_id,
                    "enforcement_status": "ACCEPTED",
                    "last_evaluated_at": now,
                    "feedback": status_feedback,
                },
                "created_at": created_at,
                "updated_at": now,
            }
            policies_for_type[policy_id] = record
            return {"operation": operation, "record": record}

    def get_policy(self, policy_type_id: str, policy_id: str) -> Optional[Dict]:
        """Return a policy by ID, or None if not found."""
        with self._lock:
            policy = self._policies_by_type.get(policy_type_id, {}).get(policy_id)
            return dict(policy) if policy else None

    def list_policy_ids(self, policy_type_id: str) -> List[str]:
        """Return policy IDs for a specific policy type."""
        with self._lock:
            policy_ids = self._policies_by_type.get(policy_type_id, {}).keys()
            return sorted(policy_ids)

    def delete_policy(self, policy_type_id: str, policy_id: str) -> bool:
        """Delete one policy if it exists and return deletion status."""
        with self._lock:
            policies_for_type = self._policies_by_type.get(policy_type_id)
            if not policies_for_type or policy_id not in policies_for_type:
                return False

            del policies_for_type[policy_id]
            if not policies_for_type:
                del self._policies_by_type[policy_type_id]
            return True

    def get_policy_status(self, policy_type_id: str, policy_id: str) -> Optional[Dict]:
        """Return PolicyStatusObject for one policy if present."""
        with self._lock:
            policy = self._policies_by_type.get(policy_type_id, {}).get(policy_id)
            if not policy:
                return None
            return dict(policy["policy_status"])

    def append_policy_feedback(self, policy_type_id: str, policy_id: str, feedback_message: str) -> Optional[Dict]:
        """Append a feedback entry to policy status and return updated status."""
        with self._lock:
            policy = self._policies_by_type.get(policy_type_id, {}).get(policy_id)
            if not policy:
                return None

            now = datetime.now(timezone.utc).isoformat()
            policy["policy_status"]["feedback"].append(
                {"message": feedback_message, "timestamp": now}
            )
            policy["policy_status"]["last_evaluated_at"] = now
            policy["updated_at"] = now
            return dict(policy["policy_status"])

    def list_policies(self) -> List[Dict]:
        """Return all policies sorted by policy type then policy ID."""
        with self._lock:
            records: List[Dict] = []
            for policy_type_id in sorted(self._policies_by_type.keys()):
                for policy_id in sorted(self._policies_by_type[policy_type_id].keys()):
                    records.append(dict(self._policies_by_type[policy_type_id][policy_id]))
            return records
