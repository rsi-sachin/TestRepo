"""
Conformance tests: TS 103 983 section 5.2.3.3 EI lifecycle resilience.
"""

import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

import app.services.a1_enrichment_service as ei_module
from app.api import oran


@pytest.fixture
def client() -> TestClient:
    oran.a1_ei_service._ei_jobs.clear()
    oran.a1_ei_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)



def test_section_5_2_3_3_1_reconcile_after_restart_marks_missing_jobs_disabled(client: TestClient) -> None:
    create = client.put(
        "/api/oran/a1/eitypes/default/eijobs/ei-restart-1",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"workload": "baseline"},
            "jobResultUri": "https://example.com/ei-result-1",
        },
    )
    assert create.status_code == 201

    report = oran.a1_ei_service.reconcile_ei_jobs_after_restart(recovered_job_ids=[])

    assert report["default:ei-restart-1"] == "DISABLED"
    status = client.get("/api/oran/a1/eitypes/default/eijobs/ei-restart-1/status")
    assert status.status_code == 200
    assert status.json()["eiJobStatus"] == "DISABLED"



def test_section_5_2_3_3_2_delivery_failure_disables_ei_job(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    create = client.put(
        "/api/oran/a1/eitypes/default/eijobs/ei-delivery-1",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"workload": "delivery"},
            "jobResultUri": "https://example.com/ei-result-delivery",
        },
    )
    assert create.status_code == 201

    class _FakeResponse:
        status_code = 503

    class _FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            return _FakeResponse()

    monkeypatch.setattr(ei_module.httpx, "AsyncClient", _FakeAsyncClient)

    asyncio.run(
        oran.a1_ei_service.deliver_ei_job_result(
            "https://example.com/ei-result-delivery",
            {"jobResult": {"kpi": "failed"}},
        )
    )

    status = client.get("/api/oran/a1/eitypes/default/eijobs/ei-delivery-1/status")
    assert status.status_code == 200
    assert status.json()["eiJobStatus"] == "DISABLED"


def test_section_5_2_5_1_push_delivery_failure_is_non_buffering_no_retry(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create = client.put(
        "/api/oran/a1/eitypes/default/eijobs/ei-delivery-2",
        json={
            "eiTypeId": "default",
            "jobDefinition": {"workload": "delivery-retry-check"},
            "jobResultUri": "https://example.com/ei-result-delivery-2",
        },
    )
    assert create.status_code == 201

    captured = {"count": 0}

    class _FakeResponse:
        status_code = 502

    class _FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            captured["count"] += 1
            return _FakeResponse()

    monkeypatch.setattr(ei_module.httpx, "AsyncClient", _FakeAsyncClient)

    asyncio.run(
        oran.a1_ei_service.deliver_ei_job_result(
            "https://example.com/ei-result-delivery-2",
            {"jobResult": {"kpi": "attempt-1"}},
        )
    )
    asyncio.run(
        oran.a1_ei_service.deliver_ei_job_result(
            "https://example.com/ei-result-delivery-2",
            {"jobResult": {"kpi": "attempt-2"}},
        )
    )

    # Exactly one callback attempt per invocation, with no hidden retry loop.
    assert captured["count"] == 2

    status = client.get("/api/oran/a1/eitypes/default/eijobs/ei-delivery-2/status")
    assert status.status_code == 200
    assert status.json()["eiJobStatus"] == "DISABLED"
