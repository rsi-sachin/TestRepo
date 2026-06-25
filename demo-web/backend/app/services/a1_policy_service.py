"""
Policy-management specific A1 service helpers.
"""

from typing import Dict, List

from app.models.a1_service import A1ServiceDefinition, A1ServiceType
from app.models.oran import SpecType
from app.services.a1_service_registry import A1ServiceRegistry


class A1PolicyService:
    """Service-specific metadata and validation for A1-P."""

    def __init__(self, registry: A1ServiceRegistry | None = None) -> None:
        self.registry = registry or A1ServiceRegistry()

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