# DUT Readiness Checklist for TS 103 989 §4.2.2 Conformance Setup

**Document:** Non-RT RIC DUT Readiness Checks  
**Scope:** Verify Non-RT RIC is ready for conformance testing  
**Date:** 2026-06-30  
**Source:** TS 103 989 §4.2.2 (General conformance setup)

---

## Overview

Before starting conformance test execution, the Device Under Test (DUT, Non-RT RIC) must be verified for readiness across role-based, connectivity, and schema-compliance dimensions.

---

## Pre-Flight Checklist

### 1. Role-Based Configuration

**Objective:** Verify DUT supports required A1 roles.

| Check | Expected Behavior | Verification Command | Status |
|---|---|---|---|
| A1-P Consumer Support | Non-RT RIC advertises as A1-P Consumer | Query Non-RT RIC config: `curl http://<NR-RIC>:config/a1-roles` | [ ] |
| A1-EI Consumer Support | Non-RT RIC advertises as A1-EI Consumer (Phase 2) | Query Non-RT RIC config: `curl http://<NR-RIC>:config/a1-roles` | [ ] |
| Role Documentation | DUT documentation specifies active roles | Review DUT architecture document | [ ] |

---

### 2. Policy Type Preconditions (A1-P Consumer)

**Objective:** Verify at least one policy type is registered for A1-P testing.

| Check | Expected Behavior | Verification Command | Status |
|---|---|---|---|
| Policy Type 1 Registered | At least 1 policy type exists | `curl http://<A1-P-Producer>/v1/policytypes` → HTTP 200 + `[{policyTypeId: "..."}]` | [ ] |
| Policy Type 2 (Optional) | Second policy type for parametric testing | Same as above | [ ] |
| Policy Type Schema Valid | Policy type JSON Schema conforms to TS 103 987 | `curl http://<A1-P-Producer>/v1/policytypes/{policyTypeId}` → HTTP 200 + valid JSON Schema | [ ] |
| Policy Type Ownership | Non-RT RIC owns policy types (or agrees to pre-registered types) | Verify in DUT documentation or via API | [ ] |

---

### 3. Enrichment Information Type Preconditions (A1-EI Consumer) — Phase 2

**Objective:** Verify at least one EI type is registered for A1-EI testing.

| Check | Expected Behavior | Verification Command | Status |
|---|---|---|---|
| EI Type 1 Registered | At least 1 EI type exists | `curl http://<A1-EI-Producer>/v1/eitypes` → HTTP 200 + `[{eiTypeId: "..."}]` | [ ] |
| EI Type Schema Valid | EI type JSON Schema conforms to TS 103 987 | `curl http://<A1-EI-Producer>/v1/eitypes/{eiTypeId}` → HTTP 200 + valid JSON Schema | [ ] |

---

### 4. Endpoint Accessibility

**Objective:** Verify all A1 endpoints are reachable from the test environment.

| Endpoint | Role | Port | Protocol | Check | Status |
|---|---|---|---|---|---|
| A1-P Producer | Producer | 8081 (default) | HTTP | `curl http://<A1-P-Producer>:8081/v1/policytypes` → HTTP 200 | [ ] |
| A1-P Consumer (Non-RT RIC) | Consumer | 8082 (config) | HTTP | `curl http://<Non-RT-RIC>:8082/config/a1-consumer` → HTTP 200 | [ ] |
| A1-EI Producer | Producer (Phase 2) | 8083 (default) | HTTP | `curl http://<A1-EI-Producer>:8083/v1/eitypes` → HTTP 200 | [ ] |
| A1-EI Consumer (Non-RT RIC) | Consumer (Phase 2) | 8082 (config) | HTTP | `curl http://<Non-RT-RIC>:8082/config/a1-consumer` → HTTP 200 | [ ] |

---

### 5. Response Schema Compliance

**Objective:** Verify DUT responses conform to TS 103 987 representation objects.

| Response Type | Expected Schema | Verification Method | Status |
|---|---|---|---|
| PolicyTypeObject | `{ "policyTypeId": "...", "schemaVersion": "...", ...schema... }` | Schema validation against TS 103 987 §5.2.2.3 | [ ] |
| PolicyObject | `{ "policyTypeId": "...", "policyId": "...", "policyData": {...} }` | Schema validation against TS 103 987 §5.2.2.3 | [ ] |
| PolicyStatusObject | `{ "status": "...", "statusReason": "..." }` | Schema validation against TS 103 987 §5.2.2.4 | [ ] |
| ProblemDetails | `{ "type": "...", "title": "...", "status": ..., "detail": "..." }` | RFC 7807 compliance check | [ ] |

---

### 6. HTTP Compliance

**Objective:** Verify DUT handles HTTP semantics correctly.

| HTTP Feature | Expected Behavior | Verification Command | Status |
|---|---|---|---|
| Content-Type Header | Response includes `Content-Type: application/json` | `curl -i http://<endpoint>/v1/policytypes` → check headers | [ ] |
| Status Codes | 200 (success), 201 (created), 204 (no content), 400 (bad request), 404 (not found) | Run negative test; verify status code mapping | [ ] |
| Location Header (201) | PUT /policies endpoint returns `Location: /v1/policytypes/{id}/policies/{id}` | Create policy; verify Location header on 201 | [ ] |
| Timeout Handling | DUT responds within configurable timeout (default: 10s) | Measure response latency; compare against threshold | [ ] |

---

### 7. Firewall and Network Policies

**Objective:** Verify network paths are open for conformance testing.

| Path | Direction | Protocol | Port | Check | Status |
|---|---|---|---|---|---|
| Test Client → A1-P Producer | Inbound to Producer | TCP | 8081 | Firewall allows port 8081 | [ ] |
| Test Client → A1-EI Producer | Inbound to EI Producer | TCP | 8083 | Firewall allows port 8083 | [ ] |
| Non-RT RIC → A1-P Producer | Inbound to Producer | TCP | 8081 | Firewall allows port 8081 | [ ] |
| A1-P Producer → Non-RT RIC (notifications) | Inbound to Consumer | TCP | 8082 | Firewall allows port 8082 for callbacks | [ ] |

---

### 8. Performance Baseline

**Objective:** Capture baseline performance metrics for conformance tests.

| Metric | Target | Measurement | Status |
|---|---|---|---|
| Policy Query Latency | < 100ms (P95) | Run 10 GET /policytypes queries; compute P95 | [ ] |
| Policy Create Latency | < 200ms (P95) | Run 10 PUT /policies operations; compute P95 | [ ] |
| Throughput | ≥ 10 ops/sec | Run sustained load test; measure ops/sec | [ ] |
| Error Rate (under load) | < 1% | Run load test; measure failed operations | [ ] |

---

## Readiness Sign-Off

| Role | Name | Date | Signature |
|---|---|---|---|
| DUT Owner | [Non-RT RIC Team] | [ ] | [ ] |
| Test Engineer | [ORAN Test Team] | [ ] | [ ] |
| Conformance Lead | [ORAN Conformance Lead] | [ ] | [ ] |

---

## Remediation Guide

**If any check fails:**

1. **Policy Type Issue:** Register missing policy types using Non-RT RIC admin CLI or API
2. **Endpoint Unreachable:** Verify firewall rules, DNS resolution, and endpoint URLs
3. **Schema Mismatch:** Compare actual response against TS 103 987 §5.2.2 representation objects; file spec conflict if applicable
4. **Performance Degradation:** Check system resource utilization (CPU, memory, network); adjust load/timeout as needed
5. **HTTP Compliance Issue:** Review HTTP handler implementation; consult TS 103 987 HTTP mapping table (§5.2.3–5.2.4)

---

## Notes

- All checks must pass before starting conformance test execution.
- Baseline performance metrics serve as regression reference for future test runs.
- Keep this checklist updated as DUT configuration changes or new A1 roles are added.
