# Demo-Web ORAN Integration - TODO List

**Project:** Extend demo-web with O-RAN A1 test generation capabilities  
**Last Updated:** January 2026  
**Status:** Phase 1 Complete (Backend + Frontend), Phase 2-4 Pending

---

## 📋 IMPLEMENTATION TASKS

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

## 🔮 FUTURE ENHANCEMENTS (Post-MVP)

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
- [x] OranExecutionService executes pytest subprocess successfully ✅
- [x] OranParser extracts statistics from pytest JSON output ✅
- [x] ORAN API endpoints respond correctly ✅
- [x] WebSocket streams ORAN execution output ✅
- [x] Frontend UI displays ORAN tabs (Upload Specs, Test Catalog) ✅
- [x] Old TTS features hidden on feature branch ✅
- [x] Script viewer modal with syntax highlighting works ✅
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
