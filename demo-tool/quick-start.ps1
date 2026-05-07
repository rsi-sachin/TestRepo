# TTS Demo Tool - Quick Start Script
# Automatically kills existing instances and launches the application

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "TTS Demo Tool - Launcher" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill existing instances
Write-Host "[1/3] Checking for existing instances..." -ForegroundColor Yellow
$killedCount = 0
$javaProcesses = Get-Process java -ErrorAction SilentlyContinue

if ($javaProcesses) {
    foreach ($proc in $javaProcesses) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            
            if ($cmdLine -like "*demo-tool*" -or $cmdLine -like "*com.tts.demo.MainApp*") {
                Write-Host "  Killing existing instance (PID: $($proc.Id))..." -ForegroundColor Gray
                Stop-Process -Id $proc.Id -Force
                $killedCount++
            }
        } catch {
            # Silently ignore processes we can't inspect
        }
    }
}

if ($killedCount -gt 0) {
    Write-Host "  [OK] Killed $killedCount existing instance(s)" -ForegroundColor Green
    Start-Sleep -Seconds 1
} else {
    Write-Host "  [OK] No existing instances found" -ForegroundColor Green
}

# Step 2: Environment check
Write-Host ""
Write-Host "[2/3] Checking environment..." -ForegroundColor Yellow

$errors = 0

$javaCheck = Get-Command java -ErrorAction SilentlyContinue
if ($javaCheck) {
    Write-Host "  [OK] Java found" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Java not found" -ForegroundColor Red
    $errors++
}

$mvnCheck = Get-Command mvn -ErrorAction SilentlyContinue
if ($mvnCheck) {
    Write-Host "  [OK] Maven found" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Maven not found" -ForegroundColor Red
    $errors++
}

if (Test-Path "C:\TTS\bin\jmeter.bat") {
    Write-Host "  [OK] TTS found at C:\TTS" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] TTS not found at C:\TTS (demos will fail)" -ForegroundColor Yellow
}

if (-not (Test-Path "pom.xml")) {
    Write-Host "  [ERROR] pom.xml not found - run from demo-tool directory" -ForegroundColor Red
    $errors++
}

if ($errors -gt 0) {
    Write-Host ""
    Write-Host "Cannot start application - fix errors above" -ForegroundColor Red
    exit 1
}

# Step 3: Launch application
Write-Host ""
Write-Host "[3/3] Launching TTS Demo Tool..." -ForegroundColor Yellow
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

mvn javafx:run
