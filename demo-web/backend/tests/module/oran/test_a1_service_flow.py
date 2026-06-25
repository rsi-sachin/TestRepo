from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry


def test_a1_service_helpers_share_registry_contract() -> None:
    registry = A1ServiceRegistry()
    policy_helper = A1PolicyService(registry)
    ei_helper = A1EnrichmentInformationService(registry)

    policy_context = policy_helper.get_catalog_context()
    ei_context = ei_helper.get_catalog_context()

    assert policy_context["service_type"] == "A1-P"
    assert ei_context["service_type"] == "A1-EI"
    assert policy_context["default_catalog_name"] != ei_context["default_catalog_name"]


def test_a1_policy_summary_has_expected_resource_domains() -> None:
    helper = A1PolicyService(A1ServiceRegistry())

    summary = helper.build_service_summary()

    assert "/policytypes" in summary["primary_resources"]
    assert "TS_103_987" in summary["recommended_specs"]
