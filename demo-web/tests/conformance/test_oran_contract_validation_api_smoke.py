import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))
from app.main import app


client = TestClient(app)


def test_o1_validate_accepts_json_object_payload():
    response = client.post(
        "/api/oran/o1/validate",
        json={
            "transaction_id": "tx-001",
            "operation": "set",
            "resource": "/o1/node-config",
            "payload": {"parameter": "value"},
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_e2_validate_accepts_json_object_payload():
    response = client.post(
        "/api/oran/e2/validate",
        json={
            "transaction_id": "tx-002",
            "message_type": "subscription",
            "node_id": "node-1",
            "payload": {"event_trigger": "periodic"},
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_o1_validate_rejects_missing_payload_for_set_operation():
    response = client.post(
        "/api/oran/o1/validate",
        json={
            "transaction_id": "tx-003",
            "operation": "set",
            "resource": "/o1/node-config",
            "payload": {},
        },
    )
    assert response.status_code == 400


def test_e2_validate_rejects_subscription_without_event_trigger():
    response = client.post(
        "/api/oran/e2/validate",
        json={
            "transaction_id": "tx-004",
            "message_type": "subscription",
            "node_id": "node-1",
            "payload": {},
        },
    )
    assert response.status_code == 400
