"""
Conformance tests: Test simulator capability verification.

Source: TS 103 989 V4.2.0 §4.2.2.2
Trace ID: ORAN-FTM-013

§4.2.2.2 Test simulator
  The test simulator has A1-P Producer and A1-EI Consumer that both have HTTP
  Client and HTTP Server capabilities and have flexibility to generate, receive
  and validate HTTP messages for all the A1 procedures.  The test simulator
  logs all message content during the testing.

  A1-P Producer simulator capabilities:
    - Enable and disable policy types
    - Changing parameters in A1-P procedure response messages
    - Responding with success and failure messages
    - Ability to deliver policy status notifications by sending HTTP POST
      messages with JSON body based on configured schemas
    - Validation of message contents based on configured schemas

  A1-EI Consumer simulator capabilities:
    - Send query messages for EI types
    - Create and delete EI jobs for available EI types
    - Request and receive EI job status notifications and EI job results
"""

import inspect
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran
from app.models.a1_policy_models import PolicyObject, PolicyStatusObject, PolicyTypeObject
from app.models.a1_service import A1ServiceType
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry


@pytest.fixture()
def fresh_service() -> A1PolicyService:
    service = A1PolicyService()
    service._policies.clear()
    service._policy_status.clear()
    service._notification_destinations.clear()
    return service


@pytest.fixture()
def api_client() -> TestClient:
    oran.a1_policy_service._policies.clear()
    oran.a1_policy_service._policy_status.clear()
    oran.a1_policy_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)


# ---------------------------------------------------------------------------
# §4.2.2.2 — A1-P Producer: enable and disable policy types
# ---------------------------------------------------------------------------


def test_simulator_a1_p_producer_can_enable_policy_type(fresh_service: A1PolicyService) -> None:
    """Simulator can register (enable) a new policy type per §4.2.2.2."""
    new_type = PolicyTypeObject(
        policy_type_id="qos-v1",
        policy_schema={"type": "object", "required": ["policy_statements"]},
        policy_status_schema={"type": "object", "required": ["policy_id", "enforcement_status"]},
        supports_policy_creation=True,
    )
    fresh_service._policy_types["qos-v1"] = new_type

    assert "qos-v1" in fresh_service.list_policy_type_ids()
    assert fresh_service.get_policy_type("qos-v1").supports_policy_creation is True


def test_simulator_a1_p_producer_can_disable_policy_type(fresh_service: A1PolicyService) -> None:
    """Simulator can disable policy creation on a policy type per §4.2.2.2."""
    fresh_service._policy_types["default"].supports_policy_creation = False

    policy_type = fresh_service.get_policy_type("default")
    assert policy_type.supports_policy_creation is False

    with pytest.raises(ValueError):
        fresh_service.create_or_replace_policy(
            policy_type_id="default",
            policy_id="should-fail",
            policy=PolicyObject(
                scope={"scope_type": "cell", "scope_value": "001"},
                policy_statements=[{"id": "s1", "action": "block"}],
            ),
        )

    # restore
    fresh_service._policy_types["default"].supports_policy_creation = True


# ---------------------------------------------------------------------------
# §4.2.2.2 — A1-P Producer: configurable response parameters
# ---------------------------------------------------------------------------


def test_simulator_a1_p_producer_returns_201_on_policy_creation(api_client: TestClient) -> None:
    """Simulator responds with 201 Created when policy did not exist per §4.2.2.2."""
    response = api_client.put(
        "/api/oran/a1/policytypes/default/policies/sim-cap-policy-new",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "s1", "action": "allow"}],
        },
        params={"notificationDestination": "https://callback.example.com/notify"},
    )

    assert response.status_code == 201
    assert "Location" in response.headers


def test_simulator_a1_p_producer_returns_200_on_policy_update(api_client: TestClient) -> None:
    """Simulator responds with 200 OK when replacing an existing policy per §4.2.2.2."""
    policy_payload = {
        "scope": {"scope_type": "cell", "scope_value": "001"},
        "policy_statements": [{"id": "s1", "action": "allow"}],
    }
    api_client.put(
        "/api/oran/a1/policytypes/default/policies/sim-cap-policy-existing",
        json=policy_payload,
        params={"notificationDestination": "https://callback.example.com/notify"},
    )

    update_response = api_client.put(
        "/api/oran/a1/policytypes/default/policies/sim-cap-policy-existing",
        json=policy_payload,
        params={"notificationDestination": "https://callback.example.com/notify"},
    )

    assert update_response.status_code == 200


def test_simulator_a1_p_producer_responds_with_failure_404_for_unknown_policy(
    api_client: TestClient,
) -> None:
    """Simulator responds with 404 ProblemDetails for unknown policy per §4.2.2.2."""
    response = api_client.get(
        "/api/oran/a1/policytypes/default/policies/does-not-exist"
    )

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["status"] == 404
    assert "title" in detail
    assert "instance" in detail


def test_simulator_a1_p_producer_responds_with_failure_404_for_unknown_policy_type(
    api_client: TestClient,
) -> None:
    """Simulator responds with 404 for unknown policy type per §4.2.2.2."""
    response = api_client.get("/api/oran/a1/policytypes/unknown-type-xyz")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# §4.2.2.2 — A1-P Producer: policy status notification via HTTP POST
# ---------------------------------------------------------------------------


def test_simulator_a1_p_producer_has_notify_policy_status_capability() -> None:
    """Simulator has async notify_policy_status method for outbound HTTP POST per §4.2.2.2."""
    service = A1PolicyService()

    assert hasattr(service, "notify_policy_status"), (
        "A1-P Producer simulator must have notify_policy_status capability "
        "(TS 103 989 §4.2.2.2: deliver policy status notifications via HTTP POST)"
    )
    assert inspect.iscoroutinefunction(service.notify_policy_status), (
        "notify_policy_status must be async (HTTP Client role per §4.2.2.2)"
    )


def test_simulator_a1_p_producer_notify_signature_accepts_destination_and_status() -> None:
    """notify_policy_status signature accepts destination URL and PolicyStatusObject per §4.2.2.2."""
    sig = inspect.signature(A1PolicyService.notify_policy_status)
    params = list(sig.parameters.keys())

    assert "destination" in params, "notify_policy_status must accept 'destination' (callback URI)"
    assert "status_obj" in params, "notify_policy_status must accept 'status_obj' (PolicyStatusObject)"


# ---------------------------------------------------------------------------
# §4.2.2.2 — A1-P Producer: message validation based on configured schemas
# ---------------------------------------------------------------------------


def test_simulator_a1_p_producer_policy_type_schema_enables_content_validation(
    fresh_service: A1PolicyService,
) -> None:
    """Policy type schema is non-empty and can serve as validation basis per §4.2.2.2."""
    policy_type = fresh_service.get_policy_type("default")

    assert "required" in policy_type.policy_schema, (
        "Policy schema must include 'required' field list for message content validation "
        "(TS 103 989 §4.2.2.2)"
    )
    assert "required" in policy_type.policy_status_schema, (
        "PolicyStatus schema must include 'required' field list for message content validation "
        "(TS 103 989 §4.2.2.2)"
    )


def test_simulator_rejects_policy_with_missing_required_statements(
    api_client: TestClient,
) -> None:
    """Simulator rejects malformed policy missing required policy_statements per §4.2.2.2."""
    response = api_client.put(
        "/api/oran/a1/policytypes/default/policies/bad-policy",
        json={
            "policy": {
                "scope": {"scope_type": "cell", "scope_value": "001"},
                # policy_statements intentionally omitted
            },
            "notification_destination": "https://callback.example.com/notify",
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# §4.2.2.2 — A1-EI Consumer: service definition and HTTP capabilities
# ---------------------------------------------------------------------------


def test_simulator_a1_ei_consumer_service_is_defined_in_registry() -> None:
    """A1-EI Consumer service definition exists in registry per §4.2.2.2."""
    registry = A1ServiceRegistry()
    definition = registry.get_service_definition(A1ServiceType.A1_EI)

    assert definition.service_type == A1ServiceType.A1_EI
    assert "A1-EI Consumer" in definition.consumer_role.label


def test_simulator_a1_ei_consumer_has_ei_type_query_resource_domain() -> None:
    """A1-EI Consumer has resource domain for EI type queries per §4.2.2.2."""
    service = A1EnrichmentInformationService()
    domains = service.definition.resource_domains

    assert any("ei-type" in d.lower() for d in domains), (
        "A1-EI Consumer must expose EI type query domain "
        "(TS 103 989 §4.2.2.2: send query messages for EI types)"
    )


def test_simulator_a1_ei_consumer_has_ei_job_resource_domain() -> None:
    """A1-EI Consumer has resource domain for EI job create/delete per §4.2.2.2."""
    service = A1EnrichmentInformationService()
    domains = service.definition.resource_domains

    assert any("ei-job" in d.lower() for d in domains), (
        "A1-EI Consumer must expose EI job resource domain "
        "(TS 103 989 §4.2.2.2: create and delete EI jobs)"
    )


def test_simulator_a1_ei_consumer_has_notifications_resource_domain() -> None:
    """A1-EI Consumer has resource domain for EI job status notifications per §4.2.2.2."""
    service = A1EnrichmentInformationService()
    domains = service.definition.resource_domains

    assert any("notif" in d.lower() for d in domains), (
        "A1-EI Consumer must expose notifications resource domain "
        "(TS 103 989 §4.2.2.2: request and receive EI job status notifications and results)"
    )


def test_simulator_a1_ei_consumer_has_notify_ei_job_status_capability() -> None:
    """A1-EI consumer helper exposes async callback-notification client capability."""
    service = A1EnrichmentInformationService()

    assert hasattr(service, "notify_ei_job_status"), (
        "A1-EI Consumer simulator must expose notify_ei_job_status capability "
        "(TS 103 989 §4.2.2.2)"
    )
    assert inspect.iscoroutinefunction(service.notify_ei_job_status), (
        "notify_ei_job_status must be async (HTTP Client role per §4.2.2.2)"
    )


def test_simulator_a1_ei_notify_signature_accepts_destination_and_status_payload() -> None:
    """notify_ei_job_status accepts destination URI and status payload."""
    sig = inspect.signature(A1EnrichmentInformationService.notify_ei_job_status)
    params = list(sig.parameters.keys())

    assert "destination" in params, "notify_ei_job_status must accept callback destination"
    assert "status_obj" in params, "notify_ei_job_status must accept EI status payload"


def test_simulator_a1_ei_notify_uses_httpx_client() -> None:
    """A1-EI notification capability is backed by httpx for outbound callback POSTs."""
    src = inspect.getsource(A1EnrichmentInformationService.notify_ei_job_status)

    assert "httpx" in src, (
        "notify_ei_job_status must use httpx AsyncClient "
        "for outbound callback delivery checks (TS 103 989 §4.2.2.2)"
    )


# ---------------------------------------------------------------------------
# §4.2.2.2 — Both roles: HTTP Client and HTTP Server capability presence
# ---------------------------------------------------------------------------


def test_simulator_has_both_http_client_and_server_capabilities() -> None:
    """
    Simulator has HTTP Client (outbound notify) and HTTP Server (FastAPI routes) per §4.2.2.2.

    HTTP Server = FastAPI router with A1 routes (inbound request handling).
    HTTP Client = httpx-based notify_policy_status for outbound callbacks.
    """
    # HTTP Server: router has routes
    assert len(oran.router.routes) > 0, (
        "Simulator HTTP Server capability: router must have registered A1 routes"
    )

    # HTTP Client: notify_policy_status is async and uses httpx
    import inspect as _inspect
    import textwrap

    src = textwrap.dedent(_inspect.getsource(A1PolicyService.notify_policy_status))
    assert "httpx" in src, (
        "Simulator HTTP Client capability: notify_policy_status must use httpx "
        "for outbound HTTP POST callbacks (TS 103 989 §4.2.2.2)"
    )
