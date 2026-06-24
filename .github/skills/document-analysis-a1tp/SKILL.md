---
name: document-analysis-a1tp
description: "Analyze A1 Technical Protocol specifications. Extract HTTP definitions, REST patterns, authentication mechanisms, and data formats. Map to existing API/protocol modules. Track version-specific changes."
domain: "A1 Interface Protocol"
document-family: "A1TP"
versions: ["v1.0", "v1.1", "v1.2"]
argument-hint: "section number or version to analyze"
user-invocable: true
related-skills:
  - document-cross-reference-analysis
  - document-analysis-a1td
  - document-analysis-a1gapconfiguration:
  ask-user-for-mode: true
  supported-modes:
    - single
    - dependencies
    - full-suite
    - version-evolution
  mode-descriptions:
    single: "Analyze this API specification in isolation"
    dependencies: "Include request/response schemas and procedure triggers from related documents"
    full-suite: "Complete analysis with all related A1 documents and ETSI standards"
    version-evolution: "Track API changes and breaking changes across document versions"---

# A1 Technical Protocol (A1TP) Analysis Skill

## Purpose
Extract and interpret A1TP specification content to:
- Identify HTTP/REST protocol requirements and constraints
- Map authentication and authorization patterns
- Extract data format and encoding specifications
- Suggest API module enrichments
- Track version-specific changes for future updates

## Document Context
**Document:** A1 Technical Protocol (A1TP)  
**Domain:** Telecom Interface Protocol - REST/HTTP Based  
**Referenced In:** Section 4.1 of TS 103.987 (A1 Application Protocol)  
**Related Documents:** 
- A1TD (Data Model)
- A1GAP (Gap Analysis/Procedures)
- ETSI TS 132 158 (Design Patterns)

## Use When
- Analyzing a new version of A1TP specification
- Extracting HTTP endpoint definitions and behaviors
- Identifying authentication/authorization requirements
- Mapping protocol requirements to code modules
- Processing version diffs to identify breaking changes
- Resolving cross-references from other A1-related documents

## Key Extraction Patterns

### HTTP Method Specifications
```
PATTERN: "HTTP (GET|POST|PUT|DELETE|PATCH) <endpoint>"
EXTRACT:
  - method: HTTP method
  - endpoint: URI path
  - request_body: Content requirements
  - response_codes: Expected HTTP status codes
  - headers: Required/optional headers
```

### Authentication/Authorization
```
PATTERN: "(Bearer|Basic|API-Key|OAuth|JWT)"
EXTRACT:
  - auth_type: Authentication mechanism
  - scope: Authorization scope
  - token_format: Token structure
  - expiry: Token validity period
```

### Data Format Specifications
```
PATTERN: "(JSON|XML|Protocol Buffer|MessagePack)"
EXTRACT:
  - format: Data format type
  - encoding: Character/binary encoding
  - schema: Structure definition
  - validation_rules: Constraints
```

### Error Handling
```
PATTERN: "(error|exception|failure|5xx|4xx)"
EXTRACT:
  - error_code: Numeric identifier
  - status_code: HTTP status
  - error_message: Description
  - recovery_action: Recommended handling
```

## Module Mapping Rules

### When to Enrich Modules
1. **api_routes.py** - New HTTP endpoint definitions
   - Map endpoint specs to FastAPI route decorators
   - Add request/response models
   - Define status code responses

2. **models/analysis_models.py** - New data structures
   - Add Protocol/RequestBody/Response dataclasses
   - Include validation constraints
   - Track enum values for status codes

3. **services/authentication_service.py** - Auth requirements
   - Implement identified auth types
   - Map scopes to role-based access control
   - Generate token validation logic

4. **utils/protocol_utils.py** - Protocol helpers
   - Error code -> HTTP status mapping
   - Content negotiation helpers
   - Header parsing utilities

## Version Tracking

### Current Implementation Target
**Versions:** v1.0, v1.1, v1.2  
**Latest:** v1.2 (as of TS 103.987 v4.3.0)

### Version-Specific Changes
```yaml
v1.0:
  base_endpoints: [/api/v1/...]
  auth_type: Bearer Token
  response_format: JSON

v1.1:
  additions:
    - new_endpoints: [/api/v1.1/...]
    - enhanced_auth: OAuth2
  deprecations:
    - old_endpoints: [/api/v1/...]

v1.2:
  additions:
    - async_operations: Supported
    - batch_operations: Supported
  breaking_changes:
    - response_format: JSON only (XML deprecated)
```

## Interpretation Rules

### Confidence Scoring
- Explicit spec language ("MUST", "SHALL", "REQUIRED"): 0.95+
- Recommended patterns ("SHOULD", "RECOMMENDED"): 0.75-0.85
- Optional guidance ("MAY", "CAN", "COULD"): 0.50-0.70

### Priority Ranking
1. **Critical:** Authentication, required endpoints, data validation
2. **High:** Error handling, content negotiation, headers
3. **Medium:** Optional features, deprecated endpoints
4. **Low:** Examples, deprecated versions

## Cross-Reference Resolution

When A1TP references other documents, extract:
- **Reference to A1TD:** Data structure definitions for request/response bodies
- **Reference to A1GAP:** Policy/procedure requirements affecting API behavior
- **Reference to ETSI TS 132 158:** Design pattern compliance for REST structures

## Extraction Output Structure

```python
A1TPAnalysis:
  document_version: str
  http_endpoints: List[HTTPEndpoint]
  authentication_specs: List[AuthSpec]
  data_formats: List[DataFormat]
  error_codes: List[ErrorCode]
  design_patterns: List[str]  # Patterns from ETSI reference
  version_diffs: Dict[str, List[Change]]
  module_suggestions: List[ModuleEnrichment]
  extraction_confidence: float
```

## Code Generation Suggestions

### When to Generate
- New HTTP endpoint definitions → Generate FastAPI route skeleton
- New auth requirement → Generate auth middleware wrapper
- New data format → Generate Pydantic model
- New error codes → Generate error enum and exception classes

### Generation Template
```python
# Generated from A1TP v1.2 specification
@router.post("/api/v1.2/endpoint-name")
@require_auth(scopes=["read:resource"])
async def endpoint_name(
    request: RequestModel,
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """
    Implementation from A1TP v1.2 Spec
    See: [document-reference]
    Cross-ref to A1TD: [data-model-ref]
    """
    # TODO: Implement per specification
    pass
```

## Quality Validation

### Expected Extraction Ranges
- HTTP endpoints per section: 2-5
- Auth specs per document: 3-8
- Data formats per section: 1-3
- Error codes: 10-20 per API version

### Confidence Thresholds
- Accept extraction if avg confidence > 0.75
- Flag for review if 0.60 < confidence ≤ 0.75
- Reject if confidence ≤ 0.60 (requires manual review)

## Usage Example

```python
# Analyze A1TP v1.2 specification
from skill import analyze_a1tp_specification

result = analyze_a1tp_specification(
    document_path="C:/docs/a1tp_v1.2.pdf",
    version="v1.2",
    target_modules=["api_routes", "models/analysis_models"],
    extract_cross_references=True,
    generate_code_suggestions=True
)

# Result contains:
# - Extracted HTTP endpoints and auth specs
# - Mapped modules to enrich
# - Code generation suggestions
# - Version comparison vs v1.1
# - Cross-reference mappings to A1TD/A1GAP
```

## Integration with Central Analysis

This skill is designed to be called by:
1. **Local Analysis:** When user requests A1TP analysis
2. **Cross-Reference Analysis:** When processing another document that references A1TP
3. **Version Update:** When a new A1TP version becomes available

The `document-cross-reference-analysis` skill orchestrates calling this skill in context of other documents.

## Related Skills
- `document-analysis-a1td` - Analyze data model definitions
- `document-analysis-a1gap` - Analyze procedure requirements
- `document-analysis-etsi-ts-132-158` - Analyze design patterns
- `document-cross-reference-analysis` - Handle inter-document dependencies
