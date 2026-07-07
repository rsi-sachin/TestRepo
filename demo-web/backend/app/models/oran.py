"""
ORAN models - Pydantic schemas for O-RAN A1 test generation and execution
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SpecType(str, Enum):
    """ETSI specification types"""
    TS_103_989 = "TS_103_989"  # A1 Test Specification
    TS_103_987 = "TS_103_987"  # A1 Application Protocol
    TS_103_988 = "TS_103_988"  # A1 Type Definitions
    TS_103_983 = "TS_103_983"  # A1 General Principles


class HttpMethod(str, Enum):
    """HTTP methods for A1 interface"""
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ScenarioType(str, Enum):
    """High-level scenario classification derived from TS 103 989 methodology."""
    CONFORMANCE = "CONFORMANCE"
    INTEROPERABILITY = "INTEROPERABILITY"


class OranTestCase(BaseModel):
    """Individual O-RAN A1 test case"""
    test_id: str = Field(..., description="Unique test identifier (e.g., A1_TC_001)")
    scenario: str = Field(..., description="Test scenario name")
    description: str = Field(..., description="Test description")
    service_type: Optional[str] = Field(None, description="A1 service type (A1-P or A1-EI)")
    scenario_type: Optional[ScenarioType] = Field(None, description="High-level test classification")
    simulator_required: bool = Field(default=False, description="Whether simulator-backed execution is required")
    configurable_request_parts: List[str] = Field(default_factory=list, description="Request parts the test harness must allow the simulator to configure")
    
    # Request specification
    method: HttpMethod = Field(..., description="HTTP method")
    endpoint: str = Field(..., description="API endpoint pattern (e.g., /policies/{id})")
    payload_type: Optional[str] = Field(None, description="Payload type (PolicyObject, EiJobObject, etc.)")
    payload_schema: Optional[Dict] = Field(None, description="JSON schema for request payload")
    
    # Validation specification
    expected_status: int = Field(..., description="Expected HTTP status code")
    validations: List[str] = Field(default_factory=list, description="Validation assertions")
    
    # Metadata
    complexity: str = Field(default="BASIC", description="Test complexity (BASIC/INTERMEDIATE/ADVANCED)")
    source_clause: Optional[str] = Field(None, description="Source spec clause number")
    
    # Phase 2 additions
    source_spec: Optional[SpecType] = Field(None, description="Source specification type")
    source_section: Optional[str] = Field(None, description="Section number in source spec")
    source_page: Optional[int] = Field(None, description="Page number in source spec")
    enrichment_sources: Dict[str, str] = Field(default_factory=dict, description="Sources of enrichment data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "test_id": "A1_TC_001",
                "scenario": "Create A1 Policy",
                "description": "Test creation of A1 policy via PUT request",
                "scenario_type": "CONFORMANCE",
                "simulator_required": True,
                "configurable_request_parts": ["uri", "headers", "body"],
                "method": "PUT",
                "endpoint": "/policies/{policy_id}",
                "payload_type": "PolicyObject",
                "expected_status": 201,
                "validations": ["status_code == 201", "schema_valid"],
                "complexity": "BASIC",
                "source_clause": "5.3.1",
                "source_spec": "TS_103_989",
                "source_section": "5.3.1",
                "source_page": 45,
                "enrichment_sources": {"base": "TS_103_989 Section 5.3.1"}
            }
        }


class OranTestCatalog(BaseModel):
    """Collection of O-RAN test cases generated from specifications"""
    catalog_id: str = Field(..., description="Unique catalog identifier")
    name: str = Field(..., description="Catalog name")
    description: Optional[str] = Field(None, description="Catalog description")
    service_type: Optional[str] = Field(None, description="A1 service type")
    service_name: Optional[str] = Field(None, description="A1 service name")
    
    # Source specifications
    spec_sources: Dict[str, str] = Field(default_factory=dict, description="Source spec files (SpecType -> file path)")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    
    # Test cases
    test_cases: List[OranTestCase] = Field(default_factory=list, description="List of test cases")
    
    # Statistics
    total_tests: int = Field(default=0, description="Total number of test cases")
    by_complexity: Dict[str, int] = Field(default_factory=dict, description="Count by complexity level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "catalog_id": "oran-catalog-001",
                "name": "A1 Interface Conformance Tests",
                "description": "Generated from ETSI TS 103 989",
                "spec_sources": {
                    "TS_103_989": "specs/ts_103_989.pdf",
                    "TS_103_987": "specs/ts_103_987.pdf"
                },
                "test_cases": [],
                "total_tests": 15,
                "by_complexity": {"BASIC": 8, "INTERMEDIATE": 5, "ADVANCED": 2}
            }
        }


class OranKpiMetrics(BaseModel):
    """O-RAN specific KPI metrics"""
    # Latency metrics
    avg_latency_ms: Optional[float] = Field(None, description="Average request latency (ms)")
    p95_latency_ms: Optional[float] = Field(None, description="95th percentile latency (ms)")
    p99_latency_ms: Optional[float] = Field(None, description="99th percentile latency (ms)")
    
    # Throughput metrics
    requests_per_second: Optional[float] = Field(None, description="Request throughput (req/s)")
    successful_requests_per_second: Optional[float] = Field(None, description="Successful request rate")
    
    # Conformance metrics
    conformance_rate: Optional[float] = Field(None, description="Conformance test pass rate (%)")
    schema_validation_rate: Optional[float] = Field(None, description="Schema validation pass rate (%)")
    
    # Resource metrics (optional)
    cpu_usage_percent: Optional[float] = Field(None, description="Average CPU usage during test")
    memory_usage_mb: Optional[float] = Field(None, description="Average memory usage (MB)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "avg_latency_ms": 45.2,
                "p95_latency_ms": 78.5,
                "p99_latency_ms": 125.3,
                "requests_per_second": 150.5,
                "successful_requests_per_second": 148.2,
                "conformance_rate": 98.5,
                "schema_validation_rate": 100.0
            }
        }


class OranExecutionResult(BaseModel):
    """Execution result for O-RAN test with KPI metrics"""
    execution_id: str
    test_id: str  # References OranTestCase.test_id
    catalog_id: Optional[str] = None
    
    # Status
    status: str  # Uses ExecutionStatus enum values
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Test results
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    pass_rate: float = 0.0
    
    # ORAN-specific KPIs
    kpis: Optional[OranKpiMetrics] = Field(None, description="O-RAN KPI metrics")
    
    # Output
    output_log: Optional[str] = None
    pytest_json_report: Optional[str] = None  # Path to pytest JSON report
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "oran-exec-001",
                "test_id": "A1_TC_001",
                "catalog_id": "oran-catalog-001",
                "status": "completed",
                "started_at": "2026-06-03T10:00:00Z",
                "completed_at": "2026-06-03T10:02:30Z",
                "duration_seconds": 150.0,
                "total_tests": 10,
                "passed": 9,
                "failed": 1,
                "skipped": 0,
                "pass_rate": 90.0,
                "kpis": {
                    "avg_latency_ms": 45.2,
                    "conformance_rate": 90.0
                }
            }
        }


# ======== PHASE 2A: A1-EI Models ========


class EiTypeObject(BaseModel):
    """Representation of an EI type as used by the A1-EI service."""

    ei_type_id: str = Field(..., description="EI type identifier")
    description: Optional[str] = Field(None, description="EI type description")
    ei_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema for EiJobObject")
    ei_status_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema for EiJobStatusObject",
    )
    ei_result_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema for EiJobResultObject",
    )
    supports_ei_job_creation: bool = Field(
        default=True,
        description="Whether EI job create/update is supported for the type",
    )


class EiTypeStatusObject(BaseModel):
    """Representation of EI type status feedback."""

    eiTypeId: str = Field(..., description="EI type identifier")
    eiTypeStatus: str = Field(..., description="Current EI type status")
    statusReason: Optional[str] = Field(None, description="Optional reason for EI type status")


class EiJobObject(BaseModel):
    """Representation of an EI job resource."""

    eiTypeId: str = Field(..., description="EI type identifier")
    jobDefinition: Dict[str, Any] = Field(..., description="EI job definition payload")
    jobStatusNotificationUri: Optional[str] = Field(
        None,
        description="Callback URI for EI job status notifications",
    )
    jobResultUri: Optional[str] = Field(
        None,
        description="Callback URI for EI job result deliveries",
    )


class EiJobStatusObject(BaseModel):
    """Representation of EI job status feedback."""

    eiJobStatus: str = Field(..., description="Annex A EI job status value")


class EiJobResultObject(BaseModel):
    """Representation of an EI job result payload."""

    jobResult: Dict[str, Any] = Field(..., description="Delivered EI job result payload")


# ======== PHASE 2 MODELS: Spec Parsing Pipeline ========

class TestClause(BaseModel):
    """Extracted test clause from ETSI specification"""
    clause_number: str = Field(..., description="Clause number (e.g., 5.3.1)")
    title: str = Field(..., description="Clause title")
    description: str = Field(..., description="Test description")
    entrance_criteria: Optional[str] = Field(None, description="Pre-conditions")
    methodology: Optional[str] = Field(None, description="Test execution steps")
    expected_result: Optional[str] = Field(None, description="Expected outcome")
    scenario_type: Optional[ScenarioType] = Field(None, description="Scenario classification inferred from methodology")
    spec_type: SpecType = Field(..., description="Source specification")
    page_number: Optional[int] = Field(None, description="Page number in source spec")
    raw_text: Optional[str] = Field(None, description="Raw extracted text (first 1000 chars)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clause_number": "5.3.1",
                "title": "Policy Creation Test",
                "description": "Test A1 policy creation via PUT request",
                "entrance_criteria": "A1 interface available",
                "methodology": "Send PUT request to /policies/{id}",
                "expected_result": "HTTP 201 Created response",
                "scenario_type": "CONFORMANCE",
                "spec_type": "TS_103_989",
                "page_number": 45,
                "raw_text": "..."
            }
        }


class TestSemantics(BaseModel):
    """Semantic information extracted from test clause"""
    scenario_type: Optional[ScenarioType] = Field(None, description="Scenario classification propagated to semantics")
    simulator_required: bool = Field(default=False, description="Whether simulator-backed execution is required")
    configurable_request_parts: List[str] = Field(default_factory=list, description="Request parts the simulator must support")
    http_method: Optional[HttpMethod] = Field(None, description="Extracted HTTP method")
    endpoint: Optional[str] = Field(None, description="Extracted API endpoint")
    payload_type: Optional[str] = Field(None, description="Extracted payload type")
    expected_status: Optional[int] = Field(None, description="Extracted expected status code")
    assertions: List[str] = Field(default_factory=list, description="Extracted assertions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_type": "CONFORMANCE",
                "simulator_required": True,
                "configurable_request_parts": ["uri", "headers", "body"],
                "http_method": "PUT",
                "endpoint": "/policies/{policy_id}",
                "payload_type": "PolicyObject",
                "expected_status": 201,
                "assertions": ["status_code == 201", "response.headers['Content-Type'] == 'application/json'"]
            }
        }


class EnrichedTestCase(BaseModel):
    """Test case enriched with data from multiple specifications"""
    base_clause: TestClause = Field(..., description="Base test clause from test spec")
    semantics: TestSemantics = Field(..., description="Extracted semantic information")
    scenario_type: Optional[ScenarioType] = Field(None, description="Scenario classification carried through enrichment")
    complexity: str = Field(default="BASIC", description="Test complexity level")
    enrichment_sources: Dict[str, str] = Field(default_factory=dict, description="Sources of enrichment data")
    
    # Cross-referenced data
    api_definition: Optional[Dict] = Field(None, description="API definition from TS 103 987")
    payload_schema: Optional[Dict] = Field(None, description="Payload schema from TS 103 988")
    terminology: Optional[Dict] = Field(None, description="Terminology from TS 103 983")
    
    # Conflict tracking
    conflicts: List[Dict] = Field(default_factory=list, description="Detected specification conflicts")
    resolution: Optional[str] = Field(None, description="Conflict resolution applied")
    
    class Config:
        json_schema_extra = {
            "example": {
                "base_clause": {},
                "semantics": {},
                "scenario_type": "CONFORMANCE",
                "complexity": "BASIC",
                "enrichment_sources": {"base": "TS_103_989 Section 5.3.1", "endpoint": "TS_103_987"},
                "api_definition": {"endpoint": "/policies/{id}", "method": "PUT"},
                "payload_schema": {"type": "object", "properties": {}},
                "conflicts": [],
                "resolution": "priority_order"
            }
        }


class SpecConflict(BaseModel):
    """Detected conflict between specifications"""
    conflict_id: str = Field(..., description="Unique conflict identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Conflict details
    field: str = Field(..., description="Conflicting field (e.g., 'endpoint', 'status_code')")
    spec1: SpecType
    value1: str
    spec2: SpecType
    value2: str
    
    # Resolution
    resolution: Optional[str] = Field(None, description="Applied resolution (e.g., 'priority_order', 'manual')")
    resolved_value: Optional[str] = Field(None, description="Final resolved value")
    reviewed: bool = Field(default=False, description="Whether conflict has been reviewed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conflict_id": "conflict-001",
                "field": "endpoint",
                "spec1": "TS_103_989",
                "value1": "/policies/{id}",
                "spec2": "TS_103_987",
                "value2": "/a1-p/policies/{policy_id}",
                "resolution": "priority_order",
                "resolved_value": "/policies/{id}",
                "reviewed": False
            }
        }


class MethodologySectionResult(BaseModel):
    """Methodology section identified in a spec."""
    section_number: str = Field(..., description="Section number")
    title: str = Field(..., description="Section title")
    page_number: Optional[int] = Field(None, description="Page number in source spec")
    depth: int = Field(..., description="Heading depth")
    evidence: List[str] = Field(default_factory=list, description="Evidence snippets")


class TestModuleCandidate(BaseModel):
    """Machine-assisted module candidate derived from methodology text."""
    module_name: str = Field(..., description="Distinct test module name")
    module_id: str = Field(..., description="Stable module identifier")
    source_section: str = Field(default="", description="Source section number")
    source_title: str = Field(default="", description="Source section title")
    confidence: float = Field(default=0.0, description="Confidence score 0..1")
    evidence: List[str] = Field(default_factory=list, description="Evidence snippets")
    keywords: List[str] = Field(default_factory=list, description="Keywords used for extraction")


class TestTitleCandidate(BaseModel):
    """Machine-assisted test title candidate derived from methodology text."""
    title: str = Field(..., description="Suggested test title")
    module_id: str = Field(..., description="Owning module identifier")
    source_section: str = Field(default="", description="Source section number")
    confidence: float = Field(default=0.0, description="Confidence score 0..1")
    evidence: List[str] = Field(default_factory=list, description="Evidence snippets")


class MethodologyAnalysisResult(BaseModel):
    """Result payload for methodology extraction and module naming."""
    spec_type: SpecType = Field(..., description="Source specification")
    service_type: Optional[str] = Field(None, description="Target A1 service type")
    spec_file: str = Field(..., description="Source file name")
    methodology_sections: List[MethodologySectionResult] = Field(default_factory=list)
    test_modules: List[TestModuleCandidate] = Field(default_factory=list)
    test_titles: List[TestTitleCandidate] = Field(default_factory=list)
    summary: Dict[str, int] = Field(default_factory=dict, description="Counts and summary metrics")
