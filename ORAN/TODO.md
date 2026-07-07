# Demo-Web ORAN Integration - TODO List

**Project:** Extend demo-web with O-RAN A1 test generation capabilities  
**Last Updated:** 2026-07-07  
**Status:** Phase 1 Complete, TS 103 989 section 4.4/Section 7 interoperability complete, TS 103 983 section 6 complete, Phase 2-4 pending

## Task Update: TS 103 983 Section 6 Signalling Procedures

- Task: Analyze and implement Section 6 of `ORAN/docs/ts_103983v040000p.pdf`, close identified implementation gaps, and verify clause coverage with evidence artifacts.
- Date completed: 2026-07-07
- Status: Complete
- Trace ID: ORAN-FTM-017
- Implementation summary:
  - Added explicit policy type status procedures (query + notify) to API/service layers.
  - Added explicit EI type status procedures (query + notify) to API/service layers.
  - Added interface API tests for new status procedures and OpenAPI callback metadata.
  - Added clause-level section-6 coverage artifacts and updated section-6 gap analysis with residual governance items.
- Verification status:
  - Section-6 scoped regression: 94 passed, 0 failed.
  - Additional broader regression (including clause-7 suites): 98 passed, 0 failed.
  - completion_gate_status: pass
- Artifacts:
  - `ORAN/docs/coverage/ts_103983_section6_clause_coverage_matrix.md`
  - `ORAN/docs/coverage/ts_103983_section6_gap_analysis.md`
  - `ORAN/docs/coverage/ts_103983_section6_verification_run_summary.md`
  - `ORAN/docs/coverage/evidence/ts103983-section6-20260707113814/`

## Task Update: Clause-7 Interoperability Follow-up Fix (Post Section-6 Broad Run)

- Task: Resolve the clause-7 interoperability regression discovered during a broad post-section-6 regression run.
- Date completed: 2026-07-07
- Status: Complete
- Scope:
  - Updated A1-P interoperability harness payload scope to match enforced policy scope schema in `demo-web/backend/app/modules/conformance_harness/service.py`.
- Verification status:
  - `tests/conformance/test_interoperability_clause7_suites.py`: 4 passed, 0 failed.
  - Combined targeted regression set: 98 passed, 0 failed.

## Task Update: TS 103 989 Section 7 Implementation

- Task: Implement Section 7 of ORAN/docs/ts_103989v040200p.pdf and reconcile with section 4.4 interoperability scope.
- Date completed: 2026-07-02
- Status: Complete
- Trace ID: ORAN-FTM-014
- Implementation summary:
  - Expanded interoperability coverage from placeholder suites to clause-level executable coverage.
  - A1-P coverage: 9 clause checks (7.2.1.1 to 7.2.6.1).
  - A1-EI coverage: 11 clause checks (7.3.1.1 to 7.3.7.1).
  - Added EI result-delivery support and corresponding negative-path validation.
  - Captured retained evidence and policy artifacts for fail-closed gate completion.
- Verification status:
  - Focused section-7 regression: 26 passed, 0 failed.
  - completion_gate_status: pass

## Task Update: TS 103 987 Section 6 API Definition Alignment

- Task: Analyze and implement Section 6 of `ORAN/docs/ts_103987v040300p.pdf` to update existing A1 API definitions and close runtime/API-schema coverage gaps.
- Date completed: 2026-07-02
- Status: Complete
- Trace IDs: ORAN-FTM-002, ORAN-FTM-003, ORAN-FTM-004
- Implementation summary:
  - Applied Section 6 API-definition response modeling to A1-P and A1-EI routes, including documented 4xx/5xx response contracts and ProblemDetails media type exposure.
  - Standardized ProblemDetails response media type handling (`application/problem+json`) for A1 error responses.
  - Added runtime method-constraint coverage (405) and conflict-mapping coverage (409) at interface layer.
  - Added/updated interface tests for policy and EI APIs to validate OpenAPI response metadata and runtime error behavior.
  - Preserved existing conformance semantics (policy/EI update behavior) while keeping explicit 409 mapping tests via controlled conflict injection.
- Verification status:
  - Interface API regression: 20 passed, 0 failed.
  - Conformance regression: 87 passed, 0 failed.
  - Combined verification run: 107 passed, 0 failed.
  - completion_gate_status: pass

## Task Update: TS 103 987 Annex A OpenAPI Alignment (Strict EI Mode)

- Task: Analyze and implement Annex A of ORAN/docs/ts_103987v040300p.pdf with strict OpenAPI-aligned A1-EI payloads and canonical EI job resource handling.
- Date completed: 2026-07-02
- Status: Complete
- Trace IDs: ORAN-FTM-002, ORAN-FTM-003, ORAN-FTM-004
- Implementation summary:
  - Added canonical Annex A EI job endpoints under /api/oran/a1/eijobs/{ei_job_id} (+ status/delete) while retaining service-aware routing.
  - Enforced strict Annex A EI payload contracts for EI create/update flows: eiTypeId, jobDefinition, and jobResultUri.
  - Aligned EI status/result object handling to Annex A canonical fields (eiJobStatus, jobResult) and removed legacy alias behavior from EI model/service contract paths.
  - Added OpenAPI callback metadata for policy and EI notification/result callbacks on relevant PUT operations.
  - Updated EI interface, service, and conformance harness tests to validate strict canonical Annex A field usage.
- Verification status:
  - Strict-mode focused regression: 38 passed, 0 failed.
  - completion_gate_status: pass
- Residual gap:
  - API deployment path remains application-prefixed (/api/oran/...) rather than exposing standalone server-root paths exactly matching Annex A server URL blocks.

## Important Document References (Repo Index)

### Program and planning documents

- ORAN/FEATURE_PLAN.md
- ORAN/IMPLEMENTATION_PLAN.md
- ORAN/TODO.md
- ORAN/TODO-F1-spec-ingestion.md
- ORAN/TODO-F2-simulator-tdd.md
- ORAN/PHASE1_COMPLETE.md

### Core source specifications

- ORAN/docs/ts_103989v040200p.pdf
- ORAN/docs/ts_103987v040300p.pdf
- ORAN/docs/ts_103988v090000p.pdf
- ORAN/docs/ts_103983v040000p.pdf

### Traceability and analysis documents

- ORAN/docs/feature_traceability_map.md
- ORAN/docs/section_4_1_analysis.md
- ORAN/docs/section_4_2_analysis.md
- ORAN/docs/section_5_trace_mapped_implementation_plan.md
- ORAN/docs/section_4_2_1_4_2_2_conformance_setup.md

### Section 7 policy and coverage artifacts

- ORAN/docs/test-policy/ts_103989_section7_policy_checklist.md
- ORAN/docs/test-policy/ts_103989_section7_test_policy_report.md
- ORAN/docs/coverage/ts_103989_section7_clause_coverage_matrix.md
- ORAN/docs/coverage/ts_103989_section7_verification_run_summary.md
- ORAN/docs/coverage/evidence/s7-20260702024430/run_config_snapshot.json
- ORAN/docs/coverage/evidence/s7-20260702024430/protocol_message_evidence.json
- ORAN/docs/coverage/evidence/s7-20260702024430/pytest_junit.xml

### Related section 5 and section 6 quality artifacts

- ORAN/docs/test-policy/ts_103989_section5_policy_checklist.md
- ORAN/docs/test-policy/ts_103989_section5_test_policy_report.md
- ORAN/docs/coverage/ts_103989_section5_clause_coverage_matrix.md
- ORAN/docs/coverage/ts_103989_section5_verification_run_summary.md
- ORAN/docs/coverage/ts_103989_section6_clause_coverage_matrix.md

### Product and workspace context documents

- docs/requirements.txt
- demo-web/README.md
- demo-web/MIGRATION.md
- demo-tool/README.md
- demo-tool/docs/requirements.txt

## Section 5 Summary

- TS 103 989 Section 5 analysis completed and trace-mapped implementation handoff closed.
- Added A1-EI lifecycle API/service/tests, updated post-analysis handoff skills, and refreshed section-5 policy artifacts.
- Focused validation passed (`35 passed`), artifacts were generated, and the changes were committed and pushed on `feature/ORAN_MVP_1_Py3_13` (`3c1004b`).

## P1-ENH: Python 3.13 Migration Readiness and Implementation

Priority: P1-ENH
Status: N/A (Already satisfied)
Owner Track: ORAN / demo-web backend and tests

Objective:
- Confirm whether migration is required for Python 3.13 runtime compatibility.

Verification:
- Date verified: 2026-07-02
- Active workspace environment: `c:/TestRepo/.venv/Scripts/python.exe`
- Detected version: 3.13.13
- Outcome: Migration work is not required because the current environment is already Python 3.13.

Scope:
- None for migration. Continue with normal compatibility/regression validation as needed.

Target Files:
- N/A

Execution Plan:
- [x] Confirm active workspace Python version.
- [x] Determine migration necessity.
- [x] Mark task as N/A and remove duplicate TODO entry.

Exit Criteria:
- Task is closed as N/A after environment verification.

---

## 📋 IMPLEMENTATION TASKS

### 🔄 Post-UI Simplification Follow-up
**Status:** Pending  
**Priority:** Medium

- [ ] Review backend usage of HTTP Method and Complexity attributes after ORAN UI simplification.
  - Validate whether Complexity should remain in API, DB model, and services.
  - Reassess HTTP Method filtering scope and retention across ORAN test management endpoints.
  - Remove obsolete backend fields/filters only after compatibility check with existing catalogs and execution flow.
- [x] Add catalog deletion support in UI and backend.
  - Add a Delete button beside each catalog name on the Test Catalog card.
  - Implement catalog deletion endpoint to remove catalog JSON and associated test cases.
  - Confirm UI refresh removes deleted catalog from the list immediately after success.
- [ ] Investigate View Script modal failure when catalog contains generated tests (observed with 2-test catalog).
  - Reproduce by generating a catalog, opening Test Catalog, and clicking View Script on each test row.
  - Confirm reproducible case: catalog name `TS_103_989_1` renders tests, but View Script click does not open modal.
  - Verify frontend handler wiring in ORAN catalog table and script modal open path.
  - Validate backend script retrieval endpoint and test-id to script-file mapping.
  - Add regression check so View Script works for both MVP-sized catalogs and larger catalogs.

### 🔁 Traceability and Quality Follow-up
**Status:** Pending  
**Priority:** High

- [ ] Add unit and module-level tests for newly added A1 service selection and service modules.
  - Scope: `backend/app/services/a1_service_registry.py`, `backend/app/services/a1_policy_service.py`, `backend/app/services/a1_enrichment_service.py`, `backend/app/api/oran.py`, and related model updates.
  - Add API tests for `/api/oran/services` and service-aware flows (`extract-methodology`, `upload-specs`, `generate`, `generate-from-selection`).
  - Add regression tests for service metadata propagation in generated catalogs and test cases.

- [ ] Add non-code metadata mapping for feature/module/component traceability to TODO sections and document skills.
  - Create and maintain a metadata artifact outside source code (no inline code comments): `ORAN/docs/feature_traceability_map.md`.
  - For each feature/module/component, map to one or more TODO sections plus one or more skills used for document interpretation.
  - Include document and section references (for example, TS/section identifiers) and ownership/status fields.

- [x] **Section 5 processing and trace-mapped implementation handoff**
  - **Completed:** 2026-07-01 | **Input:** `ORAN/docs/ts_103989v040200p.pdf` section 5 analysis
  - **Trace IDs:** ORAN-FTM-001, ORAN-FTM-002, ORAN-FTM-003, ORAN-FTM-004
  - **Implementation plan:** `ORAN/docs/section_5_trace_mapped_implementation_plan.md`
  - **Code scope updated:** `demo-web/backend/app/services/a1_enrichment_service.py`, `demo-web/backend/app/modules/conformance_harness/service.py`, `demo-web/backend/app/api/oran.py`
  - **Verification:** unit, conformance, and API tests added for A1-EI lifecycle and routing; final focused validation passed (`35 passed`)
  - **Artifacts:** `ORAN/docs/test-policy/ts_103989_section5_test_policy_report.md`, `ORAN/docs/coverage/ts_103989_section5_clause_coverage_matrix.md`, `ORAN/docs/coverage/ts_103989_section5_verification_run_summary.md`
  - **Skill update:** added explicit post-analysis handoff rules to all analysis skills so `post-analysis-test-policy-orchestration` is invoked as a formal post-step after analysis completion
  - **Published:** committed and pushed on `feature/ORAN_MVP_1_Py3_13` (`3c1004b`)
  - **Notes:** Section 5 analysis closed end-to-end; clause matrix reached zero unresolved actions, execution evidence was attached, and the section-5 gate concluded `pass`

- [x] **Analyze TS 103 987 §5.2.1–§5.2.2 — Policy management service (introduction and service description)**
  - **Completed:** 2026-06-25 | **Branch:** `feature/ORAN_MVP_1_Py3_13` | **Commits:** inline
  - **Skill used:** `document-cross-reference-analysis` (single mode), extraction lens: `document-analysis-a1tp`
  - **Document:** `ORAN/docs/ts_103987v040300p.pdf` (v4.3.0)
  - **Sections analyzed:** §5.2.1 (Introduction), §5.2.2.1 (Functional elements), §5.2.2.2 (Policy representation), §5.2.2.3 (Representation objects), §5.2.2.4 (Resource identifiers)
  - **Key findings:**
    - A1-P service operations tied to policy types defined in A1TD; schema-driven behavior.
    - Policy is a REST resource (PolicyObject) with scope identifier + at least one policy statement.
    - policyId assigned by A1-P Consumer at creation; producer cannot modify/delete policies.
    - PolicyObject excludes internal NF routing details; decoupled ownership model.
    - Status/feedback notifications subscribed at policy creation via callback URI (notificationDestination).
    - Policy type governance: producer advertises supported types; consumer cannot CRUD policy types.
    - Required representation objects: PolicyTypeObject, PolicyObject, PolicyStatusObject, ProblemDetails.
    - Required URIs: `/policytypes`, `/policytypes/{policyTypeId}`, `/policytypes/{policyTypeId}/policies`, `/policytypes/{policyTypeId}/policies/{policyId}`, `/policytypes/{policyTypeId}/policies/{policyId}/status`.
  - **Implementation verdict:** A1-P models and initial API routes implemented; callback URI validation and schema-driven policy enforcement ready for Phase 2 persistence integration.
  - **Actions taken:**
    - Created skill-based analysis document: `ORAN/docs/section_5_2_1_5_2_2_skill_analysis.md` (architectural patterns, code-level gaps, concrete implementation blueprint)
    - Added A1-P representation models: `demo-web/backend/app/models/a1_policy_models.py` — ProblemDetails, PolicyTypeObject, PolicyObject, PolicyStatusObject, CreateOrReplacePolicyRequest
    - Extended A1PolicyService: `demo-web/backend/app/services/a1_policy_service.py` — in-memory store for policy types/policies/status; methods: list_policy_type_ids(), get_policy_type(), create_or_replace_policy(), get_policy(), delete_policy(), get_policy_status()
    - Wired initial A1-P API routes: `demo-web/backend/app/api/oran.py` — GET/PUT/DELETE /a1/policytypes(/{id})/policies/{id}(/status) with ProblemDetails error payloads (404, 400, error instance tracking)
    - Updated custom instructions: `ORAN/docs/feature_traceability_map.md` rule trigger added to always invoke document-analysis workflow skill for "analyze <sections> from <document>" pattern
    - Added preference memory: `/memories/preferences.md` for persistent skill-trigger guidance
  - **Next steps:** Database persistence layer, policy-type schema validation (A1TD integration), callback URI event stream, full lifecycle tests, ownership constraint enforcement tests

- [x] **Analyze TS 103 987 §5.2.4 — Service operations for A1 policies**
  - **Completed:** 2026-06-25 | **Branch:** `feature/ORAN_MVP_1_Py3_13` | **Commits:** `007c971`, `2110bbd`
  - **Skill used:** `document-cross-reference-analysis` (single mode), extraction lenses: `document-analysis-a1tp`, `document-analysis-a1td`
  - **Trace IDs:** ORAN-FTM-002, ORAN-FTM-004
  - **Sections analyzed:** §5.2.4.1 (HTTP mapping table), §5.2.4.2 (Query policy identifiers), §5.2.4.3 (Create policy), §5.2.4.4 (Update policy), §5.2.4.5 (Query policy), §5.2.4.6 (Delete policy), §5.2.4.7 (Query policy status), §5.2.4.8 (Notify policy status)
  - **Key findings:**
    - Create and Update both use `PUT`; upsert semantics — existence of resource determines 201 vs 200.
    - `policyId` is consumer-generated (not server-assigned); included in PUT URI.
    - `notificationDestination` is a query parameter on PUT (not request body); omitting it cancels existing subscription (§5.2.4.4.1).
    - Notify policy status (§5.2.4.8) reverses HTTP roles: A1-P Producer acts as HTTP Client, Consumer exposes callback HTTP Server endpoint.
    - `policyTypeId` drives server-side JSON schema selection for `PolicyObject` and `PolicyStatusObject` validation.
    - "Query all" patterns are client-side iteration, not single server endpoints.
  - **Implementation verdict:** Spec-compliant implementation delivered; `notificationDestination` moved to query param, upsert status codes corrected, missing routes and service methods added.
  - **Actions taken:**
    - Added `list_policy_ids(policy_type_id)` to `A1PolicyService` for §5.2.4.2 query policy identifiers
    - Changed `create_or_replace_policy()` return to `(PolicyObject, was_created: bool)` for 201 vs 200 differentiation
    - Made `notification_destination` Optional in `create_or_replace_policy()`; omission cancels subscription
    - Added `async notify_policy_status(destination, status_obj)` — outbound HTTP POST via `httpx` (§5.2.4.8)
    - Added `GET /a1/policytypes/{policyTypeId}/policies` route to `oran.py` (§5.2.4.2)
    - Fixed `PUT` route: `notificationDestination` as query param, returns 201+`Location` for create / 200 for update
    - Updated `ORAN/docs/feature_traceability_map.md` — ORAN-FTM-002 source reference extended to include §5.2.4
    - Updated `tests/unit/services/test_a1_policy_service.py` — unpack `(policy, was_created)` tuple
  - **Test results:** 7 unit + 15 nonfunctional tests — all pass

- [x] **Analyze TS 103 987 §5.2.3 — Service operations for A1 policy types**
  - **Completed:** 2026-06-25 | **Branch:** `feature/ORAN_MVP_1_Py3_13` | **Commits:** `5f8f299`, `f5623bd`
  - **Skill used:** `document-cross-reference-analysis` (single mode), extraction lens: `document-analysis-a1tp`
  - **Trace IDs:** ORAN-FTM-002, ORAN-FTM-004
  - **Sections analyzed:** §5.2.3.1 (HTTP mapping table), §5.2.3.2 (Query policy type identifiers), §5.2.3.3.1–5.2.3.3.4 (Query policy type — single/multiple/all procedures)
  - **Key findings:**
    - Policy type operations are read-only (GET only); no POST/PUT/DELETE on policy types.
    - `GET /policytypes` MUST return `200 []` (not 404) when no types are registered.
    - `GET /policytypes/{policyTypeId}` MUST return `404` (normative SHALL) for unknown ids.
    - "Query all policy types" is a client-side iteration pattern, not a server endpoint.
  - **Implementation verdict:** Current code in `demo-web/backend/app/api/oran.py` is conformant; no structural changes required.
  - **Actions taken:**
    - Added interface contract tests: `test_list_policy_types_returns_200_with_empty_array_when_no_types_registered`, `test_get_unknown_policy_type_returns_404` → `tests/interface/api/test_oran_a1_policy_api.py`
    - Added unit tests: `test_list_policy_type_ids_returns_empty_list_when_store_is_cleared`, `test_get_policy_type_raises_key_error_for_unknown_type_id` → `tests/unit/services/test_a1_policy_service.py`
    - Added component test: `test_problem_details_component_shape_for_policy_type_not_found` → `tests/component/api/test_problem_details_component.py`
    - Added 6 parameter boundary tests for `policyTypeId` → `tests/nonfunctional/parameter/test_a1_policy_parameter_passing.py`
    - Updated `ORAN/docs/feature_traceability_map.md` — ORAN-FTM-002 source reference extended to include §5.2.3
    - Updated `tests/regression/impact-map.yaml` and `tests/regression/selectors.md`
  - **Analysis artifact:** `ORAN/docs/section_5_2_3_analysis.md` (not created — analysis delivered inline per session)

- [x] **Analyze TS 103 989 §4.1 — General test methodology for A1 interface**
  - **Completed:** 2026-06-25 | **Branch:** `feature/ORAN_MVP_1_Py3_13` | **Commits:** inline
  - **Skill used:** `document-cross-reference-analysis` (single mode), extraction lens: `document-analysis-a1tp`, support lens: `document-rule-learning`
  - **Trace IDs:** ORAN-FTM-005, ORAN-FTM-006, ORAN-FTM-007, ORAN-FTM-008
  - **Document:** `ORAN/docs/ts_103989v040200p.pdf` (v4.2.0)
  - **Section analyzed:** §4.1 (General)
  - **Key findings:**
    - Test methodology is split into conformance testing and interoperability testing for the A1 interface between Non-RT RIC and Near-RT RIC.
    - Conformance testing is simulator-driven and requires configurable HTTP `GET`, `PUT`, `POST`, and `DELETE` behavior.
    - URI, headers, and body must remain configurable to derive multiple test cases from common A1 procedures.
    - Interoperability testing assumes real devices under test, with surrounding systems allowed to be real or simulated.
    - The spec favors scenario-driven validation of A1 behavior, which supports a strict TDD-first implementation flow.
  - **Implementation verdict:** The current ORAN prototype plan should treat simulator-backed conformance tests as the entry point for all new A1 feature work, with interoperability scenarios promoted only after conformance is green.
  - **Actions taken:**
    - Created analysis artifact: `ORAN/docs/section_4_1_analysis.md`
    - Updated `ORAN/IMPLEMENTATION_PLAN.md` with a TS 103 989 §4.1-driven TDD development approach and verification additions
  - **Follow-up status:**
    - ✅ Scenario classification for conformance vs interoperability implemented in parser/catalog flows.
    - ✅ Simulator capability tests for configurable HTTP operations implemented in conformance harness coverage.
    - [ ] Keep new A1 route/service work gated on failing spec-derived conformance tests (process/CI policy still to be formalized if required).

- [x] **Commit and push TS 103 989 §4.1 analysis and scenario-classification implementation**
  - **Completed:** 2026-06-25 | **Branch:** `feature/ORAN_MVP_1_Py3_13` | **Commit:** `f010d8e`
  - **Scope:** ORAN analysis artifact, TDD planning updates, parser/catalog scenario classification, persistence metadata, and `/test-cases` API metadata support
  - **Remote:** `origin/feature/ORAN_MVP_1_Py3_13`
  - **Verification:** Narrow regression passed before push for scenario classification and persistence/API metadata (`7 passed`)

- [x] **P1-ENH: Analyze TS 103 987 §5.3 — Enrichment Information Service**
  - **Completed:** 2026-07-02 | **Trace ID:** `ORAN-FTM-014`
  - **Priority:** P1-ENH
  - **Skill used:** `document-analysis-a1tp` as primary, `document-cross-reference-analysis` as orchestrator
  - **Document:** `ORAN/docs/ts_103987v040300p.pdf` (v4.3.0)
  - **Section analyzed:** §5.3 (Enrichment Information Service)
  - **Key findings:**
    - EI type discovery and EI job lifecycle behavior are implemented end-to-end.
    - Top-level EI job listing was added with optional `eiTypeId` filtering to align with §5.3.4.2.
    - EI job payloads now preserve `jobStatusNotificationUri` and `jobResultUri` as part of the stored EiJobObject.
    - Added typed EI models for EiTypeObject, EiJobObject, EiJobStatusObject, and EiJobResultObject.
    - Callback/result delivery paths are covered by unit tests and conformance harness checks.
  - **Implementation impact:**
    - Updated `demo-web/backend/app/models/oran.py` with EI-specific Pydantic models.
    - Updated `demo-web/backend/app/services/a1_enrichment_service.py` to store typed EI jobs, support optional job listing, and validate EI status/result payloads.
    - Updated `demo-web/backend/app/api/oran.py` to expose `/a1/eijobs` and preserve callback URIs on create/update.
    - Updated conformance and API tests for EI lifecycle, callback persistence, and top-level job queries.
  - **Verification:**
    - Focused regression passed: 16 tests in `demo-web/backend/tests/unit/services/test_a1_enrichment_service.py` and `demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py`.
    - Clause-level interoperability harness coverage for A1-EI remains green and includes EI result delivery.
    - Retained evidence recorded under `ORAN/docs/coverage/evidence/s7-20260702024430/`.

- [x] **P1-ENH: Implement TS 103 989 §4.2.1 and §4.2.2 conformance setup coverage**
  - **Completed:** 2026-06-30 | **Branch:** `feature/ORAN_MVP_1_Py3_13` (in progress)
  - **Priority:** P1-ENH
  - **Source:** `ORAN/docs/ts_103989v040200p.pdf` (v4.2.0), sections §4.2.1 and §4.2.2
  - **Objective:** Closed — Implemented and verified Non-RT RIC conformance setup coverage.
  - **Completed items:**
    - ✅ Added explicit section traceability (ORAN-FTM-013) with Test References for §4.2.1 and §4.2.2 in `ORAN/docs/feature_traceability_map.md`
    - ✅ Added DUT readiness checks for Non-RT RIC role behavior and agreed policy type preconditions: `tests/conformance/test_non_rt_ric_dut_readiness.py` (9 tests)
    - ✅ Added simulator capability verification for A1-P Producer (enable/disable, configurable responses, HTTP Client/Server) and A1-EI Consumer (service role, resource domains): `tests/conformance/test_simulator_capabilities.py` (16 tests)
    - ✅ Added mandatory execution evidence checks (message logging, deterministic status codes, ProblemDetails error payloads, enforcement_reason verdict fields): `tests/conformance/test_execution_evidence.py` (10 tests)
    - ✅ Updated `ORAN/docs/feature_traceability_map.md` with ORAN-FTM-013, mapping to code scope and test perspectives
    - ✅ Updated `tests/regression/impact-map.yaml` with conformance test suite (35 tests)
    - ✅ Updated `tests/regression/selectors.md` with §4.2.1/§4.2.2 conformance smoke run and full regression suite
    - ✅ Created formal analysis artifact: `ORAN/docs/section_4_2_analysis.md` (document-analysis-a1tp skill extraction)
  - **Output artifacts:**
    - New conformance test suite: 35 tests covering DUT readiness, simulator capabilities, execution evidence (80%+ coverage §4.2.1–§4.2.2)
    - Analysis document with HTTP definitions, REST patterns, data formats, protocol semantics, implementation mapping, version notes, enhancement recommendations
    - Updated traceability and regression infrastructure aligned with new tests

- [x] **P1-ENH: Implement and reconcile TS 103 989 §4.4 interoperability coverage**
  - **Status:** Complete
  - **Date:** 2026-07-02
  - **Source:** `ORAN/docs/ts_103989v040200p.pdf` (v4.2.0), sections §4.4.1, §4.4.2, clause 7.2, clause 7.3
  - **Objective:** Deliver clause-level interoperability coverage for section 7 with retained verification evidence and traceability closure.
  - **Completed in this session:**
    - ✅ Expanded the conformance harness from placeholder 4-test suites to clause-level section 7 coverage: 9 A1-P checks and 11 A1-EI checks.
    - ✅ Added retained A1-EI result-delivery support in `demo-web/backend/app/services/a1_enrichment_service.py` via `deliver_ei_job_result()`.
    - ✅ Verified interoperability API, backend, readiness, and service tests:
      - `demo-web/tests/conformance/test_interoperability_conformance_4_4.py`
      - `demo-web/backend/tests/conformance/test_interoperability_readiness_4_4_2.py`
      - `demo-web/backend/tests/conformance/test_interoperability_clause7_suites.py`
      - `demo-web/backend/tests/unit/services/test_a1_enrichment_service.py`
    - ✅ Captured retained section 7 artifacts:
      - `ORAN/docs/test-policy/ts_103989_section7_policy_checklist.md`
      - `ORAN/docs/test-policy/ts_103989_section7_test_policy_report.md`
      - `ORAN/docs/coverage/ts_103989_section7_clause_coverage_matrix.md`
      - `ORAN/docs/coverage/ts_103989_section7_verification_run_summary.md`
      - `ORAN/docs/coverage/evidence/s7-20260702024430/`
    - ✅ Verified focused regression for §4.4 coverage (`26 passed`).

- [x] **P1-ENH: Analyze and implement TS 103 983 Section 4 conformance coverage (including Figure 4.1.2-1 topology contracts)**
  - **Status:** Complete
  - **Date:** 2026-07-02
  - **Source:** `ORAN/docs/ts_103983v040000p.pdf` (v4.0.0), sections §4.1, §4.2, §4.3, §4.4 and Figure 4.1.2-1
  - **Skill used:** `document-analysis-a1tp` (primary), `document-cross-reference-analysis` (single mode orchestrator)
  - **Trace ID:** `ORAN-FTM-015`
  - **Objective:** Establish explicit TS 103 983 section-4 coverage with executable conformance tests and matrixed evidence (instead of indirect-only coverage through TS 103 987/989).
  - **Completed in this session:**
    - ✅ Added dedicated section-4 principles conformance suite:
      - `demo-web/backend/tests/conformance/test_ts103983_section4_principles.py`
      - Covers A1 service architecture assertions, policy/EI lifecycle behavior, and ProblemDetails error contract checks.
    - ✅ Added section-4.1.2 topology/interaction contract suite:
      - `demo-web/backend/tests/conformance/test_ts103983_section4_topology_contracts.py`
      - Covers Figure 4.1.2-1 entity/interface presence, MVP profile alignment, O1 validator semantics, E2 validator semantics, and deterministic stub status behavior.
    - ✅ Updated regression mapping artifacts:
      - `demo-web/backend/tests/regression/selectors.md`
      - `demo-web/backend/tests/regression/impact-map.yaml`
    - ✅ Created and then updated clause matrix artifact:
      - `ORAN/docs/coverage/ts_103983_section4_clause_coverage_matrix.md`
      - Current summary: `covered=4`, `partial=4`, `missing=1`.
    - ✅ Added and updated traceability row:
      - `ORAN/docs/feature_traceability_map.md` (`ORAN-FTM-015`)
    - ✅ Updated plan-level summary for future navigation:
      - `ORAN/FEATURE_PLAN.md`
  - **Verification:**
    - TS 103 983 section-4 principles suite: `10 passed`.
    - TS 103 983 section-4.1.2 topology contracts suite: `8 passed`.
  - **Residual gaps (tracked):**
    - A1-ML capability remains unimplemented for §4.1.3.3 / §4.4.
    - O1/E2 coverage is currently contract/stub-level; full integration message-flow behavior remains pending.
    - §4.2 extensibility/backward-compatibility assertions still need explicit tests.

- [x] **P1-ENH: Analyze TS 103 983 Section 5 and enrich existing A1 interface design/code**
  - **Status:** Complete
  - **Date:** 2026-07-07
  - **Source:** `ORAN/docs/ts_103983v040000p.pdf` (v4.0.0), section §5 (`§5.1`, `§5.2`)
  - **Skill used:** `document-analysis-a1tp` (primary), `document-cross-reference-analysis` (single mode orchestrator)
  - **Trace IDs:** `ORAN-FTM-001`, `ORAN-FTM-002`, `ORAN-FTM-003`, `ORAN-FTM-004`, `ORAN-FTM-016`
  - **Objective:** Map TS 103 983 section-5 A1 function clauses to existing A1-P/A1-EI design and code, identify implementation gaps, and prepare the next enrichment slice.
  - **Completed in this session:**
    - ✅ Analyzed body clauses for `§5`, `§5.1`, and `§5.2` from `ORAN/docs/ts_103983v040000p.pdf`.
    - ✅ Created section-5 clause coverage matrix artifact:
      - `ORAN/docs/coverage/ts_103983_section5_clause_coverage_matrix.md`
      - Current summary: `covered=8`, `partial=9`, `missing=1`.
    - ✅ Updated traceability mapping with dedicated section-5 feature row:
      - `ORAN/docs/feature_traceability_map.md` (`ORAN-FTM-016`)
    - ✅ Mapped current implementation anchors for A1 service registry, A1-P, A1-EI, router flows, and current conformance coverage.
  - **Completed in this session (implementation enrichment):**
    - ✅ Added policy scope discriminator validation for section `§5.1.4.1` to `§5.1.4.5` in `demo-web/backend/app/services/a1_policy_service.py`.
    - ✅ Added explicit policy lifecycle transition helper for `§5.1.3` semantics (`ACCEPTED`/`ENFORCED`/`NOT_ENFORCED`) in `demo-web/backend/app/services/a1_policy_service.py`.
    - ✅ Added EI lifecycle restart reconciliation helper for `§5.2.3.3.1` in `demo-web/backend/app/services/a1_enrichment_service.py`.
    - ✅ Added EI delivery-failure resilience behavior for `§5.2.3.3.2` (non-buffering expectation via deterministic `DISABLED` status) in `demo-web/backend/app/services/a1_enrichment_service.py`.
    - ✅ Added explicit section-5 A1-ML scope decision (`out_of_scope`) in A1 service summaries.
    - ✅ Added dedicated section-5 conformance suites:
      - `demo-web/backend/tests/conformance/test_ts103983_section5_policy_scope_identifiers.py`
      - `demo-web/backend/tests/conformance/test_ts103983_section5_policy_lifecycle_transitions.py`
      - `demo-web/backend/tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py`
      - `demo-web/backend/tests/conformance/test_ts103983_section5_capability_summary.py`
    - ✅ Verification run: focused regression completed with `61 passed`.
  - **Residual follow-up (non-blocking):**
    - [x] Optional hardening for `§5.1.5` policy statement objective/resource taxonomy profile.
    - [x] Optional push-delivery callback contract and deterministic non-buffering checks for `§5.2.5` and `§5.2.5.1`.
    - [ ] Optional future enhancement: explicit retry/backoff policy profile for push delivery.
  - **Post-analysis orchestration:** Executed on 2026-07-07 after explicit user confirmation; fail-closed gate status is now `PASS`.
    - Test policy report: `ORAN/docs/test-policy/ts_103983_section5_test_policy_report.md`
    - Verification summary: `ORAN/docs/coverage/ts_103983_section5_verification_run_summary.md`
    - Evidence artifacts:
      - `ORAN/docs/coverage/evidence/ts_103983_section5_config_snapshot.yaml`
      - `ORAN/docs/coverage/evidence/ts_103983_section5_protocol_message_evidence.md`
  - **Notes:** Section-5 implementation enrichment is complete for the previously tracked blockers, and historical 2026-07-02 closure evidence remains in coverage artifacts.

### ✅ Phase 1: ORAN Foundation (Backend + Frontend)
**Status:** ✅ COMPLETE (100%)  
**Estimated:** 5-6 days  
**Actual:** Completed January 2026  
**Priority:** HIGH  
**Branch:** `feature/ORAN_MVP_1`  
**Commits:** 2 (Backend: 8753e16, Frontend: e02e8e6)

#### Backend Implementation ✅

- [x] **Task 1.1:** Create OranExecutionService
  - File: `backend/app/services/oran_execution_service.py` (269 lines) ✅
  - Extend ExecutionService, override `_build_jmeter_command` → `_build_pytest_command`
  - Reuse subprocess spawning + WebSocket streaming pattern
  - Command: `pytest {test_file} --json-report --json-report-file={result.json} -v`

- [x] **Task 1.2:** Create OranParser
  - File: `backend/app/parsers/oran_parser.py` (286 lines) ✅
  - Parse pytest JSON output format
  - Extract statistics (total, passed, failed, success_rate)
  - Extract O-RAN KPIs (latency, throughput, conformance status)

- [x] **Task 1.3:** Define ORAN data models
  - File: `backend/app/models/oran.py` (285 lines) ✅
  - Models: `OranTestCatalog`, `OranTestCase`, `OranExecutionResult`, `OranKpiMetrics`
  - Models: `TestClause`, `TestSemantics`, `EnrichedTestCase`, `SpecConflict` (Phase 2 ready)
  - Enums: `SpecType`, `HttpMethod`

- [x] **Task 1.4:** Add ORAN API endpoints
  - File: `backend/app/api/oran.py` (303 lines) ✅
  - 15 endpoints: upload-specs, generate, catalogs, scripts, execute, status, cancel, etc.
  - All endpoints documented with FastAPI automatic OpenAPI docs

- [x] **Task 1.5:** Write unit tests for Phase 1
  - File: `backend/verify_phase1.py` (100 lines) ✅
  - 5 API endpoint tests (health, config, catalogs, statistics, docs)

- [x] **Task 1.6:** Create infrastructure directories and update config
  - Created: `backend/data/oran_catalogs/` ✅
  - Created: `backend/data/oran_history/` ✅
  - Created: `backend/generated_tests/` ✅
  - Created: `backend/templates/oran/` ✅
  - Updated: `config.py`, `main.py`, `requirements.txt`, `.env.example` ✅
  - Added: 7 new Python dependencies ✅

#### Frontend Implementation ✅

- [x] **Task 1.7:** Hide TTS tabs and add ORAN tabs
  - File: `frontend/templates/index.html` (complete rewrite) ✅
  - Removed: "Demos" tab, "Traffic Generator" tab
  - Added: "Upload Specs" tab, "Test Catalog" tab
  - Kept: "Execution" tab, "History" tab (shared functionality)
  - Updated branding: "O-RAN A1 Test Generation Tool"

- [x] **Task 1.8:** Create Upload Specs UI
  - 4 file upload cards for ETSI specs (TS 103 989/987/988/983) ✅
  - Upload progress bar with animation ✅
  - Generation controls (catalog name, description) ✅
  - Real-time generation status log ✅

- [x] **Task 1.9:** Create Test Catalog UI
  - Grid layout of catalog cards ✅
  - Expandable catalog details panel ✅
  - Test cases table with color-coded badges ✅
  - Method badges (GET/POST/PUT/DELETE/PATCH) ✅
  - Status badges (2xx/4xx/5xx) ✅
  - Complexity badges (Basic/Intermediate/Advanced) ✅

- [x] **Task 1.10:** Create Script Viewer Modal
  - Large modal (900px) for pytest scripts ✅
  - Prism.js syntax highlighting (Python) ✅
  - Download and Copy to Clipboard buttons ✅
  - Dark theme (prism-tomorrow) ✅

- [x] **Task 1.11:** Create ORAN JavaScript module
  - File: `frontend/static/js/oran.js` (377 lines) ✅
  - ES6 module with exports ✅
  - Spec upload functionality ✅
  - Catalog display and management ✅
  - Script viewer with Prism.js integration ✅
  - Test execution API calls ✅

- [x] **Task 1.12:** Create ORAN CSS styles
  - File: `frontend/static/css/oran.css` (488 lines) ✅
  - Responsive grid layouts ✅
  - Card-based UI with hover effects ✅
  - Color-coded badges ✅
  - Modal styling ✅
  - ORAN-specific color palette ✅

- [x] **Task 1.13:** Update main app.js
  - Import and initialize ORAN module ✅
  - Disable old TTS features (demos, traffic) ✅
  - Keep shared functionality (execution, history) ✅

**Phase 1 Deliverables:**
- ✅ **Backend:** 1,180+ lines of production code
- ✅ **Frontend:** 1,346+ lines of code (HTML, JS, CSS)
- ✅ 15 API endpoints operational
- ✅ Real-time WebSocket streaming
- ✅ Pytest execution with KPI calculation
- ✅ Complete ORAN-only UI on feature branch
- ✅ Prism.js syntax highlighting
- ✅ Responsive design
- ✅ Full API documentation (Swagger UI)

**See**: 
- [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) - Backend details
- [PHASE1_FRONTEND_COMPLETE.md](PHASE1_FRONTEND_COMPLETE.md) - Frontend details

---

### Phase 2: Spec Parsing Pipeline
**Status:** ✅ COMPLETE  
**Completed:** 2026-06-27  
**Priority:** HIGH  
**Depends on:** Phase 1 ✅

- [x] **Task 2.1:** Implement document ingestion
  - File: `backend/app/parsers/pdf_parser.py` — `PdfParser` with `parse_file`, `extract_by_page`, `get_page_count`, `extract_page_range`
  - File: `backend/app/parsers/docx_parser.py` — `DocxParser` with `parse_file`, `extract_paragraphs`, `extract_with_formatting`
  - Dependencies: `pypdf==3.17.0`, `python-docx==1.1.0` (already in requirements.txt)

- [x] **Task 2.2:** Extract test clauses from specs
  - File: `backend/app/parsers/test_clause_extractor.py` — `TestClauseExtractor`
  - Method: `extract_clauses(spec_text, spec_type, max_tests)` with regex section splitting and test-section filtering
  - Clause fields: clause_number, title, description, entrance_criteria, methodology, expected_result, scenario_type, page_number

- [x] **Task 2.3:** Semantic extraction from clauses
  - Method: `extract_http_info(text)` — extracts HTTP method, endpoint path, status code via regex
  - `TestSemantics` model carries: http_method, endpoint, expected_status, payload_type, assertions, scenario_type

- [x] **Task 2.4:** Cross-reference multiple specs
  - Method: `cross_reference_specs(all_clauses)` in `SpecParserService`
  - Uses TS 103 989 as base; enriches with endpoint from TS 103 987 and status code from TS 103 988
  - Priority order: TS_103_989 → TS_103_987 → TS_103_988 → TS_103_983

- [x] **Task 2.5:** Implement conflict storage
  - Methods: `detect_conflicts(enriched_cases)`, `save_conflicts(output_path)` in `SpecParserService`
  - Storage: `data/oran_catalogs/spec_conflicts.json`
  - New endpoint: `GET /api/oran/conflicts` returns all stored conflicts

- [x] **Task 2.6:** Write unit tests for Phase 2
  - File: `tests/unit/services/test_phase2_spec_parsing.py` — 24 tests (all pass)
  - Covers: PdfParser, DocxParser, TestClauseExtractor, extract_http_info, cross_reference_specs, detect_conflicts, save_conflicts, complexity determination

---

### ✅ Phase 3: Test Generation Engine
**Status:** ✅ COMPLETE  
**Completed:** 2026-06-27  
**Priority:** HIGH  
**Depends on:** Phase 2 Task 2.4

- [x] **Task 3.1:** Generate JSON test catalog
  - File: `backend/app/services/test_generator_service.py`
  - Method: `generate_catalog(enriched_cases: List[EnrichedTestCase]) -> OranTestCatalog`
  - Save to: `backend/data/oran_catalogs/{catalog_id}.json`

- [x] **Task 3.2:** Create Jinja2 pytest templates
  - Directory: `backend/templates/oran/`
  - Template: `a1_test.py.j2` for pytest script generation
  - Template: `test_config.yaml.j2` for test configuration
  - Dependency `jinja2==3.1.2` already in requirements.txt

- [x] **Task 3.3:** Implement pytest script generation
  - Method: `generate_pytest_script(catalog: OranTestCatalog) -> Path`
  - Method: `generate_test_config(catalog: OranTestCatalog) -> Path`
  - Renders Jinja2 templates, saves to: `generated_tests/{catalog_id}.py` + `_config.yaml`
  - Called automatically from `/generate` and `/generate-from-selection` endpoints

- [x] **Task 3.4:** Create ORAN test configuration
  - YAML config: `generated_tests/{catalog_id}_config.yaml`
  - Fields: test_environment, simulator config, timeouts, retries, catalog metadata

- [x] **Task 3.5:** Write unit tests for Phase 3
  - File: `tests/unit/services/test_phase3_catalog_generation.py` — 21 tests (all pass)
  - Test catalog generation (validate JSON schema)
  - Test template rendering (verify Python syntax)
  - Integration test: Full pipeline spec → catalog → script → execute

---

### Phase 4: Frontend Enhancements
**Status:** ⏸️ Not Started (Basic UI Completed in Phase 1)  
**Estimated:** 2-3 days  
**Priority:** MEDIUM  
**Depends on:** Phases 1 ✅, 2, 3

**Note:** Phase 1 already included complete frontend UI. Phase 4 focuses on advanced visualizations and features.

- [x] **Task 4.1:** Add ORAN upload UI ✅ COMPLETED IN PHASE 1
  - File: `frontend/templates/index.html` ✅
  - 4 file upload inputs for ETSI specs (TS 103 989/987/988/983) ✅
  - Upload progress bar ✅
  - Generation status log ✅

- [x] **Task 4.2:** Display generated test catalog ✅ COMPLETED IN PHASE 1
  - File: `frontend/static/js/oran.js` ✅
  - Function: `loadCatalogs()`, `displayCatalogs()`, `viewCatalogTests()` ✅
  - Grid layout with catalog cards ✅
  - Expandable catalog details with test cases table ✅
  - "View Script" button opens modal with Prism.js syntax highlighting ✅

- [x] **Task 4.3:** Integrate ORAN execution flow ✅ COMPLETED IN PHASE 1
  - "Run" button for each test case ✅
  - Call `POST /api/oran/execute` with test_id ✅
  - Auto-switch to Execution tab ✅
  - WebSocket reused from TTS (streams pytest output) ✅

- [ ] **Task 4.4:** Add ORAN-specific visualizations (ADVANCED)
  - Replace static output with ORAN topology view
  - Option 1: vis.js network diagram (Nodes: IUT, A1 Simulator, RIC)
  - Option 2: Mermaid.js sequence diagrams for A1 message flows
  - ORAN KPIs panel with Plotly.js charts:
    - Latency histogram (P50, P95, P99)
    - Throughput line chart over time
    - Conformance rate gauge chart
  - Per-endpoint response time comparison

- [ ] **Task 4.5:** Implement conflict review UI
  - Add "Conflicts" tab in catalog details
  - Table showing spec conflicts from cross-referencing
  - Actions: View details, Override resolution, Export conflicts
  - Backend endpoint: `GET /api/oran/conflicts`

- [ ] **Task 4.6:** Add code editor for script customization
  - Integrate Monaco Editor or CodeMirror
  - "Edit Script" button in script modal
  - Python syntax highlighting, auto-completion
  - Save custom version: `POST /api/oran/scripts/{test_id}/customize`
  - Diff view showing changes from original

- [ ] **Task 4.7:** Enhance execution monitoring
  - Live KPI updates during test execution (WebSocket)
  - Progress bar showing test suite completion
  - Real-time charts updating as tests complete

- [ ] **Task 4.8:** Write E2E tests for frontend
  - File: `tests/e2e/test_oran_workflow.py` (Playwright)
  - Test: Upload specs → generate → view catalog → execute → view results

---

## � ENHANCEMENTS

### [P1-ENH] Simplify Upload Specs Tab — Dedicated Document Management
**Priority:** P1 (High)  
**Type:** Enhancement  
**Status:** 📋 Planned  
**Estimated:** 1-2 days  
**Added:** June 2026

#### Context
The current "Upload Specs" tab mixes two distinct concerns: (1) uploading/managing specification documents and (2) configuring and generating test catalogs. This makes the tab cluttered and confusing. The tab should do one thing well: manage specification documents.

#### Goal
Restrict the **Upload Specs** tab to document management only — uploading new specification PDFs or replacing an existing spec with a newer version. All catalog generation, methodology analysis, and extraction configuration moves to the **Test Catalog** tab.

#### Plan

**Step 1 — Redesign Upload Specs tab (frontend/templates/index.html + oran.js + oran.css)**
- [ ] Remove from Upload Specs tab:
  - Catalog Name / Description fields
  - MVP Demo Mode notice
  - Methodology Analysis panel
  - Rule-Based Extraction Settings panel
  - "Preview & Select Sections" button
  - "Generate Test Catalog (Auto)" button
- [ ] Redesign Upload Specs tab layout:
  - **Uploaded Specs Library** — table/card list showing all previously uploaded specs with: spec ID, title, version, upload date, file size, status (indexed / pending)
  - **Upload New Spec** — drag-and-drop zone or file-picker; user selects spec type (A1 / Diameter / etc.) before uploading
  - **Replace Existing Version** — if a spec with matching ID already exists, show a "Replace / Update Version" prompt instead of silently overwriting
  - Upload progress bar (keep existing)
  - Post-upload confirmation showing extracted metadata (page count, detected spec version)

**Step 2 — Move generation controls to Test Catalog tab (frontend/templates/index.html + oran.js)**
- [ ] Add a "Generate New Catalog" panel at the top of the Test Catalog tab:
  - Spec selection checkboxes (move from Upload Specs)
  - Protocol / Interface selector (move from Upload Specs)
  - Catalog Name + Description inputs
  - Methodology Analysis panel
  - Rule-Based Extraction toggle + rule pack status
  - "Generate Test Catalog (Auto)" button
  - "Preview & Select Sections" button

**Step 3 — Backend: add spec library endpoint**
- [ ] Add `GET /api/oran/specs` — returns list of all uploaded specs with metadata (id, title, version, upload_date, page_count, file_size_kb, status)
- [ ] Add `DELETE /api/oran/specs/{spec_id}` — removes a spec from the library
- [ ] Update `POST /api/oran/upload-specs` — detect duplicate spec ID and return `version_conflict: true` flag so frontend can prompt user to confirm replacement

**Step 4 — UX polish**
- [ ] Show a badge on the Upload Specs nav button indicating how many specs are currently in the library (e.g., "Upload Specs  4")
- [ ] Empty state: when no specs are uploaded, show a clear call-to-action card with drag-and-drop
- [ ] Warn user if they navigate to Test Catalog tab without any specs uploaded

#### Acceptance Criteria
- Upload Specs tab contains ONLY: spec library list, upload new spec, replace version, upload progress
- Test Catalog tab contains the full catalog generation workflow
- No functionality is lost — everything is preserved, just reorganised
- Existing uploaded specs remain accessible after the change

---
### [P1-ENH] Replace Checkbox Layout with Dropdown + Local File Upload
**Priority:** P1 (High)  
**Type:** Enhancement (Space Optimization)  
**Status:** 📋 Planned  
**Estimated:** 1-2 days  
**Added:** June 2026

#### Context
The current "Upload Specs" tab uses 4 visible checkboxes (one per spec: TS 103 989, 987, 988, 983) that consume significant vertical space. In the context of moving all catalog generation to the "Test Catalog" tab, the Upload Specs tab becomes compact—but the checkbox layout is still inefficient. Additionally, users should be able to upload any PDF/DOCX file from their machine into the tool's workspace.

#### Goal
Replace checkbox-based spec selection with a **dropdown selector** to minimize vertical space, and add an **"Upload New Spec"** button allowing users to upload arbitrary PDFs/DOCx files from any location on their machine, saving them to `C:\TestRepo\ORAN\Docs\` (auto-create if needed).

#### Current State
- 4 checkboxes visible for specs TS 103 989, 987, 988, 983
- Hidden file inputs with hardcoded spec IDs
- Upload triggered after spec selection

#### Plan

**Step 1 — Frontend: Replace checkboxes with dropdown (frontend/templates/index.html + oran.js + oran.css)**
- [ ] Remove the "Specification Selection" checkbox group from HTML
- [ ] Add a new single dropdown `<select id="spec-select-dropdown">`:
  - Options: TS 103 989, TS 103 987, TS 103 988, TS 103 983
  - Can select only ONE spec at a time (MVP constraint to match new simplicity goal)
  - Default selection: TS 103 989
- [ ] Add an "Upload New Spec" button beside the dropdown:
  - Opens a file picker dialog (accept `.pdf`, `.docx`)
  - User selects file from anywhere on machine
  - File is copied to `C:\TestRepo\ORAN\Docs\` with original filename preserved
  - UI shows upload progress (keep existing progress bar)
  - Post-upload: show success confirmation with file location and extracted metadata
- [ ] Update CSS: Dropdown should be compact, horizontally aligned with button on same line to save space
- [ ] Remove hidden file inputs for pre-defined specs (no longer needed; upload is triggered by button click)

**Step 2 — Backend: Add file upload and workspace management endpoints**
- [ ] Create directory helper:
  - Ensure `C:\TestRepo\ORAN\Docs\` exists (create if missing on startup)
  - Validate write permissions
- [ ] Add `POST /api/oran/upload-spec-file` — accepts multipart file upload:
  - Input: file (PDF or DOCX), optional spec_type (A1 / Diameter / etc., default="A1")
  - Validation: max 50 MB, only .pdf or .docx
  - Action: Save file to `C:\TestRepo\ORAN\Docs\{original_filename}`
  - Handle duplicates: if file already exists, prompt user to overwrite or rename (return `file_exists: true` flag)
  - Extract metadata: file size, page count (for PDFs), detected spec version/title if possible
  - Response: `{ "status": "success", "file_path": "...", "file_size_kb": ..., "page_count": ..., "metadata": {...} }`
- [ ] Add `GET /api/oran/workspace-specs` — lists all PDFs/DOCx files in `C:\TestRepo\ORAN\Docs\`:
  - Returns: filename, file_type, file_size_kb, upload_date, page_count (if PDF)
  - Used to populate dropdown or library display on Upload Specs tab

**Step 3 — Integration: Update spec selection flow**
- [ ] Dropdown selects which pre-defined spec mapping to use (TS 103 989 → A1 Test Specification, etc.)
- [ ] "Upload New Spec" adds a new arbitrary spec file to the workspace
- [ ] Spec library list on Upload Specs tab shows both pre-defined specs AND user-uploaded files
- [ ] JavaScript: Listen to dropdown change and file upload button; trigger appropriate backend calls

**Step 4 — UX polish**
- [ ] Empty state: if no specs in workspace, show message: "No specs uploaded yet. Use 'Upload New Spec' to add a PDF or Word document."
- [ ] Drag-and-drop alternative: allow drag-and-drop of files onto the upload area (in addition to file picker button)
- [ ] File list display: show uploaded files as a compact list with delete icons (right of each file)
- [ ] Validation feedback: show error messages for invalid file types, max size exceeded, etc.
- [ ] Success toast: on successful upload, show "✓ Spec uploaded: {filename}"

#### Acceptance Criteria
- Checkbox layout completely removed
- Single dropdown selector visible with 4 ETSI spec options
- "Upload New Spec" button next to dropdown (horizontal alignment)
- Users can upload arbitrary PDF/DOCX files from any machine location → saves to `C:\TestRepo\ORAN\Docs\`
- File list shows all uploaded files with delete option
- Vertical space saved: ~150px (4 checkboxes + labels removed)
- No functionality lost; catalog generation workflow unchanged
- Pre-defined specs and user-uploaded specs coexist in the system

---
## �🔮 FUTURE ENHANCEMENTS (Post-MVP)

### 📌 TODO: ML-Based Spec Parsing (Option B Review)
**Priority:** MEDIUM  
**Estimated:** 2-3 weeks  
**Status:** Future Phase

**Context:** Currently using regex-based extraction (Option A). Review feasibility of ML/NLP approach for improved accuracy.

**Tasks:**
- [ ] Research NLP models for technical document parsing (BERT, GPT-4, specialized models)
- [ ] Prototype ML extraction on 10+ ETSI spec samples
- [ ] Compare accuracy: regex vs. ML (precision, recall, edge case handling)
- [ ] Cost/benefit analysis: accuracy improvement vs. infrastructure complexity
- [ ] Decision: Keep regex, add ML fallback, or full ML replacement

**Success Criteria:** 95%+ clause extraction accuracy, handles format variations

---

### 📌 TODO: Conflict Review UI Section
**Priority:** MEDIUM  
**Estimated:** 3-5 days  
**Status:** Future Phase  
**Depends on:** Phase 2 Task 2.5 (conflict storage)

**Context:** Cross-referencing 4 ETSI specs may produce conflicts (e.g., endpoint defined differently in TS 103 987 vs. 103 989). System logs conflicts but needs UI for review.

**Tasks:**
- [ ] Design conflict review panel in ORAN tab
  - Table columns: conflict_id, timestamp, specs involved, field, conflicting values, current resolution
  - Actions: View details, Change resolution, Mark as reviewed, Export conflicts
- [ ] Backend API: `GET /api/oran/conflicts`, `PUT /api/oran/conflicts/{id}/resolve`
- [ ] Conflict statistics dashboard: Total conflicts, by spec pair, by field type
- [ ] Auto-resolution rules configuration (e.g., always prefer TS 103 989 for endpoints)
- [ ] Conflict export: CSV/JSON for documentation

**Success Criteria:** Users can review all conflicts, override priority-based resolution, track resolution history

---

### 📌 TODO: In-Browser Code Editor (Phase 2 - Script Customization)
**Priority:** LOW  
**Estimated:** 1 week  
**Status:** Future Phase  
**Depends on:** Phase 3 Task 3.3 (script generation)

**Context:** Phase 1 uses read-only scripts with Download button. Phase 2 adds in-browser editing for customization before execution.

**Tasks:**
- [ ] Integrate Monaco Editor or CodeMirror into frontend
  - Python syntax highlighting
  - Auto-completion for pytest/requests libraries
  - Linting (Pylint/Flake8 integration)
- [ ] Backend: `POST /api/oran/scripts/{test_id}/customize` - Save custom edits
  - Versioning: Store original + custom versions
  - Metadata: edited_by, edited_at, change_summary
- [ ] UI: "Edit Script" button opens editor modal
  - "Save & Execute Custom" button triggers execution with custom version
  - "Revert to Original" button discards edits
  - "Diff View" shows changes from generated version
- [ ] Custom script persistence: `backend/generated_tests/{test_id}_custom.py`
- [ ] Execution service: Detect and use custom version if exists

**Success Criteria:** Users can edit generated scripts, save changes, execute custom versions, revert to original

---

## ⚙️ INFRASTRUCTURE TASKS

### Configuration Updates
- [ ] Update `backend/.env.example` with ORAN-specific variables:
  ```env
  ORAN_INSTALL_PATH=C:/ORAN
  ORAN_CLI_PATH=C:/ORAN/bin/oran-cli.sh
  ORAN_RIC_ENDPOINT=http://localhost:8080
  ORAN_DU_SIMULATION=true
  ORAN_CATALOGS_PATH=backend/data/oran_catalogs
  ORAN_GENERATED_TESTS_PATH=backend/generated_tests
  ```

- [ ] Update `backend/requirements.txt`:
  ```
  # Existing dependencies...
  
  # ORAN additions
  pypdf==3.17.0
  python-docx==1.1.0
  jinja2==3.1.2
  requests==2.31.0
  xmltodict==0.13.0
  pyyaml==6.0.1
  ```

### Directory Structure
- [ ] Create: `backend/data/oran_catalogs/`
- [ ] Create: `backend/data/oran_history/`
- [ ] Create: `backend/data/spec_conflicts.json`
- [ ] Create: `backend/generated_tests/`
- [ ] Create: `backend/templates/oran/`

---

## 📊 PROGRESS TRACKING

| Phase | Tasks | Completed | Status | Target Date |
|-------|-------|-----------|--------|-------------|
| Phase 1 (Backend + Frontend) | 13 | 13 | ✅ COMPLETE | January 2026 |
| Phase 2 (Spec Parsing) | 6 | 0 | ⏸️ Not Started | TBD |
| Phase 3 (Test Generation) | 5 | 0 | ⏸️ Not Started | TBD |
| Phase 4 (Advanced UI) | 5 | 0 | ⏸️ Not Started | TBD |
| **Total** | **29** | **13** | **45%** | **TBD** |

**Note:** Phase 1 included full frontend implementation (Tasks 1.7-1.13), not just backend.

**Future Enhancements:** 3 TODOs identified (ML parsing, Conflict UI, Code editor)

---

## ✅ COMPLETION CRITERIA

### ✅ Phase 1 Complete When: (ALL DONE ✅)
 [x] Update regression test docs
- [x] API integration complete in frontend ✅

### Phase 2 Complete When:
- [ ] PDF/DOCX ingestion works for ETSI specs
- [ ] 15+ test clauses extracted from sample spec
- [ ] Semantic extraction identifies HTTP method/endpoint/assertions
- [ ] Cross-reference merges 4 specs with conflict logging

### Phase 3 Complete When:
- [ ] JSON test catalog generated with valid schema
- [ ] Jinja2 templates render syntactically correct pytest scripts
- [ ] Generated scripts execute successfully with pytest
- [ ] YAML configs generated with correct structure

### Phase 4 Complete When:
- [ ] ORAN topology visualization renders (vis.js or Mermaid.js)
- [ ] KPI charts display with Plotly.js (latency, throughput, conformance)
- [ ] Conflict review UI functional
- [ ] Code editor integrated (Monaco/CodeMirror)
- [ ] Real-time KPI updates during execution
- [ ] E2E test passes: upload → generate → execute → visualize

**MVP Definition:** All 4 phases complete + all completion criteria met

**Current Status:** Phase 1 complete (Backend + Frontend), ready for Phase 2 (Spec Parsing)

---

**Documentation:**
- `IMPLEMENTATION_PLAN.md` - Full technical specification (329 lines)
- `PHASE1_COMPLETE.md` - Backend completion summary (276 lines)
- `PHASE1_FRONTEND_COMPLETE.md` - Frontend completion summary (500+ lines)

**Branch:** `feature/ORAN_MVP_1`  
**Commits:** 2 (Backend: 8753e16, Frontend: e02e8e6)  
**Total Lines:** ~2,526 backend + ~1,346 frontend = **3,872 lines of production code**
- All decisions logged with rationale (Option A/B/C selections)
- Database migration path planned for future (currently file-based)
