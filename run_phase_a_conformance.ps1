#!/usr/bin/env pwsh
<#
Phase A Conformance Suite Execution Script (PowerShell)

Runs all Non-RT RIC + A1 conformance suites with evidence capture.

Usage:
    .\run_phase_a_conformance.ps1 [-TwinProfile "a1_minimal_twin_v1"] [-OutputDir "ORAN/docs/coverage/evidence"]
#>

param(
    [string]$TwinProfile = "a1_minimal_twin_v1",
    [string]$OutputDir = "ORAN/docs/coverage/evidence"
)

# Import modules
$ErrorActionPreference = "Continue"

# Setup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$runId = "phase_a_$timestamp"
$runDir = Join-Path (Resolve-Path $OutputDir) $runId
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$testSuites = @(
    @{ Name = "TS_103_989_4_2_1"; File = "demo-web/backend/tests/conformance/test_a1_policy_conformance_4_2_1.py" },
    @{ Name = "TS_103_989_4_2_2"; File = "demo-web/backend/tests/conformance/test_a1_policy_conformance_4_2_2.py" },
    @{ Name = "TS_103_989_7"; File = "demo-web/backend/tests/conformance/test_interoperability_clause7_suites.py" },
    @{ Name = "TS_103_987_API"; File = "demo-web/backend/tests/conformance/test_simulator_capabilities.py" },
    @{ Name = "TS_103_988_5"; File = "demo-web/backend/tests/conformance/test_ts103988_section5_common_types.py" },
    @{ Name = "Non_RT_RIC_DUT"; File = "demo-web/backend/tests/conformance/test_non_rt_ric_dut_readiness.py" },
    @{ Name = "TS_103_983_4_5"; File = "demo-web/backend/tests/conformance/test_ts103983_section4_principles.py" },
    @{ Name = "EI_Job_Ops"; File = "demo-web/backend/tests/conformance/test_ei_job_operations.py" },
    @{ Name = "Exec_Evidence"; File = "demo-web/backend/tests/conformance/test_execution_evidence.py" }
)

$summary = @{
    runId = $runId
    timestamp = (Get-Date -AsUTC).ToUniversalTime().ToString("o")
    twinProfile = $TwinProfile
    suitesExecuted = 0
    suitesPassed = 0
    suitesFailed = 0
    suites = @()
}

Write-Host ""
Write-Host "================================================================================"
Write-Host "PHASE A CONFORMANCE SUITE EXECUTION"
Write-Host "================================================================================"
Write-Host "Run ID:       $runId"
Write-Host "Twin Profile: $TwinProfile"
Write-Host "Output Dir:   $runDir"
Write-Host ""

foreach ($suite in $testSuites) {
    $suiteName = $suite.Name
    $testFile = $suite.File
    
    Write-Host -NoNewline "Running $suiteName... "
    
    $junitFile = Join-Path $runDir "$suiteName`_junit.xml"
    $reportFile = Join-Path $runDir "$suiteName`_report.json"
    
    # Run pytest
    & .venv\Scripts\python -m pytest $testFile `
        -v `
        --tb=short `
        --json-report `
        --json-report-file=$reportFile `
        --junit-xml=$junitFile `
        2>&1 | Out-Null
    
    $exitCode = $LASTEXITCODE
    $success = ($exitCode -eq 0)
    
    if ($success) {
        Write-Host "✅ PASSED"
        $summary.suitesPassed += 1
    } else {
        Write-Host "❌ FAILED"
        $summary.suitesFailed += 1
    }
    
    $summary.suitesExecuted += 1
    $summary.suites += @{
        suiteName = $suiteName
        testFile = $testFile
        verdict = if ($success) { "PASS" } else { "FAIL" }
        exitCode = $exitCode
        junitFile = (Resolve-Path -Relative $junitFile)
        reportFile = (Resolve-Path -Relative $reportFile)
    }
}

# Save summary
$summaryFile = Join-Path $runDir "execution_summary.json"
$summary | ConvertTo-Json -Depth 10 | Set-Content $summaryFile

Write-Host ""
Write-Host "================================================================================"
Write-Host "SUMMARY"
Write-Host "================================================================================"
Write-Host "Suites Executed: $($summary.suitesExecuted)"
Write-Host "Suites Passed:   $($summary.suitesPassed)"
Write-Host "Suites Failed:   $($summary.suitesFailed)"
Write-Host ""
Write-Host "Artifacts: $runDir"
Write-Host "Summary:   $summaryFile"
Write-Host "================================================================================"
Write-Host ""

exit 0
