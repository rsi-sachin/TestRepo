from app.services.a1_enrichment_service import A1EnrichmentInformationService


def test_section5_stress_ei_repeated_replace_stays_queryable() -> None:
    service = A1EnrichmentInformationService()

    for i in range(160):
        service.create_or_replace_ei_job(
            "default",
            "stress-ei",
            {
                "eiTypeId": "default",
                "jobDefinition": {"iteration": i},
                "jobResultUri": "https://example.com/stress-result",
            },
        )

    job = service.get_ei_job("default", "stress-ei")
    assert "iteration" in job["ei_job"]["jobDefinition"]
