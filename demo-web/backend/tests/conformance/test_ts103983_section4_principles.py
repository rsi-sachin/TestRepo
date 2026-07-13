"""
Conformance tests: TS 103 983 section 4 (A1 general aspects).

Source: TS 103 983 V4.0.0 section 4.1 to 4.4

These tests focus on section-level architectural and capability assertions
that complement protocol-level behavior tests driven by TS 103 987/989.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api import oran
from app.models.a1_service import A1ServiceType
from app.models.oran import SpecType
from app.modules.e2_interface.service import E2InterfaceService
from app.modules.o1_interface.service import O1InterfaceService
from app.modules.simulators.info_sources.external_source import ExternalInfoSourceSimulator
from app.modules.simulators.info_sources.internal_source import InternalInfoSourceSimulator
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry
from app.services.oran_spec_discovery_service import OranSpecDiscoveryService


@pytest.fixture
def client() -> TestClient:
    # Keep this suite deterministic by resetting shared in-memory stores.
    oran.a1_policy_service._policies.clear()
    oran.a1_policy_service._policy_status.clear()
    oran.a1_policy_service._notification_destinations.clear()
    oran.a1_ei_service._ei_jobs.clear()
    oran.a1_ei_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)


def test_section_4_1_service_architecture_exposes_a1_p_and_a1_ei() -> None:
    """Section 4.1.3 service architecture includes both A1-P and A1-EI."""
    registry = A1ServiceRegistry()
    service_types = {svc.service_type for svc in registry.list_services()}

    assert A1ServiceType.A1_P in service_types
    assert A1ServiceType.A1_EI in service_types


def test_section_4_1_services_map_to_ts_103_983_principles() -> None:
    """Section 4 service metadata includes TS 103 983 as a governing spec."""
    policy_service = A1PolicyService()
    ei_service = A1EnrichmentInformationService()

    assert SpecType.TS_103_983 in policy_service.get_supported_specs()
    assert SpecType.TS_103_983 in ei_service.get_supported_specs()


def test_section_4_1_2_topology_stubs_are_available() -> None:
    """Section 4.1.2 topology participants exist as callable module stubs."""
    o1 = O1InterfaceService()
    e2 = E2InterfaceService()
    internal_source = InternalInfoSourceSimulator()
    external_source = ExternalInfoSourceSimulator()

    assert o1.health()["status"] == "stub"
    assert e2.health()["status"] == "stub"
    assert internal_source.status()["status"] == "stub"
    assert external_source.status()["status"] == "stub"


def test_section_4_2_policy_and_ei_ownership_operations_exist() -> None:
    """Section 4.2 ownership split is represented by policy and EI lifecycle APIs."""
    policy_service = A1PolicyService()
    ei_service = A1EnrichmentInformationService()

    assert hasattr(policy_service, "create_or_replace_policy")
    assert hasattr(policy_service, "delete_policy")
    assert hasattr(ei_service, "create_or_replace_ei_job")
    assert hasattr(ei_service, "delete_ei_job")


def test_section_4_2_status_feedback_paths_exist() -> None:
    """Section 4.2 feedback principles are represented by status and notify hooks."""
    policy_service = A1PolicyService()
    ei_service = A1EnrichmentInformationService()

    assert hasattr(policy_service, "get_policy_status")
    assert hasattr(policy_service, "notify_policy_status")
    assert hasattr(ei_service, "get_ei_job_status")
    assert hasattr(ei_service, "notify_ei_job_status")


def test_section_4_2_policy_lifecycle_behaves_end_to_end(client: TestClient) -> None:
    """Section 4.2 policy ownership and feedback work through lifecycle operations."""
    create_response = client.put(
        "/api/oran/a1/policytypes/default/policies/ts983-policy-1",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
        params={"notificationDestination": "https://example.com/policy-callback"},
    )
    assert create_response.status_code == 201

    update_response = client.put(
        "/api/oran/a1/policytypes/default/policies/ts983-policy-1",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "stmt-1", "action": "throttle"}],
        },
        params={"notificationDestination": "https://example.com/policy-callback"},
    )
    assert update_response.status_code == 200

    status_response = client.get(
        "/api/oran/a1/policytypes/default/policies/ts983-policy-1/status"
    )
    assert status_response.status_code == 200
    assert status_response.json()["enforcement_status"] == "ACCEPTED"

    delete_response = client.delete(
        "/api/oran/a1/policytypes/default/policies/ts983-policy-1"
    )
    assert delete_response.status_code == 204

    status_after_delete = client.get(
        "/api/oran/a1/policytypes/default/policies/ts983-policy-1/status"
    )
    assert status_after_delete.status_code == 404


def test_section_4_2_ei_job_lifecycle_behaves_end_to_end(client: TestClient) -> None:
    """Section 4.2 EI ownership and delivery-state behavior work through EI job lifecycle operations."""
    create_response = client.put(
        "/api/oran/a1/eitypes/default/eijobs/ts983-ei-1",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"workload": "baseline"},
            "jobStatusNotificationUri": "https://example.com/ei-status",
            "jobResultUri": "https://example.com/ei-result",
        },
    )
    assert create_response.status_code == 201

    list_jobs_response = client.get("/api/oran/a1/eijobs", params={"eiTypeId": "default"})
    assert list_jobs_response.status_code == 200
    assert "ts983-ei-1" in list_jobs_response.json()

    status_response = client.get("/api/oran/a1/eitypes/default/eijobs/ts983-ei-1/status")
    assert status_response.status_code == 200
    assert status_response.json()["eiJobStatus"] == "ENABLED"

    delete_response = client.delete("/api/oran/a1/eitypes/default/eijobs/ts983-ei-1")
    assert delete_response.status_code == 204

    status_after_delete = client.get("/api/oran/a1/eitypes/default/eijobs/ts983-ei-1/status")
    assert status_after_delete.status_code == 404


def test_section_4_3_and_4_4_ei_delivery_capabilities_exist() -> None:
    """Section 4.3/4.4 EI discovery and delivery capabilities are implemented."""
    ei_service = A1EnrichmentInformationService()

    assert hasattr(ei_service, "list_ei_type_ids")
    assert hasattr(ei_service, "list_ei_job_ids")
    assert hasattr(ei_service, "deliver_ei_job_result")


def test_section_4_4_problem_details_contract_for_unknown_resources(client: TestClient) -> None:
    """Section 4.4 capability exposure includes deterministic error contracts for unknown resources."""
    policy_response = client.get("/api/oran/a1/policytypes/default/policies/missing-ts983")
    ei_response = client.get("/api/oran/a1/eitypes/default/eijobs/missing-ts983")

    assert policy_response.status_code == 404
    assert policy_response.headers["content-type"].startswith("application/problem+json")
    assert policy_response.json()["detail"]["title"] == "Policy Not Found"

    assert ei_response.status_code == 404
    assert ei_response.headers["content-type"].startswith("application/problem+json")
    assert ei_response.json()["detail"]["title"] == "EI Job Not Found"


def test_section_4_spec_catalog_includes_ts_103_983() -> None:
    """TS 103 983 is a canonical selectable spec in discovery metadata."""
    definitions = OranSpecDiscoveryService.SPEC_DEFINITIONS
    ts_103_983 = definitions.get("TS_103_983")

    assert ts_103_983 is not None
    assert ts_103_983["ts_number"] == "TS 103 983"
    assert ts_103_983["number_token"] == "103983"
