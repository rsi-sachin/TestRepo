import pytest

from app.models.a1_policy_models import CreateOrReplacePolicyRequest
from app.services.a1_policy_service import A1PolicyService


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


# --- §5.2.3 parameter boundary tests for policyTypeId ---

@pytest.mark.parametrize(
    "policy_type_id",
    [
        "",                          # empty string
        " ",                         # whitespace only
        "a" * 256,                   # very long identifier
        "type/with/slashes",         # path separator chars
        "type with spaces",          # space in id
        "type\x00null",              # null byte
    ],
)
def test_get_policy_type_raises_for_unregistered_boundary_ids(policy_type_id: str) -> None:
    """get_policy_type() must raise KeyError for any unregistered id, including boundary values."""
    service = A1PolicyService()

    with pytest.raises(KeyError):
        service.get_policy_type(policy_type_id)
