"""Conformance support service for TS 103 989 section 4.2.1/4.2.2 checks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

import httpx


class ConformanceService:
    """Builds deterministic readiness and evidence helper payloads."""

    def build_dut_readiness(
        self,
        service_registry,
        policy_service,
        ric_endpoint: str,
        include_phase2_ei: bool = False,
        http_get: Callable[..., object] | None = None,
    ) -> dict:
        """Evaluate DUT readiness checks aligned to TS 103 989 section 4.2.2."""
        getter = http_get or httpx.get
        checks = []

        a1p_supported = service_registry.is_supported("A1-P")
        checks.append(
            {
                "id": "ROLE_CONFIGURATION_A1P",
                "category": "role-configuration",
                "passed": a1p_supported,
                "blocking": True,
                "detail": "Non-RT RIC advertises A1-P consumer support",
            }
        )

        a1ei_supported = service_registry.is_supported("A1-EI")
        checks.append(
            {
                "id": "ROLE_CONFIGURATION_A1EI",
                "category": "role-configuration",
                "passed": a1ei_supported if include_phase2_ei else True,
                "blocking": include_phase2_ei,
                "detail": (
                    "A1-EI consumer support required for Phase 2"
                    if include_phase2_ei
                    else "A1-EI check skipped for Phase 1"
                ),
            }
        )

        policy_type_ids = policy_service.list_policy_type_ids()
        checks.append(
            {
                "id": "POLICY_TYPE_PRECONDITION",
                "category": "policy-type-preconditions",
                "passed": len(policy_type_ids) > 0,
                "blocking": True,
                "detail": f"Found {len(policy_type_ids)} configured policy type(s)",
                "policy_type_ids": policy_type_ids,
            }
        )

        schema_ok = False
        schema_detail = "No policy type available for schema validation"
        if policy_type_ids:
            first_policy_type = policy_service.get_policy_type(policy_type_ids[0])
            schema_ok = isinstance(first_policy_type.policy_schema, dict) and isinstance(
                first_policy_type.policy_status_schema, dict
            )
            schema_detail = "policy_schema and policy_status_schema are present"

        checks.append(
            {
                "id": "RESPONSE_SCHEMA_COMPLIANCE",
                "category": "response-schema-compliance",
                "passed": schema_ok,
                "blocking": True,
                "detail": schema_detail,
            }
        )

        endpoint = ric_endpoint.rstrip("/") + "/api/oran/a1/policytypes"
        endpoint_ok = False
        content_type_ok = False
        endpoint_detail = "unreachable"

        try:
            response = getter(endpoint, timeout=2.0)
            status_code = getattr(response, "status_code", 0)
            headers = getattr(response, "headers", {}) or {}
            endpoint_ok = status_code == 200
            content_type = str(headers.get("content-type", "")).lower()
            content_type_ok = "application/json" in content_type
            endpoint_detail = f"HTTP {status_code}"
        except Exception as exc:  # pragma: no cover - network/runtime dependent
            endpoint_detail = str(exc)

        checks.append(
            {
                "id": "ENDPOINT_ACCESSIBILITY",
                "category": "endpoint-accessibility",
                "passed": endpoint_ok,
                "blocking": True,
                "detail": endpoint_detail,
                "endpoint": endpoint,
            }
        )

        checks.append(
            {
                "id": "HTTP_COMPLIANCE_CONTENT_TYPE",
                "category": "http-compliance",
                "passed": content_type_ok,
                "blocking": True,
                "detail": "Response exposes application/json Content-Type",
            }
        )

        checks.append(
            {
                "id": "FIREWALL_NETWORK_POLICY",
                "category": "firewall-network-policies",
                "passed": endpoint_ok,
                "blocking": True,
                "detail": "Endpoint reachable from conformance harness network path",
            }
        )

        checks.append(
            {
                "id": "PERFORMANCE_BASELINE",
                "category": "performance-baseline",
                "passed": endpoint_ok,
                "blocking": False,
                "detail": "Baseline must be captured during conformance run execution",
            }
        )

        blocking_checks = [item for item in checks if item.get("blocking")]
        ready = all(item["passed"] for item in blocking_checks)

        return {
            "status": "ready" if ready else "not-ready",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
            "policy_type_ids": policy_type_ids,
            "phase": "phase-2" if include_phase2_ei else "phase-1",
            "spec_reference": "TS 103 989 section 4.2.2",
        }
