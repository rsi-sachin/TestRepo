#!/usr/bin/env pwsh
# Test CLI List Command

$ErrorActionPreference = "Stop"
Set-Location "C:\TestRepo\demo-tool"

Write-Host "Building classpath..." -ForegroundColor Cyan

# Get Maven dependencies classpath
$cpOutput = & "$env:USERPROFILE\tools\apache-maven-3.9.9\bin\mvn.cmd" dependency:build-classpath -DincludeScope=runtime -q -Dmdep.outputFile=target/cp.txt 2>&1
$classpath = Get-Content target/cp.txt -ErrorAction SilentlyContinue

if (-not $classpath) {
    Write-Host "Error: Could not build classpath" -ForegroundColor Red
    exit 1
}

# Add compiled classes to classpath
$fullClasspath = "target\classes;$classpath"

Write-Host "Running CLI --list command..." -ForegroundColor Cyan
Write-Host ""

# Run the CLI application
java -cp $fullClasspath com.tts.demo.CliApp --list

Write-Host ""
Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor $(if ($LASTEXITCODE -eq 0) { "Green" } else { "Red" })
