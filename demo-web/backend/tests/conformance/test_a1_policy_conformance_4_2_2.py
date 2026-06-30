from app.modules.conformance_harness.evidence_collector import collect_execution_evidence
from app.modules.conformance_harness.evidence_validator import validate_execution_evidence
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry
from app.services.conformance_service import ConformanceService


class _Response:
    def __init__(self, status_code: int = 200, content_type: str = "application/json") -> None:
        self.status_code = status_code
        self.headers = {"content-type": content_type}


def _payload(verdict: str = "PASS") -> dict:
    return {
        "test_case_id": "TC-A1-PTQ-001",
        "test_section_reference": "TS 103 989 section 4.2.1",
        "verdict": verdict,
        "verdict_reason": "verification complete",
        "checks_performed": [{"check_id": "1", "result": "PASS"}],
        "evidence_artifacts": [{"artifact_type": "http_message_log", "file_path": "logs/run.jsonl"}],
    }


def _readiness() -> dict:
    service = ConformanceService()
    registry = A1ServiceRegistry()
    policy_service = A1PolicyService()
    return service.build_dut_readiness(
        service_registry=registry,
        policy_service=policy_service,
        ric_endpoint="http://127.0.0.1:8000",
        http_get=lambda *_args, **_kwargs: _Response(),
    )


def test_section_4_2_2_readiness_includes_role_configuration_a1p() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "ROLE_CONFIGURATION_A1P" in ids


def test_section_4_2_2_readiness_includes_role_configuration_a1ei() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "ROLE_CONFIGURATION_A1EI" in ids


def test_section_4_2_2_readiness_includes_policy_type_precondition() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "POLICY_TYPE_PRECONDITION" in ids


def test_section_4_2_2_readiness_includes_response_schema_compliance() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "RESPONSE_SCHEMA_COMPLIANCE" in ids


def test_section_4_2_2_readiness_includes_endpoint_accessibility() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "ENDPOINT_ACCESSIBILITY" in ids


def test_section_4_2_2_readiness_includes_http_compliance_content_type() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "HTTP_COMPLIANCE_CONTENT_TYPE" in ids


def test_section_4_2_2_readiness_includes_firewall_network_policy() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "FIREWALL_NETWORK_POLICY" in ids


def test_section_4_2_2_readiness_includes_performance_baseline() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "PERFORMANCE_BASELINE" in ids


def test_section_4_2_2_evidence_validator_accepts_pass_verdict() -> None:
    result = validate_execution_evidence(_payload("PASS"))
    assert result["valid"] is True


def test_section_4_2_2_evidence_validator_accepts_fail_verdict() -> None:
    result = validate_execution_evidence(_payload("FAIL"))
    assert result["valid"] is True


def test_section_4_2_2_evidence_validator_accepts_inconclusive_verdict() -> None:
    result = validate_execution_evidence(_payload("INCONCLUSIVE"))
    assert result["valid"] is True


def test_section_4_2_2_evidence_validator_rejects_invalid_verdict() -> None:
    result = validate_execution_evidence(_payload("UNKNOWN"))
    assert result["valid"] is False


def test_section_4_2_2_collect_execution_evidence_normalizes_exchanges() -> None:
    result = collect_execution_evidence(
        run_id="run-42",
        test_case_id="TC-A1-PTQ-001",
        verdict="PASS",
        verdict_reason="all checks passed",
        checks_performed=[{"check_id": "1", "result": "PASS"}],
        evidence_artifacts=[{"artifact_type": "http_message_log", "file_path": "logs/test.jsonl"}],
        exchanges=[
            {
                "exchange_id": "ex-1",
                "test_case_id": "TC-A1-PTQ-001",
                "request": {"method": "GET", "uri": "/v1/policytypes", "headers": {}, "body": None},
                "response": {
                    "status_code": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": "[]",
                    "response_time_ms": 10.5,
                },
                "schema_valid": True,
                "status_code_expected": True,
                "headers_complete": True,
            }
        ],
    )

    assert result["exchange_count"] == 1
    assert result["artifact_count"] == 1
    assert result["exchanges"][0]["response"]["status_code"] == 200
