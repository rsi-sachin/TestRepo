# Phase 3 Simple Test Runner
# Runs basic file and structure validation without complex Python integration

$ErrorActionPreference = "Continue"
$PassCount = 0
$FailCount = 0

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ORAN Phase 3 Simple Test Suite" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

function Test-Result {
    param([string]$TestId, [string]$Description, [bool]$Passed)
    
    if ($Passed) {
        $script:PassCount++
        Write-Host "  [PASS] $Description" -ForegroundColor Green
    } else {
        $script:FailCount++
        Write-Host "  [FAIL] $Description" -ForegroundColor Red
    }
}

# Test Suite 1: File Structure
Write-Host "[Suite 1] File Structure Validation" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Gray

$files = @(
    "C:\TestRepo\demo-web\backend\app\config.py",
    "C:\TestRepo\demo-web\backend\app\database.py",
    "C:\TestRepo\demo-web\backend\app\models\db_models.py",
    "C:\TestRepo\demo-web\backend\app\services\test_case_service.py",
    "C:\TestRepo\demo-web\backend\app\services\catalog_generator_service.py",
    "C:\TestRepo\demo-web\backend\app\services\spec_parser_service.py",
    "C:\TestRepo\demo-web\backend\app\parsers\test_clause_extractor.py",
    "C:\TestRepo\demo-web\backend\app\api\oran.py",
    "C:\TestRepo\demo-web\backend\app\api\test_cases.py",
    "C:\TestRepo\demo-web\frontend\static\js\section_selector.js",
    "C:\TestRepo\demo-web\frontend\static\js\test_management.js",
    "C:\TestRepo\demo-web\frontend\templates\index.html",
    "C:\TestRepo\demo-web\frontend\static\css\oran.css"
)

foreach ($file in $files) {
    $exists = Test-Path $file
    Test-Result "FS-$(($files.IndexOf($file)+1))" "File exists: $(Split-Path $file -Leaf)" $exists
}

# Test Suite 2: Phase 3A - Config
Write-Host "`n[Suite 2] Phase 3A - Config Validation" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Gray

$configPath = "C:\TestRepo\demo-web\backend\app\config.py"
$configContent = Get-Content $configPath -Raw
Test-Result "3A-001" "Config has max_tests_per_spec parameter" ($configContent -match "max_tests_per_spec")
Test-Result "3A-002" "Config default value is 2" ($configContent -match "max_tests_per_spec.*=.*2")

# Test Suite 3: Phase 3B - Database Logic
Write-Host "`n[Suite 3] Phase 3B - Database Save Fix" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Gray

$catalogPath = "C:\TestRepo\demo-web\backend\app\services\catalog_generator_service.py"
$catalogContent = Get-Content $catalogPath -Raw
Test-Result "3B-001" "Catalog generator returns tuple" ($catalogContent -match "Tuple\[OranTestCatalog, List\[EnrichedTestCase\]\]")

$oranPath = "C:\TestRepo\demo-web\backend\app\api\oran.py"
$oranContent = Get-Content $oranPath -Raw
Test-Result "3B-002" "ORAN API uses deduplicated list" ($oranContent -match "deduplicated_cases")
Test-Result "3B-003" "save_to_database is called" ($oranContent -match "save_to_database")

# Test Suite 4: Phase 3C - Section Selection UI
Write-Host "`n[Suite 4] Phase 3C - Section Selection UI" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Gray

$selectorPath = "C:\TestRepo\demo-web\frontend\static\js\section_selector.js"
Test-Result "3C-001" "Section selector module exists" (Test-Path $selectorPath)

if (Test-Path $selectorPath) {
    $selectorContent = Get-Content $selectorPath -Raw
    Test-Result "3C-002" "Has initSectionSelector function" ($selectorContent -match "function initSectionSelector")
    Test-Result "3C-003" "Has handlePreviewSections function" ($selectorContent -match "function handlePreviewSections")
    Test-Result "3C-004" "Has handleGenerateFromSelection function" ($selectorContent -match "function handleGenerateFromSelection")
    Test-Result "3C-005" "Has section filtering logic" ($selectorContent -match "applyFilters")
}

# Check ORAN API endpoints
Test-Result "3C-006" "Preview sections endpoint exists" ($oranContent -match "preview-sections")
Test-Result "3C-007" "Generate from selection endpoint exists" ($oranContent -match "generate-from-selection")

# Test Suite 5: UI Components
Write-Host "`n[Suite 5] UI Component Validation" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Gray

$htmlPath = "C:\TestRepo\demo-web\frontend\templates\index.html"
$htmlContent = Get-Content $htmlPath -Raw
Test-Result "UI-001" "Section selection modal exists" ($htmlContent -match "section-selection-modal")
Test-Result "UI-002" "MVP notice exists" ($htmlContent -match "mvp-notice")
Test-Result "UI-003" "Preview button exists" ($htmlContent -match "preview-sections-btn")
Test-Result "UI-004" "Generate auto button exists" ($htmlContent -match "generate-catalog-btn")

$cssPath = "C:\TestRepo\demo-web\frontend\static\css\oran.css"
$cssContent = Get-Content $cssPath -Raw
Test-Result "UI-005" "Section selection styles exist" ($cssContent -match "sections-table")
Test-Result "UI-006" "Generation button styles exist" ($cssContent -match "generation-buttons")
Test-Result "UI-007" "MVP notice styles exist" ($cssContent -match "mvp-notice")

# Test Suite 6: Parser Logic
Write-Host "`n[Suite 6] Parser Logic Validation" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Gray

$extractorPath = "C:\TestRepo\demo-web\backend\app\parsers\test_clause_extractor.py"
$extractorContent = Get-Content $extractorPath -Raw
Test-Result "P-001" "Extractor accepts max_tests parameter" ($extractorContent -match "max_tests")

$parserPath = "C:\TestRepo\demo-web\backend\app\services\spec_parser_service.py"
$parserContent = Get-Content $parserPath -Raw
Test-Result "P-002" "Parser passes max_tests_per_spec" ($parserContent -match "max_tests_per_spec")

# Test Suite 7: Database File
Write-Host "`n[Suite 7] Database Validation" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Gray

$dbPath = "C:\TestRepo\demo-web\backend\data\oran_database\oran_test_cases.db"
$dbExists = Test-Path $dbPath
Test-Result "DB-001" "Database file exists" $dbExists

if ($dbExists) {
    $dbInfo = Get-Item $dbPath
    Test-Result "DB-002" "Database file size > 0" ($dbInfo.Length -gt 0)
}

# Test PDFs
Write-Host "`n[Suite 8] Test Data Files" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Gray

$specDir = "C:\TestRepo\ORAN\docs"
$pdfs = @(
    "ts_103989v040200p.pdf",
    "ts_103987v040300p.pdf",
    "ts_103988v090000p.pdf",
    "ts_103983v040000p.pdf"
)

foreach ($pdf in $pdfs) {
    $pdfPath = Join-Path $specDir $pdf
    Test-Result "TD-$(($pdfs.IndexOf($pdf)+1))" "PDF exists: $pdf" (Test-Path $pdfPath)
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$total = $PassCount + $FailCount
$passRate = if ($total -gt 0) { [math]::Round(($PassCount / $total) * 100, 1) } else { 0 }

Write-Host "`nTotal Tests: $total" -ForegroundColor White
Write-Host "Passed: $PassCount" -ForegroundColor Green
Write-Host "Failed: $FailCount" -ForegroundColor Red
Write-Host "Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 80) { "Green" } else { "Red" })

# Server Check
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Server Status Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "[PASS] Server is running at http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Server is NOT running" -ForegroundColor Red
    Write-Host "  Start server with:" -ForegroundColor Yellow
    Write-Host "    cd C:\TestRepo\demo-web\backend" -ForegroundColor Gray
    Write-Host "    python run.py" -ForegroundColor Gray
}

# Manual Test Instructions
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Next Steps: Manual Testing" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nProceed with manual testing:" -ForegroundColor White
Write-Host "1. Open http://localhost:8000" -ForegroundColor Gray
Write-Host "2. Upload 4 PDFs from C:\TestRepo\ORAN\docs" -ForegroundColor Gray
Write-Host "3. Test 'Generate Test Catalog (Auto)' - should create 8 tests" -ForegroundColor Gray
Write-Host "4. Test 'Preview & Select Sections' - should show ~646 sections" -ForegroundColor Gray
Write-Host "5. Use 'Select MVP' button - should select 8 sections" -ForegroundColor Gray
Write-Host "6. Generate catalog from selection" -ForegroundColor Gray
Write-Host "7. Check 'Manage Tests' tab - verify tests appear" -ForegroundColor Gray
Write-Host "`nFor database validation, run:" -ForegroundColor White
Write-Host "  cd C:\TestRepo\ORAN\tests" -ForegroundColor Gray
Write-Host "  Get-Content database-validation.sql" -ForegroundColor Gray
Write-Host "`nDetailed test plan: PHASE3_TEST_PLAN.md" -ForegroundColor Cyan

if ($FailCount -eq 0) {
    Write-Host "`n[PASS] All structural tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n[FAIL] Some tests failed. Review above." -ForegroundColor Red
    exit 1
}
