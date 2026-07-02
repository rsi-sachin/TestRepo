from app.services.a1_enrichment_service import A1EnrichmentInformationService


def test_section5_memory_ei_create_delete_cycles_leave_no_residual_state() -> None:
    service = A1EnrichmentInformationService()

    for i in range(30):
        service.create_or_replace_ei_job(
            "default",
            f"mem-ei-{i}",
            {
                "eiTypeId": "default",
                "jobDefinition": {"i": i},
                "jobStatusNotificationUri": f"https://example.com/status/{i}",
                "jobResultUri": f"https://example.com/result/{i}",
            },
        )

    assert len(service._ei_jobs) == 30
    assert len(service._notification_destinations) == 30

    for i in range(30):
        service.delete_ei_job("default", f"mem-ei-{i}")

    assert service._ei_jobs == {}
    assert service._notification_destinations == {}
