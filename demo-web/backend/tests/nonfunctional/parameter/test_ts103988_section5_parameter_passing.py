import pytest

from app.models.a1_policy_models import PolicyObject
from app.services.a1_policy_service import A1PolicyService


@pytest.mark.parametrize(
    "scope_payload",
    [
        {"scope_type": "cell", "scope_value": "001"},
        {"scope_type": "slice", "scope_value": "gold"},
        {"scope_type": "ue", "scope_value": "ue-0001"},
        {"scope_type": "ue_group", "scope_value": "group-a"},
        {"scope_type": "qos_flow", "scope_value": "qfi-9"},
    ],
)
def test_section5_parameter_supported_scope_types_round_trip(scope_payload: dict) -> None:
    service = A1PolicyService()

    policy = PolicyObject(
        scope=scope_payload,
        policy_statements=[{"id": "stmt-param", "action": "allow"}],
    )
    service.create_or_replace_policy("default", "param-s5", policy)

    fetched = service.get_policy("default", "param-s5")
    assert fetched.scope == scope_payload


def test_section5_parameter_invalid_amf_region_id_is_rejected() -> None:
    service = A1PolicyService()

    policy = PolicyObject(
        scope={
            "scope_type": "cell",
            "scope_value": "001",
            "amfRegionId": "ZZ",
        },
        policy_statements=[{"id": "stmt-param-invalid", "action": "allow"}],
    )

    with pytest.raises(ValueError, match="amfRegionId"):
        service.create_or_replace_policy("default", "param-invalid", policy)
