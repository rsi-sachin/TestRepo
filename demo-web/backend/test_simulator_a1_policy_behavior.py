"""Behavior tests for incremental A1 simulator implementation."""

import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_a1_policy_endpoint_rejects_invalid_role_pair():
    request_payload = {
        "policy_id": f"POLICY_BAD_{uuid.uuid4().hex[:8]}",
        "policy_type": "traffic_policy",
        "source_module": "NEAR_RT_RIC",
        "target_module": "NON_RT_RIC",
    }

    response = client.post("/api/oran/simulator/interfaces/a1/policies", json=request_payload)

    assert response.status_code == 400
    assert "NON_RT_RIC -> NEAR_RT_RIC" in response.json()["detail"]


def test_a1_policy_create_then_get_by_id():
    policy_id = f"POLICY_{uuid.uuid4().hex[:8]}"

    create_payload = {
        "policy_id": policy_id,
        "policy_type": "traffic_policy",
        "source_module": "NON_RT_RIC",
        "target_module": "NEAR_RT_RIC",
    }

    create_response = client.post("/api/oran/simulator/interfaces/a1/policies", json=create_payload)

    assert create_response.status_code == 200
    create_body = create_response.json()
    assert create_body["operation"] == "created"
    assert create_body["record"]["policy_id"] == policy_id

    get_response = client.get(f"/api/oran/simulator/interfaces/a1/policies/{policy_id}")

    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["item"]["policy_id"] == policy_id
    assert get_body["item"]["source_module"] == "NON_RT_RIC"
    assert get_body["item"]["target_module"] == "NEAR_RT_RIC"


def test_a1_policy_list_includes_new_policy():
    policy_id = f"POLICY_{uuid.uuid4().hex[:8]}"

    create_payload = {
        "policy_id": policy_id,
        "policy_type": "qos_policy",
        "source_module": "NON_RT_RIC",
        "target_module": "NEAR_RT_RIC",
    }
    create_response = client.post("/api/oran/simulator/interfaces/a1/policies", json=create_payload)
    assert create_response.status_code == 200

    list_response = client.get("/api/oran/simulator/interfaces/a1/policies")

    assert list_response.status_code == 200
    body = list_response.json()
    assert body["interface"] == "A1"
    assert body["count"] >= 1
    assert any(item["policy_id"] == policy_id for item in body["items"])
