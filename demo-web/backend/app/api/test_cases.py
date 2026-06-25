"""
Test Case Management API Endpoints (Phase 3)
CRUD operations for ORAN test cases in database
"""

import json

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.models.oran import SpecType, HttpMethod, ScenarioType
from app.models.db_models import TestCase as DBTestCase, TestCaseEnrichment
from app.services.test_case_service import test_case_service
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== PYDANTIC MODELS FOR API ====================

class TestCaseResponse(BaseModel):
    """Response model for test case"""
    id: int
    test_id: str
    scenario: str
    description: Optional[str]
    source_spec: str
    source_section: str
    source_page: Optional[int]
    scenario_type: Optional[str]
    simulator_required: bool
    configurable_request_parts: List[str]
    http_method: str
    endpoint: str
    expected_status: int
    complexity: str
    catalog_id: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class TestCaseUpdate(BaseModel):
    """Model for updating test case fields"""
    scenario: Optional[str] = None
    description: Optional[str] = None
    scenario_type: Optional[ScenarioType] = None
    simulator_required: Optional[bool] = None
    configurable_request_parts: Optional[List[str]] = None
    http_method: Optional[HttpMethod] = None
    endpoint: Optional[str] = None
    expected_status: Optional[int] = None
    complexity: Optional[str] = None


class EnrichmentResponse(BaseModel):
    """Response model for enrichment"""
    id: int
    enrichment_type: str
    source_spec: str
    source_section: Optional[str]
    source_page: Optional[int]
    value: Optional[str]
    
    class Config:
        from_attributes = True


class TestCaseListResponse(BaseModel):
    """Response for list endpoint with pagination"""
    total: int
    page: int
    page_size: int
    test_cases: List[TestCaseResponse]


def _parse_configurable_request_parts(value: Optional[str]) -> List[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except json.JSONDecodeError:
        logger.warning("Failed to decode configurable_request_parts: %s", value)
    return []


def _to_test_case_response(test_case: DBTestCase) -> TestCaseResponse:
    return TestCaseResponse(
        id=test_case.id,
        test_id=test_case.test_id,
        scenario=test_case.scenario,
        description=test_case.description,
        source_spec=test_case.source_spec.value if test_case.source_spec else "",
        source_section=test_case.source_section,
        source_page=test_case.source_page,
        scenario_type=test_case.scenario_type.value if test_case.scenario_type else None,
        simulator_required=bool(test_case.simulator_required),
        configurable_request_parts=_parse_configurable_request_parts(test_case.configurable_request_parts),
        http_method=test_case.http_method.value if test_case.http_method else "",
        endpoint=test_case.endpoint,
        expected_status=test_case.expected_status,
        complexity=test_case.complexity,
        catalog_id=test_case.catalog_id,
        created_at=test_case.created_at.isoformat(),
        updated_at=test_case.updated_at.isoformat(),
    )


# ==================== ENDPOINTS ====================

@router.get("/test-cases", response_model=TestCaseListResponse)
def list_test_cases(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    source_spec: Optional[List[SpecType]] = Query(None, description="Filter by source spec"),
    source_section: Optional[str] = Query(None, description="Filter by section (prefix match)"),
    scenario_type: Optional[List[ScenarioType]] = Query(None, description="Filter by scenario classification"),
    simulator_required: Optional[bool] = Query(None, description="Filter by simulator requirement"),
    http_method: Optional[List[HttpMethod]] = Query(None, description="Filter by HTTP method"),
    complexity: Optional[List[str]] = Query(None, description="Filter by complexity"),
    catalog_id: Optional[str] = Query(None, description="Filter by catalog ID"),
    db: Session = Depends(get_db)
):
    """
    List test cases with filtering and pagination
    
    Returns paginated list of test cases from database
    """
    skip = (page - 1) * page_size
    
    # Get test cases
    test_cases = test_case_service.list_all(
        db,
        skip=skip,
        limit=page_size,
        source_spec=source_spec,
        source_section=source_section,
        scenario_type=scenario_type,
        simulator_required=simulator_required,
        http_method=http_method,
        complexity=complexity,
        catalog_id=catalog_id
    )
    
    # Get total count
    total = test_case_service.count_all(
        db,
        source_spec=source_spec,
        source_section=source_section,
        scenario_type=scenario_type,
        simulator_required=simulator_required,
        http_method=http_method,
        complexity=complexity,
        catalog_id=catalog_id
    )
    
    return TestCaseListResponse(
        total=total,
        page=page,
        page_size=page_size,
        test_cases=[_to_test_case_response(tc) for tc in test_cases]
    )


@router.get("/test-cases/{test_id}", response_model=TestCaseResponse)
def get_test_case(
    test_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single test case by database ID
    """
    test_case = test_case_service.get_by_id(db, test_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    return _to_test_case_response(test_case)


@router.put("/test-cases/{test_id}", response_model=TestCaseResponse)
def update_test_case(
    test_id: int,
    updates: TestCaseUpdate,
    db: Session = Depends(get_db)
):
    """
    Update test case fields
    
    Only provided fields will be updated
    """
    # Convert to dict, excluding None values
    update_dict = updates.model_dump(exclude_none=True)
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    updated_test = test_case_service.update(db, test_id, update_dict)
    if not updated_test:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    return _to_test_case_response(updated_test)


@router.delete("/test-cases/{test_id}")
def delete_test_case(
    test_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete test case and its enrichments
    """
    success = test_case_service.delete(db, test_id)
    if not success:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    return {"message": "Test case deleted successfully", "test_id": test_id}


@router.get("/test-cases/{test_id}/enrichments", response_model=List[EnrichmentResponse])
def get_test_case_enrichments(
    test_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all enrichment sources for a test case
    
    Used for tooltip display in UI
    """
    # Verify test case exists
    test_case = test_case_service.get_by_id(db, test_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    enrichments = test_case_service.get_enrichments(db, test_id)
    return [EnrichmentResponse.model_validate(e) for e in enrichments]


@router.get("/test-cases/statistics")
def get_test_case_statistics(
    catalog_id: Optional[str] = Query(None, description="Filter by catalog ID"),
    db: Session = Depends(get_db)
):
    """
    Get statistics about test cases
    
    Returns counts by various dimensions
    """
    stats = test_case_service.get_statistics(db, catalog_id)
    return stats
