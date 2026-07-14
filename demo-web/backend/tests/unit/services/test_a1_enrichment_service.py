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


def test_create_uegeoandvel_job_accepts_section9_compound_definition() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    created_job, was_created = helper.create_or_replace_ei_job(
        "UEGeoandVel",
        "job-typed-001",
        {
            "eiTypeId": "ORAN_UEGeoandVel_3.0.1",
            "jobDefinition": {
                "scope": {"ueId": "ue-001"},
                "ueGeoandVelEIDescription": {
                    "gadShape": "POINT",
                    "granularityPeriod": 100,
                    "reportingPeriod": 1000,
                    "reportingAmount": 5,
                },
            },
            "jobResultUri": "https://consumer.example.com/typed-result",
        },
    )

    assert was_created is True
    assert created_job["ei_job"]["eiTypeId"] == "ORAN_UEGeoandVel_3.0.1"
    assert created_job["ei_job"]["jobDefinition"]["scope"]["ueId"] == "ue-001"
    assert created_job["ei_job"]["jobDefinition"]["ueGeoandVelEIDescription"]["gadShape"] == "POINT"
    assert created_job["ei_job"]["jobDefinition"]["ueGeoandVelEIDescription"]["reportingAmount"] == 5


def test_create_uegeoandvel_job_rejects_invalid_gad_shape() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="gadShape"):
        helper.create_or_replace_ei_job(
            "UEGeoandVel",
            "job-typed-invalid-shape",
            {
                "eiTypeId": "ORAN_UEGeoandVel_3.0.1",
                "jobDefinition": {
                    "scope": {"ueId": "ue-002"},
                    "ueGeoandVelEIDescription": {
                        "gadShape": "NOT_A_SHAPE",
                        "granularityPeriod": 100,
                        "reportingPeriod": 1000,
                        "reportingAmount": 5,
                    },
                },
                "jobResultUri": "https://consumer.example.com/typed-result",
            },
        )


def test_create_uegeoandvel_job_rejects_non_positive_reporting_amount() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="reportingAmount"):
        helper.create_or_replace_ei_job(
            "UEGeoandVel",
            "job-typed-invalid-amount",
            {
                "eiTypeId": "ORAN_UEGeoandVel_3.0.1",
                "jobDefinition": {
                    "scope": {"ueId": "ue-003"},
                    "ueGeoandVelEIDescription": {
                        "gadShape": "POINT",
                        "granularityPeriod": 100,
                        "reportingPeriod": 1000,
                        "reportingAmount": 0,
                    },
                },
                "jobResultUri": "https://consumer.example.com/typed-result",
            },
        )


def test_create_uegeoandvel_job_rejects_missing_scope_wrapper() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="scope"):
        helper.create_or_replace_ei_job(
            "UEGeoandVel",
            "job-typed-missing-scope",
            {
                "eiTypeId": "ORAN_UEGeoandVel_3.0.1",
                "jobDefinition": {
                    "ueGeoandVelEIDescription": {
                        "gadShape": "POINT",
                        "granularityPeriod": 100,
                        "reportingPeriod": 1000,
                        "reportingAmount": 5,
                    },
                },
                "jobResultUri": "https://consumer.example.com/typed-result",
            },
        )


def test_validate_uegeoandvel_constraints_uses_section9_property_names() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    validated = helper.validate_ei_job_constraints(
        "UEGeoandVel",
        {
            "jobConstraints": {
                "supportedGadShapes": ["POINT"],
                "supportedVelocityTypes": ["H_VELOCITY"],
            }
        },
    )

    assert validated == {
        "supportedGadShapes": ["POINT"],
        "supportedVelocityTypes": ["H_VELOCITY"],
    }


def test_validate_uegeoandvel_result_requires_array_payload() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="non-empty array"):
        helper.validate_ei_job_result(
            "UEGeoandVel",
            {
                "timeStamp": "2026-07-13T12:00:00Z",
                "ueId": "ue-004",
                "gadShape": "POINT",
                "geoLocation": {"lon": 10.0, "lat": 20.0},
            },
        )


def test_validate_uegeoandvel_result_accepts_section9_array_payload() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    validated = helper.validate_ei_job_result(
        "UEGeoandVel",
        [
            {
                "timeStamp": "2026-07-13T12:00:00Z",
                "ueId": "ue-005",
                "gadShape": "POINT",
                "geoLocation": {"lon": 10.0, "lat": 20.0},
                "velocityDesc": "H_VELOCITY",
                "velocity": {"speed": 30},
            }
        ],
    )

    assert validated[0]["ueId"] == "ue-005"


def test_validate_uegeoandvel_result_accepts_polygon_payload() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    validated = helper.validate_ei_job_result(
        "UEGeoandVel",
        [
            {
                "timeStamp": "2026-07-13T12:05:00Z",
                "ueId": "ue-006",
                "gadShape": "POLYGON",
                "geoLocation": [
                    {"lon": 10.0, "lat": 20.0},
                    {"lon": 11.0, "lat": 21.0},
                    {"lon": 12.0, "lat": 22.0},
                ],
            }
        ],
    )

    assert validated[0]["gadShape"] == "POLYGON"
    assert len(validated[0]["geoLocation"]) == 3


def test_validate_uegeoandvel_result_rejects_short_polygon_payload() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="polygon with 3 to 15 points"):
        helper.validate_ei_job_result(
            "UEGeoandVel",
            [
                {
                    "timeStamp": "2026-07-13T12:06:00Z",
                    "ueId": "ue-007",
                    "gadShape": "POLYGON",
                    "geoLocation": [
                        {"lon": 10.0, "lat": 20.0},
                        {"lon": 11.0, "lat": 21.0},
                    ],
                }
            ],
        )


def test_validate_uegeoandvel_result_rejects_circle_payload_without_uncertainty() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="geoLocation is missing required fields: uncertainty"):
        helper.validate_ei_job_result(
            "UEGeoandVel",
            [
                {
                    "timeStamp": "2026-07-13T12:07:00Z",
                    "ueId": "ue-008",
                    "gadShape": "POINT_UNCERTAINTY_CIRCLE",
                    "geoLocation": {
                        "point": {"lon": 10.0, "lat": 20.0}
                    },
                }
            ],
        )


def test_notify_ei_job_status_rejects_invalid_status_value() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="invalid eiJobStatus"):
        asyncio.run(
            helper.notify_ei_job_status(
                "https://consumer.example.com/ei-status",
                {"eiJobStatus": "BROKEN"},
            )
        )


def test_section9_eitype_alias_and_canonical_major_version_compatibility() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    created_job, was_created = helper.create_or_replace_ei_job(
        "ORAN_UEGeoandVel_3.0.1",
        "job-major-version-ok",
        {
            "eiTypeId": "UEGeoandVel",
            "jobDefinition": {
                "scope": {"ueId": "ue-major-ok"},
                "ueGeoandVelEIDescription": {
                    "gadShape": "POINT",
                    "granularityPeriod": 100,
                    "reportingPeriod": 200,
                    "reportingAmount": 3,
                },
            },
            "jobResultUri": "https://consumer.example.com/result-major-ok",
        },
    )

    assert was_created is True
    assert created_job["ei_job"]["eiTypeId"] == "ORAN_UEGeoandVel_3.0.1"


def test_section9_eitype_rejects_non_compatible_major_version() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="does not match requested EI type"):
        helper.create_or_replace_ei_job(
            "UEGeoandVel",
            "job-major-version-bad",
            {
                "eiTypeId": "ORAN_UEGeoandVel_4.0.1",
                "jobDefinition": {
                    "scope": {"ueId": "ue-major-bad"},
                    "ueGeoandVelEIDescription": {
                        "gadShape": "POINT",
                        "granularityPeriod": 100,
                        "reportingPeriod": 200,
                        "reportingAmount": 3,
                    },
                },
                "jobResultUri": "https://consumer.example.com/result-major-bad",
            },
        )


def test_section9_eitype_schema_metadata_exposes_exact_id_and_common_linkage() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    ei_type = helper.get_ei_type("UEGeoandVel")
    schema = ei_type["eiJobDefinitionSchema"]

    assert schema["$id"].endswith("ORAN_UEGeoandVel_3.0.1")
    assert schema["x-commonSchemaRef"] == "TS_103_988_common_1.0.0"


@pytest.mark.parametrize("unsupported_scope_member", ["groupId", "sliceId", "qosId", "cellId"])
def test_section9_compound_job_rejects_unsupported_scope_members(unsupported_scope_member: str) -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match=unsupported_scope_member):
        helper.create_or_replace_ei_job(
            "UEGeoandVel",
            f"job-bad-scope-{unsupported_scope_member}",
            {
                "eiTypeId": "ORAN_UEGeoandVel_3.0.1",
                "jobDefinition": {
                    "scope": {
                        "ueId": "ue-scope",
                        unsupported_scope_member: "not-supported",
                    },
                    "ueGeoandVelEIDescription": {
                        "gadShape": "POINT",
                        "granularityPeriod": 100,
                        "reportingPeriod": 1000,
                        "reportingAmount": 5,
                    },
                },
                "jobResultUri": "https://consumer.example.com/result-scope",
            },
        )


def test_section9_compound_job_rejects_description_extra_fields() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="unexpectedField"):
        helper.create_or_replace_ei_job(
            "UEGeoandVel",
            "job-extra-field",
            {
                "eiTypeId": "ORAN_UEGeoandVel_3.0.1",
                "jobDefinition": {
                    "scope": {"ueId": "ue-extra"},
                    "ueGeoandVelEIDescription": {
                        "gadShape": "POINT",
                        "granularityPeriod": 100,
                        "reportingPeriod": 1000,
                        "reportingAmount": 5,
                        "unexpectedField": "x",
                    },
                },
                "jobResultUri": "https://consumer.example.com/result-extra",
            },
        )


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("granularityPeriod", 60001),
        ("reportingPeriod", 60001),
        ("reportingAmount", 3600001),
    ],
)
def test_section9_compound_job_rejects_upper_bound_violations(field_name: str, field_value: int) -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())
    description = {
        "gadShape": "POINT",
        "granularityPeriod": 100,
        "reportingPeriod": 1000,
        "reportingAmount": 5,
    }
    description[field_name] = field_value

    with pytest.raises(ValueError, match=field_name):
        helper.create_or_replace_ei_job(
            "UEGeoandVel",
            f"job-upper-bound-{field_name}",
            {
                "eiTypeId": "ORAN_UEGeoandVel_3.0.1",
                "jobDefinition": {
                    "scope": {"ueId": "ue-upper-bound"},
                    "ueGeoandVelEIDescription": description,
                },
                "jobResultUri": "https://consumer.example.com/result-upper-bound",
            },
        )


def test_section9_constraints_reject_empty_supported_velocity_types_when_provided() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="supportedVelocityTypes"):
        helper.validate_ei_job_constraints(
            "UEGeoandVel",
            {
                "jobConstraints": {
                    "supportedGadShapes": ["POINT"],
                    "supportedVelocityTypes": [],
                }
            },
        )


def test_section9_constraints_reject_alias_conflict_between_legacy_and_canonical_fields() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="supportedVelocityDescs"):
        helper.validate_ei_job_constraints(
            "UEGeoandVel",
            {
                "jobConstraints": {
                    "supportedGadShapes": ["POINT"],
                    "supportedVelocityTypes": ["H_VELOCITY"],
                    "supportedVelocityDescs": ["HV_VELOCITY"],
                }
            },
        )


def test_section9_constraints_reject_invalid_velocity_enum() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    with pytest.raises(ValueError, match="supportedVelocityTypes"):
        helper.validate_ei_job_constraints(
            "UEGeoandVel",
            {
                "jobConstraints": {
                    "supportedGadShapes": ["POINT"],
                    "supportedVelocityTypes": ["NOT_VALID"],
                }
            },
        )


def test_section9_result_accepts_point_altitude_uncertainty_payload() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    validated = helper.validate_ei_job_result(
        "UEGeoandVel",
        [
            {
                "timeStamp": "2026-07-14T03:00:00Z",
                "ueId": "ue-alt-unc",
                "gadShape": "POINT_ALTITUDE_UNCERTAINTY",
                "geoLocation": {
                    "point": {"lon": 10.0, "lat": 20.0},
                    "altitude": 150,
                    "uncertainty": 5,
                },
            }
        ],
    )

    assert validated[0]["gadShape"] == "POINT_ALTITUDE_UNCERTAINTY"


def test_section9_result_accepts_ellipsoid_arc_payload() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    validated = helper.validate_ei_job_result(
        "UEGeoandVel",
        [
            {
                "timeStamp": "2026-07-14T03:01:00Z",
                "ueId": "ue-ellipsoid",
                "gadShape": "ELLIPSOID_ARC",
                "geoLocation": {
                    "center": {"lon": 10.0, "lat": 20.0},
                    "innerRadius": 50,
                    "uncertaintyRadius": 10,
                    "offsetAngle": 30,
                    "includedAngle": 45,
                },
                "velocityDesc": "HV_VELOCITY_UNCERTAINTY",
                "velocity": {"hSpeed": 20, "bearing": 40, "vSpeed": 3, "uncertainty": 2},
            }
        ],
    )

    assert validated[0]["gadShape"] == "ELLIPSOID_ARC"
    assert validated[0]["velocityDesc"] == "HV_VELOCITY_UNCERTAINTY"


def test_section9_result_accepts_point_uncertainty_ellipse_payload() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    validated = helper.validate_ei_job_result(
        "UEGeoandVel",
        [
            {
                "timeStamp": "2026-07-14T03:02:00Z",
                "ueId": "ue-ellipse",
                "gadShape": "POINT_UNCERTAINTY_ELLIPSE",
                "geoLocation": {
                    "point": {"lon": 10.0, "lat": 20.0},
                    "uncertaintyEllipse": {
                        "semiMajor": 100,
                        "semiMinor": 60,
                        "orientation": 15,
                    },
                    "confidence": 0.95,
                },
            }
        ],
    )

    assert validated[0]["gadShape"] == "POINT_UNCERTAINTY_ELLIPSE"


def test_section9_result_accepts_point_altitude_payload() -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    validated = helper.validate_ei_job_result(
        "UEGeoandVel",
        [
            {
                "timeStamp": "2026-07-14T03:03:00Z",
                "ueId": "ue-alt",
                "gadShape": "POINT_ALTITUDE",
                "geoLocation": {
                    "point": {"lon": 10.0, "lat": 20.0},
                    "altitude": 120,
                },
            }
        ],
    )

    assert validated[0]["gadShape"] == "POINT_ALTITUDE"


@pytest.mark.parametrize(
    "velocity_desc",
    [
        "H_VELOCITY",
        "HV_VELOCITY",
        "H_VELOCITY_UNCERTAINTY",
        "HV_VELOCITY_UNCERTAINTY",
    ],
)
def test_section9_result_accepts_all_velocity_descriptor_variants(velocity_desc: str) -> None:
    helper = A1EnrichmentInformationService(A1ServiceRegistry())

    validated = helper.validate_ei_job_result(
        "UEGeoandVel",
        [
            {
                "timeStamp": "2026-07-14T03:04:00Z",
                "ueId": "ue-velocity",
                "gadShape": "POINT",
                "geoLocation": {"lon": 10.0, "lat": 20.0},
                "velocityDesc": velocity_desc,
                "velocity": {"speed": 35, "bearing": 70, "verticalSpeed": 2, "uncertainty": 1},
            }
        ],
    )

    assert validated[0]["velocityDesc"] == velocity_desc