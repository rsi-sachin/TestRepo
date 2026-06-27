from pathlib import Path

from app.models.oran import (
    EnrichedTestCase,
    HttpMethod,
    ScenarioType,
    SpecType,
    TestClause as OranTestClause,
    TestSemantics as OranTestSemantics,
)
from app.parsers.test_clause_extractor import TestClauseExtractor as OranTestClauseExtractor
from app.services.catalog_generator_service import CatalogGeneratorService
from app.services.spec_parser_service import SpecParserService


def test_clause_extractor_classifies_conformance_and_interoperability_sections():
    extractor = OranTestClauseExtractor()
    text = """
5.3.1 Conformance policy create test
Test Purpose: Verify conformance behavior for policy creation.
Test Procedure: Simulator sends PUT request to /policies/{policy_id}
Expected Result: HTTP 201 response

5.4.1 Interoperability policy exchange test
Test Purpose: Verify interoperability between Non-RT RIC and Near-RT RIC.
Test Procedure: Real devices exchange POST /policies notifications.
Expected Result: HTTP 200 response
"""

    clauses = extractor.extract_clauses(text, SpecType.TS_103_989)

    assert [clause.scenario_type for clause in clauses] == [
        ScenarioType.CONFORMANCE,
        ScenarioType.INTEROPERABILITY,
    ]


def test_enrich_test_case_propagates_conformance_classification_and_request_parts():
    parser = SpecParserService(spec_dir=Path('.'))
    clause = OranTestClause(
        clause_number='5.3.1',
        title='Conformance policy create test',
        description='Verify conformance behavior for policy creation.',
        methodology='Simulator sends PUT request to /policies/{policy_id}',
        expected_result='HTTP 201 response',
        scenario_type=ScenarioType.CONFORMANCE,
        spec_type=SpecType.TS_103_989,
        raw_text='Simulator sends PUT request to /policies/{policy_id} expecting 201',
    )

    enriched = parser._enrich_test_case(clause, {SpecType.TS_103_989: [clause]})

    assert enriched.scenario_type == ScenarioType.CONFORMANCE
    assert enriched.semantics.scenario_type == ScenarioType.CONFORMANCE
    assert enriched.semantics.simulator_required is True
    assert enriched.semantics.configurable_request_parts == ['uri', 'headers', 'body']
    assert enriched.semantics.http_method == HttpMethod.PUT


def test_catalog_generator_preserves_scenario_classification():
    generator = CatalogGeneratorService(output_dir=Path('test-output'))
    base_clause = OranTestClause(
        clause_number='5.4.1',
        title='Interoperability policy exchange test',
        description='Verify interoperability between Non-RT RIC and Near-RT RIC.',
        methodology='Real devices exchange POST /policies notifications.',
        expected_result='HTTP 200 response',
        scenario_type=ScenarioType.INTEROPERABILITY,
        spec_type=SpecType.TS_103_989,
        raw_text='POST /policies 200',
    )
    semantics = OranTestSemantics(
        scenario_type=ScenarioType.INTEROPERABILITY,
        simulator_required=False,
        configurable_request_parts=['uri', 'headers', 'body'],
        http_method=HttpMethod.POST,
        endpoint='/policies',
        expected_status=200,
    )
    enriched = EnrichedTestCase(
        base_clause=base_clause,
        semantics=semantics,
        scenario_type=ScenarioType.INTEROPERABILITY,
        complexity='BASIC',
        enrichment_sources={'base': 'TS_103_989 Section 5.4.1'},
    )

    catalog, _ = generator.generate_catalog([enriched], catalog_name='interop-tests', apply_section_limit=False)

    assert catalog.test_cases[0].scenario_type == ScenarioType.INTEROPERABILITY
    assert catalog.test_cases[0].simulator_required is False


def test_conformance_cases_cover_configurable_http_methods_for_simulator_capability():
    generator = CatalogGeneratorService(output_dir=Path('test-output'))
    methods = [HttpMethod.GET, HttpMethod.PUT, HttpMethod.POST, HttpMethod.DELETE]
    enriched_cases = []

    for index, method in enumerate(methods, start=1):
        clause = OranTestClause(
            clause_number=f'5.3.{index}',
            title=f'Conformance {method.value} test',
            description=f'Validate simulator-backed {method.value} behavior.',
            methodology=f'Simulator sends {method.value} request to /resource/{index}',
            expected_result='HTTP 200 response',
            scenario_type=ScenarioType.CONFORMANCE,
            spec_type=SpecType.TS_103_989,
            raw_text=f'{method.value} /resource/{index} 200',
        )
        semantics = OranTestSemantics(
            scenario_type=ScenarioType.CONFORMANCE,
            simulator_required=True,
            configurable_request_parts=['uri', 'headers', 'body'],
            http_method=method,
            endpoint=f'/resource/{index}',
            expected_status=200,
        )
        enriched_cases.append(
            EnrichedTestCase(
                base_clause=clause,
                semantics=semantics,
                scenario_type=ScenarioType.CONFORMANCE,
                complexity='BASIC',
                enrichment_sources={'base': f'TS_103_989 Section 5.3.{index}'},
            )
        )

    catalog, _ = generator.generate_catalog(enriched_cases, catalog_name='conformance-http-methods', apply_section_limit=False)

    assert [test_case.method for test_case in catalog.test_cases] == methods
    for test_case in catalog.test_cases:
        assert test_case.scenario_type == ScenarioType.CONFORMANCE
        assert test_case.simulator_required is True
        assert test_case.configurable_request_parts == ['uri', 'headers', 'body']