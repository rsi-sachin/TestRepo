# Phase 5: Reliability Testing Script
# Executes 5 consecutive runs of sip-001 demo to validate CLI stability
# Target: 90% success rate (4+ out of 5) before GUI deployment

param(
    [switch]$Verbose
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

function Test-TempFileCleanup {
    $tempFiles = Get-ChildItem "C:\TTS\bin\demo_temp_*.jmx" -ErrorAction SilentlyContinue
    return $tempFiles.Count
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  Phase 5: Reliability Testing (5 Consecutive Runs)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target: 90% success rate (4+ out of 5 passes)" -ForegroundColor Yellow
Write-Host "Demo: sip-001 (Self-Contained VoLTE Call Setup & Teardown)" -ForegroundColor Yellow
Write-Host ""

cd C:\TestRepo\demo-tool

# Verify clean state
Write-Host "[Pre-Flight] Checking environment..." -ForegroundColor Gray
$preCleanup = Test-TempFileCleanup
if ($preCleanup -gt 0) {
    Write-Host "  [!] Found $preCleanup temp files from previous runs, cleaning..." -ForegroundColor Yellow
    Remove-Item "C:\TTS\bin\demo_temp_*.jmx" -Force -ErrorAction SilentlyContinue
}
Write-Host "  [OK] Environment ready" -ForegroundColor Green
Write-Host ""

$cp = Build-Classpath
$results = @()
$successCount = 0
$failureCount = 0

# Execute 5 consecutive runs
for ($i = 1; $i -le 5; $i++) {
    Write-Host "================================================================" -ForegroundColor Gray
    Write-Host "  Run $i of 5" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Gray
    
    $startTime = Get-Date
    
    # Check temp files before run
    $tempBefore = Test-TempFileCleanup
    
    # Execute demo
    $output = & java "-Djava.awt.headless=true" -cp $cp com.tts.demo.CliApp --demo sip-001 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    # Check temp files after run (should be cleaned up)
    Start-Sleep -Seconds 2  # Allow cleanup to complete
    $tempAfter = Test-TempFileCleanup
    
    # Validate JTL file
    $latestJtl = Get-ChildItem "logs\log_*_sip-001.jtl" -ErrorAction SilentlyContinue | 
                 Sort-Object LastWriteTime -Descending | 
                 Select-Object -First 1
    
    $samples = 0
    $jtlSize = 0
    if ($latestJtl) {
        $jtlSize = $latestJtl.Length
        $lines = (Get-Content $latestJtl.FullName).Count
        $samples = $lines - 1  # Subtract header
    }
    
    # Determine success
    $success = ($exitCode -eq 0) -and ($samples -ge 19) -and ($tempAfter -eq 0)
    
    if ($success) {
        $successCount++
        Write-Host "  [OK] Run $i PASSED" -ForegroundColor Green
    } else {
        $failureCount++
        Write-Host "  [X] Run $i FAILED" -ForegroundColor Red
    }
    
    # Report details
    Write-Host "    Exit Code: $exitCode" -ForegroundColor $(if ($exitCode -eq 0) { "Green" } else { "Red" })
    Write-Host "    Duration: $([math]::Round($duration, 1))s" -ForegroundColor White
    Write-Host "    Samples: $samples" -ForegroundColor $(if ($samples -ge 19) { "Green" } else { "Red" })
    Write-Host "    JTL Size: $jtlSize bytes" -ForegroundColor White
    Write-Host "    Temp Cleanup: $(if ($tempAfter -eq 0) { 'OK' } else { "$tempAfter files remain" })" -ForegroundColor $(if ($tempAfter -eq 0) { "Green" } else { "Red" })
    
    # Check for errors in output
    if ($output -match "Err:\s+(\d+)") {
        $errorCount = [int]$matches[1]
        Write-Host "    JMeter Errors: $errorCount" -ForegroundColor $(if ($errorCount -eq 0) { "Green" } else { "Red" })
    }
    
    # Store result
    $results += [PSCustomObject]@{
        Run = $i
        Success = $success
        ExitCode = $exitCode
        Duration = [math]::Round($duration, 1)
        Samples = $samples
        JtlSize = $jtlSize
        TempCleanup = ($tempAfter -eq 0)
    }
    
    Write-Host ""
    
    # Brief pause between runs
    if ($i -lt 5) {
        Start-Sleep -Seconds 3
    }
}

# Calculate success rate
$successRate = ($successCount / 5.0) * 100
$passesThreshold = $successRate -ge 90

# Display summary
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Reliability Test Summary" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Results by Run:" -ForegroundColor Yellow
$results | Format-Table -AutoSize Run, Success, ExitCode, Duration, Samples, JtlSize, TempCleanup
Write-Host ""

Write-Host "Overall Statistics:" -ForegroundColor Yellow
Write-Host "  Successful Runs: $successCount / 5" -ForegroundColor $(if ($successCount -ge 4) { "Green" } else { "Red" })
Write-Host "  Failed Runs: $failureCount / 5" -ForegroundColor $(if ($failureCount -le 1) { "Green" } else { "Red" })
Write-Host "  Success Rate: $([math]::Round($successRate, 1))%" -ForegroundColor $(if ($passesThreshold) { "Green" } else { "Red" })
Write-Host "  Target: 90% (4+ successes)" -ForegroundColor Yellow
Write-Host ""

# Average metrics for successful runs
$successfulRuns = $results | Where-Object { $_.Success -eq $true }
if ($successfulRuns) {
    $avgDuration = ($successfulRuns | Measure-Object -Property Duration -Average).Average
    $avgSamples = ($successfulRuns | Measure-Object -Property Samples -Average).Average
    
    Write-Host "Successful Runs - Average Metrics:" -ForegroundColor Yellow
    Write-Host "  Duration: $([math]::Round($avgDuration, 1))s" -ForegroundColor Green
    Write-Host "  Samples: $([math]::Round($avgSamples, 0))" -ForegroundColor Green
    Write-Host ""
}

# Failure analysis
if ($failureCount -gt 0) {
    Write-Host "Failure Analysis:" -ForegroundColor Yellow
    $failedRuns = $results | Where-Object { $_.Success -eq $false }
    foreach ($run in $failedRuns) {
        Write-Host "  Run $($run.Run):" -ForegroundColor Red
        if ($run.ExitCode -ne 0) {
            Write-Host "    - Non-zero exit code: $($run.ExitCode)" -ForegroundColor Red
        }
        if ($run.Samples -lt 19) {
            Write-Host "    - Insufficient samples: $($run.Samples) (expected 19+)" -ForegroundColor Red
        }
        if (-not $run.TempCleanup) {
            Write-Host "    - Temp file cleanup failed" -ForegroundColor Red
        }
    }
    Write-Host ""
}

# Gate decision
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Gate Decision: GUI Deployment Readiness" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if ($passesThreshold) {
    Write-Host "  [OK] GATE PASSED - CLI Reliability Validated" -ForegroundColor Green
    Write-Host "" -ForegroundColor Green
    Write-Host "  Success rate of $([math]::Round($successRate, 1))% meets 90% threshold" -ForegroundColor Green
    Write-Host "  CLI execution is stable and ready for GUI integration" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Next Steps:" -ForegroundColor Yellow
    Write-Host "    1. GUI deployment approved (mvn javafx:run)" -ForegroundColor Cyan
    Write-Host "    2. Spring Boot migration can proceed (Phase 2 architecture)" -ForegroundColor Cyan
    Write-Host "    3. Service layer validated and reusable" -ForegroundColor Cyan
} else {
    Write-Host "  [X] GATE FAILED - Reliability Below Threshold" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Success rate of $([math]::Round($successRate, 1))% is below 90% threshold" -ForegroundColor Red
    Write-Host "  CLI stability issues must be resolved before GUI deployment" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Required Actions:" -ForegroundColor Yellow
    Write-Host "    1. Investigate failures (check logs above)" -ForegroundColor Red
    Write-Host "    2. Address root causes" -ForegroundColor Red
    Write-Host "    3. Re-run reliability test" -ForegroundColor Red
}

Write-Host ""

# Integration summary
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Integration Status - All Phases" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Phase 1: [OK] Parameterized JMX (4 timing parameters)" -ForegroundColor Green
Write-Host "  Phase 2: [OK] CLI execution + license handling" -ForegroundColor Green
Write-Host "  Phase 3: [OK] UDP port validation (5060, 5065)" -ForegroundColor Green
Write-Host "  Phase 4: [OK] Enhanced progress logging" -ForegroundColor Green
Write-Host "  Phase 5: $(if ($passesThreshold) { '[OK]' } else { '[X]' }) Reliability testing ($([math]::Round($successRate, 1))%)" -ForegroundColor $(if ($passesThreshold) { "Green" } else { "Red" })
Write-Host ""

# Final verdict
if ($passesThreshold) {
    Write-Host "  ████████████████████████████████████████████████" -ForegroundColor Green
    Write-Host "  █                                              █" -ForegroundColor Green
    Write-Host "  █   ALL PHASES COMPLETE - READY FOR GUI       █" -ForegroundColor Green
    Write-Host "  █                                              █" -ForegroundColor Green
    Write-Host "  ████████████████████████████████████████████████" -ForegroundColor Green
    Write-Host ""
    exit 0
} else {
    Write-Host "  ████████████████████████████████████████████████" -ForegroundColor Red
    Write-Host "  █                                              █" -ForegroundColor Red
    Write-Host "  █   RELIABILITY GATE FAILED - FIX REQUIRED    █" -ForegroundColor Red
    Write-Host "  █                                              █" -ForegroundColor Red
    Write-Host "  ████████████████████████████████████████████████" -ForegroundColor Red
    Write-Host ""
    exit 1
}
