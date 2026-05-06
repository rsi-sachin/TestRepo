# TTS Demo Tool - Current Project State

**Last Updated:** May 5, 2026  
**Status:** ✅ CLI Production-Ready | GUI Deployment Approved

---

## Quick Status

| Component | Status | Notes |
|-----------|--------|-------|
| **CLI Execution** | ✅ Production-Ready | 100% reliability validated (5/5 runs) |
| **GUI Application** | ✅ Ready to Deploy | `mvn javafx:run` approved |
| **VoLTE Client-Server Test** | ✅ Working | sip-001 demo, 19 samples, 0% errors |
| **Phase 2 Architecture** | 🔜 Ready to Start | Service layer validated, Spring Boot migration next |

---

## How to Run

### CLI Mode (Validated, Production-Ready)
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

# Run VoLTE test
java -Djava.awt.headless=true -cp $cp com.tts.demo.CliApp --demo sip-001

# List available demos
java -Djava.awt.headless=true -cp $cp com.tts.demo.CliApp --list
```

### GUI Mode (Approved, Not Yet Launched)
```powershell
cd C:\TestRepo\demo-tool
mvn javafx:run
```

---

## VoLTE Test (sip-001) - Key Facts

### What It Does
- **Business Description:** "Self-Contained VoLTE Call Setup & Teardown"
- **Technical Implementation:** Client-server SIP/IMS signaling over UDP
- **Ports:** 5060 (server), 5065 (client)
- **Protocol Flow:** INVITE → TRYING → RINGING → OK → ACK → BYE

### Performance
- **Duration:** ~29 seconds average
- **Samples:** 19 (10 Server + 9 Client threads)
- **Success Rate:** 100% (5/5 consecutive runs)
- **Error Rate:** 0%

### Timing Parameters (Parameterized via -J flags)
- `server_rampup=5` - Server thread ramp-up (seconds)
- `client_rampup=5` - Client thread ramp-up (seconds)
- `client_delay=10000` - Client startup delay (milliseconds)
- `listen_timeout=30000` - SIP listen timeout (milliseconds)

### Example with Custom Parameters
```powershell
java -Djava.awt.headless=true -cp $cp com.tts.demo.CliApp `
    --demo sip-001 `
    --param server_rampup=3 `
    --param client_delay=8000
```

---

## Critical System Requirements

### TTS License Constraint
- **License File:** `C:\TTS\bin\cts-tts-sagu-20270630_1876.ctslic`
- **Requirement:** All JMeter tests MUST run from `C:\TTS\bin` directory
- **Implementation:** DemoRunner copies JMX to C:\TTS\bin, sets ProcessBuilder working directory

### Port Availability
- **SIP/IMS Tests:** Require ports 5060 and 5065 to be free
- **Validation:** Pre-flight check using DatagramSocket
- **Check Manually:** `netstat -an | Select-String ":5060|:5065"`

---

## Project Structure

```
C:\TestRepo\demo-tool\
├── pom.xml                                      # Maven configuration
├── src\
│   ├── main\
│   │   ├── java\com\tts\demo\
│   │   │   ├── MainApp.java                    # JavaFX entry point
│   │   │   ├── CliApp.java                     # CLI entry point ✅
│   │   │   ├── controller\                     # FXML controllers
│   │   │   ├── model\                          # Demo, RunResult POJOs
│   │   │   └── service\
│   │   │       ├── DemoCatalog.java            # Loads demos.json
│   │   │       ├── DemoRunner.java             # Execution engine ✅
│   │   │       └── ConfigManager.java          # Configuration
│   │   └── resources\
│   │       ├── data\demos.json                 # Demo catalog ✅
│   │       ├── jmx\volte_client_server_reliable.jmx  # VoLTE JMX ✅
│   │       ├── fxml\                           # UI layouts
│   │       └── css\                            # Stylesheets
│   └── test\java\                              # Unit tests
├── logs\                                        # JTL run results
├── runs\                                        # JSON run history
└── test-phase*.ps1                             # Validation scripts ✅

✅ = Recently modified/validated
```

---

## Test Scripts (All Validated)

| Script | Purpose | Result |
|--------|---------|--------|
| `test-phase1-phase2-integration.ps1` | Parameter override, consecutive runs | 8/8 tests passed |
| `test-phase3-port-validation.ps1` | UDP port validation (5060, 5065) | All checks passed |
| `test-phase4-enhanced-logging.ps1` | [PROGRESS] markers, timing context | 7/7 checks passed |
| `test-phase5-reliability.ps1` | 5 consecutive runs, gate decision | 5/5 runs passed (100%) |

---

## Recent Changes (Phase 1-5 Implementation)

### DemoRunner.java Enhancements
1. ✅ `copyJmxToTtsBin()` - Copies JMX to C:\TTS\bin for license access
2. ✅ `cleanupTempJmxFile()` - Removes temporary JMX after execution
3. ✅ `validatePortAvailability()` - Pre-flight UDP port checking
4. ✅ Enhanced `streamOutput()` - [PROGRESS] and [INFO] markers for better user feedback
5. ✅ ProcessBuilder working directory set to C:\TTS\bin

### demos.json Updates
- ✅ sip-001 entry points to `volte_client_server_reliable.jmx`
- ✅ Default parameters: server_rampup, client_rampup, client_delay, listen_timeout

### JMX Parameterization
- ✅ All 4 timing parameters use `${__P(property_name,default)}` syntax
- ✅ Runtime configuration via -J flags now working

---

## Known Issues / Limitations

### None Currently
All phases completed successfully with 100% test pass rates.

### Historical Issues (Resolved)
1. ❌ Thread synchronization failure → ✅ Fixed with 15s startup buffer
2. ❌ License file not found → ✅ Fixed with C:\TTS\bin working directory
3. ❌ Hardcoded timing values → ✅ Fixed with JMX parameterization

---

## Next Steps (In Priority Order)

### 1. GUI Deployment (Immediate)
```powershell
cd C:\TestRepo\demo-tool
mvn javafx:run
```
**Validation Checklist:**
- [ ] Application starts without errors
- [ ] sip-001 demo visible in catalog
- [ ] Run demo successfully from GUI
- [ ] Console shows [PROGRESS] markers
- [ ] Results saved to run history

### 2. Phase 2 Architecture (Next Sprint)
- [ ] Design Spring Boot REST API around service layer
- [ ] Create Vanilla JS frontend (reuse business language)
- [ ] WebSocket support for real-time progress
- [ ] Maintain CLI for automation

### 3. Additional Protocols (Future)
- [ ] Diameter demos (reference tests in C:\TTS\docs\diameter\)
- [ ] RADIUS demos (reference tests in C:\TTS\docs\radius_client\)

---

## Documentation

### Full Documentation
- 📄 `VOLTE_CLIENT_SERVER_IMPLEMENTATION_PLAN.md` - Complete 5-phase implementation plan
- 📄 `PHASE5_COMPLETION_SUMMARY.md` - Phase 5 reliability test results
- 📄 `docs\requirements.txt` - Full requirements (REQ-001 to REQ-009)
- 📄 `.github\copilot-instructions.md` - Project context for GitHub Copilot

### Repository Memory
- 📄 `/memories/repo/tts-demo-tool-facts.md` - Key facts, conventions, lessons learned

---

## Contact Information

- **GitHub Repo:** https://github.com/rsi-sachin/TestRepo
- **Branches:** main, master, develop
- **Dev Workspace:** C:\TestRepo
- **TTS Installation:** C:\TTS (read-only)

---

**🎉 Status: Ready for GUI deployment and Phase 2 migration**

*Last validated: May 5, 2026*
