# ORAN Integrator Platform — Architecture and Implementation Plan

Last updated: 2026-07-14
Owner: ORAN platform orchestration + quality engineering
Status: Design complete, implementation planned
Contract reference: ORAN/MVP_INTEGRATOR_MCP_CONTRACT.md
Feature plan reference: ORAN/FEATURE_PLAN.md
TODO reference: ORAN/TODO.md — Integration Testing section

---

## 1. Purpose

This document captures the full technical architecture and implementation plan for the ORAN Integrator Platform — an LLM-agnostic MCP multi-agent system that operates as a digital twin test orchestrator and conformance validator.

**Primary goal:** Determine, with auditable evidence, whether Non-RT RIC + A1 (and future modules) meets production-grade conformance requirements as defined by ETSI ORAN specifications and ORAN/FEATURE_PLAN.md.

**Secondary goal:** Provide a reusable, extensible orchestration platform that any system integrator can deploy, configure for their LLM of choice, and point at different DUT scopes (A1, O1, E2, cross-module).

---

## 2. Guiding Principles

1. **LLM-agnostic:** Orchestration logic is decoupled from model vendor via a Model Router service. Integrators supply their preferred LLM profiles.
2. **Deterministic gates:** Verdict computation, matrix evaluation, and evidence indexing are rule-based services — not free-form LLM outputs.
3. **Fail-closed quality:** No production-grade verdict is possible while unresolved required failures remain without an approved deferral.
4. **Traceability-first:** Every test result, fix, and verdict maps to a requirement clause, a trace ID, and an evidence artifact.
5. **Reproducibility:** Each run is defined by a versioned twin profile + test selectors. Any run can be fully reproduced from these two inputs.
6. **Incremental expansion:** MVP targets Non-RT RIC + A1. Same architecture expands to O1, E2, and cross-module integration without redesign.

---

## 3. System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        Integrator Trigger                                │
│   (CLI / UI / CI pipeline / VS Code Copilot chat)                        │
└─────────────────────────────┬────────────────────────────────────────────┘
                              │ run_id + scope + llm_profile
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       MCP Orchestrator                                   │
│  - Run registry (run_id, state, artifact index)                          │
│  - State machine (INIT → PLAN_SCOPE → ... → COMPLETE)                   │
│  - Fail-closed transition guards                                         │
│  - Agent dispatcher and result collector                                 │
└──────────┬───────────┬───────────┬───────────┬──────────┬───────────────┘
           │           │           │           │          │
    ┌──────▼──┐  ┌─────▼───┐ ┌────▼────┐ ┌───▼────┐ ┌───▼────────────┐
    │Plan     │  │Spec     │ │Code     │ │Scenario│ │Component       │
    │Scope    │  │Analysis │ │Arch     │ │Deriv.  │ │Classifier      │
    │Agent    │  │Agent    │ │Agent    │ │Agent   │ │Agent           │
    └──────┬──┘  └─────┬───┘ └────┬────┘ └───┬────┘ └───┬────────────┘
           │           │           │           │          │
           └───────────┴───────────┴───────────┴──────────┘
                                      │
                             ┌────────▼────────┐
                             │ Test Plan Matrix │
                             │ Agent            │
                             │ (execution_matrix│
                             │  .json draft)    │
                             └────────┬─────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
                    │         Digital Twin Runtime        │
                    │                                     │
                    │  Production: Non-RT RIC + A1        │
                    │  Simulators: A1 peer, Info source   │
                    │  Optional:   Near-RT RIC, E2 Nodes  │
                    └─────────────────┬──────────────────┘
                                      │
                             ┌────────▼─────────┐
                             │  Execution Agent  │
                             │  (fills verdicts  │
                             │   + evidence)     │
                             └────────┬──────────┘
                                      │
                    ┌─────────────────▼──────────────────┐
                    │         Evidence Store              │
                    │  ORAN/docs/coverage/evidence/       │
                    └─────────────────┬──────────────────┘
                                      │
                       ┌──────────────▼──────────────┐
                       │       Triage RCA Agent       │
                       │  failure_triage_ledger.json  │
                       └──────────────┬──────────────┘
                                      │
                       ┌──────────────▼──────────────┐
                       │   Gap Fix Orchestrator       │
                       │   fix_actions.json           │
                       │   → triggers reruns          │
                       └──────────────┬──────────────┘
                                      │
                       ┌──────────────▼──────────────┐
                       │     Verdict Gate Agent       │
                       │  hypothesis_verdict.json     │
                       │  Confirmed / Partially /     │
                       │  Rejected                    │
                       └─────────────────────────────┘
```

---

## 4. Component Definitions

### 4.1 MCP Orchestrator

Responsibilities:
- Holds canonical run state machine.
- Dispatches agents in sequence, collecting structured outputs at each stage.
- Enforces fail-closed transitions: if any stage returns `status=blocked|failed` for a required step, the run halts at that stage and reports.
- Maintains run registry: `run_id`, current state, timestamp, artifact index.

State machine:

```
INIT
 → PLAN_SCOPE          (PlanScopeAgent)
 → ANALYZE_SPECS       (SpecAnalysisAgent)
 → MAP_ARCHITECTURE    (CodeArchitectureAgent)
 → DERIVE_SCENARIOS    (ScenarioDerivationAgent)
 → CLASSIFY_COMPONENTS (ComponentClassifierAgent)
 → BUILD_MATRIX        (TestPlanMatrixAgent)
 → EXECUTE             (ExecutionAgent)
 → TRIAGE              (TriageRCAAgent)
 → FIX_AND_RERUN       (GapFixOrchestratorAgent)
 → GATE_VERDICT        (VerdictGateAgent)
 → COMPLETE
```

Fail-closed stages: EXECUTE, TRIAGE, FIX_AND_RERUN, GATE_VERDICT.

### 4.2 Model Router

Responsibilities:
- Accepts agent request envelopes.
- Routes to configured LLM based on task profile.
- Returns structured response envelopes.

Default routing policy:

| Task profile | Default model class |
|---|---|
| Document analysis, reasoning-heavy | High-reasoning model (e.g. Claude, GPT-4-class) |
| Code review and architecture mapping | Code-optimized model |
| Large triage batch processing | Cost-optimized model |
| Sensitive or offline data | Local/self-hosted model (vLLM or similar) |

Configuration: `integrator_llm_profile.json` (provided by integrator, not committed with secrets).

### 4.3 Agent Set (MVP)

#### PlanScopeAgent
- Input: ORAN/FEATURE_PLAN.md
- Extracts declared scope, release gates, acceptance criteria, exclusions.
- Output: `scope_contract.json`

#### SpecAnalysisAgent
- Input: existing document-analysis skill outputs, spec PDFs
- Maps technical clauses → expected runtime behaviors and API contracts
- Reuses: `document-analysis-a1tp`, `document-analysis-a1td`, `document-analysis-a1gap`
- Output: `clause_expectation_map.json`

#### CodeArchitectureAgent
- Input: demo-web/backend source tree
- Maps implemented boundaries, module ownership, interface contracts, service dependencies
- Output: `architecture_component_map.json`

Key code paths analyzed:
```
demo-web/backend/app/
  modules/non_rt_ric_a1/
  modules/o1_interface/
  modules/e2_interface/
  modules/simulators/
  modules/conformance_harness/
  services/a1_policy_service.py
  services/a1_enrichment_service.py
  services/conformance_service.py
  models/oran.py
  api/oran.py
```

#### ScenarioDerivationAgent
- Input: clause_expectation_map.json + architecture_component_map.json
- Derives test scenarios: positive path, negative path, boundary, interoperability
- Output: `scenario_catalog.json`

#### ComponentClassifierAgent
- Input: scenario_catalog.json + FEATURE_PLAN.md + architecture_component_map.json
- Classifies each component per scenario as `production` or `simulated`
- Source of truth priority: FEATURE_PLAN.md > code boundary analysis
- Output: `component_mode_map.json`

MVP classification baseline:

| Component | Mode | Justification |
|---|---|---|
| Non-RT RIC + A1 | production | Primary DUT; FEATURE_PLAN declares production-grade |
| O1 Interface | production (contract-level) | Production-capable contracts; stub internals |
| E2 Interface | production (contract-level) | Production-capable contracts; stub internals |
| Near-RT RIC | simulated | FEATURE_PLAN declares deterministic simulator |
| E2 Nodes | simulated | FEATURE_PLAN declares deterministic simulator |
| RAN User Intent | simulated | FEATURE_PLAN declares deterministic simulator |
| Info Sources | simulated | Behavior simulator; stub contracts passing |
| Conformance Harness | production (test tool) | Test orchestrator; already complete |

#### TestPlanMatrixAgent
- Input: scenario_catalog.json + component_mode_map.json + scope_contract.json
- Produces full execution matrix before test execution begins
- Every row includes simulator profile for reproducibility
- Output: `execution_matrix.json` (see Section 6 for schema)

#### ExecutionAgent
- Input: execution_matrix.json + twin_profile
- Starts digital twin runtime with correct component composition
- Runs each matrix row using pytest selectors
- Fills `actual_verdict`, `evidence_path`, and timing per row
- Output: `execution_results.json` + evidence bundle under `ORAN/docs/coverage/evidence/`

#### TriageRCAAgent
- Input: execution_results.json (failed rows only)
- For each failure: root-cause hypothesis, impacted code scope, confidence score, recommended action
- Reuses RCA skill once implemented
- Output: `failure_triage_ledger.json`

Triage record schema per failure:
```json
{
  "triage_id": "TRIAGE-0001",
  "row_id": "EM-0001",
  "failing_clause": "TS103989-4.2.1",
  "observed_behavior": "string",
  "expected_behavior": "string",
  "root_cause_hypothesis": "string",
  "confidence": 0.0,
  "impacted_code": ["file::function"],
  "trace_id": "ORAN-FTM-xxx",
  "recommended_action": "fix|defer|investigate",
  "severity": "required|optional"
}
```

#### GapFixOrchestratorAgent
- Input: failure_triage_ledger.json
- Creates fix tasks for `recommended_action=fix` entries
- Applies or delegates code fixes
- Triggers reruns of affected matrix rows
- Closes entries with rerun pass evidence or escalates to deferral
- Output: `fix_actions.json`

Fix action schema:
```json
{
  "fix_id": "FIX-0001",
  "triage_id": "TRIAGE-0001",
  "action_type": "code_fix|deferral|investigation",
  "status": "open|applied|deferred|closed",
  "code_changes": ["file", "diff_ref"],
  "rerun_row_ids": ["EM-0001"],
  "rerun_verdict": "pass|fail|not_run",
  "rerun_evidence_path": "path",
  "deferral_owner": "string",
  "deferral_due_date": "YYYY-MM-DD"
}
```

#### VerdictGateAgent
- Input: execution_results.json + fix_actions.json + scope_contract.json
- Applies deterministic gate rules (see Section 7)
- Produces final hypothesis verdict
- Output: `hypothesis_verdict.json`

---

## 5. Digital Twin Platform

### 5.1 What a digital twin is in this context

A versioned, reproducible runtime composition of:
- Production components under test (EUT)
- Minimal simulators acting as controlled peers
- Test data seed and configuration bundle
- Suite selectors and execution profile

The twin does NOT include full network emulation. It is a controlled software environment that exercises the EUT through its API and protocol interfaces.

### 5.2 Twin Profiles (MVP)

**Profile A: a1_minimal_twin_v1**

Purpose: A1 conformance and policy/EI interoperability

| Role | Component | Mode |
|---|---|---|
| EUT | Non-RT RIC + A1 | production |
| A1 peer | A1 peer behavior simulator | simulated |
| EI data | Info Sources simulator | simulated |
| Optional | Near-RT RIC simulator | off by default |
| Optional | E2 Nodes simulator | off by default |

Activation rule: enable optional components only when test row requires cross-interface dependency.

**Profile B: a1_interop_twin_v1**

Purpose: A1 full interoperability including cross-interface dependencies

| Role | Component | Mode |
|---|---|---|
| EUT | Non-RT RIC + A1 | production |
| A1 peer | A1 peer behavior simulator | simulated |
| EI data | Info Sources simulator | simulated |
| Cross-interface | Near-RT RIC simulator | simulated (active) |
| Cross-interface | E2 Nodes simulator | simulated (active) |

**Profile C: extended_integration_twin_v1** (future)

Adds O1 and E2 production-contract path under test alongside A1.

### 5.3 Twin Runtime Requirements

- Python 3.13 environment (already confirmed in workspace)
- pytest as test runner
- WebSocket or subprocess-based execution streaming for live output
- Evidence collector writes: pytest junit XML, protocol message log, run config snapshot
- Docker Compose for isolated runtime (development/CI)
- Single-node VM for production run

### 5.4 Simulator Requirements (MVP)

**A1 peer behavior simulator**
- Accepts A1-P policy create/update/delete and returns lifecycle events
- Accepts A1-EI job create/update/delete and delivers EI results
- Configurable delay and error-injection modes
- No state persistence required; resets between test runs

**Info Sources simulator**
- Exposes EI type catalog endpoint
- Delivers UEGeoandVel results matching TS 103 988 section 8/9 schema
- Configurable response payloads via data seed file

**Near-RT RIC simulator (optional in MVP)**
- Responds to A1 policy enforcement requests
- Returns enforcement status feedback
- Deterministic only; no adaptive behavior

**E2 Nodes simulator (optional in MVP)**
- Generates deterministic RAN measurement events
- Driven by test data seed file

---

## 6. Execution Matrix Schema

Full schema defined in ORAN/MVP_INTEGRATOR_MCP_CONTRACT.md Section 6.

Key design rules:
- Matrix is generated BEFORE execution (not populated retrospectively).
- Each row carries its twin profile ID so the environment is unambiguous.
- `actual_verdict` and `rerun_verdict` are the only fields filled during/after execution.
- `failure_category` is filled by TriageRCAAgent, not by the test runner.

---

## 7. Fail-Closed Gate Rules

Full rules defined in ORAN/MVP_INTEGRATOR_MCP_CONTRACT.md Section 8.

Summary:
- `production_grade=true` requires all required matrix rows to have `actual_verdict=pass` OR approved deferral with owner + date.
- Verdict values: `Confirmed`, `Partially Confirmed`, `Rejected`.
- VerdictGateAgent is the sole issuer of the final verdict — no agent upstream can override it.

---

## 8. Integration with Existing Skills

The Integrator Platform is an orchestration shell, not a replacement for existing skills.

| Existing skill | Role in Integrator Platform |
|---|---|
| `document-cross-reference-analysis` | Entry workflow for SpecAnalysisAgent |
| `document-analysis-a1tp` | A1 protocol clause extraction for SpecAnalysisAgent |
| `document-analysis-a1td` | A1 data model clause extraction for SpecAnalysisAgent |
| `document-analysis-a1gap` | Gap identification input for ScenarioDerivationAgent |
| `document-rule-learning` | Rule reuse across document analysis agents |
| `test-harness-regression` | Test generation for new scenarios identified by ScenarioDerivationAgent |
| `post-analysis-test-policy-orchestration` | Post-execution policy check and clause coverage update |

---

## 9. Recommended Rollout Phases

### Phase A — Test Setup Baseline (do this first)
**Goal:** Prove deterministic, reproducible test execution for Non-RT RIC + A1 before building orchestration.

Steps:
1. Lock minimal twin profile `a1_minimal_twin_v1` config and simulator behavior seeds.
2. Lock suite selectors for all known conformance and interface tests.
3. Run full suite manually and confirm artifact capture works end to end.
4. Publish `non_rt_ric_a1_minimal_simulator_bom.md` from this run.

Rationale: MCP agents can orchestrate but cannot issue trustworthy verdicts if the underlying test environment is not yet deterministic.

### Phase B — MCP Orchestration Skeleton
**Goal:** Automated, auditable run lifecycle with structured artifacts.

Steps:
1. Implement orchestrator state machine and run registry.
2. Implement agent request/response envelope validation.
3. Wire PlanScope, Matrix, Execution, and VerdictGate agents (minimal chain).
4. Produce mandatory artifact set on each run.
5. Verify repeat runs are reproducible from same twin profile + selectors.

### Phase C — Full Agentic Loop
**Goal:** Automated triage, gap-fix handoff, and rerun cycle.

Steps:
1. Implement TriageRCAAgent with structured triage output.
2. Implement GapFixOrchestratorAgent with fix task creation and rerun trigger.
3. Add fail-closed gate at FIX_AND_RERUN stage.
4. Tune model router policy for triage vs. code-change tasks.

### Phase D — Expansion
**Goal:** O1 + E2 integration paths and cross-module conformance.

Steps:
1. Add Profile B and Profile C twin configurations.
2. Extend ComponentClassifierAgent rules for O1 and E2.
3. Add cross-module scenario catalog generation.
4. Publish multi-module hypothesis verdict.

---

## 10. Repository Layout (target)

```
ORAN/
  FEATURE_PLAN.md
  MVP_INTEGRATOR_MCP_CONTRACT.md
  INTEGRATOR_PLATFORM_ARCHITECTURE.md   ← this document
  TODO.md
  docs/
    feature_traceability_map.md
    coverage/
      non_rt_ric_a1_execution_matrix.json
      non_rt_ric_a1_failure_triage_ledger.json
      non_rt_ric_a1_fix_actions.json
      non_rt_ric_a1_hypothesis_verdict.json
      non_rt_ric_a1_minimal_simulator_bom.json
      evidence/
        non-rt-ric-a1-hypothesis-<timestamp>/
          run_config_snapshot.json
          execution_matrix_filled.json
          pytest_junit.xml
          protocol_message_evidence.json

demo-web/backend/app/
  modules/
    non_rt_ric_a1/          ← production EUT
    o1_interface/            ← production (contracts)
    e2_interface/            ← production (contracts)
    simulators/
      near_rt_ric/           ← simulated
      e2_nodes/              ← simulated
      ran_user_intent/       ← simulated
      info_sources/          ← simulated (in progress)
      a1_peer/               ← simulated (new for Phase A)
    conformance_harness/     ← complete (test tool)
  services/
    integrator_orchestrator_service.py   ← new (Phase B)
    integrator_matrix_service.py         ← new (Phase B)
    integrator_verdict_service.py        ← new (Phase B)
    integrator_triage_service.py         ← new (Phase C)
  tests/
    integration/
      twin_profiles/
        a1_minimal_twin_v1.json
        a1_interop_twin_v1.json
      test_a1_minimal_twin_hypothesis.py
```

---

## 11. Key Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Simulator behavior masking production bugs | High | Fail-closed classifier; minimal simulator activation rule; optional-only activation for Near-RT RIC and E2 Nodes |
| LLM non-determinism in verdict computation | High | VerdictGateAgent uses deterministic rules only; LLM output is advisory only for triage |
| Test environment flakiness inflating failures | Medium | Separate `failure_category=test_env` in triage; require 2 consecutive fails before raising as implementation gap |
| MCP agent I/O schema drift over time | Medium | Versioned request/response envelopes; schema validation on every agent call |
| Specification ambiguity producing false failures | Medium | Spec clause references required in every triage entry; SpecAnalysisAgent output reviewed before matrix generation |

---

## 12. Document History

| Date | Change |
|---|---|
| 2026-07-13 | Initial MCP contract drafted and saved to ORAN/MVP_INTEGRATOR_MCP_CONTRACT.md |
| 2026-07-13 | Integration Testing P1-ENH tasks added to ORAN/TODO.md |
| 2026-07-13 | Phased rollout approach (test setup first, then MCP) agreed |
| 2026-07-14 | Full architecture document created (this file) |
