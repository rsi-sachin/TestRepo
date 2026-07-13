"""
Conformance tests: TS 103 983 section 5.1.4 scope identifier handling.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api import oran


@pytest.fixture
def client() -> TestClient:
    oran.a1_policy_service._policies.clear()
    oran.a1_policy_service._policy_status.clear()
    oran.a1_policy_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)


@pytest.mark.parametrize(
    "scope_type,scope_value",
    [
        ("ue", "imsi-001010000000001"),
        ("ue_group", "group-a"),
        ("slice", "sst1-sd010203"),
        ("qos_flow", "5qi-7"),
        ("cell", "001"),
    ],
)
def test_section_5_1_4_scope_identifiers_are_accepted(
    client: TestClient,
    scope_type: str,
    scope_value: str,
) -> None:
    response = client.put(
        f"/api/oran/a1/policytypes/default/policies/policy-{scope_type}",
        json={
            "scope": {"scope_type": scope_type, "scope_value": scope_value},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
    )

    assert response.status_code == 201


def test_section_5_1_4_scope_identifier_aliases_are_normalized(client: TestClient) -> None:
    response = client.put(
        "/api/oran/a1/policytypes/default/policies/policy-alias",
        json={
            "scope": {"scope_type": "qos-flow", "scope_value": "5qi-9"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
    )

    assert response.status_code == 201


def test_section_5_1_4_unknown_scope_identifier_is_rejected(client: TestClient) -> None:
    response = client.put(
        "/api/oran/a1/policytypes/default/policies/policy-bad-scope",
        json={
            "scope": {"scope_type": "sector", "scope_value": "north-1"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["title"] == "Invalid Policy Request"
    assert "Unsupported policy scope_type" in detail["detail"]
