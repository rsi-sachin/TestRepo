# UI Design Requirements: Conformance Test Display

**Document:** UI Design Requirements for Conformance Test Dashboard  
**Date:** 2026-06-30  
**Scope:** Display TS 103 989 §4.2.1–§4.2.2 conformance tests on demo-web frontend  
**Source:** ORAN-FTM-013 (Trace ID), Section 4.2.1–4.2.2 Conformance Setup Coverage

---

## 1. Overview

The demo-web UI must display all conformance tests defined in TS 103 989 §4.2.1–§4.2.2 (26 tests total, ~9 min execution). Tests are organized by coverage category (Policy Type Query, Policy CRUD, Error Handling, Header/Body Validation, Evidence Completeness).

---

## 2. Feature: Conformance Test Dashboard

### 2.1 New UI Tab: "Conformance Tests"

**Location:** Add new tab to main navigation after "Execution" and "History" tabs.

**Navigation:**
```
[Upload Specs] [Test Catalog] [Execution] [History] [Conformance Tests]
```

**Icon/Styling:** Use conformance badge icon (checkmark or shield) to denote verification/compliance focus.

---

## 3. Test Summary Card (Top Section)

### 3.1 Layout

Display a single summary card showing overall conformance metrics:

```
┌─────────────────────────────────────────────────────┐
│  Conformance Test Summary                           │
├─────────────────────────────────────────────────────┤
│  Status: ● Ready                                    │
│  TS 103 989 §4.2.1–§4.2.2 Coverage                  │
│                                                     │
│  Total Tests:  26                                   │
│  Categories:   5                                    │
│  Est. Time:    ~9 minutes                           │
│                                                     │
│  DUT Status:   ✓ Connected (10.0.0.5:8081)          │
│  Simulator:    ✓ Ready (10.0.0.6:8082)              │
│                                                     │
│  [Run All Tests]  [View Checklist]  [Settings]     │
└─────────────────────────────────────────────────────┘
```

### 3.2 Card Sections

| Section | Content | Data Source |
|---|---|---|
| **Status** | Ready / Running / Complete / Failed | Test suite state |
| **Title** | "TS 103 989 §4.2.1–§4.2.2 Coverage" | Static |
| **Metrics** | Total tests, categories, est. time | From conformance_setup.md test plan |
| **Preconditions** | DUT connectivity status, Simulator status | DUT readiness checks |
| **Actions** | Run All, View Checklist, Settings | Navigation buttons |

---

## 4. Test Categories Section

### 4.1 Tabbed or Collapsible Organization

Display 5 test categories as separate expandable panels:

```
Category 1: Policy Type Query Operations (5 tests)
├─ test_policy_type_list_returns_200
├─ test_policy_type_list_empty_when_none_registered
├─ test_policy_type_query_specific_returns_404_for_unknown
├─ test_policy_type_schema_conforms_to_spec
└─ test_policy_type_ownership_verification

Category 2: Policy CRUD Operations (8 tests)
├─ test_policy_create_returns_201_for_new_resource
├─ test_policy_create_returns_location_header
├─ test_policy_update_returns_200_for_existing_resource
├─ ...

Category 3: Error Handling (6 tests)
├─ test_error_400_on_invalid_request_body
├─ test_error_404_on_unknown_policy_type
├─ ...

Category 4: Header/Body Validation (4 tests)
├─ test_response_headers_include_content_type
├─ test_response_body_conforms_to_schema
├─ ...

Category 5: Evidence Completeness (3 tests)
├─ test_message_logs_captured_for_all_exchanges
├─ test_verdict_reason_linked_to_specification
└─ test_conformance_report_generated
```

### 4.2 Category Card Layout

```
┌──────────────────────────────────────────────────────┐
│ ▼ Category 1: Policy Type Query Operations          │
├──────────────────────────────────────────────────────┤
│   [5 tests, ~2 min, Status: Ready]                  │
│                                                      │
│   ☐ test_policy_type_list_returns_200                │
│     ▸ Description: Verify GET /policytypes return... │
│     ▸ Section: TS 103 987 §5.2.3.2                   │
│     ☐ Run This  ⋮ More...                            │
│                                                      │
│   ☐ test_policy_type_list_empty_when_none_...       │
│     ▸ Description: Verify empty array when no...     │
│     ▸ Section: TS 103 987 §5.2.3.3                   │
│     ☐ Run This  ⋮ More...                            │
│                                                      │
│   [Run Category]  [View Details]                    │
└──────────────────────────────────────────────────────┘
```

---

## 5. Individual Test Card

### 5.1 Information Displayed

For each test, show:

```
┌─ ☐ test_policy_type_list_returns_200
├─ Status: Ready | Running | Passed ✓ | Failed ✗
├─ Description: Verify GET /policytypes returns all available policy types
├─ Spec Reference: TS 103 989 §4.2.1, TS 103 987 §5.2.3.2
├─ Checks Performed: [3]
│  1. HTTP status code = 200
│  2. Response body is valid JSON
│  3. Response conforms to PolicyTypeObject schema
├─ Expected Duration: ~20 seconds
├─ Last Result: Passed ✓ on 2026-06-30 12:34:56
│  (Show brief result summary if previously run)
└─ Actions: [Run This] [View Evidence] [Edit Test] [⋮]
```

### 5.2 Test Card States

| State | Styling | Action Buttons |
|---|---|---|
| **Not Run** | Gray background, unchecked box | [Run This] |
| **Running** | Blue background, loading spinner | [Cancel] |
| **Passed** | Green background, ✓ checkmark | [Run Again] [View Evidence] |
| **Failed** | Red background, ✗ X mark | [Run Again] [View Evidence] [Debug] |

---

## 6. Batch Actions Section

### 6.1 Test Selection and Execution

```
┌─ Batch Actions
├─ ☐ Select All  [5/26 tests selected]
├─ Filters: [Status ▼] [Category ▼] [Spec Section ▼]
├─ [Run Selected (5)]  [Clear Selection]  [Export Selection]
└─
```

### 6.2 Bulk Run Dialog

When user clicks "Run Selected" or "Run All Tests":

```
┌──────────────────────────────────┐
│ Run Conformance Tests            │
├──────────────────────────────────┤
│                                  │
│ Tests to Run: 26                 │
│ Est. Duration: ~9 minutes        │
│                                  │
│ ☑ Stop on First Failure          │
│ ☑ Capture Full Evidence          │
│ ☑ Generate Conformance Report    │
│                                  │
│ Output Destination:              │
│ ○ Display on UI (streaming)      │
│ ○ Save to File (with path)       │
│ ○ Both                           │
│                                  │
│ [Run]  [Cancel]                  │
└──────────────────────────────────┘
```

---

## 7. Live Execution View

### 7.1 During Test Run

Display real-time progress:

```
┌─────────────────────────────────────────────────────┐
│ Running Conformance Tests...                        │
├─────────────────────────────────────────────────────┤
│ Progress: 12/26 tests completed (46%)               │
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │
│                                                     │
│ Current Test: test_policy_create_returns_201       │
│ Category: Policy CRUD Operations                   │
│ Elapsed: 3m 42s / Est. Total: ~9m                  │
│                                                     │
│ Recent Results:                                    │
│ ✓ test_policy_type_list_returns_200                │
│ ✓ test_policy_type_list_empty_when_none            │
│ ✓ test_policy_type_query_specific_returns_404      │
│ ⧖ test_policy_type_schema_conforms_to_spec         │
│                                                     │
│ [Pause]  [Cancel]  [View Log]                      │
└─────────────────────────────────────────────────────┘
```

### 7.2 Live Log Stream

Below the progress bar, show scrollable log of HTTP exchanges:

```
[12:34:56.123] GET /v1/policytypes
  → HTTP 200 OK (42ms)
  → Response: [{"policyTypeId": "policy-type-1"}, ...]
  ✓ Schema validation passed

[12:35:01.456] PUT /v1/policytypes/policy-type-1/policies/policy-1
  → HTTP 201 Created (85ms)
  → Headers: Location: /v1/policytypes/policy-type-1/policies/policy-1
  ✓ Status code validation passed

[12:35:06.789] GET /v1/policytypes/unknown
  → HTTP 404 Not Found (28ms)
  ✓ Expected error returned
```

---

## 8. Results Summary View

### 8.1 After Execution Complete

```
┌────────────────────────────────────────────────────┐
│ Conformance Test Results                           │
├────────────────────────────────────────────────────┤
│ Run ID: conformance-20260630-143056                │
│ Date: 2026-06-30 14:30:56                          │
│ Duration: 8m 47s                                   │
│                                                    │
│ Summary:                                           │
│ ✓ Passed:      26/26 (100%)                        │
│ ✗ Failed:       0/26                               │
│ ⚠ Inconclusive: 0/26                               │
│                                                    │
│ Status: CONFORM ✓                                  │
│ Verdict: DUT successfully demonstrates            │
│   conformance to TS 103 989 §4.2.1–§4.2.2         │
│                                                    │
│ Results by Category:                               │
│ • Policy Type Query Operations:    ✓ 5/5 passed   │
│ • Policy CRUD Operations:          ✓ 8/8 passed   │
│ • Error Handling:                  ✓ 6/6 passed   │
│ • Header/Body Validation:          ✓ 4/4 passed   │
│ • Evidence Completeness:           ✓ 3/3 passed   │
│                                                    │
│ [View Full Report] [Export PDF] [Share] [Retry]  │
└────────────────────────────────────────────────────┘
```

### 8.2 Category Breakdown

Click on each category to expand and see:
- Individual test results (✓/✗ status)
- Execution time per test
- Evidence artifacts (HTTP logs, schema validation)
- Failure reason (if applicable)

---

## 9. Detailed Test Results Page

### 9.1 Click on Individual Test Result

Display full evidence for selected test:

```
┌─────────────────────────────────────────────────────┐
│ Test: test_policy_type_list_returns_200             │
├─────────────────────────────────────────────────────┤
│ Status: ✓ PASSED                                    │
│ Spec Reference: TS 103 987 §5.2.3.2                │
│ Execution Time: 42ms                               │
│                                                     │
│ Test Intent:                                        │
│ Verify GET /policytypes returns all available      │
│ policy types from the A1-P Producer.               │
│                                                     │
│ Checks Performed:                                  │
│ ✓ Check 1: HTTP status code = 200                  │
│ ✓ Check 2: Response body is valid JSON             │
│ ✓ Check 3: Response conforms to PolicyTypeObject   │
│           schema                                    │
│                                                     │
│ HTTP Exchange Details:                              │
│ ───────────────────────────────────────────────    │
│ REQUEST:                                            │
│ GET /v1/policytypes HTTP/1.1                       │
│ Host: 10.0.0.5:8081                                │
│ Content-Type: application/json                     │
│                                                     │
│ RESPONSE:                                           │
│ HTTP/1.1 200 OK                                    │
│ Content-Type: application/json                     │
│ Content-Length: 156                                │
│                                                     │
│ [                                                   │
│   {                                                 │
│     "policyTypeId": "policy-type-1",               │
│     "schema": {...}                                 │
│   }                                                 │
│ ]                                                   │
│                                                     │
│ Schema Validation:                                  │
│ ✓ Field "policyTypeId" present (type: string)      │
│ ✓ Field "schema" present (type: object)            │
│ ✓ No additional properties found                    │
│                                                     │
│ Evidence Artifacts:                                 │
│ • HTTP Message Log: test_policy_type_list_...      │
│ • Schema Validation Report: schema_validation...   │
│ • Execution Log: execution_20260630_143056.log    │
│                                                     │
│ [Download Evidence] [View in JSON] [Print]        │
└─────────────────────────────────────────────────────┘
```

---

## 10. DUT Readiness Check View

### 10.1 Pre-Run Validation

Before allowing "Run All Tests" or "Run Selected", display readiness status:

```
┌─ DUT Readiness Checklist
├─ ✓ A1-P Consumer Support (Non-RT RIC)
├─ ✓ Policy Type 1 Registered: policy-type-1
├─ ✓ Endpoint Accessible: 10.0.0.5:8081 (HTTP 200)
├─ ✓ Response Schema Valid (PolicyTypeObject)
├─ ✓ HTTP Headers Valid (Content-Type: application/json)
├─ ✓ Network Connectivity OK (latency: 5ms)
└─ ✓ All checks passed. Ready to run conformance tests.

[View Full Checklist]
```

**If checks fail:**

```
┌─ DUT Readiness Checklist
├─ ⚠ A1-P Consumer Support (Non-RT RIC) — UNKNOWN
├─ ✓ Policy Type 1 Registered: policy-type-1
├─ ✗ Endpoint Unreachable: 10.0.0.5:8081 (connection timeout)
├─ — Response Schema Validation (skipped due to connectivity)
├─ — HTTP Headers Valid (skipped due to connectivity)
└─ ✗ Readiness checks failed. Cannot run conformance tests.

Remediation Guide:
1. Verify Non-RT RIC endpoint is accessible
2. Check firewall rules allow TCP 8081
3. Confirm DNS resolves 10.0.0.5
4. Review DUT configuration and restart services

[View Full Checklist] [Retry Checks]
```

---

## 11. Settings and Configuration

### 11.1 Conformance Test Settings

```
┌─ Conformance Test Settings
├─ DUT Configuration
│  ├─ Endpoint: [http://10.0.0.5:8081] 🔄 Verify
│  ├─ Timeout (ms): [10000]
│  ├─ Retry Count: [3]
│  └─ Auth Token: [••••••••] 🔑
│
├─ Simulator Configuration
│  ├─ A1-P Producer: [http://10.0.0.6:8082]
│  ├─ Failure Mode: ○ None  ◉ Random  ○ All
│  └─ Latency Injection: [0-100] ms random
│
├─ Evidence Capture
│  ├─ ☑ Capture HTTP Messages
│  ├─ ☑ Validate Schemas
│  ├─ ☑ Generate JSON Reports
│  └─ ☑ Keep Logs > 30 days
│
└─ [Save Settings] [Reset to Defaults]
```

---

## 12. Export and Reporting

### 12.1 Export Options

After test run, provide download options:

```
┌─ Export Results
├─ ◉ PDF Report (conformance_20260630_143056.pdf)
├─ ○ JSON Evidence (evidence_20260630_143056.json)
├─ ○ CSV Summary (summary_20260630_143056.csv)
├─ ○ HTML Report (report_20260630_143056.html)
└─ [Select All] [Download Selected]
```

### 12.2 PDF Report Contents

- Conformance summary (PASS/FAIL verdict)
- Test results by category
- Spec references and verification notes
- HTTP message excerpts (key exchanges)
- Evidence artifact references
- Digital signature or attestation (if enabled)

---

## 13. Navigation and Help

### 13.1 Help Sidebar (Collapsible)

```
┌─ Help & Documentation
├─ What are Conformance Tests?
│  These tests verify the Non-RT RIC implements
│  TS 103 989 §4.2 conformance requirements.
│
├─ Test Categories
│  • Policy Type Query: GET operations on policy types
│  • Policy CRUD: Create/Read/Update/Delete policies
│  • Error Handling: Verify error responses (4xx, 5xx)
│  • Header/Body: Validate HTTP response format
│  • Evidence: Check message logs and verdicts
│
├─ DUT Readiness
│  Before running tests, verify DUT is ready using
│  the checklist. All checks must pass.
│
├─ Understanding Results
│  ✓ PASS = All checks passed; conformant
│  ✗ FAIL = At least one check failed; non-conformant
│  ⚠ INCONCLUSIVE = Test infrastructure issue
│
├─ Learn More
│  📖 TS 103 989 Specification
│  📖 A1 Interface Design Guide
│  📖 Troubleshooting Guide
│
└─ [Close Help]
```

---

## 14. Technical Implementation Details

### 14.1 Frontend Components

| Component | Framework | Purpose |
|---|---|---|
| **TestSummaryCard** | React/Vue | Display overall conformance status |
| **TestCategoryTabs** | React/Vue | Organize and expand test categories |
| **TestCard** | React/Vue | Show individual test info and actions |
| **ProgressBar** | Chart.js / D3 | Visualize execution progress |
| **LiveLogStream** | Virtualized List | Scroll through HTTP messages in real-time |
| **ResultsSummary** | React/Vue | Show final pass/fail summary |
| **EvidenceViewer** | JSON/HTML renderer | Display HTTP exchanges and validation |
| **DUTReadinessChecklist** | React/Vue | Pre-run validation |
| **ExportDialog** | File Download API | Generate and download reports |

### 14.2 Backend API Endpoints (New or Extended)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/oran/conformance/tests` | GET | List all 26 conformance tests |
| `/api/oran/conformance/categories` | GET | List 5 test categories |
| `/api/oran/conformance/run` | POST | Start conformance test run |
| `/api/oran/conformance/status/{runId}` | GET | Get run status and progress |
| `/api/oran/conformance/results/{runId}` | GET | Get final results and summary |
| `/api/oran/conformance/evidence/{testId}` | GET | Get full evidence for a test |
| `/api/oran/conformance/dut-readiness` | GET | Get DUT readiness check results |
| `/api/oran/conformance/export/{runId}` | GET | Export results (PDF/JSON/CSV) |
| `/api/oran/conformance/ws/{runId}` | WS | WebSocket for live streaming |

### 14.3 Data Models (Backend/Frontend)

```python
class ConformanceTest(BaseModel):
    test_id: str  # e.g., "test_policy_type_list_returns_200"
    category: str  # "Policy Type Query Operations"
    description: str
    spec_reference: str  # "TS 103 987 §5.2.3.2"
    checks: List[str]
    expected_duration_sec: int
    status: Literal["NotRun", "Running", "Passed", "Failed", "Inconclusive"]
    last_result: Optional[dict]  # timestamp, duration, verdict_reason

class ConformanceRun(BaseModel):
    run_id: str
    start_time: datetime
    end_time: Optional[datetime]
    test_ids: List[str]
    results: Dict[str, ConformanceTest]
    summary: ConformanceSummary
    evidence_artifacts: List[str]  # file paths

class ConformanceSummary(BaseModel):
    total: int = 26
    passed: int
    failed: int
    inconclusive: int
    pass_rate: float  # 0-100%
    verdict: Literal["CONFORM", "NON-CONFORM", "INCONCLUSIVE"]
    conformance_statement: str
```

---

## 15. Responsive Design

### 15.1 Mobile Breakpoints

| Breakpoint | Device | Adaptations |
|---|---|---|
| **≥1200px** | Desktop | Full layout with sidebars |
| **992–1200px** | Tablet (landscape) | Collapsible sidebars, reduced padding |
| **576–992px** | Tablet (portrait) | Stacked layout, cards full-width |
| **<576px** | Mobile | Single-column, floating buttons |

### 15.2 Mobile-Specific UI

- Collapsible category sections (tap to expand)
- Floating action button for "Run All Tests"
- Horizontal scroll for result summary
- Bottom sheet for evidence viewer

---

## 16. Accessibility (WCAG 2.1 AA)

- **Color Contrast:** Pass/Fail/Inconclusive use distinct colors + icons
- **Keyboard Navigation:** Tab through categories, tests, and buttons
- **Screen Reader:** Semantic HTML, ARIA labels on dynamic content
- **Focus Indicators:** Visible outline on focused elements
- **Alternative Text:** Describe icons and charts with alt text

---

## 17. Performance Considerations

- **Lazy Load:** Defer loading test details until user expands category
- **Virtualization:** Render only visible test cards in live log stream
- **Caching:** Cache conformance test definitions; refresh on demand
- **WebSocket:** Use WebSocket for live streaming to reduce polling overhead
- **Progress Indicator:** Update progress bar every 2–5 seconds (not on every message)

---

## 18. Success Criteria

- [x] Conformance Test tab displays all 26 tests organized by category
- [x] User can run all tests or select subset; progress updates in real-time
- [x] DUT readiness checks pass before test execution
- [x] Individual test results show HTTP exchanges, schema validation, spec references
- [x] Conformance summary provides clear PASS/FAIL verdict
- [x] Evidence artifacts (logs, reports) are downloadable
- [x] UI is responsive on desktop, tablet, and mobile
- [x] Accessibility standards met (WCAG 2.1 AA)

---

## 19. Future Enhancements (Phase 2+)

- Test scheduling and automated runs (cron-based)
- Trend analysis (pass rates over time)
- A/B testing support (compare two DUT versions)
- Custom test scripting (user-defined conformance tests)
- Integration with CI/CD pipeline (webhook triggers)
- Multi-language support (i18n)
