from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran


def test_a1_policy_workflow_e2e() -> None:
    oran.a1_policy_service._policies.clear()
    oran.a1_policy_service._policy_status.clear()
    oran.a1_policy_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    services_response = client.get("/api/oran/services")
    assert services_response.status_code == 200

    create_response = client.put(
        "/api/oran/a1/policytypes/default/policies/e2e-policy",
        json={
            "policy": {
                "scope": {"scope_type": "cell", "scope_value": "999"},
                "policy_statements": [{"id": "stmt-e2e", "action": "allow"}],
            },
            "notification_destination": "https://example.com/e2e-callback",
        },
    )
    assert create_response.status_code == 201

    status_response = client.get("/api/oran/a1/policytypes/default/policies/e2e-policy/status")
    assert status_response.status_code == 200

    delete_response = client.delete("/api/oran/a1/policytypes/default/policies/e2e-policy")
    assert delete_response.status_code == 204

    missing_after_delete = client.get("/api/oran/a1/policytypes/default/policies/e2e-policy")
    assert missing_after_delete.status_code == 404
