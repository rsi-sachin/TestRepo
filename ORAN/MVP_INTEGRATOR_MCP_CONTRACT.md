# ORAN MVP Integrator MCP Contract (Non-RT RIC + A1)

Last updated: 2026-07-13
Scope: MVP orchestration contract for an LLM-agnostic MCP multi-agent workflow that validates production-grade readiness for Non-RT RIC + A1 in a digital twin setup.

## 1. Objective

Provide a strict, auditable workflow that:

1. Reads the program requirement baseline from ORAN/FEATURE_PLAN.md.
2. Uses technical document analysis outputs to derive expected behavior.
3. Reviews existing production code and architecture boundaries.
4. Derives architecture-relevant test scenarios.
5. Identifies production components versus simulated components.
6. Designs a test plan.
7. Executes the plan and generates an execution matrix with verdicts.
8. Performs failure triage and closes gaps via fix + rerun evidence.

This workflow is fail-closed: no production-grade verdict is allowed while unresolved required gate failures remain.

## 2. Design Principles

- LLM-agnostic model routing: each agent can run on any integrator-selected LLM.
- Deterministic outputs where possible: matrix evaluation, gate computation, and evidence indexing are rule-based.
- Traceability-first: all failures and fixes map to trace rows and source clauses.
- Reproducibility: each run stores digital twin profile, test selectors, and artifact bundle.

## 3. Agent Topology (MVP)

1. PlanScopeAgent
2. SpecAnalysisAgent
3. CodeArchitectureAgent
4. ScenarioDerivationAgent
5. ComponentClassifierAgent
6. TestPlanMatrixAgent
7. ExecutionAgent
8. TriageRCAAgent
9. GapFixOrchestratorAgent
10. VerdictGateAgent

## 4. MCP Agent Contract

Every agent must implement the same contract envelope.

### 4.1 Request envelope

```json
{
  "run_id": "string",
  "agent": "string",
  "objective": "string",
  "scope": {
    "feature_plan": "ORAN/FEATURE_PLAN.md",
    "traceability_map": "ORAN/docs/feature_traceability_map.md",
    "component_scope": ["non_rt_ric_a1"],
    "specs": ["ts_103989", "ts_103987", "ts_103988", "ts_103983"]
  },
  "inputs": {
    "artifacts": ["path1", "path2"],
    "prior_outputs": ["json objects or paths"]
  },
  "constraints": {
    "fail_closed": true,
    "allow_code_changes": false,
    "llm_profile": "integrator-selected"
  }
}
```

### 4.2 Response envelope

```json
{
  "run_id": "string",
  "agent": "string",
  "status": "ok|blocked|failed",
  "summary": "string",
  "outputs": {
    "structured": {},
    "artifacts": ["path1", "path2"]
  },
  "quality": {
    "confidence": 0.0,
    "assumptions": ["string"],
    "open_issues": ["string"]
  }
}
```

## 5. Agent Responsibilities and Required Outputs

### 5.1 PlanScopeAgent

- Reads ORAN/FEATURE_PLAN.md.
- Extracts declared scope, release gates, and completion criteria.
- Output: `scope_contract.json`.

Required fields:

```json
{
  "declared_scope": ["Non-RT RIC + A1"],
  "required_gates": ["A1 4.2.1", "A1 4.2.2", "Section 7 interoperability"],
  "exclusions": ["O1 full integration", "E2 full integration"]
}
```

### 5.2 SpecAnalysisAgent

- Uses existing document-analysis skills outputs.
- Maps technical clauses to expected runtime behaviors and API contracts.
- Output: `clause_expectation_map.json`.

### 5.3 CodeArchitectureAgent

- Reviews production code and current architecture.
- Identifies actual implemented boundaries and dependency map.
- Output: `architecture_component_map.json`.

### 5.4 ScenarioDerivationAgent

- Builds test scenarios from clause expectations + architecture map.
- Output: `scenario_catalog.json` with positive, negative, boundary, and interoperability cases.

### 5.5 ComponentClassifierAgent

- Classifies components as `production` or `simulated` for each scenario.
- Output: `component_mode_map.json`.

Classifier schema:

```json
{
  "component": "non_rt_ric_a1|o1_interface|e2_interface|near_rt_ric|e2_nodes|ran_user_intent|info_sources",
  "mode": "production|simulated",
  "justification": "string",
  "source": "feature_plan|code"
}
```

### 5.6 TestPlanMatrixAgent

- Produces initial execution matrix before test execution.
- Must include simulator profile per row.
- Output: `execution_matrix.json` and optional markdown view.

### 5.7 ExecutionAgent

- Executes matrix rows against digital twin profiles.
- Updates each row with verdict, evidence path, and timing.
- Output: `execution_results.json` + evidence bundle.

### 5.8 TriageRCAAgent

- For each failure: root-cause hypothesis, impacted code scope, confidence, next action.
- Output: `failure_triage_ledger.json`.

### 5.9 GapFixOrchestratorAgent

- Converts triage into fix tasks.
- Applies fix workflows and triggers reruns.
- Output: `fix_actions.json` + rerun evidence links.

### 5.10 VerdictGateAgent

- Computes final verdict for hypothesis:
  - Confirmed
  - Partially Confirmed
  - Rejected
- Output: `hypothesis_verdict.json`.

## 6. Execution Matrix Schema (Required)

Execution matrix is mandatory and is generated in plan stage, then updated during execution and reruns.

```json
{
  "run_id": "string",
  "rows": [
    {
      "row_id": "EM-0001",
      "requirement_ref": "TS103989-4.2.1",
      "trace_id": "ORAN-FTM-013",
      "component_under_test": "non_rt_ric_a1",
      "component_modes": [
        {"component": "non_rt_ric_a1", "mode": "production"},
        {"component": "info_sources", "mode": "simulated"}
      ],
      "test_family": "conformance|interface|module|e2e|nonfunctional",
      "selector": "pytest path::test_name",
      "twin_profile": "a1_minimal_twin_v1",
      "expected_verdict": "pass",
      "actual_verdict": "pass|fail|blocked|not_run",
      "failure_category": "none|implementation_gap|test_env|data|flaky|unknown",
      "evidence_path": "ORAN/docs/coverage/evidence/...",
      "triage_ref": "TRIAGE-xxxx",
      "fix_ref": "FIX-xxxx",
      "rerun_verdict": "pass|fail|not_run"
    }
  ]
}
```

## 7. Digital Twin Profile Schema (MVP)

```json
{
  "profile_id": "a1_minimal_twin_v1",
  "purpose": "A1 conformance and interoperability",
  "production_components": ["non_rt_ric_a1"],
  "simulated_components": ["a1_peer_sim", "info_source_sim"],
  "optional_components": ["near_rt_ric_sim", "e2_nodes_sim"],
  "activation_rules": [
    "enable optional components only when test selector requires cross-interface dependency"
  ],
  "config_bundle": {
    "env": "path",
    "timeouts": "path",
    "data_seed": "path"
  }
}
```

## 8. Gate Rules (Fail-Closed)

### 8.1 Required gate conditions

All must be true to mark `production_grade=true` for declared scope:

1. Required execution matrix rows are run (no required `not_run`).
2. No unresolved required row has `actual_verdict=fail`.
3. Every failed required row has either:
   - fix applied + rerun pass evidence, or
   - approved deferral with risk owner + due date.
4. Traceability links exist for required rows.
5. Evidence paths exist for initial run and rerun (if rerun occurred).

### 8.2 Verdict computation

- `Confirmed`: all required rows pass with no unresolved required failures.
- `Partially Confirmed`: at least one required row remains deferred with owner/date or blocked for external dependency.
- `Rejected`: unresolved required failures without approved deferral or major scope mismatch.

## 9. Suggested Artifact Paths

- ORAN/docs/coverage/non_rt_ric_a1_execution_matrix.json
- ORAN/docs/coverage/non_rt_ric_a1_failure_triage_ledger.json
- ORAN/docs/coverage/non_rt_ric_a1_fix_actions.json
- ORAN/docs/coverage/non_rt_ric_a1_hypothesis_verdict.json
- ORAN/docs/coverage/non_rt_ric_a1_minimal_simulator_bom.json
- ORAN/docs/coverage/evidence/non-rt-ric-a1-hypothesis-<timestamp>/

## 10. MVP State Machine

```text
INIT
 -> PLAN_SCOPE
 -> ANALYZE_SPECS
 -> MAP_ARCHITECTURE
 -> DERIVE_SCENARIOS
 -> CLASSIFY_COMPONENTS
 -> BUILD_MATRIX
 -> EXECUTE
 -> TRIAGE
 -> FIX_AND_RERUN
 -> GATE_VERDICT
 -> COMPLETE
```

Transitions are fail-closed at EXECUTE, TRIAGE, FIX_AND_RERUN, and GATE_VERDICT stages.

## 11. Integration with Existing Skills

Existing skills should be reused rather than replaced:

- document-cross-reference-analysis
- document-analysis-a1tp
- document-analysis-a1td
- document-analysis-a1gap
- document-rule-learning
- test-harness-regression
- post-analysis-test-policy-orchestration

This Integrator MCP contract acts as the orchestration shell around these capabilities.
