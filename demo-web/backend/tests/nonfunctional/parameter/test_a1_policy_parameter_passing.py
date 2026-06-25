import pytest

from app.models.a1_policy_models import CreateOrReplacePolicyRequest


@pytest.mark.parametrize(
    "destination",
    [
        "https://example.com/callback",
        "https://example.com/status/notify",
    ],
)
def test_notification_destination_accepts_valid_urls(destination: str) -> None:
    request = CreateOrReplacePolicyRequest(
        policy={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
        notification_destination=destination,
    )

    assert str(request.notification_destination).startswith("https://")


@pytest.mark.parametrize("destination", ["", "not-a-url", "ftp://example.com", "https://"])
def test_notification_destination_rejects_invalid_urls(destination: str) -> None:
    with pytest.raises(Exception):
        CreateOrReplacePolicyRequest(
            policy={
                "scope": {"scope_type": "cell", "scope_value": "001"},
                "policy_statements": [{"id": "stmt-1", "action": "allow"}],
            },
            notification_destination=destination,
        )
