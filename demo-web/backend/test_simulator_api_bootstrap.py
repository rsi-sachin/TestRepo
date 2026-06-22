"""
Contract-first tests for ORAN simulator bootstrap endpoints.

These tests verify route registration and deterministic scaffold contracts
before scenario-specific simulator behavior is implemented.
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_simulator_health_route_returns_placeholder_contract():
    response = client.get("/api/oran/simulator/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["placeholder"] is True
    assert payload["primary_target"] == "NEAR_RT_RIC"
    assert "INIT" in payload["valid_states"]


def test_simulator_modules_route_lists_list1_identifiers():
    response = client.get("/api/oran/simulator/modules")

    assert response.status_code == 200
    payload = response.json()
    assert payload["placeholder"] is True
    assert payload["source"] == "List-1 Module Names"

    module_ids = {item["module_id"] for item in payload["items"]}
    assert "NEAR_RT_RIC" in module_ids
    assert "ORAN_INT_INFO_SOURCE" in module_ids
    assert "SMO" in module_ids


def test_simulator_module_state_returns_init_for_known_module():
    response = client.get("/api/oran/simulator/modules/NEAR_RT_RIC/state")

    assert response.status_code == 200
    payload = response.json()
    assert payload["module_id"] == "NEAR_RT_RIC"
    assert payload["state"] == "INIT"
    assert payload["placeholder"] is True


def test_simulator_module_state_returns_404_for_unknown_module():
    response = client.get("/api/oran/simulator/modules/UNKNOWN_MODULE/state")

    assert response.status_code == 404


def test_orchestrator_command_accepts_known_modules_and_returns_queue_status():
    request_payload = {
        "action": "start",
        "execution_mode": "sequential",
        "target_modules": ["NON_RT_RIC", "NEAR_RT_RIC"],
        "scenario_id": "PLACEHOLDER_SCENARIO_001",
        "parameters": {"dry_run": "true"},
    }

    response = client.post("/api/oran/simulator/orchestrator/command", json=request_payload)

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["placeholder"] is True
    assert payload["status"] == "queued"


def test_orchestrator_command_rejects_unknown_module():
    request_payload = {
        "action": "start",
        "execution_mode": "sequential",
        "target_modules": ["UNKNOWN_MODULE"],
        "parameters": {},
    }

    response = client.post("/api/oran/simulator/orchestrator/command", json=request_payload)

    assert response.status_code == 400


def test_a1_policy_endpoint_accepts_placeholder_contract():
    request_payload = {
        "policy_id": "POLICY_001",
        "policy_type": "traffic_policy",
        "source_module": "NON_RT_RIC",
        "target_module": "NEAR_RT_RIC",
    }

    response = client.post("/api/oran/simulator/interfaces/a1/policies", json=request_payload)

    assert response.status_code == 200
    payload = response.json()
    assert payload["interface"] == "A1"
    assert payload["status"] == "recorded"


def test_o1_alarm_endpoint_accepts_placeholder_contract():
    request_payload = {
        "alarm_id": "ALARM_001",
        "severity": "MAJOR",
        "source_module": "ORAN_INT_INFO_SOURCE",
        "target_module": "SMO",
    }

    response = client.post("/api/oran/simulator/interfaces/o1/alarms", json=request_payload)

    assert response.status_code == 200
    payload = response.json()
    assert payload["interface"] == "O1"
    assert payload["status"] == "recorded"


def test_e2_event_endpoint_accepts_known_source_module():
    request_payload = {
        "event_id": "E2_EVT_001",
        "source_module": "O_DU",
        "target_module": "NEAR_RT_RIC",
        "message_type": "control_update",
    }

    response = client.post("/api/oran/simulator/interfaces/e2/events", json=request_payload)

    assert response.status_code == 200
    payload = response.json()
    assert payload["interface"] == "E2"
    assert payload["status"] == "recorded"


def test_e2_event_endpoint_rejects_unknown_source_module():
    request_payload = {
        "event_id": "E2_EVT_002",
        "source_module": "UNKNOWN_MODULE",
        "target_module": "NEAR_RT_RIC",
        "message_type": "control_update",
    }

    response = client.post("/api/oran/simulator/interfaces/e2/events", json=request_payload)

    assert response.status_code == 400
