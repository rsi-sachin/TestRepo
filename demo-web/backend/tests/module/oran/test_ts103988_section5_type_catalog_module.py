from app.services.a1_enrichment_service import A1EnrichmentInformationService
from app.services.a1_policy_service import A1PolicyService
from app.services.a1_service_registry import A1ServiceRegistry


def test_section5_module_type_catalog_contract_is_exposed_for_a1p_and_a1ei() -> None:
    registry = A1ServiceRegistry()
    policy_service = A1PolicyService(registry)
    ei_service = A1EnrichmentInformationService(registry)

    policy_summary = policy_service.build_service_summary()
    ei_summary = ei_service.build_service_summary()

    assert policy_summary["type_definition_catalog"]["source_reference"] == "TS 103 988 section 5.2"
    assert ei_summary["type_definition_catalog"]["source_reference"] == "TS 103 988 section 5.2"
    assert policy_summary["type_definition_catalog"]["types"]["QoSTarget"] == "4.0.1"
    assert ei_summary["type_definition_catalog"]["types"]["UEGeoandVel"] == "3.0.1"
