"""
Conformance tests: TS 103 983 section 4.1.2 topology and interaction contracts.

Source: TS 103 983 V4.0.0 Figure 4.1.2-1

These tests verify that repository topology artifacts, O1/E2 contracts,
and info-source simulators align with the section 4.1.2 architecture model.
"""

from pathlib import Path
import json

from app.modules.e2_interface.models import E2Request
from app.modules.e2_interface.service import E2InterfaceService
from app.modules.e2_interface.validators import validate_e2_message
from app.modules.o1_interface.models import O1Request
from app.modules.o1_interface.service import O1InterfaceService
from app.modules.o1_interface.validators import validate_o1_request
from app.modules.simulators.info_sources.external_source import ExternalInfoSourceSimulator
from app.modules.simulators.info_sources.internal_source import InternalInfoSourceSimulator


def _topology_artifact_path() -> Path:
    # tests/conformance -> tests -> backend -> demo-web -> TestRepo
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / "ORAN" / "docs" / "figure_4_1_2_1_oran_entities.json"


def _load_topology_artifact() -> dict:
    with _topology_artifact_path().open("r", encoding="utf-8") as f:
        return json.load(f)


def test_figure_4_1_2_1_topology_artifact_contains_required_entities() -> None:
    """Figure 4.1.2-1 artifact contains core O-RAN entities used by A1 context."""
    artifact = _load_topology_artifact()
    entity_ids = {entity["id"] for entity in artifact["entities"]}

    assert "smo" in entity_ids
    assert "non_rt_ric" in entity_ids
    assert "near_rt_ric" in entity_ids


def test_figure_4_1_2_1_topology_artifact_contains_required_interfaces() -> None:
    """Figure 4.1.2-1 artifact includes A1, O1, and E2 interface domains."""
    artifact = _load_topology_artifact()
    interface_ids = {interface["id"] for interface in artifact["interfaces"]}

    assert "a1" in interface_ids
    assert "o1" in interface_ids
    assert "e2" in interface_ids


def test_o1_interface_contract_accepts_get_without_payload() -> None:
    """O1 contract allows GET operations without payload."""
    request = O1Request(
        transaction_id="o1-get-1",
        operation="get",
        resource="/managed-element/1",
        payload={},
    )

    is_valid, reason = validate_o1_request(request)
    assert is_valid is True
    assert reason == "ok"


def test_o1_interface_contract_rejects_set_without_payload() -> None:
    """O1 contract enforces payload for set operations."""
    request = O1Request(
        transaction_id="o1-set-1",
        operation="set",
        resource="/managed-element/1/config",
        payload={},
    )

    is_valid, reason = validate_o1_request(request)
    assert is_valid is False
    assert "Payload is required" in reason


def test_e2_interface_contract_accepts_subscription_with_event_trigger() -> None:
    """E2 contract accepts subscription message with required event trigger."""
    request = E2Request(
        transaction_id="e2-sub-1",
        message_type="subscription",
        node_id="node-001",
        payload={"event_trigger": "periodic-10s"},
    )

    is_valid, reason = validate_e2_message(request)
    assert is_valid is True
    assert reason == "ok"


def test_e2_interface_contract_rejects_indication_without_ran_function_id() -> None:
    """E2 contract enforces ran_function_id for indication/control messages."""
    request = E2Request(
        transaction_id="e2-ind-1",
        message_type="indication",
        node_id="node-001",
        payload={"signal": "kpi"},
    )

    is_valid, reason = validate_e2_message(request)
    assert is_valid is False
    assert "ran_function_id" in reason


def test_topology_modules_expose_stub_health_for_o1_e2_and_info_sources() -> None:
    """Topology module stubs are callable and report deterministic health/status."""
    o1 = O1InterfaceService()
    e2 = E2InterfaceService()
    internal_source = InternalInfoSourceSimulator()
    external_source = ExternalInfoSourceSimulator()

    assert o1.health() == {"module": "o1_interface", "status": "stub"}
    assert e2.health() == {"module": "e2_interface", "status": "stub"}
    assert internal_source.status() == {"module": "internal_info_source", "status": "stub"}
    assert external_source.status() == {"module": "external_info_source", "status": "stub"}


def test_topology_artifact_mvp_profile_aligns_with_stubbed_modules() -> None:
    """MVP profile in Figure 4.1.2-1 artifact matches current module implementation strategy."""
    artifact = _load_topology_artifact()
    profile = artifact["mvp_execution_profile"]

    assert "non_rt_ric" in profile["components_to_implement"]
    assert "near_rt_ric" in profile["components_to_stub"]
    assert "o_cu_cp" in profile["components_to_stub"]
    assert "a1" in profile["primary_test_focus"]
