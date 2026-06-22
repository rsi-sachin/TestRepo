"""Tests for A1 policy-type scoped resources from TS 103 987 Section 5.2.2."""

import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_a1_policytypes_endpoint_returns_supported_types_and_schemas():
    response = client.get("/api/oran/simulator/interfaces/a1/policytypes")

    assert response.status_code == 200
    body = response.json()
    assert body["resource"] == "/policytypes"
    assert body["count"] >= 1

    ids = {item["policy_type_id"] for item in body["items"]}
    assert "traffic_policy" in ids


def test_put_get_status_and_notify_policy_for_policytype_resource():
    policy_type_id = "traffic_policy"
    policy_id = f"POLICY_{uuid.uuid4().hex[:8]}"

    put_payload = {
        "source_module": "NON_RT_RIC",
        "target_module": "NEAR_RT_RIC",
        "notification_destination": "https://consumer.example.local/callbacks/policy-status",
        "policy_object": {
            "scope": {"cell_id": "CELL-001"},
            "statements": [{"target": "throughput", "operator": ">=", "value": 150}],
        },
    }

    put_response = client.put(
        f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies/{policy_id}",
        json=put_payload,
    )
    assert put_response.status_code == 200

    put_body = put_response.json()
    assert put_body["operation"] == "created"
    assert put_body["record"]["callback_subscription"]["subscribed"] is True

    get_response = client.get(
        f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies/{policy_id}"
    )
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["item"]["policy_object"]["scope"]["cell_id"] == "CELL-001"

    status_response = client.get(
        f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies/{policy_id}/status"
    )
    assert status_response.status_code == 200
    status_body = status_response.json()
    assert status_body["item"]["enforcement_status"] == "ACCEPTED"

    notify_response = client.post(
        f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies/{policy_id}/status/notify",
        json={"feedback_message": "Policy applied to NEAR_RT_RIC control loop"},
    )
    assert notify_response.status_code == 204

    status_after_notify = client.get(
        f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies/{policy_id}/status"
    )
    assert status_after_notify.status_code == 200
    feedback = status_after_notify.json()["item"]["feedback"]
    assert any("Policy applied" in item["message"] for item in feedback)


def test_policyobject_rejects_internal_function_details():
    policy_type_id = "traffic_policy"
    policy_id = f"POLICY_{uuid.uuid4().hex[:8]}"
    payload = {
        "source_module": "NON_RT_RIC",
        "target_module": "NEAR_RT_RIC",
        "policy_object": {
            "scope": {"region": "R1"},
            "statements": [],
            "internal_function": "scheduler_v3",
        },
    }

    response = client.put(
        f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies/{policy_id}",
        json=payload,
    )

    assert response.status_code == 400
    assert "must not include internal function" in response.json()["detail"]


def test_delete_policy_removes_policy_id_from_policytype_collection():
    policy_type_id = "qos_policy"
    policy_id = f"POLICY_{uuid.uuid4().hex[:8]}"

    create_response = client.put(
        f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies/{policy_id}",
        json={
            "source_module": "NON_RT_RIC",
            "target_module": "NEAR_RT_RIC",
            "policy_object": {
                "scope": {"ue_group": "gold"},
                "statements": [{"target": "latency_ms", "operator": "<=", "value": 20}],
            },
        },
    )
    assert create_response.status_code == 200

    list_before_delete = client.get(f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies")
    assert list_before_delete.status_code == 200
    assert policy_id in list_before_delete.json()["items"]

    delete_response = client.delete(
        f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies/{policy_id}"
    )
    assert delete_response.status_code == 200

    list_after_delete = client.get(f"/api/oran/simulator/interfaces/a1/policytypes/{policy_type_id}/policies")
    assert list_after_delete.status_code == 200
    assert policy_id not in list_after_delete.json()["items"]
