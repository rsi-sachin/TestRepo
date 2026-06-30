from app.modules.conformance_harness.service import ConformanceHarnessService
from app.modules.conformance_harness.simulator_verifier import verify_simulator_capability


def test_simulator_capability_verification_returns_eight_matrix_checks() -> None:
    payload = verify_simulator_capability()

    assert payload["status"] == "ready"
    assert len(payload["capabilities"]) == 8


def test_simulator_capability_verification_includes_required_http_method_support() -> None:
    payload = verify_simulator_capability()
    methods_capability = next(item for item in payload["capabilities"] if item["id"] == "HTTP_OPERATION_CONFIGURABILITY")

    assert methods_capability["passed"] is True
    assert methods_capability["supported_methods"] == ["GET", "PUT", "POST", "DELETE"]


def test_simulator_capability_verification_can_report_not_ready() -> None:
    payload = verify_simulator_capability(
        {
            "LATENCY_TIMEOUT_SIMULATION": False,
            "FAILURE_MODE_SIMULATION": False,
        }
    )

    assert payload["status"] == "not-ready"
    failing_ids = {item["id"] for item in payload["capabilities"] if not item["passed"]}
    assert "LATENCY_TIMEOUT_SIMULATION" in failing_ids
    assert "FAILURE_MODE_SIMULATION" in failing_ids


def test_harness_service_get_simulator_capability_is_matrix_aligned() -> None:
    payload = ConformanceHarnessService().get_simulator_capability()

    assert payload["status"] in {"ready", "not-ready"}
    assert len(payload["capabilities"]) == 8
    assert payload["spec_reference"] == "TS 103 989 section 4.2.2"
