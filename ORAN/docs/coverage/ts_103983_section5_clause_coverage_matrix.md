# TS 103 983 Section 5 Clause Coverage Matrix

Document: `ORAN/docs/ts_103983v040000p.pdf` (v4.0.0)
Scope: Section 5 (5.1, 5.2)
Analysis mode: `single` (protocol-centric)
Section target validation: requested section `5`; TOC match skipped; body section used (pages 11-17)

## Routing Audit

```yaml
selected_primary_skill: document-analysis-a1tp
selected_secondary_skills:
  - document-cross-reference-analysis
why_selected: Protocol-oriented A1 interface function clauses (service roles, lifecycle, resources, delivery)
protocol_markers_detected:
  - resource
  - lifecycle
  - delivery
  - request
  - status
section_target_validation:
  requested_section: "5"
  toc_match_skipped: true
  body_section_used: true
```

## Traceability Mapping

```yaml
selected_trace_ids:
  - ORAN-FTM-001
  - ORAN-FTM-002
  - ORAN-FTM-003
  - ORAN-FTM-004
mapped_todo_sections:
  - Traceability and Quality Follow-up
  - P1-ENH: Implement and reconcile TS 103 989 section 4.4 interoperability coverage
mapped_code_scope:
  - demo-web/backend/app/services/a1_service_registry.py
  - demo-web/backend/app/services/a1_policy_service.py
  - demo-web/backend/app/services/a1_enrichment_service.py
  - demo-web/backend/app/api/oran.py
  - demo-web/backend/tests/conformance/
verification_targets:
  - Clause-to-test conformance matrix for TS 103 983 section 5
  - A1-P and A1-EI lifecycle/ownership regression
  - EI registration/discovery/delivery behavior assertions
  - Explicit gap status for A1-ML service in section 5 context
```

## Clause Matrix

| Clause | Clause intent | Existing implementation evidence | Existing tests/evidence | Coverage status | Enrichment action |
|---|---|---|---|---|---|
| 5 Functions of the A1 interface | Define A1 function families: policy, EI, and AI/ML message exchange support | Service registry defines A1-P and A1-EI service boundaries in `demo-web/backend/app/services/a1_service_registry.py`; capability summaries now include explicit A1-ML scope verdict in policy and EI service summaries | Dedicated section-5 capability suite in `demo-web/backend/tests/conformance/test_ts103983_section5_capability_summary.py` validates explicit A1-ML scope declaration | Covered | Keep explicit scope declaration stable in service summaries and OpenAPI metadata |
| 5.1 Policy management | Non-RT RIC provisions/manages policy in Near-RT RIC | Policy CRUD, status, and policy-type operations in `demo-web/backend/app/services/a1_policy_service.py` and `demo-web/backend/app/api/oran.py` | Existing policy operation suites and interoperability clause-7 coverage | Covered | Keep aligned; add explicit TS 103 983 section-5 reference tags in conformance metadata |
| 5.1.1 Introduction | Policy goals and policy-type discovery support | `list_policy_type_ids`, policy schemas, role metadata in service registry and policy service | Policy type query suites in conformance harness | Covered | Add explicit clause-level mapping artifacts for 5.1.1 discovery intent |
| 5.1.2 Policy management function | Query available policies; create/update/delete; query status/content; feedback path | `create_or_replace_policy`, `list_policy_ids`, `get_policy`, `get_policy_status`, callback notification plumbing | API and conformance tests for policy CRUD and status behavior | Covered | Extend negative-path tests for status transition reasons tied to section 5.1.2 notes |
| 5.1.3 Lifecycle aspects of A1 policies | Policy lifecycle state transitions from Non-RT RIC perspective | Explicit lifecycle transition model added in `transition_policy_status` with guarded transitions between ACCEPTED, ENFORCED, and NOT_ENFORCED states | Dedicated transition conformance suite in `demo-web/backend/tests/conformance/test_ts103983_section5_policy_lifecycle_transitions.py` validates transition semantics and invalid transition rejection | Covered | Preserve transition-guard behavior and extend if additional states are introduced |
| 5.1.4 Identification and scope of A1 policies | Policy identified by PolicyId; scope identifier + statements | Policy scope validator enforces non-empty scope and supported scope discriminator classes in `a1_policy_service.py` | Dedicated scope suite in `demo-web/backend/tests/conformance/test_ts103983_section5_policy_scope_identifiers.py` validates accepted and rejected scope forms | Covered | Keep strict scope validation aligned with accepted discriminator list |
| 5.1.4.1 - 5.1.4.5 Scope identifiers | UE, UE groups, slices, QoS flows, cells as policy scope identifiers | Scope discriminator validator now accepts `ue`, `ue_group`, `slice`, `qos_flow`, `cell` (with alias normalization) | Parametrized clause-focused tests in `demo-web/backend/tests/conformance/test_ts103983_section5_policy_scope_identifiers.py` cover all scope subtypes and unknown-scope rejection | Covered | Extend discriminator aliases only when explicitly mapped to section semantics |
| 5.1.5 Policy content | Policy objectives/resources statement categories | Policy service now provides explicit objective/resource validation profile (`objective_resource_v1`) while preserving legacy statement compatibility | Unit/API taxonomy tests validate accepted objective/resource payloads and rejected malformed statements in `demo-web/backend/tests/unit/services/test_a1_policy_service.py` and `demo-web/backend/tests/interface/api/test_oran_a1_policy_api.py` | Covered | Maintain profile compatibility and extend categories only via explicit schema versioning |
| 5.2 A1 enrichment information | Non-RT RIC exposes EI, Near-RT RIC discovers/requests EI delivery | EI type, EI job lifecycle, status/result delivery implemented in enrichment service and API routes | EI job operations and interoperability EI suites | Covered | Add direct clause references for section 5.2 in metadata and coverage docs |
| 5.2.1 Introduction | EI type discovery and controlled delivery setup | EI types listing and EI-type lookup in service/API | EI type query tests exist | Covered | Keep aligned |
| 5.2.2 Enrichment information function | Non-RT RIC publishes EiTypeIds and delivers based on EI jobs | `list_ei_type_ids`, `create_or_replace_ei_job`, delivery helpers and callback URIs | EI lifecycle tests and clause-7 EI tests | Covered | Add explicit assertions for secure-delivery contract assumptions (connection setup failures and behavior) |
| 5.2.3 Lifecycle aspects of EI | Registration, discovery, request/delivery lifecycle | EI lifecycle now includes explicit restart reconciliation helper and delivery-failure state demotion behavior in `a1_enrichment_service.py` | Dedicated resilience suite in `demo-web/backend/tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py` validates restart reconciliation and delivery-failure semantics | Covered | Keep non-buffering expectation explicit in service behavior and tests |
| 5.2.3.3.1 EI job lifecycle | Near-RT RIC controls EI job creation/update/delete and post-restart reconciliation | Reconciliation helper `reconcile_ei_jobs_after_restart` added to preserve/disable EI jobs based on recovered state | Resilience test `test_section_5_2_3_3_1_reconcile_after_restart_marks_missing_jobs_disabled` validates post-restart disable path | Covered | Expand reconciliation matrix when persistent storage is introduced |
| 5.2.3.3.2 EI result lifecycle | Delivery starts on create, stops on delete, and may fail without buffering guarantees | `deliver_ei_job_result` and status notification paths now mark job status `DISABLED` on failed callback delivery instead of buffering retries | Resilience test `test_section_5_2_3_3_2_delivery_failure_disables_ei_job` validates connection-failure behavior | Covered | Keep failure handling deterministic and non-buffering |
| 5.2.4 Identification of A1 enrichment information | EI identified by EiTypeId and EiJobId conventions | EI type and EI job identifiers are primary keys in service storage model | EI id-based query tests exist | Covered | Keep aligned |
| 5.2.5 EI format and delivery | Push/delivery mechanisms and payload agreements | EI status/result callbacks enforce JSON payloads and deterministic callback handling semantics in enrichment service | Unit tests validate callback request header contract, response handling classes, and DISABLED demotion behavior in `demo-web/backend/tests/unit/services/test_a1_enrichment_service.py` | Covered | Keep callback content contract stable across service/API releases |
| 5.2.5.1 Push-based delivery | Callback-style push of EI status/result | Non-buffering push behavior uses one callback attempt per invocation with deterministic DISABLED status on endpoint failure | Conformance and unit tests assert no hidden retry loop and stable DISABLED state across repeated failures in `demo-web/backend/tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py` and `demo-web/backend/tests/unit/services/test_a1_enrichment_service.py` | Covered | Retry/backoff remains optional enhancement outside current section-5 closure baseline |

## Coverage Summary

- covered: 17
- partial: 0
- missing: 0

## Post-Orchestration Update (2026-07-02)

Targeted closure run added and validated section-5 tests for scope identifiers, lifecycle transitions,
EI reconciliation, and missing test perspectives (module, e2e, nonfunctional, interface).

```yaml
section5_targeted_clause_actions:
  - clause: 5.1.3
    action: none
    covered_by:
      - demo-web/backend/tests/conformance/test_ts103983_section5_a1_functions.py
  - clause: 5.1.4.1-5.1.4.5
    action: none
    covered_by:
      - demo-web/backend/tests/conformance/test_ts103983_section5_a1_functions.py
      - demo-web/backend/tests/nonfunctional/parameter/test_ts103983_section5_parameter_passing.py
  - clause: 5.2.3.3.1
    action: none
    covered_by:
      - demo-web/backend/tests/conformance/test_ts103983_section5_a1_functions.py
      - demo-web/backend/tests/e2e/test_ts103983_section5_reconciliation_e2e.py
  - clause: 5.2.3.3.2
    action: none
    covered_by:
      - demo-web/backend/tests/conformance/test_ts103983_section5_a1_functions.py
      - demo-web/backend/tests/interface/api/test_ts103983_section5_interface_faults.py
verification:
  command: pytest (targeted section-5 set)
  result: 25 passed, 0 failed
  junit: ORAN/docs/coverage/evidence/ts103983-section5-20260702/pytest_junit.xml
  completion_gate_status: pass
```

## Design and Code Enrichment Backlog

1. Completed: Added section-5 conformance suite with clause-aligned coverage files.
2. Completed: Implemented policy scope identifier validation profile for `5.1.4.x` sub-clauses.
3. Completed: Added explicit policy lifecycle transition model and conformance validation for `5.1.3` semantics.
4. Completed: Added EI lifecycle resilience tests and service behavior for restart reconciliation and connection failure (`5.2.3.3.x`).
5. Completed: Added explicit A1-ML section-5 scope decision in A1 service capability summaries.

## Proposed New Tests

- `demo-web/backend/tests/conformance/test_ts103983_section5_policy_scope_identifiers.py` (implemented)
- `demo-web/backend/tests/conformance/test_ts103983_section5_policy_lifecycle_transitions.py` (implemented)
- `demo-web/backend/tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py` (implemented)
- `demo-web/backend/tests/conformance/test_ts103983_section5_capability_summary.py` (implemented)

## Proposed Modified Tests

- `demo-web/backend/tests/conformance/test_ts103983_section4_principles.py` (optional future consolidation)
- `demo-web/backend/tests/conformance/test_ei_job_operations.py` (optional future extension for mixed-suite redundancy reduction)
- `demo-web/backend/tests/conformance/test_interoperability_clause7_suites.py` (optional future tagging enhancement)

## Implementation Gaps (Code-Level)

1. No open MVP blocking gaps for TS 103 983 section 5 clause closure.
2. Optional enhancement track: add explicit retry/backoff policy profile for push delivery if future requirements demand it.

## Pre-Response Checklist

- Body section target validated (TOC skipped): complete
- Protocol markers extracted/listed: complete
- HTTP/REST/auth/data/error extraction where applicable: complete (resource/lifecycle/error contracts)
- Existing tests and code mapped: complete
- New tests/modified tests/gaps listed: complete
- Routing audit fields populated: complete

## Post-Analysis Handoff Status

```yaml
post_analysis_handoff_status: executed_pass
post_analysis_handoff_target: post-analysis-test-policy-orchestration
post_analysis_handoff_reason: Workflow executed after explicit user confirmation; all section-5 clauses are now covered and completion gates passed.
confirmation_checkpoint:
  prompt: "Post-analysis orchestration is pending for ts_103983 section5. Confirm to run now? (yes/no)"
  response: "run the psot-analysis orchestration workflow"
  timestamp: "2026-07-07T11:03:35.0012652+05:30"
  source: "user"
gate_statuses:
  creation: pass
  execution: pass
  validation: pass
  triage: pass
completion_gate_status: pass
artifact_paths:
  test_policy_orchestrator_report: "ORAN/docs/test-policy/ts_103983_section5_test_policy_report.md"
  clause_coverage_matrix: "ORAN/docs/coverage/ts_103983_section5_clause_coverage_matrix.md"
  verification_run_summary: "ORAN/docs/coverage/ts_103983_section5_verification_run_summary.md"
  config_snapshot: "ORAN/docs/coverage/evidence/ts_103983_section5_config_snapshot.yaml"
  protocol_message_evidence: "ORAN/docs/coverage/evidence/ts_103983_section5_protocol_message_evidence.md"
```

## Verification Snapshot (2026-07-07)

- Focused regression command executed in `demo-web/backend`:
  - `pytest tests/unit/services/test_a1_policy_service.py tests/interface/api/test_oran_a1_policy_api.py tests/unit/services/test_a1_enrichment_service.py tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py tests/conformance/test_ts103983_section5_policy_scope_identifiers.py tests/conformance/test_ts103983_section5_policy_lifecycle_transitions.py tests/conformance/test_ts103983_section5_capability_summary.py tests/interface/api/test_oran_a1_ei_api.py`
- Result: `61 passed`
