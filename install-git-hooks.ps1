#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Install git hooks for TTS Demo Tool
    
.DESCRIPTION
    Sets up pre-commit hooks to automatically check for temporary files
    and other issues before each commit.
    
.EXAMPLE
    .\install-git-hooks.ps1
    Installs the pre-commit hook
#>

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n=============================================================" -ForegroundColor Cyan
Write-Host "           Git Hooks Installation - TTS Demo Tool        " -ForegroundColor Cyan
Write-Host "=============================================================`n" -ForegroundColor Cyan

# Check if git is initialized
$gitDir = Join-Path $scriptRoot ".git"
if (-not (Test-Path $gitDir)) {
    Write-Host "[ERROR] Git repository not initialized" -ForegroundColor Red
    Write-Host "`nInitializing git repository..." -ForegroundColor Yellow
    
    Push-Location $scriptRoot
    git init
    Pop-Location
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to initialize git repository" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[OK] Git repository initialized" -ForegroundColor Green
}

# Create hooks directory if it doesn't exist
$hooksDir = Join-Path $gitDir "hooks"
if (-not (Test-Path $hooksDir)) {
    New-Item -Path $hooksDir -ItemType Directory -Force | Out-Null
    Write-Host "[OK] Created hooks directory" -ForegroundColor Green
}

# Install pre-commit hook
$preCommitSource = Join-Path $scriptRoot "pre-commit.ps1"
$preCommitDest = Join-Path $hooksDir "pre-commit"

if (Test-Path $preCommitDest) {
    if (-not $Force) {
        Write-Host "[WARN] Pre-commit hook already exists" -ForegroundColor Yellow
        $response = Read-Host "Overwrite? (y/n)"
        if ($response -ne "y") {
            Write-Host "Installation cancelled" -ForegroundColor Gray
            exit 0
        }
    }
}

# On Windows, git hooks need to be executable PowerShell scripts
# Create a wrapper that calls PowerShell
$hookContent = @"
#!/bin/sh
# Git pre-commit hook for TTS Demo Tool
# Calls PowerShell script for actual checks

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$preCommitSource"
exit `$?
"@

# Write hook file
Set-Content -Path $preCommitDest -Value $hookContent -NoNewline
Write-Host "[OK] Installed pre-commit hook" -ForegroundColor Green

# Make executable (on Unix-like systems)
if ($IsLinux -or $IsMacOS) {
    chmod +x $preCommitDest
    Write-Host "[OK] Made hook executable" -ForegroundColor Green
}

Write-Host "`nInstalled hooks:" -ForegroundColor Cyan
Write-Host "  [OK] pre-commit - Checks for temporary files before commit" -ForegroundColor White

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Review .gitignore to ensure it covers your needs" -ForegroundColor White
Write-Host "  2. Run: .\cleanup-before-commit.ps1 (to clean existing files)" -ForegroundColor White
Write-Host "  3. Stage files: git add ." -ForegroundColor White
Write-Host "  4. Commit: git commit -m 'Your message'" -ForegroundColor White
Write-Host "     The pre-commit hook will automatically check for issues!" -ForegroundColor Gray

Write-Host "`nTips:" -ForegroundColor Cyan
Write-Host "  - To bypass hook: git commit --no-verify" -ForegroundColor Gray
Write-Host "  - To uninstall: Remove .git/hooks/pre-commit" -ForegroundColor Gray
Write-Host "  - Hook runs automatically before each commit" -ForegroundColor Gray

Write-Host "`n[OK] Git hooks installed successfully!`n" -ForegroundColor Green
