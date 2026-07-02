"""
Enrichment-information specific A1 service helpers.
"""

import logging
from copy import deepcopy
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

import httpx
from pydantic import ValidationError

from app.models.a1_service import A1ServiceDefinition, A1ServiceType
from app.models.oran import EiJobObject, EiJobResultObject, EiJobStatusObject, EiTypeObject, SpecType
from app.services.a1_service_registry import A1ServiceRegistry

logger = logging.getLogger(__name__)


class A1EnrichmentInformationService:
    """Service-specific metadata and validation for A1-EI."""

    def __init__(self, registry: A1ServiceRegistry | None = None) -> None:
        self.registry = registry or A1ServiceRegistry()
        self._lock = Lock()
        self._ei_types: Dict[str, EiTypeObject] = {
            "default": EiTypeObject(
                ei_type_id="default",
                description="Default enrichment job type",
                ei_schema={
                    "type": "object",
                    "required": ["ei_payload"],
                },
                ei_status_schema={
                    "type": "object",
                    "required": ["ei_job_id", "delivery_status"],
                },
                ei_result_schema={
                    "type": "object",
                    "required": ["ei_job_id", "result_payload"],
                },
                supports_ei_job_creation=True,
            )
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

    def _ei_type_schema(self, ei_type: EiTypeObject | Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(ei_type, EiTypeObject):
            return ei_type.ei_schema
        return ei_type.get("ei_schema", {})

    def _ei_type_supports_job_creation(self, ei_type: EiTypeObject | Dict[str, Any]) -> bool:
        if isinstance(ei_type, EiTypeObject):
            return ei_type.supports_ei_job_creation
        return bool(ei_type.get("supports_ei_job_creation", True))

    def _ei_type_to_dict(self, ei_type: EiTypeObject | Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(ei_type, EiTypeObject):
            return ei_type.model_dump(mode="json")
        return deepcopy(ei_type)

    def get_ei_type(self, ei_type_id: str) -> Dict[str, Any]:
        """Return one EI type definition."""
        with self._lock:
            ei_type = self._ei_types.get(ei_type_id)
            if ei_type is None:
                raise KeyError(f"EI type not found: {ei_type_id}")
            return self._ei_type_to_dict(ei_type)

    def list_ei_job_ids(self, ei_type_id: Optional[str] = None) -> List[str]:
        """Return EI job identifiers, optionally filtered by EI type."""
        with self._lock:
            if ei_type_id is None:
                return sorted({job_id for (_, job_id) in self._ei_jobs})
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
            if not self._ei_type_supports_job_creation(ei_type):
                raise ValueError(f"EI job creation is not supported for EI type: {ei_type_id}")
            if not isinstance(ei_job, dict):
                raise ValueError("EI job payload must be an object")

            required_fields = self._ei_type_schema(ei_type).get("required", [])
            missing_fields = [field for field in required_fields if field not in ei_job]
            if missing_fields:
                raise ValueError(
                    "EI job payload missing required fields: " + ", ".join(sorted(missing_fields))
                )

            key = (ei_type_id, ei_job_id)
            was_created = key not in self._ei_jobs
            existing_job = deepcopy(self._ei_jobs[key]["ei_job"]) if key in self._ei_jobs else {}
            merged_job = existing_job
            merged_job.update(deepcopy(ei_job))

            if notification_destination is not None and "jobStatusNotificationUri" not in merged_job:
                merged_job["jobStatusNotificationUri"] = notification_destination
            elif "jobStatusNotificationUri" not in ei_job:
                merged_job.pop("jobStatusNotificationUri", None)

            if "jobResultUri" not in ei_job and "jobResultUri" in existing_job:
                merged_job["jobResultUri"] = existing_job["jobResultUri"]

            job_model = EiJobObject(
                ei_payload=merged_job.get("ei_payload", {}),
                jobStatusNotificationUri=merged_job.get("jobStatusNotificationUri"),
                jobResultUri=merged_job.get("jobResultUri"),
            )

            stored_job = {
                "ei_type_id": ei_type_id,
                "ei_job_id": ei_job_id,
                "ei_job": job_model.model_dump(mode="json"),
            }
            self._ei_jobs[key] = stored_job

            callback_destination = job_model.jobStatusNotificationUri
            if callback_destination is not None:
                self._notification_destinations[key] = callback_destination
            else:
                self._notification_destinations.pop(key, None)

            self._ei_jobs[key]["ei_status"] = EiJobStatusObject(
                ei_job_id=ei_job_id,
                delivery_status="ACCEPTED",
                delivery_reason="EI job accepted for evaluation by A1-EI Producer",
                feedback=[],
            ).model_dump(mode="json")
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

    def get_ei_job_notification_destination(self, ei_type_id: str, ei_job_id: str) -> Optional[str]:
        """Return the subscribed EI job status notification URI, if present."""
        with self._lock:
            key = (ei_type_id, ei_job_id)
            ei_job = self._ei_jobs.get(key)
            if ei_job is None:
                raise KeyError(f"EI job not found for eiTypeId={ei_type_id}, eiJobId={ei_job_id}")
            return ei_job["ei_job"].get("jobStatusNotificationUri")

    def get_ei_job_result_destination(self, ei_type_id: str, ei_job_id: str) -> Optional[str]:
        """Return the EI job result delivery URI, if present."""
        with self._lock:
            key = (ei_type_id, ei_job_id)
            ei_job = self._ei_jobs.get(key)
            if ei_job is None:
                raise KeyError(f"EI job not found for eiTypeId={ei_type_id}, eiJobId={ei_job_id}")
            return ei_job["ei_job"].get("jobResultUri")

    async def notify_ei_job_status(self, destination: str, status_obj: Dict[str, Any]) -> None:
        """Send outbound EI job status notification to the consumer callback URI."""
        try:
            payload = EiJobStatusObject.model_validate(status_obj)
        except ValidationError as exc:
            raise ValueError("EI status payload must include ei_job_id and delivery_status") from exc

        if not payload.ei_job_id or not payload.delivery_status:
            raise ValueError("EI status payload must include ei_job_id and delivery_status")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                destination,
                json=payload.model_dump(mode="json"),
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
        if response.status_code not in (200, 204):
            logger.warning(
                "EI job status notification to %s returned unexpected status %d",
                destination,
                response.status_code,
            )

    async def deliver_ei_job_result(self, destination: str, result_obj: Dict[str, Any]) -> None:
        """Send outbound EI job result delivery to the consumer callback URI."""
        try:
            payload = EiJobResultObject.model_validate(result_obj)
        except ValidationError as exc:
            raise ValueError("EI result payload must include ei_job_id and result_payload") from exc

        if not payload.ei_job_id:
            raise ValueError("EI result payload must include ei_job_id and result_payload")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                destination,
                json=payload.model_dump(mode="json"),
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
        if response.status_code not in (200, 204):
            logger.warning(
                "EI job result delivery to %s returned unexpected status %d",
                destination,
                response.status_code,
            )