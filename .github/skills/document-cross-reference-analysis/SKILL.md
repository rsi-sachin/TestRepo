---
name: document-cross-reference-analysis
description: "Orchestrate analysis of interconnected A1 documents. Resolve cross-references, extract overlapping information, map dependencies, and generate unified enrichment recommendations. Detect conflicts and prioritize implementation."
domain: "A1 Interface Unified Analysis"
document-family: "A1 Reference Set"
versions: ["v1.0"]
argument-hint: "analysis scope (single, dependencies, full-suite, version-evolution)"
user-invocable: true
master-skill: true
orchestrates:
  - document-analysis-a1tp
  - document-analysis-a1td
  - document-analysis-a1gap
  - document-analysis-etsi-ts-132-158
configuration:
  ask-user-for-mode: true
  default-mode: single
  post-analysis-handoff:
    target-skill: post-analysis-test-policy-orchestration
    trigger: "after cross-reference analysis completes and follow-up implementation/testing is requested"
    fail-closed-if-skipped: true
  implicit-prompt-routing:
    - prompt-pattern: "Analyze sections <section-list> from <document-path>"
      inferred-primary-skill: document-analysis-a1tp
      inferred-orchestrator-skill: document-cross-reference-analysis
      inferred-mode: single
      inferred-extraction-focus:
        - http
        - rest
        - resource
        - status code
        - authentication
      inferred-section-selection:
        skip-first-section-match: true
        use-body-section-text: true
      inferred-output-requirements:
        - map findings to existing tests and code
        - generate a trace-mapped implementation gap list for section 5
        - generate a test matrix showing exactly which section 5 clauses are already covered and which are missing
        - list new tests
        - list modified tests
        - list implementation and coverage gaps
    - prompt-pattern: "Analyze section 6 from <document-path>"
      inferred-primary-skill: document-analysis-a1tp
      inferred-orchestrator-skill: document-cross-reference-analysis
      inferred-mode: single
      inferred-extraction-focus:
        - http
        - rest
        - resource
        - status code
        - authentication
        - conformance test cases
      inferred-section-selection:
        skip-first-section-match: true
        use-body-section-text: true
      inferred-output-requirements:
        - map each section 6 subclause to existing ORAN trace IDs and test files
        - generate a clause-to-test matrix for all analyzed section 6 clauses
        - identify direct coverage, partial coverage, and coverage gaps
        - list new tests
        - list modified tests
        - list implementation and coverage gaps
  supported-modes:
    - single
    - dependencies
    - full-suite
    - version-evolution
  mode-descriptions:
    single: "Analyze one document and identify external references"
    dependencies: "Automatically resolve dependencies and gather context from referenced documents"
    full-suite: "Analyze all A1 documents (A1TP, A1TD, A1GAP) together with complete cross-referencing"
    version-evolution: "Compare document versions to identify breaking changes and schema evolution"
  section-selection-defaults:
    skip-first-section-match: true
    rationale: "The first section-name/ID match is often from Table of Contents; prefer body headings by default."
  routing-gate:
    protocol-markers:
      - http
      - rest
      - endpoint
      - uri
      - resource
      - status code
      - authentication
      - authorization
    required-sub-skill: document-analysis-a1tp
    fail-closed: true
    failure-action: "Stop and report missing required sub-skill selection before continuing analysis."
  required-analysis-output-fields:
    - selected_primary_skill
    - selected_secondary_skills
    - why_selected
    - protocol_markers_detected
    - post_analysis_handoff_status
    - post_analysis_handoff_target
    - post_analysis_handoff_reason
traceability:
  required-artifact: "ORAN/docs/feature_traceability_map.md"
  required-before-code-generation: true
  required-output-fields:
    - selected_trace_ids
    - mapped_todo_sections
    - mapped_code_scope
    - verification_targets
    - implementation_plan
  code-generation-gate: "Do not generate source code unless selected_trace_ids is non-empty and resolved against ORAN/docs/feature_traceability_map.md."
---

# Document Cross-Reference Analysis Skill

## Purpose
Orchestrate intelligent analysis of interconnected A1-related documents to:
- Resolve cross-references between documents
- Extract and consolidate overlapping information
- Identify and map dependencies between documents
- Detect conflicts and inconsistencies
- Generate unified module enrichment recommendations
- Prioritize implementation based on dependencies
- Track version evolution across document set
- Validate conformance to industry standards (ETSI)

## Traceability Requirements

Before converting analysis knowledge into source code, this skill must:

0. Map findings to Trace IDs in `ORAN/docs/feature_traceability_map.md` before proposing code changes.

1. Read `ORAN/docs/feature_traceability_map.md`.
2. Select one or more matching Trace IDs for the requested implementation.
3. Map recommendations to TODO sections and code scopes listed in the traceability map.
4. Produce explicit verification targets from the `Verification` column.
5. Stop code generation if no Trace ID mapping is available.
6. When the trace-mapped plan is complete, hand it off as the implementation input and do not start production code edits until that plan exists.
7. After analysis completion, invoke `post-analysis-test-policy-orchestration` as a formal post-step whenever implementation, testing, or coverage closure is requested.

## Post-Analysis Handoff Rules

When this orchestrator finishes analysis and the request continues into implementation/testing, it must:

1. Invoke `post-analysis-test-policy-orchestration` using the latest analysis artifact or trace-mapped implementation plan.
2. Include selected Trace IDs, mapped TODO sections, mapped code scope, and verification targets in the handoff payload.
3. Preserve fail-closed behavior: if the handoff cannot be dispatched, mark the analysis result as incomplete rather than complete.
4. Emit `post_analysis_handoff_status`, `post_analysis_handoff_target`, and `post_analysis_handoff_reason` in the analysis output.

Required conversion payload fields:

```yaml
selected_trace_ids: ["ORAN-FTM-001"]
mapped_todo_sections:
  - "Traceability and Quality Follow-up"
mapped_code_scope:
  - "demo-web/backend/app/services/a1_service_registry.py"
verification_targets:
  - "API regression tests for service-aware flows"
```

Hard gate:

- Do not emit source code unless `selected_trace_ids` is non-empty and resolved against `ORAN/docs/feature_traceability_map.md`.
- Do not propose code changes unless findings are mapped to Trace IDs in `ORAN/docs/feature_traceability_map.md`.

## Required Skill Routing Gate

Before analysis begins, this skill must classify request content and select sub-skills with fail-closed behavior.

- If protocol markers are detected (HTTP/REST/endpoints/resources/status codes/authentication), `document-analysis-a1tp` is mandatory.
- Cross-reference orchestration may continue only after the mandatory sub-skill is selected.
- If mandatory selection is missing, stop and report routing failure rather than continuing with partial analysis.

Required routing audit fields in every analysis response:

```yaml
selected_primary_skill: "document-analysis-a1tp"
selected_secondary_skills: ["document-cross-reference-analysis"]
why_selected: "Protocol markers detected in request and document section"
protocol_markers_detected: ["HTTP", "REST", "resource"]
```

## Implicit Prompt Defaults

When the user prompt matches `Analyze sections <section-list> from <document-path>`:

- Treat it as protocol-centric technical analysis by default.
- Auto-select `document-analysis-a1tp` as primary skill.
- Use `document-cross-reference-analysis` in `single` mode unless the user explicitly requests dependencies/full-suite/version-evolution.
- Apply section-selection policy to skip TOC match and use body section text.
- Always include mapping to existing tests/code and report:
  - new tests,
  - modified tests,
  - implementation/coverage gaps.

## Document Ecosystem

### Document Map
```
┌─────────────────────────────────────────────┐
│  ETSI TS 132 158 (Design Standards)        │
│  ↓ defines standards and patterns for ↓    │
├─────────────────────────────────────────────┤
│                                              │
│  A1TP ←─┐  A1TD ←─┐  A1GAP ←─┐            │
│  (REST) │ (Data)  │ (Procs)  │            │
│    ↓    └─────────┴────────┬─┘            │
│    └────────────────────────┘              │
│         (interdependent)                   │
│                                              │
└─────────────────────────────────────────────┘

A1TP (Protocol):
  - Defines REST API endpoints
  - References A1TD for request/response schemas
  - References A1GAP for procedure triggers
  - Must comply with ETSI patterns

A1TD (Data Model):
  - Defines entity structures
  - Used by A1TP endpoints
  - Used by A1GAP procedures
  - Must follow ETSI naming conventions

A1GAP (Procedures):
  - Defines workflows and state machines
  - Triggered by A1TP endpoints
  - Modifies A1TD entities
  - Must follow ETSI process patterns

ETSI TS 132 158 (Standards):
  - Cross-cutting standards for all above
  - Defines REST patterns
  - Establishes naming conventions
  - Sets architecture best practices
```

### Dependency Types

**Strong Dependency** (A → B: A cannot be implemented without B)
- A1TP → A1TD: API endpoints need data models
- A1TP → A1GAP: Endpoints trigger procedures
- A1GAP → A1TD: Procedures modify entities

**Weak Dependency** (A → B: A is enhanced by B, but can exist alone)
- All → ETSI: Code should follow standards, but basic functionality works without

**Conflict** (A ≠ B: Statements contradict)
- Same field defined differently in A1TD vs A1TP
- Procedure in A1GAP conflicts with API behavior in A1TP
- ETSI standard violated by A1TD entity

## Analysis Modes

## Section Selection Policy (Default)

When a user asks to analyze specific section IDs or section names:

1. Find all heading matches for each requested section token (for example, `4.1`, `7.3.2`, `Policy Lifecycle`).
2. Skip the first match by default.
3. Treat that first match as likely Table of Contents/navigation content.
4. Use the next matching heading from body pages as the analysis target.
5. If multiple body matches remain, prefer exact section-ID + title matches over partial matches.
6. If no body match exists after skipping the first match, report ambiguity and ask for confirmation before analyzing TOC text.

Heuristics for non-body matches:
- Ignore matches inside sections titled `Table of Contents` or `Contents`.
- Ignore matches that are list-only entries with page numbers and no substantive paragraph content.

### Mode 1: Single Document Analysis
Analyze one document in isolation, then check for references.

```
Input: analyze_document("A1TP", "v1.2", sections=["4.1"])
Output:
  - Extracted facts from document
  - Cross-references found [A1TD, A1GAP, ETSI]
  - Suggestions for related documents to analyze
  - Preliminary module enrichments (standalone)
```

### Mode 2: Dependency Chain Analysis
Analyze one document, then follow its dependencies.

```
Input: analyze_with_dependencies("A1TP", "v1.2", depth=2)
Process:
  1. Analyze A1TP v1.2
  2. Find references to A1TD, A1GAP
  3. Analyze A1TD, A1GAP
  4. Find references to ETSI
  5. Analyze ETSI patterns
Output:
  - Unified facts from all 4 documents
  - Dependency map showing relationships
  - Module enrichments with full context
  - Conflict detection
  - Implementation priority based on dependencies
```

### Mode 3: Full Suite Analysis
Analyze all documents together, resolving all cross-references.

```
Input: analyze_full_suite("all", latest_version=True)
Process:
  1. Analyze A1TP, A1TD, A1GAP (parallel where possible)
  2. Analyze ETSI patterns
  3. Cross-reference all documents
  4. Build comprehensive dependency graph
  5. Detect conflicts
  6. Validate ETSI compliance
  7. Generate unified recommendations
Output:
  - Global information index populated
  - Dependency matrix
  - Conflict resolution recommendations
  - Complete module enrichment plan
  - Implementation roadmap
  - Code generation templates (pattern-compliant)
```

### Mode 4: Version Evolution Analysis
Track changes across document versions, identifying impact.

```
Input: analyze_version_diff("all", from_version="v1.1", to_version="v1.2")
Process:
  1. Analyze both versions
  2. Identify breaking changes
  3. Assess impact on implementations
  4. Track procedure changes
  5. Map data model migrations
Output:
  - Breaking changes list
  - API endpoint deprecations
  - Data migration requirements
  - Procedure modifications
  - Backward compatibility assessment
  - Migration implementation guide
```

## Key Workflows

### Workflow 1: Resolve Cross-References

**Trigger:** When analyzing document X that references document Y

```
Process:
  1. Identify reference in X (e.g., "A1TD [4]")
  2. Locate referenced section in Y
  3. Extract relevant content from Y
  4. Map connection in dependency graph
  5. Check for conflicts between X and Y
  6. Validate ETSI compliance of both
  7. Add to unified index
  
Output:
  - Cross-reference resolved
  - Context from both documents
  - Any conflicts flagged
  - Combined recommendations
```

### Workflow 2: Extract Overlapping Information

**Trigger:** Same information mentioned in multiple documents

```
Example Overlap:
  A1TP says: "Authentication uses Bearer tokens"
  A1GAP says: "Security procedures enforce Bearer token validation"
  ETSI says: "Standard pattern for auth: Bearer tokens per RFC 6750"

Process:
  1. Identify same concept in multiple docs
  2. Compare statements for consistency
  3. Detect if one is more authoritative
  4. Consolidate into single fact
  5. Track provenance (which docs mention it)
  6. Assess confidence (more mentions = higher confidence)
  
Output:
  - Single consolidated fact
  - Multiple sources cited
  - Higher confidence score (corroboration)
  - Implementation notes from all sources
```

### Workflow 3: Dependency-Based Implementation Order

**Trigger:** Need to prioritize module enrichments

```
Dependency Chain Analysis:
  A1TP endpoint → needs → A1TD data model
                        → needs → Validation from ETSI
                        → triggers → A1GAP procedure
                                   → needs → A1TD state update
                                   → follows → ETSI patterns

Implementation Order:
  1. ETSI patterns (foundation)
  2. A1TD data models (most depended-on)
  3. A1GAP procedures (state management)
  4. A1TP endpoints (public interface, depends on all above)
  5. Integration and testing

Output:
  - Ordered implementation plan
  - Rationale for each ordering decision
  - Code generation order
  - Testing dependencies
```

### Workflow 4: Conflict Detection and Resolution

**Trigger:** Inconsistent information across documents

```
Example Conflict:
  A1TD says: "userId field is required"
  A1TP says: "userId is optional in request"
  A1GAP says: "Procedures require userId for audit"

Process:
  1. Flag conflict
  2. Assess severity (low/medium/high)
  3. Identify affected modules
  4. Determine authoritative source (usually ETSI, then primary doc)
  5. Propose resolution
  6. Require user confirmation
  
Output:
  - Conflict report
  - Severity assessment
  - Proposed resolution
  - Downstream impacts
  - Implementation notes
```

## Extraction Output Structure

```python
CrossReferenceAnalysis:
  analysis_mode: str  # single, dependencies, full_suite, version_evolution
  timestamp: datetime
  document_set: List[str]  # [A1TP, A1TD, A1GAP, ETSI]
  versions: Dict[str, str]  # {A1TP: v1.2, A1TD: v1.2, ...}
  
  # Core findings
  cross_references: List[CrossReference]
  overlapping_facts: List[OverlappingFact]
  dependency_graph: DependencyGraph
  conflicts: List[Conflict]
  etsi_compliance_status: Dict[str, ComplianceLevel]
  
  # Consolidated findings
  unified_global_facts: List[GlobalFact]
  consolidated_module_suggestions: List[ModuleEnrichment]
  implementation_roadmap: ImplementationRoadmap
  
  # Analysis metadata
  confidence_scores: Dict[str, float]
  ambiguities_flagged: List[Ambiguity]
  recommendations: List[Recommendation]
  extraction_confidence: float
```

### Cross-Reference Object
```python
CrossReference:
  from_document: str  # A1TP
  from_section: str   # 4.1
  reference_text: str  # "A1TD [4]"
  to_document: str    # A1TD
  to_section: str     # 5.2
  reference_type: str  # "data-model", "procedure", "pattern", "example"
  context: str        # Surrounding text
  resolution: str     # Resolved content/location
```

### Overlapping Fact Object
```python
OverlappingFact:
  concept: str  # "Bearer token authentication"
  mentioned_in: List[str]  # [A1TP, A1GAP, ETSI]
  statements: Dict[str, str]  # {A1TP: "uses Bearer tokens", ...}
  consistency: str  # "consistent", "conflicting", "complementary"
  unified_description: str  # Consolidated description
  confidence: float  # Higher if mentioned in multiple docs
```

### Conflict Object
```python
Conflict:
  conflict_id: str
  type: str  # "contradiction", "mismatch", "incompleteness"
  documents_involved: List[str]  # [A1TD, A1TP]
  statements: Dict[str, str]
  severity: str  # low, medium, high
  affected_modules: List[str]
  proposed_resolution: str
  requires_user_decision: bool
```

### Dependency Graph
```python
DependencyGraph:
  nodes: List[DocumentNode]  # A1TP, A1TD, A1GAP, ETSI
  edges: List[Dependency]
  
  def get_topological_sort() -> List[str]:
      """Implementation order respecting all dependencies"""
  
  def get_dependents(doc: str) -> List[str]:
      """Which docs depend on this one?"""
  
  def get_dependencies(doc: str) -> List[str]:
      """Which docs does this one depend on?"""
```

### Implementation Roadmap
```python
ImplementationRoadmap:
  phases: List[Phase]  # Ordered phases
  
class Phase:
  phase_number: int
  name: str  # "Foundation: Data Models"
  documents: List[str]  # Which docs addressed in this phase
  modules_to_enrich: List[str]
  code_to_generate: List[str]
  estimated_effort: str  # "1-2 weeks", "2-5 days"
  dependencies_satisfied: bool
  success_criteria: List[str]
```

## Usage Examples

### Example 1: Single Document with References
```python
result = analyze_document_with_references(
    document="A1TP",
    version="v1.2",
    sections=["4.1"],
  trace_references=True,
  skip_first_section_match=True
)

# Outputs:
# - A1TP Section 4.1 analysis
# - References found: [A1TD v1.2 section 5.2, A1GAP v1.2 section 3.4, ...]
# - Suggestion: "Analyze A1TD and A1GAP for complete context"
# - Preliminary module suggestions (standalone)
```

### Example 2: Full Suite with Dependency Resolution
```python
result = analyze_full_document_suite(
    mode="full_suite",
    versions="latest",
    resolve_dependencies=True,
    validate_etsi_compliance=True,
    detect_conflicts=True,
    generate_roadmap=True
)

# Outputs unified analysis:
# - Global information index populated
# - 12 cross-references resolved
# - 5 overlapping facts consolidated
# - 2 conflicts detected (severity: medium, high)
# - ETSI compliance: A1TP 95%, A1TD 87%, A1GAP 91%
# - 4-phase implementation roadmap
# - Code generation priorities
```

### Example 3: Version Diff with Impact Assessment
```python
result = analyze_version_differences(
    from_version="v1.1",
    to_version="v1.2",
    assess_impact=True,
    generate_migration=True
)

# Outputs:
# - 8 breaking changes identified
# - A1TP: New endpoints [POST /resources/async, ...]
# - A1TD: userId now required (was optional)
# - A1GAP: Rollback procedure added
# - A1TD data migration script needed
# - Backward compatibility: 70% (some old clients will break)
# - Migration guide generated
```

## Integration Points

### When This Skill is Invoked

1. **User requests:** "Analyze full A1 specification set"
   → Triggers Mode 3 (Full Suite)

2. **Document-specific skill:** References A1TD while analyzing A1TP
   → Invokes cross-reference resolution

3. **New document version:** "Process A1TP v1.3"
   → Triggers Mode 4 (Version Evolution) comparing to v1.2

4. **Agent planning:** "What needs implementation for A1 support?"
   → Triggers Mode 3 with implementation roadmap

### Called By
- User: "Analyze A1 documents"
- Agents: When processing any A1-related document
- System: When new document version detected

### Calls To
- document-analysis-a1tp
- document-analysis-a1td
- document-analysis-a1gap
- document-analysis-etsi-ts-132-158

## Quality Metrics

### Cross-Reference Resolution
- References found: 100%
- References resolved: ≥95%
- False positives: <5%
- Reference accuracy: ≥90%

### Conflict Detection
- Actual conflicts caught: ≥95%
- False positives: <10%
- Severity assessment accuracy: ≥85%

### Implementation Roadmap
- Dependency ordering correct: 100%
- Effort estimates accurate: ±30%
- Completeness: All modules covered: 100%

## Related Skills
- `document-analysis-a1tp` - Protocol analysis (called by this skill)
- `document-analysis-a1td` - Data model analysis (called by this skill)
- `document-analysis-a1gap` - Procedure analysis (called by this skill)
- `document-analysis-etsi-ts-132-158` - Standards analysis (called by this skill)
- `document-rule-learning` - Store learned patterns from this analysis
