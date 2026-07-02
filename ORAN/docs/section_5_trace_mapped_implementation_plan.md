# TS 103 989 Section 5 Trace-Mapped Implementation Plan

Generated from the section 5 analysis of `ORAN/docs/ts_103989v040200p.pdf` and the current traceability map in `ORAN/docs/feature_traceability_map.md`.

## Implementation Input

selected_trace_ids:
- ORAN-FTM-001
- ORAN-FTM-002
- ORAN-FTM-003
- ORAN-FTM-004

mapped_todo_sections:
- Traceability and Quality Follow-up

mapped_code_scope:
- demo-web/backend/app/services/a1_service_registry.py
- demo-web/backend/app/services/a1_policy_service.py
- demo-web/backend/app/services/a1_enrichment_service.py
- demo-web/backend/app/api/oran.py

verification_targets:
- API regression tests for service-aware flows
- Unit tests for policy operations and constraints
- Service unit tests and API tests for A1-EI workflow and payload requirements
- API tests for `/api/oran/services`, generation, upload, selection flows

## Section 5 Gap Summary

| Trace ID | Section 5 Coverage | Current State | Implementation Focus |
|---|---|---|---|
| ORAN-FTM-001 | 5.1 service boundary | Partially implemented | Keep A1-P/A1-EI service discovery explicit and stable |
| ORAN-FTM-002 | 5.2 policy operations | Mostly implemented | Preserve CRUD and callback behavior while keeping conformance coverage current |
| ORAN-FTM-003 | 5.3 EI job lifecycle | Missing production lifecycle behavior | Add in-memory EI type/job management, status handling, and notification support |
| ORAN-FTM-004 | service-aware API surface | Partially implemented | Expose EI capability in API metadata and conformance category routing |

## Recommended Implementation Order

1. Extend `A1EnrichmentInformationService` with EI type and EI job lifecycle methods.
2. Expose EI-aware conformance category metadata and execution flow in `backend/app/api/oran.py`.
3. Add direct unit coverage for the new EI service lifecycle methods.
4. Add conformance coverage for the EI job operations path.

## Clause-to-Change Matrix

| Section 5 Clause | Coverage Status | Planned Change |
|---|---|---|
| 5.1 General | Covered | Keep service registry and role definitions aligned |
| 5.2 Policy consumer/producer operations | Covered with follow-up risk | Maintain existing policy CRUD and callback behavior |
| 5.2.6 Notify policy status | Partially covered | Preserve callback notification path and keep negative-path coverage in tests |
| 5.3 EI producer operations | Missing | Implement EI type and job lifecycle methods in `a1_enrichment_service.py` |
| 5.3 query/create/update/delete/status scenarios | Missing | Add conformance harness coverage and direct unit tests |

## Implementation Handoff

The analysis output for section 5 should be treated as the source of truth for the implementation phase. Production code edits should begin only after the trace-mapped plan above is present and validated against the traceability map.