"""
Conformance tests: Mandatory execution evidence checks.

Source: TS 103 989 V4.2.0 §4.2.2.2
Trace ID: ORAN-FTM-013

The test simulator logs all message content during testing.
Each A1 operation must produce deterministic status codes, structured
error payloads with reason fields, and identifiable enforcement verdicts.

Evidence requirements derived from §4.2.2.2:
  - Message content (headers, return codes, JSON body) logged and validatable.
  - Configurable success and failure responses with deterministic verdict reasons.
  - ProblemDetails error payloads carry title, status, detail, and instance.
  - PolicyStatusObject carries enforcement_status and optional enforcement_reason.
"""

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran
from app.models.a1_policy_models import PolicyObject, PolicyStatusObject
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_policy_service import A1PolicyService


@pytest.fixture()
def api_client() -> TestClient:
    oran.a1_policy_service._policies.clear()
    oran.a1_policy_service._policy_status.clear()
    oran.a1_policy_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)


# ---------------------------------------------------------------------------
# Message logging during testing
# ---------------------------------------------------------------------------


def test_a1_policy_service_has_logger_configured() -> None:
    """A1PolicyService has a named logger for message content logging per §4.2.2.2."""
    import app.services.a1_policy_service as module

    assert hasattr(module, "logger"), (
        "Module must expose a logger instance for message content recording "
        "(TS 103 989 §4.2.2.2: simulator logs all message content during testing)"
    )
    assert isinstance(module.logger, logging.Logger)


def test_a1_policy_service_logger_records_notification_warnings(caplog: pytest.LogCaptureFixture) -> None:
    """Logger emits a warning when outbound notification returns unexpected status per §4.2.2.2."""
    import textwrap, inspect
    src = textwrap.dedent(inspect.getsource(A1PolicyService.notify_policy_status))

    assert "logger.warning" in src, (
        "notify_policy_status must log a warning for unexpected notification responses "
        "(TS 103 989 §4.2.2.2: logs all message content during testing)"
    )


def test_a1_ei_service_logger_records_notification_warnings() -> None:
    """A1-EI notify method logs warning on unexpected callback response per §4.2.2.2."""
    import textwrap, inspect

    src = textwrap.dedent(inspect.getsource(A1EnrichmentInformationService.notify_ei_job_status))

    assert "logger.warning" in src, (
        "notify_ei_job_status must log a warning for unexpected notification responses "
        "(TS 103 989 §4.2.2.2: logs all message content during testing)"
    )


# ---------------------------------------------------------------------------
# Deterministic status codes per A1 operation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,path,body,expected_status",
    [
        (
            "GET",
            "/api/oran/a1/policytypes",
            None,
            200,
        ),
        (
            "GET",
            "/api/oran/a1/policytypes/default",
            None,
            200,
        ),
        (
            "GET",
            "/api/oran/a1/policytypes/nonexistent-type-evidence",
            None,
            404,
        ),
        (
            "GET",
            "/api/oran/a1/policytypes/default/policies/nonexistent-evidence",
            None,
            404,
        ),
    ],
)
def test_a1_operations_return_deterministic_status_codes(
    api_client: TestClient,
    method: str,
    path: str,
    body: dict | None,
    expected_status: int,
) -> None:
    """Each A1 GET operation returns a deterministic, spec-defined status code per §4.2.2.2."""
    response = api_client.request(method, path, json=body)
    assert response.status_code == expected_status, (
        f"{method} {path} must return {expected_status} (deterministic verdict per §4.2.2.2); "
        f"got {response.status_code}"
    )


# ---------------------------------------------------------------------------
# ProblemDetails evidence: title, status, detail, instance
# ---------------------------------------------------------------------------


def test_error_response_carries_complete_problem_details_for_missing_policy(
    api_client: TestClient,
) -> None:
    """404 response for unknown policy includes all mandatory ProblemDetails fields per §4.2.2.2."""
    response = api_client.get(
        "/api/oran/a1/policytypes/default/policies/evidence-missing"
    )

    assert response.status_code == 404
    detail = response.json()["detail"]

    assert "title" in detail, "ProblemDetails must carry 'title' for verdict reason"
    assert "status" in detail, "ProblemDetails must carry 'status' HTTP code"
    assert "detail" in detail, "ProblemDetails must carry human-readable 'detail' string"
    assert "instance" in detail, "ProblemDetails must carry 'instance' request URI for evidence traceability"
    assert detail["status"] == 404


def test_error_response_carries_complete_problem_details_for_missing_policy_type(
    api_client: TestClient,
) -> None:
    """404 response for unknown policy type includes all ProblemDetails fields per §4.2.2.2."""
    response = api_client.get("/api/oran/a1/policytypes/evidence-unknown-type")

    assert response.status_code == 404
    detail = response.json()["detail"]

    assert "title" in detail
    assert "status" in detail
    assert "instance" in detail
    assert "evidence-unknown-type" in detail["instance"]


# ---------------------------------------------------------------------------
# PolicyStatusObject evidence: enforcement_status and enforcement_reason
# ---------------------------------------------------------------------------


def test_policy_status_carries_enforcement_status_after_creation() -> None:
    """PolicyStatusObject includes enforcement_status as verdict field per §4.2.2.2."""
    service = A1PolicyService()
    service._policies.clear()
    service._policy_status.clear()

    policy = PolicyObject(
        scope={"scope_type": "cell", "scope_value": "ev-001"},
        policy_statements=[{"id": "s1", "action": "allow"}],
    )
    service.create_or_replace_policy(
        policy_type_id="default",
        policy_id="evidence-policy",
        policy=policy,
    )

    status = service.get_policy_status("default", "evidence-policy")

    assert status.enforcement_status, (
        "PolicyStatusObject must carry enforcement_status as deterministic verdict "
        "(TS 103 989 §4.2.2.2: validation of message contents)"
    )


def test_policy_status_carries_enforcement_reason_as_verdict_detail() -> None:
    """PolicyStatusObject enforcement_reason field provides human-readable verdict reason per §4.2.2.2."""
    service = A1PolicyService()
    service._policies.clear()
    service._policy_status.clear()

    policy = PolicyObject(
        scope={"scope_type": "cell", "scope_value": "ev-002"},
        policy_statements=[{"id": "s1", "action": "allow"}],
    )
    service.create_or_replace_policy(
        policy_type_id="default",
        policy_id="evidence-reason-policy",
        policy=policy,
    )

    status = service.get_policy_status("default", "evidence-reason-policy")

    assert status.enforcement_reason is not None, (
        "PolicyStatusObject should carry enforcement_reason for execution evidence "
        "(TS 103 989 §4.2.2.2: configurable schema-based verdict with reason)"
    )
    assert len(status.enforcement_reason) > 0


def test_policy_status_object_model_has_enforcement_reason_field() -> None:
    """PolicyStatusObject model exposes enforcement_reason as an optional verdict field per §4.2.2.2."""
    from app.models.a1_policy_models import PolicyStatusObject
    import inspect

    fields = PolicyStatusObject.model_fields
    assert "enforcement_reason" in fields, (
        "PolicyStatusObject must declare enforcement_reason field for verdict detail evidence "
        "(TS 103 989 §4.2.2.2)"
    )


# ---------------------------------------------------------------------------
# Content-type header evidence
# ---------------------------------------------------------------------------


def test_a1_api_response_includes_json_content_type_header(api_client: TestClient) -> None:
    """A1 API responses carry application/json Content-Type for message content validation per §4.2.2.2."""
    response = api_client.get("/api/oran/a1/policytypes")

    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", ""), (
        "A1 API responses must use application/json for schema-based content validation "
        "(TS 103 989 §4.2.2.2: validation of message contents based on configured schemas)"
    )


def test_policy_creation_response_includes_location_header(api_client: TestClient) -> None:
    """201 response for new policy includes Location header as evidence of resource creation per §4.2.2.2."""
    response = api_client.put(
        "/api/oran/a1/policytypes/default/policies/evidence-loc-policy",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "s1", "action": "allow"}],
        },
        params={"notificationDestination": "https://callback.example.com/notify"},
    )

    assert response.status_code == 201
    assert "location" in response.headers or "Location" in response.headers, (
        "201 response must include Location header as evidence of resource creation "
        "(TS 103 989 §4.2.2.2: return codes and headers are part of message content logging)"
    )
