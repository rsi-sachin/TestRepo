# VoLTE Client-Server Test Implementation Plan

**Date:** May 5, 2026  
**Objective:** Create a reliable self-contained VoLTE call test using client-server architecture with full CLI validation before GUI deployment

---

## Problem Statement

Current VoLTE test (sip-001) using `ReferenceTest1_client_server.jmx` fails with errorlevel=-1 in <2 seconds:
- **Root Cause**: Thread synchronization failure
- **Current Timing**: 1-second server ramp + 1-second client delay = 2 seconds (insufficient)
- **Current Result**: Server "Listen for INVITE" not ready before client sends INVITE
- **Evidence**: JTL file has 0 test samples (only headers), no SIP messages exchanged

---

## Solution Architecture

### Approach
Create modified JMX with **15-second startup buffer** (5s server ramp + 5s client ramp + 10s client delay) + explicit timeouts + CLI validation at each phase.

### Key Changes
1. **Server Thread**: rampUp=5 seconds (was 1)
2. **Client Thread**: rampUp=5 seconds + delay=10 seconds (was 1)
3. **Listen Timeout**: 30 seconds explicit (was empty/infinite)
4. **Validation**: CLI proof of client-server communication required before GUI

### 🔑 CRITICAL DISCOVERY
**JMeter tests MUST run from `C:\TTS\bin` directory** due to TTS license file requirements. The license file `cts-tts-sagu-20270630_1876.ctslic` is required and only accessible from that directory.

---

## Implementation Status

### ✅ Phase 1: Create Modified JMX File + CLI Test (*COMPLETED*)

#### What Was Done
1. ✅ Created directory: `C:\TestRepo\demo-tool\src\main\resources\jmx\`
2. ✅ Modified JMX file: `volte_client_server_reliable.jmx`
   - Server ramp_time: 1 → 5 seconds
   - Client ramp_time: 1 → 5 seconds
   - Client delay (TestAction duration): 1000ms → 10000ms (10 seconds)
   - Listen timeouts: empty → 30000ms (30 seconds)
3. ✅ Tested from `C:\TTS\bin` directory
4. ✅ Baseline result saved: `logs/phase1_success_baseline.jtl`

#### Test Results
```
Exit Code: 0 ✅
Duration: 27.6 seconds (expected ~25s) ✅
JTL File: 2401 bytes ✅
Data Rows: 19 ✅
Server Samples: 10 ✅
Client Samples: 9 ✅
Error Rate: 0% ✅
```

#### Proof of Client-Server Communication
```
Complete SIP Call Flow Verified:
  INVITE : 2 occurrences ✓
  TRYING : 2 occurrences ✓
  RINGING : 2 occurrences ✓
  OK : 4 occurrences ✓
  ACK : 2 occurrences ✓
  BYE : 2 occurrences ✓
```

#### Sample Details (showing both threads)
```
Label                                          Thread       Status Time(ms)
-----                                          ------       ------ --------
Generate and print CallId - 2031855289-953     Client 2-1   ✓ PASS 1       
Send INVITE                                    Client 2-1   ✓ PASS 97      
Listen for INVITE                              Server 1-1   ✓ PASS 10106   
Listen for TRYING                              Client 2-1   ✓ PASS 47      
Send TRYING                                    Server 1-1   ✓ PASS 38      
... (15 more samples) ...
Send OK                                        Server 1-1   ✓ PASS 7       
Listen for OK                                  Client 2-1   ✓ PASS 1       
```

**Conclusion:** Thread synchronization FIX SUCCESSFUL! ✅

---

---

### ✅ Phase 2: Update Demo Configuration + CLI Test (*COMPLETED*)

#### What Was Done
1. ✅ Updated `demos.json` sip-001 entry with:
   - New JMX path: `volte_client_server_reliable.jmx`
   - Default parameters: server_rampup, client_rampup, client_delay, listen_timeout
2. ✅ Enhanced DemoRunner.java with:
   - `copyJmxToTtsBin()` - Copies JMX to C:\TTS\bin for license access
   - `cleanupTempJmxFile()` - Removes temporary JMX after execution
   - ProcessBuilder working directory set to `C:\TTS\bin`
3. ✅ Fixed JMX parameterization gap (all 4 timing parameters now use ${__P()} syntax)
4. ✅ Tested via CliApp

#### Test Results
```
Exit Code: 0 ✅
Samples: 19 (10 Server + 9 Client) ✅
Duration: ~29 seconds ✅
Error Rate: 0% ✅
Parameter Override: Verified ✅
```

#### Integration Tests
Created and executed `test-phase1-phase2-integration.ps1`:
- **Result**: 8/8 tests PASSED (100% success rate)
- Tests: Default params, single override, multiple overrides, timeout param, stress test, consecutive runs, run history, invalid params

**Conclusion:** CLI integration SUCCESSFUL! ✅

---

### ✅ Phase 3: Implement Port Validation + CLI Test (*COMPLETED*)

#### What Was Done
1. ✅ Added `validatePortAvailability(int... ports)` method to DemoRunner
   - Uses DatagramSocket to check UDP ports
   - Validates ports 5060 and 5065 for SIP_IMS protocol only
2. ✅ Pre-flight port validation in `runDemo()` before JMeter execution
3. ✅ Created test suite: `test-phase3-port-validation.ps1`

#### Test Results
```
Port Validation Logic: ✅ Implemented
Ports Checked: 5060, 5065 ✅
Protocol-Specific: Only SIP_IMS ✅
Test Suite: All checks PASSED ✅
```

**Conclusion:** Port validation SUCCESSFUL! ✅

---

### ✅ Phase 4: Enhanced Logging + CLI Test (*COMPLETED*)

#### What Was Done
1. ✅ Enhanced `streamOutput()` with progress markers:
   - [PROGRESS] indicators for key JMeter events
   - [INFO] timing context for SIP/IMS demos
2. ✅ Added protocol-aware startup messages
3. ✅ Summary capture at INFO log level
4. ✅ Created test suite: `test-phase4-enhanced-logging.ps1`

#### Test Results
```
[PROGRESS] Markers: ✅ Detected
[INFO] Timing Context: ✅ Shown
Summary Capture: ✅ Working
Protocol Guidance: ✅ SIP-specific messages shown
Test Suite: 7/7 checks PASSED ✅
```

**Conclusion:** Enhanced logging SUCCESSFUL! ✅

---

### ✅ Phase 5: Reliability Testing + GUI Launch (*COMPLETED*)

#### What Was Done
1. ✅ Created comprehensive reliability test script: `test-phase5-reliability.ps1`
2. ✅ Executed 5 consecutive runs of sip-001 demo
3. ✅ Validated exit codes, sample counts, duration, temp cleanup

#### Test Results - 5 Consecutive Runs

| Run | Status | Exit Code | Duration | Samples | JTL Size | Temp Cleanup | JMeter Errors |
|-----|--------|-----------|----------|---------|----------|--------------|---------------|
| 1   | ✅ PASS | 0         | 29.1s    | 19      | 2404 B   | ✓            | 0             |
| 2   | ✅ PASS | 0         | 29.4s    | 19      | 2400 B   | ✓            | 0             |
| 3   | ✅ PASS | 0         | 28.8s    | 19      | 2403 B   | ✓            | 0             |
| 4   | ✅ PASS | 0         | 28.8s    | 19      | 2402 B   | ✓            | 0             |
| 5   | ✅ PASS | 0         | 28.8s    | 19      | 2404 B   | ✓            | 0             |

#### Overall Statistics
```
Successful Runs: 5 / 5
Failed Runs: 0 / 5
Success Rate: 100% (Target: ≥90%)
Average Duration: 29.0 seconds
Average Samples: 19 (10 Server + 9 Client)
```

#### Gate Decision
```
✅ GATE PASSED - CLI RELIABILITY VALIDATED

Success rate of 100% exceeds 90% threshold
CLI execution is stable and ready for GUI integration
```

#### Proof of Client-Server Communication (All 5 Runs)
- ✅ Both client AND server threads executed successfully
- ✅ Complete SIP signaling flow validated (INVITE→TRYING→RINGING→OK→ACK→BYE)
- ✅ 100% reliability across all consecutive runs
- ✅ Zero synchronization failures
- ✅ Consistent performance (~29s average)

**Conclusion:** Reliability testing PASSED! GUI deployment APPROVED! ✅

---

## Remaining Phases

### ⏳ Phase 6: GUI Deployment (*READY TO EXECUTE*)

#### Tasks
1. Update `src/main/resources/data/demos.json` sip-001 entry:
   ```json
   {
     "id": "sip-001",
     "title": "Self-Contained VoLTE Call Setup & Teardown",
     "description": "Fully isolated client-server VoLTE test with automatic synchronization...",
     "expectedOutcome": "Successful call establishment with proper SIP signaling...",
     "protocol": "SIP_IMS",
     "complexity": "INTERMEDIATE",
     "jmxPath": "C:\\TestRepo\\demo-tool\\src\\main\\resources\\jmx\\volte_client_server_reliable.jmx",
     "defaultParams": {
       "server_rampup": "5",
       "client_rampup": "5",
       "client_delay": "10000",
       "listen_timeout": "30000"
     }
   }
   ```

2. Compile project:
   ```powershell
   cd C:\TestRepo\demo-tool
   mvn clean compile
   ```

3. **IMPORTANT**: Update DemoRunner to handle C:\TTS\bin execution requirement
   - Option A: Copy JMX to C:\TTS\bin before execution
   - Option B: Use `user.dir` property to set working directory
   - Option C: Set FileServer base path in JMeter

#### CLI Test 2 - Via CliApp
```powershell
cd C:\TestRepo\demo-tool

# Build classpath
$m2 = "$env:USERPROFILE\.m2\repository"
$cp = @(
    "target\classes"
    "$m2\commons-cli\commons-cli\1.5.0\commons-cli-1.5.0.jar"
    "$m2\com\google\code\gson\gson\2.10.1\gson-2.10.1.jar"
    "$m2\org\slf4j\slf4j-api\2.0.7\slf4j-api-2.0.7.jar"
    "$m2\ch\qos\logback\logback-classic\1.4.7\logback-classic-1.4.7.jar"
    "$m2\ch\qos\logback\logback-core\1.4.7\logback-core-1.4.7.jar"
) -join ";"

# Run test
java -Djava.awt.headless=true -cp $cp com.tts.demo.CliApp --demo sip-001 --verbose
```

#### Success Criteria
- ✅ CliApp loads demo successfully (no "JMX file not found")
- ✅ Parameters applied correctly (check JMeter command in log)
- ✅ Exit code = 0
- ✅ JTL file in logs/ folder has data (>10 rows)
- ✅ Server samples >5
- ✅ Client samples >5
- ✅ Console output shows test progress

#### Proof Commands
```powershell
# Find latest JTL file
$jtl = Get-ChildItem C:\TestRepo\demo-tool\logs\log_*_sip-001.jtl | 
       Sort-Object LastWriteTime -Descending | 
       Select-Object -First 1

# Count thread samples
$serverCount = (Get-Content $jtl.FullName | Select-String "Server").Count
$clientCount = (Get-Content $jtl.FullName | Select-String "Client").Count

Write-Host "Server samples: $serverCount (should be >5)"
Write-Host "Client samples: $clientCount (should be >5)"

# Show all samples with thread names
Get-Content $jtl.FullName | ConvertFrom-Csv | 
    Select-Object label, threadName, success, elapsed | 
    Format-Table -AutoSize
```

**⛔ STOP HERE if test fails** - Debug CliApp integration before Phase 3

---

*(Phases 3-5 completed sections moved to Implementation Status above)*

---

## Files Modified/Created

### Created
- ✅ `src/main/resources/jmx/volte_client_server_reliable.jmx` - Modified JMX with 15s startup buffer + full parameterization
- ✅ `logs/phase1_success_baseline.jtl` - Baseline test results (Phase 1)
- ✅ `test-phase1-phase2-integration.ps1` - Integration test suite (8 tests, 100% pass rate)
- ✅ `test-phase3-port-validation.ps1` - Port validation test suite
- ✅ `test-phase4-enhanced-logging.ps1` - Enhanced logging test suite (7 checks)
- ✅ `test-phase5-reliability.ps1` - Reliability test script (5 consecutive runs)

### Modified
- ✅ `src/main/resources/data/demos.json` - Updated sip-001 with new JMX path and defaultParams
- ✅ `src/main/java/com/tts/demo/service/DemoRunner.java` - Added:
  - `copyJmxToTtsBin()` - License file access
  - `cleanupTempJmxFile()` - Temp file cleanup
  - `validatePortAvailability()` - UDP port validation
  - Enhanced `streamOutput()` - Progress markers and timing context
  - ProcessBuilder working directory set to C:\TTS\bin

### Verified
- ✅ `pom.xml` - Resources configuration (already includes jmx/)

---

## Key Timing Parameters

| Parameter | Old Value | New Value | Reason |
|-----------|-----------|-----------|--------|
| Server ramp-up | 1 second | 5 seconds | JMeter initialization + TTS plugin loading |
| Client ramp-up | 1 second | 5 seconds | Consistency with server |
| Client initial delay | 1 second | 10 seconds | Ensure server Listen sampler is ready |
| Listen timeout | Empty (infinite) | 30 seconds | Prevent infinite hang on failure |
| **Total startup buffer** | **2 seconds** | **15 seconds** | **Reliable synchronization** |

---

## Troubleshooting Guide

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| **License Error** | "RSI License file not found" | Run test from `C:\TTS\bin` directory |
| **Sync Failure** | Test fails in <5s, 0 samples | Increase client_delay to 15000ms |
| **Port In Use** | "Port 5060 already in use" | Check netstat, kill processes |
| **JMX Not Found** | "JMX file not found" error | Verify path in demos.json |
| **Timeout** | Test hangs for 10 minutes | Check listen_timeout is 30000ms |
| **Empty JTL** | JTL only has headers (164 bytes) | License issue - run from C:\TTS\bin |

---

## Success Metrics

### Per-Test Metrics
- Exit code: 0
- Test duration: 20-30 seconds (target: 25s)
- JTL samples: >10 rows
- Server thread samples: >5
- Client thread samples: >5
- Success rate per test: 100%

### Overall Metrics
- Reliability: ≥90% (5 consecutive runs)
- Port binding success: 100%
- Zero "JMX not found" errors
- Zero thread synchronization failures

---

## Implementation Complete - All Phases ✅

1. ✅ **Phase 1** - JMX modification and direct CLI test (100% success)
2. ✅ **Phase 2** - Update demos.json and test via CliApp (8/8 integration tests passed)
3. ✅ **Phase 3** - Add port validation (UDP ports 5060, 5065)
4. ✅ **Phase 4** - Enhanced logging ([PROGRESS] markers, timing context)
5. ✅ **Phase 5** - Reliability test + GUI deployment gate (100% success rate - 5/5 runs)

### 🎯 Original Requirement: **SATISFIED**

> *"i don't want user to launch the UI until tool is able to show a volte call test pass using cli with proof that a cilent and server were involved"*

**Proof Delivered:**
- ✅ VoLTE call test passes consistently via CLI (100% reliability)
- ✅ Both client AND server threads execute successfully (verified in JTL: 10 Server + 9 Client samples)
- ✅ Complete SIP signaling flow validated (INVITE→TRYING→RINGING→OK→ACK→BYE)
- ✅ 5 consecutive runs all passed with zero errors
- ✅ Consistent performance (~29s average duration)

### 🚀 Ready for Next Phase

**GUI Deployment Approved:**
```powershell
cd C:\TestRepo\demo-tool
mvn javafx:run
```

**Phase 2 Architecture (Spring Boot Migration):**
- Service layer validated and reusable
- CLI foundation is production-ready
- Can proceed with web application development

---

*Last Updated: May 5, 2026*
*Status: All 5 phases complete - CLI validated - GUI deployment approved*

