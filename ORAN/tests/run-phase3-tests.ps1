# Phase 3 Automated Test Suite
# Tests extraction limit, database save, and section selection functionality

param(
    [switch]$Verbose,
    [switch]$SkipCleanup
)

$ErrorActionPreference = "Continue"
$script:TestResults = @()
$script:PassCount = 0
$script:FailCount = 0
$script:StartTime = Get-Date

# Configuration
$API_BASE = "http://localhost:8000"
$DB_PATH = "C:\TestRepo\demo-web\backend\data\oran_database\oran_test_cases.db"
$SPEC_DIR = "C:\TestRepo\ORAN\docs"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ORAN Phase 3 Automated Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Helper Functions
function Write-TestHeader {
    param([string]$TestName)
    Write-Host "`n[TEST] $TestName" -ForegroundColor Yellow
    Write-Host ("=" * 60) -ForegroundColor Gray
}

function Write-TestResult {
    param(
        [string]$TestId,
        [string]$Description,
        [bool]$Passed,
        [string]$Details = ""
    )
    
    $result = @{
        TestId = $TestId
        Description = $Description
        Passed = $Passed
        Details = $Details
        Timestamp = Get-Date
    }
    
    $script:TestResults += $result
    
    if ($Passed) {
        $script:PassCount++
        Write-Host "  ✓ PASS: $Description" -ForegroundColor Green
    } else {
        $script:FailCount++
        Write-Host "  ✗ FAIL: $Description" -ForegroundColor Red
        if ($Details) {
            Write-Host "    Details: $Details" -ForegroundColor Gray
        }
    }
}

function Test-ServerRunning {
    try {
        $response = Invoke-WebRequest -Uri "$API_BASE/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        return $true
    } catch {
        try {
            $response = Invoke-WebRequest -Uri "$API_BASE/" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
            return $true
        } catch {
            return $false
        }
    }
}

function Get-DatabaseTestCount {
    param([string]$CatalogId = "")
    
    try {
        $query = if ($CatalogId) {
            "SELECT COUNT(*) as count FROM test_cases WHERE catalog_id='$CatalogId'"
        } else {
            "SELECT COUNT(*) as count FROM test_cases"
        }
        
        $result = & python -c @"
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()
cursor.execute('$query')
result = cursor.fetchone()
print(result[0] if result else 0)
conn.close()
"@
        return [int]$result
    } catch {
        return -1
    }
}

function Get-LatestCatalogId {
    try {
        $result = & python -c @"
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()
cursor.execute('SELECT catalog_id FROM test_cases ORDER BY created_at DESC LIMIT 1')
result = cursor.fetchone()
print(result[0] if result else '')
conn.close()
"@
        return $result
    } catch {
        return ""
    }
}

# Pre-Test Validation
Write-TestHeader "Pre-Test Validation"

# Check if server is running
$serverRunning = Test-ServerRunning
Write-TestResult "PRE-001" "Server is running" $serverRunning "Check http://localhost:8000"

# Check if test files exist
$specFiles = @(
    "$SPEC_DIR\ts_103989v040200p.pdf",
    "$SPEC_DIR\ts_103987v040300p.pdf",
    "$SPEC_DIR\ts_103988v090000p.pdf",
    "$SPEC_DIR\ts_103983v040000p.pdf"
)

$allFilesExist = $true
foreach ($file in $specFiles) {
    if (-not (Test-Path $file)) {
        Write-TestResult "PRE-002" "Test file exists: $(Split-Path $file -Leaf)" $false "File not found"
        $allFilesExist = $false
    }
}
if ($allFilesExist) {
    Write-TestResult "PRE-002" "All test files exist" $true
}

# Check database exists
$dbExists = Test-Path $DB_PATH
Write-TestResult "PRE-003" "Database file exists" $dbExists $DB_PATH

if (-not $serverRunning) {
    Write-Host "`nERROR: Server is not running. Start server with:" -ForegroundColor Red
    Write-Host "  cd C:\TestRepo\demo-web\backend" -ForegroundColor Yellow
    Write-Host "  python run.py" -ForegroundColor Yellow
    exit 1
}

# Test Suite 1: Phase 3A - Test Extraction Limit
Write-TestHeader "Test Suite 1: Phase 3A - Test Extraction Limit"

# Test 1.1: Check config parameter
try {
    $configContent = Get-Content "C:\TestRepo\demo-web\backend\app\config.py" -Raw
    $hasConfig = $configContent -match "max_tests_per_spec.*=.*2"
    Write-TestResult "3A-001" "Config parameter 'max_tests_per_spec' exists with value 2" $hasConfig
} catch {
    Write-TestResult "3A-001" "Config parameter check" $false $_.Exception.Message
}

# Test 1.2: Auto-generation produces 8 tests
Write-Host "`n  Note: Automated upload and generation requires browser automation." -ForegroundColor Gray
Write-Host "  This test requires manual execution through UI." -ForegroundColor Gray
Write-Host "  Expected: Catalog generation produces exactly 8 tests (2 per spec)" -ForegroundColor Gray

# Test Suite 2: Phase 3B - Database Save Fix
Write-TestHeader "Test Suite 2: Phase 3B - Database Save Fix"

# Test 2.1: Check database structure
try {
    $tableCheck = & python -c @"
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_cases'")
result = cursor.fetchone()
print('exists' if result else 'missing')
conn.close()
"@
    $tableExists = $tableCheck -eq "exists"
    Write-TestResult "3B-001" "Database table 'test_cases' exists" $tableExists
} catch {
    Write-TestResult "3B-001" "Database table check" $false $_.Exception.Message
}

# Test 2.2: Check current database count
try {
    $currentCount = Get-DatabaseTestCount
    Write-TestResult "3B-002" "Database query successful" ($currentCount -ge 0) "Current count: $currentCount"
} catch {
    Write-TestResult "3B-002" "Database query" $false $_.Exception.Message
}

# Test 2.3: Check for duplicate test_ids
try {
    $duplicates = & python -c @"
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()
cursor.execute('SELECT test_id, COUNT(*) as count FROM test_cases GROUP BY test_id HAVING COUNT(*) > 1')
result = cursor.fetchall()
print(len(result))
conn.close()
"@
    $hasDuplicates = [int]$duplicates -gt 0
    Write-TestResult "3B-003" "No duplicate test_ids in database" (-not $hasDuplicates) "Duplicates found: $duplicates"
} catch {
    Write-TestResult "3B-003" "Duplicate test_id check" $false $_.Exception.Message
}

# Test Suite 3: Phase 3C - Section Selection UI
Write-TestHeader "Test Suite 3: Phase 3C - Section Selection UI"

# Test 3.1: Check section selector module exists
$selectorExists = Test-Path "C:\TestRepo\demo-web\frontend\static\js\section_selector.js"
Write-TestResult "3C-001" "Section selector module exists" $selectorExists

# Test 3.2: Check HTML has section selection modal
try {
    $htmlContent = Get-Content "C:\TestRepo\demo-web\frontend\templates\index.html" -Raw
    $hasModal = $htmlContent -match "section-selection-modal"
    Write-TestResult "3C-002" "Section selection modal exists in HTML" $hasModal
} catch {
    Write-TestResult "3C-002" "HTML modal check" $false $_.Exception.Message
}

# Test 3.3: Check API endpoint exists
try {
    $apiContent = Get-Content "C:\TestRepo\demo-web\backend\app\api\oran.py" -Raw
    $hasPreviewEndpoint = $apiContent -match "preview-sections"
    $hasSelectionEndpoint = $apiContent -match "generate-from-selection"
    
    Write-TestResult "3C-003" "Preview sections API endpoint exists" $hasPreviewEndpoint
    Write-TestResult "3C-004" "Generate from selection API endpoint exists" $hasSelectionEndpoint
} catch {
    Write-TestResult "3C-003" "API endpoint check" $false $_.Exception.Message
}

# Test Suite 4: UI Component Validation
Write-TestHeader "Test Suite 4: UI Component Validation"

# Test 4.1: Check MVP notice exists
try {
    $htmlContent = Get-Content "C:\TestRepo\demo-web\frontend\templates\index.html" -Raw
    $hasMvpNotice = $htmlContent -match "mvp-notice"
    Write-TestResult "4-001" "MVP notice exists in HTML" $hasMvpNotice
} catch {
    Write-TestResult "4-001" "MVP notice check" $false $_.Exception.Message
}

# Test 4.2: Check CSS for Phase 3C styles
try {
    $cssContent = Get-Content "C:\TestRepo\demo-web\frontend\static\css\oran.css" -Raw
    $hasSelectionStyles = $cssContent -match "sections-table"
    $hasModalStyles = $cssContent -match "generation-buttons"
    
    Write-TestResult "4-002" "Section selection CSS exists" $hasSelectionStyles
    Write-TestResult "4-003" "Generation buttons CSS exists" $hasModalStyles
} catch {
    Write-TestResult "4-002" "CSS check" $false $_.Exception.Message
}

# Test Suite 5: Backend Logic Validation
Write-TestHeader "Test Suite 5: Backend Logic Validation"

# Test 5.1: Check catalog generator returns tuple
try {
    $serviceContent = Get-Content "C:\TestRepo\demo-web\backend\app\services\catalog_generator_service.py" -Raw
    $returnsTuple = $serviceContent -match "-> Tuple\[OranTestCatalog, List\[EnrichedTestCase\]\]"
    Write-TestResult "5-001" "Catalog generator returns tuple (catalog, deduplicated_cases)" $returnsTuple
} catch {
    Write-TestResult "5-001" "Catalog generator signature check" $false $_.Exception.Message
}

# Test 5.2: Check save_to_database receives deduplicated list
try {
    $oranContent = Get-Content "C:\TestRepo\demo-web\backend\app\api\oran.py" -Raw
    $usesDeduplicated = $oranContent -match "deduplicated_cases.*save_to_database"
    Write-TestResult "5-002" "save_to_database receives deduplicated list" $usesDeduplicated
} catch {
    Write-TestResult "5-002" "Database save logic check" $false $_.Exception.Message
}

# Test 5.3: Check max_tests_per_spec is used
try {
    $parserContent = Get-Content "C:\TestRepo\demo-web\backend\app\services\spec_parser_service.py" -Raw
    $usesLimit = $parserContent -match "max_tests_per_spec"
    Write-TestResult "5-003" "Parser service uses max_tests_per_spec parameter" $usesLimit
} catch {
    Write-TestResult "5-003" "Parser service check" $false $_.Exception.Message
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$duration = (Get-Date) - $script:StartTime
$totalTests = $script:PassCount + $script:FailCount

Write-Host "`nTotal Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $script:PassCount" -ForegroundColor Green
Write-Host "Failed: $script:FailCount" -ForegroundColor Red
Write-Host "Duration: $($duration.TotalSeconds) seconds" -ForegroundColor Gray

# Calculate pass rate
$passRate = if ($totalTests -gt 0) { [math]::Round(($script:PassCount / $totalTests) * 100, 1) } else { 0 }
Write-Host "Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 80) { "Green" } else { "Red" })

# Export results to JSON
$reportPath = "C:\TestRepo\ORAN\tests\test_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$script:TestResults | ConvertTo-Json | Out-File $reportPath -Encoding UTF8
Write-Host "`nTest results exported to: $reportPath" -ForegroundColor Cyan

# Manual Testing Instructions
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Manual Testing Required" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nThe following tests require manual execution through the browser:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Auto-Generation Test (8 tests):" -ForegroundColor White
Write-Host "   - Open http://localhost:8000" -ForegroundColor Gray
Write-Host "   - Upload all 4 PDFs" -ForegroundColor Gray
Write-Host "   - Click 'Generate Test Catalog (Auto)'" -ForegroundColor Gray
Write-Host "   - Verify: Catalog shows 8 tests" -ForegroundColor Gray
Write-Host "   - Verify: Database has 8 rows" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Preview & Select Sections Test:" -ForegroundColor White
Write-Host "   - Click 'Preview & Select Sections'" -ForegroundColor Gray
Write-Host "   - Verify: Modal shows ~646 total sections" -ForegroundColor Gray
Write-Host "   - Click 'Select MVP (2 per spec)'" -ForegroundColor Gray
Write-Host "   - Verify: 8 sections selected" -ForegroundColor Gray
Write-Host "   - Click 'Generate Catalog (8 sections)'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Custom Selection Test:" -ForegroundColor White
Write-Host "   - Open section selection modal" -ForegroundColor Gray
Write-Host "   - Manually select 5 different sections" -ForegroundColor Gray
Write-Host "   - Generate catalog" -ForegroundColor Gray
Write-Host "   - Verify: Catalog has exactly 5 tests" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Manage Tests Tab:" -ForegroundColor White
Write-Host "   - Navigate to 'Manage Tests' tab" -ForegroundColor Gray
Write-Host "   - Verify: Tests from catalog are displayed" -ForegroundColor Gray
Write-Host "   - Test filters, edit, delete functions" -ForegroundColor Gray
Write-Host ""

if ($script:FailCount -eq 0) {
    Write-Host "`n✓ All automated tests passed!" -ForegroundColor Green
    Write-Host "  Please complete manual tests to verify full functionality." -ForegroundColor White
    exit 0
} else {
    Write-Host "`n✗ Some automated tests failed." -ForegroundColor Red
    Write-Host "  Please review failures before proceeding to manual tests." -ForegroundColor White
    exit 1
}
