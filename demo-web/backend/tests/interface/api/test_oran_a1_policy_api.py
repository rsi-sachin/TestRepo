from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api import oran


@pytest.fixture
def client() -> TestClient:
    # Keep interface tests isolated by clearing shared in-memory stores.
    oran.a1_policy_service._policies.clear()
    oran.a1_policy_service._policy_status.clear()
    oran.a1_policy_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)


def test_list_a1_services_contract(client: TestClient) -> None:
    response = client.get("/api/oran/services")

    assert response.status_code == 200
    payload = response.json()
    assert "services" in payload
    assert any(service["service_type"] == "A1-P" for service in payload["services"])


def test_policy_lifecycle_endpoints(client: TestClient) -> None:
    create_response = client.put(
        "/api/oran/a1/policytypes/default/policies/policy-42",
        json={
            "policy": {
                "scope": {"scope_type": "cell", "scope_value": "001"},
                "policy_statements": [{"id": "stmt-1", "action": "allow"}],
            },
            "notification_destination": "https://example.com/callback",
        },
    )
    assert create_response.status_code == 201

    get_response = client.get("/api/oran/a1/policytypes/default/policies/policy-42")
    assert get_response.status_code == 200
    assert get_response.json()["policy_statements"][0]["action"] == "allow"

    status_response = client.get("/api/oran/a1/policytypes/default/policies/policy-42/status")
    assert status_response.status_code == 200
    assert status_response.json()["enforcement_status"] == "ACCEPTED"

    delete_response = client.delete("/api/oran/a1/policytypes/default/policies/policy-42")
    assert delete_response.status_code == 204


def test_policy_not_found_returns_problem_details_shape(client: TestClient) -> None:
    response = client.get("/api/oran/a1/policytypes/default/policies/missing")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["title"] == "Policy Not Found"
    assert detail["status"] == 404
    assert detail["instance"] == "/a1/policytypes/default/policies/missing"


def test_invalid_notification_destination_is_rejected(client: TestClient) -> None:
    response = client.put(
        "/api/oran/a1/policytypes/default/policies/policy-99",
        json={
            "policy": {
                "scope": {"scope_type": "cell", "scope_value": "001"},
                "policy_statements": [{"id": "stmt-1", "action": "allow"}],
            },
            "notification_destination": "not-a-valid-url",
        },
    )

    assert response.status_code == 422


# --- Section 5.2.3 contract tests ---

def test_list_policy_types_returns_200_with_empty_array_when_no_types_registered(
    client: TestClient,
) -> None:
    """GET /policytypes MUST return 200 with empty array, never 404, per TS 103 987 §5.2.3.2."""
    oran.a1_policy_service._policy_types.clear()

    response = client.get("/api/oran/a1/policytypes")

    assert response.status_code == 200
    assert response.json() == []


def test_get_unknown_policy_type_returns_404(
    client: TestClient,
) -> None:
    """GET /policytypes/{unknown} MUST return 404 per TS 103 987 §5.2.3.3."""
    response = client.get("/api/oran/a1/policytypes/nonexistent-type")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["status"] == 404
    assert detail["title"] == "Policy Type Not Found"
    assert "nonexistent-type" in detail["instance"]
