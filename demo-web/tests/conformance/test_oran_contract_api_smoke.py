import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))
from app.main import app


client = TestClient(app)


def test_o1_health_endpoint_returns_stub_contract():
    response = client.get("/api/oran/o1/health")
    assert response.status_code == 200
    assert response.json()["module"] == "o1_interface"


def test_e2_health_endpoint_returns_stub_contract():
    response = client.get("/api/oran/e2/health")
    assert response.status_code == 200
    assert response.json()["module"] == "e2_interface"


def test_conformance_dut_readiness_endpoint_returns_stub_payload():
    response = client.get("/api/oran/conformance/dut-readiness")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ready", "not-ready"}
    assert "checks" in payload


def test_conformance_evidence_validation_fails_for_missing_keys():
    response = client.post("/api/oran/conformance/evidence/validate", json={"test_case_id": "x"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert payload["status"] == "failed"


def test_conformance_categories_exposes_policy_type_query_category():
    response = client.get("/api/oran/conformance/categories")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    assert payload[0]["category_id"] == "policy-type-query"


def test_conformance_categories_exposes_policy_operations_category():
    response = client.get("/api/oran/conformance/categories")
    assert response.status_code == 200
    payload = response.json()
    category_ids = {item["category_id"] for item in payload}
    assert "policy-operations" in category_ids


def test_conformance_run_executes_policy_type_query_category():
    response = client.post("/api/oran/conformance/run", json={"category_id": "policy-type-query"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["category_id"] == "policy-type-query"
    assert payload["summary"]["total"] == 5


def test_conformance_run_executes_policy_operations_category():
    response = client.post("/api/oran/conformance/run", json={"category_id": "policy-operations"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["category_id"] == "policy-operations"
    assert payload["summary"]["total"] == 8


def test_o1_validate_requires_schema_fields():
    response = client.post("/api/oran/o1/validate", json={"intent": "missing-required-fields"})
    assert response.status_code == 422


def test_e2_validate_requires_schema_fields():
    response = client.post("/api/oran/e2/validate", json={"intent": "missing-required-fields"})
    assert response.status_code == 422


def test_feature_plan_status_board_json_endpoint():
    response = client.get("/api/oran/feature-plan/status-board")
    assert response.status_code == 200
    payload = response.json()
    assert "modules" in payload
    assert "summary" in payload
    assert "next_best_item" in payload


def test_feature_plan_status_board_html_endpoint():
    response = client.get("/oran/status-board")
    assert response.status_code == 200
    assert "ORAN Feature Plan Status Board" in response.text
