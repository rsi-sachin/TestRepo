from app.models.a1_policy_models import PolicyObject
from app.services.a1_policy_service import A1PolicyService


def test_section5_stress_repeated_replace_stays_queryable() -> None:
    service = A1PolicyService()

    for i in range(180):
        service.create_or_replace_policy(
            policy_type_id="default",
            policy_id="stress-pol",
            policy=PolicyObject(
                scope={"scope_type": "cell", "scope_value": "stress"},
                policy_statements=[{"id": f"stmt-stress-{i}", "action": "allow"}],
            ),
        )

    policy = service.get_policy("default", "stress-pol")
    assert policy.policy_statements[0]["id"].startswith("stmt-stress-")
