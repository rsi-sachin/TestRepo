"""
Registry of supported A1 services.

This module makes the section 5.1 service boundary explicit by
describing the supported services, their roles, and the specs they touch.
"""

from typing import Dict, List, Optional

from app.models.a1_service import (
    A1RoleType,
    A1ServiceDefinition,
    A1ServiceRegistryResponse,
    A1ServiceRole,
    A1ServiceType,
)
from app.models.oran import SpecType


class A1ServiceRegistry:
    """Central registry for A1 service metadata."""

    def __init__(self) -> None:
        self._services: Dict[A1ServiceType, A1ServiceDefinition] = {
            A1ServiceType.A1_P: A1ServiceDefinition(
                service_type=A1ServiceType.A1_P,
                name="A1 policy management service",
                description=(
                    "Policy lifecycle, policy status, and policy type operations "
                    "for the A1 interface"
                ),
                consumer_role=A1ServiceRole(
                    role_type=A1RoleType.CONSUMER,
                    label="A1-P Consumer",
                    description="Requests policy operations from the producer",
                ),
                producer_role=A1ServiceRole(
                    role_type=A1RoleType.PRODUCER,
                    label="A1-P Producer",
                    description="Owns and evaluates policy resources",
                ),
                supported_specs=[
                    SpecType.TS_103_989,
                    SpecType.TS_103_987,
                    SpecType.TS_103_988,
                    SpecType.TS_103_983,
                ],
                resource_domains=["/policytypes", "/policies", "/status"],
                default_catalog_name="A1 Policy Management Catalog",
            ),
            A1ServiceType.A1_EI: A1ServiceDefinition(
                service_type=A1ServiceType.A1_EI,
                name="A1 enrichment information service",
                description=(
                    "EI job submission, result delivery, and enrichment status "
                    "operations for the A1 interface"
                ),
                consumer_role=A1ServiceRole(
                    role_type=A1RoleType.CONSUMER,
                    label="A1-EI Consumer",
                    description="Requests enrichment information from the producer",
                ),
                producer_role=A1ServiceRole(
                    role_type=A1RoleType.PRODUCER,
                    label="A1-EI Producer",
                    description="Owns and delivers EI job resources",
                ),
                supported_specs=[
                    SpecType.TS_103_989,
                    SpecType.TS_103_987,
                    SpecType.TS_103_988,
                    SpecType.TS_103_983,
                ],
                resource_domains=["/ei-jobs", "/ei-types", "/notifications"],
                default_catalog_name="A1 Enrichment Information Catalog",
            ),
        }

    def list_services(self) -> List[A1ServiceDefinition]:
        """Return all supported A1 services."""
        return [service for service in self._services.values() if service.supported]

    def get_response(self) -> A1ServiceRegistryResponse:
        """Return a serializable registry payload."""
        return A1ServiceRegistryResponse(services=self.list_services())

    def get_service_definition(self, service_type: str | A1ServiceType) -> A1ServiceDefinition:
        """Resolve a service definition or raise ValueError."""
        service_enum = self._normalize_service_type(service_type)
        if service_enum not in self._services:
            raise ValueError(f"Unsupported A1 service: {service_type}")
        return self._services[service_enum]

    def is_supported(self, service_type: str | A1ServiceType) -> bool:
        """Check whether a service is enabled in this tool."""
        try:
            service = self.get_service_definition(service_type)
        except ValueError:
            return False
        return service.supported

    def validate_specs_for_service(
        self,
        service_type: str | A1ServiceType,
        selected_specs: Optional[List[SpecType]] = None,
    ) -> List[SpecType]:
        """Filter selected specs to the ones supported by the service."""
        service = self.get_service_definition(service_type)
        if not selected_specs:
            return list(service.supported_specs)

        return [spec for spec in selected_specs if spec in service.supported_specs]

    def get_default_catalog_name(self, service_type: str | A1ServiceType) -> str:
        """Return the default catalog name for a service."""
        return self.get_service_definition(service_type).default_catalog_name

    def _normalize_service_type(self, service_type: str | A1ServiceType) -> A1ServiceType:
        if isinstance(service_type, A1ServiceType):
            return service_type
        normalized = str(service_type).strip().upper().replace("_", "-")
        for candidate in A1ServiceType:
            if candidate.value.upper() == normalized:
                return candidate
        raise ValueError(f"Unsupported A1 service: {service_type}")