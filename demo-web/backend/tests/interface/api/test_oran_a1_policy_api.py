from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api import oran
from app.models.a1_policy_models import PolicyTypeObject
from app.services.a1_errors import A1ConflictError


@pytest.fixture
def client() -> TestClient:
    # Keep interface tests isolated by clearing shared in-memory stores.
    oran.a1_policy_service._policy_types.clear()
    oran.a1_policy_service._policy_types["default"] = PolicyTypeObject(
        policy_type_id="default",
        policy_schema={"type": "object", "required": ["policy_statements"]},
        policy_status_schema={"type": "object", "required": ["policy_id", "enforcement_status"]},
        supports_policy_creation=True,
    )
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


def test_service_role_boundary_for_a1p_and_a1ei(client: TestClient) -> None:
    a1p = client.get("/api/oran/services/A1-P")
    a1ei = client.get("/api/oran/services/A1-EI")

    assert a1p.status_code == 200
    assert a1ei.status_code == 200

    a1p_payload = a1p.json()
    a1ei_payload = a1ei.json()

    assert a1p_payload["service"]["consumer_role"]["label"] == "A1-P Consumer"
    assert a1p_payload["service"]["producer_role"]["label"] == "A1-P Producer"
    assert a1ei_payload["service"]["consumer_role"]["label"] == "A1-EI Consumer"
    assert a1ei_payload["service"]["producer_role"]["label"] == "A1-EI Producer"


def test_policy_lifecycle_endpoints(client: TestClient) -> None:
    create_response = client.put(
        "/api/oran/a1/policytypes/default/policies/policy-42",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
        params={"notificationDestination": "https://example.com/callback"},
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
    assert response.headers["content-type"].startswith("application/problem+json")
    detail = response.json()["detail"]
    assert detail["title"] == "Policy Not Found"
    assert detail["status"] == 404
    assert detail["instance"] == "/a1/policytypes/default/policies/missing"


def test_policy_status_after_delete_returns_not_found_problem_details(client: TestClient) -> None:
    client.put(
        "/api/oran/a1/policytypes/default/policies/delete-status-check",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "stmt-del", "action": "allow"}],
        },
        params={"notificationDestination": "https://example.com/callback"},
    )

    delete_response = client.delete("/api/oran/a1/policytypes/default/policies/delete-status-check")
    status_response = client.get("/api/oran/a1/policytypes/default/policies/delete-status-check/status")

    assert delete_response.status_code == 204
    assert status_response.status_code == 404
    detail = status_response.json()["detail"]
    assert detail["title"] == "Policy Status Not Found"


def test_delete_unknown_policy_returns_not_found_problem_details(client: TestClient) -> None:
    response = client.delete("/api/oran/a1/policytypes/default/policies/not-there")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    detail = response.json()["detail"]
    assert detail["title"] == "Policy Not Found"
    assert detail["status"] == 404


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


def test_section6_policy_openapi_definitions_include_problem_details_responses(
    client: TestClient,
) -> None:
    """Section 6 requires documented 4xx/5xx and method constraints for A1-P resources."""
    schema = client.get("/openapi.json").json()
    operations = schema["paths"]

    put_policy = operations["/api/oran/a1/policytypes/{policy_type_id}/policies/{policy_id}"]["put"]
    assert "400" in put_policy["responses"]
    assert "404" in put_policy["responses"]
    assert "405" in put_policy["responses"]
    assert "409" in put_policy["responses"]

    get_policy_type = operations["/api/oran/a1/policytypes/{policy_type_id}"]["get"]
    assert "405" in get_policy_type["responses"]

    policy_not_found_response = put_policy["responses"]["404"]
    assert (
        "application/problem+json"
        in policy_not_found_response["content"]
    )


def test_policy_conflict_is_mapped_to_problem_details(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_conflict(*args, **kwargs):
        raise A1ConflictError("simulated policy conflict")

    monkeypatch.setattr(oran.a1_policy_service, "create_or_replace_policy", _raise_conflict)

    response = client.put(
        "/api/oran/a1/policytypes/default/policies/policy-conflict",
        json={
            "scope": {"scope_type": "cell", "scope_value": "002"},
            "policy_statements": [{"id": "stmt-c", "action": "allow"}],
        },
    )

    assert response.status_code == 409
    assert response.headers["content-type"].startswith("application/problem+json")
    detail = response.json()["detail"]
    assert detail["title"] == "Policy Conflict"
    assert detail["status"] == 409


def test_policy_resources_reject_unsupported_methods_with_405(client: TestClient) -> None:
    list_delete = client.request("DELETE", "/api/oran/a1/policytypes")
    status_put = client.request(
        "PUT",
        "/api/oran/a1/policytypes/default/policies/policy-m/status",
        json={},
    )

    assert list_delete.status_code == 405
    assert status_put.status_code == 405


def test_policy_content_taxonomy_profile_is_accepted(client: TestClient) -> None:
    response = client.put(
        "/api/oran/a1/policytypes/default/policies/policy-taxonomy-api-1",
        json={
            "scope": {"scope_type": "cell", "scope_value": "010"},
            "policy_statements": [
                {
                    "id": "objective-api-1",
                    "category": "objective",
                    "objective": {"name": "availability", "target": ">=99.9%"},
                },
                {
                    "id": "resource-api-1",
                    "category": "resource",
                    "resource": {"type": "cpu", "limit": "2 cores"},
                },
            ],
        },
    )

    assert response.status_code == 201


def test_policy_content_taxonomy_profile_rejects_invalid_statement(client: TestClient) -> None:
    response = client.put(
        "/api/oran/a1/policytypes/default/policies/policy-taxonomy-api-2",
        json={
            "scope": {"scope_type": "cell", "scope_value": "011"},
            "policy_statements": [
                {
                    "id": "objective-api-2",
                    "category": "objective",
                }
            ],
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["title"] == "Invalid Policy Request"
    assert "non-empty objective object" in detail["detail"]
