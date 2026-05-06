# Phase 1+2 Integration Test Suite
# Validates end-to-end parameter flow from CLI ??? DemoConfig ??? JMeter ??? JMX execution

param(
    [switch]$Verbose,
    [switch]$StopOnFailure
)

$ErrorActionPreference = "Continue"
$script:TestResults = @()
$script:PassCount = 0
$script:FailCount = 0

# Build classpath for CliApp execution
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

# Execute CliApp with parameters
function Invoke-CliApp {
    param([string]$Args)
    
    $cp = Build-Classpath
    $output = & java "-Djava.awt.headless=true" -cp $cp com.tts.demo.CliApp $Args.Split(" ") 2>&1 | Out-String
    
    return @{
        ExitCode = $LASTEXITCODE
        Output = $output
    }
}

# Validate test result
function Test-Result {
    param(
        [string]$TestId,
        [string]$Description,
        [hashtable]$Actual,
        [int]$ExpectedExitCode = 0,
        [int]$ExpectedMinSamples = 0,
        [int]$ExpectedMaxSamples = 999,
        [int]$ExpectedMinDuration = 0,
        [int]$ExpectedMaxDuration = 999,
        [switch]$CheckTempCleanup
    )
    
    $passed = $true
    $issues = @()
    
    # Check exit code
    if ($Actual.ExitCode -ne $ExpectedExitCode) {
        $passed = $false
        $issues += "Exit code mismatch: expected $ExpectedExitCode, got $($Actual.ExitCode)"
    }
    
    # Extract metrics from output
    if ($Actual.Output -match "Duration:\s+(\d+)\s+seconds") {
        $duration = [int]$matches[1]
        if ($duration -lt $ExpectedMinDuration -or $duration -gt $ExpectedMaxDuration) {
            $passed = $false
            $issues += "Duration out of range: expected $ExpectedMinDuration-${ExpectedMaxDuration}s, got ${duration}s"
        }
    } else {
        $duration = -1
    }
    
    # Check JTL file
    $latestJtl = Get-ChildItem "logs\log_*_sip-001.jtl" -ErrorAction SilentlyContinue | 
                 Sort-Object LastWriteTime -Descending | 
                 Select-Object -First 1
    
    $samples = 0
    if ($latestJtl) {
        $lines = Get-Content $latestJtl.FullName
        $samples = $lines.Count - 1  # Subtract header
        
        if ($samples -lt $ExpectedMinSamples -or $samples -gt $ExpectedMaxSamples) {
            $passed = $false
            $issues += "Sample count out of range: expected $ExpectedMinSamples-$ExpectedMaxSamples, got $samples"
        }
    } else {
        if ($ExpectedMinSamples -gt 0) {
            $passed = $false
            $issues += "No JTL file found"
        }
    }
    
    # Check temp file cleanup
    if ($CheckTempCleanup) {
        Start-Sleep -Seconds 2  # Allow cleanup to complete
        $tempFiles = Get-ChildItem "C:\TTS\bin\demo_temp_*.jmx" -ErrorAction SilentlyContinue
        if ($tempFiles) {
            $passed = $false
            $issues += "Temp files not cleaned up: $($tempFiles.Count) files remain"
        }
    }
    
    # Record result
    $result = [PSCustomObject]@{
        TestId = $TestId
        Description = $Description
        Status = if ($passed) { "PASS" } else { "FAIL" }
        ExitCode = $Actual.ExitCode
        Duration = $duration
        Samples = $samples
        Issues = $issues -join "; "
    }
    
    $script:TestResults += $result
    
    if ($passed) {
        $script:PassCount++
        Write-Host "??? $TestId PASSED" -ForegroundColor Green
    } else {
        $script:FailCount++
        Write-Host "??? $TestId FAILED: $($issues -join ', ')" -ForegroundColor Red
        if ($StopOnFailure) {
            throw "Test failed, stopping execution"
        }
    }
    
    if ($Verbose -and $Actual.Output) {
        Write-Host "  Output excerpt:" -ForegroundColor Gray
        $Actual.Output -split "`n" | Select-Object -First 20 | ForEach-Object {
            Write-Host "    $_" -ForegroundColor DarkGray
        }
    }
    
    return $passed
}

# Main test execution
Write-Host "`n????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????" -ForegroundColor Cyan
Write-Host "???     Phase 1+2 Integration Test Suite                   ???" -ForegroundColor Cyan
Write-Host "????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????" -ForegroundColor Cyan

# Pre-test setup
Write-Host "`n[SETUP] Preparing test environment..." -ForegroundColor Yellow

# Clean temp files
$tempFiles = Get-ChildItem "C:\TTS\bin\demo_temp_*.jmx" -ErrorAction SilentlyContinue
if ($tempFiles) {
    Write-Host "  Cleaning $($tempFiles.Count) temp files from C:\TTS\bin" -ForegroundColor Gray
    $tempFiles | Remove-Item -Force
}

# Ensure project is compiled
Write-Host "  Verifying compilation..." -ForegroundColor Gray
cd C:\TestRepo\demo-tool
mvn compile -q 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "??? Compilation failed" -ForegroundColor Red
    exit 1
}
Write-Host "  ??? Environment ready" -ForegroundColor Green

Start-Sleep -Seconds 2

# Test T1: Baseline with defaults
Write-Host "`n[T1] Baseline Test - Default Parameters" -ForegroundColor Cyan
$result = Invoke-CliApp "--demo sip-001"
Test-Result -TestId "T1" `
            -Description "Baseline with demos.json defaults" `
            -Actual $result `
            -ExpectedExitCode 0 `
            -ExpectedMinSamples 18 `
            -ExpectedMaxSamples 20 `
            -ExpectedMinDuration 25 `
            -ExpectedMaxDuration 35 `
            -CheckTempCleanup

Start-Sleep -Seconds 3

# Test T2: Single parameter override
Write-Host "`n[T2] Single Parameter Override - client_delay" -ForegroundColor Cyan
$result = Invoke-CliApp "--demo sip-001 --param client_delay=15000"
Test-Result -TestId "T2" `
            -Description "Override client_delay to 15s" `
            -Actual $result `
            -ExpectedExitCode 0 `
            -ExpectedMinSamples 18 `
            -ExpectedMaxSamples 20 `
            -ExpectedMinDuration 30 `
            -ExpectedMaxDuration 40 `
            -CheckTempCleanup

# Verify parameter in output
if ($result.Output -match "-Jclient_delay=15000") {
    Write-Host "  ??? Parameter override detected in command" -ForegroundColor Green
} else {
    Write-Host "  ??? Parameter override not visible in output" -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

# Test T3: Multiple parameter overrides
Write-Host "`n[T3] Multiple Parameter Overrides" -ForegroundColor Cyan
$result = Invoke-CliApp "--demo sip-001 --param server_rampup=10 --param client_rampup=10 --param client_delay=20000"
Test-Result -TestId "T3" `
            -Description "Override ramp times and delay" `
            -Actual $result `
            -ExpectedExitCode 0 `
            -ExpectedMinSamples 18 `
            -ExpectedMaxSamples 20 `
            -ExpectedMinDuration 37 `
            -ExpectedMaxDuration 47 `
            -CheckTempCleanup

Start-Sleep -Seconds 3

# Test T4: Timeout parameter
Write-Host "`n[T4] Timeout Parameter Override" -ForegroundColor Cyan
$result = Invoke-CliApp "--demo sip-001 --param listen_timeout=60000"
Test-Result -TestId "T4" `
            -Description "Double listen_timeout to 60s" `
            -Actual $result `
            -ExpectedExitCode 0 `
            -ExpectedMinSamples 18 `
            -ExpectedMaxSamples 20 `
            -ExpectedMinDuration 25 `
            -ExpectedMaxDuration 35 `
            -CheckTempCleanup

Start-Sleep -Seconds 3

# Test T5: Stress test with minimal timing
Write-Host "`n[T5] Stress Test - Minimal Timing" -ForegroundColor Cyan
Write-Host "  (May fail due to race conditions - testing error handling)" -ForegroundColor Yellow
$result = Invoke-CliApp "--demo sip-001 --param server_rampup=1 --param client_rampup=1 --param client_delay=5000"
# Allow failure for this test
Test-Result -TestId "T5" `
            -Description "Minimal timing stress test" `
            -Actual $result `
            -ExpectedExitCode 0 `
            -ExpectedMinSamples 0 `
            -ExpectedMaxSamples 20 `
            -ExpectedMinDuration 0 `
            -ExpectedMaxDuration 30 `
            -CheckTempCleanup

Start-Sleep -Seconds 3

# Test T6: Consecutive runs (file lifecycle)
Write-Host "`n[T6] Consecutive Runs - File Lifecycle" -ForegroundColor Cyan
$run1 = Invoke-CliApp "--demo sip-001"
Start-Sleep -Seconds 2
$run2 = Invoke-CliApp "--demo sip-001"
Start-Sleep -Seconds 2
$run3 = Invoke-CliApp "--demo sip-001"

$allPassed = ($run1.ExitCode -eq 0) -and ($run2.ExitCode -eq 0) -and ($run3.ExitCode -eq 0)
$tempFiles = Get-ChildItem "C:\TTS\bin\demo_temp_*.jmx" -ErrorAction SilentlyContinue

Test-Result -TestId "T6" `
            -Description "Three consecutive runs" `
            -Actual @{ ExitCode = if ($allPassed) { 0 } else { 1 }; Output = "3 runs completed" } `
            -ExpectedExitCode 0 `
            -CheckTempCleanup

if ($tempFiles) {
    Write-Host "  ??? Found $($tempFiles.Count) leftover temp files" -ForegroundColor Red
} else {
    Write-Host "  ??? All temp files cleaned up" -ForegroundColor Green
}

Start-Sleep -Seconds 3

# Test T7: Run history persistence
Write-Host "`n[T7] Run History Persistence" -ForegroundColor Cyan
$result = Invoke-CliApp "--demo sip-001"
Start-Sleep -Seconds 2

$latestRun = Get-ChildItem "runs\run_*_sip-001.json" -ErrorAction SilentlyContinue | 
             Sort-Object LastWriteTime -Descending | 
             Select-Object -First 1

$historyValid = $false
if ($latestRun) {
    try {
        $runData = Get-Content $latestRun.FullName | ConvertFrom-Json
        $historyValid = ($runData.runId -and $runData.demoId -eq "sip-001" -and $runData.exitCode -ne $null)
        
        if ($historyValid) {
            Write-Host "  ??? Valid run history JSON:" -ForegroundColor Green
            Write-Host "    runId: $($runData.runId)" -ForegroundColor Gray
            Write-Host "    exitCode: $($runData.exitCode)" -ForegroundColor Gray
            Write-Host "    duration: $($runData.durationSeconds)s" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ??? Invalid JSON structure" -ForegroundColor Red
    }
} else {
    Write-Host "  ??? No run history file found" -ForegroundColor Red
}

Test-Result -TestId "T7" `
            -Description "Run history JSON validation" `
            -Actual @{ ExitCode = if ($historyValid) { 0 } else { 1 }; Output = "History check" } `
            -ExpectedExitCode 0

Start-Sleep -Seconds 3

# Test T8: Invalid parameter handling
Write-Host "`n[T8] Invalid Parameter Handling" -ForegroundColor Cyan
$result = Invoke-CliApp "--demo sip-001 --param invalid_param=999"
Test-Result -TestId "T8" `
            -Description "Graceful handling of unknown params" `
            -Actual $result `
            -ExpectedExitCode 0 `
            -ExpectedMinSamples 18 `
            -ExpectedMaxSamples 20 `
            -ExpectedMinDuration 25 `
            -ExpectedMaxDuration 35 `
            -CheckTempCleanup

# Generate summary report
Write-Host "`n????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????" -ForegroundColor Cyan
Write-Host "???                    Test Summary                         ???" -ForegroundColor Cyan
Write-Host "????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????" -ForegroundColor Cyan

Write-Host "`nResults:" -ForegroundColor Yellow
$script:TestResults | Format-Table -AutoSize TestId, Status, ExitCode, Duration, Samples, Issues

Write-Host "`nOverall:" -ForegroundColor Yellow
Write-Host "  Passed: $script:PassCount / $($script:TestResults.Count)" -ForegroundColor $(if ($script:PassCount -eq $script:TestResults.Count) { "Green" } else { "Yellow" })
Write-Host "  Failed: $script:FailCount / $($script:TestResults.Count)" -ForegroundColor $(if ($script:FailCount -eq 0) { "Green" } else { "Red" })

if ($script:FailCount -eq 0) {
    Write-Host "`n????????? ALL TESTS PASSED ?????????" -ForegroundColor Green
    Write-Host "Phase 1+2 integration validated successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n??? SOME TESTS FAILED ???" -ForegroundColor Red
    Write-Host "Review failures above for details" -ForegroundColor Yellow
    exit 1
}

