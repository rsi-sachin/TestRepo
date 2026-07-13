from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran


def test_section5_e2e_policy_and_ei_reconciliation_flow() -> None:
    oran.a1_policy_service._policies.clear()
    oran.a1_policy_service._policy_status.clear()
    oran.a1_policy_service._notification_destinations.clear()
    oran.a1_ei_service._ei_jobs.clear()
    oran.a1_ei_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    policy_create = client.put(
        "/api/oran/a1/policytypes/default/policies/e2e-s5-policy",
        json={
            "scope": {"scope_type": "slice", "scope_value": "gold"},
            "policy_statements": [{"id": "stmt-e2e", "action": "allow"}],
        },
    )
    assert policy_create.status_code == 201

    ei_create = client.put(
        "/api/oran/a1/eitypes/default/eijobs/e2e-s5-ei",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"flow": "baseline"},
            "jobStatusNotificationUri": "https://example.com/ei-status",
            "jobResultUri": "https://example.com/ei-result",
        },
    )
    assert ei_create.status_code == 201

    ei_update_invalid = client.put(
        "/api/oran/a1/eitypes/default/eijobs/e2e-s5-ei",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"flow": "updated"},
        },
    )
    assert ei_update_invalid.status_code == 400

    ei_get = client.get("/api/oran/a1/eitypes/default/eijobs/e2e-s5-ei")
    assert ei_get.status_code == 200
    assert ei_get.json()["ei_job"]["jobResultUri"] == "https://example.com/ei-result"

    policy_delete = client.delete("/api/oran/a1/policytypes/default/policies/e2e-s5-policy")
    ei_delete = client.delete("/api/oran/a1/eitypes/default/eijobs/e2e-s5-ei")

    assert policy_delete.status_code == 204
    assert ei_delete.status_code == 204
