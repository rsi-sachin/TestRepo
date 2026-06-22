# Feature 2 TODO - Component Simulator via TDD

Project: Extend demo-web with simulator generation from extracted ORAN test plans
Status: NOT STARTED
Owner Track: Feature 2 (Downstream)

## Scope

- For each selected test case, build simulator code that makes the test pass.
- Apply strict TDD cycle (red -> green -> refactor).
- Keep traceability from test cases to simulator modules and implementation.

## Upstream Dependency

Feature 2 can only target components/modules identified by Feature 1 JSON outputs.
Required upstream input fields:
- test_id
- component_targets
- module_targets
- expected_results
- protocol_or_interface

See upstream: [Feature 1 TODO](TODO-F1-spec-ingestion.md)

---

## Core TDD Workstream

- [ ] Define simulator acceptance test template mapped to test_id.
- [ ] Select first target component/module from Feature 1 JSON output.
- [ ] Write failing test for target behavior.
- [ ] Implement minimum simulator code to pass.
- [ ] Refactor while preserving green tests.
- [ ] Repeat per test case and target component.

## Implementation Planning

- [ ] Define simulator package/module structure.
- [ ] Define per-component simulator interfaces.
- [ ] Define protocol fixtures/mocks and test data.
- [ ] Add simulator run harness and reporting hooks.
- [ ] Add quality gates (coverage + regression checks).

## Approved Architecture Plan (List-1 Aligned)

- [ ] Implement in existing demo-web/backend codebase.
- [ ] Keep module identifiers exactly as List-1 names in API payloads and persisted JSON.
- [ ] Implement Near-RT RIC as full simulator in this phase; keep all other modules as orchestrator-controlled stubs.
- [ ] Add top-level orchestrator with per-scenario execution mode: sequential or parallel.
- [ ] Build scenario loader using Feature-1 JSON only (no ad-hoc scenarios in this phase).
- [ ] Add runtime contracts for timers, state machine, counters, buffers, alerts, and user contexts.
- [ ] Implement E2 interactions from O_CU_CP/O_CU_DP/O_DU/O_ENODEB to NEAR_RT_RIC.
- [ ] Implement O1 monitoring flow from ORAN_INT_INFO_SOURCE aggregate to SMO, starting with alarms/alerts.
- [ ] Expose simulator API routes under /api/v1/oran/simulator/... with thin routing and service-layer logic.
- [ ] Persist simulator runtime state/events under data/oran_learning as JSON.

## Pre-Test-Case Bootstrap (Contract-First)

Until first concrete test case is selected from Feature-1 output:

- [ ] Create placeholder simulator route handlers under /api/v1/oran/simulator/... with deterministic scaffold responses.
- [ ] Add request/response schema validation for placeholder handlers.
- [ ] Add API routing tests that verify endpoint registration, status codes, and response contract shape.
- [ ] Add failing tests first, then implement minimal placeholder handlers to pass (strict TDD).
- [ ] Mark placeholder handlers for scenario-specific behavior replacement once first test case is identified.

## Detailed Legacy Backlog Migrated from TODO.md (Downstream-aligned)

### In-Browser Code Editor (Phase 2 - Script Customization)
Priority: LOW
Status: NOT STARTED
Depends on: Phase 3 Task 3.3

- [ ] Integrate Monaco Editor or CodeMirror into frontend.
- [ ] Backend: POST /api/oran/scripts/{test_id}/customize to save custom edits.
- [ ] UI: Edit Script flow with Save and Execute, Revert, and Diff View.
- [ ] Persist custom scripts: backend/generated_tests/{test_id}_custom.py.
- [ ] Execution service uses custom version when available.

Success criteria:
- Users can edit generated scripts, save changes, execute custom versions, and revert.

## Completion Criteria

- [ ] Every selected test case has at least one passing simulator-backed test.
- [ ] Traceability exists from test_id -> component/module -> simulator implementation.
- [ ] Regression suite is green for implemented simulator components.
- [ ] Simulator target selection is always sourced from Feature 1 JSON output.
