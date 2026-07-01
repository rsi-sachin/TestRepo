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
  - document-analysis-a1gap
configuration:
  ask-user-for-mode: true
  implicit-trigger-patterns:
    - prompt-pattern: "Analyze sections <section-list> from <document-path>"
      implied-primary-skill: document-analysis-a1tp
      implied-orchestrator-skill: document-cross-reference-analysis
      implied-mode: single
      implied-extraction-focus:
        - http
        - rest
        - resource
        - status code
        - authentication
      implied-section-selection:
        skip-first-section-match: true
        use-body-section-text: true
      implied-output-requirements:
        - map findings to existing tests and code
        - list new tests
        - list modified tests
        - list implementation and coverage gaps
  supported-modes:
    - single
    - dependencies
    - full-suite
    - version-evolution
  mode-descriptions:
    single: "Analyze this API specification in isolation"
    dependencies: "Include request/response schemas and procedure triggers from related documents"
    full-suite: "Complete analysis with all related A1 documents and ETSI standards"
    version-evolution: "Track API changes and breaking changes across document versions"
  mandatory-invocation-when:
    - request contains protocol markers (http, rest, endpoint, resource, uri, status code, authentication)
    - target document is technical protocol oriented
  fail-closed-if-not-invoked: true
  required-analysis-output-fields:
    - selected_primary_skill
    - selected_secondary_skills
    - why_selected
    - protocol_markers_detected
    - section_target_validation
    - pre_response_checklist
traceability:
  required-artifact: "ORAN/docs/feature_traceability_map.md"
  required-before-code-generation: true
  required-output-fields:
    - selected_trace_ids
    - mapped_todo_sections
    - mapped_code_scope
    - verification_targets
  code-generation-gate: "Do not generate source code unless selected_trace_ids is non-empty and resolved against ORAN/docs/feature_traceability_map.md."
---

# A1 Technical Protocol (A1TP) Analysis Skill

## Purpose
Extract and interpret A1TP specification content to:
- Identify HTTP/REST protocol requirements and constraints
- Map authentication and authorization patterns
- Extract data format and encoding specifications
- Suggest API module enrichments
- Track version-specific changes for future updates

## Traceability Requirements

Before converting extracted protocol knowledge to source code, this skill must:

0. Map findings to Trace IDs in `ORAN/docs/feature_traceability_map.md` before proposing code changes.

1. Read `ORAN/docs/feature_traceability_map.md`.
2. Resolve extracted endpoint/auth/data requirements to one or more Trace IDs.
3. Restrict generated file targets to mapped `Code Scope` entries.
4. Produce verification work from mapped `Verification` entries.
5. Block code generation if no traceable mapping exists.

Required conversion payload fields:

```yaml
selected_trace_ids: ["ORAN-FTM-004", "ORAN-FTM-008"]
mapped_todo_sections:
  - "Traceability and Quality Follow-up"
  - "Phase 3 Task 3.1"
mapped_code_scope:
  - "demo-web/backend/app/api/oran.py"
  - "demo-web/backend/app/services/test_generator_service.py"
verification_targets:
  - "API tests for /api/oran/services, generation, upload, selection flows"
  - "JSON schema validation for generated catalogs"
```

Hard gate:

- Do not emit source code unless `selected_trace_ids` is non-empty and resolved against `ORAN/docs/feature_traceability_map.md`.
- Do not propose code changes unless findings are mapped to Trace IDs in `ORAN/docs/feature_traceability_map.md`.

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

## Invocation Requirements

- This skill is mandatory as the primary skill for protocol-centric technical analysis.
- If protocol markers are present and this skill is not selected, analysis must stop and report a routing error.
- `document-cross-reference-analysis` can be used as orchestrator, but does not replace mandatory primary selection of this skill for protocol-centric requests.
- For prompts matching `Analyze sections <section-list> from <document-path>`, this skill is implied as primary by default.
- For that prompt pattern, `document-cross-reference-analysis` runs in `single` mode by default unless the user explicitly asks for a different mode.

Required routing audit fields in every analysis response:

```yaml
selected_primary_skill: "document-analysis-a1tp"
selected_secondary_skills: ["document-cross-reference-analysis"]
why_selected: "Protocol markers detected in user request/document section"
protocol_markers_detected: ["HTTP", "REST", "status code"]
section_target_validation:
  requested_section: "4.4"
  toc_match_skipped: true
  body_section_used: true
```

## Pre-Response Checklist

Before finalizing an analysis response, confirm all items below:

- Body section target validated (TOC match skipped when duplicate heading is found).
- Protocol markers extracted and listed.
- HTTP/REST/auth/data/error handling extraction performed when applicable.
- Test or module impact mapping provided.
- Existing tests/code mapping provided, with explicit lists for new tests, modified tests, and gaps.
- Required routing audit fields populated.

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
    target_modules=["api_routes.py", "models/analysis_models"],
    compare_to_version="v1.1",  # Show API changes
    extract_methods=True,
    extract_cross_references=True,
    generate_code_suggestions=True
)

# Result contains:
# - Extracted endpoints, methods, auth, error patterns
# - FastAPI route templates
# - Version diff highlighting breaking changes
# - Data schema references (from A1TD cross-ref)
# - Procedure triggers (from A1GAP cross-ref)
```

## Impact Analysis

### Step 1: Identify Impacted Modules/Features

The skill automatically identifies which modules and features are affected by extracted API definitions:

```python
Impacted Modules Analysis:

For each extracted endpoint:
  - Feature: Authentication & Authorization
    Modules: services/authentication_service.py, utils/token_validator.py
    Impact: HIGH (all endpoints require auth)
    
  - Feature: API Request/Response Handling
    Modules: api_routes.py, models/request_models.py, models/response_models.py
    Impact: DIRECT (new endpoints = new routes)
    
  - Feature: Error Handling
    Modules: services/error_handler.py, utils/error_formatter.py
    Impact: MEDIUM (new error codes/scenarios)
    
  - Feature: API Documentation
    Modules: docs/api_reference.md, utils/openapi_generator.py
    Impact: MEDIUM (OpenAPI/Swagger updates needed)
    
  - Feature: Request Validation
    Modules: utils/validation.py, services/request_validator.py
    Impact: DIRECT (validate new request schemas)
    
  - Feature: Response Serialization
    Modules: services/serialization_service.py, utils/json_encoder.py
    Impact: DIRECT (serialize new response schemas)
```

### Step 2: Identify Files to Modify

The skill lists files that must be updated to implement extracted changes:

```python
Files to Modify:

┌─ PRODUCTION CODE ─────────────────────────────────────┐
│                                                       │
│ api_routes.py                                         │
│   Changes: Add 3 new FastAPI routes                  │
│   Lines: Insert routes for POST/PUT/DELETE            │
│   Priority: CRITICAL                                  │
│                                                       │
│ models/request_models.py                              │
│   Changes: Add 2 new Pydantic request models          │
│   Lines: Add ResourceCreateRequest,                   │
│          ResourceUpdateRequest                        │
│   Priority: CRITICAL                                  │
│                                                       │
│ services/authentication_service.py                    │
│   Changes: Add auth for new endpoints                 │
│   Lines: Update token validation logic                │
│   Priority: CRITICAL                                  │
│                                                       │
│ utils/validation.py                                   │
│   Changes: Add validators for new fields              │
│   Lines: Add field constraints validation             │
│   Priority: HIGH                                      │
│                                                       │
│ services/error_handler.py                             │
│   Changes: Add new error codes                        │
│   Lines: Add 409 Conflict handler                     │
│   Priority: MEDIUM                                    │
│                                                       │
└───────────────────────────────────────────────────────┘

┌─ CONFIGURATION & DOCUMENTATION ─────────────────────┐
│                                                     │
│ docs/api_reference.md                               │
│   Changes: Document new endpoints                   │
│   Scope: Add Section 4.2 endpoint docs              │
│   Priority: HIGH                                    │
│                                                     │
│ config/api_config.json                              │
│   Changes: Add feature flags                        │
│   Lines: Add "enable_resource_management"           │
│   Priority: MEDIUM                                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Step 3: Identify Tests to Modify/Create

The skill identifies test files requiring updates to cover new functionality:

```python
Tests to Create/Modify:

┌─ NEW TEST FILES ──────────────────────────────────────┐
│                                                       │
│ tests/test_api_endpoints_section_4_2.py              │
│   Type: Unit tests for new endpoints                 │
│   Test Cases:                                         │
│     - test_create_resource_201                       │
│     - test_create_resource_400_invalid               │
│     - test_create_resource_409_conflict              │
│     - test_get_resource_200                          │
│     - test_get_resource_404_not_found                │
│     - test_update_resource_200                       │
│     - test_update_resource_404                       │
│     - test_delete_resource_204                       │
│     - test_delete_resource_404                       │
│   Total Test Cases: 12                               │
│   Priority: CRITICAL                                 │
│                                                       │
│ tests/test_auth_section_4_2.py                       │
│   Type: Auth validation for new endpoints            │
│   Test Cases:                                         │
│     - test_endpoints_require_bearer_token            │
│     - test_invalid_token_401                         │
│     - test_expired_token_401                         │
│     - test_token_scope_validation                    │
│   Total Test Cases: 4                                │
│   Priority: CRITICAL                                 │
│                                                       │
│ tests/test_validation_section_4_2.py                 │
│   Type: Request validation tests                     │
│   Test Cases:                                         │
│     - test_create_resource_validation                │
│     - test_required_fields_validation                │
│     - test_field_type_validation                     │
│   Total Test Cases: 5                                │
│   Priority: HIGH                                     │
│                                                       │
└───────────────────────────────────────────────────────┘

┌─ MODIFY EXISTING TEST FILES ──────────────────────────┐
│                                                       │
│ tests/test_api_routes.py                             │
│   Changes: Add new endpoints to suite                │
│   Lines: Add parametrized test cases                 │
│   Priority: HIGH                                     │
│                                                       │
│ tests/test_error_handling.py                         │
│   Changes: Add 409 Conflict error tests              │
│   Lines: Add error code 409 test cases               │
│   Priority: HIGH                                     │
│                                                       │
│ tests/integration/test_full_workflow.py              │
│   Changes: Add integration tests                     │
│   Lines: Add end-to-end workflow tests               │
│   Priority: MEDIUM                                   │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### Impact Summary Report

The skill generates a structured impact report:

```python
Impact Assessment Output:

{
  "document_version": "v1.2",
  "section_analyzed": "4.2",
  "extraction_summary": {
    "endpoints_found": 8,
    "request_models_needed": 2,
    "response_models_needed": 2,
    "error_scenarios": 5
  },
  "module_impact": {
    "high_impact": [
      "api_routes.py",
      "models/request_models.py",
      "services/authentication_service.py"
    ],
    "medium_impact": [
      "services/error_handler.py",
      "utils/validation.py"
    ],
    "low_impact": [
      "docs/api_reference.md",
      "config/api_config.json"
    ]
  },
  "files_to_modify": {
    "production_files": 5,
    "test_files": 8,
    "config_files": 1,
    "doc_files": 1
  },
  "test_requirements": {
    "new_test_files": 3,
    "tests_to_create": 21,
    "existing_files_to_update": 3
  },
  "implementation_effort": {
    "estimated_hours": 8,
    "critical_priority": 5,
    "high_priority": 7,
    "medium_priority": 2
  },
  "risk_assessment": "MEDIUM - New error scenarios require careful testing",
  "recommendation": "Create comprehensive unit + integration test suite before deployment"
}
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
