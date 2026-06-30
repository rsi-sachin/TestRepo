"""O1 interface semantic validators."""

from app.modules.o1_interface.models import O1Request


def validate_o1_request(request: O1Request) -> tuple[bool, str]:
    """Validate semantic constraints that are not covered by schema types."""
    if request.operation in {"set", "notify"} and not request.payload:
        return False, "Payload is required for set and notify operations"
    return True, "ok"
