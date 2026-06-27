import json
from datetime import datetime, UTC

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.test_cases import _to_test_case_response
from app.database import Base
from app.models.db_models import TestCase as DbTestCase
from app.models.oran import EnrichedTestCase, HttpMethod, ScenarioType, SpecType, TestClause as OranTestClause, TestSemantics as OranTestSemantics
from app.services.test_case_service import TestCaseService


def _build_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return session_factory()


def test_create_from_enriched_persists_scenario_metadata():
    service = TestCaseService()
    session = _build_session()
    enriched = EnrichedTestCase(
        base_clause=OranTestClause(
            clause_number='5.3.1',
            title='Conformance create policy test',
            description='Validate conformance create policy flow.',
            spec_type=SpecType.TS_103_989,
            scenario_type=ScenarioType.CONFORMANCE,
        ),
        semantics=OranTestSemantics(
            scenario_type=ScenarioType.CONFORMANCE,
            simulator_required=True,
            configurable_request_parts=['uri', 'headers', 'body'],
            http_method=HttpMethod.PUT,
            endpoint='/policies/{policy_id}',
            expected_status=201,
        ),
        scenario_type=ScenarioType.CONFORMANCE,
        complexity='BASIC',
        enrichment_sources={'base': 'TS_103_989 Section 5.3.1'},
    )

    saved = service.create_from_enriched(session, enriched, 'catalog-1')

    assert saved.scenario_type == ScenarioType.CONFORMANCE
    assert saved.simulator_required is True
    assert json.loads(saved.configurable_request_parts) == ['uri', 'headers', 'body']


def test_list_and_statistics_support_scenario_filters():
    service = TestCaseService()
    session = _build_session()
    records = [
        DbTestCase(
            test_id='oran-a1-5-3-1',
            scenario='Conformance create policy test',
            description='desc',
            source_spec=SpecType.TS_103_989,
            source_section='5.3.1',
            source_page=10,
            scenario_type=ScenarioType.CONFORMANCE,
            simulator_required=True,
            configurable_request_parts='["uri", "headers", "body"]',
            http_method=HttpMethod.PUT,
            endpoint='/policies/{policy_id}',
            expected_status=201,
            complexity='BASIC',
            catalog_id='catalog-1',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        DbTestCase(
            test_id='oran-a1-5-4-1',
            scenario='Interoperability policy exchange test',
            description='desc',
            source_spec=SpecType.TS_103_989,
            source_section='5.4.1',
            source_page=11,
            scenario_type=ScenarioType.INTEROPERABILITY,
            simulator_required=False,
            configurable_request_parts='["uri", "headers", "body"]',
            http_method=HttpMethod.POST,
            endpoint='/policies',
            expected_status=200,
            complexity='BASIC',
            catalog_id='catalog-1',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]
    session.add_all(records)
    session.commit()

    filtered = service.list_all(session, scenario_type=[ScenarioType.CONFORMANCE], simulator_required=True)
    stats = service.get_statistics(session, catalog_id='catalog-1')

    assert len(filtered) == 1
    assert filtered[0].scenario_type == ScenarioType.CONFORMANCE
    assert stats['by_scenario_type']['CONFORMANCE'] == 1
    assert stats['by_scenario_type']['INTEROPERABILITY'] == 1
    assert stats['by_simulator_requirement']['required'] == 1
    assert stats['by_simulator_requirement']['not_required'] == 1


def test_api_response_decodes_configurable_request_parts():
    test_case = DbTestCase(
        id=3,
        test_id='oran-a1-5-3-2',
        scenario='Conformance query test',
        description='desc',
        source_spec=SpecType.TS_103_989,
        source_section='5.3.2',
        source_page=12,
        scenario_type=ScenarioType.CONFORMANCE,
        simulator_required=True,
        configurable_request_parts='["uri", "headers", "body"]',
        http_method=HttpMethod.GET,
        endpoint='/policies/{policy_id}',
        expected_status=200,
        complexity='BASIC',
        catalog_id='catalog-2',
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    response = _to_test_case_response(test_case)

    assert response.scenario_type == 'CONFORMANCE'
    assert response.simulator_required is True
    assert response.configurable_request_parts == ['uri', 'headers', 'body']