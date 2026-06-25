"""
Test Case Service - Database CRUD operations for ORAN test cases
"""

import json
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.models.db_models import TestCase, TestCaseEnrichment, EnrichmentType
from app.models.oran import SpecType, HttpMethod, EnrichedTestCase, OranTestCase, ScenarioType

logger = logging.getLogger(__name__)


class TestCaseService:
    """Service for managing test cases in database"""
    
    def create_from_enriched(
        self, 
        db: Session, 
        enriched_case: EnrichedTestCase,
        catalog_id: str
    ) -> TestCase:
        """
        Create test case in database from EnrichedTestCase
        
        Args:
            db: Database session
            enriched_case: Enriched test case from parsing
            catalog_id: ID of catalog this test belongs to
            
        Returns:
            Created TestCase database record
        """
        base = enriched_case.base_clause
        sem = enriched_case.semantics
        
        # Generate test ID
        test_id = f"oran-a1-{base.clause_number.replace('.', '-')}"
        
        # Create test case
        db_test = TestCase(
            test_id=test_id,
            scenario=base.title,
            description=base.description or base.title,
            source_spec=base.spec_type,
            source_section=base.clause_number,
            source_page=base.page_number,
            scenario_type=enriched_case.scenario_type or sem.scenario_type,
            simulator_required=sem.simulator_required,
            configurable_request_parts=json.dumps(sem.configurable_request_parts),
            http_method=sem.http_method or HttpMethod.GET,
            endpoint=sem.endpoint or "/unknown",
            expected_status=sem.expected_status or 200,
            complexity=enriched_case.complexity,
            catalog_id=catalog_id
        )
        
        db.add(db_test)
        db.flush()  # Get the ID without committing
        
        # Create enrichments
        for enrich_type, source_info in enriched_case.enrichment_sources.items():
            # Parse source_info like "TS_103_989 Section 4"
            parts = source_info.split()
            source_spec = SpecType(parts[0]) if len(parts) > 0 else base.spec_type
            source_section = parts[2] if len(parts) > 2 else None
            
            enrichment = TestCaseEnrichment(
                test_case_id=db_test.id,
                enrichment_type=EnrichmentType(enrich_type) if enrich_type in ['base', 'endpoint', 'status_code', 'payload', 'validation'] else EnrichmentType.BASE,
                source_spec=source_spec,
                source_section=source_section,
                value=source_info
            )
            db.add(enrichment)
        
        return db_test
    
    def get_by_id(self, db: Session, test_id: int) -> Optional[TestCase]:
        """Get test case by database ID"""
        return db.query(TestCase).filter(TestCase.id == test_id).first()
    
    def get_by_test_id(self, db: Session, test_id: str) -> Optional[TestCase]:
        """Get test case by test_id string (e.g., 'oran-a1-4')"""
        return db.query(TestCase).filter(TestCase.test_id == test_id).first()
    
    def list_all(
        self, 
        db: Session,
        skip: int = 0,
        limit: int = 100,
        source_spec: Optional[List[SpecType]] = None,
        source_section: Optional[str] = None,
        scenario_type: Optional[List[ScenarioType]] = None,
        simulator_required: Optional[bool] = None,
        http_method: Optional[List[HttpMethod]] = None,
        complexity: Optional[List[str]] = None,
        catalog_id: Optional[str] = None
    ) -> List[TestCase]:
        """
        List test cases with optional filtering and pagination
        
        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum records to return
            source_spec: Filter by source specification(s)
            source_section: Filter by section (partial match)
            scenario_type: Filter by scenario classification(s)
            simulator_required: Filter by simulator requirement
            http_method: Filter by HTTP method(s)
            complexity: Filter by complexity level(s)
            catalog_id: Filter by catalog ID
            
        Returns:
            List of TestCase records
        """
        query = db.query(TestCase)
        
        # Apply filters
        if source_spec:
            query = query.filter(TestCase.source_spec.in_(source_spec))
        
        if source_section:
            query = query.filter(TestCase.source_section.like(f"{source_section}%"))

        if scenario_type:
            query = query.filter(TestCase.scenario_type.in_(scenario_type))

        if simulator_required is not None:
            query = query.filter(TestCase.simulator_required == simulator_required)
        
        if http_method:
            query = query.filter(TestCase.http_method.in_(http_method))
        
        if complexity:
            query = query.filter(TestCase.complexity.in_(complexity))
        
        if catalog_id:
            query = query.filter(TestCase.catalog_id == catalog_id)
        
        # Apply pagination and return
        return query.offset(skip).limit(limit).all()
    
    def count_all(
        self,
        db: Session,
        source_spec: Optional[List[SpecType]] = None,
        source_section: Optional[str] = None,
        scenario_type: Optional[List[ScenarioType]] = None,
        simulator_required: Optional[bool] = None,
        http_method: Optional[List[HttpMethod]] = None,
        complexity: Optional[List[str]] = None,
        catalog_id: Optional[str] = None
    ) -> int:
        """Count test cases with same filters as list_all"""
        query = db.query(TestCase)
        
        if source_spec:
            query = query.filter(TestCase.source_spec.in_(source_spec))
        if source_section:
            query = query.filter(TestCase.source_section.like(f"{source_section}%"))
        if scenario_type:
            query = query.filter(TestCase.scenario_type.in_(scenario_type))
        if simulator_required is not None:
            query = query.filter(TestCase.simulator_required == simulator_required)
        if http_method:
            query = query.filter(TestCase.http_method.in_(http_method))
        if complexity:
            query = query.filter(TestCase.complexity.in_(complexity))
        if catalog_id:
            query = query.filter(TestCase.catalog_id == catalog_id)
        
        return query.count()
    
    def update(
        self,
        db: Session,
        test_id: int,
        updates: Dict
    ) -> Optional[TestCase]:
        """
        Update test case fields
        
        Args:
            db: Database session
            test_id: Database ID of test case
            updates: Dictionary of fields to update
            
        Returns:
            Updated TestCase or None if not found
        """
        db_test = self.get_by_id(db, test_id)
        if not db_test:
            return None
        
        # Update allowed fields
        for key, value in updates.items():
            if hasattr(db_test, key):
                if key == "configurable_request_parts" and isinstance(value, list):
                    value = json.dumps(value)
                setattr(db_test, key, value)
        
        db.commit()
        db.refresh(db_test)
        return db_test
    
    def delete(self, db: Session, test_id: int) -> bool:
        """
        Delete test case and its enrichments
        
        Args:
            db: Database session
            test_id: Database ID of test case
            
        Returns:
            True if deleted, False if not found
        """
        db_test = self.get_by_id(db, test_id)
        if not db_test:
            return False
        
        db.delete(db_test)
        db.commit()
        return True
    
    def get_enrichments(self, db: Session, test_id: int) -> List[TestCaseEnrichment]:
        """Get all enrichments for a test case"""
        return db.query(TestCaseEnrichment).filter(
            TestCaseEnrichment.test_case_id == test_id
        ).all()
    
    def get_statistics(self, db: Session, catalog_id: Optional[str] = None) -> Dict:
        """
        Get statistics about test cases
        
        Returns:
            Dictionary with counts by various dimensions
        """
        query = db.query(TestCase)
        if catalog_id:
            query = query.filter(TestCase.catalog_id == catalog_id)
        
        total = query.count()
        
        # Count by source spec
        by_spec = {}
        for spec in SpecType:
            count = query.filter(TestCase.source_spec == spec).count()
            if count > 0:
                by_spec[spec.value] = count
        
        # Count by method
        by_method = {}
        for method in HttpMethod:
            count = query.filter(TestCase.http_method == method).count()
            if count > 0:
                by_method[method.value] = count
        
        # Count by complexity
        by_complexity = {}
        for complexity in ["BASIC", "INTERMEDIATE", "ADVANCED"]:
            count = query.filter(TestCase.complexity == complexity).count()
            if count > 0:
                by_complexity[complexity] = count

        by_scenario_type = {}
        for scenario in ScenarioType:
            count = query.filter(TestCase.scenario_type == scenario).count()
            if count > 0:
                by_scenario_type[scenario.value] = count

        simulator_breakdown = {
            "required": query.filter(TestCase.simulator_required == True).count(),
            "not_required": query.filter(TestCase.simulator_required == False).count(),
        }
        
        return {
            "total": total,
            "by_source_spec": by_spec,
            "by_scenario_type": by_scenario_type,
            "by_simulator_requirement": simulator_breakdown,
            "by_http_method": by_method,
            "by_complexity": by_complexity
        }


# Global instance
test_case_service = TestCaseService()
