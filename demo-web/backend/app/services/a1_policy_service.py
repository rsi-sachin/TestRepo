"""
Policy-management specific A1 service helpers.
"""

import logging
from copy import deepcopy
import re
from typing import Dict, List, Optional, Tuple

import httpx

from app.models.a1_service import A1ServiceDefinition, A1ServiceType
from app.models.a1_policy_models import PolicyObject, PolicyStatusObject, PolicyTypeObject
from app.models.a1_policy_models import PolicyTypeStatusObject

logger = logging.getLogger(__name__)
from app.models.oran import SpecType
from app.services.a1_service_registry import A1ServiceRegistry


class A1PolicyService:
    """Service-specific metadata and validation for A1-P."""

    _SUPPORTED_SCOPE_TYPES = {
        "ue",
        "ue_group",
        "slice",
        "qos_flow",
        "cell",
    }
    _SCOPE_TYPE_ALIASES = {
        "ue-group": "ue_group",
        "uegroup": "ue_group",
        "qos-flow": "qos_flow",
        "qosflow": "qos_flow",
    }
    _ALLOWED_STATUS_TRANSITIONS = {
        "ACCEPTED": {"ENFORCED", "NOT_ENFORCED"},
        "ENFORCED": {"ENFORCED", "NOT_ENFORCED"},
        "NOT_ENFORCED": {"ENFORCED", "NOT_ENFORCED"},
    }
    _SUPPORTED_POLICY_STATEMENT_CATEGORIES = {"objective", "resource"}
    _HEX_RE = re.compile(r"^[0-9A-Fa-f]+$")
    _TYPE_DEFINITION_CATALOG = {
        "common": "1.0.0",
        "QoSTarget": "4.0.1",
        "QoETarget": "4.0.1",
        "TrafficSteeringPreference": "4.0.1",
        "QoSandTSP": "4.0.1",
        "QoEandTSP": "4.0.1",
        "UELevelTarget": "3.0.1",
        "SliceSLATarget": "3.0.0",
        "LoadBalancing": "1.0.2",
        "EnergySaving": "2.0.0",
    }

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
            "policy_content_profile": {
                "name": "objective_resource_v1",
                "supported_categories": sorted(self._SUPPORTED_POLICY_STATEMENT_CATEGORIES),
                "legacy_statements_allowed": True,
            },
            "type_definition_catalog": {
                "source_reference": "TS 103 988 section 5.2",
                "types": deepcopy(self._TYPE_DEFINITION_CATALOG),
            },
            "a1_ml_support": {
                "status": "out_of_scope",
                "reference": "TS 103 983 section 5",
                "note": "A1-P and A1-EI are implemented; A1-ML is not part of the current MVP baseline.",
            },
        }

    def _validate_hex_attr(self, scope: Dict[str, object], name: str, length: int) -> None:
        value = scope.get(name)
        if value is None:
            return
        if not isinstance(value, str) or len(value) != length or self._HEX_RE.fullmatch(value) is None:
            raise ValueError(f"Scope attribute {name} must be a {length}-character hexadecimal string")

    def _validate_int_attr(self, scope: Dict[str, object], name: str, upper: int) -> None:
        value = scope.get(name)
        if value is None:
            return
        if not isinstance(value, int) or isinstance(value, bool) or value < 0 or value > upper:
            raise ValueError(f"Scope attribute {name} must be an integer between 0 and {upper}")

    def _validate_encoded_scope_attributes(self, policy: PolicyObject) -> None:
        scope = policy.scope
        self._validate_hex_attr(scope, "ranUeId", 16)
        self._validate_hex_attr(scope, "amfRegionId", 2)
        self._validate_hex_attr(scope, "mmeGroupId", 4)
        self._validate_hex_attr(scope, "mmeCode", 2)
        self._validate_int_attr(scope, "amfUeNgapId", (1 << 40) - 1)
        self._validate_int_attr(scope, "mmeUeS1apId", (1 << 32) - 1)
        self._validate_int_attr(scope, "gnbCuUeF1apId", (1 << 32) - 1)
        self._validate_int_attr(scope, "gnbCuCpUeE1apId", (1 << 32) - 1)

        amf_set_id = scope.get("amfSetId")
        if amf_set_id is not None:
            if (
                not isinstance(amf_set_id, str)
                or len(amf_set_id) != 3
                or self._HEX_RE.fullmatch(amf_set_id) is None
                or amf_set_id[0] not in {"0", "1", "2", "3"}
            ):
                raise ValueError(
                    "Scope attribute amfSetId must be a 3-character hexadecimal string with first nibble 0-3"
                )

        amf_pointer = scope.get("amfPointer")
        if amf_pointer is not None:
            if (
                not isinstance(amf_pointer, str)
                or len(amf_pointer) != 2
                or self._HEX_RE.fullmatch(amf_pointer) is None
                or amf_pointer[0] not in {"0", "1", "2", "3"}
            ):
                raise ValueError(
                    "Scope attribute amfPointer must be a 2-character hexadecimal string with first nibble 0-3"
                )

    def _validate_policy_content(self, policy: PolicyObject) -> None:
        for index, statement in enumerate(policy.policy_statements):
            if not isinstance(statement, dict):
                raise ValueError(f"Policy statement at index {index} must be an object")

            # Backward-compatible mode: legacy statements with no explicit category are accepted.
            category = statement.get("category")
            if category in (None, ""):
                continue

            normalized_category = str(category).strip().lower()
            if normalized_category not in self._SUPPORTED_POLICY_STATEMENT_CATEGORIES:
                supported = ", ".join(sorted(self._SUPPORTED_POLICY_STATEMENT_CATEGORIES))
                raise ValueError(
                    f"Unsupported policy statement category '{category}'. "
                    f"Supported categories: {supported}"
                )

            if normalized_category == "objective":
                payload = statement.get("objective")
                if not isinstance(payload, dict) or not payload:
                    raise ValueError(
                        f"Policy statement at index {index} with category objective must include "
                        "a non-empty objective object"
                    )

            if normalized_category == "resource":
                payload = statement.get("resource")
                if not isinstance(payload, dict) or not payload:
                    raise ValueError(
                        f"Policy statement at index {index} with category resource must include "
                        "a non-empty resource object"
                    )

    def _normalize_scope_type(self, scope_type: object) -> str:
        normalized = str(scope_type).strip().lower().replace(" ", "_")
        normalized = self._SCOPE_TYPE_ALIASES.get(normalized, normalized)
        return normalized

    def _validate_policy_scope(self, policy: PolicyObject) -> None:
        scope_type = policy.scope.get("scope_type")
        scope_value = policy.scope.get("scope_value")

        if scope_type in (None, "") or scope_value in (None, ""):
            raise ValueError("Policy scope must include non-empty scope_type and scope_value")

        normalized_scope_type = self._normalize_scope_type(scope_type)
        if normalized_scope_type not in self._SUPPORTED_SCOPE_TYPES:
            supported = ", ".join(sorted(self._SUPPORTED_SCOPE_TYPES))
            raise ValueError(
                "Unsupported policy scope_type '"
                f"{scope_type}'. Supported scope types: {supported}"
            )

        # Section-5 representative encoding checks for common A1 attribute fields.
        self._validate_encoded_scope_attributes(policy)

    def transition_policy_status(
        self,
        policy_type_id: str,
        policy_id: str,
        new_status: str,
        reason: Optional[str] = None,
    ) -> PolicyStatusObject:
        """Apply explicit lifecycle transitions aligned with section-5 semantics."""
        key = (policy_type_id, policy_id)
        existing = self._policy_status.get(key)
        if existing is None:
            raise KeyError(f"Policy status not found for policyTypeId={policy_type_id}, policyId={policy_id}")

        normalized_new = str(new_status).strip().upper()
        normalized_current = existing.enforcement_status.strip().upper()

        allowed = self._ALLOWED_STATUS_TRANSITIONS.get(normalized_current, set())
        if normalized_new not in allowed:
            raise ValueError(
                "Invalid policy status transition "
                f"{normalized_current} -> {normalized_new}; "
                f"allowed transitions: {sorted(allowed)}"
            )

        existing.enforcement_status = normalized_new
        existing.enforcement_reason = reason
        self._policy_status[key] = deepcopy(existing)
        return deepcopy(existing)

    def list_policy_type_ids(self) -> List[str]:
        """Return known policy type identifiers."""
        return list(self._policy_types.keys())

    def list_policy_ids(self, policy_type_id: str) -> List[str]:
        """Return all policy identifiers for a given policy type (§5.2.4.2)."""
        if policy_type_id not in self._policy_types:
            raise KeyError(f"Policy type not found: {policy_type_id}")
        return [pid for (ptid, pid) in self._policies if ptid == policy_type_id]

    def get_policy_type(self, policy_type_id: str) -> PolicyTypeObject:
        """Return one policy type definition."""
        policy_type = self._policy_types.get(policy_type_id)
        if policy_type is None:
            raise KeyError(f"Policy type not found: {policy_type_id}")
        return deepcopy(policy_type)

    def get_policy_type_status(self, policy_type_id: str) -> PolicyTypeStatusObject:
        """Return status metadata for one policy type."""
        policy_type = self._policy_types.get(policy_type_id)
        if policy_type is None:
            raise KeyError(f"Policy type not found: {policy_type_id}")

        status = "ENABLED" if policy_type.supports_policy_creation else "DISABLED"
        reason = (
            "Policy type is available for policy create/update operations"
            if status == "ENABLED"
            else "Policy type is currently unavailable for policy create/update operations"
        )
        return PolicyTypeStatusObject(
            policy_type_id=policy_type_id,
            policy_type_status=status,
            status_reason=reason,
        )

    def create_or_replace_policy(
        self,
        policy_type_id: str,
        policy_id: str,
        policy: PolicyObject,
        notification_destination: Optional[str] = None,
    ) -> Tuple[PolicyObject, bool]:
        """Create or update a policy. Returns (policy, was_created) per §5.2.4.3/5.2.4.4.

        was_created is True when the resource did not previously exist (→ 201);
        False when an existing policy was replaced (→ 200).
        Omitting notification_destination cancels any existing status subscription.
        """
        policy_type = self._policy_types.get(policy_type_id)
        if policy_type is None:
            raise KeyError(f"Policy type not found: {policy_type_id}")
        if not policy_type.supports_policy_creation:
            raise ValueError(f"Policy creation is not supported for policy type: {policy_type_id}")
        self._validate_policy_scope(policy)
        self._validate_policy_content(policy)

        key = (policy_type_id, policy_id)
        was_created = key not in self._policies
        self._policies[key] = deepcopy(policy)
        if notification_destination is not None:
            self._notification_destinations[key] = notification_destination
        else:
            # Omitting notificationDestination cancels the existing subscription (§5.2.4.4.1)
            self._notification_destinations.pop(key, None)
        if was_created:
            self._policy_status[key] = PolicyStatusObject(
                policy_id=policy_id,
                enforcement_status="ACCEPTED",
                enforcement_reason="Policy accepted for evaluation by A1-P Producer",
            )
        else:
            self._policy_status[key] = PolicyStatusObject(
                policy_id=policy_id,
                enforcement_status="ACCEPTED",
                enforcement_reason="Policy updated and accepted for re-evaluation by A1-P Producer",
            )
        return deepcopy(self._policies[key]), was_created

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

    async def notify_policy_status(
        self, destination: str, status_obj: PolicyStatusObject
    ) -> None:
        """Send outbound policy status notification to the consumer callback URI (§5.2.4.8).

        The A1-P Producer acts as a reduced-feature HTTP Client; the Consumer
        exposes the notificationDestination as an HTTP Server endpoint.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                destination,
                json=status_obj.model_dump(mode="json"),
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
        if response.status_code not in (200, 204):
            logger.warning(
                "Policy status notification to %s returned unexpected status %d",
                destination,
                response.status_code,
            )

    async def notify_policy_type_status(
        self, destination: str, status_obj: PolicyTypeStatusObject
    ) -> None:
        """Send outbound policy-type status notification to the consumer callback URI."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                destination,
                json=status_obj.model_dump(mode="json"),
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
        if response.status_code not in (200, 204):
            logger.warning(
                "Policy type status notification to %s returned unexpected status %d",
                destination,
                response.status_code,
            )