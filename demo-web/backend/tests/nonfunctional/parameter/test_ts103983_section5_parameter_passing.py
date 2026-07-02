import pytest

from app.models.a1_policy_models import PolicyObject
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_policy_service import A1PolicyService


@pytest.mark.parametrize(
    "scope_payload",
    [
        {"scope_type": "cell", "scope_value": "001"},
        {"scope_type": "slice", "scope_value": "gold"},
        {"scope_type": "region", "scope_value": "west"},
        {"scope_type": "qos", "scope_value": "qci-9"},
        {"scope_type": "ue", "scope_value": "imsi-001010000000001"},
    ],
)
def test_section5_parameter_scope_permutations_round_trip(scope_payload: dict) -> None:
    service = A1PolicyService()

    policy = PolicyObject(
        scope=scope_payload,
        policy_statements=[{"id": "stmt-1", "action": "allow"}],
    )
    service.create_or_replace_policy("default", "param-s5", policy)

    fetched = service.get_policy("default", "param-s5")
    assert fetched.scope == scope_payload


@pytest.mark.parametrize(
    "payload",
    [
        {"eiTypeId": "default", "jobDefinition": {"k": "v"}},
        {"eiTypeId": "default", "jobResultUri": "https://example.com/r"},
        {"jobDefinition": {"k": "v"}, "jobResultUri": "https://example.com/r"},
    ],
)
def test_section5_parameter_ei_required_fields_are_enforced(payload: dict) -> None:
    service = A1EnrichmentInformationService()

    with pytest.raises(ValueError):
        service.create_or_replace_ei_job("default", "ei-param", payload)
