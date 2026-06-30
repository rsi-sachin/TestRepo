import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))
from app.main import app


client = TestClient(app)


def _run_policy_operations_suite() -> dict:
    response = client.post("/api/oran/conformance/run", json={"category_id": "policy-operations"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["category_id"] == "policy-operations"
    return payload


def test_policy_operations_suite_metadata():
    response = client.get("/api/oran/conformance/tests", params={"category_id": "policy-operations"})
    assert response.status_code == 200
    tests = response.json()
    assert len(tests) == 8


def test_policy_operations_tc_001_create_policy_returns_created():
    payload = _run_policy_operations_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PO-001")
    assert result["status"] == "PASS"


def test_policy_operations_tc_002_update_policy_returns_replaced():
    payload = _run_policy_operations_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PO-002")
    assert result["status"] == "PASS"


def test_policy_operations_tc_003_query_policy_returns_policy():
    payload = _run_policy_operations_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PO-003")
    assert result["status"] == "PASS"


def test_policy_operations_tc_004_query_ids_contains_created_policy():
    payload = _run_policy_operations_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PO-004")
    assert result["status"] == "PASS"


def test_policy_operations_tc_005_query_policy_status_returns_status():
    payload = _run_policy_operations_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PO-005")
    assert result["status"] == "PASS"


def test_policy_operations_tc_006_delete_policy_succeeds():
    payload = _run_policy_operations_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PO-006")
    assert result["status"] == "PASS"


def test_policy_operations_tc_007_query_deleted_policy_not_found():
    payload = _run_policy_operations_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PO-007")
    assert result["status"] == "PASS"


def test_policy_operations_tc_008_delete_unknown_policy_not_found():
    payload = _run_policy_operations_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PO-008")
    assert result["status"] == "PASS"
