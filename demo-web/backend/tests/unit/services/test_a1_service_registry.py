from app.models.oran import SpecType
from app.services.a1_service_registry import A1ServiceRegistry


def test_get_service_definition_accepts_normalized_strings() -> None:
    registry = A1ServiceRegistry()

    definition = registry.get_service_definition("a1_p")

    assert definition.service_type.value == "A1-P"
    assert definition.consumer_role.label == "A1-P Consumer"


def test_validate_specs_for_service_filters_unsupported() -> None:
    registry = A1ServiceRegistry()

    selected = [SpecType.TS_103_989]
    validated = registry.validate_specs_for_service("A1-EI", selected)

    assert validated == [SpecType.TS_103_989]


def test_default_catalog_name_by_service() -> None:
    registry = A1ServiceRegistry()

    assert registry.get_default_catalog_name("A1-P") == "A1 Policy Management Catalog"
    assert registry.get_default_catalog_name("A1-EI") == "A1 Enrichment Information Catalog"


def test_is_supported_returns_false_for_unknown_service() -> None:
    registry = A1ServiceRegistry()

    assert registry.is_supported("A1-UNKNOWN") is False
