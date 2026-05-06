# TTS Demo Tool - Copilot Instructions

This workspace contains the **TTS Demo Tool** — a JavaFX desktop application for demonstrating
Computaris TTS (Telecom Testing System) capabilities to internal engineers.

## Project Context

| Item | Value |
|---|---|
| Dev workspace | `C:\testrepo` |
| TTS install (read-only) | `C:\TTS` — do NOT modify anything here |
| Requirements | `C:\testrepo\docs\requirements.txt` |
| GitHub repo | https://github.com/rsi-sachin/TestRepo |
| Branches | main, master, develop |

## Technology Stack

- **Phase 1 (current):** JavaFX desktop app, Maven, Java 11+
- **Phase 2 (future):** Spring Boot + Vanilla JS web app (reuse service layer)
- **Package:** `com.tts.demo`

## Project Structure

```
C:\testrepo\demo-tool\
  pom.xml
  src/
    main/
      java/com/tts/demo/
        MainApp.java              # JavaFX Application entry point
        controller/               # FXML UI controllers
        model/                    # POJOs: Demo, RunResult, DemoConfig
        service/                  # DemoCatalog, DemoRunner, ConfigManager
      resources/
        fxml/                     # FXML layout files
        css/                      # Stylesheets
        data/demos.json           # Demo catalog: business scenarios -> JMX mapping
    test/java/                    # Unit tests
  docs/
    requirements.txt              # Full requirements with REQ-IDs
  runs/                           # JSON run history files (auto-generated)
```

## TTS / JMeter Execution

JMeter non-GUI command used to run demos:
```
C:\TTS\bin\jmeter-n.cmd -n -t {jmx_path} -l {log_path} -J{param}={value}
```

## Demo Protocols (Phase 1)

| Protocol | JMX Templates | Reference Tests |
|---|---|---|
| SIP/IMS | `C:\TTS\bin\templates\tts\tts_sip_*.jmx` | `C:\TTS\docs\sip\reference_tests\` (9 files) |
| Diameter | `C:\TTS\bin\templates\tts\tts_diameter_*.jmx` | `C:\TTS\docs\diameter\reference_tests\` (11 files) |
| RADIUS | `C:\TTS\bin\templates\tts\tts_*radius*.jmx` | `C:\TTS\docs\radius_client\reference_tests\` (32 files) |

## Key Requirements (summary)

- **REQ-001:** Support 6 use case categories (Telco, Traffic Gen, API, Web, Mobile, IoT)
- **REQ-002:** IMS testing demos (UE simulation, NE simulation, traffic gen, pcap, reports)
- **REQ-003:** IMS & VoLTE demos (Diameter + SIP signaling, x-CSCF connectivity)
- **REQ-004:** Isolated IMS environment testing (no external systems needed)
- **REQ-005:** Phase 1 protocols — SIP/IMS, Diameter, RADIUS
- **REQ-006:** UI MUST use business-level KPI language, NOT raw protocol/technical terms
  - CORRECT: "Simulate VoLTE Call Setup", "Test Subscriber Authentication"
  - WRONG: "Send SIP INVITE", "Run tts_diameter_client1.jmx"
- **REQ-007:** Phase 1 audience = internal engineers; Phase 2 = external customers
- **REQ-008:** Demo execution engine wraps jmeter-n.cmd, streams live output to UI
- **REQ-009:** Run history persisted as JSON in `runs/` folder

Full requirements: `C:\testrepo\docs\requirements.txt`

## Coding Guidelines

- Do NOT modify anything under `C:\TTS\`
- All new code goes under `C:\testrepo\demo-tool\`
- Follow standard Maven project layout
- UI labels must always use business language (REQ-006)
- Each demo scenario in `demos.json` must have: id, title, description, outcome, protocol, complexity, jmxPath, defaultParams
