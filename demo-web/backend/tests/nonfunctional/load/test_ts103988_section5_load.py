from app.models.a1_policy_models import PolicyObject
from app.services.a1_policy_service import A1PolicyService


def test_section5_load_policy_handles_moderate_throughput() -> None:
    service = A1PolicyService()

    total = 60
    for i in range(total):
        service.create_or_replace_policy(
            policy_type_id="default",
            policy_id=f"load-pol-{i}",
            policy=PolicyObject(
                scope={"scope_type": "cell", "scope_value": str(i)},
                policy_statements=[{"id": f"stmt-load-{i}", "action": "allow"}],
            ),
        )

    assert len(service.list_policy_ids("default")) == total
