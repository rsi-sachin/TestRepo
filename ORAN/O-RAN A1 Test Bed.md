# Project: O-RAN A1 Test Bed with Non-RT RIC and Near-RT RIC Simulators

## 1. Objective
Build a local-first, containerized test bed for O-RAN A1 interface validation between:
- Non-RT RIC simulator
- Near-RT RIC simulator

The platform shall support:
- A1 Policy Management (mandatory)
- A1 Enrichment Information (optional but planned)
- ML/model lifecycle stubs (optional)
- fault injection
- observability
- automated regression testing

The implementation should be primarily in Python unless there is a compelling reason to use another language.

---

## 2. Key Design Principles
1. API-first design
2. Contract-driven development using OpenAPI + JSON Schema
3. Deterministic simulation behavior
4. Full test automation
5. Local-first Docker Compose deployment
6. Easy extensibility for future A1/EI/ML features
7. Strong logging, metrics, and traceability
8. Clear separation between platform code and test scenarios

---

## 3. Target Architecture

### Components
1. nonrtric-sim
2. nearrtric-sim
3. a1-gateway
4. scenario-orchestrator
5. optional info-coordinator-sim
6. optional e2-effect-sim
7. shared-db
8. metrics stack

### Communication
- REST/JSON for A1 APIs
- HTTPS optional
- callback/webhook support optional
- async internal events via in-memory queues initially; Redis/Kafka later if required

---

## 4. Preferred Tech Stack

### Runtime
- Python 3.12+

### APIs
- FastAPI
- Uvicorn

### Models / Validation
- Pydantic
- jsonschema

### Testing
- pytest
- pytest-asyncio
- httpx
- Schemathesis

### Observability
- Prometheus
- OpenTelemetry
- structured JSON logging

### Packaging
- Docker
- Docker Compose

### Persistence
- SQLite for dev
- Postgres support via configuration

---

## 5. Repository Structure

repo-root/
  README.md
  docker-compose.yml
  .env.example
  docs/
    architecture.md
    api/
    scenarios/
  simulators/
    nonrtric_sim/
      app/
      tests/
      Dockerfile
    nearrtric_sim/
      app/
      tests/
      Dockerfile
    a1_gateway/
      app/
      tests/
      Dockerfile
    info_coordinator_sim/
      app/
      tests/
      Dockerfile
    e2_effect_sim/
      app/
      tests/
      Dockerfile
  harness/
    scenario_runner/
    common/
    reports/
  schemas/
    a1/
      policy_types/
      policy_instances/
      status/
      ei/
  testdata/
    topologies/
    policies/
    ei_jobs/
  scripts/
    start.sh
    stop.sh
    reset.sh
    seed.sh
  reports/

---

## 6. Functional Requirements

### 6.1 Non-RT RIC Simulator
Implement a simulator for Non-RT RIC behavior with the following capabilities:
- maintain inventory of one or more Near-RT RIC targets
- register supported policy types for each target
- create/update/delete policy instances
- retrieve and cache policy status
- retry failed operations according to configurable policy
- maintain correlation IDs for every transaction
- expose admin APIs for topology and state inspection
- support seeded scenarios through YAML or JSON

### 6.2 Near-RT RIC Simulator
Implement a simulator for Near-RT RIC behavior with:
- policy type registry
- policy instance store
- status generation engine
- validation of policy instance against policy type JSON schema
- support for accepted / rejected / partially enforced / unknown states
- support artificial conflict detection
- support restart recovery behavior
- support delayed apply behavior
- support per-policy-type custom handlers

### 6.3 A1 Gateway
Implement an A1 gateway / mediator layer with:
- northbound and southbound request tracing
- request/response validation
- configurable artificial faults:
  - delay
  - timeout
  - HTTP error injection
  - dropped response
  - duplicated delivery
  - malformed payload
- optional TLS / auth hooks
- metrics for request count, latency, failures, retries

### 6.4 Information / EI Simulator (Optional Phase 2)
Implement optional EI-related simulation:
- EI type advertisement
- producer registration
- information job creation/update/delete
- data delivery simulation
- stale/missing data scenarios

### 6.5 E2 Effect Simulator (Optional Phase 4)
Implement a simple effect sink that models:
- cells
- UE groups
- slices
- KPI trends
- application of policy to a simulated domain object
No real E2 protocol support is required at first.

---

## 7. Non-Functional Requirements

1. Every service shall expose:
   - /health
   - /ready
   - /metrics

2. Every request shall include:
   - request_id
   - correlation_id
   - actor
   - timestamp

3. Logs shall be:
   - structured JSON
   - queryable by correlation_id
   - environment-configurable log level

4. All service behavior must be deterministic when seed is provided.

5. All APIs must have OpenAPI specs generated or maintained.

---

## 8. Configuration Model

Use environment variables plus YAML config files.

Examples of config categories:
- service ports
- target endpoints
- retry count
- retry backoff
- auth mode
- TLS enabled
- policy conflict mode
- partial enforcement mode
- artificial latency
- persistence backend
- seed data paths

---

## 9. Data Models

Create explicit Pydantic models for:
- PolicyType
- PolicyInstance
- PolicyStatus
- NearRtRicDescriptor
- EnrichmentInfoType
- InformationJob
- FaultInjectionProfile
- ScenarioDefinition
- ServiceHealth
- MetricsSnapshot

Policy types and policy instances must support JSON Schema validation.

---

## 10. Behavior Rules

### 10.1 Policy Lifecycle
Support:
- register policy type
- list policy types
- get policy type
- create policy instance
- update policy instance
- delete policy instance
- list policy instances by type
- get policy status

### 10.2 Policy Status Values
Support at least:
- ACCEPTED
- REJECTED
- PENDING
- ENFORCED
- PARTIALLY_ENFORCED
- FAILED
- DELETED
- UNKNOWN

### 10.3 Conflict Rules
Provide a configurable rule engine that can simulate conflict if:
- same scope + contradictory target value
- precedence collision
- incompatible intent class
- resource exhaustion

### 10.4 Partial Enforcement
Simulate partial enforcement when:
- only subset of target cells accepted
- only subset of UE groups matched
- target capability gap
- stale topology

---

## 11. API Design Guidance

1. Generate OpenAPI docs automatically.
2. Keep payloads JSON-only.
3. Add version prefix:
   - /api/v1/...
4. Keep internal admin APIs separate:
   - /admin/v1/...
5. Keep scenario control APIs separate:
   - /scenario/v1/...

---

## 12. Test Strategy

### 12.1 Unit Tests
- model validation
- schema validation
- rule engine
- retry logic
- fault injector

### 12.2 Component Tests
- nonrtric-sim ↔ a1-gateway
- a1-gateway ↔ nearrtric-sim
- policy status transitions
- persistence recovery

### 12.3 End-to-End Tests
- happy path create/apply/status/delete
- invalid schema rejection
- unknown policy type
- Near-RT RIC unavailable then recovery
- delayed apply
- duplicate request/idempotency
- conflict scenario
- partial enforcement scenario
- authentication failure
- TLS failure (if enabled)

### 12.4 Fuzz / Contract Tests
Use Schemathesis against all public APIs.

### 12.5 Performance Tests
Measure:
- request latency
- rate under load
- concurrent policy operations
- recovery after restart
- stability during soak test

---

## 13. CI/CD Requirements

Create GitHub Actions for:
- lint
- unit tests
- component tests
- end-to-end tests
- Docker build
- security scan
- artifact upload
- test report export

Use:
- ruff
- black
- mypy
- pytest
- coverage

---

## 14. Deliverables

The agent must produce:
1. source code for all simulators
2. Dockerfiles
3. docker-compose.yml
4. OpenAPI specs
5. seed data
6. example scenarios
7. README with run instructions
8. architecture document
9. test reports folder
10. GitHub Actions workflow files

---

## 15. Acceptance Criteria

### Must Have
- system starts with one docker compose up
- policy type CRUD works
- policy instance CRUD works
- status retrieval works
- invalid policy rejected with clear error
- logs contain correlation IDs
- metrics exposed
- pytest suite runs successfully

### Should Have
- fault injection profiles
- partial enforcement
- conflict simulation
- restart recovery
- admin UI or simple CLI

### Nice to Have
- EI simulation
- E2 effect sink
- TLS/mTLS test mode
- Grafana dashboards

---

## 16. Implementation Order

1. common models + config library
2. nearrtric-sim
3. nonrtric-sim
4. a1-gateway
5. scenario orchestrator
6. docker-compose
7. tests
8. observability
9. EI simulator
10. E2 effect sink

---

## 17. Coding Standards
- type hints everywhere
- no hidden globals
- explicit interfaces for storage and transport
- dependency injection where practical
- avoid framework lock-in outside API layer
- keep business logic separate from REST handlers
- all externally visible behavior must be test-covered

---

## 18. Output Expectations for the Agent
When implementing:
1. create files incrementally
2. keep each service independently runnable
3. generate complete code, not pseudo-code
4. prefer simple and maintainable implementation over over-engineering
5. add TODO markers only for truly optional future work
6. include realistic sample policy schemas and scenario data

---

## 19. Example Initial Scenarios
1. Happy path policy lifecycle
2. Invalid schema rejection
3. Unknown policy type
4. Near-RT RIC down and recovery
5. Duplicate PUT / idempotency
6. Conflict between two policies
7. Partial enforcement across 3 cells
8. stale status after restart recovery
9. EI job created but producer unavailable
10. artificial latency and timeout

---

## 20. First Sprint Goal
Build an MVP that can:
- start all core services
- register one policy type
- create one policy instance
- return status transitions
- expose metrics and logs
- run 10 passing automated tests
``

