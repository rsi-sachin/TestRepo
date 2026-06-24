---
name: document-analysis-a1gap
description: "Analyze A1 Gap Analysis Protocol specifications. Extract procedures, policy rules, state machines, and business logic. Generate workflow definitions and policy enforcement code. Track procedural changes across versions."
domain: "A1 Interface Procedures & Policies"
document-family: "A1GAP"
versions: ["v1.0", "v1.1", "v1.2"]
argument-hint: "procedure name or policy type to analyze"
user-invocable: true
related-skills:
  - document-cross-reference-analysis
  - document-analysis-a1tp
  - document-analysis-a1td
configuration:
  ask-user-for-mode: true
  supported-modes:
    - single
    - dependencies
    - full-suite
    - version-evolution
  mode-descriptions:
    single: "Analyze procedures and policies in this specification alone"
    dependencies: "Include API endpoints that trigger procedures and data entities affected"
    full-suite: "Complete analysis with all related A1 documents and ETSI standards"
    version-evolution: "Track procedure changes and breaking changes across policy versions"
---

# A1 Gap Analysis Protocol (A1GAP) Analysis Skill

## Purpose
Extract and interpret A1GAP specification content to:
- Identify business procedures and workflows
- Extract policy rules and decision logic
- Map state machines and transitions
- Identify error handling and recovery procedures
- Generate workflow engine definitions
- Track procedure evolution across versions
- Resolve procedure references from API/data model specs

## Document Context
**Document:** A1 Gap Analysis Protocol (A1GAP)  
**Domain:** Telecom Interface - Procedures & Policy Rules  
**Referenced In:** Section 4.1 of TS 103.987 (A1 Application Protocol)  
**Related Documents:**
- A1TP (API endpoints that trigger these procedures)
- A1TD (Data entities affected by procedures)
- ETSI TS 132 158 (Process design patterns)

## Use When
- Analyzing new A1GAP specification version
- Extracting business procedures and workflows
- Identifying policy rules and constraints
- Mapping state machines and transitions
- Processing procedural changes vs previous version
- Generating workflow execution logic
- Enforcing policy constraints in code
- Resolving procedure calls from A1TP endpoints

## Key Extraction Patterns

### Procedures/Workflows
```
PATTERN: "(procedure|process|workflow|operation) <Name>"
EXTRACT:
  - procedure_name: Name identifier
  - triggers: Events/conditions that start procedure
  - steps: Ordered sequence of actions
  - inputs: Required parameters/preconditions
  - outputs: Results/postconditions
  - error_handling: Failure scenarios and recovery
  - duration: Expected execution time
```

### Policy Rules
```
PATTERN: "(policy|rule|constraint|requirement) <Name>"
EXTRACT:
  - rule_name: Rule identifier
  - condition: Triggering condition (if/when)
  - action: Result/enforcement action
  - scope: Which entities/roles affected
  - priority: Rule precedence
  - exceptions: Cases where rule doesn't apply
```

### State Machines
```
PATTERN: "(state|status) (transition|change|moves)"
EXTRACT:
  - entity: What changes state
  - states: List of valid states
  - transitions: State changes
  - guards: Conditions for transitions
  - actions: Side effects of transitions
  - initial_state: Starting state
  - final_states: End states
```

### Decision Logic
```
PATTERN: "(if|when|unless|case|switch|match)"
EXTRACT:
  - condition: Decision point
  - branches: Possible outcomes
  - logic: Evaluation criteria
  - default: Fallback behavior
```

### Error Scenarios
```
PATTERN: "(error|fail|exception|invalid|timeout|retry)"
EXTRACT:
  - error_type: Category of failure
  - trigger: What causes this error
  - impact: Consequences
  - recovery: How to recover
  - notification: Who/what to alert
```

## Module Mapping Rules

### When to Enrich Modules
1. **services/workflow_engine.py** - Procedure execution
   - Create workflow executor for each procedure
   - Implement state machine transitions
   - Add action handlers for procedure steps
   - Include error recovery logic

2. **services/policy_enforcer.py** - Policy rules
   - Implement policy rule evaluators
   - Create constraint validators
   - Add audit logging for policy enforcement
   - Include exception handlers

3. **models/state_machine.py** - State definitions
   - Define state enums for each entity type
   - Create transition validators
   - Map guards and conditions
   - Include state metadata

4. **services/error_handler.py** - Error scenarios
   - Create error type definitions
   - Implement recovery strategies
   - Add retry logic and backoff
   - Generate error notifications

## Version Tracking

### Current Implementation Target
**Versions:** v1.0, v1.1, v1.2  
**Latest:** v1.2 (as of TS 103.987 v4.3.0)

### Version-Specific Changes
```yaml
v1.0:
  procedures:
    - CreateResource: Basic create workflow
    - UpdateResource: Simple update procedure
    - DeleteResource: Removal workflow
  policies:
    - AuthenticationRequired: All APIs need auth
    - RateLimitPolicy: 1000 req/hour default

v1.1:
  additions:
    - procedures: [BulkCreateResource, AsyncDeleteResource]
    - policies: [DataValidationPolicy, AuditLoggingPolicy]
  modifications:
    - CreateResource: Add step for tag assignment
    - RateLimitPolicy: Per-user limit vs global

v1.2:
  additions:
    - procedures: [TransactionRollback, CompensatingTransaction]
    - policies: [CachingPolicy, ConcurrencyPolicy]
  breaking_changes:
    - DeleteResource: Now requires audit reason parameter
    - ErrorRecovery: Automatic retry changed from 3 to 5 attempts
```

## Interpretation Rules

### Confidence Scoring
- Explicit procedural steps with preconditions: 0.95+
- Clearly defined policies with rules: 0.85-0.95
- State machine diagrams: 0.90+
- Implied procedures from examples: 0.65-0.80
- Procedural descriptions: 0.75-0.85

### Priority Ranking
1. **Critical:** Main workflows, critical policies, required procedures
2. **High:** Error handling, state transitions, constraints
3. **Medium:** Optional procedures, performance policies
4. **Low:** Historical context, deprecated procedures, examples

## Cross-Reference Resolution

When A1GAP references other documents, extract:
- **Reference to A1TP:** Which API endpoints trigger which procedures
- **Reference to A1TD:** Which data entities are created/modified by procedures
- **Reference to ETSI TS 132 158:** Process design patterns and workflow styles

## Extraction Output Structure

```python
A1GAPAnalysis:
  document_version: str
  procedures: List[Procedure]
  policies: List[Policy]
  state_machines: List[StateMachine]
  error_scenarios: List[ErrorScenario]
  decision_trees: List[DecisionTree]
  design_patterns: List[str]  # From ETSI reference
  version_diffs: Dict[str, List[ProcedureChange]]
  api_endpoint_triggers: Dict[str, List[Procedure]]  # From A1TP
  data_entity_impacts: Dict[str, List[Procedure]]  # From A1TD
  module_suggestions: List[ModuleEnrichment]
  extraction_confidence: float
```

## Code Generation Suggestions

### When to Generate
- New procedure → Generate workflow executor skeleton
- New policy → Generate policy enforcer/validator
- New state machine → Generate state transition handler
- New error scenario → Generate error handler with recovery

### Generation Template - Procedure
```python
# Generated from A1GAP v1.2 specification
from typing import Dict, Any, List
from enum import Enum
from datetime import datetime

class ProcedureName:
    """
    Procedure from A1GAP v1.2 Spec
    See: [document-reference]
    Triggered by A1TP endpoints: [endpoint-refs]
    Affects A1TD entities: [entity-refs]
    """
    
    class Step(Enum):
        VALIDATE_INPUT = "validate"
        PREPARE_DATA = "prepare"
        EXECUTE_ACTION = "execute"
        UPDATE_STATE = "update"
        NOTIFY_COMPLETION = "notify"

    def __init__(self, input_data: Dict[str, Any]):
        self.input = input_data
        self.current_step = self.Step.VALIDATE_INPUT
        self.state = {}
        self.errors = []

    def validate_input(self) -> bool:
        """Validate preconditions from A1GAP spec"""
        # Constraints from specification
        if not self.input.get('required_field'):
            self.errors.append("Missing required_field")
            return False
        return True

    def prepare_data(self) -> bool:
        """Prepare and transform data"""
        # Transformations from A1GAP
        self.state['prepared'] = True
        return True

    def execute_action(self) -> bool:
        """Execute main action"""
        # Business logic from A1GAP spec
        return True

    def update_state(self) -> bool:
        """Update entity state"""
        # State transitions from A1GAP state machine
        return True

    def execute(self) -> Dict[str, Any]:
        """Execute full procedure"""
        steps = [
            (self.Step.VALIDATE_INPUT, self.validate_input),
            (self.Step.PREPARE_DATA, self.prepare_data),
            (self.Step.EXECUTE_ACTION, self.execute_action),
            (self.Step.UPDATE_STATE, self.update_state),
        ]
        
        for step, handler in steps:
            self.current_step = step
            try:
                if not handler():
                    raise Exception(f"Step {step} failed")
            except Exception as e:
                return self.handle_error(e)
        
        return {"status": "success", "result": self.state}

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Error recovery from A1GAP spec"""
        # Recovery logic per specification
        return {"status": "error", "message": str(error)}
```

### Generation Template - Policy
```python
# Generated from A1GAP v1.2 specification
from abc import ABC, abstractmethod
from typing import Any, Dict

class PolicyName(ABC):
    """
    Policy from A1GAP v1.2 Spec
    See: [document-reference]
    Priority: [priority-level]
    """

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate policy condition"""
        pass

    @abstractmethod
    def enforce(self, context: Dict[str, Any]) -> None:
        """Enforce policy action"""
        pass

class AuthenticationPolicy(PolicyName):
    """Authentication required for all operations"""
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        # Rule from A1GAP: "All API requests must include valid authentication"
        return context.get('user') is not None and context['user'].is_authenticated

    def enforce(self, context: Dict[str, Any]) -> None:
        if not self.evaluate(context):
            raise AuthenticationRequired("User must be authenticated")
```

## Quality Validation

### Expected Extraction Ranges
- Procedures per section: 2-6
- Policies per version: 5-15
- State machines: 3-8
- Error scenarios: 5-20
- Decision points: 10-30

### Completeness Checklist
- Procedures have clear inputs/outputs: ≥90%
- Policies have explicit conditions: 100%
- State machines have defined transitions: 100%
- Error scenarios have recovery actions: ≥80%

## Usage Example

```python
# Analyze A1GAP v1.2 specification
from skill import analyze_a1gap_specification

result = analyze_a1gap_specification(
    document_path="C:/docs/a1gap_v1.2.pdf",
    version="v1.2",
    target_modules=["services/workflow_engine", "services/policy_enforcer"],
    compare_to_version="v1.1",  # Show procedural changes
    extract_procedures=True,
    extract_policies=True,
    extract_state_machines=True,
    extract_cross_references=True,
    generate_code_suggestions=True
)

# Result contains:
# - Extracted procedures and state machines
# - Policy rules and constraints
# - Workflow execution logic suggestions
# - Version diff highlighting breaking changes
# - API endpoint triggers (from A1TP cross-ref)
# - Data entity impacts (from A1TD cross-ref)
```

## Integration with Central Analysis

This skill is called by:
1. **Local Analysis:** When user requests A1GAP analysis
2. **Cross-Reference Analysis:** When A1TP/A1TD reference procedures
3. **Workflow Generation:** When creating execution workflows
4. **Policy Update:** When policy rules need enforcement

The `document-cross-reference-analysis` skill orchestrates this skill's execution with dependency awareness.

## Related Skills
- `document-analysis-a1tp` - Analyze API endpoints that trigger procedures
- `document-analysis-a1td` - Analyze data entities affected by procedures
- `document-analysis-etsi-ts-132-158` - Analyze workflow design patterns
- `document-cross-reference-analysis` - Handle inter-document dependencies and orchestration
