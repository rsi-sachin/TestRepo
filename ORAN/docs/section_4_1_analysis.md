# TS 103 989 Section 4.1 Analysis

Document: `ts_103989v040200p.pdf`

Section analyzed: `4.1 General`

## Workflow Skill Used

- Workflow entry skill: document-cross-reference-analysis
- Applied mode: single
- Orchestrated extraction lens: document-analysis-a1tp
- Supporting interpretation lens: document-rule-learning
- Trace IDs: ORAN-FTM-005, ORAN-FTM-006, ORAN-FTM-007, ORAN-FTM-008

## Source Meaning

Section 4.1 defines the overall test methodology for the A1 interface.

- The target of testing is the A1 interface between Non-RT RIC and Near-RT RIC.
- Two test families are required:
  - conformance testing
  - interoperability testing
- Conformance testing uses simulators for A1 procedures.
- The simulator must support HTTP `GET`, `PUT`, `POST`, and `DELETE`.
- The simulator must allow flexible configuration of URI, headers, and body so that multiple test cases can be created from the same transport primitive.
- Interoperability testing uses actual devices under test for Non-RT RIC and Near-RT RIC, with surrounding peers that may be real or simulated.

## Interpretation for A1 Interface Prototype Development

This section does not define individual API resources or payload schemas. It defines the testing posture that the prototype should optimize for.

The practical implications are:

- The prototype should be developed test-first from executable A1 scenarios, not implementation-first from UI or storage concerns.
- Test generation must distinguish conformance scenarios from interoperability scenarios.
- The harness must treat HTTP operation, URI, headers, and body as first-class configurable test inputs.
- Simulators are part of the architecture, not only a QA convenience, because conformance depends on controlled request/response behavior.
- Interoperability workflows should be layered on top of the same scenario model so that conformance cases can graduate into real-device integration checks.

## TDD-Oriented Development Approach

Section 4.1 supports the following TDD workflow for the prototype.

### 1. Write failing scenario tests before endpoint implementation

For every A1 feature slice:

- start from a spec-derived scenario
- encode expected HTTP method, URI pattern, headers, body shape, and expected status/result
- run the failing test against the current FastAPI surface
- implement only the minimum code needed to satisfy the scenario

This keeps development aligned with the conformance posture defined in the spec.

### 2. Separate conformance tests from interoperability tests

Maintain two explicit layers:

- **Conformance layer**
  - simulator-driven
  - deterministic
  - used for red/green TDD cycles
  - validates request/response behavior and protocol rules

- **Interoperability layer**
  - real or semi-real integration topology
  - used after conformance passes
  - validates behavior across Non-RT RIC and Near-RT RIC roles

The prototype should not rely on interoperability tests as the first correctness signal because they are slower and less isolating.

### 3. Build the simulator surface as reusable test infrastructure

The simulator requirements in Section 4.1 imply that the prototype needs reusable test fixtures for:

- configurable HTTP method execution
- configurable URI templates
- configurable headers
- configurable request and response bodies
- repeatable success and failure responses

This infrastructure should be implemented early because later A1-P and A1-EI tests depend on it.

### 4. Promote scenario definitions to the central artifact

The prototype should treat a generated or curated scenario definition as the source of truth for:

- parser output
- generated test catalog entries
- pytest script generation
- simulator invocation
- regression selection

That makes the TDD loop traceable from spec clause to executable test.

## Concrete Impact on Current ORAN Plan

### Phase 2: Spec Parsing Pipeline

Strengthen parsing output so each extracted TS 103 989 clause can capture:

- test family: conformance or interoperability
- A1 actor role: Non-RT RIC, Near-RT RIC, simulator, peer system
- HTTP operation and URI shape
- configurable request parts: headers, body, query parameters
- expected result class: success, protocol error, interop outcome

### Phase 3: Test Generation Engine

Generate two test styles from the same normalized scenario model:

- conformance pytest scripts using simulated peers
- interoperability pytest scripts or execution profiles using real/simulated topology bindings

### Regression Strategy

Adopt a strict test progression:

1. clause extraction test
2. semantic extraction test
3. simulator-backed conformance test
4. cross-spec enrichment test
5. interoperability flow test

This reduces the risk of building API code that cannot later be exercised in a spec-faithful way.

## Recommended Backlog Adjustments

1. Add scenario classification fields to clause and semantic extraction outputs.
2. Add simulator capability tests covering `GET`, `PUT`, `POST`, and `DELETE` with configurable URI, headers, and body.
3. Add a separate interoperability execution profile instead of treating all generated tests as identical pytest cases.
4. Keep TDD entry criteria at the scenario level: no new A1 route or service logic should be added without a failing spec-derived conformance test.

## Short Conclusion

Section 4.1 is the strongest justification in TS 103 989 for a TDD-first A1 prototype.

It says the prototype must be shaped around configurable HTTP-scenario testing, with conformance handled through simulators and interoperability handled through broader topology tests. The development approach should therefore begin with simulator-driven failing tests derived from TS 103 989 clauses, then grow into cross-spec enrichment and real-device interoperability checks.
