import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))
from app.main import app


client = TestClient(app)


def test_conformance_categories_exposes_4_4_interoperability_categories():
    response = client.get("/api/oran/conformance/categories")

    assert response.status_code == 200
    payload = response.json()
    category_ids = {item["category_id"] for item in payload}

    assert "interoperability-a1p" in category_ids
    assert "interoperability-a1ei" in category_ids


def test_conformance_tests_exposes_interoperability_a1p_suite_metadata():
    response = client.get("/api/oran/conformance/tests", params={"category_id": "interoperability-a1p"})

    assert response.status_code == 200
    tests = response.json()

    assert len(tests) == 9
    assert {item["category_id"] for item in tests} == {"interoperability-a1p"}
    assert any("4.4" in item["spec_reference"] for item in tests)


def test_conformance_tests_exposes_interoperability_a1ei_suite_metadata():
    response = client.get("/api/oran/conformance/tests", params={"category_id": "interoperability-a1ei"})

    assert response.status_code == 200
    tests = response.json()

    assert len(tests) == 11
    assert {item["category_id"] for item in tests} == {"interoperability-a1ei"}
    assert any("4.4" in item["spec_reference"] for item in tests)


def test_conformance_run_executes_interoperability_a1p_category():
    response = client.post("/api/oran/conformance/run", json={"category_id": "interoperability-a1p"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["category_id"] == "interoperability-a1p"
    assert payload["summary"]["total"] == 9
    assert payload["summary"]["failed"] == 0


def test_conformance_run_executes_interoperability_a1ei_category():
    response = client.post("/api/oran/conformance/run", json={"category_id": "interoperability-a1ei"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["category_id"] == "interoperability-a1ei"
    assert payload["summary"]["total"] == 11
    assert payload["summary"]["failed"] == 0
