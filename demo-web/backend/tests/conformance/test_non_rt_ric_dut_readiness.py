"""
Conformance tests: Non-RT RIC DUT readiness checks.

Source: TS 103 989 V4.2.0 §4.2.1 and §4.2.2.1
Trace ID: ORAN-FTM-013

§4.2.1 General
  Non-RT RIC is the device under test; clause 5 specifies conformance tests
  for A1-P Consumer and A1-EI Producer functionality as specified in A1AP.

§4.2.2.1 Device under test (Non-RT RIC)
  For enabling conformance testing, the Non-RT RIC has implemented A1-P Consumer
  and/or A1-EI Producer functionality and the procedures specified in A1AP that
  are required to perform testing of the applicable test cases.
  It also supports one agreed policy type and/or one agreed EI type.
"""

import pytest

from app.models.a1_service import A1RoleType, A1ServiceType
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry


# ---------------------------------------------------------------------------
# §4.2.2.1 — DUT role: A1-P Consumer
# ---------------------------------------------------------------------------


def test_non_rt_ric_dut_has_a1_p_consumer_role_defined() -> None:
    """Non-RT RIC DUT implements A1-P Consumer role per §4.2.2.1."""
    registry = A1ServiceRegistry()
    definition = registry.get_service_definition(A1ServiceType.A1_P)

    assert definition.consumer_role.role_type == A1RoleType.CONSUMER
    assert "A1-P Consumer" in definition.consumer_role.label


def test_non_rt_ric_dut_a1_p_consumer_can_initiate_policy_procedures() -> None:
    """Non-RT RIC (A1-P Consumer) can initiate create, query, and delete procedures per §4.2.2.1."""
    service = A1PolicyService()

    from app.models.a1_policy_models import PolicyObject

    policy = PolicyObject(
        scope={"scope_type": "cell", "scope_value": "cell-001"},
        policy_statements=[{"id": "stmt-1", "action": "allow"}],
    )

    created_policy, was_created = service.create_or_replace_policy(
        policy_type_id="default",
        policy_id="dut-readiness-policy",
        policy=policy,
    )
    assert was_created is True

    queried = service.get_policy("default", "dut-readiness-policy")
    assert queried.policy_statements[0]["action"] == "allow"

    service.delete_policy("default", "dut-readiness-policy")
    with pytest.raises(KeyError):
        service.get_policy("default", "dut-readiness-policy")


# ---------------------------------------------------------------------------
# §4.2.2.1 — DUT role: A1-EI Producer
# ---------------------------------------------------------------------------


def test_non_rt_ric_dut_has_a1_ei_producer_role_defined() -> None:
    """Non-RT RIC DUT implements A1-EI Producer role per §4.2.2.1."""
    registry = A1ServiceRegistry()
    definition = registry.get_service_definition(A1ServiceType.A1_EI)

    assert definition.producer_role.role_type == A1RoleType.PRODUCER
    assert "A1-EI Producer" in definition.producer_role.label


def test_non_rt_ric_dut_a1_ei_producer_service_is_reachable() -> None:
    """A1-EI Producer service is instantiable and carries its service definition per §4.2.2.1."""
    service = A1EnrichmentInformationService()
    definition = service.definition

    assert definition.service_type == A1ServiceType.A1_EI
    assert "/ei-jobs" in definition.resource_domains or "/ei-types" in definition.resource_domains


# ---------------------------------------------------------------------------
# §4.2.2.1 — Agreed policy type precondition
# ---------------------------------------------------------------------------


def test_non_rt_ric_dut_supports_at_least_one_agreed_policy_type() -> None:
    """DUT supports at least one agreed policy type as required by §4.2.2.1."""
    service = A1PolicyService()
    policy_type_ids = service.list_policy_type_ids()

    assert len(policy_type_ids) >= 1, (
        "Non-RT RIC DUT must support at least one agreed policy type for conformance testing "
        "(TS 103 989 §4.2.2.1)"
    )


def test_non_rt_ric_dut_agreed_policy_type_permits_policy_creation() -> None:
    """Agreed policy type allows policy formulation; DUT can create A1 policies per §4.2.2.1."""
    service = A1PolicyService()
    policy_type_ids = service.list_policy_type_ids()
    agreed_type_id = policy_type_ids[0]

    policy_type = service.get_policy_type(agreed_type_id)

    assert policy_type.supports_policy_creation is True, (
        f"Agreed policy type '{agreed_type_id}' must allow policy creation "
        "(TS 103 989 §4.2.2.1)"
    )


def test_non_rt_ric_dut_agreed_policy_type_has_policy_schema() -> None:
    """Agreed policy type carries a schema to validate PolicyObjects per §4.2.2.1."""
    service = A1PolicyService()
    agreed_type_id = service.list_policy_type_ids()[0]
    policy_type = service.get_policy_type(agreed_type_id)

    assert isinstance(policy_type.policy_schema, dict)
    assert len(policy_type.policy_schema) > 0, (
        "Policy schema must be non-empty to validate policy objects "
        "(TS 103 989 §4.2.2.1 requires schema-driven validation)"
    )


def test_non_rt_ric_dut_agreed_policy_type_has_status_schema() -> None:
    """Agreed policy type carries a PolicyStatusObject schema per §4.2.2.1."""
    service = A1PolicyService()
    agreed_type_id = service.list_policy_type_ids()[0]
    policy_type = service.get_policy_type(agreed_type_id)

    assert isinstance(policy_type.policy_status_schema, dict)
    assert len(policy_type.policy_status_schema) > 0, (
        "PolicyStatusObject schema must be non-empty; DUT must be able to validate "
        "PolicyStatusObjects based on agreed policy type schemas (TS 103 989 §4.2.2.1)"
    )


# ---------------------------------------------------------------------------
# §4.2.2.1 — A1-EI type precondition (registry-level check)
# ---------------------------------------------------------------------------


def test_non_rt_ric_dut_a1_ei_service_carries_ei_type_resource_domain() -> None:
    """A1-EI service definition includes EI type resource domain per §4.2.2.1."""
    service = A1EnrichmentInformationService()
    domains = service.definition.resource_domains

    assert any("ei-type" in d.lower() or "eitype" in d.lower() for d in domains), (
        "A1-EI Producer service must expose an EI type resource domain "
        "(TS 103 989 §4.2.2.1 requires DUT to support at least one agreed EI type)"
    )
