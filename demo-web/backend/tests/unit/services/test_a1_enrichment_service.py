import asyncio
import logging
import sys
from pathlib import Path

import httpx
import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

import app.services.a1_enrichment_service as ei_module
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_service_registry import A1ServiceRegistry


def test_ei_service_summary_exposes_supported_types_and_resources() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    summary = helper.build_service_summary()

    assert "/ei-jobs" in summary["primary_resources"]
    assert "default" in summary["supported_ei_types"]


def test_ei_job_lifecycle_create_query_update_delete() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    created_job, was_created = helper.create_or_replace_ei_job(
        "default",
        "job-001",
        {"ei_payload": {"name": "initial"}},
    )
    updated_job, was_created_on_update = helper.create_or_replace_ei_job(
        "default",
        "job-001",
        {"ei_payload": {"name": "updated"}},
    )

    assert was_created is True
    assert was_created_on_update is False
    assert created_job["ei_job_id"] == "job-001"
    assert updated_job["ei_job"]["ei_payload"]["name"] == "updated"
    assert helper.list_ei_job_ids("default") == ["job-001"]
    assert helper.get_ei_job("default", "job-001")["ei_job"]["ei_payload"]["name"] == "updated"
    assert helper.get_ei_job_status("default", "job-001")["delivery_status"] == "ACCEPTED"

    helper.delete_ei_job("default", "job-001")

    assert helper.list_ei_job_ids("default") == []


def test_unknown_ei_type_raises_key_error() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    try:
        helper.get_ei_type("unknown")
        assert False, "Expected KeyError"
    except KeyError:
        assert True


def test_ei_notification_destination_is_cleared_when_omitted_on_replace() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())
    key = ("default", "job-notify-clear")

    helper.create_or_replace_ei_job(
        "default",
        "job-notify-clear",
        {"ei_payload": {"name": "with-notify"}},
        notification_destination="https://consumer.example.com/ei-status",
    )
    assert helper._notification_destinations[key] == "https://consumer.example.com/ei-status"

    helper.create_or_replace_ei_job(
        "default",
        "job-notify-clear",
        {"ei_payload": {"name": "without-notify"}},
    )

    assert key not in helper._notification_destinations


def test_notify_ei_job_status_logs_warning_for_non_success_status(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())
    post_call_count = {"value": 0}

    class _FakeResponse:
        status_code = 503

    class _FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            post_call_count["value"] += 1
            return _FakeResponse()

    monkeypatch.setattr(ei_module.httpx, "AsyncClient", _FakeAsyncClient)

    with caplog.at_level(logging.WARNING, logger=ei_module.logger.name):
        asyncio.run(
            helper.notify_ei_job_status(
                "https://consumer.example.com/ei-status",
                {"ei_job_id": "job-001", "delivery_status": "FAILED"},
            )
        )

    assert "unexpected status 503" in caplog.text
    assert post_call_count["value"] == 1


def test_notify_ei_job_status_propagates_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())
    post_call_count = {"value": 0}

    class _FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            post_call_count["value"] += 1
            raise httpx.TimeoutException("EI callback timed out")

    monkeypatch.setattr(ei_module.httpx, "AsyncClient", _FakeAsyncClient)

    with pytest.raises(httpx.TimeoutException):
        asyncio.run(
            helper.notify_ei_job_status(
                "https://consumer.example.com/ei-status",
                {"ei_job_id": "job-001", "delivery_status": "PENDING"},
            )
        )

    assert post_call_count["value"] == 1


def test_create_ei_job_rejects_payload_without_required_ei_payload_field() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="missing required fields"):
        helper.create_or_replace_ei_job("default", "bad-job", {"wrong": "shape"})


def test_notify_ei_job_status_rejects_payload_missing_required_fields() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="must include ei_job_id and delivery_status"):
        asyncio.run(helper.notify_ei_job_status("https://consumer.example.com/ei-status", {"ei_job_id": "x"}))