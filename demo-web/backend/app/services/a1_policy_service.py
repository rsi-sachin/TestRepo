"""
Policy-management specific A1 service helpers.
"""

from copy import deepcopy
from typing import Dict, List, Tuple

from app.models.a1_service import A1ServiceDefinition, A1ServiceType
from app.models.a1_policy_models import PolicyObject, PolicyStatusObject, PolicyTypeObject
from app.models.oran import SpecType
from app.services.a1_service_registry import A1ServiceRegistry


class A1PolicyService:
    """Service-specific metadata and validation for A1-P."""

    def __init__(self, registry: A1ServiceRegistry | None = None) -> None:
        self.registry = registry or A1ServiceRegistry()
        self._policy_types: Dict[str, PolicyTypeObject] = {
            "default": PolicyTypeObject(
                policy_type_id="default",
                policy_schema={
                    "type": "object",
                    "required": ["policy_statements"],
                },
                policy_status_schema={
                    "type": "object",
                    "required": ["policy_id", "enforcement_status"],
                },
                supports_policy_creation=True,
            )
        }
        self._policies: Dict[Tuple[str, str], PolicyObject] = {}
        self._policy_status: Dict[Tuple[str, str], PolicyStatusObject] = {}
        self._notification_destinations: Dict[Tuple[str, str], str] = {}

    @property
    def definition(self) -> A1ServiceDefinition:
        return self.registry.get_service_definition(A1ServiceType.A1_P)

    def get_supported_specs(self) -> List[SpecType]:
        return list(self.definition.supported_specs)

    def get_catalog_context(self) -> Dict[str, str]:
        return {
            "service_type": self.definition.service_type.value,
            "service_name": self.definition.name,
            "default_catalog_name": self.definition.default_catalog_name,
            "consumer_role": self.definition.consumer_role.label,
            "producer_role": self.definition.producer_role.label,
        }

    def build_service_summary(self) -> Dict[str, object]:
        return {
            "definition": self.definition.model_dump(mode="json"),
            "recommended_specs": [spec.value for spec in self.get_supported_specs()],
            "primary_resources": self.definition.resource_domains,
        }

    def list_policy_type_ids(self) -> List[str]:
        """Return known policy type identifiers."""
        return list(self._policy_types.keys())

    def get_policy_type(self, policy_type_id: str) -> PolicyTypeObject:
        """Return one policy type definition."""
        policy_type = self._policy_types.get(policy_type_id)
        if policy_type is None:
            raise KeyError(f"Policy type not found: {policy_type_id}")
        return deepcopy(policy_type)

    def create_or_replace_policy(
        self,
        policy_type_id: str,
        policy_id: str,
        policy: PolicyObject,
        notification_destination: str,
    ) -> PolicyObject:
        """Create or replace a policy under a policy type."""
        policy_type = self._policy_types.get(policy_type_id)
        if policy_type is None:
            raise KeyError(f"Policy type not found: {policy_type_id}")
        if not policy_type.supports_policy_creation:
            raise ValueError(f"Policy creation is not supported for policy type: {policy_type_id}")

        key = (policy_type_id, policy_id)
        self._policies[key] = deepcopy(policy)
        self._notification_destinations[key] = notification_destination
        self._policy_status[key] = PolicyStatusObject(
            policy_id=policy_id,
            enforcement_status="ACCEPTED",
            enforcement_reason="Policy accepted for evaluation by A1-P Producer",
        )
        return deepcopy(self._policies[key])

    def get_policy(self, policy_type_id: str, policy_id: str) -> PolicyObject:
        """Get a policy by policy type and policy id."""
        key = (policy_type_id, policy_id)
        policy = self._policies.get(key)
        if policy is None:
            raise KeyError(f"Policy not found for policyTypeId={policy_type_id}, policyId={policy_id}")
        return deepcopy(policy)

    def delete_policy(self, policy_type_id: str, policy_id: str) -> None:
        """Delete a policy and related status/callback metadata."""
        key = (policy_type_id, policy_id)
        if key not in self._policies:
            raise KeyError(f"Policy not found for policyTypeId={policy_type_id}, policyId={policy_id}")

        del self._policies[key]
        self._policy_status.pop(key, None)
        self._notification_destinations.pop(key, None)

    def get_policy_status(self, policy_type_id: str, policy_id: str) -> PolicyStatusObject:
        """Get policy enforcement status."""
        key = (policy_type_id, policy_id)
        status = self._policy_status.get(key)
        if status is None:
            raise KeyError(f"Policy status not found for policyTypeId={policy_type_id}, policyId={policy_id}")
        return deepcopy(status)