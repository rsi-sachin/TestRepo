from app.models.a1_policy_models import PolicyObject
from app.services.a1_policy_service import A1PolicyService


def test_policy_service_cleans_up_internal_state_after_delete_cycles() -> None:
    service = A1PolicyService()

    for idx in range(25):
        policy_id = f"mem-{idx}"
        service.create_or_replace_policy(
            policy_type_id="default",
            policy_id=policy_id,
            policy=PolicyObject(
                scope={"scope_type": "cell", "scope_value": str(idx)},
                policy_statements=[{"id": f"stmt-{idx}", "action": "allow"}],
            ),
            notification_destination="https://example.com/callback",
        )

    assert len(service._policies) == 25
    assert len(service._policy_status) == 25
    assert len(service._notification_destinations) == 25

    for idx in range(25):
        service.delete_policy("default", f"mem-{idx}")

    assert service._policies == {}
    assert service._policy_status == {}
    assert service._notification_destinations == {}
