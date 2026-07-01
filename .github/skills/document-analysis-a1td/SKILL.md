---
name: document-analysis-a1td
description: "Analyze A1 Technical Data Model specifications. Extract data structures, fields, types, constraints, and relationships. Generate Pydantic models and database schemas. Track version-specific schema changes."
domain: "A1 Interface Data Model"
document-family: "A1TD"
versions: ["v1.0", "v1.1", "v1.2"]
argument-hint: "section number or entity type to analyze"
user-invocable: true
related-skills:
  - document-cross-reference-analysis
  - document-analysis-a1tp
  - document-analysis-a1gap
configuration:
  ask-user-for-mode: true
  post-analysis-handoff:
    target-skill: post-analysis-test-policy-orchestration
    trigger: "after analysis completes and the user requests implementation, testing, or coverage closure"
    fail-closed-if-skipped: true
  supported-modes:
    - single
    - dependencies
    - full-suite
    - version-evolution
  mode-descriptions:
    single: "Analyze data structures in this specification alone"
    dependencies: "Include API endpoints that use these models and procedures that modify them"
    full-suite: "Complete analysis with all related A1 documents and ETSI standards"
    version-evolution: "Track schema changes and breaking changes across data model versions"
traceability:
  required-artifact: "ORAN/docs/feature_traceability_map.md"
  required-before-code-generation: true
  required-output-fields:
    - selected_trace_ids
    - mapped_todo_sections
    - mapped_code_scope
    - verification_targets
    - post_analysis_handoff_status
    - post_analysis_handoff_target
    - post_analysis_handoff_reason
  code-generation-gate: "Do not generate source code unless selected_trace_ids is non-empty and resolved against ORAN/docs/feature_traceability_map.md."
---

# A1 Technical Data Model (A1TD) Analysis Skill

## Purpose
Extract and interpret A1TD specification content to:
- Identify data structure definitions and relationships
- Map field types, constraints, and validation rules
- Extract enumeration values and allowed ranges
- Generate Pydantic models and database schemas
- Track schema evolution across versions
- Resolve data model references in API specifications

## Traceability Requirements

Before converting extracted data-model knowledge to source code, this skill must:

0. Map findings to Trace IDs in `ORAN/docs/feature_traceability_map.md` before proposing code changes.

1. Read `ORAN/docs/feature_traceability_map.md`.
2. Resolve extracted entities/fields/constraints to one or more Trace IDs.
3. Restrict generated file targets to mapped `Code Scope` entries.
4. Produce verification work from mapped `Verification` entries.
5. Block code generation if no traceable mapping exists.

## Post-Analysis Handoff Rules

When the analysis result is complete and the request continues into implementation/testing, this skill must:

1. Invoke `post-analysis-test-policy-orchestration` as a formal post-step.
2. Pass the trace-mapped implementation plan, selected Trace IDs, mapped code scope, and verification targets.
3. Keep the handoff fail-closed if the plan is incomplete or cannot be dispatched.
4. Record `post_analysis_handoff_status`, `post_analysis_handoff_target`, and `post_analysis_handoff_reason` in the analysis output.

Required conversion payload fields:

```yaml
selected_trace_ids: ["ORAN-FTM-002"]
mapped_todo_sections:
  - "Traceability and Quality Follow-up"
mapped_code_scope:
  - "demo-web/backend/app/services/a1_policy_service.py"
verification_targets:
  - "Unit tests for policy operations and constraints"
```

Hard gate:

- Do not emit source code unless `selected_trace_ids` is non-empty and resolved against `ORAN/docs/feature_traceability_map.md`.
- Do not propose code changes unless findings are mapped to Trace IDs in `ORAN/docs/feature_traceability_map.md`.

## Document Context
**Document:** A1 Technical Data Model (A1TD)  
**Domain:** Telecom Interface - Data Structure Definitions  
**Referenced In:** Section 4.1 of TS 103.987 (A1 Application Protocol)  
**Related Documents:**
- A1TP (Protocol/API definitions using this data model)
- A1GAP (Procedures that manipulate these data structures)
- ETSI TS 132 158 (Design patterns for data representation)

## Use When
- Analyzing new A1TD specification version
- Extracting data structure and field definitions
- Identifying constraint rules and validations
- Mapping to ORM/Pydantic models
- Processing schema version diffs
- Resolving data model references from A1TP endpoints
- Generating database schemas

## Key Extraction Patterns

### Entity/Object Definitions
```
PATTERN: "(Object|Entity|Message|Structure|Model|Class) <Name>"
EXTRACT:
  - entity_name: Name of data structure
  - parent_type: Base class or inheritance
  - description: Purpose/meaning
  - fields: List of field definitions
  - constraints: Rules/invariants
  - examples: Sample values
```

### Field Definitions
```
PATTERN: "<field_name> : <type> [constraints]"
EXTRACT:
  - field_name: Field identifier
  - field_type: Data type (int, string, enum, object, array)
  - required: Boolean (mandatory vs optional)
  - constraints: Validation rules (min/max, pattern, enum values)
  - default_value: Default if optional
  - cardinality: Single (1) vs collection (0..N, 1..N)
```

### Enumerations
```
PATTERN: "(enum|enumeration|values|options|choices)"
EXTRACT:
  - enum_name: Name of enumeration
  - values: List of allowed values
  - value_meanings: Description of each value
  - default_value: Default selection
  - extensibility: Fixed vs extensible set
```

### Type Constraints
```
PATTERN: "(minimum|maximum|length|pattern|format|regex|allowed)"
EXTRACT:
  - constraint_type: Type of validation
  - constraint_value: Specific value/rule
  - applies_to: Field name
  - error_message: Validation failure message
```

### Relationships
```
PATTERN: "(references|contains|aggregates|inherits|extends)"
EXTRACT:
  - relationship_type: Has-a, is-a, references
  - source_entity: Entity containing reference
  - target_entity: Referenced entity
  - cardinality: 1:1, 1:N, N:M
  - navigability: Bidirectional vs unidirectional
```

## Module Mapping Rules

### When to Enrich Modules
1. **models/analysis_models.py** - Data structure definitions
   - Create Pydantic dataclass for each entity
   - Define field validators
   - Add enum classes for allowed values
   - Include relationship mappings

2. **models/database_models.py** - Database schemas
   - Create SQLAlchemy models from entities
   - Define relationships and foreign keys
   - Add indexes on frequently queried fields
   - Include constraint definitions

3. **utils/validation.py** - Field validation
   - Implement constraint validators
   - Generate regex patterns from specifications
   - Create custom validators for complex rules
   - Range and length checkers

4. **serialization/schemas.py** - API schemas
   - Create request/response JSON schemas
   - Define field serialization rules
   - Map database to API representation
   - Handle nested object serialization

## Version Tracking

### Current Implementation Target
**Versions:** v1.0, v1.1, v1.2  
**Latest:** v1.2 (as of TS 103.987 v4.3.0)

### Version-Specific Changes
```yaml
v1.0:
  core_entities:
    - User: Basic user profile
    - Resource: Generic resource
    - Action: Operation audit log

v1.1:
  additions:
    - new_entities: [Policy, RoleBinding]
    - new_fields: [User.department, User.cost_center]
  deprecations:
    - fields: [User.legacy_id]
  modifications:
    - Resource.description: length 256 -> 512

v1.2:
  additions:
    - new_entities: [AuditLog, SecurityContext]
    - new_fields: [Resource.tags, User.mfa_enabled]
  breaking_changes:
    - User.status: [active, inactive] -> [active, inactive, suspended, archived]
```

## Interpretation Rules

### Confidence Scoring
- Formal table/schema definition: 0.95+
- Explicit field documentation: 0.85-0.95
- Implied from context: 0.70-0.85
- Optional/example data: 0.50-0.70

### Priority Ranking
1. **Critical:** Core entities, required fields, unique identifiers
2. **High:** Relationships, constraint rules, validations
3. **Medium:** Optional fields, enumerations, descriptions
4. **Low:** Examples, deprecated fields, future extensions

## Cross-Reference Resolution

When A1TD references other documents, extract:
- **Reference to A1TP:** This data model used as request/response in API endpoints
- **Reference to A1GAP:** Procedures that create/modify these entities
- **Reference to ETSI TS 132 158:** Data representation patterns to follow

## Extraction Output Structure

```python
A1TDAnalysis:
  document_version: str
  entities: List[Entity]
  enumerations: List[Enumeration]
  relationships: List[Relationship]
  constraints: List[Constraint]
  patterns: List[str]  # From ETSI reference
  version_diffs: Dict[str, List[SchemaChange]]
  api_endpoint_mappings: Dict[str, List[Entity]]  # From A1TP
  procedure_mappings: Dict[str, List[Entity]]  # From A1GAP
  module_suggestions: List[ModuleEnrichment]
  extraction_confidence: float
```

## Code Generation Suggestions

### When to Generate
- New entity → Generate Pydantic model with validators
- New enumeration → Generate Python enum class
- New relationship → Generate foreign key and relationship decorators
- New constraint → Generate custom Pydantic validator

### Generation Template
```python
# Generated from A1TD v1.2 specification
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime
from typing import Optional, List

class EntityNameEnum(str, Enum):
    """Enum from A1TD v1.2"""
    VALUE_A = "value_a"
    VALUE_B = "value_b"

class EntityModel(BaseModel):
    """
    Entity definition from A1TD v1.2 Spec
    See: [document-reference]
    Used in A1TP endpoints: [endpoint-refs]
    Modified by A1GAP procedures: [procedure-refs]
    """
    field_name: str = Field(
        ...,
        description="From A1TD specification",
        min_length=1,
        max_length=256
    )
    enum_field: EntityNameEnum
    optional_field: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('field_name')
    def validate_field_name(cls, v):
        # Constraint from A1TD specification
        if not v.isalnum():
            raise ValueError('Must be alphanumeric')
        return v

    class Config:
        # From ETSI TS 132 158 patterns
        schema_extra = {
            "example": {
                "field_name": "example",
                "enum_field": "value_a"
            }
        }
```

### Database Schema Generation
```python
# Generated SQLAlchemy model from A1TD
from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

class EntityTableModel(Base):
    """
    Database table from A1TD v1.2 Spec
    """
    __tablename__ = "entity_table"
    
    id = Column(Integer, primary_key=True)
    field_name = Column(String(256), nullable=False, unique=True)
    enum_field = Column(Enum(EntityNameEnum), nullable=False)
    optional_field = Column(String(256), nullable=True)
    
    # Relationships from A1TD
    related_entities = relationship(
        "RelatedEntityTableModel",
        foreign_keys=[RelatedEntityTableModel.entity_id]
    )
```

## Quality Validation

### Expected Extraction Ranges
- Entities per section: 2-8
- Fields per entity: 3-15
- Enumerations: 2-5 per version
- Constraints: 1-3 per field

### Schema Completeness
- Required fields defined: 100%
- Constraints documented: ≥80%
- Relationships mapped: 100%
- Examples provided: ≥60%

## Usage Example

```python
# Analyze A1TD v1.2 specification
from skill import analyze_a1td_specification

result = analyze_a1td_specification(
    document_path="C:/docs/a1td_v1.2.pdf",
    version="v1.2",
    target_modules=["models/analysis_models", "models/database_models"],
    compare_to_version="v1.1",  # Show schema evolution
    extract_relationships=True,
    extract_cross_references=True,
    generate_code_suggestions=True
)

# Result contains:
# - Extracted entities, fields, enumerations
# - Database schema suggestions
# - Version diff highlighting breaking changes
# - API endpoint usage (from A1TP cross-ref)
# - Procedure impacts (from A1GAP cross-ref)
```

## Impact Analysis

### Step 1: Identify Impacted Modules/Features

The skill automatically identifies which modules are affected by extracted data structures:

```python
Impacted Modules Analysis:

For each extracted entity:
  - Feature: Data Persistence
    Modules: models/database_models.py, services/repository_service.py
    Impact: DIRECT (new database tables/relationships)
    
  - Feature: API Request/Response Models
    Modules: models/request_models.py, models/response_models.py
    Impact: DIRECT (new Pydantic schemas)
    
  - Feature: Data Validation
    Modules: utils/validation.py, services/data_validator.py
    Impact: DIRECT (new field validators)
    
  - Feature: Database Migrations
    Modules: services/migration_service.py, alembic/versions/
    Impact: DIRECT (new schema migrations)
    
  - Feature: ORM Relationships
    Modules: models/database_models.py, utils/relationship_mapper.py
    Impact: MEDIUM (new entity relationships)
    
  - Feature: Serialization/Deserialization
    Modules: services/serialization_service.py, utils/json_encoder.py
    Impact: MEDIUM (new data structures to serialize)
```

### Step 2: Identify Files to Modify

The skill lists files requiring updates to implement new data structures:

```python
Files to Modify:

┌─ PYDANTIC/ORM MODELS ────────────────────┐
│                                           │
│ models/analysis_models.py                 │
│   Changes: Add 3 new Pydantic classes    │
│   Lines: Add User, Resource, Tag models  │
│   Priority: CRITICAL                      │
│                                           │
│ models/database_models.py                 │
│   Changes: Add 3 new SQLAlchemy models   │
│   Lines: Add User, Resource, Tag tables  │
│   Priority: CRITICAL                      │
│                                           │
│ models/request_models.py                  │
│   Changes: Add request schemas            │
│   Lines: Add CreateUserRequest, etc       │
│   Priority: CRITICAL                      │
│                                           │
│ models/response_models.py                 │
│   Changes: Add response schemas           │
│   Lines: Add UserResponse, etc            │
│   Priority: CRITICAL                      │
│                                           │
└─────────────────────────────────────────┘

┌─ VALIDATION & CONSTRAINTS ───────────────┐
│                                           │
│ utils/validation.py                       │
│   Changes: Add field validators           │
│   Lines: Add email validation, length     │
│   Priority: HIGH                          │
│                                           │
│ utils/constraint_validators.py            │
│   Changes: Add constraint checking        │
│   Lines: Add unique constraint validators │
│   Priority: HIGH                          │
│                                           │
└─────────────────────────────────────────┘

┌─ DATABASE & MIGRATIONS ──────────────────┐
│                                           │
│ alembic/versions/[new_timestamp].py      │
│   Changes: Create migration script        │
│   Lines: Add migration for new tables    │
│   Priority: CRITICAL                      │
│                                           │
│ services/repository_service.py            │
│   Changes: Add repository methods         │
│   Lines: Add CRUD for new entities       │
│   Priority: HIGH                          │
│                                           │
└─────────────────────────────────────────┘

┌─ DOCUMENTATION & CONFIG ─────────────────┐
│                                           │
│ docs/data_model_reference.md              │
│   Changes: Document new entities         │
│   Scope: Add entity descriptions          │
│   Priority: MEDIUM                        │
│                                           │
│ config/database_config.json               │
│   Changes: Add table mappings             │
│   Lines: Add entity-to-table mappings    │
│   Priority: MEDIUM                        │
│                                           │
└─────────────────────────────────────────┘
```

### Step 3: Identify Tests to Modify/Create

The skill identifies comprehensive test requirements for new data models:

```python
Tests to Create/Modify:

┌─ NEW TEST FILES ─────────────────────────┐
│                                           │
│ tests/test_pydantic_models_section_5.py  │
│   Type: Pydantic model validation tests  │
│   Test Cases:                             │
│     - test_user_model_creation           │
│     - test_user_required_fields          │
│     - test_user_email_validation         │
│     - test_resource_model_creation       │
│     - test_tag_model_constraints         │
│   Total Test Cases: 15                   │
│   Priority: CRITICAL                     │
│                                           │
│ tests/test_database_models_section_5.py  │
│   Type: SQLAlchemy ORM tests             │
│   Test Cases:                             │
│     - test_user_table_creation           │
│     - test_user_relationships            │
│     - test_unique_constraints            │
│     - test_foreign_keys                  │
│   Total Test Cases: 12                   │
│   Priority: CRITICAL                     │
│                                           │
│ tests/test_migrations_section_5.py       │
│   Type: Database migration tests         │
│   Test Cases:                             │
│     - test_forward_migration             │
│     - test_downgrade_migration           │
│     - test_data_integrity_post_migration │
│   Total Test Cases: 5                    │
│   Priority: HIGH                         │
│                                           │
│ tests/test_constraints_section_5.py      │
│   Type: Data constraint validation       │
│   Test Cases:                             │
│     - test_unique_email_constraint       │
│     - test_required_field_enforcement    │
│     - test_type_coercion                 │
│   Total Test Cases: 8                    │
│   Priority: HIGH                         │
│                                           │
└─────────────────────────────────────────┘

┌─ MODIFY EXISTING TEST FILES ─────────────┐
│                                           │
│ tests/test_models.py                     │
│   Changes: Add new model test cases      │
│   Lines: Add parametrized tests          │
│   Priority: HIGH                         │
│                                           │
│ tests/test_validation.py                 │
│   Changes: Add field validators tests    │
│   Lines: Add validator test cases        │
│   Priority: HIGH                         │
│                                           │
│ tests/integration/test_orm.py            │
│   Changes: Add ORM integration tests     │
│   Lines: Add end-to-end ORM tests        │
│   Priority: MEDIUM                       │
│                                           │
└─────────────────────────────────────────┘
```

### Impact Summary Report

The skill generates structured impact analysis:

```python
Impact Assessment Output:

{
  "document_version": "v1.2",
  "section_analyzed": "5",
  "extraction_summary": {
    "entities_found": 5,
    "fields_total": 28,
    "relationships": 6,
    "enumerations": 3,
    "constraints": 12
  },
  "module_impact": {
    "high_impact": [
      "models/analysis_models.py",
      "models/database_models.py",
      "alembic/versions/"
    ],
    "medium_impact": [
      "utils/validation.py",
      "services/repository_service.py"
    ]
  },
  "files_to_modify": {
    "pydantic_models": 2,
    "orm_models": 1,
    "request_response_schemas": 2,
    "validators": 2,
    "migrations": 1,
    "test_files": 8
  },
  "test_requirements": {
    "new_test_files": 4,
    "tests_to_create": 40,
    "existing_files_to_update": 3
  },
  "database_impact": {
    "new_tables": 5,
    "new_indexes": 8,
    "new_relationships": 6,
    "migration_required": true
  },
  "implementation_effort": {
    "estimated_hours": 16,
    "critical_priority": 8,
    "high_priority": 6,
    "medium_priority": 3
  },
  "risk_assessment": "MEDIUM - Database migrations must be carefully tested",
  "recommendation": "Create comprehensive ORM + migration tests before production deployment"
}
```

## Integration with Central Analysis

This skill is called by:
1. **Local Analysis:** When user requests A1TD analysis
2. **Cross-Reference Analysis:** When A1TP/A1GAP reference data models
3. **Schema Evolution:** When analyzing version diffs for breaking changes
4. **API Generation:** When creating API models from endpoint specs

The `document-cross-reference-analysis` skill orchestrates this skill's execution in dependency order.

## Related Skills
- `document-analysis-a1tp` - Analyze protocol definitions using this data
- `document-analysis-a1gap` - Analyze procedures that modify this data
- `document-analysis-etsi-ts-132-158` - Analyze design patterns for data representation
- `document-cross-reference-analysis` - Handle inter-document dependencies
