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
| 5 Functions of the A1 interface | Define A1 function families: policy, EI, and AI/ML message exchange support | Service registry defines A1-P and A1-EI service boundaries in `demo-web/backend/app/services/a1_service_registry.py`; A1 API routes in `demo-web/backend/app/api/oran.py` | Section-4 principle tests validate A1-P/A1-EI service presence in `demo-web/backend/tests/conformance/test_ts103983_section4_principles.py` | Partial | Add explicit section-5 top-level conformance assertions for all listed function families, including explicit A1-ML scope verdict |
| 5.1 Policy management | Non-RT RIC provisions/manages policy in Near-RT RIC | Policy CRUD, status, and policy-type operations in `demo-web/backend/app/services/a1_policy_service.py` and `demo-web/backend/app/api/oran.py` | Existing policy operation suites and interoperability clause-7 coverage | Covered | Keep aligned; add explicit TS 103 983 section-5 reference tags in conformance metadata |
| 5.1.1 Introduction | Policy goals and policy-type discovery support | `list_policy_type_ids`, policy schemas, role metadata in service registry and policy service | Policy type query suites in conformance harness | Covered | Add explicit clause-level mapping artifacts for 5.1.1 discovery intent |
| 5.1.2 Policy management function | Query available policies; create/update/delete; query status/content; feedback path | `create_or_replace_policy`, `list_policy_ids`, `get_policy`, `get_policy_status`, callback notification plumbing | API and conformance tests for policy CRUD and status behavior | Covered | Extend negative-path tests for status transition reasons tied to section 5.1.2 notes |
| 5.1.3 Lifecycle aspects of A1 policies | Policy lifecycle state transitions from Non-RT RIC perspective | In-memory status lifecycle and deletion semantics in policy service | Lifecycle flow checks in section-4 principles test and clause-7 interoperability tests | Partial | Add explicit state-transition tests mirroring figure 5.1.3-1 transitions (ENFORCED/NOT_ENFORCED transitions triggered by query/notify) |
| 5.1.4 Identification and scope of A1 policies | Policy identified by PolicyId; scope identifier + statements | Policy object supports scope + policy statements, but uniqueness and scope semantics are lightweight | Basic policy object/schema tests exist | Partial | Add validation and tests for PolicyId uniqueness semantics and scope identifier class coverage (UE/group/slice/QoS/cell) |
| 5.1.4.1 - 5.1.4.5 Scope identifiers | UE, UE groups, slices, QoS flows, cells as policy scope identifiers | No strong scope-type specific validator in policy service | No clause-specific tests found | Missing | Add scope discriminator validation layer and dedicated tests per scope subtype |
| 5.1.5 Policy content | Policy objectives/resources statement categories | Policy payload accepts generic statements; no explicit objective/resource taxonomy in backend schema | Generic payload checks only | Partial | Introduce optional structured policy statement schema profile and tests for objective/resource categories |
| 5.2 A1 enrichment information | Non-RT RIC exposes EI, Near-RT RIC discovers/requests EI delivery | EI type, EI job lifecycle, status/result delivery implemented in enrichment service and API routes | EI job operations and interoperability EI suites | Covered | Add direct clause references for section 5.2 in metadata and coverage docs |
| 5.2.1 Introduction | EI type discovery and controlled delivery setup | EI types listing and EI-type lookup in service/API | EI type query tests exist | Covered | Keep aligned |
| 5.2.2 Enrichment information function | Non-RT RIC publishes EiTypeIds and delivers based on EI jobs | `list_ei_type_ids`, `create_or_replace_ei_job`, delivery helpers and callback URIs | EI lifecycle tests and clause-7 EI tests | Covered | Add explicit assertions for secure-delivery contract assumptions (connection setup failures and behavior) |
| 5.2.3 Lifecycle aspects of EI | Registration, discovery, request/delivery lifecycle | EI create/update/delete/query/status implemented; delivery callbacks implemented | Existing EI job operations tests cover core lifecycle | Partial | Add tests for registration precondition semantics and restart/reconciliation behavior described in 5.2.3 |
| 5.2.3.3.1 EI job lifecycle | Near-RT RIC controls EI job creation/update/delete and post-restart reconciliation | EI job CRUD is implemented | Coverage exists for CRUD but not restart reconciliation | Partial | Add test scenario for post-restart EI job query and reconcile decision path |
| 5.2.3.3.2 EI result lifecycle | Delivery starts on create, stops on delete, and may fail without buffering guarantees | `deliver_ei_job_result` exists; delete removes job/callback state | Tests cover positive delivery path | Partial | Add negative-path tests for delivery-connection failure and non-buffering expectations |
| 5.2.4 Identification of A1 enrichment information | EI identified by EiTypeId and EiJobId conventions | EI type and EI job identifiers are primary keys in service storage model | EI id-based query tests exist | Covered | Keep aligned |
| 5.2.5 EI format and delivery | Push/delivery mechanisms and payload agreements | Push-style callback result/status delivery implemented | Positive callback tests present | Partial | Add explicit push delivery mode matrix and content-type/contract robustness tests |
| 5.2.5.1 Push-based delivery | Callback-style push of EI status/result | Async POST callback implementations in enrichment service | Callback tests exist in interoperability EI suite | Partial | Add retry/backoff and endpoint-failure behavior tests to strengthen delivery reliability expectations |

## Coverage Summary

- covered: 8
- partial: 9
- missing: 1

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

1. Add section-5 conformance suite with clause IDs in test names/metadata.
2. Implement policy scope identifier validation profile for `5.1.4.x` sub-clauses.
3. Add policy lifecycle state transition test model for `5.1.3` figure semantics.
4. Add EI lifecycle resilience tests for restart reconciliation and connection failure behavior (`5.2.3.3.x`).
5. Add explicit A1-ML section-5 scope decision artifact (out-of-scope vs planned baseline).

## Proposed New Tests

- `demo-web/backend/tests/conformance/test_ts103983_section5_policy_scope_identifiers.py`
- `demo-web/backend/tests/conformance/test_ts103983_section5_policy_lifecycle_transitions.py`
- `demo-web/backend/tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py`
- `demo-web/backend/tests/conformance/test_ts103983_section5_capability_summary.py`

## Proposed Modified Tests

- `demo-web/backend/tests/conformance/test_ts103983_section4_principles.py` (add explicit section-5 linkage assertions)
- `demo-web/backend/tests/conformance/test_ei_job_operations.py` (add restart and connection-failure scenarios)
- `demo-web/backend/tests/conformance/test_interoperability_clause7_suites.py` (tag and map relevant checks to TS 103 983 section 5 clauses)

## Implementation Gaps (Code-Level)

1. No dedicated policy scope validator for UE/group/slice/QoS/cell scope forms (`5.1.4.x`).
2. No explicit policy-state transition model mirroring figure `5.1.3-1` semantics.
3. EI lifecycle logic lacks explicit restart reconciliation helper flow and corresponding tests.
4. No A1-ML executable capability path or explicit section-5 exclusion artifact in backend conformance outputs.

## Pre-Response Checklist

- Body section target validated (TOC skipped): complete
- Protocol markers extracted/listed: complete
- HTTP/REST/auth/data/error extraction where applicable: complete (resource/lifecycle/error contracts)
- Existing tests and code mapped: complete
- New tests/modified tests/gaps listed: complete
- Routing audit fields populated: complete

## Post-Analysis Handoff Status

```yaml
post_analysis_handoff_status: complete
post_analysis_handoff_target: post-analysis-test-policy-orchestration
post_analysis_handoff_reason: Workflow dispatched and artifacts persisted under ORAN/docs/test-policy and ORAN/docs/coverage.
```