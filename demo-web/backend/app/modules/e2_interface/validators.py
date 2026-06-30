"""E2 interface semantic validators."""

from app.modules.e2_interface.models import E2Request


def validate_e2_message(request: E2Request) -> tuple[bool, str]:
    """Validate semantic constraints that are not covered by schema types."""
    if request.message_type == "subscription" and "event_trigger" not in request.payload:
        return False, "subscription payload must include event_trigger"

    if request.message_type in {"indication", "control"} and "ran_function_id" not in request.payload:
        return False, "indication/control payload must include ran_function_id"

    return True, "ok"
