"""Execution evidence collection helpers for conformance harness."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _normalize_exchange(index: int, exchange: Dict[str, Any]) -> Dict[str, Any]:
    request = exchange.get("request", {})
    response = exchange.get("response", {})

    request_body = request.get("body")
    response_body = response.get("body")

    return {
        "exchange_id": exchange.get("exchange_id", f"exchange-{index:03d}"),
        "test_case_id": exchange.get("test_case_id", "unknown"),
        "timestamp": exchange.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "request": {
            "method": request.get("method", "GET"),
            "uri": request.get("uri", ""),
            "headers": request.get("headers", {}),
            "body": request_body,
            "body_size_bytes": len(str(request_body).encode("utf-8")) if request_body is not None else 0,
        },
        "response": {
            "status_code": int(response.get("status_code", 0)),
            "headers": response.get("headers", {}),
            "body": response_body,
            "body_size_bytes": len(str(response_body).encode("utf-8")) if response_body is not None else 0,
            "response_time_ms": float(response.get("response_time_ms", 0.0)),
        },
        "validation": {
            "schema_valid": bool(exchange.get("schema_valid", False)),
            "status_code_expected": bool(exchange.get("status_code_expected", False)),
            "headers_complete": bool(exchange.get("headers_complete", False)),
        },
    }


def collect_execution_evidence(
    run_id: str = "manual-run",
    test_case_id: str = "unknown",
    test_section_reference: str = "TS 103 989 section 4.2.1/4.2.2",
    verdict: str = "INCONCLUSIVE",
    verdict_reason: str = "No execution evidence submitted",
    checks_performed: List[Dict[str, Any]] | None = None,
    evidence_artifacts: List[Dict[str, Any]] | None = None,
    exchanges: List[Dict[str, Any]] | None = None,
) -> dict:
    """Build a normalized evidence payload for a conformance run."""
    checks_performed = checks_performed or []
    evidence_artifacts = evidence_artifacts or []
    exchanges = exchanges or []

    normalized_exchanges = [
        _normalize_exchange(index=index + 1, exchange=exchange) for index, exchange in enumerate(exchanges)
    ]

    return {
        "run_id": run_id,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "status": "captured",
        "test_case_id": test_case_id,
        "test_section_reference": test_section_reference,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "checks_performed": checks_performed,
        "evidence_artifacts": evidence_artifacts,
        "exchanges": normalized_exchanges,
        "artifact_count": len(evidence_artifacts),
        "exchange_count": len(normalized_exchanges),
    }
