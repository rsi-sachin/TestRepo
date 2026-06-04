# TTS Demo Tool

A JavaFX desktop application for demonstrating Computaris TTS (Telecom Testing System) capabilities to internal engineers.

## Project Overview

**Phase 1** (Current): JavaFX desktop application  
**Phase 2** (Future): Spring Boot + Vanilla JS web application

## Technology Stack

- **Java**: 11+
- **Build Tool**: Maven
- **UI Framework**: JavaFX 17
- **JSON Processing**: Gson
- **Logging**: SLF4J + Logback
- **Testing**: JUnit 5, Mockito, TestFX

## Prerequisites

- **Java JDK**: 11 or higher
- **Maven**: 3.6 or higher
- **TTS Installation**: `C:\TTS` (required for demo execution)

## Project Structure

```
demo-tool/
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/com/tts/demo/
│   │   │   ├── MainApp.java              # Application entry point
│   │   │   ├── controller/               # JavaFX controllers
│   │   │   │   ├── MainController.java
│   │   │   │   └── RunHistoryController.java
│   │   │   ├── model/                    # Domain models
│   │   │   │   ├── Demo.java
│   │   │   │   ├── DemoConfig.java
│   │   │   │   └── RunResult.java
│   │   │   └── service/                  # Business logic
│   │   │       ├── DemoCatalog.java
│   │   │       ├── ConfigManager.java
│   │   │       ├── DemoRunner.java
│   │   │       └── LocalDateTimeAdapter.java
│   │   └── resources/
│   │       ├── fxml/                     # FXML layouts
│   │       │   ├── main.fxml
│   │       │   └── run-history.fxml
│   │       ├── css/                      # Stylesheets
│   │       │   └── styles.css
│   │       ├── data/                     # Demo catalog
│   │       │   └── demos.json
│   │       └── logback.xml               # Logging configuration
│   └── test/java/                        # Unit tests
│       └── com/tts/demo/
│           ├── model/
│           └── service/
├── docs/
│   └── requirements.txt                  # Full requirements
├── runs/                                 # Run history (generated)
└── logs/                                 # Application logs (generated)
```

## Building the Project

### Compile

```powershell
mvn clean compile
```

### Run Tests

```powershell
mvn test
```

### Package

```powershell
mvn clean package
```

This creates `target/demo-tool-1.0.0-SNAPSHOT.jar`

## Running the Application

### Using Maven

```powershell
mvn javafx:run
```

### Using JAR (with JavaFX modules)

```powershell
java --module-path "C:\path\to\javafx-sdk\lib" `
     --add-modules javafx.controls,javafx.fxml `
     -jar target/demo-tool-1.0.0-SNAPSHOT.jar
```

## Demo Catalog

The application loads demo scenarios from `src/main/resources/data/demos.json`.

### Demo Protocols (Phase 1)

| Protocol | JMX Templates | Reference Tests |
|----------|---------------|-----------------|
| **SIP/IMS** | `C:\TTS\bin\templates\tts\tts_sip_*.jmx` | `C:\TTS\docs\sip\reference_tests\` (9 files) |
| **Diameter** | `C:\TTS\bin\templates\tts\tts_diameter_*.jmx` | `C:\TTS\docs\diameter\reference_tests\` (11 files) |
| **RADIUS** | `C:\TTS\bin\templates\tts\tts_*radius*.jmx` | `C:\TTS\docs\radius_client\reference_tests\` (32 files) |

### Demo Complexity Levels

- **Basic**: Simple scenarios (e.g., single registration, basic authentication)
- **Intermediate**: Multi-step flows (e.g., authentication with charging)
- **Advanced**: Load testing, complex integrations (e.g., 100+ concurrent calls)

## Key Features

### REQ-006: Business-Level KPI Framing

All demo scenarios use **business-level language**, not technical protocol terms:

✅ **Correct**: "Simulate VoLTE Call Setup & Teardown"  
❌ **Incorrect**: "Run tts_sip_client.jmx"

### Demo Execution (REQ-008)

The tool invokes JMeter in non-GUI mode:

```
C:\TTS\bin\jmeter-n.cmd -n -t {jmx_path} -l {log_path} -J{param}={value}
```

- Live stdout/stderr streaming to UI
- Configurable parameters per demo
- 10-minute execution timeout

### Run History (REQ-009)

- Persisted as JSON files in `runs/` folder
- Metadata: scenario name, timestamps, duration, status, exit code
- Accessible via **View → Show Run History** menu

## Development Guidelines

1. **Do NOT modify anything under `C:\TTS\`** — read-only TTS installation
2. All new code goes under `C:\testrepo\demo-tool\`
3. Follow standard Maven project layout
4. UI labels must use business language (REQ-006)
5. Each demo in `demos.json` requires: id, title, description, outcome, protocol, complexity, jmxPath, defaultParams

## Testing

### Run All Tests

```powershell
mvn test
```

### Test Coverage

- **Model Tests**: `DemoTest`, `RunResultTest`, `DemoConfigTest`
- **Service Tests**: `DemoCatalogTest`, `ConfigManagerTest`, `DemoRunnerTest`
- **Integration**: TestFX for UI testing (future)

## Troubleshooting

### Issue: "TTS: Not Found" in status bar

**Solution**: Ensure TTS is installed at `C:\TTS` with `jmeter-n.cmd` present.

### Issue: Demo execution fails immediately

**Solution**: 
1. Validate TTS installation via **Help → Validate TTS Installation**
2. Check that JMX file exists at the specified path
3. Review logs in `logs/tts-demo-tool.log`

### Issue: No demos appear in catalog

**Solution**: Verify `src/main/resources/data/demos.json` exists and is valid JSON.

## Logging

Logs are written to:
- **Console**: INFO level
- **File**: `logs/tts-demo-tool.log` (DEBUG level for `com.tts.demo` package)
- **Rotation**: Daily, 30-day retention

## Future Enhancements (Phase 2)

- Spring Boot backend with REST API
- Vanilla JS/HTML web frontend
- Remote demo execution (no local TTS installation required)
- Enhanced reporting with graphs and metrics
- CI/CD integration demos (Jenkins)
- Additional protocols (HTTP, gRPC, MQTT)

## License

Internal use only - Computaris TTS Demo Tool

## Contact

For questions or issues, contact the TTS development team.
