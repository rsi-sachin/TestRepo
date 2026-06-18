# Migration Plan: JavaFX Desktop → Web Application

## Overview

This document outlines the parallel migration strategy from the JavaFX desktop application to a browser-based web application.

## Migration Strategy: Parallel Development

**Approach**: Build web application alongside desktop app, maintain feature parity, eventual cutover.

**Benefits**:
- Desktop app remains functional during migration
- Incremental feature delivery
- Lower risk
- Time to validate web approach
- Users can choose preferred interface

**Timeline**: Phased approach over 8-12 weeks

## Phase Breakdown

### Phase 1: Foundation (Weeks 1-2) ✅ **COMPLETED**

**Backend**:
- ✅ FastAPI project structure
- ✅ Pydantic models (Demo, ExecutionResult, TrafficProfile, etc.)
- ✅ REST API endpoints (demos, execution, history)
- ✅ WebSocket infrastructure
- ✅ Service layer stubs (DemoService, ExecutionService)

**Frontend**:
- ✅ HTML structure with tabs (Demos, Execution, Traffic, History)
- ✅ CSS styling with responsive layout
- ✅ JavaScript app skeleton
- ✅ API integration code
- ✅ WebSocket connection handling

**Testing**:
- ✅ Playwright configuration
- ✅ Initial E2E tests (navigation, demo selection)

**Status**: Foundation complete, ready for feature implementation

---

### Phase 2: Core Features (Weeks 3-4) **NEXT**

**Backend**:
- [ ] Complete DemoService implementation
  - Load demos.json from Java project
  - Implement filtering logic
  - Validate JMX file paths
- [ ] Complete ExecutionService implementation
  - Build JMeter command with parameters
  - Spawn subprocess for JMeter
  - Stream console output via WebSocket
  - Monitor process completion
- [ ] Implement JTL file parser
  - Real-time file tailing
  - Parse CSV format
  - Extract SIP messages
  - Calculate statistics

**Frontend**:
- [ ] Demo list rendering from API
- [ ] Demo detail view with parameters
- [ ] Search and filter implementation
- [ ] Console output display
- [ ] Basic statistics display

**Testing**:
- [ ] E2E test: Load and display demos
- [ ] E2E test: Execute demo end-to-end
- [ ] Unit tests for services

**Deliverable**: Users can browse demos, view details, and execute basic demos with console output.

---

### Phase 3: Real-Time Visualization (Weeks 5-6)

**Backend**:
- [ ] SIP message parser from JTL
- [ ] WebSocket broadcasting for:
  - Console output lines
  - SIP messages
  - Statistics updates
- [ ] Real-time statistics calculator

**Frontend**:
- [ ] Mermaid.js sequence diagram rendering
  - Parse SIP messages to Mermaid syntax
  - Real-time diagram updates
  - Actor positioning (UE, P-CSCF, S-CSCF, HSS, etc.)
- [ ] Scrolling call flow panel
- [ ] Live statistics updates

**Testing**:
- [ ] E2E test: Verify real-time diagram updates
- [ ] E2E test: Statistics update during execution
- [ ] WebSocket message handling tests

**Deliverable**: Real-time call flow visualization matches desktop app functionality.

---

### Phase 4: Traffic Generation (Weeks 7-8)

**Backend**:
- [ ] TrafficProfile → JMeter properties converter
- [ ] Traffic generation execution
- [ ] Per-node statistics tracking
- [ ] Real-time traffic stats streaming

**Frontend**:
- [ ] Traffic configuration form
  - Sliders for concurrent calls, total calls, ramp-up
  - Failure rate and scenario selection
- [ ] Plotly.js multi-line chart
  - Dynamic series per network node
  - Real-time data updates
  - Last 60 seconds window
- [ ] Live traffic statistics display

**Testing**:
- [ ] E2E test: Configure and start traffic generation
- [ ] E2E test: Verify per-node chart rendering
- [ ] E2E test: Stop traffic generation
- [ ] Performance test: High-volume traffic (100+ threads)

**Deliverable**: Full traffic generation feature with per-node visualization.

---

### Phase 5: History & Advanced Features (Weeks 9-10)

**Backend**:
- [ ] History service implementation
  - Load run history from JSON files
  - Filter and pagination
  - Statistics aggregation
- [ ] Export capabilities (CSV, JSON)
- [ ] Run comparison API

**Frontend**:
- [ ] History list rendering
- [ ] Run details view
- [ ] Historical statistics charts
- [ ] Export buttons
- [ ] Run comparison UI

**Testing**:
- [ ] E2E test: View run history
- [ ] E2E test: Load run details
- [ ] E2E test: Export data

**Deliverable**: Complete history management, on par with desktop app.

---

### Phase 6: Polish & Performance (Weeks 11-12)

**Backend**:
- [ ] Performance optimization
  - Connection pooling
  - Caching demo catalog
  - Efficient JTL parsing
- [ ] Error handling and logging
- [ ] Rate limiting
- [ ] Health checks and monitoring

**Frontend**:
- [ ] UI polish and animations
- [ ] Responsive design (mobile/tablet)
- [ ] Accessibility (ARIA labels, keyboard navigation)
- [ ] Dark mode
- [ ] Loading states and spinners
- [ ] Error notifications

**Testing**:
- [ ] Full E2E test coverage (>80%)
- [ ] Performance tests (load testing, stress testing)
- [ ] Accessibility tests
- [ ] Cross-browser testing (Chrome, Firefox, Edge, Safari)

**Documentation**:
- [ ] User guide
- [ ] API documentation
- [ ] Deployment guide
- [ ] Migration guide for users

**Deliverable**: Production-ready web application.

---

## Code Reuse Strategy

### 100% Reusable (Java → Python Port)

**Models**: Direct mapping
- `Demo.java` → `Demo` (Pydantic)
- `TrafficProfile.java` → `TrafficProfile` (Pydantic)
- `TrafficStats.java` → `TrafficStats` (Pydantic)
- `ConformanceScenario.java` → `ConformanceScenario` (Enum)

**Business Logic**: Algorithmic reuse
- `DemoRunner.buildJMeterCommand()` → `ExecutionService._build_jmeter_command()`
- `DemoRunner.parseJtlLine()` → Python JTL parser
- `RcaAnalyzer.analyze()` → Python RCA analyzer

**Data Files**: Shared
- `demos.json`: Used directly from Java project path
- JMX templates: Reference same `C:\TTS` files
- Run history: Share `demo-tool/runs/` directory

### 0% Reusable (Complete Rewrite)

**Presentation Layer**:
- JavaFX controllers → REST API + WebSocket handlers
- FXML files → HTML templates
- Canvas components → SVG/Mermaid.js
- Event handlers → JavaScript event listeners

**Threading Model**:
- `Platform.runLater()` → WebSocket callbacks
- JavaFX Application Thread → JavaScript main thread
- Background threads → Python `asyncio` tasks

## Testing Strategy

### Desktop App (Existing)
- JUnit tests continue to run
- No changes required
- Validates service layer behavior

### Web App (New)

**Unit Tests** (pytest):
- Service layer functions
- API endpoint logic
- WebSocket message handling
- Data transformations

**E2E Tests** (Playwright):
- User workflows (browse → select → execute → view results)
- Real-time updates
- WebSocket connectivity
- UI interactions

**Integration Tests**:
- API + JMeter execution
- JTL file parsing
- WebSocket broadcasting

**Performance Tests**:
- Concurrent demo executions
- High-volume traffic generation
- WebSocket message throughput
- Memory usage under load

## Deployment Considerations

### Development
- Run desktop and web side-by-side
- Share TTS installation (`C:\TTS`)
- Share demo catalog and run history

### Production Options

**Option 1: Desktop + Web Server (Recommended for Phase 2)**
- Desktop app for engineers (existing workflow)
- Web app for remote access and demos
- Both use same TTS backend

**Option 2: Web-Only (Future)**
- Deploy FastAPI on Linux server
- Install TTS/JMeter on server
- Serve via reverse proxy (Nginx)
- HTTPS with authentication

**Option 3: Containerized**
- Docker image with Python + TTS + JMeter
- Kubernetes for scaling
- Cloud deployment (Azure, AWS)

## User Migration Path

### Phase 1: Parallel Operation (Weeks 1-8)
- Desktop app: Primary interface
- Web app: Preview/testing
- Users opt-in to try web version

### Phase 2: Feature Parity (Weeks 9-12)
- Web app has all desktop features
- Gradual user migration
- Desktop app still available

### Phase 3: Web Primary (Month 4+)
- Web app becomes primary
- Desktop app maintenance mode
- Users encouraged to switch

### Phase 4: Desktop Deprecation (Month 6+)
- Web app only
- Desktop app sunset
- Migration complete

## Risk Mitigation

### Technical Risks

**Risk**: WebSocket connection instability
**Mitigation**: Implement reconnection logic, heartbeat pings, fallback to polling

**Risk**: Browser compatibility issues
**Mitigation**: Test on major browsers (Chrome, Firefox, Edge), use standard APIs, polyfills if needed

**Risk**: Performance degradation with large JTL files
**Mitigation**: Streaming parsing, data pagination, client-side filtering

**Risk**: JMeter subprocess management complexity
**Mitigation**: Use proven libraries (subprocess, psutil), comprehensive error handling, process cleanup

### User Adoption Risks

**Risk**: Resistance to change from desktop users
**Mitigation**: Parallel operation period, training, highlight web benefits (remote access, no install)

**Risk**: Missing features in initial web version
**Mitigation**: Phased rollout, gather feedback, prioritize high-value features

## Success Metrics

### Technical
- [ ] 100% feature parity with desktop app
- [ ] <2s page load time
- [ ] <100ms WebSocket message latency
- [ ] >80% E2E test coverage
- [ ] Zero data loss during executions

### User
- [ ] 80% user satisfaction score
- [ ] <5 minutes to complete first demo (new users)
- [ ] 50%+ users migrated to web within 3 months

## Next Steps

1. **Week 1-2**: Complete Phase 2 backend implementation (DemoService, ExecutionService)
2. **Week 3**: Implement JTL parsing and WebSocket streaming
3. **Week 4**: Build demo list UI and execution flow
4. **Week 5-6**: Add call flow visualization (Mermaid.js)
5. **Week 7-8**: Implement traffic generation with Plotly.js charts

## Questions for Stakeholders

1. **Timeline**: Is 12-week timeline acceptable, or need faster delivery?
2. **Deployment**: Prefer on-premise server or cloud deployment?
3. **Authentication**: Need user authentication or open access?
4. **Database**: When to migrate from file-based to database persistence?
5. **Features**: Any desktop app features we can skip for web version?

---

**Document Status**: Phase 1 Complete (May 14, 2026)
**Next Update**: After Phase 2 completion (estimated Week 4)
