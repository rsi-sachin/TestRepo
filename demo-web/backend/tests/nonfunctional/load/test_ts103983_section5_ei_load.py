from app.services.a1_enrichment_service import A1EnrichmentInformationService


def test_section5_load_ei_handles_moderate_job_throughput() -> None:
    service = A1EnrichmentInformationService()

    total = 50
    for i in range(total):
        service.create_or_replace_ei_job(
            "default",
            f"load-ei-{i}",
            {
                "eiTypeId": "default",
                "jobDefinition": {"workload": i},
                "jobResultUri": f"https://example.com/result/{i}",
            },
        )

    assert len(service.list_ei_job_ids("default")) == total
