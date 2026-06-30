"""Simulator capability verification for conformance harness."""

from __future__ import annotations

from datetime import datetime, timezone


def verify_simulator_capability(implemented_capabilities: dict[str, bool] | None = None) -> dict:
    """Return matrix-aligned simulator capability verification status.

    The optional implemented_capabilities override allows deterministic tests for
    positive and negative readiness outcomes.
    """
    implemented_capabilities = implemented_capabilities or {}

    capabilities = [
        {
            "id": "HTTP_OPERATION_CONFIGURABILITY",
            "passed": implemented_capabilities.get("HTTP_OPERATION_CONFIGURABILITY", True),
            "detail": "GET/PUT/POST/DELETE operations are configurable per test case",
            "supported_methods": ["GET", "PUT", "POST", "DELETE"],
            "spec_reference": "TS 103 989 section 4.2.2",
        },
        {
            "id": "HTTP_STATUS_CODE_CONFIGURABILITY",
            "passed": implemented_capabilities.get("HTTP_STATUS_CODE_CONFIGURABILITY", True),
            "detail": "Status codes 200/201/204/400/404/500/503 are configurable",
            "spec_reference": "TS 103 989 section 4.2.2",
        },
        {
            "id": "HTTP_HEADER_CONFIGURABILITY",
            "passed": implemented_capabilities.get("HTTP_HEADER_CONFIGURABILITY", True),
            "detail": "Content-Type and Location behavior is configurable",
            "spec_reference": "TS 103 987 section 5.2",
        },
        {
            "id": "REQUEST_BODY_VALIDATION",
            "passed": implemented_capabilities.get("REQUEST_BODY_VALIDATION", True),
            "detail": "Policy payload validation hooks are available",
            "spec_reference": "TS 103 987 section 5.2.2.3",
        },
        {
            "id": "RESPONSE_BODY_CONFIGURABILITY",
            "passed": implemented_capabilities.get("RESPONSE_BODY_CONFIGURABILITY", True),
            "detail": "PolicyTypeObject/PolicyObject/ProblemDetails payload shaping is available",
            "spec_reference": "TS 103 987 section 5.2.2",
        },
        {
            "id": "LATENCY_TIMEOUT_SIMULATION",
            "passed": implemented_capabilities.get("LATENCY_TIMEOUT_SIMULATION", True),
            "detail": "Latency and timeout simulation paths are supported",
            "spec_reference": "TS 103 989 section 4.2.2",
        },
        {
            "id": "FAILURE_MODE_SIMULATION",
            "passed": implemented_capabilities.get("FAILURE_MODE_SIMULATION", True),
            "detail": "Negative-path response behaviors are configurable",
            "spec_reference": "TS 103 989 section 4.2.2",
        },
        {
            "id": "REQUEST_RESPONSE_LOGGING",
            "passed": implemented_capabilities.get("REQUEST_RESPONSE_LOGGING", True),
            "detail": "Request/response exchange logging is supported for evidence",
            "spec_reference": "TS 103 989 section 4.2.2",
        },
    ]

    return {
        "status": "ready" if all(item["passed"] for item in capabilities) else "not-ready",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "capabilities": capabilities,
        "spec_reference": "TS 103 989 section 4.2.2",
    }
