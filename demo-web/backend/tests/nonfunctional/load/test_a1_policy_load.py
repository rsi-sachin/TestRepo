from app.models.a1_policy_models import PolicyObject
from app.services.a1_policy_service import A1PolicyService


def test_policy_service_handles_moderate_load_create_and_status_reads() -> None:
    service = A1PolicyService()

    total = 40
    for idx in range(total):
        policy_id = f"load-{idx}"
        service.create_or_replace_policy(
            policy_type_id="default",
            policy_id=policy_id,
            policy=PolicyObject(
                scope={"scope_type": "cell", "scope_value": str(idx)},
                policy_statements=[{"id": f"stmt-{idx}", "action": "allow"}],
            ),
            notification_destination="https://example.com/callback",
        )

    for idx in range(total):
        policy_id = f"load-{idx}"
        status = service.get_policy_status("default", policy_id)
        assert status.enforcement_status == "ACCEPTED"
