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
from app.models.oran import (
    EiJobObject,
    EiJobResultObject,
    EiJobStatusObject,
    EiTypeObject,
    EiTypeStatusObject,
    SpecType,
)
from app.services.a1_errors import A1ConflictError
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
                    "required": ["eiTypeId", "jobDefinition", "jobResultUri"],
                },
                ei_status_schema={
                    "type": "object",
                    "required": ["eiJobStatus"],
                },
                ei_result_schema={
                    "type": "object",
                    "required": ["jobResult"],
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
            "a1_ml_support": {
                "status": "out_of_scope",
                "reference": "TS 103 983 section 5",
                "note": "A1-EI is implemented in MVP; A1-ML exchange is not included in current scope.",
            },
        }

    def reconcile_ei_jobs_after_restart(self, recovered_job_ids: Optional[List[str]] = None) -> Dict[str, str]:
        """Reconcile EI job lifecycle state after restart without buffering assumptions.

        When recovered_job_ids is provided, jobs not present in this set are marked
        DISABLED so Near-RT RIC can explicitly recreate or update them.
        """
        with self._lock:
            recovered = set(recovered_job_ids or [])
            report: Dict[str, str] = {}
            for (ei_type_id, ei_job_id), record in self._ei_jobs.items():
                if recovered_job_ids is not None and ei_job_id not in recovered:
                    record["ei_status"] = EiJobStatusObject(eiJobStatus="DISABLED").model_dump(mode="json")
                    report[f"{ei_type_id}:{ei_job_id}"] = "DISABLED"
                else:
                    record["ei_status"] = EiJobStatusObject(eiJobStatus="ENABLED").model_dump(mode="json")
                    report[f"{ei_type_id}:{ei_job_id}"] = "ENABLED"
            return report

    def _set_ei_status_by_destination(self, destination: str, status: str) -> None:
        if not destination:
            return

        with self._lock:
            for key, callback in self._notification_destinations.items():
                if callback == destination and key in self._ei_jobs:
                    self._ei_jobs[key]["ei_status"] = EiJobStatusObject(
                        eiJobStatus=status
                    ).model_dump(mode="json")

            for key, record in self._ei_jobs.items():
                if record.get("ei_job", {}).get("jobResultUri") == destination:
                    self._ei_jobs[key]["ei_status"] = EiJobStatusObject(
                        eiJobStatus=status
                    ).model_dump(mode="json")

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

    def get_ei_type_status(self, ei_type_id: str) -> Dict[str, Any]:
        """Return status metadata for one EI type."""
        with self._lock:
            ei_type = self._ei_types.get(ei_type_id)
            if ei_type is None:
                raise KeyError(f"EI type not found: {ei_type_id}")

            supports_creation = self._ei_type_supports_job_creation(ei_type)
            status = "ENABLED" if supports_creation else "DISABLED"
            reason = (
                "EI type is available for EI job create/update operations"
                if supports_creation
                else "EI type is currently unavailable for EI job create/update operations"
            )

            return EiTypeStatusObject(
                eiTypeId=ei_type_id,
                eiTypeStatus=status,
                statusReason=reason,
            ).model_dump(mode="json")

    def list_ei_job_ids(self, ei_type_id: Optional[str] = None) -> List[str]:
        """Return EI job identifiers, optionally filtered by EI type."""
        with self._lock:
            if ei_type_id is None:
                return sorted({job_id for (_, job_id) in self._ei_jobs})
            if ei_type_id not in self._ei_types:
                raise KeyError(f"EI type not found: {ei_type_id}")
            return sorted(job_id for (stored_type, job_id) in self._ei_jobs if stored_type == ei_type_id)

    def _resolve_key_by_job_id(self, ei_job_id: str) -> Tuple[str, str]:
        matching = [key for key in self._ei_jobs if key[1] == ei_job_id]
        if not matching:
            raise KeyError(f"EI job not found for eiJobId={ei_job_id}")
        if len(matching) > 1:
            raise A1ConflictError(
                f"Multiple EI jobs found for eiJobId={ei_job_id}; include eiTypeId to disambiguate"
            )
        return matching[0]

    @staticmethod
    def _normalize_job_definition(ei_job: Dict[str, Any]) -> Dict[str, Any]:
        job_definition = ei_job.get("jobDefinition")
        if not isinstance(job_definition, dict):
            raise ValueError("EI job payload field jobDefinition must be an object")
        return deepcopy(job_definition)

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

            payload_ei_type_id = str(ei_job.get("eiTypeId", ""))
            if not payload_ei_type_id:
                raise ValueError("EI job payload missing required fields: eiTypeId")
            if payload_ei_type_id != ei_type_id:
                raise ValueError(
                    "eiTypeId in EI job payload does not match requested EI type"
                )

            existing_conflicts = [
                key for key in self._ei_jobs if key[1] == ei_job_id and key[0] != ei_type_id
            ]
            if existing_conflicts:
                raise A1ConflictError(
                    f"EI job id already exists under another eiTypeId: {ei_job_id}"
                )

            required_fields = self._ei_type_schema(ei_type).get("required", [])
            missing_fields = [
                field for field in required_fields if ei_job.get(field) in (None, "")
            ]
            if missing_fields:
                raise ValueError(
                    "EI job payload missing required fields: " + ", ".join(sorted(missing_fields))
                )

            key = (ei_type_id, ei_job_id)
            was_created = key not in self._ei_jobs
            existing_job = deepcopy(self._ei_jobs[key]["ei_job"]) if key in self._ei_jobs else {}
            merged_job = deepcopy(existing_job)
            merged_job.update(deepcopy(ei_job))

            merged_job["eiTypeId"] = payload_ei_type_id
            merged_job["jobDefinition"] = self._normalize_job_definition(merged_job)

            if notification_destination is not None and "jobStatusNotificationUri" not in merged_job:
                merged_job["jobStatusNotificationUri"] = notification_destination
            elif "jobStatusNotificationUri" not in ei_job:
                merged_job.pop("jobStatusNotificationUri", None)

            if "jobResultUri" not in ei_job and "jobResultUri" in existing_job:
                merged_job["jobResultUri"] = existing_job["jobResultUri"]

            job_model = EiJobObject(
                eiTypeId=payload_ei_type_id,
                jobDefinition=merged_job.get("jobDefinition", {}),
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
                eiJobStatus="ENABLED",
            ).model_dump(mode="json")
            return deepcopy(self._ei_jobs[key]), was_created

    def get_ei_job_by_id(self, ei_job_id: str) -> Dict[str, Any]:
        """Get an EI job by EI job identifier only (Annex A canonical path)."""
        with self._lock:
            key = self._resolve_key_by_job_id(ei_job_id)
            return deepcopy(self._ei_jobs[key])

    def delete_ei_job_by_id(self, ei_job_id: str) -> None:
        """Delete an EI job by EI job identifier only (Annex A canonical path)."""
        with self._lock:
            key = self._resolve_key_by_job_id(ei_job_id)
            if key not in self._ei_jobs:
                raise KeyError(f"EI job not found for eiJobId={ei_job_id}")
            del self._ei_jobs[key]
            self._notification_destinations.pop(key, None)

    def get_ei_job_status_by_id(self, ei_job_id: str) -> Dict[str, Any]:
        """Get EI job status by EI job identifier only (Annex A canonical path)."""
        with self._lock:
            key = self._resolve_key_by_job_id(ei_job_id)
            ei_job = self._ei_jobs.get(key)
            if ei_job is None:
                raise KeyError(f"EI job status not found for eiJobId={ei_job_id}")
            return deepcopy(ei_job["ei_status"])

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
            raise ValueError("EI status payload must include eiJobStatus") from exc

        if not payload.eiJobStatus:
            raise ValueError("EI status payload must include eiJobStatus")

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
            # Section-5 resilience behavior: do not buffer failed callbacks; mark as disabled.
            self._set_ei_status_by_destination(destination, "DISABLED")

    async def deliver_ei_job_result(self, destination: str, result_obj: Dict[str, Any]) -> None:
        """Send outbound EI job result delivery to the consumer callback URI."""
        try:
            payload = EiJobResultObject.model_validate(result_obj)
        except ValidationError as exc:
            raise ValueError("EI result payload must include jobResult") from exc

        if payload.jobResult in (None, {}):
            raise ValueError("EI result payload must include jobResult")

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
            # Section-5 resilience behavior: do not buffer failed deliveries; mark as disabled.
            self._set_ei_status_by_destination(destination, "DISABLED")

    async def notify_ei_type_status(self, destination: str, status_obj: Dict[str, Any]) -> None:
        """Send outbound EI-type status notification to the consumer callback URI."""
        try:
            payload = EiTypeStatusObject.model_validate(status_obj)
        except ValidationError as exc:
            raise ValueError("EI type status payload must include eiTypeId and eiTypeStatus") from exc

        async with httpx.AsyncClient() as client:
            response = await client.post(
                destination,
                json=payload.model_dump(mode="json"),
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
        if response.status_code not in (200, 204):
            logger.warning(
                "EI type status notification to %s returned unexpected status %d",
                destination,
                response.status_code,
            )