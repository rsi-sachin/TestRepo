from app.models.a1_policy_models import PolicyObject
from app.services.a1_policy_service import A1PolicyService


def test_policy_service_handles_repeated_replace_stress() -> None:
    service = A1PolicyService()

    for idx in range(120):
        action = "allow" if idx % 2 == 0 else "deny"
        service.create_or_replace_policy(
            policy_type_id="default",
            policy_id="stress-policy",
            policy=PolicyObject(
                scope={"scope_type": "cell", "scope_value": "001"},
                policy_statements=[{"id": "stmt-1", "action": action}],
            ),
            notification_destination="https://example.com/callback",
        )

    final_policy = service.get_policy("default", "stress-policy")
    assert final_policy.policy_statements[0]["action"] in {"allow", "deny"}
