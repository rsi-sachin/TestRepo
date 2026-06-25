# Demo-Web ORAN Integration - TODO List

**Project:** Extend demo-web with O-RAN A1 test generation capabilities  
**Last Updated:** 2026-06-25  
**Status:** Phase 1 Complete (Backend + Frontend), Phase 2-4 Pending

## P1-ENH: Python 3.13 Migration Readiness and Implementation

Priority: P1-ENH
Status: In Progress
Owner Track: ORAN / demo-web backend and tests

Objective:
- Confirm and implement Python 3.13 compatibility for existing demo-web backend and test code that was previously developed for Python 3.11/3.12.

Scope:
- Dependency alignment in backend and test requirements.
- Runtime compatibility fixes for asyncio loop handling.
- FastAPI lifecycle/startup-shutdown compatibility hardening.
- Test harness validation for pytest and Playwright on Python 3.13.

Target Files:
- demo-web/backend/requirements.txt
- demo-web/tests/requirements.txt
- demo-web/backend/app/services/execution_service.py
- demo-web/backend/app/services/oran_execution_service.py
- demo-web/backend/app/websockets/demo_output.py
- demo-web/backend/app/main.py
- demo-web/backend/run.py
- demo-web/tests/conftest.py

Execution Plan:
- [ ] Capture baseline and run backend smoke checks on Python 3.13.
- [ ] Replace loop access patterns that can fail under stricter asyncio behavior.
- [ ] Align dependency versions for Python 3.13 compatibility.
- [ ] Run backend tests and classify/fix failures.
- [ ] Run Playwright E2E tests and classify/fix failures.
- [ ] Re-run regression matrix and confirm no critical compatibility blockers.

Exit Criteria:
- Backend starts successfully and `/health` returns healthy.
- Backend and E2E test flows run on Python 3.13.
- No critical runtime failures related to event loop handling or dependency incompatibility.
- Changes are committed on feature branch with PR against develop.

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
  - **Next steps:** Add scenario classification for conformance vs interoperability, add simulator capability tests for configurable HTTP operations, and keep new A1 route/service work gated on failing spec-derived conformance tests.

- [x] **Commit and push TS 103 989 §4.1 analysis and scenario-classification implementation**
  - **Completed:** 2026-06-25 | **Branch:** `feature/ORAN_MVP_1_Py3_13` | **Commit:** `f010d8e`
  - **Scope:** ORAN analysis artifact, TDD planning updates, parser/catalog scenario classification, persistence metadata, and `/test-cases` API metadata support
  - **Remote:** `origin/feature/ORAN_MVP_1_Py3_13`
  - **Verification:** Narrow regression passed before push for scenario classification and persistence/API metadata (`7 passed`)

- [ ] **P1-ENH: Analyze TS 103 987 §5.3 — Enrichment Information Service**
  - **Priority:** P1-ENH
  - **Skill to use:** `document-cross-reference-analysis` (single mode), extraction lens: `document-analysis-a1tp`
  - **Document:** `ORAN/docs/ts_103987v040300p.pdf` (v4.3.0)
  - **Section to analyze:** §5.3 (Enrichment Information Service)
  - **Expected output:** analysis notes, implementation impact, and TODO follow-ups for service models/routes/tests

- [ ] **P1-ENH: Implement TS 103 989 §4.2.1 and §4.2.2 conformance setup coverage**
  - **Priority:** P1-ENH
  - **Source:** `ORAN/docs/ts_103989v040200p.pdf` (v4.2.0), sections §4.2.1 and §4.2.2
  - **Objective:** Close pending implementation and verification gaps identified from Non-RT RIC conformance setup analysis.
  - **Pending items:**
    - Add explicit section traceability and test references for **both** §4.2.1 and §4.2.2 in ORAN test planning artifacts.
    - Add DUT readiness checks for Non-RT RIC role behavior and agreed policy type and/or EI type preconditions.
    - Add simulator capability verification for A1-P Producer and A1-EI Consumer behavior, including HTTP client/server handling, configurable request/response behavior, and message validation.
    - Add mandatory execution evidence checks per test run (message logs, headers/body/code validation, deterministic verdict reason).
    - Add or update a traceability mapping row in `ORAN/docs/feature_traceability_map.md` to explicitly include §4.2.1 and §4.2.2 source references and verification targets.
  - **Expected output:**
    - Updated test plan and quick reference entries with §4.2.1 + §4.2.2 coverage.
    - New or updated tests for DUT preconditions, simulator capabilities, and evidence completeness.
    - Traceability map update and regression impact-map update aligned with new tests.

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
**Status:** ⏸️ Not Started  
**Estimated:** 4-5 days  
**Priority:** HIGH  
**Depends on:** Phase 1 ✅

- [ ] **Task 2.1:** Implement document ingestion
  - File: `backend/app/services/spec_parser_service.py`
  - Method: `ingest_pdf(file_path: str) -> str` using pypdf
  - Method: `ingest_docx(file_path: str) -> str` using python-docx
  - Add dependencies: `pypdf==3.17.0`, `python-docx==1.1.0`

- [ ] **Task 2.2:** Extract test clauses from specs
  - Method: `extract_clauses(spec_text: str, spec_type: SpecType) -> List[TestClause]`
  - Regex patterns for ETSI clause format: `^\d+\.\d+\s+[A-Z]`
  - Parse: clause_number, title, description, entrance_criteria, methodology, expected_result
  - **DECISION IMPLEMENTED**: Regex-based extraction with manual JSON fallback

- [ ] **Task 2.3:** Semantic extraction from clauses
  - Method: `extract_test_semantics(clause: TestClause) -> TestSemantics`
  - Extract: HTTP method (GET/PUT/POST/DELETE), endpoint, payload type, assertions
  - Regex-based extraction for MVP

- [ ] **Task 2.4:** Cross-reference multiple specs
  - Method: `enrich_test_case(base_clause: TestClause, specs: Dict[SpecType, str]) -> EnrichedTestCase`
  - **DECISION IMPLEMENTED**: Priority order - TS 103 989 → TS 103 987 → TS 103 988
  - **ENHANCEMENT**: Log conflicts to JSON file for review

- [ ] **Task 2.5:** Implement conflict storage
  - File: `backend/data/spec_conflicts.json` (initial file-based storage)
  - Store: conflict_id, timestamp, spec1, spec2, field, value1, value2, resolution
  - Later migration path to database

- [ ] **Task 2.6:** Write unit tests for Phase 2
  - Test PDF ingestion with sample ETSI spec
  - Test clause extraction (verify 15+ clauses)
  - Test semantic extraction (HTTP method/endpoint detection)
  - Test cross-reference with conflict detection

---

### ✅ Phase 3: Test Generation Engine
**Status:** Not Started  
**Estimated:** 3-4 days  
**Priority:** HIGH  
**Depends on:** Phase 2 Task 2.4

- [ ] **Task 3.1:** Generate JSON test catalog
  - File: `backend/app/services/test_generator_service.py`
  - Method: `generate_catalog(enriched_cases: List[EnrichedTestCase]) -> OranTestCatalog`
  - Save to: `backend/data/oran_catalogs/{catalog_id}.json`

- [ ] **Task 3.2:** Create Jinja2 pytest templates
  - Directory: `backend/templates/oran/`
  - Template: `a1_test.py.j2` for pytest script generation
  - Template: `test_config.yaml.j2` for test configuration
  - Add dependency: `jinja2==3.1.2`

- [ ] **Task 3.3:** Implement pytest script generation
  - Method: `generate_pytest_script(catalog: OranTestCatalog) -> str`
  - Load Jinja2 template, render with catalog data
  - Save to: `backend/generated_tests/{test_id}.py`
  - **DECISION IMPLEMENTED**: Read-only scripts with Download button

- [ ] **Task 3.4:** Create ORAN test configuration
  - Generate YAML config: `backend/generated_tests/{test_id}_config.yaml`
  - Fields: test_environment, simulator config, timeouts, retries

- [ ] **Task 3.5:** Write unit tests for Phase 3
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
