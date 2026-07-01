import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran


def test_ei_job_operations_conformance_category_is_exposed_via_api() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    tests_response = client.get("/api/oran/conformance/tests", params={"category_id": "ei-job-operations"})
    run_response = client.post("/api/oran/conformance/run", json={"category_id": "ei-job-operations"})

    assert tests_response.status_code == 200
    assert run_response.status_code == 200
    assert tests_response.json()[0]["category_id"] == "ei-job-operations"
    assert all("5.3" in item["spec_reference"] for item in tests_response.json())
    assert run_response.json()["category_id"] == "ei-job-operations"
    assert run_response.json()["summary"] == {
        "total": 8,
        "passed": 8,
        "failed": 0,
        "verdict": "PASS",
    }


def test_ei_type_and_job_lifecycle_endpoints() -> None:
    oran.a1_ei_service._ei_jobs.clear()
    oran.a1_ei_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    list_types_response = client.get("/api/oran/a1/eitypes")
    get_type_response = client.get("/api/oran/a1/eitypes/default")
    create_response = client.put(
        "/api/oran/a1/eitypes/default/eijobs/ei-job-42",
        json={"ei_payload": {"workload": "baseline"}},
        params={"notificationDestination": "https://example.com/ei-callback"},
    )
    list_jobs_response = client.get("/api/oran/a1/eitypes/default/eijobs")
    get_job_response = client.get("/api/oran/a1/eitypes/default/eijobs/ei-job-42")
    status_response = client.get("/api/oran/a1/eitypes/default/eijobs/ei-job-42/status")
    update_response = client.put(
        "/api/oran/a1/eitypes/default/eijobs/ei-job-42",
        json={"ei_payload": {"workload": "updated"}},
    )
    delete_response = client.delete("/api/oran/a1/eitypes/default/eijobs/ei-job-42")
    status_after_delete_response = client.get("/api/oran/a1/eitypes/default/eijobs/ei-job-42/status")

    assert list_types_response.status_code == 200
    assert "default" in list_types_response.json()
    assert get_type_response.status_code == 200
    assert get_type_response.json()["ei_type_id"] == "default"
    assert create_response.status_code == 201
    assert "Location" in create_response.headers
    assert list_jobs_response.status_code == 200
    assert "ei-job-42" in list_jobs_response.json()
    assert get_job_response.status_code == 200
    assert get_job_response.json()["ei_job"]["ei_payload"]["workload"] == "baseline"
    assert status_response.status_code == 200
    assert status_response.json()["delivery_status"] == "ACCEPTED"
    assert update_response.status_code == 200
    assert delete_response.status_code == 204
    assert status_after_delete_response.status_code == 404


def test_ei_endpoints_return_problem_details_for_unknown_resources() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    unknown_type_response = client.get("/api/oran/a1/eitypes/unknown-type")
    unknown_job_response = client.get("/api/oran/a1/eitypes/default/eijobs/unknown-job")

    assert unknown_type_response.status_code == 404
    assert unknown_type_response.json()["detail"]["title"] == "EI Type Not Found"
    assert unknown_job_response.status_code == 404
    assert unknown_job_response.json()["detail"]["title"] == "EI Job Not Found"


def test_ei_job_create_rejects_invalid_payload_shape() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    response = client.put(
        "/api/oran/a1/eitypes/default/eijobs/invalid-job",
        json={"wrong": "shape"},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["title"] == "Invalid EI Job Request"
    assert detail["status"] == 400