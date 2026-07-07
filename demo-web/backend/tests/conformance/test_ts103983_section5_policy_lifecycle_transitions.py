"""
Conformance tests: TS 103 983 section 5.1.3 policy lifecycle transitions.
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


def test_section_5_1_3_policy_can_transition_from_accepted_to_enforced(client: TestClient) -> None:
    create = client.put(
        "/api/oran/a1/policytypes/default/policies/policy-lifecycle-1",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
    )
    assert create.status_code == 201

    transitioned = oran.a1_policy_service.transition_policy_status(
        "default",
        "policy-lifecycle-1",
        "ENFORCED",
        reason="Policy activated by producer",
    )

    assert transitioned.enforcement_status == "ENFORCED"
    assert transitioned.enforcement_reason == "Policy activated by producer"



def test_section_5_1_3_policy_allows_enforced_to_not_enforced_toggle(client: TestClient) -> None:
    client.put(
        "/api/oran/a1/policytypes/default/policies/policy-lifecycle-2",
        json={
            "scope": {"scope_type": "cell", "scope_value": "002"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
    )

    oran.a1_policy_service.transition_policy_status(
        "default",
        "policy-lifecycle-2",
        "ENFORCED",
        reason="Activated",
    )
    toggled = oran.a1_policy_service.transition_policy_status(
        "default",
        "policy-lifecycle-2",
        "NOT_ENFORCED",
        reason="Superseded by newer policy",
    )

    assert toggled.enforcement_status == "NOT_ENFORCED"



def test_section_5_1_3_invalid_transition_is_rejected(client: TestClient) -> None:
    client.put(
        "/api/oran/a1/policytypes/default/policies/policy-lifecycle-3",
        json={
            "scope": {"scope_type": "cell", "scope_value": "003"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
    )

    with pytest.raises(ValueError, match="Invalid policy status transition"):
        oran.a1_policy_service.transition_policy_status(
            "default",
            "policy-lifecycle-3",
            "ACCEPTED",
        )
