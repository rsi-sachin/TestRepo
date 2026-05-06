# Kill any stray TTS Demo Tool GUI processes

Write-Host ""
Write-Host "Checking for stray TTS Demo Tool processes..." -ForegroundColor Cyan
Write-Host ""

$javaProcesses = Get-Process java -ErrorAction SilentlyContinue

if ($javaProcesses) {
    Write-Host "Found $($javaProcesses.Count) Java process(es):" -ForegroundColor Yellow
    
    foreach ($proc in $javaProcesses) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            
            if ($cmdLine -like "*demo-tool*" -or $cmdLine -like "*com.tts.demo*") {
                Write-Host ""
                Write-Host "  PID: $($proc.Id)" -ForegroundColor Red
                Write-Host "  Command: $($cmdLine.Substring(0, [Math]::Min(100, $cmdLine.Length)))..." -ForegroundColor Gray
                
                $response = Read-Host "  Kill this process? (Y/N)"
                if ($response -eq "Y" -or $response -eq "y") {
                    Stop-Process -Id $proc.Id -Force
                    Write-Host "  Process killed" -ForegroundColor Green
                } else {
                    Write-Host "  Skipped" -ForegroundColor Yellow
                }
            }
        } catch {
            Write-Host "  PID: $($proc.Id) - Unable to check command line" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host "Done." -ForegroundColor Cyan
} else {
    Write-Host "No Java processes found." -ForegroundColor Green
}

Write-Host ""
Write-Host "Tip: Use test-cli-simple.ps1 or test-cli-run.ps1 to avoid stray GUIs" -ForegroundColor Yellow
Write-Host ""
