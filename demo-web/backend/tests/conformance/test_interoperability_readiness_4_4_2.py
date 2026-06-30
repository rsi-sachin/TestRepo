from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry
from app.services.conformance_service import ConformanceService


def _readiness(**kwargs) -> dict:
    service = ConformanceService()
    registry = A1ServiceRegistry()
    policy_service = A1PolicyService(registry)
    return service.build_interoperability_readiness(
        service_registry=registry,
        policy_service=policy_service,
        **kwargs,
    )


def test_4_4_2_readiness_includes_dual_dut_role_configuration() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "DUAL_DUT_ROLE_CONFIGURATION" in ids


def test_4_4_2_readiness_requires_matching_policy_type_or_ei_type() -> None:
    ids = {item["id"] for item in _readiness()["checks"]}
    assert "MATCHING_POLICY_TYPE_PRECONDITION" in ids
    assert "MATCHING_EI_TYPE_PRECONDITION" in ids


def test_4_4_2_readiness_includes_passive_a1_capture_capability() -> None:
    check_map = {item["id"]: item for item in _readiness()["checks"]}
    assert check_map["PASSIVE_A1_CAPTURE_CAPABILITY"]["passed"] is True


def test_4_4_2_readiness_marks_o1_as_conditional() -> None:
    check_map = {item["id"]: item for item in _readiness(require_o1=True)["checks"]}
    assert check_map["OPTIONAL_O1_CAPABILITY"]["blocking"] is True


def test_4_4_2_readiness_marks_e2_ue_trigger_as_conditional() -> None:
    check_map = {item["id"]: item for item in _readiness(require_e2_ue=True)["checks"]}
    assert check_map["OPTIONAL_E2_UE_TRIGGER_CAPABILITY"]["blocking"] is True


def test_4_4_2_readiness_marks_core_network_as_conditional() -> None:
    check_map = {item["id"]: item for item in _readiness(require_core=True)["checks"]}
    assert check_map["OPTIONAL_CORE_NETWORK_CAPABILITY"]["blocking"] is True
