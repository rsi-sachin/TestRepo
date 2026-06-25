# ORAN Feature Traceability Map (Metadata Tracking)

Last updated: 2026-06-25 (ORAN-FTM-002: added TS 103 987 §5.2.4 to source reference scope)
Scope: ORAN feature, module, and component traceability for planning, implementation, and verification.

## Purpose

This artifact provides non-code metadata mapping between:

- Features, modules, and components
- TODO sections and implementation tracks
- Document-analysis skills used for interpretation
- Source document sections (TS references)
- Ownership, status, and verification evidence

## Metadata Fields

| Field | Description |
|---|---|
| Trace ID | Stable identifier for each traceability row |
| Level | Feature, Module, or Component |
| Item | Name of the feature/module/component |
| TODO Mapping | Section in `ORAN/TODO.md` where work is tracked |
| Skills Used | Skills used to interpret the source requirements |
| Source Reference | Document and section identifiers |
| Code Scope | Primary implementation area |
| Owner | Responsible team/person track |
| Status | Planned, In Progress, Complete, or Blocked |
| Verification | Test or validation artifact |
| Notes | Additional context or constraints |

## Traceability Matrix

| Trace ID | Level | Item | TODO Mapping | Skills Used | Source Reference | Code Scope | Owner | Status | Verification | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| ORAN-FTM-001 | Feature | A1 Service Selection and Registry | Traceability and Quality Follow-up; Phase 2 | document-cross-reference-analysis, document-analysis-a1tp | TS 103 987 Section 5.1 | demo-web/backend/app/services/a1_service_registry.py | ORAN backend | In Progress | API regression tests for service-aware flows | A1-P and A1-EI in scope; A1-ML out of scope |
| ORAN-FTM-002 | Module | A1 Policy Service | Traceability and Quality Follow-up | document-cross-reference-analysis, document-analysis-a1tp, document-analysis-a1td | TS 103 987 Sections 5.2.1, 5.2.2.1-5.2.2.4, 5.2.3, 5.2.4 | demo-web/backend/app/services/a1_policy_service.py | ORAN backend | In Progress | Unit tests for policy operations and constraints | Must enforce policy ownership and mutability rules |
| ORAN-FTM-003 | Module | A1 Enrichment Service | Traceability and Quality Follow-up; Phase 2 | document-cross-reference-analysis, document-analysis-a1tp | TS 103 987 A1-EI service scope (Section 5.1) | demo-web/backend/app/services/a1_enrichment_service.py | ORAN backend | Planned | Service unit tests and API tests | Align with A1-EI workflow and payload requirements |
| ORAN-FTM-004 | Component | ORAN API Router and Service-Aware Endpoints | Traceability and Quality Follow-up | document-cross-reference-analysis, document-analysis-a1tp | TS 103 987 resource model and HTTP operations | demo-web/backend/app/api/oran.py | ORAN backend | In Progress | API tests for `/api/oran/services`, generation, upload, selection flows | Include ProblemDetails-style error handling where applicable |
| ORAN-FTM-005 | Feature | Specification Ingestion Pipeline | Phase 2 Task 2.1 | document-cross-reference-analysis, document-analysis-a1tp | TS 103 989 (test clauses), TS 103 987 (protocol), TS 103 988 (types), TS 103 983 (principles) | demo-web/backend/app/services/spec_parser_service.py | ORAN backend | Planned | Unit tests for PDF/DOCX ingestion | Supports multi-spec ingestion for enrichment |
| ORAN-FTM-006 | Feature | Clause and Semantic Extraction | Phase 2 Task 2.2, 2.3 | document-cross-reference-analysis, document-analysis-a1tp, document-rule-learning | TS 103 989 clause structures; TS 103 987 endpoint semantics | demo-web/backend/app/services/spec_parser_service.py | ORAN backend | Planned | Clause extraction and semantic parsing tests | Regex-first extraction with fallback strategy |
| ORAN-FTM-007 | Feature | Multi-Spec Cross-Reference and Conflict Tracking | Phase 2 Task 2.4, 2.5 | document-cross-reference-analysis, document-analysis-a1tp, document-analysis-a1td, document-analysis-a1gap | TS 103 989/987/988/983 cross-reference behavior | demo-web/backend/app/services/spec_parser_service.py; demo-web/backend/data/spec_conflicts.json | ORAN backend | Planned | Integration tests for enrichment and conflict detection | Conflict logs must preserve source and resolution metadata |
| ORAN-FTM-008 | Feature | Test Catalog Generation | Phase 3 Task 3.1 | document-cross-reference-analysis, document-analysis-a1tp | TS 103 989 test intent mapped to executable catalog entries | demo-web/backend/app/services/test_generator_service.py | ORAN backend | Planned | JSON schema validation for generated catalogs | Must preserve service metadata in generated catalog/test cases |
| ORAN-FTM-009 | Component | Pytest Script Template and Generation | Phase 3 Task 3.2, 3.3 | document-analysis-a1tp, document-rule-learning | TS 103 987 HTTP/resource semantics | demo-web/backend/templates/oran/a1_test.py.j2; demo-web/backend/generated_tests/ | ORAN backend | Planned | Template rendering and syntax validation tests | Keep generated scripts readable and reproducible |
| ORAN-FTM-010 | Component | ORAN Execution Service and KPI Parsing | Phase 1 complete; P1-ENH for Python 3.13 | test-harness-regression | Internal execution requirements and KPI expectations | demo-web/backend/app/services/oran_execution_service.py; demo-web/backend/app/parsers/oran_parser.py | ORAN backend | In Progress | Execution smoke tests, parser unit tests | Python 3.13 compatibility track active |
| ORAN-FTM-011 | Feature | ORAN Frontend Upload and Catalog UX | Phase 1 complete; Post-UI Simplification Follow-up | document-analysis-a1tp | TS 103 989/987/988/983 document upload and mapping workflow | demo-web/frontend/templates/index.html; demo-web/frontend/static/js/oran.js; demo-web/frontend/static/css/oran.css | ORAN frontend | In Progress | UI functional checks and script-view regression tests | Includes open issue for View Script modal behavior |
| ORAN-FTM-012 | Feature | Metadata Mapping Artifact Governance | Traceability and Quality Follow-up | document-cross-reference-analysis, document-rule-learning | Internal governance requirement from TODO follow-up | ORAN/docs/feature_traceability_map.md | ORAN docs owner | In Progress | Manual review on each milestone update | Update after each phase or major requirement change |

## Status Legend

- Planned: Defined but implementation not started
- In Progress: Actively being implemented or validated
- Complete: Implemented and verified
- Blocked: Waiting on dependency or decision

## Update Protocol

1. Add or update rows when a feature/module/component is introduced or split.
2. Keep TODO mapping synchronized with section names in `ORAN/TODO.md`.
3. Keep source references specific to TS and section identifiers.
4. Update status and verification evidence at the end of each phase.
5. Preserve Trace ID stability; do not recycle IDs for different items.
