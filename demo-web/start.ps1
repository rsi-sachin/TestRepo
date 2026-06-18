# Quick Start Script for TTS Demo Tool Web
# Run this to set up and start the web application

Write-Host "TTS Demo Tool - Web Application Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.1[1-9]") {
    Write-Host "✓ Python version OK: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3.11+ required. Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Navigate to backend
Set-Location "$PSScriptRoot\backend"

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Copy .env if doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env created (please review and update paths)" -ForegroundColor Green
}

# Validate TTS installation
Write-Host ""
Write-Host "Validating TTS installation..." -ForegroundColor Yellow
if (Test-Path "C:\TTS\bin\jmeter.bat") {
    Write-Host "✓ JMeter found at C:\TTS\bin\jmeter.bat" -ForegroundColor Green
} else {
    Write-Host "⚠ JMeter not found at C:\TTS\bin\jmeter.bat" -ForegroundColor Yellow
    Write-Host "  Update TTS_PATH in .env if installed elsewhere" -ForegroundColor Yellow
}

# Validate demo catalog
$catalogPath = "..\..\demo-tool\src\main\resources\data\demos.json"
if (Test-Path $catalogPath) {
    Write-Host "✓ Demo catalog found" -ForegroundColor Green
} else {
    Write-Host "⚠ Demo catalog not found at $catalogPath" -ForegroundColor Yellow
    Write-Host "  Update DEMO_CATALOG_PATH in .env" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Setup complete! Starting server..." -ForegroundColor Green
Write-Host ""
Write-Host "Access the web app at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API documentation: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
python run.py
