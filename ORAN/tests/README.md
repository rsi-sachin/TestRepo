# ORAN Test Suite

Comprehensive test suite for validating Phase 3 implementation of the ORAN Test Generation Tool.

## Quick Start

### Run All Automated Tests
```powershell
cd C:\TestRepo\ORAN\tests
powershell -ExecutionPolicy Bypass -File run-simple-tests.ps1
```

**Expected Output:** 100% pass rate (40/40 tests)

### Start Server for Manual Testing
```powershell
cd C:\TestRepo\demo-web\backend
python run.py
```

Then open: http://localhost:8000

---

## Test Files

| File | Description | Type |
|------|-------------|------|
| **TEST_RESULTS.md** | Complete test execution results and status | Documentation |
| **PHASE3_TEST_PLAN.md** | Detailed test plan with all test cases | Test Plan |
| **QUICK_REFERENCE.md** | Quick commands and validation queries | Reference |
| **run-simple-tests.ps1** | Automated structural validation tests | Test Script |
| **run-phase3-tests.ps1** | Advanced automated tests (with Python) | Test Script |
| **database-validation.sql** | SQL queries for database validation | SQL Queries |
| **test_results_*.json** | Test execution logs (auto-generated) | Test Results |

---

## Test Coverage

### Phase 3A: Test Extraction Limit
- ✅ Config parameter validation (`max_tests_per_spec = 2`)
- ✅ Auto-generation produces exactly 8 tests (2 per spec)
- ✅ Extraction limit logic in parser service
- ⏳ End-to-end generation test (manual)

### Phase 3B: Database Save Fix
- ✅ Catalog generator returns tuple (catalog, deduplicated_cases)
- ✅ ORAN API uses deduplicated list
- ✅ save_to_database function properly called
- ✅ Database file exists and has content
- ⏳ Catalog-database consistency check (manual)
- ⏳ No duplicate test_ids verification (manual)

### Phase 3C: Section Selection UI
- ✅ Section selector JavaScript module exists
- ✅ All section selection functions implemented
- ✅ Preview sections API endpoint exists
- ✅ Generate from selection API endpoint exists
- ✅ Section selection modal in HTML
- ✅ All CSS styles present
- ⏳ Modal functionality test (manual)
- ⏳ Section filtering test (manual)
- ⏳ Custom selection test (manual)

### UI/UX Validation
- ✅ MVP notice present in HTML
- ✅ Both generation buttons present
- ✅ Manage Tests tab structure
- ✅ All CSS styling
- ⏳ Button state transitions (manual)
- ⏳ Filter functionality (manual)
- ⏳ Edit/Delete operations (manual)

---

## Test Results Summary

**Last Run:** June 4, 2026

### Automated Tests
- **Status:** ✅ PASSED
- **Pass Rate:** 100% (40/40)
- **Duration:** ~2 seconds

### Manual Tests
- **Status:** ⏳ PENDING
- **Requires:** Server running at http://localhost:8000

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed results.

---

## Running Tests

### Option 1: Simple Automated Tests (Recommended)
```powershell
cd C:\TestRepo\ORAN\tests
powershell -ExecutionPolicy Bypass -File run-simple-tests.ps1
```

**Tests:**
- File structure validation (13 tests)
- Config parameter validation (2 tests)
- Database save fix validation (3 tests)
- Section selection UI validation (7 tests)
- UI component validation (7 tests)
- Parser logic validation (2 tests)
- Database file validation (2 tests)
- Test data files validation (4 tests)

**Output:** Console report + test_results_*.json

### Option 2: Database Validation
```powershell
cd C:\TestRepo\ORAN\tests
Get-Content database-validation.sql
```

Copy and run SQL queries in your SQL client or using Python:
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM test_cases'); print(cursor.fetchone()[0]); conn.close()"
```

### Option 3: Manual UI Testing
1. Start server: `cd C:\TestRepo\demo-web\backend; python run.py`
2. Open browser: http://localhost:8000
3. Follow test scenarios in [PHASE3_TEST_PLAN.md](PHASE3_TEST_PLAN.md)

**Test Scenarios:**
- Scenario 1: Auto-generation (8 tests)
- Scenario 2: Preview sections (~646 sections)
- Scenario 3: MVP selection (8 tests)
- Scenario 4: Custom selection (5 tests)
- Scenario 5: Section filtering
- Scenario 6: Manage Tests tab
- Scenario 7: Large catalog (646 tests)

---

## Quick Validation Commands

### Check Database Test Count
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); print(f'Total: {conn.execute(\"SELECT COUNT(*) FROM test_cases\").fetchone()[0]}'); conn.close()"
```

### Check Latest Catalog
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); cursor = conn.cursor(); cursor.execute('SELECT catalog_id, COUNT(*) FROM test_cases GROUP BY catalog_id ORDER BY MAX(created_at) DESC LIMIT 1'); result = cursor.fetchone(); print(f'{result[0]}: {result[1]} tests'); conn.close()"
```

### Check for Duplicates
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); dups = conn.execute('SELECT COUNT(*) FROM (SELECT test_id FROM test_cases GROUP BY test_id HAVING COUNT(*) > 1)').fetchone()[0]; print(f'Duplicates: {dups} {\"PASS\" if dups == 0 else \"FAIL\"}'); conn.close()"
```

### Test API Endpoints
```powershell
# Preview sections
Invoke-RestMethod -Uri "http://localhost:8000/api/oran/preview-sections" -Method POST

# Generate from selection
$body = @{"TS_103_989" = @("5.2.6.2.1")} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/oran/generate-from-selection?catalog_name=Test" -Method POST -ContentType "application/json" -Body $body
```

---

## Expected Test Results

### Phase 3A: Extraction Limit
- Auto-generation: **8 tests** (2 per spec)
- Distribution: TS_103_989(2), TS_103_987(2), TS_103_988(2), TS_103_983(2)

### Phase 3B: Database Save
- Catalog JSON count = Database count
- Zero duplicate test_ids
- All required fields populated

### Phase 3C: Section Selection
- Preview: ~646 total sections available
- MVP selection: 8 sections (2 per spec)
- Custom selection: matches selected count
- All sections: ~646 tests generated

---

## Troubleshooting

### Server Won't Start
```powershell
# Check if port 8000 is in use
$pid = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess
if ($pid) { Stop-Process -Id $pid -Force }

# Restart server
cd C:\TestRepo\demo-web\backend
python run.py
```

### Database File Missing
Server auto-creates on startup. Just restart.

### Python Module Errors
```powershell
cd C:\TestRepo\demo-web\backend
pip install -r requirements.txt
```

### Test PDFs Missing
Ensure PDFs are in: `C:\TestRepo\ORAN\docs\`
- ts_103989v040200p.pdf
- ts_103987v040300p.pdf
- ts_103988v090000p.pdf
- ts_103983v040000p.pdf

---

## Performance Benchmarks

| Operation | Target | Notes |
|-----------|--------|-------|
| Upload 4 PDFs | <5s | Per-file upload |
| Preview sections | <5s | Extract all sections |
| Generate 8 tests | <10s | MVP mode |
| Generate 50 tests | <15s | Medium catalog |
| Generate 646 tests | <60s | Full catalog |

---

## CI/CD Integration

Add to your pipeline:

```yaml
test-phase3:
  runs-on: windows-latest
  steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        cd demo-web/backend
        pip install -r requirements.txt
    
    - name: Run automated tests
      run: |
        cd ORAN/tests
        powershell -ExecutionPolicy Bypass -File run-simple-tests.ps1
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: ORAN/tests/test_results_*.json
```

---

## Regression Testing

Before each release:

1. Run automated tests: `run-simple-tests.ps1` → Should be 100% pass
2. Start server and run manual scenarios 1-7
3. Run database validation queries
4. Check performance benchmarks
5. Verify no duplicate test_ids
6. Test all UI features (edit, delete, filter)

---

## Contributing

When adding new tests:

1. Add test case to `PHASE3_TEST_PLAN.md`
2. Implement in `run-simple-tests.ps1` if automated
3. Document expected results in `TEST_RESULTS.md`
4. Update this README with new coverage

---

## Support

**Documentation:**
- Full test plan: [PHASE3_TEST_PLAN.md](PHASE3_TEST_PLAN.md)
- Test results: [TEST_RESULTS.md](TEST_RESULTS.md)
- Quick reference: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**Commands:**
- All database queries: [database-validation.sql](database-validation.sql)
- Test scripts: `run-simple-tests.ps1`, `run-phase3-tests.ps1`

**Project Docs:**
- Main README: `C:\TestRepo\demo-web\README.md`
- Phase 2 completion: `C:\TestRepo\demo-web\PHASE2-COMPLETE.md`
- Requirements: `C:\TestRepo\docs\requirements.txt`

---

**Last Updated:** June 4, 2026  
**Phase:** 3 (Database Integration + Extraction Limit + Section Selection)  
**Status:** Automated tests passing, manual tests pending
