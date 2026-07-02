from app.modules.conformance_harness.service import ConformanceHarnessService
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry


def _service() -> ConformanceHarnessService:
    return ConformanceHarnessService()


def test_clause_7_2_interoperability_a1p_suite_metadata_is_exposed() -> None:
    tests = _service().list_interoperability_a1p_tests()

    assert len(tests) == 9
    assert {item["category_id"] for item in tests} == {"interoperability-a1p"}
    assert all("TS 103 989" in item["spec_reference"] for item in tests)
    assert {item["test_id"] for item in tests} == {
        "TC-A1-INT-P-001",
        "TC-A1-INT-P-002",
        "TC-A1-INT-P-003",
        "TC-A1-INT-P-004",
        "TC-A1-INT-P-005",
        "TC-A1-INT-P-006",
        "TC-A1-INT-P-007",
        "TC-A1-INT-P-008",
        "TC-A1-INT-P-009",
    }


def test_clause_7_2_interoperability_a1p_run_passes_with_default_registry() -> None:
    payload = _service().run_interoperability_a1p_tests(
        policy_service=A1PolicyService(),
        service_registry=A1ServiceRegistry(),
    )

    assert payload["category_id"] == "interoperability-a1p"
    assert payload["summary"]["total"] == 9
    assert payload["summary"]["failed"] == 0


def test_clause_7_3_interoperability_a1ei_suite_metadata_is_exposed() -> None:
    tests = _service().list_interoperability_a1ei_tests()

    assert len(tests) == 11
    assert {item["category_id"] for item in tests} == {"interoperability-a1ei"}
    assert all("TS 103 989" in item["spec_reference"] for item in tests)
    assert {item["test_id"] for item in tests} == {
        "TC-A1-INT-EI-001",
        "TC-A1-INT-EI-002",
        "TC-A1-INT-EI-003",
        "TC-A1-INT-EI-004",
        "TC-A1-INT-EI-005",
        "TC-A1-INT-EI-006",
        "TC-A1-INT-EI-007",
        "TC-A1-INT-EI-008",
        "TC-A1-INT-EI-009",
        "TC-A1-INT-EI-010",
        "TC-A1-INT-EI-011",
    }


def test_clause_7_3_interoperability_a1ei_run_passes_with_default_registry() -> None:
    payload = _service().run_interoperability_a1ei_tests(
        service_registry=A1ServiceRegistry(),
    )

    assert payload["category_id"] == "interoperability-a1ei"
    assert payload["summary"]["total"] == 11
    assert payload["summary"]["failed"] == 0
