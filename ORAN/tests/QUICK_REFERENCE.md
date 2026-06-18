# Phase 3 Testing Quick Reference

## Quick Test Execution

### 1. Run Automated Tests
```powershell
cd C:\TestRepo\ORAN\tests
.\run-phase3-tests.ps1
```

### 2. Run Database Validation
```powershell
cd C:\TestRepo\ORAN\tests
sqlite3 C:\TestRepo\demo-web\backend\data\oran_database\oran_test_cases.db < database-validation.sql
```

Or use Python:
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); print(conn.execute('SELECT COUNT(*) FROM test_cases').fetchone()[0]); conn.close()"
```

### 3. Manual UI Tests
- Open http://localhost:8000
- Follow test plan in PHASE3_TEST_PLAN.md

---

## Quick Validation Commands

### Check Test Count
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM test_cases'); print(f'Total tests: {cursor.fetchone()[0]}'); conn.close()"
```

### Check Latest Catalog
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); cursor = conn.cursor(); cursor.execute('SELECT catalog_id, COUNT(*) FROM test_cases GROUP BY catalog_id ORDER BY MAX(created_at) DESC LIMIT 1'); result = cursor.fetchone(); print(f'Latest catalog: {result[0]} with {result[1]} tests'); conn.close()"
```

### Check for Duplicates
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM (SELECT test_id FROM test_cases GROUP BY test_id HAVING COUNT(*) > 1)'); dups = cursor.fetchone()[0]; print(f'Duplicate test_ids: {dups}'); print('PASS' if dups == 0 else 'FAIL'); conn.close()"
```

### Check Distribution by Spec
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); cursor = conn.cursor(); cursor.execute('SELECT source_spec, COUNT(*) FROM test_cases WHERE catalog_id=(SELECT catalog_id FROM test_cases ORDER BY created_at DESC LIMIT 1) GROUP BY source_spec'); print('\n'.join([f'{row[0]}: {row[1]}' for row in cursor.fetchall()])); conn.close()"
```

---

## API Testing

### Test Preview Sections
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/oran/preview-sections" -Method POST | ConvertTo-Json -Depth 3
```

### Test Generate from Selection
```powershell
$body = @{
    "TS_103_989" = @("5.2.6.2.1", "5.3.1")
    "TS_103_987" = @("4.2.1")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/oran/generate-from-selection?catalog_name=Test&description=API+Test" -Method POST -ContentType "application/json" -Body $body | ConvertTo-Json
```

---

## Expected Results Summary

### Phase 3A: Test Extraction Limit
- ✅ Auto-generation produces 8 tests
- ✅ Distribution: 2 tests per spec (4 specs × 2 = 8)
- ✅ Log shows: "Limited extraction to 2/XXX available tests"

### Phase 3B: Database Save
- ✅ Catalog JSON test count matches database count
- ✅ No duplicate test_ids
- ✅ All required fields populated
- ✅ Valid HTTP methods and status codes

### Phase 3C: Section Selection
- ✅ Preview shows ~646 total sections
- ✅ "Select MVP" selects 8 sections
- ✅ Custom selection generates correct count
- ✅ Modal closes after generation
- ✅ Tests appear in Manage Tests tab

---

## Common Issues & Solutions

### Issue: Server not running
**Solution:**
```powershell
cd C:\TestRepo\demo-web\backend
python run.py
```

### Issue: Port 8000 in use
**Solution:**
```powershell
# Find and kill process on port 8000
$pid = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess
if ($pid) { Stop-Process -Id $pid -Force }
```

### Issue: Database file missing
**Solution:** Server auto-creates on startup. Restart server.

### Issue: Test files not found
**Solution:** Ensure PDFs are in `C:\TestRepo\ORAN\docs\`

### Issue: Module import errors
**Solution:**
```powershell
cd C:\TestRepo\demo-web\backend
pip install -r requirements.txt
```

---

## Regression Test Checklist

Before each release, verify:
- [ ] Auto-generation produces 8 tests
- [ ] Database count matches catalog count
- [ ] No duplicate test_ids
- [ ] Preview sections shows all available
- [ ] Section selection generates correct count
- [ ] Manage Tests tab displays results
- [ ] Edit/Delete functions work
- [ ] Filters function correctly

---

## Performance Benchmarks

| Operation | Expected Time | Actual Time |
|-----------|--------------|-------------|
| Upload 4 PDFs | < 5s | _measure_ |
| Preview sections | < 5s | _measure_ |
| Generate 8 tests | < 10s | _measure_ |
| Generate 50 tests | < 15s | _measure_ |
| Generate 646 tests | < 60s | _measure_ |

---

## Test Data Cleanup

### Delete specific catalog
```powershell
python -c "import sqlite3; conn = sqlite3.connect('C:/TestRepo/demo-web/backend/data/oran_database/oran_test_cases.db'); conn.execute('DELETE FROM test_cases WHERE catalog_id=\"<catalog-id>\"'); conn.commit(); conn.close()"
```

### Reset entire database
```powershell
Remove-Item C:\TestRepo\demo-web\backend\data\oran_database\oran_test_cases.db
# Restart server to recreate
```

---

## CI/CD Integration

Add to your CI pipeline:
```yaml
test:
  script:
    - cd C:/TestRepo/ORAN/tests
    - powershell -ExecutionPolicy Bypass -File run-phase3-tests.ps1
  artifacts:
    paths:
      - ORAN/tests/test_results_*.json
    when: always
```

---

**For detailed test plan, see:** PHASE3_TEST_PLAN.md  
**For database queries, see:** database-validation.sql
