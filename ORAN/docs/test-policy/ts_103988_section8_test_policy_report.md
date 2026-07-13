# TS 103 988 Section 8 Test Policy Report

Document: ORAN/docs/ts_103988v090000p.pdf
Section scope: section8
Date: 2026-07-13

## Confirmation Checkpoint

- confirmation_prompt: Post-analysis orchestration is pending for ts_103988 section8. Confirm to run now? (yes/no)
- confirmation_response: yes
- confirmation_timestamp: 2026-07-13T16:10:22.7880590+05:30
- confirmation_source: user
- confirmation_status: confirmed

## Routing and Traceability

- selected_primary_skill: document-analysis-a1td
- selected_secondary_skills: document-cross-reference-analysis
- mandatory_agent: Test Policy Orchestrator
- selected_trace_ids: ORAN-FTM-003, ORAN-FTM-004, ORAN-FTM-020, ORAN-FTM-021

Mapped code scope:
1. demo-web/backend/app/models/oran.py
2. demo-web/backend/app/services/a1_enrichment_service.py
3. demo-web/backend/app/api/oran.py
4. demo-web/backend/tests/unit/services/test_a1_enrichment_service.py
5. demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py

## Test Policy Orchestrator Output (Condensed)

### Coverage summary

- overall_decision: no-go
- creation: pass
- execution: pass
- validation: pass
- triage: pass
- completion_gate_status: fail
- completion_reason: Required artifact and execution evidence now exist, but Section 8 still has open clause actions and missing typed UEGeoandVel data-model implementation required by clauses 8.2.2.2 through 8.4.5.

### Required tests by perspective

Unit:
1. Modify demo-web/backend/tests/unit/services/test_a1_enrichment_service.py for strict JobStatusType negatives and later typed Section 8 payload negatives.
2. Add a dedicated Section 8 model-validation suite for GadShapeType, VelocityDescType, GeoLocationType discriminators, VelocityType discriminators, and EI job constraints objects.

Component:
1. Add a clause-tagged TS 103 988 Section 8 conformance suite for enums, typed job definition, typed result payloads, and constraints-object behavior.

Module:
1. Add schema-consistency checks that service and API layers expose the same Section 8 schema names and constraints contract.

Interface:
1. Modify demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py for negative-path validation of invalid discriminators, unsupported shape values, and malformed constraints payloads once implementation exists.

Feature/E2E:
1. Add a typed UEGeoandVel EI create/status/result round-trip suite after the Section 8 typed result model is implemented.

Nonfunctional:
1. Memory: typed create/delete cycles with constraints objects.
2. Load: mixed valid and invalid UEGeoandVel jobs at moderate throughput.
3. Stress: repeated replace/query on typed EI jobs.
4. Parameter: boundary permutations across shape, velocity, and discriminator combinations.
5. Fault: deterministic API rejection of invalid Section 8 typed payloads.

### Priority and blockers

P0 blockers:
1. BLK-TRACE-001: new Section 8 trace row required and now created as ORAN-FTM-021.
2. BLK-MODEL-002: typed UEGeoandVel enums, discriminators, and constraints objects are not implemented in demo-web/backend/app/models/oran.py.
3. BLK-SERVICE-003: demo-web/backend/app/services/a1_enrichment_service.py does not validate Section 8 typed payloads.
4. BLK-API-004: demo-web/backend/app/api/oran.py cannot reject invalid Section 8 typed payloads because the underlying typed model is absent.

P1:
1. Add clause-tagged unit and interface suites for typed Section 8 validation after the model and service gaps are closed.
2. Add module and E2E consistency checks once typed Section 8 schemas are exposed.

P2:
1. Add nonfunctional memory/load/stress/parameter/fault hardening after P0 and P1 close.

## Clause Actions

1. Clause 8.1: action=modify
2. Clause 8.2.1: action=modify
3. Clause 8.2.2.1: action=modify
4. Clause 8.2.2.2: action=add
5. Clause 8.2.2.3: action=add
6. Clause 8.3.1: action=add
7. Clause 8.3.2.1: action=add
8. Clause 8.3.2.2: action=add
9. Clause 8.3.3.1: action=add
10. Clause 8.3.3.2: action=add
11. Clause 8.3.4.1: action=add
12. Clause 8.3.4.2: action=add
13. Clause 8.4.1: action=modify
14. Clause 8.4.2.1: action=modify
15. Clause 8.4.2.2: action=modify
16. Clause 8.4.3: action=modify
17. Clause 8.4.4: action=add
18. Clause 8.4.5: action=add
19. Clause 8.5: action=modify

## Missing Tests Planned

1. Typed Section 8 model-validation suite for enums, discriminators, and constraints objects.
2. Interface/API negatives for invalid typed EI payloads.
3. Clause-tagged Section 8 conformance suite.
4. Module consistency tests for schema naming and constraints exposure.
5. Typed Section 8 E2E round-trip suite.

## Executed Tests and Evidence

1. Targeted current-state regression: 41 passed, 0 failed, 25 warnings.
2. junit: ORAN/docs/coverage/evidence/ts103988-section8-20260713161022/pytest_junit.xml
3. config snapshot: ORAN/docs/coverage/evidence/ts103988-section8-20260713161022/run_config_snapshot.json
4. protocol/message evidence: ORAN/docs/coverage/evidence/ts103988-section8-20260713161022/protocol_message_evidence.md
5. requirement linkage: ORAN/docs/coverage/evidence/ts103988-section8-20260713161022/requirement_registry_linkage.md

## Gate Status Snapshot

- creation: pass
- execution: pass
- validation: pass
- triage: pass
- completion_gate_status: fail
- completion_reason: Section 8 remains blocked by open clause add/modify actions and missing typed EI data-model behavior, not by missing execution evidence.

## Residual Risks

1. Existing EI lifecycle regressions may overstate Section 8 conformance because they validate generic CRUD, callback, and status behavior rather than typed UEGeoandVel semantics.
2. ORAN-FTM-020 is insufficient for Section 8 closure because it is scoped to TS 103 988 Sections 4.1-4.2.
3. The current implementation only closes a first typed validation slice; full Section 8 closure still requires constraints-object and result-object conformance plus additional clause-level tests.