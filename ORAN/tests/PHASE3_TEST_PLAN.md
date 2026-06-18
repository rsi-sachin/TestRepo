# Phase 3 Test Plan - ORAN Test Generation Tool

**Test Date:** June 4, 2026  
**Phase:** 3 (Database Integration + Test Extraction Limit + Section Selection UI)  
**Test Author:** Automated Testing Suite  

---

## Overview

Phase 3 consists of three major components:
- **Phase 3A:** Test extraction limit (2 tests per spec, 8 total for MVP)
- **Phase 3B:** Database save bug fix (catalog and database match)
- **Phase 3C:** Section selection UI (manual section selection)

---

## Test Environment

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2.0.50
- **Frontend:** Vanilla JavaScript ES6, HTML5, CSS3
- **Database:** SQLite at `./data/oran_database/oran_test_cases.db`
- **Server:** http://localhost:8000
- **Browser:** Modern browser with ES6 module support

---

## Pre-Test Setup

### 1. Database Initialization
```powershell
# Clean database for fresh test
Remove-Item C:\TestRepo\demo-web\backend\data\oran_database\oran_test_cases.db -ErrorAction SilentlyContinue

# Server will auto-create on startup
```

### 2. Required Test Files
```
C:\TestRepo\ORAN\docs\
├── ts_103989v040200p.pdf  (TS 103 989 - Test Spec)
├── ts_103987v040300p.pdf  (TS 103 987 - App Protocol)
├── ts_103988v090000p.pdf  (TS 103 988 - Type Definitions)
└── ts_103983v040000p.pdf  (TS 103 983 - General Principles)
```

### 3. Server Start
```powershell
cd C:\TestRepo\demo-web\backend
python run.py
```

---

## Test Suite 1: Phase 3A - Test Extraction Limit

### Test 1.1: Config Parameter Validation
**Objective:** Verify `max_tests_per_spec` config exists

**Steps:**
1. Open `backend/app/config.py`
2. Verify line contains: `max_tests_per_spec: int = 2`

**Expected Result:** ✅ Config parameter exists with default value of 2

**Actual Result:** _To be filled during test execution_

---

### Test 1.2: Auto-Generation with Limit
**Objective:** Verify catalog generates exactly 8 tests (2 per spec)

**Steps:**
1. Open http://localhost:8000
2. Click "Upload Specs" tab
3. Upload all 4 ETSI PDF files
4. Enter catalog name: "Phase 3A Test - Auto Mode"
5. Click "Generate Test Catalog (Auto)"
6. Wait for completion

**Expected Results:**
- ✅ Catalog generation succeeds
- ✅ Catalog JSON shows `"total_tests": 8`
- ✅ Database query returns 8 rows
- ✅ UI shows "8 tests" in catalog list
- ✅ Logs show "Limited extraction to 2/XXX available tests (MVP constraint)"

**SQL Verification:**
```sql
SELECT COUNT(*) FROM test_cases;  -- Should return 8
SELECT catalog_id, COUNT(*) as test_count 
FROM test_cases 
GROUP BY catalog_id;  -- Should show 8 for new catalog
```

**Actual Result:** _To be filled during test execution_

---

### Test 1.3: Extraction Distribution
**Objective:** Verify 2 tests extracted from each spec

**Steps:**
1. Generate catalog using auto mode
2. Query database by source spec

**SQL Verification:**
```sql
SELECT source_spec, COUNT(*) as count 
FROM test_cases 
WHERE catalog_id = '<latest-catalog-id>'
GROUP BY source_spec;
```

**Expected Result:**
```
TS_103_989 | 2
TS_103_987 | 2
TS_103_988 | 2
TS_103_983 | 2
```

**Actual Result:** _To be filled during test execution_

---

## Test Suite 2: Phase 3B - Database Save Fix

### Test 2.1: Catalog-Database Consistency
**Objective:** Verify catalog JSON and database have same test count

**Steps:**
1. Generate catalog using auto mode
2. Get catalog JSON test count
3. Query database test count
4. Compare values

**SQL Verification:**
```sql
-- Get latest catalog
SELECT catalog_id, COUNT(*) as db_count 
FROM test_cases 
WHERE catalog_id = (SELECT catalog_id FROM test_cases ORDER BY created_at DESC LIMIT 1)
GROUP BY catalog_id;
```

**Expected Result:** ✅ JSON total_tests == database count (both 8)

**Actual Result:** _To be filled during test execution_

---

### Test 2.2: Individual Test Case Verification
**Objective:** Verify test cases are properly saved with all fields

**Steps:**
1. Generate catalog
2. Query database for test case details

**SQL Verification:**
```sql
SELECT test_id, scenario, source_spec, source_section, http_method, endpoint, expected_status, complexity
FROM test_cases
WHERE catalog_id = '<latest-catalog-id>'
LIMIT 5;
```

**Expected Result:**
- ✅ All fields populated (no NULL values in required fields)
- ✅ test_id follows format: `oran-a1-X-X-X`
- ✅ http_method is valid (GET, POST, PUT, DELETE, PATCH)
- ✅ expected_status is numeric (200, 201, etc.)
- ✅ complexity is valid (BASIC, INTERMEDIATE, ADVANCED)

**Actual Result:** _To be filled during test execution_

---

### Test 2.3: No Duplicate Test IDs
**Objective:** Verify UNIQUE constraint on test_id works

**Steps:**
1. Generate multiple catalogs
2. Check for duplicate test_ids

**SQL Verification:**
```sql
SELECT test_id, COUNT(*) as count
FROM test_cases
GROUP BY test_id
HAVING COUNT(*) > 1;
```

**Expected Result:** ✅ No results (no duplicates)

**Actual Result:** _To be filled during test execution_

---

## Test Suite 3: Phase 3C - Section Selection UI

### Test 3.1: Preview Sections Functionality
**Objective:** Verify "Preview & Select Sections" button works

**Steps:**
1. Upload all 4 PDFs
2. Click "Preview & Select Sections" button
3. Verify modal opens

**Expected Results:**
- ✅ Modal opens with title "Select Test Sections"
- ✅ Shows selection stats: "0 of XXX sections selected"
- ✅ Table displays sections from all 4 specs
- ✅ Search box is functional
- ✅ Spec filter dropdown is populated

**Actual Result:** _To be filled during test execution_

---

### Test 3.2: Section Filtering
**Objective:** Verify search and filter work correctly

**Steps:**
1. Open section selection modal
2. Type "test" in search box
3. Observe filtered results
4. Clear search
5. Select "TS_103_989" from spec filter
6. Observe filtered results

**Expected Results:**
- ✅ Search filters by title/section number
- ✅ Spec filter shows only selected spec's sections
- ✅ Filters work together (AND logic)
- ✅ "X of Y sections" updates correctly

**Actual Result:** _To be filled during test execution_

---

### Test 3.3: Selection Controls
**Objective:** Verify all selection buttons work

**Steps:**
1. Open section selection modal
2. Click "Select All" button
3. Verify all checkboxes checked
4. Click "Deselect All" button
5. Verify all checkboxes unchecked
6. Click "Select MVP (2 per spec)" button
7. Verify exactly 8 sections selected (2 from each spec)

**Expected Results:**
- ✅ "Select All" checks all visible sections
- ✅ "Deselect All" unchecks all sections
- ✅ "Select MVP" selects first 2 from each spec
- ✅ Selection count updates in real-time
- ✅ Generate button enables/disables based on selection

---

## Test Suite 4: Methodology Analysis Preview (Phase 2)

### Test 4.1: Methodology Analysis Panel
**Objective:** Verify the upload tab shows methodology analysis controls and results

**Steps:**
1. Open the Upload Specs tab
2. Select `TS 103 989 - A1 Test Specification` from the analysis dropdown
3. Click `Preview Modules & Titles`
4. Verify methodology sections, module candidates, and test title candidates render

**Expected Results:**
- ✅ Analysis summary shows spec file and counts
- ✅ Methodology sections list includes section number and title (single non-duplicated title line)
- ✅ Page/depth metadata is hidden in UI but remains available in API JSON (`page_number`, `depth`)
- ✅ Module candidates list shows candidate names and confidence
- ✅ Test title candidates list shows generated title-only suggestions

**Actual Result:** _To be filled during test execution_

### Test 4.2: Analysis Error Handling
**Objective:** Verify user sees a clear error if the selected spec cannot be analyzed

**Steps:**
1. Temporarily remove or rename the source document
2. Click `Preview Modules & Titles`
3. Verify failure state is shown in the panel

**Expected Results:**
- ✅ Panel shows a readable failure message
- ✅ No stale results remain displayed
- ✅ Backend returns a 404 with a useful detail message

**Actual Result:** _To be filled during test execution_

**Actual Result:** _To be filled during test execution_

---

### Test 3.4: Generate from Selection
**Objective:** Verify catalog generation from selected sections

**Steps:**
1. Open section selection modal
2. Select 5 specific sections manually
3. Click "Generate Catalog (5 sections)" button
4. Wait for completion
5. Verify results

**Expected Results:**
- ✅ Catalog generates successfully
- ✅ Catalog contains exactly 5 tests
- ✅ Database contains exactly 5 test cases
- ✅ Test IDs match selected sections
- ✅ Toast notification shows success message
- ✅ UI switches to Test Catalog tab

**SQL Verification:**
```sql
SELECT COUNT(*) FROM test_cases WHERE catalog_id = '<new-catalog-id>';
-- Should return 5
```

**Actual Result:** _To be filled during test execution_

---

### Test 3.5: Select All Sections (Full Catalog)
**Objective:** Verify generating catalog with all available sections

**Steps:**
1. Open section selection modal
2. Click "Select All" button
3. Note total count (should be ~646)
4. Click "Generate Catalog (646 sections)" button
5. Wait for completion (may take 30-60 seconds)

**Expected Results:**
- ✅ Catalog generates successfully
- ✅ Catalog contains ~646 tests
- ✅ Database contains ~646 test cases
- ✅ No duplicate test_ids
- ✅ Performance is acceptable (<60s)

**SQL Verification:**
```sql
SELECT COUNT(*) FROM test_cases WHERE catalog_id = '<new-catalog-id>';
-- Should return ~646
```

**Actual Result:** _To be filled during test execution_

---

## Test Suite 4: UI/UX Validation

### Test 4.1: MVP Notice Display
**Objective:** Verify MVP notice is visible and informative

**Steps:**
1. Navigate to Upload Specs tab
2. Locate blue info box above buttons

**Expected Result:**
- ✅ Blue notice box is visible
- ✅ Contains text: "MVP Demo Mode: Extraction limited to 2 tests per specification"
- ✅ Info icon is displayed
- ✅ Text is readable and well-formatted

**Actual Result:** _To be filled during test execution_

---

### Test 4.2: Button States
**Objective:** Verify buttons enable/disable correctly

**Steps:**
1. Navigate to Upload Specs tab
2. Verify both buttons are disabled
3. Upload 1 PDF
4. Verify buttons still disabled
5. Upload remaining 3 PDFs
6. Verify both buttons are enabled

**Expected Results:**
- ✅ Initial state: both buttons disabled
- ✅ After 4 uploads: both buttons enabled
- ✅ Button text updates to show "4 specs ready"
- ✅ Icons are visible in buttons

**Actual Result:** _To be filled during test execution_

---

### Test 4.3: Manage Tests Tab Integration
**Objective:** Verify Phase 3 tests appear in Manage Tests tab

**Steps:**
1. Generate catalog (8 tests)
2. Navigate to "Manage Tests" tab
3. Verify tests are listed

**Expected Results:**
- ✅ Table shows 8 test cases
- ✅ All columns populated correctly
- ✅ Filters work
- ✅ Edit/Delete buttons functional
- ✅ Enrichment tooltips work

**Actual Result:** _To be filled during test execution_

---

## Test Suite 5: Error Handling

### Test 5.1: Preview Without Upload
**Objective:** Verify error handling when previewing without files

**Steps:**
1. Navigate to Upload Specs tab (don't upload files)
2. Click "Preview & Select Sections" button

**Expected Result:**
- ✅ Error message displayed
- ✅ Message indicates files must be uploaded first
- ✅ No modal opens

**Actual Result:** _To be filled during test execution_

---

### Test 5.2: Generate Without Selection
**Objective:** Verify error handling for empty selection

**Steps:**
1. Open section selection modal
2. Deselect all sections
3. Try to click "Generate Catalog" button

**Expected Result:**
- ✅ Generate button is disabled when count is 0
- ✅ Cannot proceed without selection

**Actual Result:** _To be filled during test execution_

---

## Test Suite 6: Backend API Validation

### Test 6.1: Preview Sections API
**Objective:** Test `/api/oran/preview-sections` endpoint

**HTTP Request:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/oran/preview-sections" -Method POST
```

**Expected Response:**
```json
{
  "status": "success",
  "total_sections": 646,
  "sections_by_spec": {
    "TS_103_989": [...],
    "TS_103_987": [...],
    "TS_103_988": [...],
    "TS_103_983": [...]
  },
  "message": "Found 646 available test sections across 4 specifications"
}
```

**Actual Result:** _To be filled during test execution_

---

### Test 6.2: Generate from Selection API
**Objective:** Test `/api/oran/generate-from-selection` endpoint

**HTTP Request:**
```powershell
$body = @{
    "TS_103_989" = @("5.2.6.2.1", "5.3.1")
    "TS_103_987" = @("4.2.1")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/oran/generate-from-selection?catalog_name=API Test&description=Testing API" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Expected Response:**
```json
{
  "catalog_id": "catalog-XXXX",
  "status": "completed",
  "message": "Successfully generated catalog with 3 test cases from selected sections",
  "total_tests": "3",
  "total_selected_sections": "3"
}
```

**Actual Result:** _To be filled during test execution_

---

## Performance Benchmarks

### Benchmark 1: Auto Generation (8 tests)
- **Expected Time:** < 10 seconds
- **Actual Time:** _To be measured_

### Benchmark 2: Preview All Sections
- **Expected Time:** < 5 seconds
- **Actual Time:** _To be measured_

### Benchmark 3: Generate from Selection (50 tests)
- **Expected Time:** < 15 seconds
- **Actual Time:** _To be measured_

### Benchmark 4: Generate All Sections (646 tests)
- **Expected Time:** < 60 seconds
- **Actual Time:** _To be measured_

---

## Test Suite 9: Protocol-Led Spec Selection (Phase 4)

### Test 9.1: Protocol/Interface Dropdown Visible and Defaulted
**Steps:**
1. Open http://localhost:8000
2. Navigate to Upload Specs tab

**Expected:**
- ✅ Protocol/Interface dropdown is visible
- ✅ "A1 Application Protocol" is preselected
- ✅ No other options are shown (single entry for now)

---

### Test 9.2: Specification Selection Multi-Select Shows All 4 Docs
**Steps:**
1. With Upload Specs tab active, inspect Specification Selection area

**Expected:**
- ✅ Four checkboxes, all pre-checked
- ✅ Each checkbox shows TS number and title:
  - TS 103 989 – A1 Test Specification
  - TS 103 987 – A1 Application Protocol
  - TS 103 988 – A1 Type Definitions
  - TS 103 983 – A1 General Principles

---

### Test 9.3: Auto-Bind from Docs Folder
**Steps:**
1. Verify PDFs are present in `C:\TestRepo\ORAN\docs\`
2. Open Upload Specs tab (all 4 specs checked)
3. Wait for Document Status panel to appear

**Expected:**
- ✅ Each spec shows green status: "Found in docs folder: ts_XXXXX.pdf"
- ✅ No file picker is shown
- ✅ Generate and Preview buttons become enabled

---

### Test 9.4: Missing Spec Triggers File Picker Row
**Steps:**
1. Temporarily rename one PDF in ORAN/docs to break auto-bind (e.g., add `.bak`)
2. Reload Upload Specs tab

**Expected:**
- ✅ That spec shows orange status: "Not found in docs folder — please select file"
- ✅ A "Choose File" button appears inline for that spec only
- ✅ Generate / Preview buttons remain disabled until resolved

---

### Test 9.5: Manual File Selection Resolves Missing Spec
**Steps:**
1. With one spec showing missing status, click its "Choose File" button
2. Select a valid PDF from the file explorer

**Expected:**
- ✅ Status changes to blue: "File selected: <filename>"
- ✅ Generate and Preview buttons enable once all specs resolved

---

### Test 9.6: Uncheck Spec Removes It from Resolution
**Steps:**
1. Uncheck "TS 103 988" checkbox
2. Observe Document Status panel

**Expected:**
- ✅ TS 103 988 row is removed from Document Status
- ✅ Generate / Preview buttons re-check enablement based on remaining selected specs

---

### Test 9.7: Generation Uses Only Selected Specs
**Steps:**
1. Uncheck TS 103 987 and TS 103 983
2. Click "Generate Test Catalog (Auto)" (all remaining selected specs resolved)
3. Verify catalog created with tests only from TS 103 989 and TS 103 988

**SQL Verification:**
```sql
SELECT source_spec, COUNT(*) FROM test_cases
WHERE catalog_id = '<latest>'
GROUP BY source_spec;
-- Should return only TS_103_989 and TS_103_988
```

---

Run this checklist before each release:

- [ ] Test 1.2: Auto-generation produces 8 tests
- [ ] Test 2.1: Catalog and database counts match
- [ ] Test 2.3: No duplicate test IDs
- [ ] Test 3.1: Preview sections modal opens
- [ ] Test 3.3: Selection controls work
- [ ] Test 3.4: Generate from 5 selected sections
- [ ] Test 4.2: Button states correct
- [ ] Test 4.3: Manage Tests tab shows tests
- [ ] Test 6.1: Preview API returns data
- [ ] Test 6.2: Generate API creates tests

---

## Test Execution Log

### Test Run 1: June 4, 2026

**Tester:** _Name_  
**Environment:** Windows 11, Python 3.13, Chrome 125  
**Server Version:** ORAN MVP Phase 3  

**Results:**
- Suite 1 (Extraction Limit): _PASS/FAIL_
- Suite 2 (Database Save): _PASS/FAIL_
- Suite 3 (Section Selection): _PASS/FAIL_
- Suite 4 (UI/UX): _PASS/FAIL_
- Suite 5 (Error Handling): _PASS/FAIL_
- Suite 6 (API): _PASS/FAIL_

**Issues Found:** _List any bugs or problems_

**Notes:** _Additional observations_

---

## Known Issues

_To be documented during testing_

---

## Future Test Cases

1. **Concurrent Users:** Test multiple users generating catalogs simultaneously
2. **Large Files:** Test with 100MB+ PDF files
3. **Corrupt Files:** Test error handling with invalid PDFs
4. **Browser Compatibility:** Test on Firefox, Safari, Edge
5. **Mobile Responsiveness:** Test on tablet and phone screens
6. **Load Testing:** Generate 10+ catalogs in rapid succession

---

**End of Test Plan**
