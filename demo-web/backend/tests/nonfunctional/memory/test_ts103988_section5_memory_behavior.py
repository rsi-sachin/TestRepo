from app.models.a1_policy_models import PolicyObject
from app.services.a1_policy_service import A1PolicyService


def test_section5_memory_policy_create_delete_cycles_leave_no_residual_state() -> None:
    service = A1PolicyService()

    for i in range(40):
        service.create_or_replace_policy(
            policy_type_id="default",
            policy_id=f"mem-pol-{i}",
            policy=PolicyObject(
                scope={"scope_type": "cell", "scope_value": str(i)},
                policy_statements=[{"id": f"stmt-{i}", "action": "allow"}],
            ),
        )

    assert len(service.list_policy_ids("default")) == 40

    for i in range(40):
        service.delete_policy("default", f"mem-pol-{i}")

    assert service.list_policy_ids("default") == []
