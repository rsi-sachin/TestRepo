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
            "eiTypeId": "default",
            "jobDefinition": {"workload": "baseline"},
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
        json={
            "eiTypeId": "default",
            "jobDefinition": {"workload": "updated"},
            "jobResultUri": "https://example.com/ei-result",
        },
    )
    delete_response = client.delete("/api/oran/a1/eitypes/default/eijobs/ei-job-42")
    status_after_delete_response = client.get("/api/oran/a1/eitypes/default/eijobs/ei-job-42/status")

    assert list_types_response.status_code == 200
    assert "default" in list_types_response.json()
    assert get_type_response.status_code == 200
    assert get_type_response.json()["ei_type_id"] == "default"

    ei_type_status_response = client.get("/api/oran/a1/eitypes/default/status")
    assert ei_type_status_response.status_code == 200
    assert ei_type_status_response.json()["eiTypeId"] == "default"
    assert ei_type_status_response.json()["eiTypeStatus"] == "ENABLED"

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
    assert get_job_response.json()["ei_job"]["jobDefinition"]["workload"] == "baseline"
    assert status_response.status_code == 200
    assert status_response.json()["eiJobStatus"] == "ENABLED"
    assert update_response.status_code == 200
    assert delete_response.status_code == 204
    assert status_after_delete_response.status_code == 404


def test_annex_a_canonical_ei_job_endpoints() -> None:
    oran.a1_ei_service._ei_jobs.clear()
    oran.a1_ei_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    create_response = client.put(
        "/api/oran/a1/eijobs/annex-job-1",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"workload": "annex-a"},
            "jobStatusNotificationUri": "https://example.com/annex-status",
            "jobResultUri": "https://example.com/annex-result",
        },
    )
    get_response = client.get("/api/oran/a1/eijobs/annex-job-1")
    status_response = client.get("/api/oran/a1/eijobs/annex-job-1/status")
    delete_response = client.delete("/api/oran/a1/eijobs/annex-job-1")

    assert create_response.status_code == 201
    assert create_response.json()["ei_job"]["eiTypeId"] == "default"
    assert create_response.json()["ei_job"]["jobDefinition"]["workload"] == "annex-a"
    assert get_response.status_code == 200
    assert get_response.json()["ei_job"]["jobDefinition"]["workload"] == "annex-a"
    assert status_response.status_code == 200
    assert status_response.json()["eiJobStatus"] == "ENABLED"
    assert delete_response.status_code == 204


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

    get_ei_type_status = operations["/api/oran/a1/eitypes/{ei_type_id}/status"]["get"]
    assert "404" in get_ei_type_status["responses"]
    assert "405" in get_ei_type_status["responses"]

    post_ei_type_status_notify = operations["/api/oran/a1/eitypes/{ei_type_id}/status/notify"]["post"]
    assert "400" in post_ei_type_status_notify["responses"]
    assert "404" in post_ei_type_status_notify["responses"]
    assert "405" in post_ei_type_status_notify["responses"]
    type_callbacks = post_ei_type_status_notify.get("callbacks", {})
    assert "eiTypeStatusNotification" in type_callbacks

    error_response = put_ei_job["responses"]["404"]
    assert "application/problem+json" in error_response["content"]

    put_ei_job_annex = operations["/api/oran/a1/eijobs/{ei_job_id}"]["put"]
    callbacks = put_ei_job_annex.get("callbacks", {})
    assert "jobStatusNotification" in callbacks
    assert "jobResult" in callbacks


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
            "eiTypeId": "default",
            "jobDefinition": {"workload": "conflict"},
            "jobResultUri": "https://example.com/conflict-result",
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


def test_notify_ei_type_status_returns_204(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    observed = {}

    async def _fake_notify(destination: str, status_obj: dict):
        observed["destination"] = destination
        observed["status"] = status_obj

    monkeypatch.setattr(oran.a1_ei_service, "notify_ei_type_status", _fake_notify)

    response = client.post(
        "/api/oran/a1/eitypes/default/status/notify",
        params={"notificationDestination": "https://callback.example.com/ei-type-status"},
        json={
            "eiTypeId": "default",
            "eiTypeStatus": "ENABLED",
            "statusReason": "type available",
        },
    )

    assert response.status_code == 204
    assert observed["destination"] == "https://callback.example.com/ei-type-status"
    assert observed["status"]["eiTypeId"] == "default"


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


def test_a1ei_service_summary_exposes_ts103988_type_definition_catalog() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    response = client.get("/api/oran/services/A1-EI")

    assert response.status_code == 200
    catalog = response.json()["summary"]["type_definition_catalog"]
    assert catalog["source_reference"] == "TS 103 988 section 5.2"
    assert catalog["types"]["UEGeoandVel"] == "3.0.1"


def test_ei_job_create_rejects_invalid_eitype_identifier_format() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    response = client.put(
        "/api/oran/a1/eitypes/default/eijobs/invalid-format-job",
        json={
            "eiTypeId": "default bad",
            "jobDefinition": {"workload": "baseline"},
            "jobResultUri": "https://example.com/ei-result",
        },
    )

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    detail = response.json()["detail"]
    assert detail["title"] == "Invalid EI Job Request"
    assert "identifier" in detail["detail"]