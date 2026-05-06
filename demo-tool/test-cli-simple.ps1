#!/usr/bin/env pwsh
# Test CLI - Simplified version
# 
# IMPORTANT: This script uses direct Java execution with minimal classpath
# to avoid loading JavaFX dependencies, which would create unwanted GUI windows.

Set-Location "C:\TestRepo\demo-tool"

Write-Host "Running CLI --list command..." -ForegroundColor Cyan
Write-Host ""

# Build classpath with known dependencies (excluding JavaFX)
$m2 = "$env:USERPROFILE\.m2\repository"
$cp = @(
    "target\classes"
    "$m2\commons-cli\commons-cli\1.5.0\commons-cli-1.5.0.jar"
    "$m2\com\google\code\gson\gson\2.10.1\gson-2.10.1.jar"
    "$m2\org\slf4j\slf4j-api\2.0.7\slf4j-api-2.0.7.jar"
    "$m2\ch\qos\logback\logback-classic\1.4.7\logback-classic-1.4.7.jar"
    "$m2\ch\qos\logback\logback-core\1.4.7\logback-core-1.4.7.jar"
) -join ";"

# Run the CLI application (headless mode to prevent GUI initialization)
java -Djava.awt.headless=true -cp $cp com.tts.demo.CliApp --list

$exitCode = $LASTEXITCODE
Write-Host ""
Write-Host "Exit code: $exitCode" -ForegroundColor $(if ($exitCode -eq 0) { "Green" } else { "Red" })
exit $exitCode
