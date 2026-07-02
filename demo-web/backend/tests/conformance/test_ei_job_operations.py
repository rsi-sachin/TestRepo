import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.modules.conformance_harness.service import ConformanceHarnessService
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_service_registry import A1ServiceRegistry


def _service() -> ConformanceHarnessService:
    return ConformanceHarnessService()


def test_ei_job_operations_suite_metadata_is_exposed() -> None:
    tests = _service().list_ei_job_operations_tests()

    assert len(tests) == 8
    assert {item["category_id"] for item in tests} == {"ei-job-operations"}
    assert all("TS 103 989" in item["spec_reference"] for item in tests)


def test_ei_job_operations_run_passes_with_default_registry() -> None:
    payload = _service().run_ei_job_operations_tests(
        ei_service=A1EnrichmentInformationService(A1ServiceRegistry()),
        service_registry=A1ServiceRegistry(),
    )

    assert payload["category_id"] == "ei-job-operations"
    assert payload["summary"]["total"] == 8
    assert payload["summary"]["failed"] == 0


def test_ei_job_operations_run_includes_all_expected_test_ids() -> None:
    payload = _service().run_ei_job_operations_tests(
        ei_service=A1EnrichmentInformationService(A1ServiceRegistry()),
        service_registry=A1ServiceRegistry(),
    )

    ids = {item["test_id"] for item in payload["results"]}
    assert ids == {
        "TC-A1-EI-001",
        "TC-A1-EI-002",
        "TC-A1-EI-003",
        "TC-A1-EI-004",
        "TC-A1-EI-005",
        "TC-A1-EI-006",
        "TC-A1-EI-007",
        "TC-A1-EI-008",
    }


def test_ei_job_operations_unknown_type_check_passes() -> None:
    payload = _service().run_ei_job_operations_tests(
        ei_service=A1EnrichmentInformationService(A1ServiceRegistry()),
        service_registry=A1ServiceRegistry(),
    )

    tc_002 = next(item for item in payload["results"] if item["test_id"] == "TC-A1-EI-002")
    assert tc_002["status"] == "PASS"
    assert "KeyError raised" in tc_002["detail"]


def test_ei_job_operations_deleted_job_is_no_longer_queryable() -> None:
    service = A1EnrichmentInformationService(A1ServiceRegistry())
    service.create_or_replace_ei_job("default", "delete-me", {"ei_payload": {"name": "x"}})
    service.delete_ei_job("default", "delete-me")

    try:
        service.get_ei_job("default", "delete-me")
        assert False, "Expected KeyError when querying deleted EI job"
    except KeyError:
        assert True