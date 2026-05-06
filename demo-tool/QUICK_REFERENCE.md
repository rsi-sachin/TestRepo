# TTS Demo Tool - Quick Reference Card

**Date:** May 5, 2026 | **Status:** ✅ Production-Ready

---

## 🚀 Quick Start

### Run VoLTE Test (CLI)
```powershell
cd C:\TestRepo\demo-tool
.\quick-start.ps1
```

### Launch GUI (Approved)
```powershell
cd C:\TestRepo\demo-tool
mvn javafx:run
```

---

## 📋 Essential Commands

### CLI Mode (Manual Classpath)
```powershell
cd C:\TestRepo\demo-tool

# Build classpath variable
$m2 = "$env:USERPROFILE\.m2\repository"
$cp = @(
    "target\classes",
    "$m2\commons-cli\commons-cli\1.5.0\commons-cli-1.5.0.jar",
    "$m2\com\google\code\gson\gson\2.10.1\gson-2.10.1.jar",
    "$m2\org\slf4j\slf4j-api\2.0.7\slf4j-api-2.0.7.jar",
    "$m2\ch\qos\logback\logback-classic\1.4.7\logback-classic-1.4.7.jar",
    "$m2\ch\qos\logback\logback-core\1.4.7\logback-core-1.4.7.jar"
) -join ";"

# Run demo
java -Djava.awt.headless=true -cp $cp com.tts.demo.CliApp --demo sip-001

# List demos
java -Djava.awt.headless=true -cp $cp com.tts.demo.CliApp --list

# Custom parameters
java -Djava.awt.headless=true -cp $cp com.tts.demo.CliApp --demo sip-001 --param client_delay=8000
```

### Build Project
```powershell
cd C:\TestRepo\demo-tool
mvn clean compile
```

---

## 🎯 VoLTE Test (sip-001)

| Property | Value |
|----------|-------|
| **Duration** | ~29 seconds |
| **Samples** | 19 (10 Server + 9 Client) |
| **Ports** | 5060 (server), 5065 (client) |
| **Success Rate** | 100% (validated) |
| **Protocol Flow** | INVITE→TRYING→RINGING→OK→ACK→BYE |

### Tunable Parameters
```powershell
--param server_rampup=5        # Server thread ramp-up (seconds)
--param client_rampup=5        # Client thread ramp-up (seconds)
--param client_delay=10000     # Client startup delay (ms)
--param listen_timeout=30000   # SIP listen timeout (ms)
```

---

## 🔍 Troubleshooting

### Check Port Availability
```powershell
netstat -an | Select-String ":5060|:5065"
# Should return nothing if ports are free
```

### Verify Latest Test Results
```powershell
# Find latest JTL file
Get-ChildItem C:\TestRepo\demo-tool\logs\log_*.jtl | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1 | 
    Get-Content | 
    ConvertFrom-Csv | 
    Select-Object label, threadName, success, elapsed | 
    Format-Table -AutoSize
```

### Check Exit Code
```powershell
java -Djava.awt.headless=true -cp $cp com.tts.demo.CliApp --demo sip-001
Write-Host "Exit Code: $LASTEXITCODE"
```

---

## ⚠️ Critical Constraints

### TTS License Requirement
- **License File:** `C:\TTS\bin\cts-tts-sagu-20270630_1876.ctslic`
- **Impact:** Tests MUST run from `C:\TTS\bin` working directory
- **Solution:** DemoRunner automatically copies JMX to C:\TTS\bin

### Port Requirements (SIP/IMS)
- **Ports:** 5060, 5065 must be free
- **Validation:** Automatic pre-flight check by DemoRunner
- **Error:** "Port already in use" → Close conflicting applications

### Thread Synchronization
- **Startup Buffer:** 15 seconds (5s + 5s + 10s)
- **Reason:** JMeter + TTS plugin initialization time
- **Warning:** Reducing below 10s may cause sync failures

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `src/main/resources/data/demos.json` | Demo catalog (business descriptions) |
| `src/main/resources/jmx/volte_client_server_reliable.jmx` | VoLTE JMX template |
| `src/main/java/com/tts/demo/service/DemoRunner.java` | Execution engine |
| `logs/log_*.jtl` | Test result files (JMeter CSV format) |
| `runs/*.json` | Run history (JSON format) |

---

## 📊 Test Scripts

| Script | Usage |
|--------|-------|
| `test-phase1-phase2-integration.ps1` | Full integration test (8 tests) |
| `test-phase5-reliability.ps1` | 5 consecutive runs (gate check) |

---

## 🧪 Expected Test Output

### Success Indicators
```
✅ Exit Code: 0
✅ Samples: 19
✅ Duration: 25-30 seconds
✅ Error Rate: 0%
✅ [PROGRESS] markers visible
✅ Temp JMX cleanup successful
```

### Sample Thread Output
```
Server Thread: 10 samples
  - Listen for INVITE (10s wait)
  - Send TRYING
  - Send RINGING
  - Send OK
  
Client Thread: 9 samples
  - Send INVITE
  - Listen for TRYING
  - Listen for RINGING
  - Listen for OK
  - Send ACK
  - Send BYE
```

---

## 🔗 Documentation

- 📄 **Implementation Plan:** `VOLTE_CLIENT_SERVER_IMPLEMENTATION_PLAN.md`
- 📄 **Completion Summary:** `PHASE5_COMPLETION_SUMMARY.md`
- 📄 **Current Status:** `PROJECT_STATUS.md`
- 📄 **Requirements:** `docs\requirements.txt`

---

## 📞 Support

### Common Issues

| Issue | Solution |
|-------|----------|
| "License file not found" | Run from C:\TTS\bin (handled automatically by DemoRunner) |
| "Port already in use" | Check netstat, kill conflicting processes |
| Test hangs forever | Check listen_timeout is set (30000ms default) |
| 0 samples in JTL | Thread sync failure - use 15s startup buffer |
| JMX file not found | Verify demos.json path, rebuild project |

---

**🎉 CLI is production-ready | GUI deployment approved**

*Quick Reference v1.0 - May 5, 2026*
