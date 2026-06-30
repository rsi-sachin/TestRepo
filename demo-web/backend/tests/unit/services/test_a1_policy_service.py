import pytest

from app.models.a1_policy_models import PolicyObject
from app.services.a1_policy_service import A1PolicyService


def _sample_policy(statement: str = "allow") -> PolicyObject:
    return PolicyObject(
        scope={"scope_type": "cell", "scope_value": "001"},
        policy_statements=[{"id": "rule-1", "action": statement}],
    )


def test_list_policy_type_ids_contains_default() -> None:
    service = A1PolicyService()

    assert "default" in service.list_policy_type_ids()


def test_create_get_status_and_delete_policy() -> None:
    service = A1PolicyService()

    created, was_created = service.create_or_replace_policy(
        policy_type_id="default",
        policy_id="policy-1",
        policy=_sample_policy(),
        notification_destination="https://example.com/callback",
    )
    fetched = service.get_policy("default", "policy-1")
    status = service.get_policy_status("default", "policy-1")

    assert created.policy_statements[0]["action"] == "allow"
    assert was_created is True
    assert fetched.scope["scope_type"] == "cell"
    assert status.enforcement_status == "ACCEPTED"

    service.delete_policy("default", "policy-1")
    with pytest.raises(KeyError):
        service.get_policy("default", "policy-1")


def test_create_policy_rejects_unknown_policy_type() -> None:
    service = A1PolicyService()

    with pytest.raises(KeyError):
        service.create_or_replace_policy(
            policy_type_id="unknown",
            policy_id="policy-1",
            policy=_sample_policy(),
            notification_destination="https://example.com/callback",
        )


def test_get_policy_returns_deepcopy_to_prevent_shared_mutation() -> None:
    service = A1PolicyService()
    service.create_or_replace_policy(
        policy_type_id="default",
        policy_id="policy-1",
        policy=_sample_policy("allow"),
        notification_destination="https://example.com/callback",
    )

    fetched = service.get_policy("default", "policy-1")
    fetched.policy_statements[0]["action"] = "deny"

    assert service.get_policy("default", "policy-1").policy_statements[0]["action"] == "allow"


def test_delete_unknown_policy_raises_key_error() -> None:
    service = A1PolicyService()

    with pytest.raises(KeyError):
        service.delete_policy("default", "missing-policy")


# --- §5.2.3 unit coverage ---

def test_list_policy_type_ids_returns_empty_list_when_store_is_cleared() -> None:
    """list_policy_type_ids() must return [] (not raise) when _policy_types is empty."""
    service = A1PolicyService()
    service._policy_types.clear()

    result = service.list_policy_type_ids()

    assert result == []


def test_get_policy_type_raises_key_error_for_unknown_type_id() -> None:
    """get_policy_type() must raise KeyError for an unregistered policyTypeId per §5.2.3.3."""
    service = A1PolicyService()

    with pytest.raises(KeyError, match="Policy type not found"):
        service.get_policy_type("nonexistent-type")
