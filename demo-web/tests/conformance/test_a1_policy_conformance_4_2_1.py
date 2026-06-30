import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))
from app.main import app


client = TestClient(app)


def _run_policy_type_query_suite() -> dict:
    response = client.post("/api/oran/conformance/run", json={"category_id": "policy-type-query"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["category_id"] == "policy-type-query"
    return payload


def test_policy_type_query_operation_suite_metadata():
    response = client.get("/api/oran/conformance/tests", params={"category_id": "policy-type-query"})
    assert response.status_code == 200
    tests = response.json()
    assert len(tests) == 5


def test_policy_type_query_operation_tc_001_list_returns_list():
    payload = _run_policy_type_query_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PTQ-001")
    assert result["status"] == "PASS"


def test_policy_type_query_operation_tc_002_empty_when_none_registered():
    payload = _run_policy_type_query_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PTQ-002")
    assert result["status"] == "PASS"


def test_policy_type_query_operation_tc_003_unknown_type_not_found_behavior():
    payload = _run_policy_type_query_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PTQ-003")
    assert result["status"] == "PASS"


def test_policy_type_query_operation_tc_004_schema_presence():
    payload = _run_policy_type_query_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PTQ-004")
    assert result["status"] == "PASS"


def test_policy_type_query_operation_tc_005_role_ownership_context():
    payload = _run_policy_type_query_suite()
    result = next(item for item in payload["results"] if item["test_id"] == "TC-A1-PTQ-005")
    assert result["status"] == "PASS"
