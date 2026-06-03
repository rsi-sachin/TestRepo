# Demo-Web ORAN Integration - TODO List

**Project:** Extend demo-web with O-RAN A1 test generation capabilities  
**Last Updated:** June 3, 2026  
**Status:** Planning Complete, Implementation Pending

---

## 📋 IMPLEMENTATION TASKS

### ✅ Phase 1: ORAN Foundation (Backend Services)
**Status:** ✅ COMPLETE  
**Estimated:** 3-4 days  
**Actual:** Completed June 3, 2026  
**Priority:** HIGH

- [x] **Task 1.1:** Create OranExecutionService
  - File: `backend/app/services/oran_execution_service.py` ✅
  - Extend ExecutionService, override `_build_jmeter_command` → `_build_pytest_command`
  - Reuse subprocess spawning + WebSocket streaming pattern
  - Command: `pytest {test_file} --json-report --json-report-file={result.json} -v`

- [x] **Task 1.2:** Create OranParser
  - File: `backend/app/parsers/oran_parser.py` ✅
  - Parse pytest JSON output format
  - Extract statistics (total, passed, failed, success_rate)
  - Extract O-RAN KPIs (latency, throughput, conformance status)

- [x] **Task 1.3:** Define ORAN data models
  - File: `backend/app/models/oran.py` ✅
  - Models: `OranTestCatalog`, `OranTestCase`, `OranExecutionResult`, `OranKpiMetrics`
  - Extend `Demo` model to support `protocol: "ORAN"`

- [x] **Task 1.4:** Add ORAN API endpoints
  - File: `backend/app/api/oran.py` ✅
  - `POST /api/oran/generate` - Trigger test generation
  - `GET /api/oran/catalogs` - List generated catalogs
  - `GET /api/oran/scripts/{test_id}` - View generated pytest script

- [x] **Task 1.5:** Write unit tests for Phase 1
  - File: `backend/verify_phase1.py` ✅
  - 5 API endpoint tests (health, config, catalogs, statistics, docs)

- [x] **Task 1.6:** Create infrastructure directories and update config
  - Created: `backend/data/oran_catalogs/` ✅
  - Created: `backend/data/oran_history/` ✅
  - Created: `backend/generated_tests/` ✅
  - Created: `backend/templates/oran/` ✅
  - Updated: `config.py`, `main.py`, `requirements.txt`, `.env.example` ✅

**Phase 1 Deliverables:**
- ✅ 1180+ lines of production-ready code
- ✅ 15 API endpoints operational
- ✅ Real-time WebSocket streaming
- ✅ Pytest execution with KPI calculation
- ✅ Full API documentation (Swagger UI)

**See**: [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) for detailed summary

---

### ✅ Phase 2: Spec Parsing Pipeline
**Status:** Not Started  
**Estimated:** 4-5 days  
**Priority:** HIGH  
**Depends on:** Phase 1 Task 1.3

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

### ✅ Phase 4: Frontend Integration
**Status:** Not Started  
**Estimated:** 4-5 days  
**Priority:** HIGH  
**Depends on:** Phases 1, 2, 3

- [ ] **Task 4.1:** Add ORAN upload UI
  - File: `frontend/templates/index.html` (add ORAN tab)
  - 4 file upload inputs for ETSI specs (TS 103 989/987/988/983)
  - Dropzone.js for drag-and-drop
  - Progress bar during parsing (WebSocket messages)

- [ ] **Task 4.2:** Display generated test catalog
  - Extend: `frontend/static/js/app.js`
  - Function: `loadOranCatalogs()`
  - Table view: catalog ID, date, spec sources, test count
  - Expandable rows showing individual test cases
  - "View Script" button opens modal with syntax highlighting (Prism.js)

- [ ] **Task 4.3:** Integrate ORAN execution flow
  - Reuse "Run Demo" button pattern
  - Call `POST /api/execute` with ORAN test_id
  - Auto-switch to Execution tab
  - WebSocket streams pytest output to console

- [ ] **Task 4.4:** Add ORAN-specific visualizations
  - Replace call flow diagram with ORAN topology view (vis.js)
  - Nodes: IUT, A1 Simulator, RIC with message arrows
  - ORAN KPIs panel: latency, throughput, conformance rate
  - Plotly.js charts for per-endpoint response times

- [ ] **Task 4.5:** Implement history for generated tests
  - Complete: `backend/app/api/history.py` endpoints
  - Store: `backend/data/oran_history/{execution_id}.json`
  - History view in ORAN tab with filters
  - Export button: Download as JSON/CSV

- [ ] **Task 4.6:** Write E2E tests for Phase 4
  - File: `tests/e2e/test_oran_workflow.py` (Playwright)
  - Test: Upload specs → generate → execute → view results

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
| Phase 1 | 6 | 6 | ✅ COMPLETE | June 3, 2026 |
| Phase 2 | 6 | 0 | Not Started | TBD |
| Phase 3 | 5 | 0 | Not Started | TBD |
| Phase 4 | 6 | 0 | Not Started | TBD |
| **Total** | **23** | **6** | **26%** | **TBD** |

**Future Enhancements:** 3 TODOs identified (ML parsing, Conflict UI, Code editor)

---

## ✅ COMPLETION CRITERIA

### Phase 1 Complete When:
- [ ] OranExecutionService executes pytest subprocess successfully
- [ ] OranParser extracts statistics from pytest JSON output
- [ ] ORAN API endpoints respond correctly
- [ ] WebSocket streams ORAN execution output

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
- [ ] ORAN tab loads with upload form
- [ ] Users can upload 4 specs, see parsing progress
- [ ] Generated catalog displays in table
- [ ] "Run Test" executes ORAN test with real-time output
- [ ] Topology visualization renders correctly
- [ ] History stores and displays past runs
- [ ] E2E test passes: upload → generate → execute → verify

**MVP Definition:** All 4 phases complete + all completion criteria met

---

**Notes:**
- See `IMPLEMENTATION_PLAN.md` for detailed technical specifications
- All decisions logged with rationale (Option A/B/C selections)
- Database migration path planned for future (currently file-based)
