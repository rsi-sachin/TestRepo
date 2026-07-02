# ORAN Feature Plan

Last updated: 2026-07-02 (aligned with TS 103 987 Section 6 plus Annex A strict EI progress and latest regression evidence)
Primary objective: Deliver a conformance-first ORAN implementation for System Integrators with module-separated code ownership, module-level traceability, and auditable conformance coverage.

This is the main guiding document for planning and execution.
Detailed feature/module/component trace metadata is maintained in:

- ORAN/docs/feature_traceability_map.md

## 0. Document Usage Model (Single-Entry Navigation)

Use this file as the primary entry point for planning, status interpretation, and execution sequencing.

- Plan-level decisions, delivery gates, and module sequencing are defined here.
- Detailed trace rows (Trace ID, code scope, source clauses, verification evidence) are defined in ORAN/docs/feature_traceability_map.md.
- Sprint/task execution details are tracked in ORAN/TODO.md.

Update rule:

1. Update ORAN/docs/feature_traceability_map.md first for any feature/module/component implementation delta.
2. Reflect only summarized status deltas in this FEATURE_PLAN.md.
3. Keep references bidirectional so a reader can navigate from this file to trace rows and evidence quickly.

## 1. Scope and Architecture Baseline

This feature aligns implementation and testing to the Figure 4.1.2.1 module model:

- SMO -> Non-RT RIC
- Near-RT RIC
- E2 Nodes
- RAN User Intent Provider
- ORAN Internal and External Information Sources
- Interfaces: A1, O1, E2

### Implementation policy

- Non-RT RIC + A1: production-grade in this phase
- O1 and E2 interfaces: production-capable contracts in this phase (stub-compatible internals)
- Remaining modules: simple deterministic simulators in this phase
- Conformance tests are release blockers

## 2. Module Folder Structure (Mandatory)

### Runtime layout

- demo-web/backend/app/modules/non_rt_ric_a1
- demo-web/backend/app/modules/o1_interface
- demo-web/backend/app/modules/e2_interface
- demo-web/backend/app/modules/simulators/near_rt_ric
- demo-web/backend/app/modules/simulators/e2_nodes
- demo-web/backend/app/modules/simulators/ran_user_intent
- demo-web/backend/app/modules/simulators/info_sources
- demo-web/backend/app/modules/conformance_harness

### Documentation layout

- ORAN/docs/traceability/matrix_non_rt_ric_a1.md
- ORAN/docs/traceability/matrix_o1_interface.md
- ORAN/docs/traceability/matrix_e2_interface.md
- ORAN/docs/traceability/matrix_near_rt_ric_simulator.md
- ORAN/docs/traceability/matrix_e2_nodes_simulator.md
- ORAN/docs/traceability/matrix_ran_user_intent_simulator.md
- ORAN/docs/traceability/matrix_info_sources_simulator.md
- ORAN/docs/traceability/matrix_conformance_harness.md

## 3. Conformance-First Delivery Gates

A module can move to Complete only when all three conditions pass:

1. Implementation complete for planned phase scope
2. Traceability matrix rows complete (requirement -> function/file -> test case)
3. Conformance suite and evidence gates pass

### A1 hard gates (current release blocker)

- DUT readiness checks implemented and passing
- Simulator capability verification implemented and passing
- Evidence collector and validator implemented and passing
- TS 103 989 section 4.2.1 and 4.2.2 conformance suite passing

### O1 and E2 hard gates (this phase)

- Interface contract tests in place
- Schema validation and deterministic error mapping in place
- Correlation and observability checks in place
- Conformance coverage status reported in module matrix

## 4. Module Status Board

| Module | Status | Conformance Coverage | Evidence Anchor |
|---|---|---|---|
| Non-RT RIC + A1 Interface | In Progress | TS 103 989 section 4.2.1/4.2.2 conformance passing; TS 103 989 section 7 interoperability passing; TS 103 987 section 6 API-definition alignment verified; TS 103 987 Annex A strict EI payload/resource alignment verified | ORAN-FTM-001, ORAN-FTM-002, ORAN-FTM-003, ORAN-FTM-004, ORAN-FTM-013, ORAN-FTM-014 |
| O1 Interface | TBD | Not started | Trace row pending in ORAN/docs/feature_traceability_map.md |
| E2 Interface | TBD | Not started | Trace row pending in ORAN/docs/feature_traceability_map.md |
| Near-RT RIC Simulator | TBD | Not started | Trace row pending in ORAN/docs/feature_traceability_map.md |
| E2 Nodes Simulator | TBD | Not started | Trace row pending in ORAN/docs/feature_traceability_map.md |
| RAN User Intent Simulator | TBD | Not started | Trace row pending in ORAN/docs/feature_traceability_map.md |
| Internal/External Info Sources Simulator | TBD | Not started | Trace row pending in ORAN/docs/feature_traceability_map.md |
| Conformance Harness | Complete | DUT readiness, simulator capability verification, and evidence checks implemented; conformance suites passing | ORAN-FTM-013, ORAN-FTM-014 |

### Current verified snapshot (from latest trace updates)

- TS 103 987 Section 6 API-definition alignment completed for A1 policy/EI/API router scope.
- Interface regression: 20 passed, 0 failed.
- Combined interface + conformance verification: 107 passed, 0 failed.
- TS 103 987 Annex A strict EI alignment completed for canonical EI job payload/resource handling and callback metadata exposure.
- Strict-mode focused regression: 38 passed, 0 failed.
- Residual deployment-path gap remains: application-prefixed API roots are still used for runtime exposure.
- See ORAN/docs/feature_traceability_map.md rows: ORAN-FTM-002, ORAN-FTM-003, ORAN-FTM-004.

## 5. Already In Place vs TBD

### Already in place

- A1 policy models and API baseline
- A1 service registry baseline
- ORAN execution and parser baseline
- Conformance requirement documents:
  - ORAN/docs/section_4_2_1_4_2_2_conformance_setup.md
  - ORAN/docs/dut_readiness_checklist.md
  - ORAN/docs/simulator_capability_matrix.md
  - ORAN/docs/execution_evidence_specification.md
- A1 conformance executable suites and support services:
  - demo-web/backend/tests/conformance/test_a1_policy_conformance_4_2_1.py
  - demo-web/backend/tests/conformance/test_a1_policy_conformance_4_2_2.py
  - demo-web/backend/tests/conformance/simulator_capability_verification.py
  - demo-web/backend/app/services/conformance_service.py
  - demo-web/backend/app/modules/conformance_harness/

### TBD or incomplete

- O1 interface module (contracts, API, tests)
- E2 interface module (contracts, API, tests)
- Simulators for Near-RT RIC, E2 Nodes, RAN User intent, info sources
- Module-level conformance dashboards and coverage reporting

## 6. Skills Usage Policy

The following skills are mandatory inputs for requirement-to-code planning and updates:

- document-cross-reference-analysis (workflow entry)
- document-analysis-a1tp
- document-analysis-a1td
- document-analysis-a1gap
- document-rule-learning
- test-harness-regression

Each matrix row must include source section references extracted through skill-assisted analysis artifacts.

## 7. Implementation Sequence

1. Implement module scaffolding and per-module matrices
2. Close A1 conformance blockers (first release gate)
3. Implement O1 and E2 production-capable contracts
4. Implement remaining simulator modules for integrated testbeds
5. Execute cross-module conformance and integration suites
6. Promote modules from In Progress/TBD to Complete only with evidence

## 8. Reporting Format (mandatory for each sprint)

- Module status: Complete, In Progress, TBD
- Conformance coverage: Planned, In Progress, Passed, Blocked
- Failing gates: list of blockers with owner
- Evidence artifact links: logs, reports, and test IDs

## 9. Cross-Reference Index

- Strategic execution plan: ORAN/FEATURE_PLAN.md (this document)
- Trace row details and verification mapping: ORAN/docs/feature_traceability_map.md
- Sprint/task execution log: ORAN/TODO.md
- Coverage and policy artifacts:
  - ORAN/docs/coverage/
  - ORAN/docs/test-policy/

## 10. Deployment Target

- Development: Docker Compose
- Production: single-node VM
- Release precondition: conformance evidence bundle for A1/O1/E2 and required simulator interactions
