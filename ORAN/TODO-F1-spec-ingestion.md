# Feature 1 TODO - Specification Ingestion and Test Plan JSON

Project: Extend demo-web with O-RAN A1 test generation capabilities
Status: IN PROGRSES
Owner Track: Feature 1 (Upstream)

## Scope

- Read test specification documents.
- Extract structured information for test cases, components, and modules.
- Store extracted data in normalized JSON test plans.
- Show test-plan data in UI.

## Downstream Contract for Feature 2

Feature 1 output is the input contract for simulator implementation in Feature 2.
Required per-test JSON fields:
- test_id
- test_name
- component_targets
- module_targets
- preconditions
- steps
- expected_results
- protocol_or_interface
- priority_or_complexity

See downstream: [Feature 2 TODO](TODO-F2-simulator-tdd.md)

---

## Priority Next Item

- [ ] P1-ENH: Simplify Upload Specs Tab - Dedicated Document Management.

---

## Detailed Legacy Backlog Migrated from TODO.md

### Post-UI Simplification Follow-up
Status: Pending
Priority: Medium

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
  - Confirm reproducible case: catalog name TS_103_989_1 renders tests, but View Script click does not open modal.
  - Verify frontend handler wiring in ORAN catalog table and script modal open path.
  - Validate backend script retrieval endpoint and test-id to script-file mapping.
  - Add regression check so View Script works for both MVP-sized catalogs and larger catalogs.

### Phase 2: Spec Parsing Pipeline
Status: NOT STARTED
Priority: HIGH

- [ ] Task 2.1: Implement document ingestion
  - File: backend/app/services/spec_parser_service.py
  - Method: ingest_pdf(file_path: str) -> str using pypdf
  - Method: ingest_docx(file_path: str) -> str using python-docx
  - Add dependencies: pypdf==3.17.0, python-docx==1.1.0
- [ ] Task 2.2: Extract test clauses from specs
  - Method: extract_clauses(spec_text: str, spec_type: SpecType) -> List[TestClause]
  - Regex patterns for ETSI clause format: ^\d+\.\d+\s+[A-Z]
  - Parse: clause_number, title, description, entrance_criteria, methodology, expected_result
  - Decision implemented: Regex-based extraction with manual JSON fallback
- [ ] Task 2.3: Semantic extraction from clauses
  - Method: extract_test_semantics(clause: TestClause) -> TestSemantics
  - Extract: HTTP method (GET/PUT/POST/DELETE), endpoint, payload type, assertions
  - Regex-based extraction for MVP
- [ ] Task 2.4: Cross-reference multiple specs
  - Method: enrich_test_case(base_clause: TestClause, specs: Dict[SpecType, str]) -> EnrichedTestCase
  - Decision implemented: Priority order TS 103 989 -> TS 103 987 -> TS 103 988
  - Enhancement: Log conflicts to JSON file for review
- [ ] Task 2.5: Implement conflict storage
  - File: backend/data/spec_conflicts.json (initial file-based storage)
  - Store: conflict_id, timestamp, spec1, spec2, field, value1, value2, resolution
- [ ] Task 2.6: Write unit tests for Phase 2
  - Test PDF ingestion with sample ETSI spec
  - Test clause extraction (verify 15+ clauses)
  - Test semantic extraction (HTTP method/endpoint detection)
  - Test cross-reference with conflict detection

### Phase 3: Test Generation Engine
Status: NOT STARTED
Priority: HIGH

- [ ] Task 3.1: Generate JSON test catalog
  - File: backend/app/services/test_generator_service.py
  - Method: generate_catalog(enriched_cases: List[EnrichedTestCase]) -> OranTestCatalog
  - Save to: backend/data/oran_catalogs/{catalog_id}.json
- [ ] Task 3.2: Create Jinja2 pytest templates
  - Directory: backend/templates/oran/
  - Template: a1_test.py.j2 for pytest script generation
  - Template: test_config.yaml.j2 for test configuration
  - Add dependency: jinja2==3.1.2
- [ ] Task 3.3: Implement pytest script generation
  - Method: generate_pytest_script(catalog: OranTestCatalog) -> str
  - Save to: backend/generated_tests/{test_id}.py
  - Decision implemented: Read-only scripts with Download button
- [ ] Task 3.4: Create ORAN test configuration
  - Generate YAML config: backend/generated_tests/{test_id}_config.yaml
  - Fields: test_environment, simulator config, timeouts, retries
- [ ] Task 3.5: Write unit tests for Phase 3
  - Test catalog generation (validate JSON schema)
  - Test template rendering (verify Python syntax)
  - Integration test: Full pipeline spec -> catalog -> script -> execute

### Phase 4: Frontend Enhancements (Feature-1 aligned items)
Status: NOT STARTED
Priority: MEDIUM

- [ ] Task 4.4: Add ORAN-specific visualizations (advanced)
  - Replace static output with ORAN topology view (vis.js or Mermaid)
  - KPI charts with Plotly.js (latency, throughput, conformance)
  - Per-endpoint response time comparison
- [ ] Task 4.5: Implement conflict review UI
  - Add Conflicts tab in catalog details
  - Table for spec conflicts and actions
  - Backend endpoint: GET /api/oran/conflicts
- [ ] Task 4.7: Enhance execution monitoring
  - Live KPI updates during test execution (WebSocket)
  - Progress bar for test suite completion
  - Real-time chart updates
- [ ] Task 4.8: Write E2E tests for frontend
  - File: tests/e2e/test_oran_workflow.py
  - Flow: upload specs -> generate -> view catalog -> execute -> view results

### Enhancements: Upload Specs and Parsing

#### P1-ENH: Simplify Upload Specs Tab - Dedicated Document Management
Priority: High
Status: NOT STARTED

- [ ] Remove generation controls from Upload Specs tab.
- [ ] Redesign Upload Specs for spec library + upload + replace flow.
- [ ] Move generation controls to Test Catalog tab.
- [ ] Add backend endpoints for spec library and version conflict handling.
- [ ] Add UX polish (badge count, empty state, navigation warning).

Acceptance criteria:
- Upload Specs only handles document management.
- Test Catalog handles generation workflow.
- No functionality lost.

#### P1-ENH: Replace Checkbox Layout with Dropdown + Local File Upload
Priority: High
Status: NOT STARTED

- [ ] Replace checkbox selection with single dropdown.
- [ ] Add Upload New Spec button for arbitrary PDF/DOCX.
- [ ] Add workspace docs upload/listing endpoints.
- [ ] Add drag-drop, validation feedback, and success toast.

Acceptance criteria:
- Checkbox layout removed.
- Dropdown + upload button shown inline.
- Uploaded files listed and manageable.

### Future Enhancements (Feature-1 aligned)

#### ML-Based Spec Parsing (Option B Review)
- [ ] Research NLP models for technical document parsing.
- [ ] Prototype ML extraction on 10+ ETSI samples.
- [ ] Compare regex vs ML accuracy.
- [ ] Perform cost/benefit analysis.
- [ ] Decide: regex only, ML fallback, or ML replacement.

#### Conflict Review UI Section
- [ ] Design conflict review panel.
- [ ] Implement conflict APIs.
- [ ] Add conflict statistics dashboard.
- [ ] Add auto-resolution rule configuration.
- [ ] Add conflict export (CSV/JSON).

### Infrastructure Tasks (Feature-1 aligned)

- [ ] Update backend/.env.example with ORAN variables.
- [ ] Update backend/requirements.txt with ORAN dependencies.
- [ ] Create backend/data/oran_catalogs.
- [ ] Create backend/data/oran_history.
- [ ] Create backend/data/spec_conflicts.json.
- [ ] Create backend/generated_tests.
- [ ] Create backend/templates/oran.

### Completion Criteria (Feature-1 aligned)

- [ ] PDF/DOCX ingestion works for ETSI specs.
- [ ] 15+ test clauses extracted from sample spec.
- [ ] Semantic extraction identifies HTTP method/endpoint/assertions.
- [ ] Cross-reference merges specs with conflict logging.
- [ ] JSON test catalog generated with valid schema.
- [ ] Jinja2 templates render syntactically correct pytest scripts.
- [ ] Generated scripts execute successfully with pytest.
- [ ] YAML configs generated with correct structure.
- [ ] ORAN topology/KPI visualization and conflict UI operational.
- [ ] E2E path upload -> generate -> execute -> visualize passes.
