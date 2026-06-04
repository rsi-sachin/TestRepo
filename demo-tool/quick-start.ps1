# TTS Demo Tool - Quick Start Script
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "TTS Demo Tool - Environment Check" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Check Java
Write-Host "Checking Java..." -ForegroundColor Yellow
$javaCheck = Get-Command java -ErrorAction SilentlyContinue
if ($javaCheck) {
    Write-Host "[OK] Java found" -ForegroundColor Green
} else {
    Write-Host "[MISSING] Java not found" -ForegroundColor Red
}

# Check Maven
Write-Host "Checking Maven..." -ForegroundColor Yellow
$mvnCheck = Get-Command mvn -ErrorAction SilentlyContinue
if ($mvnCheck) {
    Write-Host "[OK] Maven found" -ForegroundColor Green
} else {
    Write-Host "[MISSING] Maven not found - install with: choco install maven" -ForegroundColor Red
}

# Check TTS
Write-Host "Checking TTS..." -ForegroundColor Yellow
if (Test-Path "C:\TTS\bin\jmeter-n.cmd") {
    Write-Host "[OK] TTS found at C:\TTS" -ForegroundColor Green
} else {
    Write-Host "[MISSING] TTS not found at C:\TTS" -ForegroundColor Red
}

# Check project files
Write-Host "Checking project..." -ForegroundColor Yellow
if (Test-Path "pom.xml") {
    Write-Host "[OK] Project files present" -ForegroundColor Green
} else {
    Write-Host "[ERROR] pom.xml not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. mvn clean compile" -ForegroundColor White
Write-Host "  2. mvn test" -ForegroundColor White
Write-Host "  3. mvn javafx:run" -ForegroundColor White
Write-Host ""
Write-Host "See README.md for details" -ForegroundColor Cyan
