#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Git pre-commit hook for TTS Demo Tool
    
.DESCRIPTION
    Automatically runs cleanup checks before each commit.
    This script is called by git before a commit is made.
    
    To install this hook:
    1. Initialize git: git init
    2. Copy this file to .git/hooks/pre-commit (remove .ps1 extension)
    3. Make it executable: chmod +x .git/hooks/pre-commit (Unix/Mac)
    
    Or run: .\install-git-hooks.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "`n[INFO] Pre-commit checks..." -ForegroundColor Cyan

# Get script directory (repository root)
$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    $repoRoot = Split-Path -Parent $PSScriptRoot
}

# Run cleanup script in dry-run mode to check for issues
$cleanupScript = Join-Path $repoRoot "cleanup-before-commit.ps1"

if (Test-Path $cleanupScript) {
    Write-Host "Running cleanup checks..." -ForegroundColor Gray
    
    # Run in dry-run mode
    & $cleanupScript -DryRun -Auto | Out-Null
    
    # Check for problematic files that shouldn't be committed
    $issues = @()
    
    # Check for logs in staged files
    $stagedFiles = git diff --cached --name-only
    
    foreach ($file in $stagedFiles) {
        # Check for log files
        if ($file -match '\.(log|jtl)$' -and $file -notlike '*baseline*') {
            $issues += "[WARN] Log/result file staged: $file"
        }
        
        # Check for temporary files
        if ($file -match '\.(tmp|temp|bak)$') {
            $issues += "[WARN] Temporary file staged: $file"
        }
        
        # Check for target directory files
        if ($file -match '^demo-tool/target/') {
            $issues += "[WARN] Build artifact staged: $file"
        }
    }
    
    if ($issues.Count -gt 0) {
        Write-Host "`n[ERROR] Pre-commit check failed!" -ForegroundColor Red
        Write-Host "`nThe following issues were found:" -ForegroundColor Yellow
        foreach ($issue in $issues) {
            Write-Host "  $issue" -ForegroundColor Yellow
        }
        Write-Host "`nRecommendations:" -ForegroundColor Cyan
        Write-Host "  1. Run: .\cleanup-before-commit.ps1" -ForegroundColor White
        Write-Host "  2. Unstage unwanted files: git reset HEAD <file>" -ForegroundColor White
        Write-Host "  3. Or force commit: git commit --no-verify" -ForegroundColor Gray
        Write-Host ""
        exit 1
    }
    
    Write-Host "[OK] Pre-commit checks passed" -ForegroundColor Green
} else {
    Write-Host "[WARN] Cleanup script not found, skipping checks" -ForegroundColor Yellow
}

Write-Host ""
exit 0
