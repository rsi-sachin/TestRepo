# Run Playwright E2E Tests

Write-Host "TTS Demo Tool - Running E2E Tests" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "Checking if backend is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✓ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend is not running!" -ForegroundColor Red
    Write-Host "  Please start backend first: .\start.ps1" -ForegroundColor Yellow
    exit 1
}

# Navigate to tests directory
Set-Location "$PSScriptRoot\tests"

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating test virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Test virtual environment created" -ForegroundColor Green
}

# Activate venv
Write-Host "Activating test virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install test dependencies
Write-Host "Installing test dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✓ Test dependencies installed" -ForegroundColor Green

# Install Playwright browsers if needed
Write-Host "Checking Playwright browsers..." -ForegroundColor Yellow
playwright install chromium --quiet
Write-Host "✓ Playwright browsers ready" -ForegroundColor Green

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Running E2E tests..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Run tests
pytest e2e/test_demo_workflows.py -v --tb=short

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Tests complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
