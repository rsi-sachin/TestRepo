# Simulator Capability Matrix for TS 103 989 §4.2.1–4.2.2 Conformance Testing

**Document:** Simulator Capabilities Required for Conformance Test Coverage  
**Date:** 2026-06-30  
**Source:** TS 103 989 §4.2.1–4.2.2, TS 103 987 §5.2 (A1 Interface)  
**Scope:** A1-P Producer Simulator, A1-EI Producer Simulator (Phase 2)

---

## Overview

Conformance testing relies on simulators to provide deterministic, configurable behavior for A1 interface endpoints. This matrix defines the required capabilities for each simulator component to ensure test repeatability and comprehensive coverage.

---

## A1-P Producer Simulator Capabilities

### 1. HTTP Operation Configurability

**Requirement:** Simulator must support configurable HTTP method handling.

| Operation | Method | URI Pattern | Configurable Aspects | Test Purpose |
|---|---|---|---|---|
| Query Policy Types | GET | `/v1/policytypes` | Response status, body, headers | List availability |
| Query Policy Type | GET | `/v1/policytypes/{policyTypeId}` | Status (200/404), schema payload | Type existence/details |
| List Policy IDs | GET | `/v1/policytypes/{policyTypeId}/policies` | Status (200), policy ID list | Policy enumeration |
| Query Policy | GET | `/v1/policytypes/{policyTypeId}/policies/{policyId}` | Status (200/404), policy object | Policy retrieval |
| Create/Replace Policy | PUT | `/v1/policytypes/{policyTypeId}/policies/{policyId}` | Status (201/200), Location header, error response | Policy lifecycle |
| Delete Policy | DELETE | `/v1/policytypes/{policyTypeId}/policies/{policyId}` | Status (204/404), response body | Policy cleanup |
| Query Policy Status | GET | `/v1/policytypes/{policyTypeId}/policies/{policyId}/status` | Status (200/404), status object | Policy state query |

---

### 2. HTTP Status Code Configurability

**Requirement:** Simulator must return configurable HTTP status codes for each operation.

| Status Code | Use Case | Configuration | Example |
|---|---|---|---|
| 200 OK | Successful GET/PUT (update existing) | Default for successful queries and updates | GET /policies returns 200 + array |
| 201 Created | Successful PUT (create new resource) | Configurable per policy type or per test | PUT /policies (new) returns 201 + Location |
| 204 No Content | Successful DELETE | Configurable per test scenario | DELETE /policies returns 204 (empty body) |
| 400 Bad Request | Invalid request (schema validation failure) | Triggered by invalid JSON body, missing fields, etc. | PUT /policies with malformed JSON returns 400 |
| 404 Not Found | Resource not found | Configurable to simulate missing policy type or policy | GET /policytypes/unknown returns 404 |
| 500 Internal Server Error | Server error (for negative testing) | Configurable to simulate backend failure | Simulate transient errors for retry testing |
| 503 Service Unavailable | Service temporarily down | Configurable for resilience testing | Simulate maintenance windows |

---

### 3. HTTP Header Configurability

**Requirement:** Simulator must include configurable HTTP response headers.

| Header | Value | Configurable | Purpose |
|---|---|---|---|
| Content-Type | `application/json` | Default; configurable to test invalid types | Response format negotiation |
| Location | `/v1/policytypes/{id}/policies/{id}` | Configurable per 201 response | Resource location (create) |
| Content-Length | Integer bytes | Auto-calculated; can be overridden to test partial responses | Payload size metadata |
| Retry-After | Integer seconds or HTTP-date | Configurable for rate-limiting scenarios | Backoff guidance for clients |
| X-Trace-ID | UUID or string | Configurable per request | Correlation and debugging |
| X-RIC-Request-ID | String | Configurable per test | Non-RT RIC correlation |

---

### 4. Request Body Validation

**Requirement:** Simulator must validate incoming policy JSON against configurable schema.

| Validation Rule | Behavior | Configurable Scenarios |
|---|---|---|
| Schema Enforcement | Validate request body matches PolicyObject schema for the policyTypeId | Accept schema per policy type; reject invalid fields |
| Required Fields | `policyTypeId`, `policyId`, `policyData` must be present | Allow selective requirement per test |
| Type Checking | Strings must be strings, objects must be objects, etc. | Strict or lenient mode per test |
| Nested Schema | Validate `policyData` JSON against policy-type-specific schema | Per-type schema storage and validation |
| Enum Validation | If policy type specifies enum values, enforce them | Configure allowed values per policy type |

---

### 5. Response Body Configurability

**Requirement:** Simulator must generate configurable response payloads.

| Response Type | Template Fields | Configurable Aspects |
|---|---|---|
| PolicyTypeObject | `policyTypeId`, `schemaVersion`, `schema` (JSON Schema) | Return schema as-configured, add/remove fields for negative tests |
| PolicyObject | `policyTypeId`, `policyId`, `policyData` | Echo back request or return modified version |
| PolicyStatusObject | `status` (e.g., "UNDEFINED"), `statusReason` | Override status per policy type or per test |
| ProblemDetails | `type`, `title`, `status`, `detail`, `instance` | Configurable error messages for error scenarios |

---

### 6. Latency and Timeout Simulation

**Requirement:** Simulator must support configurable request/response delays.

| Scenario | Configuration | Purpose |
|---|---|---|
| Fixed Delay | Add N milliseconds to every response | Test client timeout handling |
| Variable Delay | Add random delay between min/max ms | Simulate realistic network jitter |
| Timeout Trigger | Delay > client timeout threshold | Test timeout recovery and retry logic |
| Partial Response | Send headers, delay, then send body | Test streaming and multi-part handling |

---

### 7. Failure Mode Simulation

**Requirement:** Simulator must inject configurable failure modes for negative testing.

| Failure Mode | Configuration | Test Purpose |
|---|---|---|
| Malformed JSON | Return invalid JSON body on demand | Test JSON parsing error handling |
| Missing Content-Type | Omit Content-Type header | Test content negotiation handling |
| Wrong Status Code | Return 200 instead of 201 on create | Test status code validation |
| Missing Required Field | Omit required field from response | Test schema validation |
| Oversized Response | Return response exceeding size limit | Test buffer overflow handling |
| Connection Drop | Terminate connection mid-response | Test partial response handling |
| Slow Response | Inject multi-second delays | Test timeout and retry logic |

---

### 8. Request/Response Logging

**Requirement:** Simulator must capture and log all HTTP transactions.

| Log Aspect | Captured Data | Format | Purpose |
|---|---|---|---|
| Request Metadata | Timestamp, method, URI, client IP | JSON | Transaction traceability |
| Request Headers | All headers | JSON | Header validation in test |
| Request Body | Full JSON payload (if applicable) | JSON | Payload validation in test |
| Response Metadata | Timestamp, status code, response time | JSON | Performance and correctness |
| Response Headers | All headers | JSON | Header validation in test |
| Response Body | Full JSON payload | JSON | Response validation in test |
| Verdict Trace | Pass/fail reason linked to HTTP exchange | JSON | Evidence for test verdict |

---

## A1-EI Producer Simulator Capabilities (Phase 2)

### 1. Notification Receipt and Response

**Requirement:** A1-EI Producer must act as HTTP **Client** to send notifications; Non-RT RIC (A1-EI Consumer) acts as **Server** to receive.

| Capability | Configuration | Purpose |
|---|---|---|
| Outbound HTTP POST | Issue POST to `notificationDestination` URI | Send EI notifications to consumer |
| Notification Payload | JSON EI status/update | Configurable per test scenario |
| Response Status Acceptance | Accept 202 (Accepted) or 200 (OK) from consumer | Validate consumer acknowledgment |
| Retry on Failure | Configurable retry strategy (exponential backoff) | Test consumer resilience |
| Notification Logging | Capture all outbound notifications | Audit trail for test verification |

### 2. Configurable EI Type and State

| Capability | Configuration | Purpose |
|---|---|---|
| EI Type Registration | Advertise configurable EI types | Support multi-type test scenarios |
| EI Type Schema | Define JSON Schema per EI type | Validate EI data conform to type |
| EI State Mutation | Simulate state changes (e.g., available → unavailable) | Test consumer reaction to state changes |
| EI Data Updates | Send updated EI data to subscribers | Test change notification mechanism |

---

## Conformance Test Scenarios Enabled by These Capabilities

### Positive Test Cases
- Simulator returns 200/201/204 as specified
- Simulator validates request schema and accepts valid payloads
- Simulator includes required headers and fields
- Simulator enforces policy type existence

### Negative Test Cases
- Simulator returns 400 for invalid JSON
- Simulator returns 404 for nonexistent policy type
- Simulator returns 500 to test client error handling
- Simulator introduces latency to test timeout handling

### Boundary and Parameter Tests
- Simulator accepts policy ID at max length
- Simulator rejects policy ID exceeding max length
- Simulator handles concurrent requests
- Simulator recovers from connection drop

### Performance Tests
- Simulator measures response latency (P50, P95, P99)
- Simulator measures throughput (ops/sec)
- Simulator logs performance degradation under load

---

## Implementation Checklist

- [ ] A1-P Producer simulator supports all 7 operations (1.1–1.7) with configurable status codes
- [ ] Simulator validates request JSON against configurable schema
- [ ] Simulator logs all HTTP transactions (request/response) in JSON format
- [ ] Simulator supports latency injection (fixed and variable delays)
- [ ] Simulator supports failure mode injection (malformed responses, connection drops)
- [ ] A1-EI Producer simulator (Phase 2) can send configurable notifications
- [ ] Conformance test harness can configure simulator behavior per test case
- [ ] Test evidence includes simulator logs, request/response pairs, and latency metrics

---

## Notes

- All capabilities must be configurable **per test case** to support deterministic, repeatable conformance testing.
- Simulator behavior is captured in JSON logs for full traceability in test verdict assignment.
- Phase 1 focus: A1-P Producer simulator. Phase 2: A1-EI Producer and Consumer simulators.
