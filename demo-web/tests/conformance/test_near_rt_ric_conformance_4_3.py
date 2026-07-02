import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))
from app.main import app


client = TestClient(app)


def test_conformance_categories_exposes_near_rt_ric_conformance_category():
    response = client.get("/api/oran/conformance/categories")

    assert response.status_code == 200
    payload = response.json()
    category_ids = {item["category_id"] for item in payload}

    assert "near-rt-ric-conformance" in category_ids

    category = next(item for item in payload if item["category_id"] == "near-rt-ric-conformance")
    assert category["title"] == "Conformance Testing Near-RT RIC"
    assert category["spec_reference"] == "TS 103 989 sections 4.3.1 and 4.3.2"
    assert category["status"] == "implemented"


def test_conformance_tests_exposes_near_rt_ric_setup_suite():
    response = client.get("/api/oran/conformance/tests", params={"category_id": "near-rt-ric-conformance"})

    assert response.status_code == 200
    tests = response.json()

    assert len(tests) >= 3
    assert {item["category_id"] for item in tests} == {"near-rt-ric-conformance"}
    assert {item["spec_reference"] for item in tests} == {"TS 103 989 sections 4.3.1 and 4.3.2"}
    assert any("Near-RT RIC" in item["description"] or "Near-RT RIC" in item["name"] for item in tests)


def test_conformance_run_executes_near_rt_ric_conformance_category():
    response = client.post("/api/oran/conformance/run", json={"category_id": "near-rt-ric-conformance"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["category_id"] == "near-rt-ric-conformance"
    assert payload["summary"]["total"] >= 3
    assert payload["summary"]["failed"] == 0