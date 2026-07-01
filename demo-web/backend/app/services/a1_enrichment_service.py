"""
Enrichment-information specific A1 service helpers.
"""

import logging
from copy import deepcopy
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.models.a1_service import A1ServiceDefinition, A1ServiceType
from app.models.oran import SpecType
from app.services.a1_service_registry import A1ServiceRegistry

logger = logging.getLogger(__name__)


class A1EnrichmentInformationService:
    """Service-specific metadata and validation for A1-EI."""

    def __init__(self, registry: A1ServiceRegistry | None = None) -> None:
        self.registry = registry or A1ServiceRegistry()
        self._lock = Lock()
        self._ei_types: Dict[str, Dict[str, Any]] = {
            "default": {
                "ei_type_id": "default",
                "description": "Default enrichment job type",
                "ei_schema": {
                    "type": "object",
                    "required": ["ei_payload"],
                },
                "ei_status_schema": {
                    "type": "object",
                    "required": ["ei_job_id", "delivery_status"],
                },
                "supports_ei_job_creation": True,
            }
        }
        self._ei_jobs: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._notification_destinations: Dict[Tuple[str, str], str] = {}

    @property
    def definition(self) -> A1ServiceDefinition:
        return self.registry.get_service_definition(A1ServiceType.A1_EI)

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
            "supported_ei_types": self.list_ei_type_ids(),
        }

    def list_ei_type_ids(self) -> List[str]:
        """Return known EI type identifiers."""
        with self._lock:
            return sorted(self._ei_types.keys())

    def get_ei_type(self, ei_type_id: str) -> Dict[str, Any]:
        """Return one EI type definition."""
        with self._lock:
            ei_type = self._ei_types.get(ei_type_id)
            if ei_type is None:
                raise KeyError(f"EI type not found: {ei_type_id}")
            return deepcopy(ei_type)

    def list_ei_job_ids(self, ei_type_id: str) -> List[str]:
        """Return EI job identifiers for a given EI type."""
        with self._lock:
            if ei_type_id not in self._ei_types:
                raise KeyError(f"EI type not found: {ei_type_id}")
            return sorted(job_id for (stored_type, job_id) in self._ei_jobs if stored_type == ei_type_id)

    def create_or_replace_ei_job(
        self,
        ei_type_id: str,
        ei_job_id: str,
        ei_job: Dict[str, Any],
        notification_destination: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], bool]:
        """Create or update an EI job record."""
        with self._lock:
            ei_type = self._ei_types.get(ei_type_id)
            if ei_type is None:
                raise KeyError(f"EI type not found: {ei_type_id}")
            if not ei_type.get("supports_ei_job_creation", True):
                raise ValueError(f"EI job creation is not supported for EI type: {ei_type_id}")
            if not isinstance(ei_job, dict):
                raise ValueError("EI job payload must be an object")

            required_fields = ei_type.get("ei_schema", {}).get("required", [])
            missing_fields = [field for field in required_fields if field not in ei_job]
            if missing_fields:
                raise ValueError(
                    "EI job payload missing required fields: " + ", ".join(sorted(missing_fields))
                )

            key = (ei_type_id, ei_job_id)
            was_created = key not in self._ei_jobs
            stored_job = {
                "ei_type_id": ei_type_id,
                "ei_job_id": ei_job_id,
                "ei_job": deepcopy(ei_job),
            }
            self._ei_jobs[key] = stored_job
            if notification_destination is not None:
                self._notification_destinations[key] = notification_destination
            else:
                self._notification_destinations.pop(key, None)

            self._ei_jobs[key]["ei_status"] = {
                "ei_job_id": ei_job_id,
                "delivery_status": "ACCEPTED",
                "delivery_reason": "EI job accepted for evaluation by A1-EI Producer",
                "feedback": [],
            }
            return deepcopy(self._ei_jobs[key]), was_created

    def get_ei_job(self, ei_type_id: str, ei_job_id: str) -> Dict[str, Any]:
        """Get an EI job by type and job id."""
        with self._lock:
            key = (ei_type_id, ei_job_id)
            ei_job = self._ei_jobs.get(key)
            if ei_job is None:
                raise KeyError(f"EI job not found for eiTypeId={ei_type_id}, eiJobId={ei_job_id}")
            return deepcopy(ei_job)

    def delete_ei_job(self, ei_type_id: str, ei_job_id: str) -> None:
        """Delete an EI job and related status/callback metadata."""
        with self._lock:
            key = (ei_type_id, ei_job_id)
            if key not in self._ei_jobs:
                raise KeyError(f"EI job not found for eiTypeId={ei_type_id}, eiJobId={ei_job_id}")

            del self._ei_jobs[key]
            self._notification_destinations.pop(key, None)

    def get_ei_job_status(self, ei_type_id: str, ei_job_id: str) -> Dict[str, Any]:
        """Get EI job delivery status."""
        with self._lock:
            key = (ei_type_id, ei_job_id)
            ei_job = self._ei_jobs.get(key)
            if ei_job is None:
                raise KeyError(f"EI job status not found for eiTypeId={ei_type_id}, eiJobId={ei_job_id}")
            return deepcopy(ei_job["ei_status"])

    async def notify_ei_job_status(self, destination: str, status_obj: Dict[str, Any]) -> None:
        """Send outbound EI job status notification to the consumer callback URI."""
        required_fields = ["ei_job_id", "delivery_status"]
        if not isinstance(status_obj, dict) or any(field not in status_obj for field in required_fields):
            raise ValueError("EI status payload must include ei_job_id and delivery_status")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                destination,
                json=status_obj,
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
        if response.status_code not in (200, 204):
            logger.warning(
                "EI job status notification to %s returned unexpected status %d",
                destination,
                response.status_code,
            )