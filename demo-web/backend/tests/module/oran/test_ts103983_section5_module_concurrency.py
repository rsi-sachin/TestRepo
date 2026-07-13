from concurrent.futures import ThreadPoolExecutor

from app.models.a1_policy_models import PolicyObject
from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry


def test_section5_module_policy_and_ei_lifecycle_calls_are_consistent_under_concurrency() -> None:
    registry = A1ServiceRegistry()
    policy_service = A1PolicyService(registry)
    ei_service = A1EnrichmentInformationService(registry)

    def _policy_task(i: int) -> None:
        policy_service.create_or_replace_policy(
            policy_type_id="default",
            policy_id=f"m-pol-{i}",
            policy=PolicyObject(
                scope={"scope_type": "cell", "scope_value": str(i)},
                policy_statements=[{"id": f"stmt-{i}", "action": "allow"}],
            ),
        )

    def _ei_task(i: int) -> None:
        ei_service.create_or_replace_ei_job(
            ei_type_id="default",
            ei_job_id=f"m-ei-{i}",
            ei_job={
                "eiTypeId": "default",
                "jobDefinition": {"batch": i},
                "jobResultUri": f"https://example.com/result/{i}",
            },
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        for i in range(20):
            executor.submit(_policy_task, i)
            executor.submit(_ei_task, i)

    assert len(policy_service.list_policy_ids("default")) == 20
    assert len(ei_service.list_ei_job_ids("default")) == 20
