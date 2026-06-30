# ORAN Test Generation Integration Plan

## TL;DR
Feture to extract test plan from an already provided test specification document.

Extend demo-web (existing FastAPI + Vanilla JS TTS execution platform) to add O-RAN A1 specification-to-test generation capabilities. Reuses 60-70% of existing infrastructure (WebSocket streaming, execution engine, UI shell) while adding new components for spec parsing, semantic extraction, and pytest script generation. Target: transform PDF/DOCX O-RAN specs into executable test catalogs and Python pytest scripts.

**Approach**: Incremental extension with 4 phases - (1) Core ORAN services, (2) Spec parsing pipeline, (3) Test generation engine, (4) UI integration. Each phase independently testable.

---

## Steps

### **Phase 1: ORAN Foundation (Backend Services)**
*Estimated: 3-4 days | Dependencies: None*

1. **Create ORAN execution service** (*parallel with Step 2*)
   - Extend [backend/app/services/execution_service.py](c:\TestRepo\demo-web\backend\app\services\execution_service.py) → Create `OranExecutionService(ExecutionService)`
   - Override `_build_jmeter_command` → `_build_pytest_command`
   - Reuse subprocess spawning pattern (`ThreadPoolExecutor` + `subprocess.Popen`)
   - Command structure: `pytest {test_file} --json-report --json-report-file={result.json} -v`
   - Keep WebSocket streaming logic from parent class (lines 105-167)

2. **Create ORAN log parser** (*parallel with Step 1*)
   - New file: [backend/app/parsers/oran_parser.py](c:\TestRepo\demo-web\backend\app\parsers\oran_parser.py)
   - Parse pytest JSON output format (test results, KPIs, assertions)
   - Extract O-RAN specific metrics (latency, throughput, conformance status)
   - Pattern: `{"tests": [{"nodeid": "...", "outcome": "passed", "call": {...}}]}`
   - Reuse statistics calculation pattern from [JtlParser.parse_statistics()](c:\TestRepo\demo-web\backend\app\parsers\jtl_parser.py#L18-63)

3. **Define ORAN data models**
   - New file: [backend/app/models/oran.py](c:\TestRepo\demo-web\backend\app\models\oran.py)
   - Models: `OranTestCatalog`, `OranTestCase`, `OranExecutionResult`, `OranKpiMetrics`
   - Extend existing `Demo` model to support `protocol: "ORAN"` and `test_type: "pytest"`
   - Add optional `OranKpiMetrics` to `ExecutionResult` model

4. **Add ORAN API endpoints**
   - New file: [backend/app/api/oran.py](c:\TestRepo\demo-web\backend\app\api\oran.py)
   - `POST /api/oran/generate` - Generate tests from specs (triggers generation pipeline)
   - `GET /api/oran/catalogs` - List generated test catalogs
   - `GET /api/oran/scripts/{test_id}` - View generated pytest script
   - Reuse FastAPI router pattern from [demos.py](c:\TestRepo\demo-web\backend\app\api\demos.py)

**Verification**:
- Run pytest unit tests for `OranExecutionService` (mock subprocess)
- Verify `OranParser` correctly extracts stats from sample pytest JSON output
- Test API endpoints with curl/Postman
- Confirm WebSocket messages broadcast ORAN execution output

---

### **Phase 2: Spec Parsing Pipeline**
*Estimated: 4-5 days | Depends on Phase 1 Step 3 (data models)*

5. **Implement document ingestion**
   - New file: [backend/app/services/spec_parser_service.py](c:\TestRepo\demo-web\backend\app\services\spec_parser_service.py)
   - Method: `ingest_pdf(file_path: str) -> str` using `pypdf.PdfReader`
   - Method: `ingest_docx(file_path: str) -> str` using `python-docx.Document`
   - Handle multi-page PDFs, extract text preserving structure
   - Dependencies: Add `pypdf==3.17.0`, `python-docx==1.1.0` to [requirements.txt](c:\TestRepo\demo-web\backend\requirements.txt)

6. **Extract test clauses from specs** (*depends on Step 5*)
   - Method: `extract_clauses(spec_text: str, spec_type: SpecType) -> List[TestClause]`
   - Regex patterns for ETSI clause format: `^\d+\.\d+\s+[A-Z]` (e.g., "5.3.1 Test Scenario Name")
   - Parse fields: clause_number, title, description, entrance_criteria, methodology, expected_result
   - Return `TestClause` Pydantic models with structured fields

7. **Semantic extraction from clauses** (*parallel with Step 6 implementation*)
   - Method: `extract_test_semantics(clause: TestClause) -> TestSemantics`
   - Extract HTTP method: Regex for `GET|PUT|POST|DELETE` in methodology text
   - Extract endpoint: Regex for URI patterns `/policies/{id}`, `/ei-jobs/{jobId}`
   - Extract payload type: Match against TS 103 988 type names (PolicyObject, EiJobObject)
   - Extract assertions: Parse expected results for status codes (200, 201, 400, 404)
   - Return structured `TestSemantics` model

8. **Cross-reference multiple specs** (*depends on Step 6, 7*)
   - Method: `enrich_test_case(base_clause: TestClause, specs: Dict[SpecType, str]) -> EnrichedTestCase`
   - TS 103 989 (test spec) provides test logic
   - TS 103 987 (API protocol) provides endpoint definitions and parameters
   - TS 103 988 (type defs) provides JSON schema for payloads
   - TS 103 983 (general principles) provides terminology/context
   - Merge data into single `EnrichedTestCase` with complete test definition

**Verification**:
- Unit test: Parse sample ETSI PDF, verify clause extraction (10+ clauses expected)
- Unit test: Extract semantics from mock clause text, verify HTTP method/endpoint detected
- Integration test: Cross-reference 4 specs, generate 3 enriched test cases
- Manual: Upload sample ETSI spec via `/api/oran/upload`, verify parsing logs

---

### **Phase 3: Test Generation Engine**
*Estimated: 3-4 days | Depends on Phase 2 Step 8*

9. **Generate JSON test catalog** (*depends on Phase 2 Step 8*)
   - New file: [backend/app/services/test_generator_service.py](c:\TestRepo\demo-web\backend\app\services\test_generator_service.py)
   - Method: `generate_catalog(enriched_cases: List[EnrichedTestCase]) -> OranTestCatalog`
   - Output format matches existing [demos.json](c:\TestRepo\demo-tool\src\main\resources\data\demos.json) structure
   - Example: `{"test_id": "A1_TC_001", "scenario": "Create policy", "request": {...}, "validations": [...]}`
   - Save to `backend/data/oran_catalogs/{catalog_id}.json`

10. **Create Jinja2 pytest templates** (*parallel with Step 9*)
    - New directory: [backend/templates/oran/](c:\TestRepo\demo-web\backend\templates\oran/)
    - Template: `a1_test.py.j2` for pytest script generation
    - Template structure:
      ```python
      import requests
      import pytest

      @pytest.mark.parametrize("test_case", {{ test_cases }})
      def test_{{ scenario_name }}(test_case):
          response = requests.{{ method.lower() }}(
              f"{{ base_url }}{{ endpoint }}",
              json=test_case["payload"]
          )
          assert response.status_code == {{ expected_status }}
      ```
    - Variables: `test_cases`, `base_url`, `method`, `endpoint`, `expected_status`, `validations`

11. **Implement pytest script generation** (*depends on Step 9, 10*)
    - Method: `generate_pytest_script(catalog: OranTestCatalog) -> str`
    - Load Jinja2 template from `backend/templates/oran/a1_test.py.j2`
    - Render with test catalog data
    - Save to `backend/generated_tests/{test_id}.py`
    - Return file path for execution
    - Dependencies: Add `jinja2==3.1.2` to [requirements.txt](c:\TestRepo\demo-web\backend\requirements.txt)

12. **Create ORAN test configuration** (*parallel with Step 11*)
    - Generate YAML config for each test catalog: `backend/generated_tests/{test_id}_config.yaml`
    - Config fields: `test_environment` (IUT host/port), `simulator` (type, config), `timeouts`, `retries`
    - Passed to pytest via `--config {yaml_file}` or environment variables
    - Template: [backend/templates/oran/test_config.yaml.j2](c:\TestRepo\demo-web\backend\templates\oran\test_config.yaml.j2)

**Verification**:
- Unit test: Generate catalog from 3 enriched test cases, validate JSON schema
- Unit test: Render Jinja2 template with mock data, verify Python syntax valid
- Integration test: Full pipeline - spec → catalog → pytest script → execute script → parse results
- Manual: View generated pytest script at `/api/oran/scripts/{test_id}`, verify readability

---

### **Phase 4: Frontend Integration**
*Estimated: 4-5 days | Depends on Phase 1, 2, 3*

13. **Add ORAN upload UI** (*depends on Phase 2 Step 5*)
    - Add new tab to [frontend/templates/index.html](c:\TestRepo\demo-web\frontend\templates\index.html): `<section id="oran-tab">`
    - File upload form: 4 file inputs for ETSI specs (TS 103 989, 987, 988, 983)
    - Dropzone.js for drag-and-drop upload
    - Progress bar during spec parsing (WebSocket messages)
    - Button: "Generate Test Catalog" triggers `/api/oran/generate`

14. **Display generated test catalog** (*depends on Phase 3 Step 9, Step 13*)
    - Extend [frontend/static/js/app.js](c:\TestRepo\demo-web\frontend\static\js\app.js) with `loadOranCatalogs()` function
    - Table view: List generated test catalogs (ID, date, spec sources, test count)
    - Click catalog → expand to show individual test cases
    - Each test case row shows: test_id, scenario name, HTTP method, endpoint, expected status
    - Button: "View Script" opens modal with syntax-highlighted pytest code (Prism.js)

15. **Integrate ORAN execution with existing flow** (*depends on Phase 1 Step 1, 4*)
    - Reuse "Run Demo" button pattern from [demos tab](c:\TestRepo\demo-web\frontend\templates\index.html#L100-150)
    - Clicking "Run Test" on ORAN catalog row calls `POST /api/execute` with `demo_id={test_id}`
    - Auto-switch to "Execution" tab (reuse existing logic)
    - WebSocket streams pytest output to console panel (reuse [connectWebSocket](c:\TestRepo\demo-web\frontend\static\js\app.js#L229-253))
    - Parse pytest JSON results and display in statistics panel

16. **Add ORAN-specific visualizations** (*parallel with Step 15*)
    - Replace call flow diagram panel with ORAN topology view when ORAN test runs
    - Topology: nodes (IUT, A1 Simulator, RIC) with arrows showing message flow
    - Use vis.js library for network graph rendering
    - Display ORAN KPIs in statistics panel: latency (ms), throughput (msgs/sec), conformance rate (%)
    - Add Plotly.js chart for per-endpoint response times

17. **Implement history for generated tests** (*depends on existing history API stubs*)
    - Complete implementation of [backend/app/api/history.py](c:\TestRepo\demo-web\backend\app\api\history.py) endpoints
    - Store ORAN run results in `backend/data/oran_history/{execution_id}.json`
    - Add "History" view in ORAN tab: table of past runs with filters (test_id, status, date range)
    - Click history row → replay results (show output log, stats, visualizations)
    - Export button: Download run results as JSON/CSV

**Verification**:
- Manual: Upload 4 ETSI spec PDFs, verify parsing progress shown
- Manual: Generate catalog, verify table displays 5+ test cases
- Manual: Click "View Script" on test case, verify syntax highlighting works
- Manual: Run ORAN test, verify console output streams in real-time
- E2E test (Playwright): Upload specs → generate → execute → view results

---

## Relevant Files

### **Core Services (Reusable)**
- [backend/app/services/execution_service.py](c:\TestRepo\demo-web\backend\app\services\execution_service.py) - Subprocess spawning pattern (lines 105-167), WebSocket streaming (lines 28-103)
- [backend/app/services/demo_service.py](c:\TestRepo\demo-web\backend\app\services\demo_service.py) - Catalog loading pattern (_load_catalog method, lines 18-55)
- [backend/app/websockets/demo_output.py](c:\TestRepo\demo-web\backend\app\websockets\demo_output.py) - WebSocket manager (ConnectionManager class, broadcast_output function)

### **Parsers (Adaptation Template)**
- [backend/app/parsers/jtl_parser.py](c:\TestRepo\demo-web\backend\app\parsers\jtl_parser.py) - Statistics calculation pattern (parse_statistics method, lines 18-63)

### **Data Models (Extension Points)**
- [backend/app/models/demo.py](c:\TestRepo\demo-web\backend\app\models\demo.py) - Demo schema (add `protocol: "ORAN"`)
- [backend/app/models/execution.py](c:\TestRepo\demo-web\backend\app\models\execution.py) - ExecutionResult model (add optional oran_kpis field)

### **API Patterns (Reference)**
- [backend/app/api/demos.py](c:\TestRepo\demo-web\backend\app\api\demos.py) - FastAPI router pattern
- [backend/app/api/execution.py](c:\TestRepo\demo-web\backend\app\api\execution.py) - Execution endpoints

### **Frontend (UI Shell)**
- [frontend/templates/index.html](c:\TestRepo\demo-web\frontend\templates\index.html) - Tab structure, add new ORAN tab
- [frontend/static/js/app.js](c:\TestRepo\demo-web\frontend\static\js\app.js) - WebSocket handling (connectWebSocket, handleWebSocketMessage functions)

### **Configuration**
- [backend/.env.example](c:\TestRepo\demo-web\backend\.env.example) - Add ORAN-specific env vars (ORAN_INSTALL_PATH, ORAN_RIC_ENDPOINT)
- [backend/requirements.txt](c:\TestRepo\demo-web\backend\requirements.txt) - Add pypdf, python-docx, jinja2, requests, xmltodict

### **New Files to Create**
- [backend/app/services/spec_parser_service.py](c:\TestRepo\demo-web\backend\app\services\spec_parser_service.py) - Document ingestion, clause extraction
- [backend/app/services/test_generator_service.py](c:\TestRepo\demo-web\backend\app\services\test_generator_service.py) - Catalog and script generation
- [backend/app/services/oran_execution_service.py](c:\TestRepo\demo-web\backend\app\services\oran_execution_service.py) - Pytest execution
- [backend/app/parsers/oran_parser.py](c:\TestRepo\demo-web\backend\app\parsers\oran_parser.py) - Pytest JSON result parsing
- [backend/app/models/oran.py](c:\TestRepo\demo-web\backend\app\models\oran.py) - ORAN data models
- [backend/app/api/oran.py](c:\TestRepo\demo-web\backend\app\api\oran.py) - ORAN API endpoints
- [backend/templates/oran/a1_test.py.j2](c:\TestRepo\demo-web\backend\templates\oran\a1_test.py.j2) - Jinja2 template for pytest scripts
- [backend/templates/oran/test_config.yaml.j2](c:\TestRepo\demo-web\backend\templates\oran\test_config.yaml.j2) - YAML config template

---

## Verification

### **Phase 1 Verification**
1. **Unit Tests**: Run `pytest tests/unit/test_oran_execution_service.py` - verify subprocess spawning with mock pytest command
2. **Parser Test**: Feed sample pytest JSON output to OranParser, assert correct statistics extracted (total, passed, failed, success_rate)
3. **API Test**: `curl http://localhost:8000/api/oran/catalogs` - verify empty list initially
4. **WebSocket Test**: Connect to `/ws/demo-output/{exec_id}`, trigger ORAN execution, verify output messages received

### **Phase 2 Verification**
1. **PDF Ingestion**: Upload sample ETSI TS 103 989 PDF (5+ pages), verify text extraction returns 10,000+ characters
2. **Clause Extraction**: Parse extracted text, assert 15+ test clauses identified with valid structure
3. **Semantic Analysis**: Test clause "Test Case 5.3.1: Create Policy via PUT /policies/{id}" → assert extracts method=PUT, endpoint=/policies/{id}
4. **Cross-Reference**: Provide 4 mock spec texts, generate enriched test case, verify payload schema from TS 103 988 merged into test definition
5. **Integration Test**: Full pipeline with sample specs → assert JSON catalog generated with 3+ test cases
6. **Conformance Classification**: Verify TS 103 989 methodology-derived scenarios can be tagged as conformance vs interoperability with preserved HTTP configurability metadata

### **Phase 3 Verification**
1. **Catalog Generation**: Generate catalog from 3 enriched cases, assert JSON valid, conforms to schema
2. **Template Rendering**: Render Jinja2 template with mock test data, run `python -m py_compile` on output to verify syntax
3. **Script Generation**: Generate pytest script for test_id=A1_TC_001, verify file created at `backend/generated_tests/A1_TC_001.py`
4. **End-to-End**: Generate script → execute with `pytest A1_TC_001.py` → parse results → assert statistics match expected
5. **Manual Review**: Call `/api/oran/scripts/A1_TC_001` → inspect generated code for readability, correct assertions
6. **Simulator Conformance Coverage**: Verify generated conformance cases can exercise configurable `GET`, `PUT`, `POST`, and `DELETE` request shapes before interoperability profiles are enabled

### **Phase 4 Verification**
1. **UI Load**: Open `http://localhost:8000`, verify ORAN tab visible, upload form renders correctly
2. **File Upload**: Drag 4 ETSI spec PDFs into dropzone, verify progress bar animates, success message shown
3. **Catalog Display**: After generation, verify catalog table shows test cases with correct data (test_id, method, endpoint)
4. **Execution Flow**: Click "Run Test" on catalog row → verify auto-switch to Execution tab → console output streams → statistics update
5. **Topology Visualization**: Run ORAN test → verify topology diagram renders with IUT, Simulator, RIC nodes and message arrows
6. **E2E Test (Playwright)**: `pytest tests/e2e/test_oran_workflow.py` - automated upload → generate → execute → verify flow

### **System Integration Verification**
1. **Mixed Protocol Test**: Run both JMeter demo (SIP) and ORAN pytest test simultaneously → verify no interference
2. **WebSocket Isolation**: Connect 2 browser tabs to different executions → verify messages routed correctly
3. **History Persistence**: Run ORAN test → restart backend → verify history loads correctly
4. **Error Handling**: Provide invalid spec PDF → verify graceful error message displayed
5. **Performance**: Generate catalog with 50 test cases → verify UI remains responsive

---

## Decisions

### **Architecture Decisions**
- **Extend vs. Separate**: Extend demo-web as unified test platform (both JMeter and pytest) rather than building standalone ORAN system. Rationale: Reuses 60-70% of infrastructure, unified UX for internal engineers.
- **Backend Technology**: Keep FastAPI + Python stack. Pytest native to Python, simplifies script generation and execution.
- **Frontend Approach**: Add ORAN tab to existing monolithic app.js rather than refactoring to modules. Rationale: Faster MVP delivery, refactoring can be separate initiative.
- **Storage Strategy**: File-based JSON storage for test catalogs and history (no database). Rationale: Consistent with existing demo-web architecture, sufficient for internal tool.

### **Technical Decisions**
- **Subprocess Pattern**: Reuse `ThreadPoolExecutor` + `subprocess.Popen` from ExecutionService for pytest execution. Rationale: Proven Windows-compatible pattern.
- **Log Parsing**: Parse pytest's JSON report plugin output (not console text). Rationale: Structured data easier to parse than regex on console output.
- **Template Engine**: Jinja2 for pytest script generation. Rationale: Industry standard, powerful, mature Python integration.
- **Spec Parsing Approach**: Regex-based clause extraction from text (not ML/NLP). Rationale: ETSI spec format is consistent, regex sufficient for MVP. AI/ML extraction can be Phase 2 enhancement.
- **TDD Development Approach**: Apply TS 103 989 §4.1 as the governing delivery model. Rationale: the spec defines simulator-driven conformance testing with configurable HTTP `GET`, `PUT`, `POST`, and `DELETE` primitives before broader interoperability validation, so new A1 prototype slices should start with failing spec-derived conformance tests and only then expand to topology-level interoperability checks.

### **TDD Approach from TS 103 989 §4.1**
- Start each A1 feature slice with a spec-derived failing conformance test that encodes HTTP method, URI, headers, body, and expected result.
- Keep conformance and interoperability as separate execution layers: conformance for fast TDD cycles, interoperability for slower end-to-end validation between Non-RT RIC and Near-RT RIC roles.
- Treat simulator capabilities as first-class infrastructure, with reusable fixtures for configurable request/response behavior across `GET`, `PUT`, `POST`, and `DELETE`.
- Use a normalized scenario artifact as the handoff between clause extraction, semantic enrichment, generated catalogs, pytest script generation, and regression selection.
- Do not add new A1 route or service logic without a failing scenario-based conformance test first.

### **Scope Decisions**
- **Included**:
  - All 6 priority features: PDF/DOCX parsing, clause extraction, semantic analysis, catalog generation, script generation, pytest execution
  - Real-time output streaming via existing WebSocket infrastructure
  - Basic ORAN topology visualization (nodes + arrows)
  - Test result history with run replay
  - Export functionality (JSON/CSV)

- **Explicitly Excluded (Future Phases)**:
  - Advanced AI/NLP for spec parsing (start with regex, upgrade later if needed)
  - Multi-tenant support (internal tool, single user assumption)
  - Database integration (file-based sufficient for MVP)
  - Authentication/authorization (internal tool, trust-based)
  - Advanced failure injection for ORAN protocols (basic conformance testing only)
  - xApp management UI (ORAN catalog generation only, no runtime xApp control)
  - Integration with external ORAN RIC systems (simulator-based testing initially)

### **Data Model Decisions**
- **Test Catalog Schema**: Extend existing demos.json structure with `protocol: "ORAN"` and `test_type: "pytest"`. Rationale: Backwards compatible, minimal changes to DemoService.
- **Execution Results**: Add optional `oran_kpis` field to ExecutionResult model rather than new model. Rationale: Maintains unified execution API.

### **User Experience Decisions**
- **Spec Upload**: Support drag-and-drop for 4 spec files simultaneously. Rationale: Matches ORAN workflow (4 interdependent specs).
- **Catalog View**: Show test cases in expandable table (not tree view). Rationale: Simpler implementation, sufficient for 10-50 test cases per catalog.
- **Execution Integration**: Reuse existing "Execution" tab for ORAN tests (not separate tab). Rationale: Consistent UX with JMeter demos, unified history view.

---

## Further Considerations - ✅ DECISIONS MADE

### **1. Spec Parsing Accuracy**
**Question**: ETSI specs vary in format. Will regex-based clause extraction handle all edge cases, or should we invest in ML-based extraction from the start?

✅ **DECISION**: **Option A** - Start with regex for MVP (covers 80%+ of cases based on ETSI format consistency). Add fallback to manual clause definition via JSON upload if regex fails.

📋 **TODO**: Review Option B (ML-based extraction using NLP models) in future phase for improved accuracy on edge cases.

### **2. Multi-Spec Cross-Referencing Strategy**
**Question**: How to handle ambiguous references when merging data from 4 specs (e.g., endpoint defined differently in TS 103 987 vs. TS 103 989)?

✅ **DECISION**: **Option A** - Use priority order: TS 103 989 (test spec) takes precedence for test logic, TS 103 987 for API definitions, TS 103 988 for schemas. Log warnings for conflicts, allow manual override in generated catalog JSON.

🔧 **ENHANCEMENT**: Store all detected conflicts in database (or JSON file initially) for later review and analytics.

📋 **TODO**: Add conflict review section to UI showing all detected spec conflicts with resolution options (accept priority, manual merge, flag for review).

### **3. Generated Script Customization**
**Question**: Should users be able to edit generated pytest scripts before execution, or are they read-only?

✅ **DECISION**: **Option A** - Phase 1: read-only with "Download" button for external editing workflow.

📋 **TODO**: Phase 2 - Add in-browser code editor (Monaco Editor or CodeMirror) with "Save & Execute Custom" feature. Include version control for custom edits.

### **4. Consolidated Output Artifacts**

The implementation should consistently produce these artifacts:

- JSON test catalog
- Python pytest scripts
- Test configuration YAML
- Execution results and logs

### **5. Failure Injection Baseline Scenarios**

Baseline negative scenarios to support in MVP execution and validation:

- Schema error -> expect HTTP 400
- Invalid URI -> expect HTTP 404
- Timeout handling -> expect controlled failure result
