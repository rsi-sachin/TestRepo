"""
Phase 3 unit tests — Test Generation Engine

Covers:
  - CatalogGeneratorService.generate_catalog (from enriched cases)
  - CatalogGeneratorService.generate_pytest_script (Jinja2 rendering)
  - CatalogGeneratorService.generate_test_config (YAML rendering)
  - CatalogGeneratorService.save_catalog (JSON persistence)
  - Deduplication / section limit behaviour
"""

import json
import yaml
import pytest
from pathlib import Path

from app.services.catalog_generator_service import CatalogGeneratorService
from app.models.oran import (
    OranTestCatalog, OranTestCase, EnrichedTestCase,
    TestClause, TestSemantics, SpecType, HttpMethod, ScenarioType,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_enriched_case(
    clause_number: str = "5.2.1",
    title: str = "Policy Creation Test",
    method: HttpMethod = HttpMethod.PUT,
    status: int = 201,
    spec_type: SpecType = SpecType.TS_103_989,
) -> EnrichedTestCase:
    clause = TestClause(
        clause_number=clause_number,
        title=title,
        description=f"Test {title}",
        spec_type=spec_type,
        page_number=10,
        raw_text=f"Send {method.value} /policytypes Expected result: HTTP {status}",
    )
    semantics = TestSemantics(
        scenario_type=ScenarioType.CONFORMANCE,
        simulator_required=True,
        configurable_request_parts=["uri", "headers", "body"],
        http_method=method,
        endpoint="/a1-p/policytypes/{policyTypeId}/policies/{policyId}",
        expected_status=status,
        payload_type="PolicyObject",
        assertions=[f"status_code == {status}"],
    )
    return EnrichedTestCase(
        base_clause=clause,
        semantics=semantics,
        scenario_type=ScenarioType.CONFORMANCE,
        complexity="BASIC",
        enrichment_sources={"base": f"{spec_type.value} Section {clause_number}"},
    )


def _make_service(tmp_path: Path) -> CatalogGeneratorService:
    templates_dir = Path(__file__).parent.parent.parent.parent / "templates" / "oran"
    return CatalogGeneratorService(
        output_dir=tmp_path / "oran_catalogs",
        templates_dir=templates_dir,
    )


# ---------------------------------------------------------------------------
# generate_catalog
# ---------------------------------------------------------------------------

class TestGenerateCatalog:
    def test_catalog_has_correct_test_count(self, tmp_path):
        service = _make_service(tmp_path)
        cases = [_make_enriched_case(f"5.{i}.1") for i in range(1, 5)]
        catalog, _ = service.generate_catalog(cases, "Test Catalog")
        assert catalog.total_tests == 4
        assert len(catalog.test_cases) == 4

    def test_catalog_id_is_unique(self, tmp_path):
        service = _make_service(tmp_path)
        cases = [_make_enriched_case("5.1.1")]
        catalog1, _ = service.generate_catalog(cases, "Catalog A")
        catalog2, _ = service.generate_catalog(cases, "Catalog B")
        assert catalog1.catalog_id != catalog2.catalog_id

    def test_catalog_name_is_preserved(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "My Catalog")
        assert catalog.name == "My Catalog"

    def test_section_limit_deduplicates_same_section(self, tmp_path):
        service = _make_service(tmp_path)
        # Two enriched cases with the same section number
        cases = [_make_enriched_case("5.2.1"), _make_enriched_case("5.2.1")]
        catalog, dedup = service.generate_catalog(cases, "Dedup Catalog", apply_section_limit=True)
        assert catalog.total_tests == 1
        assert len(dedup) == 1

    def test_section_limit_disabled_keeps_all(self, tmp_path):
        service = _make_service(tmp_path)
        cases = [_make_enriched_case("5.2.1"), _make_enriched_case("5.2.1")]
        catalog, _ = service.generate_catalog(cases, "No Dedup", apply_section_limit=False)
        assert catalog.total_tests == 2

    def test_test_case_method_is_preserved(self, tmp_path):
        service = _make_service(tmp_path)
        cases = [_make_enriched_case("5.1.1", method=HttpMethod.DELETE, status=204)]
        catalog, _ = service.generate_catalog(cases, "Methods Catalog")
        assert catalog.test_cases[0].method == HttpMethod.DELETE
        assert catalog.test_cases[0].expected_status == 204

    def test_spec_sources_populated(self, tmp_path):
        service = _make_service(tmp_path)
        cases = [_make_enriched_case("5.1.1", spec_type=SpecType.TS_103_989)]
        catalog, _ = service.generate_catalog(cases, "Sources Catalog")
        assert SpecType.TS_103_989.value in catalog.spec_sources


# ---------------------------------------------------------------------------
# save_catalog
# ---------------------------------------------------------------------------

class TestSaveCatalog:
    def test_save_creates_json_file(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "Save Test")
        path = service.save_catalog(catalog)
        assert path.exists()
        assert path.suffix == ".json"

    def test_saved_json_is_valid(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "JSON Test")
        path = service.save_catalog(catalog)
        data = json.loads(path.read_text())
        assert data["catalog_id"] == catalog.catalog_id
        assert "test_cases" in data

    def test_saved_file_name_matches_catalog_id(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "ID Test")
        path = service.save_catalog(catalog)
        assert catalog.catalog_id in path.name


# ---------------------------------------------------------------------------
# generate_pytest_script
# ---------------------------------------------------------------------------

class TestGeneratePytestScript:
    def test_script_file_is_created(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "Script Test")
        script_path = service.generate_pytest_script(catalog)
        assert script_path.exists()
        assert script_path.suffix == ".py"

    def test_script_contains_catalog_name(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "My Script Catalog")
        script_path = service.generate_pytest_script(catalog)
        content = script_path.read_text()
        assert "My Script Catalog" in content

    def test_script_contains_test_class(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "Class Test")
        script_path = service.generate_pytest_script(catalog)
        content = script_path.read_text()
        assert "class Test_" in content

    def test_script_contains_pytest_import(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "Import Test")
        script_path = service.generate_pytest_script(catalog)
        content = script_path.read_text()
        assert "import pytest" in content

    def test_script_uses_correct_http_method(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog(
            [_make_enriched_case(method=HttpMethod.GET, status=200)], "Method Check"
        )
        script_path = service.generate_pytest_script(catalog)
        content = script_path.read_text()
        assert "http_client.get(" in content

    def test_script_file_name_matches_catalog_id(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "ID Match")
        script_path = service.generate_pytest_script(catalog)
        assert catalog.catalog_id in script_path.name


# ---------------------------------------------------------------------------
# generate_test_config
# ---------------------------------------------------------------------------

class TestGenerateTestConfig:
    def test_config_file_is_created(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "Config Test")
        config_path = service.generate_test_config(catalog)
        assert config_path.exists()
        assert config_path.suffix == ".yaml"

    def test_config_is_valid_yaml(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "YAML Test")
        config_path = service.generate_test_config(catalog)
        parsed = yaml.safe_load(config_path.read_text())
        assert isinstance(parsed, dict)

    def test_config_contains_test_environment(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "Env Test")
        config_path = service.generate_test_config(catalog)
        parsed = yaml.safe_load(config_path.read_text())
        assert "test_environment" in parsed
        assert "a1_endpoint" in parsed["test_environment"]

    def test_config_contains_catalog_metadata(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "Meta Test")
        config_path = service.generate_test_config(catalog)
        parsed = yaml.safe_load(config_path.read_text())
        assert parsed["catalog"]["catalog_id"] == catalog.catalog_id
        assert parsed["catalog"]["name"] == "Meta Test"

    def test_config_file_name_matches_catalog_id(self, tmp_path):
        service = _make_service(tmp_path)
        catalog, _ = service.generate_catalog([_make_enriched_case()], "Name Test")
        config_path = service.generate_test_config(catalog)
        assert catalog.catalog_id in config_path.name
        assert "_config" in config_path.name
