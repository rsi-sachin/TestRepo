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
