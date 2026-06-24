---
name: document-analysis-etsi-ts-132-158
description: "Analyze ETSI TS 132 158 design patterns and standards. Extract architectural patterns, coding standards, naming conventions, and design guidelines. Map to existing codebase patterns. Validate conformance."
domain: "ETSI Telecom Design Standards"
document-family: "ETSI TS 132 158"
versions: ["v15.0.0", "v16.0.0", "v17.0.0"]
argument-hint: "pattern type or section to analyze"
user-invocable: true
related-skills:
  - document-cross-reference-analysis
  - document-analysis-a1tp
  - document-analysis-a1td
  - document-analysis-a1gap
configuration:
  ask-user-for-mode: true
  supported-modes:
    - single
    - dependencies
    - full-suite
  mode-descriptions:
    single: "Analyze ETSI patterns and standards in isolation"
    dependencies: "Validate A1TP, A1TD, and A1GAP compliance against these standards"
    full-suite: "Complete analysis with all A1 specifications validated against ETSI"
---

# ETSI TS 132 158 Design Patterns Analysis Skill

## Purpose
Extract and interpret ETSI TS 132 158 content to:
- Identify architectural and design patterns
- Extract coding standards and conventions
- Map naming conventions and structure
- Identify REST/HTTP best practices
- Generate pattern-compliant code
- Validate existing code conformance
- Establish baseline standards for new development

## Document Context
**Document:** ETSI TS 132 158 - 3GPP Design Patterns  
**Domain:** Telecom Industry Standards - Design Best Practices  
**Referenced In:** Section 4.1 of TS 103.987 (A1 Application Protocol)  
**Application:** Cross-cutting standard for A1TP, A1TD, and A1GAP compliance

## Use When
- Analyzing design pattern compliance in A1 specifications
- Establishing coding standards for implementation
- Validating API design against industry standards
- Creating code templates that follow ETSI patterns
- Reviewing existing code for standard compliance
- Training agents on telecom industry best practices

## Key Extraction Patterns

### Architectural Patterns
```
PATTERN: "(pattern|architecture|style|approach) <Name>"
EXTRACT:
  - pattern_name: Pattern identifier
  - pattern_type: Category (REST, microservice, message-driven, etc)
  - use_case: When to apply
  - components: Key architectural elements
  - benefits: Advantages of this pattern
  - tradeoffs: Disadvantages or constraints
  - examples: Concrete implementations
```

### API Design Patterns
```
PATTERN: "(REST|HTTP|API) (resource|endpoint|operation)"
EXTRACT:
  - resource_pattern: Resource naming convention
  - method_pattern: HTTP method usage rules
  - status_code_pattern: Expected response codes
  - header_pattern: Standard headers
  - body_structure: Request/response structure
  - versioning_strategy: API version management
```

### Data Representation Patterns
```
PATTERN: "(JSON|XML|serialization|encoding)"
EXTRACT:
  - format_type: Data format
  - structure_rules: How to structure objects
  - naming_conventions: Field naming rules
  - type_mappings: Type equivalences
  - cardinality_rules: Single vs collection
  - metadata_representation: How to include metadata
```

### Error Handling Patterns
```
PATTERN: "(error|exception|fault|failure) (handling|response)"
EXTRACT:
  - error_structure: Error object format
  - status_mapping: Error category to HTTP status
  - error_codes: Standard error code ranges
  - error_messages: Message formatting rules
  - retry_strategy: Retry policies
  - logging_requirements: What to log
```

### Security Patterns
```
PATTERN: "(security|authentication|authorization|encryption)"
EXTRACT:
  - auth_pattern: Authentication mechanism
  - token_pattern: Token format and lifecycle
  - scope_pattern: Authorization scope structure
  - encryption_pattern: Data protection approach
  - audit_pattern: Audit logging requirements
```

### Naming Conventions
```
PATTERN: "(naming|convention|identifier|naming_rule)"
EXTRACT:
  - resource_naming: How resources are named
  - method_naming: Function/method naming rules
  - class_naming: Class/type naming conventions
  - variable_naming: Variable naming style
  - constant_naming: Constant naming rules
  - case_style: camelCase vs snake_case vs PascalCase
```

## Module Mapping Rules

### When to Enrich Modules
1. **codestyle/** - Coding standards
   - Create style guide documentation
   - Define naming convention checkers
   - Add pattern validators
   - Generate code linters

2. **patterns/templates.py** - Code templates
   - Create pattern-compliant API route templates
   - Generate request/response model templates
   - Build error handling templates
   - Include security/auth templates

3. **validators/pattern_validator.py** - Conformance checking
   - Validate API designs against patterns
   - Check naming convention compliance
   - Verify data structure patterns
   - Audit error handling conformance

4. **documentation/style_guide.md** - Developer guidance
   - Document applicable patterns
   - Provide code examples
   - Establish team standards
   - Include anti-patterns to avoid

## Version Tracking

### Current Implementation Target
**Versions:** v15.0.0, v16.0.0, v17.0.0  
**Latest:** v17.0.0 (3GPP Release 17)

### Version-Specific Standards
```yaml
v15.0.0:
  patterns:
    - RESTful Resources
    - JSON serialization
    - Bearer Token Auth
    - Stateless services
  standards:
    - Naming: camelCase for fields
    - Errors: Standard HTTP status codes
    - Versioning: /api/v1/ prefix

v16.0.0:
  additions:
    - Async operation patterns
    - Batch operation patterns
    - Server-sent events support
  deprecations:
    - XML serialization
  modifications:
    - Error format: Enhanced structured errors

v17.0.0:
  additions:
    - OpenAPI 3.1 compliance
    - Rate limiting patterns
    - Distributed tracing standards
    - GraphQL federation (optional)
  modifications:
    - Security: OAuth2.1 requirements
    - Versioning: Support for content negotiation
```

## Interpretation Rules

### Confidence Scoring
- Explicit ETSI pattern specification: 0.95+
- Clear standards with examples: 0.85-0.95
- Industry best practices guidance: 0.75-0.85
- Implied from context: 0.65-0.75

### Priority Ranking
1. **Critical:** Core architectural patterns, security requirements, data protection
2. **High:** Naming conventions, API design patterns, error handling
3. **Medium:** Optional patterns, enhancement techniques
4. **Low:** Historical context, deprecated approaches, research topics

## Cross-Document Pattern Compliance

This skill checks if A1TP, A1TD, and A1GAP comply with ETSI standards:

### A1TP Compliance Points
- API endpoints follow resource naming conventions
- HTTP methods used per ETSI recommendations
- Status codes align with ETSI mappings
- Error responses follow standard structure
- Authentication patterns match ETSI guidance

### A1TD Compliance Points
- Data structures follow entity naming conventions
- Field naming consistent with ETSI style
- Type mappings align with standards
- JSON serialization follows ETSI format rules
- Enumerations properly documented

### A1GAP Compliance Points
- Procedures follow ETSI orchestration patterns
- State machines use standard terminology
- Error scenarios mapped to standard codes
- Policy rules use ETSI convention

## Extraction Output Structure

```python
ETSIPatternAnalysis:
  document_version: str
  architectural_patterns: List[ArchitecturalPattern]
  api_patterns: List[APIPattern]
  data_patterns: List[DataPattern]
  error_patterns: List[ErrorPattern]
  security_patterns: List[SecurityPattern]
  naming_conventions: Dict[str, NamingRule]
  code_templates: List[CodeTemplate]
  compliance_mapping: Dict[str, ComplianceLevel]  # A1TP/TD/GAP compliance
  implementation_guide: str
  module_suggestions: List[ModuleEnrichment]
  extraction_confidence: float
```

## Code Generation Suggestions

### Pattern Template - RESTful Resource
```python
# Generated from ETSI TS 132 158 patterns
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List

class ResourceModel(BaseModel):
    """
    Resource following ETSI TS 132 158 patterns
    Naming: camelCase fields
    Serialization: JSON per v17.0.0
    """
    resourceId: str
    resourceName: str
    createdAt: Optional[str] = None
    lastModifiedAt: Optional[str] = None

class ResourceListResponse(BaseModel):
    """Collection response per ETSI pattern"""
    resources: List[ResourceModel]
    totalCount: int
    pageSize: Optional[int] = None

router = APIRouter(prefix="/api/v1/resources", tags=["Resources"])

@router.post(
    "",
    response_model=ResourceModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid input"},
        409: {"description": "Resource already exists"},
        500: {"description": "Internal server error"}
    }
)
async def create_resource(resource: ResourceModel) -> ResourceModel:
    """
    Create resource per ETSI pattern
    - Uses POST for creation
    - Returns 201 Created
    - Returns created resource
    """
    # Implementation per ETSI guidelines
    pass

@router.get(
    "/{resourceId}",
    response_model=ResourceModel,
    responses={404: {"description": "Resource not found"}}
)
async def get_resource(resourceId: str) -> ResourceModel:
    """Get resource per ETSI read pattern"""
    pass

@router.put(
    "/{resourceId}",
    response_model=ResourceModel,
    responses={404: {"description": "Resource not found"}}
)
async def update_resource(resourceId: str, resource: ResourceModel) -> ResourceModel:
    """Update resource per ETSI pattern"""
    pass

@router.delete(
    "/{resourceId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Resource not found"}}
)
async def delete_resource(resourceId: str) -> None:
    """Delete resource per ETSI pattern"""
    pass

@router.get("", response_model=ResourceListResponse)
async def list_resources(
    pageSize: int = 10,
    pageMarker: Optional[str] = None
) -> ResourceListResponse:
    """
    List resources per ETSI pagination pattern
    Uses query parameters: pageSize, pageMarker
    Returns total count and resource collection
    """
    pass
```

### Pattern Validator Template
```python
# Generated from ETSI TS 132 158 compliance rules
from typing import List, Dict, Any

class ETSIPatternValidator:
    """Validate code conformance to ETSI patterns"""
    
    NAMING_RULES = {
        "resource_names": r"^[a-z][a-zA-Z0-9]*s?$",  # camelCase, plural
        "method_names": r"^[a-z][a-zA-Z0-9]*$",  # camelCase
        "class_names": r"^[A-Z][a-zA-Z0-9]*$",  # PascalCase
        "constant_names": r"^[A-Z_]+$",  # UPPER_SNAKE_CASE
    }
    
    HTTP_METHOD_RULES = {
        "POST": ["201", "202", "400", "409", "500"],
        "GET": ["200", "404", "500"],
        "PUT": ["200", "204", "404", "500"],
        "DELETE": ["204", "404", "500"],
        "PATCH": ["200", "204", "404", "500"],
    }

    def validate_api_naming(self, endpoint: str) -> bool:
        """Validate endpoint naming per ETSI pattern"""
        # Check camelCase resource names
        # Check appropriate pluralization
        # Verify no abbreviations
        return True

    def validate_status_codes(self, method: str, codes: List[str]) -> bool:
        """Validate status codes per ETSI standard"""
        allowed = self.HTTP_METHOD_RULES.get(method, [])
        return all(code in allowed for code in codes)

    def validate_error_response(self, error_obj: Dict[str, Any]) -> bool:
        """Validate error structure per ETSI pattern"""
        required_fields = ["errorCode", "errorDescription"]
        return all(field in error_obj for field in required_fields)
```

## Quality Validation

### Pattern Conformance Checklist
- API endpoints follow naming conventions: ≥95%
- HTTP methods used correctly: 100%
- Error responses match standard structure: 100%
- Status codes align with standards: 100%
- Data models use proper naming: ≥95%

### Standards Compliance Report
- Architecture aligned with ETSI patterns: Yes/No
- Security measures meet ETSI requirements: Yes/No
- Data handling follows ETSI guidelines: Yes/No
- Integration points use standard interfaces: Yes/No

## Usage Example

```python
# Analyze ETSI TS 132 158 patterns
from skill import analyze_etsi_patterns

result = analyze_etsi_patterns(
    document_path="C:/docs/etsi_ts_132_158_v17.pdf",
    version="v17.0.0",
    cross_check_documents=["a1tp", "a1td", "a1gap"],  # Validate compliance
    generate_templates=True,
    generate_validators=True
)

# Result contains:
# - Architectural and design patterns
# - Naming conventions and standards
# - API/data/error patterns
# - Code generation templates
# - Pattern compliance validators
# - A1TP/TD/GAP compliance mapping
```

## Impact Analysis

### Step 1: Identify Impacted Modules/Features

The skill automatically identifies which modules need to be enhanced for standards compliance:

```python
Impacted Modules Analysis:

For each design pattern/standard:
  - Feature: Code Style & Conventions
    Modules: codestyle/naming_conventions.py, utils/style_validator.py
    Impact: MEDIUM (linter rules, formatters)
    
  - Feature: API Design Patterns
    Modules: patterns/rest_patterns.py, templates/route_templates.py
    Impact: MEDIUM (route generation guidance)
    
  - Feature: Data Format Standards
    Modules: utils/serialization_validator.py, services/format_converter.py
    Impact: MEDIUM (JSON encoding rules)
    
  - Feature: Security Patterns
    Modules: services/security_validator.py, utils/auth_pattern_checker.py
    Impact: HIGH (OAuth2.1, token patterns)
    
  - Feature: Error Handling Standards
    Modules: services/error_formatter.py, utils/error_code_mapper.py
    Impact: MEDIUM (error code standards)
    
  - Feature: Compliance Validation
    Modules: validators/pattern_validator.py, utils/conformance_checker.py
    Impact: MEDIUM (audit and compliance)
```

### Step 2: Identify Files to Modify

The skill lists files needing updates to achieve ETSI compliance:

```python
Files to Modify:

┌─ CODING STANDARDS & LINTING ─────────────┐
│                                           │
│ codestyle/naming_conventions.py           │
│   Changes: Add ETSI naming rules          │
│   Lines: Add camelCase, snake_case rules │
│   Priority: MEDIUM                        │
│                                           │
│ .pylintrc                                 │
│   Changes: Add ETSI-specific rules        │
│   Lines: Add pattern matching rules       │
│   Priority: MEDIUM                        │
│                                           │
│ pyproject.toml                            │
│   Changes: Configure tools per ETSI       │
│   Lines: Add black, isort, mypy configs   │
│   Priority: MEDIUM                        │
│                                           │
└─────────────────────────────────────────┘

┌─ API DESIGN PATTERNS ────────────────────┐
│                                           │
│ patterns/rest_patterns.py                 │
│   Changes: Implement ETSI REST patterns  │
│   Lines: Add resource patterns            │
│   Priority: MEDIUM                        │
│                                           │
│ templates/route_templates.py              │
│   Changes: Add ETSI-compliant templates  │
│   Lines: Add FastAPI endpoint template    │
│   Priority: MEDIUM                        │
│                                           │
│ utils/api_design_validator.py             │
│   Changes: Validate API design            │
│   Lines: Add endpoint validation logic    │
│   Priority: HIGH                          │
│                                           │
└─────────────────────────────────────────┘

┌─ SECURITY STANDARDS ─────────────────────┐
│                                           │
│ services/security_validator.py            │
│   Changes: Enforce ETSI security rules   │
│   Lines: Add OAuth2.1 validation logic    │
│   Priority: CRITICAL                      │
│                                           │
│ utils/auth_pattern_checker.py             │
│   Changes: Check token patterns           │
│   Lines: Add token format validators      │
│   Priority: HIGH                          │
│                                           │
│ config/security_config.json               │
│   Changes: Configure security standards  │
│   Lines: Add ETSI-compliant settings     │
│   Priority: HIGH                          │
│                                           │
└─────────────────────────────────────────┘

┌─ ERROR & DATA FORMAT STANDARDS ──────────┐
│                                           │
│ services/error_formatter.py               │
│   Changes: Format errors per ETSI         │
│   Lines: Add error response structure     │
│   Priority: MEDIUM                        │
│                                           │
│ utils/serialization_validator.py          │
│   Changes: Validate JSON format           │
│   Lines: Add JSON structure validators    │
│   Priority: MEDIUM                        │
│                                           │
├─ DOCUMENTATION ──────────────────────────┤
│                                           │
│ docs/etsi_compliance_guide.md             │
│   Changes: Document compliance rules      │
│   Scope: Add ETSI pattern guide           │
│   Priority: MEDIUM                        │
│                                           │
│ docs/architecture_patterns.md             │
│   Changes: Document architectural ways   │
│   Scope: Add pattern descriptions         │
│   Priority: MEDIUM                        │
│                                           │
└─────────────────────────────────────────┘
```

### Step 3: Identify Tests to Modify/Create

The skill identifies test requirements for standards compliance:

```python
Tests to Create/Modify:

┌─ NEW TEST FILES ─────────────────────────┐
│                                           │
│ tests/test_naming_conventions.py          │
│   Type: Naming standard compliance tests │
│   Test Cases:                             │
│     - test_camel_case_method_names       │
│     - test_pascal_case_class_names       │
│     - test_snake_case_variable_names     │
│     - test_constant_naming_rules         │
│   Total Test Cases: 10                   │
│   Priority: HIGH                         │
│                                           │
│ tests/test_api_patterns_compliance.py     │
│   Type: REST API pattern tests           │
│   Test Cases:                             │
│     - test_resource_naming_convention    │
│     - test_http_method_semantics         │
│     - test_status_code_patterns          │
│     - test_error_response_structure      │
│   Total Test Cases: 12                   │
│   Priority: HIGH                         │
│                                           │
│ tests/test_security_compliance.py         │
│   Type: Security standard tests          │
│   Test Cases:                             │
│     - test_oauth2_1_compliance           │
│     - test_token_format_validation       │
│     - test_encryption_standards          │
│   Total Test Cases: 8                    │
│   Priority: CRITICAL                     │
│                                           │
│ tests/test_json_format_compliance.py      │
│   Type: Data format tests                │
│   Test Cases:                             │
│     - test_json_field_naming             │
│     - test_nested_object_structure       │
│     - test_array_serialization           │
│   Total Test Cases: 7                    │
│   Priority: MEDIUM                       │
│                                           │
└─────────────────────────────────────────┘

┌─ MODIFY EXISTING TEST FILES ─────────────┐
│                                           │
│ tests/test_api_routes.py                 │
│   Changes: Validate ETSI compliance     │
│   Lines: Add pattern compliance checks   │
│   Priority: HIGH                         │
│                                           │
│ tests/test_security.py                   │
│   Changes: Add ETSI security tests       │
│   Lines: Add OAuth2.1 test scenarios     │
│   Priority: HIGH                         │
│                                           │
│ tests/test_models.py                     │
│   Changes: Validate naming conventions   │
│   Lines: Add naming validation tests     │
│   Priority: MEDIUM                       │
│                                           │
└─────────────────────────────────────────┘
```

### Impact Summary Report

The skill generates standards compliance assessment:

```python
Impact Assessment Output:

{
  "document_version": "v17.0.0",
  "patterns_analyzed": 25,
  "extraction_summary": {
    "architectural_patterns": 6,
    "naming_conventions": 12,
    "api_patterns": 8,
    "error_patterns": 5,
    "security_patterns": 4
  },
  "module_impact": {
    "high_impact": [
      "services/security_validator.py",
      "utils/api_design_validator.py"
    ],
    "medium_impact": [
      "codestyle/naming_conventions.py",
      "services/error_formatter.py"
    ]
  },
  "files_to_modify": {
    "standards_validators": 5,
    "config_files": 2,
    "template_files": 2,
    "test_files": 7,
    "doc_files": 2
  },
  "test_requirements": {
    "new_test_files": 4,
    "tests_to_create": 37,
    "existing_files_to_update": 3
  },
  "compliance_status": {
    "current_compliance": "70%",
    "violations_found": 8,
    "violations_severity": {
      "critical": 2,
      "high": 3,
      "medium": 3
    }
  },
  "implementation_effort": {
    "estimated_hours": 12,
    "critical_priority": 2,
    "high_priority": 5,
    "medium_priority": 4
  },
  "risk_assessment": "MEDIUM - Security pattern changes require careful review",
  "recommendation": "Address security violations (critical) first, then implement naming standards"
}
```

## Integration with Central Analysis

This skill:
1. **Validates** - Checks A1TP/TD/GAP compliance with ETSI standards
2. **Guides** - Provides standard templates for new development
3. **Audits** - Ensures existing code follows industry standards
4. **Educates** - Explains why standards matter for telecom

The `document-cross-reference-analysis` skill uses this skill to validate that derived implementations meet industry standards.

## Related Skills
- `document-analysis-a1tp` - Validate REST API design against ETSI patterns
- `document-analysis-a1td` - Validate data models against ETSI standards
- `document-analysis-a1gap` - Validate procedures against ETSI patterns
- `document-cross-reference-analysis` - Orchestrate cross-document compliance checking
