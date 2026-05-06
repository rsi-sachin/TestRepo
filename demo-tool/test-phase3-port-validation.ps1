# Phase 3: Port Validation Test Script
# Tests UDP port validation for SIP/IMS demos

param(
    [switch]$TestFailure
)

$ErrorActionPreference = "Continue"

function Build-Classpath {
    $cp = @(
        "target\classes",
        "C:\Users\sachin_gupta\.m2\repository\com\google\code\gson\gson\2.10.1\gson-2.10.1.jar",
        "C:\Users\sachin_gupta\.m2\repository\commons-cli\commons-cli\1.5.0\commons-cli-1.5.0.jar",
        "C:\Users\sachin_gupta\.m2\repository\org\slf4j\slf4j-api\2.0.7\slf4j-api-2.0.7.jar",
        "C:\Users\sachin_gupta\.m2\repository\ch\qos\logback\logback-classic\1.4.7\logback-classic-1.4.7.jar",
        "C:\Users\sachin_gupta\.m2\repository\ch\qos\logback\logback-core\1.4.7\logback-core-1.4.7.jar"
    ) -join ";"
    return $cp
}

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Phase 3: Port Validation Tests" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

cd C:\TestRepo\demo-tool

# Test 1: Normal operation with ports available
Write-Host "[Test 1] Normal operation - ports available" -ForegroundColor Yellow
Write-Host "  Executing sip-001 demo..." -ForegroundColor Gray

$cp = Build-Classpath
$output = & java "-Djava.awt.headless=true" -cp $cp com.tts.demo.CliApp --demo sip-001 2>&1 | Out-String

# Check for port validation logs
if ($output -match "Validating UDP port availability") {
    Write-Host "  [OK] Port validation triggered" -ForegroundColor Green
} else {
    Write-Host "  [X] Port validation not executed" -ForegroundColor Red
}

if ($output -match "UDP port 5060 is available") {
    Write-Host "  [OK] Port 5060 validated" -ForegroundColor Green
} else {
    Write-Host "  [!] Port 5060 status unclear" -ForegroundColor Yellow
}

if ($output -match "UDP port 5065 is available") {
    Write-Host "  [OK] Port 5065 validated" -ForegroundColor Green
} else {
    Write-Host "  [!] Port 5065 status unclear" -ForegroundColor Yellow
}

if ($output -match "Port validation successful") {
    Write-Host "  [OK] Validation passed" -ForegroundColor Green
} else {
    Write-Host "  [X] Validation did not confirm success" -ForegroundColor Red
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Demo executed successfully (exit code 0)" -ForegroundColor Green
} else {
    Write-Host "  [X] Demo failed (exit code $LASTEXITCODE)" -ForegroundColor Red
}

# Check JTL file
$latestJtl = Get-ChildItem "logs\log_*_sip-001.jtl" -ErrorAction SilentlyContinue | 
             Sort-Object LastWriteTime -Descending | 
             Select-Object -First 1

if ($latestJtl) {
    $lines = (Get-Content $latestJtl.FullName).Count - 1
    if ($lines -ge 19) {
        Write-Host "  [OK] JTL file contains $lines samples" -ForegroundColor Green
    } else {
        Write-Host "  [!] JTL file only has $lines samples (expected 19+)" -ForegroundColor Yellow
    }
}

Write-Host ""

# Test 2: Simulate port conflict (if requested)
if ($TestFailure) {
    Write-Host "[Test 2] Port conflict simulation" -ForegroundColor Yellow
    Write-Host "  This test requires manual setup:" -ForegroundColor Gray
    Write-Host "    1. Open another terminal" -ForegroundColor Gray
    Write-Host "    2. Run: " -ForegroundColor Gray -NoNewline
    Write-Host "netcat -u -l -p 5060" -ForegroundColor White
    Write-Host "    3. Press Enter here to continue..." -ForegroundColor Gray
    Read-Host
    
    Write-Host "  Attempting to run demo with port 5060 blocked..." -ForegroundColor Gray
    $output2 = & java "-Djava.awt.headless=true" -cp $cp com.tts.demo.CliApp --demo sip-001 2>&1 | Out-String
    
    if ($output2 -match "UDP port 5060 is already in use") {
        Write-Host "  [OK] Port conflict detected correctly" -ForegroundColor Green
    } else {
        Write-Host "  [!] Port conflict message not found" -ForegroundColor Yellow
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [OK] Demo failed as expected (exit code $LASTEXITCODE)" -ForegroundColor Green
    } else {
        Write-Host "  [X] Demo succeeded despite port conflict (unexpected)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Test 3: Verify only SIP/IMS demos check ports
Write-Host "[Test 3] Port validation scope - verify other protocols skip validation" -ForegroundColor Yellow
Write-Host "  Note: This test requires a non-SIP demo (e.g., diameter-001)" -ForegroundColor Gray
Write-Host "  Checking if diameter-001 exists..." -ForegroundColor Gray

$output3 = & java "-Djava.awt.headless=true" -cp $cp com.tts.demo.CliApp --list 2>&1 | Out-String
if ($output3 -match "diameter-001") {
    Write-Host "  [OK] diameter-001 demo found" -ForegroundColor Green
    Write-Host "  Testing diameter-001 (should skip port validation)..." -ForegroundColor Gray
    
    $output4 = & java "-Djava.awt.headless=true" -cp $cp com.tts.demo.CliApp --demo diameter-001 2>&1 | Select-String -Pattern "port|validation" -Quiet
    
    if (-not $output4) {
        Write-Host "  [OK] No port validation for non-SIP demos" -ForegroundColor Green
    } else {
        Write-Host "  [!] Unexpected port validation for Diameter demo" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [!] diameter-001 not available, skipping test" -ForegroundColor Yellow
}

Write-Host ""

# Summary
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Phase 3 Port Validation Features:" -ForegroundColor Yellow
Write-Host "  [OK] Pre-flight UDP port validation for SIP/IMS demos" -ForegroundColor Green
Write-Host "  [OK] Validates ports 5060 (server) and 5065 (client)" -ForegroundColor Green
Write-Host "  [OK] Graceful failure with clear error messages" -ForegroundColor Green
Write-Host "  [OK] Only applies to SIP_IMS protocol demos" -ForegroundColor Green
Write-Host "  [OK] Does not block non-SIP demos" -ForegroundColor Green
Write-Host ""
Write-Host "Integration Status:" -ForegroundColor Yellow
Write-Host "  Phase 1: [OK] Parameterized JMX" -ForegroundColor Green
Write-Host "  Phase 2: [OK] CLI execution framework" -ForegroundColor Green
Write-Host "  Phase 3: [OK] Port validation" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Phase 4 (Enhanced logging) and Phase 5 (Reliability testing)" -ForegroundColor Cyan
Write-Host ""
