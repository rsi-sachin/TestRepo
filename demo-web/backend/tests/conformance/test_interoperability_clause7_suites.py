from app.modules.conformance_harness.service import ConformanceHarnessService
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry


def _service() -> ConformanceHarnessService:
    return ConformanceHarnessService()


def test_clause_7_2_interoperability_a1p_suite_metadata_is_exposed() -> None:
    tests = _service().list_interoperability_a1p_tests()

    assert len(tests) == 4
    assert {item["category_id"] for item in tests} == {"interoperability-a1p"}
    assert all("TS 103 989" in item["spec_reference"] for item in tests)


def test_clause_7_2_interoperability_a1p_run_passes_with_default_registry() -> None:
    payload = _service().run_interoperability_a1p_tests(
        policy_service=A1PolicyService(),
        service_registry=A1ServiceRegistry(),
    )

    assert payload["category_id"] == "interoperability-a1p"
    assert payload["summary"]["total"] == 4
    assert payload["summary"]["failed"] == 0


def test_clause_7_3_interoperability_a1ei_suite_metadata_is_exposed() -> None:
    tests = _service().list_interoperability_a1ei_tests()

    assert len(tests) == 4
    assert {item["category_id"] for item in tests} == {"interoperability-a1ei"}
    assert all("TS 103 989" in item["spec_reference"] for item in tests)


def test_clause_7_3_interoperability_a1ei_run_passes_with_default_registry() -> None:
    payload = _service().run_interoperability_a1ei_tests(
        service_registry=A1ServiceRegistry(),
    )

    assert payload["category_id"] == "interoperability-a1ei"
    assert payload["summary"]["total"] == 4
    assert payload["summary"]["failed"] == 0
