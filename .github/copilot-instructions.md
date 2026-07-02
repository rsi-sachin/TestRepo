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
- For any Python-based software, package, or tooling need, including document and PDF reading, always use the workspace virtual environment and its installed packages.
- Do not rely on system Python or globally installed packages when a workspace virtual environment is available.

## Skill Trigger Rules

- When a user request matches the pattern `analyze <sections> from <document>`, always invoke the document-analysis workflow skill first.
- Prefer `document-cross-reference-analysis` as the workflow entry skill, and choose `single` mode unless the user asks for dependency or multi-document expansion.
- For protocol-centric content (HTTP/REST/resources/status-codes/authentication), invoke `document-analysis-a1tp` as the primary analysis skill before extraction or mapping.
- Do not proceed with protocol-centric analysis using only `document-cross-reference-analysis`; `document-analysis-a1tp` selection is mandatory.
- Missing required skill invocation is a blocker, not a warning.
- When a user request includes `Use Test Harness skill to add unit/component/module/interface/feature and e2e tests for a given commit or change summary`, invoke `test-harness-regression` first.
- For test harness requests, include perspectives for memory, load, stress, parameter passing, and fault/error handling where applicable, and maintain regression mapping artifacts for changed files/modules.
- After any `analyze <sections> from <document>` workflow completes and implementation/testing is requested, invoke `post-analysis-test-policy-orchestration` to launch post-analysis test planning.
- In `post-analysis-test-policy-orchestration`, the `Test Policy Orchestrator` agent must be invoked with recent analysis/commit changes to derive required tests.
- If the analyzed source is a test specification (for example, TS 103 989), `post-analysis-test-policy-orchestration` must generate a clause-by-clause coverage matrix and add missing tests for uncovered clauses before completion.
- `post-analysis-test-policy-orchestration` must persist outputs using fixed artifact paths under `ORAN/docs/test-policy/` and `ORAN/docs/coverage/`.
- `post-analysis-test-policy-orchestration` is fail-closed: do not mark completion when uncovered clauses remain with unresolved `action=add|modify` entries.
- Optional mode: `auto-commit` may be used only when explicitly requested; default is off.

## Traceability Gate for Document-to-Code Conversion

- Mandatory pre-code step: before generating or modifying source code from document analysis, read `ORAN/docs/feature_traceability_map.md`.
- Resolve implementation to existing Trace IDs (for example, `ORAN-FTM-001`) and map each change to its `Code Scope` and `Verification` fields.
- If no matching Trace ID exists, do not proceed to code generation; first propose or add a new traceability row in `ORAN/docs/feature_traceability_map.md` and get alignment.
- Include selected Trace IDs and source section references in the implementation summary for every document-driven code change.
- Treat missing traceability mapping as a blocker, not as a warning.
