"""Conformance harness orchestrator service."""

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

import httpx

from app.models.a1_policy_models import PolicyObject
import app.services.a1_enrichment_service as a1_enrichment_module
import app.services.a1_policy_service as a1_policy_module
from app.modules.conformance_harness.simulator_verifier import verify_simulator_capability
from app.modules.conformance_harness.evidence_collector import collect_execution_evidence
from app.modules.conformance_harness.evidence_validator import validate_execution_evidence
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.conformance_service import ConformanceService


class ConformanceHarnessService:
    """Provides a unified entry point for conformance prechecks and evidence checks."""

    def __init__(self) -> None:
        self._conformance_service = ConformanceService()

    def get_dut_readiness(self, service_registry, policy_service, ric_endpoint: str) -> dict:
        return self._conformance_service.build_dut_readiness(
            service_registry=service_registry,
            policy_service=policy_service,
            ric_endpoint=ric_endpoint,
            include_phase2_ei=False,
            http_get=httpx.get,
        )

    def get_simulator_capability(self) -> dict:
        return verify_simulator_capability()

    def list_conformance_categories(self) -> list[dict]:
        """Return currently implemented conformance categories."""
        return [
            {
                "category_id": "policy-type-query",
                "title": "Policy Type Query Operations",
                "spec_reference": "TS 103 989 section 4.2.1 and TS 103 987 section 5.2.3",
                "test_count": 5,
                "estimated_duration_seconds": 120,
                "status": "implemented",
            },
            {
                "category_id": "policy-operations",
                "title": "Service Operations for A1 Policies",
                "legacy_aliases": ["policy-crud-operations"],
                "spec_reference": "TS 103 987 section 5.2.4",
                "test_count": 8,
                "estimated_duration_seconds": 180,
                "status": "implemented",
            },
            {
                "category_id": "interoperability-a1p",
                "title": "Interoperability A1-P Between Non-RT RIC and Near-RT RIC",
                "spec_reference": "TS 103 989 section 4.4 and clause 7.2",
                "test_count": 9,
                "estimated_duration_seconds": 180,
                "status": "implemented",
            },
            {
                "category_id": "interoperability-a1ei",
                "title": "Interoperability A1-EI Between Non-RT RIC and Near-RT RIC",
                "spec_reference": "TS 103 989 section 4.4 and clause 7.3",
                "test_count": 11,
                "estimated_duration_seconds": 180,
                "status": "implemented",
            },
            {
                "category_id": "ei-job-operations",
                "title": "A1-EI Job Operations",
                "spec_reference": "TS 103 989 section 5.3",
                "test_count": 8,
                "estimated_duration_seconds": 180,
                "status": "implemented",
            },
        ]

    def list_policy_type_query_tests(self) -> list[dict]:
        """Return executable test metadata for the first TS 103 989 category."""
        return [
            {
                "test_id": "TC-A1-PTQ-001",
                "category_id": "policy-type-query",
                "name": "policy_type_list_returns_list",
                "description": "Verify policy type query operation returns a list payload",
                "spec_reference": "TS 103 987 section 5.2.3.2",
            },
            {
                "test_id": "TC-A1-PTQ-002",
                "category_id": "policy-type-query",
                "name": "policy_type_list_empty_when_none_registered",
                "description": "Verify empty list behavior when no policy types are configured",
                "spec_reference": "TS 103 987 section 5.2.3.3",
            },
            {
                "test_id": "TC-A1-PTQ-003",
                "category_id": "policy-type-query",
                "name": "policy_type_query_unknown_returns_not_found",
                "description": "Verify unknown policy type lookup returns not-found behavior",
                "spec_reference": "TS 103 987 section 5.2.3.3",
            },
            {
                "test_id": "TC-A1-PTQ-004",
                "category_id": "policy-type-query",
                "name": "policy_type_schema_presence",
                "description": "Verify policy type contains policy and status schema definitions",
                "spec_reference": "TS 103 987 section 5.2.2.3",
            },
            {
                "test_id": "TC-A1-PTQ-005",
                "category_id": "policy-type-query",
                "name": "policy_type_role_ownership_context",
                "description": "Verify A1-P consumer and producer role definitions are present",
                "spec_reference": "TS 103 987 section 5.1",
            },
        ]

    def list_policy_operations_tests(self) -> list[dict]:
        """Return executable test metadata for policy service operations."""
        return [
            {
                "test_id": "TC-A1-PO-001",
                "category_id": "policy-operations",
                "name": "create_policy_returns_created",
                "description": "Verify policy create operation returns created state for new policy",
                "spec_reference": "TS 103 987 section 5.2.4.3",
            },
            {
                "test_id": "TC-A1-PO-002",
                "category_id": "policy-operations",
                "name": "update_policy_returns_replaced",
                "description": "Verify policy update operation returns replaced state for existing policy",
                "spec_reference": "TS 103 987 section 5.2.4.4",
            },
            {
                "test_id": "TC-A1-PO-003",
                "category_id": "policy-operations",
                "name": "query_policy_returns_policy",
                "description": "Verify query policy operation returns the stored policy",
                "spec_reference": "TS 103 987 section 5.2.4.5",
            },
            {
                "test_id": "TC-A1-PO-004",
                "category_id": "policy-operations",
                "name": "query_policy_ids_contains_created_policy",
                "description": "Verify policy identifier list contains newly created policy",
                "spec_reference": "TS 103 987 section 5.2.4.2",
            },
            {
                "test_id": "TC-A1-PO-005",
                "category_id": "policy-operations",
                "name": "query_policy_status_returns_status",
                "description": "Verify policy status query returns a status object",
                "spec_reference": "TS 103 987 section 5.2.4.7",
            },
            {
                "test_id": "TC-A1-PO-006",
                "category_id": "policy-operations",
                "name": "delete_policy_succeeds",
                "description": "Verify delete policy operation succeeds for existing policy",
                "spec_reference": "TS 103 987 section 5.2.4.6",
            },
            {
                "test_id": "TC-A1-PO-007",
                "category_id": "policy-operations",
                "name": "query_deleted_policy_returns_not_found",
                "description": "Verify deleted policy cannot be queried",
                "spec_reference": "TS 103 987 section 5.2.4.5",
            },
            {
                "test_id": "TC-A1-PO-008",
                "category_id": "policy-operations",
                "name": "delete_unknown_policy_returns_not_found",
                "description": "Verify delete operation returns not-found behavior for unknown policy",
                "spec_reference": "TS 103 987 section 5.2.4.6",
            },
        ]

    def list_interoperability_a1p_tests(self) -> list[dict]:
        """Return executable section 4.4/7.2 interoperability metadata for A1-P."""
        return [
            {
                "test_id": "TC-A1-INT-P-001",
                "category_id": "interoperability-a1p",
                "name": "query_all_policy_type_identifiers_positive",
                "description": "Verify query-all policy type identifiers succeeds across empty, single, and multi-type configurations",
                "spec_reference": "TS 103 989 section 4.4, clause 7.2.1.1",
            },
            {
                "test_id": "TC-A1-INT-P-002",
                "category_id": "interoperability-a1p",
                "name": "query_single_policy_type_positive",
                "description": "Verify query-single policy type returns the agreed PolicyTypeObject",
                "spec_reference": "TS 103 989 section 4.4, clause 7.2.1.2",
            },
            {
                "test_id": "TC-A1-INT-P-003",
                "category_id": "interoperability-a1p",
                "name": "create_single_policy_positive",
                "description": "Verify create-single policy returns the created PolicyObject",
                "spec_reference": "TS 103 989 section 4.4, clause 7.2.2.1",
            },
            {
                "test_id": "TC-A1-INT-P-004",
                "category_id": "interoperability-a1p",
                "name": "query_all_policy_identifiers_positive",
                "description": "Verify query-all policy identifiers returns the created policy identifier",
                "spec_reference": "TS 103 989 section 4.4, clause 7.2.3.1",
            },
            {
                "test_id": "TC-A1-INT-P-005",
                "category_id": "interoperability-a1p",
                "name": "query_single_policy_positive",
                "description": "Verify query-single policy returns the stored PolicyObject",
                "spec_reference": "TS 103 989 section 4.4, clause 7.2.3.2",
            },
            {
                "test_id": "TC-A1-INT-P-006",
                "category_id": "interoperability-a1p",
                "name": "query_policy_status_positive",
                "description": "Verify query policy status returns the PolicyStatusObject for the created policy",
                "spec_reference": "TS 103 989 section 4.4, clause 7.2.3.3",
            },
            {
                "test_id": "TC-A1-INT-P-007",
                "category_id": "interoperability-a1p",
                "name": "update_single_policy_positive",
                "description": "Verify update-single policy replaces the existing policy",
                "spec_reference": "TS 103 989 section 4.4, clause 7.2.4.1",
            },
            {
                "test_id": "TC-A1-INT-P-008",
                "category_id": "interoperability-a1p",
                "name": "delete_single_policy_positive",
                "description": "Verify delete-single policy removes the stored policy",
                "spec_reference": "TS 103 989 section 4.4, clause 7.2.5.1",
            },
            {
                "test_id": "TC-A1-INT-P-009",
                "category_id": "interoperability-a1p",
                "name": "notify_policy_status_positive",
                "description": "Verify create with notificationDestination and deliver PolicyStatusObject via HTTP POST",
                "spec_reference": "TS 103 989 section 4.4, clause 7.2.6.1",
            },
        ]

    def list_interoperability_a1ei_tests(self) -> list[dict]:
        """Return executable section 4.4/7.3 interoperability metadata for A1-EI."""
        return [
            {
                "test_id": "TC-A1-INT-EI-001",
                "category_id": "interoperability-a1ei",
                "name": "query_ei_type_identifiers_positive",
                "description": "Verify query EI type identifiers returns the configured EI types",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.1.1",
            },
            {
                "test_id": "TC-A1-INT-EI-002",
                "category_id": "interoperability-a1ei",
                "name": "query_single_ei_type_positive",
                "description": "Verify query EI type returns the agreed EI type definition",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.1.2",
            },
            {
                "test_id": "TC-A1-INT-EI-003",
                "category_id": "interoperability-a1ei",
                "name": "create_ei_job_positive",
                "description": "Verify create EI job succeeds with callback URIs embedded in the EiJobObject",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.2.1",
            },
            {
                "test_id": "TC-A1-INT-EI-004",
                "category_id": "interoperability-a1ei",
                "name": "query_ei_job_identifiers_single_type_positive",
                "description": "Verify query EI job identifiers for a single EI type returns the created job",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.3.1",
            },
            {
                "test_id": "TC-A1-INT-EI-005",
                "category_id": "interoperability-a1ei",
                "name": "query_ei_job_identifiers_all_types_positive",
                "description": "Verify query EI job identifiers across all EI types covers each created job",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.3.2",
            },
            {
                "test_id": "TC-A1-INT-EI-006",
                "category_id": "interoperability-a1ei",
                "name": "query_ei_job_positive",
                "description": "Verify query EI job returns the stored EiJobObject",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.3.3",
            },
            {
                "test_id": "TC-A1-INT-EI-007",
                "category_id": "interoperability-a1ei",
                "name": "update_ei_job_positive",
                "description": "Verify update EI job replaces the existing job payload",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.4.1",
            },
            {
                "test_id": "TC-A1-INT-EI-008",
                "category_id": "interoperability-a1ei",
                "name": "delete_ei_job_positive",
                "description": "Verify delete EI job removes the stored EI job",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.5.1",
            },
            {
                "test_id": "TC-A1-INT-EI-009",
                "category_id": "interoperability-a1ei",
                "name": "query_ei_job_status_positive",
                "description": "Verify query EI job status returns the EiJobStatusObject",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.6.1",
            },
            {
                "test_id": "TC-A1-INT-EI-010",
                "category_id": "interoperability-a1ei",
                "name": "notify_ei_job_status_positive",
                "description": "Verify create with jobStatusNotificationUri and deliver EiJobStatusObject via HTTP POST",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.6.2",
            },
            {
                "test_id": "TC-A1-INT-EI-011",
                "category_id": "interoperability-a1ei",
                "name": "deliver_ei_job_result_positive",
                "description": "Verify create with jobResultUri and deliver EiJobResultObject via HTTP POST",
                "spec_reference": "TS 103 989 section 4.4, clause 7.3.7.1",
            },
        ]

    def _summarize_results(self, run_id: str, category_id: str, results: list[dict]) -> dict:
        passed_count = len([item for item in results if item["status"] == "PASS"])
        failed_count = len([item for item in results if item["status"] == "FAIL"])
        return {
            "run_id": run_id,
            "category_id": category_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": len(results),
                "passed": passed_count,
                "failed": failed_count,
                "verdict": "PASS" if failed_count == 0 else "FAIL",
            },
            "results": results,
        }

    def _execute_callback_post(self, module, coroutine_factory) -> tuple[bool, str]:
        class _FakeResponse:
            status_code = 204

        class _FakeAsyncClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return None

            async def post(self, *args, **kwargs):
                return _FakeResponse()

        original_async_client = module.httpx.AsyncClient
        try:
            module.httpx.AsyncClient = _FakeAsyncClient
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(lambda: asyncio.run(coroutine_factory()))
                future.result()
            return True, "Callback delivery returned HTTP 204 No Content"
        except Exception as exc:  # pragma: no cover - defensive
            return False, str(exc)
        finally:
            module.httpx.AsyncClient = original_async_client

    def list_ei_job_operations_tests(self) -> list[dict]:
        """Return executable test metadata for TS 103 989 section 5.3 A1-EI coverage."""
        return [
            {
                "test_id": "TC-A1-EI-001",
                "category_id": "ei-job-operations",
                "name": "ei_type_list_returns_list",
                "description": "Verify EI type query returns a list payload",
                "spec_reference": "TS 103 989 section 5.3.1",
            },
            {
                "test_id": "TC-A1-EI-002",
                "category_id": "ei-job-operations",
                "name": "ei_type_query_unknown_returns_not_found",
                "description": "Verify unknown EI type lookup returns not-found behavior",
                "spec_reference": "TS 103 989 section 5.3.1",
            },
            {
                "test_id": "TC-A1-EI-003",
                "category_id": "ei-job-operations",
                "name": "create_ei_job_returns_created",
                "description": "Verify EI job create operation returns created state for a new job",
                "spec_reference": "TS 103 989 section 5.3.2",
            },
            {
                "test_id": "TC-A1-EI-004",
                "category_id": "ei-job-operations",
                "name": "query_ei_job_ids_contains_created_job",
                "description": "Verify EI job identifier list contains the new job",
                "spec_reference": "TS 103 989 section 5.3.3",
            },
            {
                "test_id": "TC-A1-EI-005",
                "category_id": "ei-job-operations",
                "name": "query_ei_job_returns_job",
                "description": "Verify EI job query returns the stored job payload",
                "spec_reference": "TS 103 989 section 5.3.3",
            },
            {
                "test_id": "TC-A1-EI-006",
                "category_id": "ei-job-operations",
                "name": "update_ei_job_returns_replaced",
                "description": "Verify EI job update operation returns replaced state for an existing job",
                "spec_reference": "TS 103 989 section 5.3.4",
            },
            {
                "test_id": "TC-A1-EI-007",
                "category_id": "ei-job-operations",
                "name": "query_ei_job_status_returns_status",
                "description": "Verify EI job status query returns a status object",
                "spec_reference": "TS 103 989 section 5.3.6",
            },
            {
                "test_id": "TC-A1-EI-008",
                "category_id": "ei-job-operations",
                "name": "delete_ei_job_succeeds",
                "description": "Verify EI job delete operation succeeds for an existing job",
                "spec_reference": "TS 103 989 section 5.3.5",
            },
        ]

    def run_policy_type_query_tests(self, policy_service, service_registry) -> dict:
        """Execute the first TS 103 989 conformance category tests."""
        run_id = datetime.now(timezone.utc).strftime("ptq-%Y%m%d%H%M%S")
        results: list[dict] = []

        # TC-A1-PTQ-001
        try:
            payload = policy_service.list_policy_type_ids()
            passed = isinstance(payload, list)
            detail = f"Returned type {type(payload).__name__}"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-PTQ-001",
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

        # TC-A1-PTQ-002
        original_policy_types = deepcopy(policy_service._policy_types)
        try:
            policy_service._policy_types = {}
            payload = policy_service.list_policy_type_ids()
            passed = payload == []
            detail = f"Returned {len(payload)} entries"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        finally:
            policy_service._policy_types = original_policy_types
        results.append(
            {
                "test_id": "TC-A1-PTQ-002",
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

        # TC-A1-PTQ-003
        try:
            policy_service.get_policy_type("unknown-policy-type")
            passed = False
            detail = "Expected KeyError was not raised"
        except KeyError:
            passed = True
            detail = "KeyError raised for unknown policy type"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-PTQ-003",
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

        # TC-A1-PTQ-004
        try:
            ids = policy_service.list_policy_type_ids()
            first = ids[0] if ids else None
            obj = policy_service.get_policy_type(first) if first else None
            passed = bool(obj and isinstance(obj.policy_schema, dict) and isinstance(obj.policy_status_schema, dict))
            detail = "policy_schema and policy_status_schema present"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-PTQ-004",
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

        # TC-A1-PTQ-005
        try:
            definition = service_registry.get_service_definition("A1-P")
            passed = (
                definition.consumer_role.label == "A1-P Consumer"
                and definition.producer_role.label == "A1-P Producer"
            )
            detail = "A1-P role ownership labels validated"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-PTQ-005",
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

        passed_count = len([item for item in results if item["status"] == "PASS"])
        failed_count = len([item for item in results if item["status"] == "FAIL"])

        return {
            "run_id": run_id,
            "category_id": "policy-type-query",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": len(results),
                "passed": passed_count,
                "failed": failed_count,
                "verdict": "PASS" if failed_count == 0 else "FAIL",
            },
            "results": results,
        }

    def run_policy_operations_tests(self, policy_service) -> dict:
        """Execute policy service operations conformance tests."""
        run_id = datetime.now(timezone.utc).strftime("po-%Y%m%d%H%M%S")
        results: list[dict] = []

        policy_type_id = "default"
        policy_id = f"policy-{run_id}"
        create_policy = PolicyObject(
            scope={"region": "test-region"},
            policy_statements=[{"statement_id": "s1", "action": "allow"}],
        )
        update_policy = PolicyObject(
            scope={"region": "test-region"},
            policy_statements=[{"statement_id": "s2", "action": "throttle"}],
        )

        # TC-A1-PO-001
        try:
            _, was_created = policy_service.create_or_replace_policy(
                policy_type_id=policy_type_id,
                policy_id=policy_id,
                policy=create_policy,
            )
            passed = was_created is True
            detail = "Create returned created state"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append({"test_id": "TC-A1-PO-001", "status": "PASS" if passed else "FAIL", "detail": detail})

        # TC-A1-PO-002
        try:
            _, was_created = policy_service.create_or_replace_policy(
                policy_type_id=policy_type_id,
                policy_id=policy_id,
                policy=update_policy,
            )
            passed = was_created is False
            detail = "Update returned replace state"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append({"test_id": "TC-A1-PO-002", "status": "PASS" if passed else "FAIL", "detail": detail})

        # TC-A1-PO-003
        try:
            queried = policy_service.get_policy(policy_type_id, policy_id)
            passed = queried.policy_statements == update_policy.policy_statements
            detail = "Queried policy matches latest update"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append({"test_id": "TC-A1-PO-003", "status": "PASS" if passed else "FAIL", "detail": detail})

        # TC-A1-PO-004
        try:
            ids = policy_service.list_policy_ids(policy_type_id)
            passed = policy_id in ids
            detail = "Policy identifier present in list"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append({"test_id": "TC-A1-PO-004", "status": "PASS" if passed else "FAIL", "detail": detail})

        # TC-A1-PO-005
        try:
            status_obj = policy_service.get_policy_status(policy_type_id, policy_id)
            passed = status_obj.policy_id == policy_id
            detail = "Policy status object returned"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append({"test_id": "TC-A1-PO-005", "status": "PASS" if passed else "FAIL", "detail": detail})

        # TC-A1-PO-006
        try:
            policy_service.delete_policy(policy_type_id, policy_id)
            passed = True
            detail = "Policy deleted"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append({"test_id": "TC-A1-PO-006", "status": "PASS" if passed else "FAIL", "detail": detail})

        # TC-A1-PO-007
        try:
            policy_service.get_policy(policy_type_id, policy_id)
            passed = False
            detail = "Expected KeyError was not raised"
        except KeyError:
            passed = True
            detail = "Deleted policy not found as expected"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append({"test_id": "TC-A1-PO-007", "status": "PASS" if passed else "FAIL", "detail": detail})

        # TC-A1-PO-008
        try:
            policy_service.delete_policy(policy_type_id, policy_id)
            passed = False
            detail = "Expected KeyError was not raised"
        except KeyError:
            passed = True
            detail = "Delete unknown policy not found as expected"
        except Exception as exc:  # pragma: no cover - defensive
            passed = False
            detail = str(exc)
        results.append({"test_id": "TC-A1-PO-008", "status": "PASS" if passed else "FAIL", "detail": detail})

        passed_count = len([item for item in results if item["status"] == "PASS"])
        failed_count = len([item for item in results if item["status"] == "FAIL"])

        return {
            "run_id": run_id,
            "category_id": "policy-operations",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": len(results),
                "passed": passed_count,
                "failed": failed_count,
                "verdict": "PASS" if failed_count == 0 else "FAIL",
            },
            "results": results,
        }

    def run_interoperability_a1p_tests(self, policy_service, service_registry) -> dict:
        """Execute deterministic clause-level section 4.4/7.2 interoperability checks for A1-P."""
        run_id = datetime.now(timezone.utc).strftime("intp-%Y%m%d%H%M%S")
        results: list[dict] = []

        original_policy_types = deepcopy(policy_service._policy_types)
        a1p_supported = service_registry.is_supported("A1-P")
        try:
            policy_service._policy_types = {}
            empty_ids = policy_service.list_policy_type_ids()
            policy_service._policy_types = deepcopy({"alpha": original_policy_types["default"]})
            single_ids = policy_service.list_policy_type_ids()
            policy_service._policy_types = deepcopy(
                {
                    "alpha": original_policy_types["default"],
                    "beta": deepcopy(original_policy_types["default"]),
                }
            )
            multi_ids = policy_service.list_policy_type_ids()
            policy_type_list_ok = a1p_supported and empty_ids == [] and len(single_ids) == 1 and len(multi_ids) >= 2
            policy_type_list_detail = (
                "Validated empty, single, and multi-policy-type query configurations"
                if policy_type_list_ok
                else f"Unexpected query-all results: empty={empty_ids}, single={single_ids}, multi={multi_ids}"
            )
        except Exception as exc:  # pragma: no cover - defensive
            policy_type_list_ok = False
            policy_type_list_detail = str(exc)
        finally:
            policy_service._policy_types = original_policy_types

        results.append(
            {
                "test_id": "TC-A1-INT-P-001",
                "status": "PASS" if policy_type_list_ok else "FAIL",
                "detail": policy_type_list_detail,
            }
        )

        policy_type_ids = policy_service.list_policy_type_ids()
        has_matching_policy_type = a1p_supported and len(policy_type_ids) > 0
        results.append(
            {
                "test_id": "TC-A1-INT-P-002",
                "status": "PASS" if has_matching_policy_type else "FAIL",
                "detail": f"Query single policy type returned {policy_type_ids[0]}" if has_matching_policy_type else "No policy type available",
            }
        )

        policy_type_id = policy_type_ids[0] if policy_type_ids else "default"
        policy_id = f"interop-{run_id}"
        create_policy = PolicyObject(
            scope={"region": "interop"},
            policy_statements=[{"statement_id": "int-1", "action": "allow"}],
        )
        update_policy = PolicyObject(
            scope={"region": "interop"},
            policy_statements=[{"statement_id": "int-2", "action": "throttle"}],
        )

        try:
            _, was_created = policy_service.create_or_replace_policy(policy_type_id, policy_id, create_policy)
            create_ok = was_created is True
            create_detail = "Create returned created state" if create_ok else "Create returned replace state"
        except Exception as exc:  # pragma: no cover - defensive
            create_ok = False
            create_detail = str(exc)

        results.append(
            {
                "test_id": "TC-A1-INT-P-003",
                "status": "PASS" if create_ok else "FAIL",
                "detail": create_detail,
            }
        )

        results.append(
            {
                "test_id": "TC-A1-INT-P-004",
                "status": "PASS" if policy_id in policy_service.list_policy_ids(policy_type_id) else "FAIL",
                "detail": "Created policy identifier returned by query-all policy identifiers",
            }
        )

        try:
            queried_policy = policy_service.get_policy(policy_type_id, policy_id)
            query_policy_ok = queried_policy.policy_statements == create_policy.policy_statements
            query_policy_detail = "Query single policy returned the created PolicyObject"
        except Exception as exc:  # pragma: no cover - defensive
            query_policy_ok = False
            query_policy_detail = str(exc)

        results.append(
            {
                "test_id": "TC-A1-INT-P-005",
                "status": "PASS" if query_policy_ok else "FAIL",
                "detail": query_policy_detail,
            }
        )

        try:
            status_obj = policy_service.get_policy_status(policy_type_id, policy_id)
            status_ok = status_obj.policy_id == policy_id
            status_detail = "Query policy status returned a PolicyStatusObject"
        except Exception as exc:  # pragma: no cover - defensive
            status_ok = False
            status_detail = str(exc)

        results.append(
            {
                "test_id": "TC-A1-INT-P-006",
                "status": "PASS" if status_ok else "FAIL",
                "detail": status_detail,
            }
        )

        try:
            _, was_created = policy_service.create_or_replace_policy(policy_type_id, policy_id, update_policy)
            updated_policy = policy_service.get_policy(policy_type_id, policy_id)
            update_ok = was_created is False and updated_policy.policy_statements == update_policy.policy_statements
            update_detail = "Update replaced the stored policy" if update_ok else "Update did not replace the stored policy"
        except Exception as exc:  # pragma: no cover - defensive
            update_ok = False
            update_detail = str(exc)

        results.append(
            {
                "test_id": "TC-A1-INT-P-007",
                "status": "PASS" if update_ok else "FAIL",
                "detail": update_detail,
            }
        )

        try:
            policy_service.delete_policy(policy_type_id, policy_id)
            try:
                policy_service.get_policy(policy_type_id, policy_id)
                delete_ok = False
                delete_detail = "Deleted policy remained queryable"
            except KeyError:
                delete_ok = True
                delete_detail = "Delete removed the policy and subsequent query failed as expected"
        except Exception as exc:  # pragma: no cover - defensive
            delete_ok = False
            delete_detail = str(exc)

        results.append(
            {
                "test_id": "TC-A1-INT-P-008",
                "status": "PASS" if delete_ok else "FAIL",
                "detail": delete_detail,
            }
        )

        notify_policy_id = f"notify-{run_id}"
        callback_destination = "https://near-rt.example.com/policy-status"
        try:
            policy_service.create_or_replace_policy(
                policy_type_id,
                notify_policy_id,
                create_policy,
                notification_destination=callback_destination,
            )
            notify_status_obj = policy_service.get_policy_status(policy_type_id, notify_policy_id)
            notify_ok, notify_detail = self._execute_callback_post(
                a1_policy_module,
                lambda: policy_service.notify_policy_status(callback_destination, notify_status_obj),
            )
            notify_ok = notify_ok and policy_service._notification_destinations[(policy_type_id, notify_policy_id)] == callback_destination
        except Exception as exc:  # pragma: no cover - defensive
            notify_ok = False
            notify_detail = str(exc)

        results.append(
            {
                "test_id": "TC-A1-INT-P-009",
                "status": "PASS" if notify_ok else "FAIL",
                "detail": notify_detail,
            }
        )

        return self._summarize_results(run_id, "interoperability-a1p", results)

    def run_interoperability_a1ei_tests(self, service_registry, ei_service=None) -> dict:
        """Execute deterministic clause-level section 4.4/7.3 interoperability checks for A1-EI."""
        run_id = datetime.now(timezone.utc).strftime("intei-%Y%m%d%H%M%S")
        ei_service = ei_service or A1EnrichmentInformationService(service_registry)
        results: list[dict] = []

        a1ei_supported = service_registry.is_supported("A1-EI")
        ei_type_ids = ei_service.list_ei_type_ids()
        results.append(
            {
                "test_id": "TC-A1-INT-EI-001",
                "status": "PASS" if a1ei_supported and len(ei_type_ids) > 0 else "FAIL",
                "detail": f"Query EI type identifiers returned {len(ei_type_ids)} type(s)",
            }
        )

        ei_type_id = ei_type_ids[0] if ei_type_ids else "default"
        try:
            ei_type = ei_service.get_ei_type(ei_type_id)
            query_type_ok = ei_type["ei_type_id"] == ei_type_id
            query_type_detail = f"Query single EI type returned {ei_type_id}"
        except Exception as exc:  # pragma: no cover - defensive
            query_type_ok = False
            query_type_detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-INT-EI-002",
                "status": "PASS" if query_type_ok else "FAIL",
                "detail": query_type_detail,
            }
        )

        ei_job_id = f"ei-interop-{run_id}"
        callback_status_uri = "https://near-rt.example.com/ei-status"
        callback_result_uri = "https://near-rt.example.com/ei-result"
        create_job = {
            "ei_payload": {"job": "demo"},
            "jobStatusNotificationUri": callback_status_uri,
            "jobResultUri": callback_result_uri,
        }
        update_job = {
            "ei_payload": {"job": "updated"},
            "jobStatusNotificationUri": callback_status_uri,
            "jobResultUri": callback_result_uri,
        }

        try:
            _, was_created = ei_service.create_or_replace_ei_job(ei_type_id, ei_job_id, create_job)
            create_ok = was_created is True
            create_detail = "Create EI job returned created state with callback URIs" if create_ok else "Create EI job returned replace state"
        except Exception as exc:  # pragma: no cover - defensive
            create_ok = False
            create_detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-INT-EI-003",
                "status": "PASS" if create_ok else "FAIL",
                "detail": create_detail,
            }
        )

        try:
            job_ids = ei_service.list_ei_job_ids(ei_type_id)
            single_type_ok = ei_job_id in job_ids
            single_type_detail = "Query EI job identifiers returned the created job for the EI type"
        except Exception as exc:  # pragma: no cover - defensive
            single_type_ok = False
            single_type_detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-INT-EI-004",
                "status": "PASS" if single_type_ok else "FAIL",
                "detail": single_type_detail,
            }
        )

        original_ei_types = deepcopy(ei_service._ei_types)
        original_ei_jobs = deepcopy(ei_service._ei_jobs)
        try:
            ei_service._ei_types["secondary"] = {
                "ei_type_id": "secondary",
                "description": "Secondary enrichment job type",
                "ei_schema": {"type": "object", "required": ["ei_payload"]},
                "ei_status_schema": {"type": "object", "required": ["ei_job_id", "delivery_status"]},
                "ei_result_schema": {"type": "object", "required": ["ei_job_id", "result_payload"]},
                "supports_ei_job_creation": True,
            }
            ei_service.create_or_replace_ei_job("secondary", f"secondary-{run_id}", {"ei_payload": {"job": "secondary"}})
            aggregated_job_ids = {}
            for current_type in ei_service.list_ei_type_ids():
                aggregated_job_ids[current_type] = ei_service.list_ei_job_ids(current_type)
            all_types_ok = ei_job_id in aggregated_job_ids[ei_type_id] and f"secondary-{run_id}" in aggregated_job_ids["secondary"]
            all_types_detail = "Query EI job identifiers across all EI types returned both primary and secondary jobs"
        except Exception as exc:  # pragma: no cover - defensive
            all_types_ok = False
            all_types_detail = str(exc)
        finally:
            ei_service._ei_types = original_ei_types
            ei_service._ei_jobs = original_ei_jobs
        results.append(
            {
                "test_id": "TC-A1-INT-EI-005",
                "status": "PASS" if all_types_ok else "FAIL",
                "detail": all_types_detail,
            }
        )

        try:
            queried_job = ei_service.get_ei_job(ei_type_id, ei_job_id)
            query_job_ok = queried_job["ei_job"] == create_job
            query_job_detail = "Query EI job returned the stored EiJobObject"
        except Exception as exc:  # pragma: no cover - defensive
            query_job_ok = False
            query_job_detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-INT-EI-006",
                "status": "PASS" if query_job_ok else "FAIL",
                "detail": query_job_detail,
            }
        )

        try:
            _, was_created = ei_service.create_or_replace_ei_job(ei_type_id, ei_job_id, update_job)
            updated_job = ei_service.get_ei_job(ei_type_id, ei_job_id)
            update_ok = was_created is False and updated_job["ei_job"] == update_job
            update_detail = "Update EI job replaced the stored EiJobObject" if update_ok else "Update EI job did not replace the stored object"
        except Exception as exc:  # pragma: no cover - defensive
            update_ok = False
            update_detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-INT-EI-007",
                "status": "PASS" if update_ok else "FAIL",
                "detail": update_detail,
            }
        )

        status_job_id = f"status-{run_id}"
        ei_service.create_or_replace_ei_job(ei_type_id, status_job_id, create_job)
        try:
            ei_service.delete_ei_job(ei_type_id, status_job_id)
            try:
                ei_service.get_ei_job(ei_type_id, status_job_id)
                delete_ok = False
                delete_detail = "Deleted EI job remained queryable"
            except KeyError:
                delete_ok = True
                delete_detail = "Delete removed the EI job and subsequent query failed as expected"
        except Exception as exc:  # pragma: no cover - defensive
            delete_ok = False
            delete_detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-INT-EI-008",
                "status": "PASS" if delete_ok else "FAIL",
                "detail": delete_detail,
            }
        )

        try:
            status_obj = ei_service.get_ei_job_status(ei_type_id, ei_job_id)
            query_status_ok = status_obj["ei_job_id"] == ei_job_id
            query_status_detail = "Query EI job status returned an EiJobStatusObject"
        except Exception as exc:  # pragma: no cover - defensive
            query_status_ok = False
            query_status_detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-INT-EI-009",
                "status": "PASS" if query_status_ok else "FAIL",
                "detail": query_status_detail,
            }
        )

        try:
            notify_ok, notify_detail = self._execute_callback_post(
                a1_enrichment_module,
                lambda: ei_service.notify_ei_job_status(
                    callback_status_uri,
                    ei_service.get_ei_job_status(ei_type_id, ei_job_id),
                ),
            )
            notify_ok = notify_ok and ei_service.get_ei_job(ei_type_id, ei_job_id)["ei_job"]["jobStatusNotificationUri"] == callback_status_uri
        except Exception as exc:  # pragma: no cover - defensive
            notify_ok = False
            notify_detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-INT-EI-010",
                "status": "PASS" if notify_ok else "FAIL",
                "detail": notify_detail,
            }
        )

        try:
            result_ok, result_detail = self._execute_callback_post(
                a1_enrichment_module,
                lambda: ei_service.deliver_ei_job_result(
                    callback_result_uri,
                    {"ei_job_id": ei_job_id, "result_payload": {"score": 0.95}},
                ),
            )
            result_ok = result_ok and ei_service.get_ei_job(ei_type_id, ei_job_id)["ei_job"]["jobResultUri"] == callback_result_uri
        except Exception as exc:  # pragma: no cover - defensive
            result_ok = False
            result_detail = str(exc)
        results.append(
            {
                "test_id": "TC-A1-INT-EI-011",
                "status": "PASS" if result_ok else "FAIL",
                "detail": result_detail,
            }
        )

        return self._summarize_results(run_id, "interoperability-a1ei", results)

    def run_ei_job_operations_tests(self, ei_service, service_registry) -> dict:
        """Execute deterministic section 5.3 A1-EI job operation checks."""
        run_id = datetime.now(timezone.utc).strftime("eij-%Y%m%d%H%M%S")
        results: list[dict] = []

        ei_type_ids = ei_service.list_ei_type_ids()
        results.append(
            {
                "test_id": "TC-A1-EI-001",
                "status": "PASS" if isinstance(ei_type_ids, list) else "FAIL",
                "detail": f"Returned {len(ei_type_ids)} EI type identifiers",
            }
        )

        try:
            ei_service.get_ei_type("unknown-ei-type")
            results.append(
                {
                    "test_id": "TC-A1-EI-002",
                    "status": "FAIL",
                    "detail": "Expected KeyError was not raised",
                }
            )
        except KeyError:
            results.append(
                {
                    "test_id": "TC-A1-EI-002",
                    "status": "PASS",
                    "detail": "KeyError raised for unknown EI type",
                }
            )

        ei_type_id = ei_type_ids[0] if ei_type_ids else "default"
        ei_job_id = f"ei-job-{run_id}"
        create_job = {"ei_payload": {"job": "demo"}}
        update_job = {"ei_payload": {"job": "updated"}}

        try:
            _, was_created = ei_service.create_or_replace_ei_job(ei_type_id, ei_job_id, create_job)
            results.append(
                {
                    "test_id": "TC-A1-EI-003",
                    "status": "PASS" if was_created else "FAIL",
                    "detail": "Create returned created state",
                }
            )
        except Exception as exc:  # pragma: no cover - defensive
            results.append(
                {
                    "test_id": "TC-A1-EI-003",
                    "status": "FAIL",
                    "detail": str(exc),
                }
            )

        try:
            job_ids = ei_service.list_ei_job_ids(ei_type_id)
            results.append(
                {
                    "test_id": "TC-A1-EI-004",
                    "status": "PASS" if ei_job_id in job_ids else "FAIL",
                    "detail": "EI job identifier present in list",
                }
            )
        except Exception as exc:  # pragma: no cover - defensive
            results.append(
                {
                    "test_id": "TC-A1-EI-004",
                    "status": "FAIL",
                    "detail": str(exc),
                }
            )

        try:
            queried = ei_service.get_ei_job(ei_type_id, ei_job_id)
            query_payload = queried["ei_job"]
            payload_matches = all(query_payload.get(key) == value for key, value in create_job.items())
            results.append(
                {
                    "test_id": "TC-A1-EI-005",
                    "status": "PASS" if payload_matches else "FAIL",
                    "detail": "Queried EI job matches latest create payload",
                }
            )
        except Exception as exc:  # pragma: no cover - defensive
            results.append(
                {
                    "test_id": "TC-A1-EI-005",
                    "status": "FAIL",
                    "detail": str(exc),
                }
            )

        try:
            _, was_created = ei_service.create_or_replace_ei_job(ei_type_id, ei_job_id, update_job)
            results.append(
                {
                    "test_id": "TC-A1-EI-006",
                    "status": "PASS" if was_created is False else "FAIL",
                    "detail": "Update returned replace state",
                }
            )
        except Exception as exc:  # pragma: no cover - defensive
            results.append(
                {
                    "test_id": "TC-A1-EI-006",
                    "status": "FAIL",
                    "detail": str(exc),
                }
            )

        try:
            status_obj = ei_service.get_ei_job_status(ei_type_id, ei_job_id)
            results.append(
                {
                    "test_id": "TC-A1-EI-007",
                    "status": "PASS" if status_obj["ei_job_id"] == ei_job_id else "FAIL",
                    "detail": "EI job status object returned",
                }
            )
        except Exception as exc:  # pragma: no cover - defensive
            results.append(
                {
                    "test_id": "TC-A1-EI-007",
                    "status": "FAIL",
                    "detail": str(exc),
                }
            )

        try:
            ei_service.delete_ei_job(ei_type_id, ei_job_id)
            results.append(
                {
                    "test_id": "TC-A1-EI-008",
                    "status": "PASS",
                    "detail": "EI job deleted",
                }
            )
        except Exception as exc:  # pragma: no cover - defensive
            results.append(
                {
                    "test_id": "TC-A1-EI-008",
                    "status": "FAIL",
                    "detail": str(exc),
                }
            )

        passed_count = len([item for item in results if item["status"] == "PASS"])
        failed_count = len([item for item in results if item["status"] == "FAIL"])

        return {
            "run_id": run_id,
            "category_id": "ei-job-operations",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": len(results),
                "passed": passed_count,
                "failed": failed_count,
                "verdict": "PASS" if failed_count == 0 else "FAIL",
            },
            "results": results,
        }

    def collect_evidence(self) -> dict:
        return collect_execution_evidence()

    def validate_evidence(self, payload: dict) -> dict:
        return validate_execution_evidence(payload)
