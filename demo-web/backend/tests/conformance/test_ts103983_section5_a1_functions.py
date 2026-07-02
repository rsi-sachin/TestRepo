"""
Conformance tests: TS 103 983 section 5 (A1 functions).

Source: TS 103 983 V4.0.0 section 5.1 and 5.2

Coverage in this suite focuses on:
- Policy scope identifier handling (§5.1.4.1 to §5.1.4.5)
- Policy lifecycle transition semantics (§5.1.3)
- EI lifecycle resilience/reconciliation behavior (§5.2.3.3.1 and §5.2.3.3.2)
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api import oran


@pytest.fixture
def client() -> TestClient:
    # Reset shared in-memory stores before each test for deterministic assertions.
    oran.a1_policy_service._policies.clear()
    oran.a1_policy_service._policy_status.clear()
    oran.a1_policy_service._notification_destinations.clear()
    oran.a1_ei_service._ei_jobs.clear()
    oran.a1_ei_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)


@pytest.mark.parametrize(
    "scope_payload",
    [
        {"scope_type": "cell", "scope_value": "cell-001"},
        {"scope_type": "slice", "scope_value": "slice-gold"},
        {"scope_type": "ue", "scope_value": "imsi-001010000000001"},
        {"scope_type": "region", "scope_value": "region-west"},
        {"scope_type": "qos", "scope_value": "qci-9"},
    ],
)
def test_section_5_1_4_policy_scope_identifier_variants_are_persisted(
    client: TestClient, scope_payload: dict
) -> None:
    """Policy scope identifiers are accepted and preserved across create/query flows."""
    create = client.put(
        "/api/oran/a1/policytypes/default/policies/scope-test",
        json={
            "scope": scope_payload,
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
    )
    assert create.status_code == 201

    fetched = client.get("/api/oran/a1/policytypes/default/policies/scope-test")
    assert fetched.status_code == 200
    assert fetched.json()["scope"] == scope_payload


def test_section_5_1_3_policy_lifecycle_create_update_delete_status_transitions(
    client: TestClient,
) -> None:
    """Policy lifecycle transitions remain consistent across create, update, and delete."""
    create = client.put(
        "/api/oran/a1/policytypes/default/policies/lifecycle-1",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
        params={"notificationDestination": "https://example.com/policy-status"},
    )
    assert create.status_code == 201

    created_status = client.get(
        "/api/oran/a1/policytypes/default/policies/lifecycle-1/status"
    )
    assert created_status.status_code == 200
    assert created_status.json()["enforcement_status"] == "ACCEPTED"

    update = client.put(
        "/api/oran/a1/policytypes/default/policies/lifecycle-1",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "stmt-1", "action": "throttle"}],
        },
    )
    assert update.status_code == 200

    # Updating without notificationDestination intentionally clears subscription.
    assert (
        oran.a1_policy_service._notification_destinations.get(("default", "lifecycle-1"))
        is None
    )

    delete = client.delete("/api/oran/a1/policytypes/default/policies/lifecycle-1")
    assert delete.status_code == 204

    status_after_delete = client.get(
        "/api/oran/a1/policytypes/default/policies/lifecycle-1/status"
    )
    assert status_after_delete.status_code == 404


def test_section_5_2_3_3_1_ei_update_reconciles_partial_payload_with_existing_job(
    client: TestClient,
) -> None:
    """EI update reconciliation rejects incomplete payloads without corrupting stored state."""
    create = client.put(
        "/api/oran/a1/eitypes/default/eijobs/reconcile-1",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"profile": "baseline"},
            "jobStatusNotificationUri": "https://example.com/status-initial",
            "jobResultUri": "https://example.com/result-initial",
        },
    )
    assert create.status_code == 201

    update = client.put(
        "/api/oran/a1/eitypes/default/eijobs/reconcile-1",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"profile": "updated"},
        },
    )
    assert update.status_code == 400
    assert update.json()["detail"]["title"] == "Invalid EI Job Request"

    fetched = client.get("/api/oran/a1/eitypes/default/eijobs/reconcile-1")
    assert fetched.status_code == 200
    payload = fetched.json()["ei_job"]
    assert payload["jobDefinition"] == {"profile": "baseline"}
    assert payload["jobResultUri"] == "https://example.com/result-initial"
    assert payload["jobStatusNotificationUri"] == "https://example.com/status-initial"


def test_section_5_2_3_3_1_ei_reconciliation_detects_cross_type_job_id_conflict(
    client: TestClient,
) -> None:
    """EI reconciliation path rejects duplicate eiJobId across EI types with conflict semantics."""
    # Add a second EI type to exercise cross-type disambiguation behavior.
    oran.a1_ei_service._ei_types["alt"] = {
        "ei_type_id": "alt",
        "ei_schema": {
            "type": "object",
            "required": ["eiTypeId", "jobDefinition", "jobResultUri"],
        },
        "supports_ei_job_creation": True,
    }

    create_default = client.put(
        "/api/oran/a1/eitypes/default/eijobs/shared-job",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"k": "v"},
            "jobResultUri": "https://example.com/default-result",
        },
    )
    assert create_default.status_code == 201

    create_alt = client.put(
        "/api/oran/a1/eitypes/alt/eijobs/shared-job",
        json={
            "eiTypeId": "alt",
            "jobDefinition": {"k": "v2"},
            "jobResultUri": "https://example.com/alt-result",
        },
    )
    assert create_alt.status_code == 409
    assert create_alt.json()["detail"]["title"] == "EI Job Conflict"


def test_section_5_2_3_3_2_ei_delete_reconciliation_cleans_notification_mapping(
    client: TestClient,
) -> None:
    """Deleting an EI job reconciles all related in-memory metadata and prevents stale reads."""
    create = client.put(
        "/api/oran/a1/eitypes/default/eijobs/reconcile-delete-1",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"task": "x"},
            "jobStatusNotificationUri": "https://example.com/notify",
            "jobResultUri": "https://example.com/result",
        },
    )
    assert create.status_code == 201

    key = ("default", "reconcile-delete-1")
    assert key in oran.a1_ei_service._notification_destinations

    delete = client.delete("/api/oran/a1/eitypes/default/eijobs/reconcile-delete-1")
    assert delete.status_code == 204
    assert key not in oran.a1_ei_service._notification_destinations

    status_after_delete = client.get(
        "/api/oran/a1/eitypes/default/eijobs/reconcile-delete-1/status"
    )
    assert status_after_delete.status_code == 404


def test_section_5_2_3_3_2_ei_type_filtered_and_global_listing_stay_consistent(
    client: TestClient,
) -> None:
    """Reconciliation keeps EI job list views consistent for both type-filtered and global queries."""
    # Add a second EI type to validate global and per-type list reconciliation.
    oran.a1_ei_service._ei_types["alt"] = {
        "ei_type_id": "alt",
        "ei_schema": {
            "type": "object",
            "required": ["eiTypeId", "jobDefinition", "jobResultUri"],
        },
        "supports_ei_job_creation": True,
    }

    create_default = client.put(
        "/api/oran/a1/eitypes/default/eijobs/job-default",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"mode": "d"},
            "jobResultUri": "https://example.com/default",
        },
    )
    assert create_default.status_code == 201

    create_alt = client.put(
        "/api/oran/a1/eitypes/alt/eijobs/job-alt",
        json={
            "eiTypeId": "alt",
            "jobDefinition": {"mode": "a"},
            "jobResultUri": "https://example.com/alt",
        },
    )
    assert create_alt.status_code == 201

    default_only = client.get("/api/oran/a1/eijobs", params={"eiTypeId": "default"})
    assert default_only.status_code == 200
    assert default_only.json() == ["job-default"]

    global_list = client.get("/api/oran/a1/eijobs")
    assert global_list.status_code == 200
    assert set(global_list.json()) == {"job-default", "job-alt"}
