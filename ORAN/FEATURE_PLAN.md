# ORAN Feature Plan

Last updated: 2026-07-14 (aligned with TS 103 988 Section 9 follow-up gap closure, TS 103 989 section 4.2.1/4.2.2 gate remediation tracking, and Integrator Platform architecture design)
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

### Hypothesis-Driven Closure Policy (Non-RT RIC + A1)

- Working hypothesis: current Non-RT RIC + A1 implementation is production-grade for its declared scope.
- Validation method: execute conformance suites first; treat observed failures as implementation-gap discovery events.
- Closure rule: remaining gaps are prioritized and implemented when a target conformance/integration test fails due to missing behavior.
- Evidence rule: every failure must map to traceability rows, a concrete fix, and a rerun verdict artifact before closure.
- Promotion rule: move to Complete only when required conformance suites are green for the declared scope and no open fail-closed actions remain.

## 4. Module Status Board

| Module | Status | Conformance Coverage | Evidence Anchor |
|---|---|---|---|
| Non-RT RIC + A1 Interface | In Progress | TS 103 989 section 4.2.1/4.2.2 conformance gate currently blocked by policy-status enum regression (`70 passed, 6 failed` on 2026-07-14 — remediation in progress); TS 103 989 section 7 interoperability passing; TS 103 987 section 6 API-definition alignment verified; TS 103 987 Annex A strict EI payload/resource alignment verified; TS 103 983 section 4 principle-level conformance suite passing; TS 103 983 sections 7/8 analyzed (signalling procedure gaps identified); TS 103 988 section 5 common types conformance passing (99 tests); TS 103 988 section 6 A1-P data model complete (106 tests); TS 103 988 section 8 typed UEGeoandVel model slice in progress (41 tests); TS 103 988 section 9 follow-up gap set closed for implemented alignment slice | ORAN-FTM-001, ORAN-FTM-002, ORAN-FTM-003, ORAN-FTM-004, ORAN-FTM-013, ORAN-FTM-014, ORAN-FTM-015, ORAN-FTM-017, ORAN-FTM-020, ORAN-FTM-021, ORAN-FTM-022 |
| O1 Interface | In Progress | TS 103 983 section 4.1.2 topology/contract checks passing at validator and stub-contract level (integration-path tests pending) | ORAN-FTM-015 |
| E2 Interface | In Progress | TS 103 983 section 4.1.2 topology/contract checks passing at validator and stub-contract level (integration-path tests pending) | ORAN-FTM-015 |
| Near-RT RIC Simulator | TBD | Not started | Trace row pending in ORAN/docs/feature_traceability_map.md |
| E2 Nodes Simulator | TBD | Not started | Trace row pending in ORAN/docs/feature_traceability_map.md |
| RAN User Intent Simulator | TBD | Not started | Trace row pending in ORAN/docs/feature_traceability_map.md |
| Internal/External Info Sources Simulator | In Progress | TS 103 983 section 4.1.2 topology/contract checks passing at stub-contract level (behavioral simulator flows pending) | ORAN-FTM-015 |
| Conformance Harness | Complete | DUT readiness, simulator capability verification, and evidence checks implemented; conformance suites passing | ORAN-FTM-013, ORAN-FTM-014 |

### Current verified snapshot (from latest trace updates)

- TS 103 988 Section 9 follow-up gap set closed for the implemented alignment slice (major-version compatibility assertions, schema metadata linkage, compound scope negatives, constraints alias-conflict/enum coverage, and expanded discriminator coverage).
- Focused EI validation after closure updates: 66 passed, 0 failed (unit + interface suites).
- ORAN/TODO section-9 queued follow-up bullets marked closed (2026-07-14) with corresponding code and test coverage updates.
- TS 103 989 section 4.2.1/4.2.2 gate re-validation run (2026-07-14): 70 passed, 6 failed; remediation task is active for policy-status enum alignment in A1 policy service paths.
- TS 103 987 Section 6 API-definition alignment completed for A1 policy/EI/API router scope.
- Interface regression: 20 passed, 0 failed.
- Combined interface + conformance verification: 107 passed, 0 failed.
- TS 103 987 Annex A strict EI alignment completed for canonical EI job payload/resource handling and callback metadata exposure.
- Strict-mode focused regression: 38 passed, 0 failed.
- TS 103 983 section 4 conformance principles suite added and passing: 10 passed, 0 failed.
- TS 103 983 section 4.1.2 topology and interface-contract suite added and passing: 8 passed, 0 failed.
- TS 103 983 section 4 clause matrix status: covered=4, partial=4, missing=1.
- TS 103 983 sections 7 and 8 analyzed (2026-07-09); signalling procedure status procedures added to API/service layers; section-6 scoped regression: 94 passed, 0 failed; broader regression: 98 passed, 0 failed. Trace ID: ORAN-FTM-017.
- TS 103 988 section 4 analyzed (2026-07-09); no open implementation gaps identified.
- TS 103 988 section 5 common types: JSON encoding and type-catalog metadata enforcement completed (2026-07-10); 99 passed, 0 failed. Trace IDs: ORAN-FTM-020, ORAN-FTM-002, ORAN-FTM-003, ORAN-FTM-007.
- TS 103 988 section 6 A1-P data model Phase 1: PolicyScopeValidator, 10 scope identifiers, 8 objective types, 9 policy type combination rules implemented (2026-07-10); 106 passed, 0 failed. Trace ID: ORAN-FTM-020.
- TS 103 988 section 8 A1-EI data model: typed UEGeoandVel model slice (JobStatusType, GadShapeType, VelocityDescType, constraints, result) implemented (2026-07-13); 41 passed, 0 failed for initial slice; full closure pending. Trace IDs: ORAN-FTM-003, ORAN-FTM-004, ORAN-FTM-020, ORAN-FTM-021.
- TS 103 988 section 9 A1-EI concrete type alignment slice: canonical ORAN_UEGeoandVel_3.0.1 EI type ID, compound job definition, stricter bounds, and discriminator-based result validation implemented (2026-07-13); 16 passed for slice; 7 partial clauses queued for follow-up. Trace IDs: ORAN-FTM-022, ORAN-FTM-021, ORAN-FTM-003, ORAN-FTM-004.
- Residual deployment-path gap remains: application-prefixed API roots are still used for runtime exposure.
- Residual section-4 gaps remain for A1-ML implementation scope and full O1/E2 integration-level message flows.
- Residual TS 103 988 section 8/9 full closure pending: typed constraints/result handling and 7 partial clauses (9.1.1, 9.1.2.2, 9.1.2.3, 9.2.1.2.2, 9.2.1.3.1, 9.2.1.3.2, 9.2.1.3.4) need additional tests.
- See ORAN/docs/feature_traceability_map.md rows: ORAN-FTM-002, ORAN-FTM-003, ORAN-FTM-004, ORAN-FTM-015, ORAN-FTM-017, ORAN-FTM-020, ORAN-FTM-021, ORAN-FTM-022.

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
  - demo-web/backend/tests/conformance/test_ts103983_section4_principles.py
  - demo-web/backend/tests/conformance/test_ts103983_section4_topology_contracts.py
  - demo-web/backend/tests/conformance/test_ts103988_section5_common_types.py
  - demo-web/backend/app/services/conformance_service.py
  - demo-web/backend/app/modules/conformance_harness/
  - ORAN/docs/coverage/ts_103983_section4_clause_coverage_matrix.md
- TS 103 988 Section 5 type-catalog and encoding enforcement:
  - demo-web/backend/app/services/a1_policy_service.py (3GPP attribute encoding validation)
  - demo-web/backend/app/services/a1_enrichment_service.py (EI type identifier lexical validation, type-catalog metadata)
  - demo-web/backend/tests/module/oran/test_ts103988_section5_type_catalog_module.py
  - demo-web/backend/tests/e2e/test_ts103988_section5_catalog_e2e.py
  - demo-web/backend/tests/nonfunctional/memory/test_ts103988_section5_memory_behavior.py
  - demo-web/backend/tests/nonfunctional/load/test_ts103988_section5_load.py
  - demo-web/backend/tests/nonfunctional/stress/test_ts103988_section5_stress.py
  - demo-web/backend/tests/nonfunctional/parameter/test_ts103988_section5_parameter_passing.py
  - demo-web/backend/tests/interface/api/test_ts103988_section5_interface_faults.py
  - ORAN/docs/coverage/ts_103988_section5_clause_coverage_matrix.md
  - ORAN/docs/coverage/evidence/ts103988-section5-20260710132538/
  - ORAN/docs/coverage/evidence/ts103988-section5-hardening-20260710133538/
- TS 103 988 Section 6 A1-P data model (Phase 1):
  - demo-web/backend/app/models/validators/a1_policy_validator.py
  - demo-web/backend/app/data/models/a1_statement_components.py
  - demo-web/backend/app/data/models/a1_scope_identifiers.py
  - demo-web/backend/tests/unit/models/test_policy_scope_validator.py
  - demo-web/backend/tests/unit/models/test_a1_components_and_scopes.py
  - ORAN/docs/section_6_4_1_2_allowed_combinations.md
- TS 103 988 Sections 8 and 9 A1-EI typed model slice:
  - demo-web/backend/app/models/oran.py (UEGeoandVel, JobStatusType, GadShapeType, VelocityDescType, constraints, result, Section 9 compound job definition)
  - demo-web/backend/app/services/a1_enrichment_service.py (canonical EI type ID normalization, Section 9 schema metadata)
  - demo-web/backend/tests/unit/services/test_a1_enrichment_service.py (extended for Sections 8 and 9)
  - demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py (extended for Sections 8 and 9)
  - ORAN/docs/coverage/ts_103988_section8_clause_coverage_matrix.md
  - ORAN/docs/coverage/ts_103988_section9_clause_coverage_matrix.md
  - ORAN/docs/coverage/evidence/ts103988-section8-20260713161022/
  - ORAN/docs/coverage/evidence/ts103988-section9-20260713164329/
- TS 103 983 Section 6 signalling procedures and status procedures:
  - ORAN/docs/coverage/ts_103983_section6_clause_coverage_matrix.md
  - ORAN/docs/coverage/ts_103983_section6_gap_analysis.md
  - ORAN/docs/coverage/evidence/ts103983-section6-20260707113814/

### TBD or incomplete

- O1 interface module full API/integration behavior (contract-level validation complete)
- E2 interface module full API/integration behavior (contract-level validation complete)
- Simulators for Near-RT RIC, E2 Nodes, RAN User intent, info sources (topology contracts in place; scenario behaviors pending)
- A1-ML scope decision and baseline implementation/tests for TS 103 983 section 4.1.3.3 and 4.4
- Module-level conformance dashboards and coverage reporting
- TS 103 988 section 8 full closure: additional typed constraints/result handling and clause-level test expansion
- TS 103 988 section 9 full closure: 7 partial clauses (9.1.1, 9.1.2.2, 9.1.2.3, 9.2.1.2.2, 9.2.1.3.1, 9.2.1.3.2, 9.2.1.3.4) require negative tests, boundary tests, and discriminator coverage for remaining geo-location/velocity subtypes
- TS 103 988 section 6 Phase 2 (optional): binary encoding/serialization support for policy statements
- TS 103 983 sections 7/8 implementation gaps: analysis artifacts exist; implementation actions pending
- RCA Skill creation: failure identification, correlation, root-cause analysis, and test-orchestration handoff
- View Script modal regression fix for generated catalogs (UI bug)
- Backend field review after UI simplification (Complexity attribute and HTTP Method filtering scope)

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
- MVP multi-agent orchestration contract: ORAN/MVP_INTEGRATOR_MCP_CONTRACT.md
- Integrator Platform architecture and implementation plan: ORAN/INTEGRATOR_PLATFORM_ARCHITECTURE.md
- Coverage and policy artifacts:
  - ORAN/docs/coverage/
  - ORAN/docs/test-policy/

## 10. Deployment Target

- Development: Docker Compose
- Production: single-node VM
- Release precondition: conformance evidence bundle for A1/O1/E2 and required simulator interactions
