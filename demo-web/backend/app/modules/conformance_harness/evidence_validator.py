"""Execution evidence validation skeleton for conformance harness."""


def validate_execution_evidence(payload: dict) -> dict:
    """Validate required evidence keys and deterministic verdict fields."""
    required = {
        "test_case_id",
        "test_section_reference",
        "verdict",
        "verdict_reason",
        "checks_performed",
        "evidence_artifacts",
    }
    missing = sorted(required - set(payload.keys()))
    if missing:
        return {
            "valid": False,
            "missing_keys": missing,
            "status": "failed",
            "errors": [f"Missing required key: {name}" for name in missing],
        }

    verdict = str(payload.get("verdict", "")).upper()
    if verdict not in {"PASS", "FAIL", "INCONCLUSIVE"}:
        return {
            "valid": False,
            "missing_keys": [],
            "status": "failed",
            "errors": ["verdict must be one of PASS, FAIL, INCONCLUSIVE"],
        }

    checks = payload.get("checks_performed", [])
    if not isinstance(checks, list):
        return {
            "valid": False,
            "missing_keys": [],
            "status": "failed",
            "errors": ["checks_performed must be a list"],
        }

    artifacts = payload.get("evidence_artifacts", [])
    if not isinstance(artifacts, list):
        return {
            "valid": False,
            "missing_keys": [],
            "status": "failed",
            "errors": ["evidence_artifacts must be a list"],
        }

    artifact_errors = []
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            artifact_errors.append(f"Artifact at index {index} must be an object")
            continue
        for key in ("artifact_type", "file_path"):
            if key not in artifact:
                artifact_errors.append(f"Artifact at index {index} missing key: {key}")

    if artifact_errors:
        return {
            "valid": False,
            "missing_keys": [],
            "status": "failed",
            "errors": artifact_errors,
        }

    return {
        "valid": True,
        "missing_keys": [],
        "status": "passed",
        "errors": [],
    }
