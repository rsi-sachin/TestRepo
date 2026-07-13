# TS 103 988 Section 9 Test Policy Report

Document: ORAN/docs/ts_103988v090000p.pdf
Section scope: section9
Date: 2026-07-13

## Confirmation Checkpoint

- confirmation_prompt: Post-analysis orchestration is pending for ts_103988 section9. Confirm to run now? (yes/no)
- confirmation_response: yes
- confirmation_timestamp: 2026-07-13
- confirmation_source: user
- confirmation_status: confirmed

## Routing and Traceability

- selected_primary_skill: document-analysis-a1td
- selected_secondary_skills: document-cross-reference-analysis
- mandatory_agent: Test Policy Orchestrator
- selected_trace_ids: ORAN-FTM-022, ORAN-FTM-021, ORAN-FTM-003, ORAN-FTM-004
- branch: feature/ORAN_MVP_1_Py3_13
- baseline_commit_sha: 3599c5513c513c9df011c4666b5e01c994aed74d

Mapped code scope:
1. demo-web/backend/app/models/oran.py
2. demo-web/backend/app/services/a1_enrichment_service.py
3. demo-web/backend/app/api/oran.py
4. demo-web/backend/tests/unit/services/test_a1_enrichment_service.py
5. demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py
6. ORAN/docs/coverage/ts_103988_section9_gap_analysis.md

## Requirement Registry

| Clause | Priority | Normative focus | Current status |
|---|---|---|---|
| 9.1.1 | P0 | EI type identity and SemVer compatibility | partial |
| 9.1.2.1 | P0 | Generic EI job status schema | covered |
| 9.1.2.2 | P0 | Common data types linkage and compatibility handling | partial |
| 9.1.2.3 | P1 | EI type identifier embedded in schema `$id` | partial |
| 9.2.1.1 | P0 | Concrete EI type identifier `ORAN_UEGeoandVel_3.0.1` | covered |
| 9.2.1.2.2 | P0 | Allowed scope combinations for `UEGeoandVelEIDescription` | partial |
| 9.2.1.3.1 | P0 | Compound EI job definition schema | partial |
| 9.2.1.3.2 | P0 | EI job constraints schema | partial |
| 9.2.1.3.3 | P0 | EI job status schema reuse | covered |
| 9.2.1.3.4 | P0 | EI job result array and discriminator-specific payloads | partial |

## Traceability Matrix

| Clause | Existing coverage | Evidence target | Negative cases required |
|---|---|---|---|
| 9.1.1 | unit and API canonical-id coverage | service canonical storage and alias normalization | yes |
| 9.1.2.1 | existing EI status model coverage | focused EI unit/API regression | no |
| 9.1.2.2 | compound job-definition validation | unit clause-tagged schema checks | yes |
| 9.1.2.3 | schema metadata exposure | service/API schema-consistency checks | yes |
| 9.2.1.1 | unit and API canonical-id create-path assertions | stored `eiTypeId` and EI type metadata | no |
| 9.2.1.2.2 | scope wrapper enforcement | explicit rejection of unsupported scope members | yes |
| 9.2.1.3.1 | unit and API create-path validation | min/max bounds and extra-field rejection | yes |
| 9.2.1.3.2 | unit constraints validation | invalid enum, empty-array, alias-conflict tests | yes |
| 9.2.1.3.3 | existing EI status model coverage | status-schema reuse evidence | no |
| 9.2.1.3.4 | unit result-array validation | full discriminator matrix and malformed-result rejection | yes |

## Test Policy Orchestrator Output (Condensed)

### Coverage summary

- overall_decision: no-go
- creation: pass
- execution: pass
- validation: fail
- triage: pass
- completion_gate_status: fail
- completion_reason: Section 9 evidence artifacts now exist and the focused validation slice is green, but seven clauses remain partial and broader component/feature/nonfunctional coverage is still missing.

### Required tests by perspective

Unit:
1. Add explicit min/max boundary tests for `granularityPeriod`, `reportingPeriod`, and `reportingAmount`.
2. Add scope exclusivity tests that reject `groupId`, `sliceId`, `qosId`, `cellId`, and any extra `scope` members.
3. Add full discriminator matrix tests for all Section 9 geo-location and velocity subtype objects.
4. Add compatibility tests for alias versus canonical EI type handling and major-version mismatch behavior.

Component:
1. Add a service-level round-trip test for create, query, constraints validation, result validation, and status retrieval on one Section 9 job.

Module:
1. Add schema-contract consistency checks ensuring model, service, and API surfaces expose the same Section 9 `$id`, required fields, and result-array contract.

Interface:
1. Add API negatives for unsupported scope members, out-of-range numeric values, invalid `supportedVelocityTypes`, and malformed result arrays.

Feature/E2E:
1. Add a canonical `ORAN_UEGeoandVel_3.0.1` lifecycle round-trip across create, get, status, and result-delivery behavior.

Nonfunctional:
1. Memory: repeated create/replace/delete cycles for Section 9 jobs and array result payloads.
2. Load: mixed valid and invalid Section 9 jobs at moderate throughput.
3. Stress: repeated result-array submissions and status polling.
4. Parameter: permutation matrix across `gadShape`, `velocityDesc`, scope shape, and numeric boundaries.
5. Fault: malformed discriminator payloads, alias/canonical ID conflicts, and callback failure propagation.

## Missing Tests Planned

1. Dedicated Section 9 clause-tagged unit suite for compatibility, scope exclusivity, bounds, constraints, and discriminator coverage.
2. Dedicated Section 9 API negative suite for malformed scope, bounds, constraints, and result-array payloads.
3. Component/module consistency checks for schema metadata and runtime behavior.
4. Feature/E2E Section 9 lifecycle suite.
5. Nonfunctional memory/load/stress/parameter/fault hardening for the Section 9 slice.

## Executed Tests and Evidence

1. Combined focused validation: 16 passed, 23 deselected.
2. junit: ORAN/docs/coverage/evidence/ts103988-section9-20260713164329/pytest_junit.xml
3. config snapshot: ORAN/docs/coverage/evidence/ts103988-section9-20260713164329/run_config_snapshot.json
4. protocol/message evidence: ORAN/docs/coverage/evidence/ts103988-section9-20260713164329/protocol_message_evidence.md
5. requirement linkage: ORAN/docs/coverage/evidence/ts103988-section9-20260713164329/requirement_registry_linkage.md

## Gate Status Snapshot

- creation: pass
- execution: pass
- validation: fail
- triage: pass
- completion_gate_status: fail
- completion_reason: Section 9 still has seven `action=modify` clauses and lacks the broader clause-closing test inventory required for fail-closed completion.

## Residual Risks

1. Not every Section 9 discriminator-specific `geoLocation` and `velocity` subtype is yet proven by tests.
2. Generic A1-EI flows outside the Section 9-specific path may still dilute strict conformance expectations.
3. Alias handling can mask missing explicit compatibility-rule assertions if major-version behavior is not directly tested.
