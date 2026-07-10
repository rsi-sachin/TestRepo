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
        {
            "eiTypeId": "default",
            "jobDefinition": {"name": "initial"},
            "jobStatusNotificationUri": "https://consumer.example.com/status",
            "jobResultUri": "https://consumer.example.com/result",
        },
    )
    updated_job, was_created_on_update = helper.create_or_replace_ei_job(
        "default",
        "job-001",
        {
            "eiTypeId": "default",
            "jobDefinition": {"name": "updated"},
            "jobResultUri": "https://consumer.example.com/result",
        },
    )

    assert was_created is True
    assert was_created_on_update is False
    assert created_job["ei_job_id"] == "job-001"
    assert created_job["ei_job"]["jobStatusNotificationUri"] == "https://consumer.example.com/status"
    assert created_job["ei_job"]["jobResultUri"] == "https://consumer.example.com/result"
    assert updated_job["ei_job"]["jobDefinition"]["name"] == "updated"
    assert helper.list_ei_job_ids("default") == ["job-001"]
    assert helper.list_ei_job_ids() == ["job-001"]
    assert helper.get_ei_job("default", "job-001")["ei_job"]["jobDefinition"]["name"] == "updated"
    assert helper.get_ei_job_status("default", "job-001")["eiJobStatus"] == "ENABLED"

    helper.delete_ei_job("default", "job-001")

    assert helper.list_ei_job_ids("default") == []


def test_ei_job_ids_can_be_listed_without_type_filter() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())
    helper._ei_types["secondary"] = {
        "ei_type_id": "secondary",
        "description": "Secondary enrichment job type",
        "ei_schema": {"type": "object", "required": ["eiTypeId", "jobDefinition", "jobResultUri"]},
        "ei_status_schema": {"type": "object", "required": ["eiJobStatus"]},
        "ei_result_schema": {"type": "object", "required": ["jobResult"]},
        "supports_ei_job_creation": True,
    }

    helper.create_or_replace_ei_job(
        "default",
        "job-a",
        {"eiTypeId": "default", "jobDefinition": {"name": "a"}, "jobResultUri": "https://c.example/a"},
    )
    helper.create_or_replace_ei_job(
        "secondary",
        "job-b",
        {"eiTypeId": "secondary", "jobDefinition": {"name": "b"}, "jobResultUri": "https://c.example/b"},
    )

    assert helper.list_ei_job_ids() == ["job-a", "job-b"]
    assert helper.list_ei_job_ids("default") == ["job-a"]


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
        {
            "eiTypeId": "default",
            "jobDefinition": {"name": "with-notify"},
            "jobResultUri": "https://consumer.example.com/ei-result",
        },
        notification_destination="https://consumer.example.com/ei-status",
    )
    assert helper._notification_destinations[key] == "https://consumer.example.com/ei-status"

    helper.create_or_replace_ei_job(
        "default",
        "job-notify-clear",
        {
            "eiTypeId": "default",
            "jobDefinition": {"name": "without-notify"},
            "jobResultUri": "https://consumer.example.com/ei-result",
        },
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
                {"eiJobStatus": "DISABLED"},
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
                {"eiJobStatus": "ENABLED"},
            )
        )

    assert post_call_count["value"] == 1


def test_create_ei_job_rejects_payload_without_required_annex_a_fields() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="missing required fields"):
        helper.create_or_replace_ei_job("default", "bad-job", {"wrong": "shape"})


def test_notify_ei_job_status_rejects_payload_missing_required_fields() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="must include eiJobStatus"):
        asyncio.run(helper.notify_ei_job_status("https://consumer.example.com/ei-status", {"status": "x"}))


def test_deliver_ei_job_result_logs_warning_for_non_success_status(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())
    post_call_count = {"value": 0}

    class _FakeResponse:
        status_code = 502

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
            helper.deliver_ei_job_result(
                "https://consumer.example.com/ei-result",
                {"jobResult": {"quality": "good"}},
            )
        )

    assert "unexpected status 502" in caplog.text
    assert post_call_count["value"] == 1


def test_deliver_ei_job_result_propagates_timeout(
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
            raise httpx.TimeoutException("EI result callback timed out")

    monkeypatch.setattr(ei_module.httpx, "AsyncClient", _FakeAsyncClient)

    with pytest.raises(httpx.TimeoutException):
        asyncio.run(
            helper.deliver_ei_job_result(
                "https://consumer.example.com/ei-result",
                {"jobResult": {"quality": "pending"}},
            )
        )

    assert post_call_count["value"] == 1


def test_deliver_ei_job_result_rejects_payload_missing_required_fields() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="must include jobResult"):
        asyncio.run(helper.deliver_ei_job_result("https://consumer.example.com/ei-result", {"wrong": "x"}))


def test_notify_ei_job_status_uses_json_content_type_and_disables_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())
    helper.create_or_replace_ei_job(
        "default",
        "job-status-contract",
        {
            "eiTypeId": "default",
            "jobDefinition": {"name": "status-contract"},
            "jobStatusNotificationUri": "https://consumer.example.com/status-contract",
            "jobResultUri": "https://consumer.example.com/result-contract",
        },
    )

    captured = {"count": 0, "headers": None}

    class _FakeResponse:
        status_code = 500

    class _FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            captured["count"] += 1
            captured["headers"] = kwargs.get("headers", {})
            return _FakeResponse()

    monkeypatch.setattr(ei_module.httpx, "AsyncClient", _FakeAsyncClient)

    asyncio.run(
        helper.notify_ei_job_status(
            "https://consumer.example.com/status-contract",
            {"eiJobStatus": "ENABLED"},
        )
    )

    assert captured["count"] == 1
    assert captured["headers"] == {"Content-Type": "application/json"}
    assert helper.get_ei_job_status("default", "job-status-contract")["eiJobStatus"] == "DISABLED"


def test_deliver_ei_job_result_repeated_failure_is_non_buffering_and_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())
    helper.create_or_replace_ei_job(
        "default",
        "job-result-contract",
        {
            "eiTypeId": "default",
            "jobDefinition": {"name": "result-contract"},
            "jobResultUri": "https://consumer.example.com/result-contract",
        },
    )

    captured = {"count": 0, "headers": []}

    class _FakeResponse:
        status_code = 503

    class _FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            captured["count"] += 1
            captured["headers"].append(kwargs.get("headers", {}))
            return _FakeResponse()

    monkeypatch.setattr(ei_module.httpx, "AsyncClient", _FakeAsyncClient)

    asyncio.run(
        helper.deliver_ei_job_result(
            "https://consumer.example.com/result-contract",
            {"jobResult": {"value": "first"}},
        )
    )
    asyncio.run(
        helper.deliver_ei_job_result(
            "https://consumer.example.com/result-contract",
            {"jobResult": {"value": "second"}},
        )
    )

    assert captured["count"] == 2
    assert captured["headers"] == [
        {"Content-Type": "application/json"},
        {"Content-Type": "application/json"},
    ]
    assert helper.get_ei_job_status("default", "job-result-contract")["eiJobStatus"] == "DISABLED"


def test_ei_service_summary_exposes_ts103988_type_definition_catalog() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    summary = helper.build_service_summary()

    assert summary["type_definition_catalog"]["source_reference"] == "TS 103 988 section 5.2"
    assert summary["type_definition_catalog"]["types"]["UEGeoandVel"] == "3.0.1"


def test_create_ei_job_rejects_invalid_eitype_identifier_format() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())
    helper._ei_types["bad id"] = {
        "ei_type_id": "bad id",
        "description": "Invalid ID for negative-path validation",
        "ei_schema": {"type": "object", "required": ["eiTypeId", "jobDefinition", "jobResultUri"]},
        "ei_status_schema": {"type": "object", "required": ["eiJobStatus"]},
        "ei_result_schema": {"type": "object", "required": ["jobResult"]},
        "supports_ei_job_creation": True,
    }

    with pytest.raises(ValueError, match="identifier"):
        helper.create_or_replace_ei_job(
            "bad id",
            "job-invalid-type-id",
            {
                "eiTypeId": "bad id",
                "jobDefinition": {"name": "bad-id"},
                "jobResultUri": "https://consumer.example.com/result",
            },
        )