import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran
from app.services.a1_errors import A1ConflictError


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
        json={
            "ei_payload": {"workload": "baseline"},
            "jobStatusNotificationUri": "https://example.com/ei-status",
            "jobResultUri": "https://example.com/ei-result",
        },
        params={"notificationDestination": "https://example.com/ei-callback"},
    )
    list_all_jobs_response = client.get("/api/oran/a1/eijobs")
    list_jobs_by_type_response = client.get("/api/oran/a1/eijobs", params={"eiTypeId": "default"})
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
    assert create_response.json()["ei_job"]["jobStatusNotificationUri"] == "https://example.com/ei-status"
    assert create_response.json()["ei_job"]["jobResultUri"] == "https://example.com/ei-result"
    assert list_all_jobs_response.status_code == 200
    assert list_all_jobs_response.json() == ["ei-job-42"]
    assert list_jobs_by_type_response.status_code == 200
    assert list_jobs_by_type_response.json() == ["ei-job-42"]
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
    assert unknown_type_response.headers["content-type"].startswith("application/problem+json")
    assert unknown_type_response.json()["detail"]["title"] == "EI Type Not Found"
    assert unknown_job_response.status_code == 404
    assert unknown_job_response.headers["content-type"].startswith("application/problem+json")
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
    assert response.headers["content-type"].startswith("application/problem+json")
    detail = response.json()["detail"]
    assert detail["title"] == "Invalid EI Job Request"
    assert detail["status"] == 400


def test_section6_ei_openapi_definitions_include_problem_details_responses() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    operations = schema["paths"]

    put_ei_job = operations["/api/oran/a1/eitypes/{ei_type_id}/eijobs/{ei_job_id}"]["put"]
    assert "400" in put_ei_job["responses"]
    assert "404" in put_ei_job["responses"]
    assert "405" in put_ei_job["responses"]
    assert "409" in put_ei_job["responses"]

    get_ei_job_status = operations["/api/oran/a1/eitypes/{ei_type_id}/eijobs/{ei_job_id}/status"]["get"]
    assert "405" in get_ei_job_status["responses"]

    error_response = put_ei_job["responses"]["404"]
    assert "application/problem+json" in error_response["content"]


def test_ei_job_conflict_is_mapped_to_problem_details(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    def _raise_conflict(*args, **kwargs):
        raise A1ConflictError("simulated ei conflict")

    monkeypatch.setattr(oran.a1_ei_service, "create_or_replace_ei_job", _raise_conflict)

    response = client.put(
        "/api/oran/a1/eitypes/default/eijobs/ei-job-conflict",
        json={
            "ei_payload": {"workload": "conflict"},
        },
    )

    assert response.status_code == 409
    assert response.headers["content-type"].startswith("application/problem+json")
    detail = response.json()["detail"]
    assert detail["title"] == "EI Job Conflict"
    assert detail["status"] == 409


def test_ei_resources_reject_unsupported_methods_with_405() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    eitypes_post = client.request("POST", "/api/oran/a1/eitypes", json={})
    status_delete = client.request("DELETE", "/api/oran/a1/eitypes/default/eijobs/sample/status")

    assert eitypes_post.status_code == 405
    assert status_delete.status_code == 405


def test_eijobs_filter_unknown_eitype_returns_problem_details() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    response = client.get("/api/oran/a1/eijobs", params={"eiTypeId": "unknown-type"})

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    detail = response.json()["detail"]
    assert detail["title"] == "EI Type Not Found"
    assert detail["status"] == 404