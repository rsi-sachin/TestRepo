# ORAN TODO Index - Parallel Feature Tracks

Project: Extend demo-web with O-RAN A1 test generation and simulator creation capabilities
Last Updated: June 2026
Tracking Mode: ORAN-only split with 2 feature TODO files

## Feature Files

- [Feature 1 TODO - Specification Ingestion and Test Plan JSON](TODO-F1-spec-ingestion.md)
- [Feature 2 TODO - Component Simulator via TDD](TODO-F2-simulator-tdd.md)

## Feature Linkage

- Feature 1 is upstream and produces normalized JSON test plan data with test-case, component, and module targets.
- Feature 2 is downstream and must select simulator targets only from Feature 1 outputs.
- Dependency flow: Feature 1 output -> Feature 2 target selection -> TDD simulator implementation.

---

## A1 Test Bed MVP - Pickup TODO

**Objective:** Build a local-first, containerized O-RAN A1 test bed under `ORAN/a1-testbed/` with standalone simulators and a demo-web integration tab.

### Decisions Locked
- [x] Keep all new source code in `ORAN/a1-testbed/`
- [x] Hybrid integration: standalone services + demo-web frontend tab
- [x] A1 interface target: O-RAN A1-P v4.0 (`/A1-P/v2/...`)
- [x] Start with First Sprint MVP scope
- [x] Policy schemas source: ORAN-SC style samples
- [x] CI/CD deferred to later phase

### MVP Scope
- [ ] 3 services: `nearrtric-sim` (8081), `nonrtric-sim` (8080), `a1-gateway` (8082)
- [ ] One-command startup via Docker Compose
- [ ] Policy type and policy instance CRUD
- [ ] Status transitions and status retrieval
- [ ] Fault injection + request tracing + metrics
- [ ] 10 automated tests passing
- [ ] demo-web "A1 Test Bed" tab for health/types/create/status

### Phase A1-1: Foundation
- [ ] Create `ORAN/a1-testbed/` root structure
  - [ ] `docker-compose.yml`
  - [ ] `.env.example`
  - [ ] `scripts/start.sh`, `scripts/stop.sh`, `scripts/reset.sh`, `scripts/seed.sh`
- [ ] Add schemas in `ORAN/a1-testbed/schemas/a1/policy_types/`
  - [ ] `ORAN_QoSTarget_0.2.0.json`
  - [ ] `ORAN_TrafficSteeringPreference_0.2.0.json`
- [ ] Add sample policy instances in `ORAN/a1-testbed/schemas/a1/policy_instances/`
- [ ] Add seed test data in `ORAN/a1-testbed/testdata/`
  - [ ] `topologies/simple_topology.json`
  - [ ] `policies/happy_path_policy.json`
- [ ] Add shared harness helpers in `ORAN/a1-testbed/harness/common/`
  - [ ] `models.py`
  - [ ] `http_client.py`

### Phase A1-2: Near-RT RIC Simulator (`ORAN/a1-testbed/simulators/nearrtric_sim`)
- [ ] `app/models/policy.py` (PolicyType, PolicyInstance, PolicyStatus, StatusValue enum)
- [ ] `app/services/policy_store.py` (thread-safe in-memory store)
- [ ] `app/services/validator.py` (jsonschema validation)
- [ ] `app/services/status_engine.py` (deterministic transitions)
- [ ] `app/routers/a1_pm.py`
  - [ ] `GET /A1-P/v2/policytypes`
  - [ ] `GET /A1-P/v2/policytypes/{ptId}`
  - [ ] `GET /A1-P/v2/policytypes/{ptId}/policies`
  - [ ] `PUT /A1-P/v2/policytypes/{ptId}/policies/{pId}`
  - [ ] `GET /A1-P/v2/policytypes/{ptId}/policies/{pId}`
  - [ ] `DELETE /A1-P/v2/policytypes/{ptId}/policies/{pId}`
  - [ ] `GET /A1-P/v2/policytypes/{ptId}/policies/{pId}/status`
- [ ] `app/routers/admin.py`
  - [ ] `POST /admin/v1/policytypes`
  - [ ] `GET /admin/v1/state`
  - [ ] `POST /admin/v1/scenario`
- [ ] `app/main.py` with `/health`, `/ready`, `/metrics`
- [ ] `Dockerfile` and `requirements.txt`

### Phase A1-3: Non-RT RIC Simulator (`ORAN/a1-testbed/simulators/nonrtric_sim`)
- [ ] `app/models/nearrtic.py` (NearRtRicDescriptor, PolicyEntry, RicStatus)
- [ ] `app/services/ric_registry.py`
- [ ] `app/services/a1_client.py` (headers: request_id, correlation_id, actor)
- [ ] `app/services/retry.py` (exponential backoff)
- [ ] `app/routers/admin.py`
  - [ ] `POST /admin/v1/nearrtics`
  - [ ] `GET /admin/v1/nearrtics`
  - [ ] `POST /admin/v1/policies`
  - [ ] `DELETE /admin/v1/policies/{pId}`
  - [ ] `GET /admin/v1/policies`
- [ ] `app/main.py`, `Dockerfile`, `requirements.txt`

### Phase A1-4: A1 Gateway (`ORAN/a1-testbed/simulators/a1_gateway`)
- [ ] `app/middleware/tracing.py` (request/correlation/actor/timestamp)
- [ ] `app/middleware/faults.py` (delay, timeout, error injection, dropped response)
- [ ] `app/services/metrics.py` (Prometheus counters + histograms)
- [ ] `app/routers/proxy.py` (forward `/A1-P/v2/...` to Near-RT sim)
- [ ] `app/routers/admin.py`
  - [ ] `GET /admin/v1/config`
  - [ ] `POST /admin/v1/faults`
  - [ ] `DELETE /admin/v1/faults`
- [ ] `app/main.py`, `Dockerfile`, `requirements.txt`

### Phase A1-5: Harness Tests (`ORAN/a1-testbed/harness`)
- [ ] Add `tests/conftest.py` fixtures + seeding
- [ ] Add `requirements.txt` (pytest, pytest-asyncio, httpx)
- [ ] Add tests (10):
  - [ ] happy path lifecycle
  - [ ] invalid schema rejection
  - [ ] unknown policy type
  - [ ] unavailability + recovery
  - [ ] idempotent PUT
  - [ ] conflict scenario
  - [ ] partial enforcement
  - [ ] delayed status transitions
  - [ ] metrics exposure
  - [ ] correlation ID propagation

### Phase A1-6: demo-web Integration (hybrid)
- [ ] Update `demo-web/frontend/templates/index.html` with "A1 Test Bed" tab
- [ ] Add `demo-web/frontend/static/js/a1testbed.js`
  - [ ] service health checks
  - [ ] policy type loading
  - [ ] create policy call
  - [ ] status polling
- [ ] Add `demo-web/frontend/static/css/a1testbed.css`
- [ ] Update `demo-web/frontend/static/js/app.js` to initialize A1 tab
- [ ] Update `demo-web/backend/app/config.py` with `a1_gateway_url`

### Phase A1-7: Architecture JSON to Test Modules
- [ ] Pick up `ORAN/docs/figure_4_1_2_1_oran_entities.json` and generate test module scaffolding around the interfaces and components in the diagram
  - [ ] Create a test module map for `SMO`, `Non-RT RIC`, `Near-RT RIC`, `rApps`, `xApps`, `O-CU-CP`, `O-CU-UP`, `O-DU`, `O-RU`, and `O-Cloud`
  - [ ] Create interface-focused test modules for `A1`, `O1`, `O2`, and `E2`
  - [ ] Separate real implementation targets from stubbed components using the JSON `mvp_execution_profile`
  - [ ] Add shared fixtures/mocks for component interactions, message flow assertions, and interface contract checks
  - [ ] Keep the generated tests aligned with the A1 test-bed MVP scope and the SMO / Non-RT RIC implementation path

### Acceptance Checklist (Sprint MVP)
- [ ] `docker compose up` starts all 3 services cleanly
- [ ] `/health` available on ports 8080, 8081, 8082
- [ ] Register one policy type and create one policy instance
- [ ] Status transitions observable and retrievable
- [ ] Invalid policy rejected with clear validation errors
- [ ] Logs include correlation IDs
- [ ] `/metrics` exposed on all services
- [ ] Harness test suite passes with 10 tests
- [ ] demo-web A1 tab shows service health and policy lifecycle flow

### Open Decision for Test 04
- [ ] Choose outage simulation method for recovery test:
  - [ ] A) A1 Gateway fault injection (recommended for deterministic testing)
  - [ ] B) Stop/restart Near-RT container during test

#### Backend Implementation ✅

## Feature Status Snapshot

| Feature | Status |
|---|---|
| Feature 1: Specification Ingestion and Test Plan JSON | IN PROGRSES |
| Feature 2: Component Simulator via TDD | NOT STARTED |

## Notes

- This is a compact index-only file.
- Detailed legacy sections have been moved into the feature TODO files.
