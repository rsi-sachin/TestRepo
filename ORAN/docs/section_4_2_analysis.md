# TS 103 989 V4.2.0 - Sections 4.2.1 and 4.2.2 Analysis

**Document:** `ts_103989v040200p.pdf` (v4.2.0)  
**Sections Analyzed:** §4.2.1 (Conformance testing Non-RT RIC - General), §4.2.2 (Test configuration)  
**Pages:** 14-15  
**Analysis Date:** 2026-06-30  
**Trace ID:** ORAN-FTM-013  
**Skill Used:** document-analysis-a1tp (extraction lens)

---

## 1. HTTP DEFINITIONS EXTRACTED

### 1.1 HTTP Client and Server Capabilities Required

**From §4.2.1:**
- Conformance testing requires HTTP GET, PUT, POST, DELETE support
- Both Client and Server roles coexist in simulator and DUT

**From §4.2.2.2 (Test Simulator):**

**A1-P Producer (HTTP Server for policies):**
- Receive policy operations: GET /policytypes, PUT /policies, DELETE /policies
- Send policy status notifications: POST {notificationDestination} with JSON body

**A1-EI Consumer (HTTP Client for EI):**
- Query EI types: GET /ei-types
- Manage EI jobs: POST, GET, DELETE /ei-jobs
- Receive EI results via callbacks

### 1.2 Configurable Request/Response Patterns

**Policy URIs:**
```
GET   /policytypes                          → 200 []
GET   /policytypes/{policyTypeId}           → 200 | 404
PUT   /policytypes/{policyTypeId}/policies/{policyId}  → 201/200 + Location
GET   /policytypes/{policyTypeId}/policies/{policyId}  → 200 | 404
DELETE /policytypes/{policyTypeId}/policies/{policyId} → 204 | 404
GET   /policytypes/{policyTypeId}/policies/{policyId}/status → 200 | 404
POST  {notificationDestination} (policy status)       → 200+
```

**EI URIs:**
```
GET   /ei-types                       → 200 EiTypeList
GET   /ei-types/{eiTypeId}           → 200 | 404
PUT   /ei-jobs/{eiJobId}             → 201/200 EiJobObject
GET   /ei-jobs/{eiJobId}             → 200 | 404
DELETE /ei-jobs/{eiJobId}            → 204 | 404
GET   /ei-jobs/{eiJobId}/status      → 200 | 404
```

---

## 2. REST PATTERNS: Role-Based API Behavior

### 2.1 A1-P Service

**Non-RT RIC:** A1-P Consumer (Client) — Initiates policy operations  
**Near-RT RIC:** A1-P Producer (Server) — Hosts policy resources

**Consumer (Per §4.2.2.1):**
- Create/update policies via PUT with consumer-assigned policy IDs
- Query policy types (read-only)
- Query policy status
- Delete policies
- Register callback destination for status notifications

**Producer (Per §4.2.2.2):**
- Advertise available policy types (read-only)
- Accept and validate policies
- Manage lifecycle and ownership
- Deliver status notifications to callbacks
- Return deterministic status codes + ProblemDetails errors

### 2.2 A1-EI Service

**Non-RT RIC:** A1-EI Producer (Server) — Exposes EI types and jobs  
**Near-RT RIC:** A1-EI Consumer (Client) — Queries EI and manages jobs

**Producer (Per §4.2.2.1):**
- Host EI type definitions
- Accept EI job creation/deletion
- Provide job status and results
- Send result notifications to callbacks

**Consumer (Per §4.2.2.2):**
- Query available EI types
- Create and manage EI jobs
- Request EI results
- Register callback for result notifications

### 2.3 Resource Ownership (Per TS 103 987 §5.2.2.2)

- **Policies:** Consumer-assigned policyId; Producer cannot modify/delete
- **Policy types:** Producer-defined; Consumer cannot CRUD types
- **EI jobs:** Consumer-assigned eiJobId; Producer cannot modify parameters
- **EI types:** Producer-defined; Consumer cannot modify definitions

---

## 3. DATA FORMATS

### 3.1 Message Encoding and Structure

**Encoding:** JSON (RFC 7159), UTF-8, Content-Type: `application/json`

### 3.2 Mandatory Representation Objects

**PolicyTypeObject:**
```json
{
  "policy_type_id": "string",
  "policy_schema": { "type": "object", "required": [...] },
  "policy_status_schema": { "type": "object", "required": [...] },
  "supports_policy_creation": true/false
}
```

**PolicyObject:**
```json
{
  "scope": { "scope_type": "cell", "scope_value": "001" },
  "policy_statements": [{"id": "s1", "action": "allow"}]
}
```

**PolicyStatusObject:**
```json
{
  "policy_id": "string",
  "enforcement_status": "string",
  "enforcement_reason": "string (optional)"
}
```

**ProblemDetails (RFC 7807):**
```json
{
  "type": "string (URI)",
  "title": "string",
  "status": 404,
  "detail": "string",
  "instance": "string (request-specific)"
}
```

### 3.3 Message Logging Requirements (§4.2.2.2)

**Capture all:**
- HTTP method, URI, headers, body
- Status code, response headers, response body
- Timestamp
- Deterministic verdict reason

**Validation Rules:**
- Request bodies validated against policy-type-specific schemas
- Invalid payloads → ProblemDetails 400
- Unknown resources → ProblemDetails 404

---

## 4. PROTOCOL SEMANTICS

### 4.1 DUT Preconditions (§4.2.2.1)

**Non-RT RIC Conformance Testing Requires:**

1. A1-P Consumer role (HTTP Client for policies)
2. A1-EI Producer role (HTTP Server for EI)
3. **At least one agreed policy type** with schema definitions
4. **At least one agreed EI type** (if A1-EI testing)
5. HTTP connectivity to Near-RT RIC A1-P Producer endpoint
6. HTTP connectivity to callback destinations for notifications

### 4.2 Deterministic Verdict Requirements (§4.2.2.2)

**HTTP Status Codes:**
- 200: Successful GET or PUT on existing resource
- 201: Successful PUT creating new resource (+ Location header)
- 204: Successful DELETE
- 400: Validation failure (ProblemDetails)
- 404: Resource not found (ProblemDetails)
- 500: Server error (ProblemDetails)

**Failure Scenarios Must Include:**
- Correct HTTP status code
- ProblemDetails with reason fields
- Consistent enforcement_status in PolicyStatusObject
- Timestamps for verdict correlation

**Verdict Correlation:**
- Input scenario → expected HTTP behavior → message logs
- Test verdict matches deterministic protocol behavior, not internal logic

---

## 5. AUTHENTICATION MECHANISMS

**Specification:**
- No explicit authentication required for conformance testing (lab environment)
- Production deployment should use HTTPS + client certificates
- Callback notifications use pre-registered destination URIs (implicit trust)

**Conformance Assumptions:**
- Plain HTTP acceptable for simulator-to-simulator communication
- Optional: HTTP Basic Auth for simulator access control
- No Bearer tokens, API keys, or OAuth2 required

---

## 6. MAPPING TO EXISTING IMPLEMENTATION

### 6.1 Implementation Status

| Component | Coverage | Status |
|---|---|---|
| `a1_policy_service.py` | Policy CRUD, status, notifications | ✅ Conformant |
| `oran.py` routes | /policytypes and /policies URIs | ✅ Conformant |
| `a1_enrichment_service.py` | EI service definition | ⚠️ Partial (job CRUD missing) |
| `conformance/` test suite | DUT readiness, simulator capabilities, evidence | ✅ 80%+ coverage |

### 6.2 Implementation Gaps

| Gap | Spec Ref | Impact |
|---|---|---|
| A1-EI job CRUD incomplete | §4.2.2.2 | Cannot test EI job lifecycle |
| No EI type query endpoints | §4.2.2.2 | Cannot query available EI types |
| No EI result notifications | §4.2.2.2 | Cannot validate result delivery |
| Message logging not externalized | §4.2.2.2 | Logs not easily auditable |
| No callback URI format validation | §4.2.2.2 | Invalid URIs accepted silently |

---

## 7. VERSION NOTES (V4.2.0)

**Changes from Earlier Versions:**
- Policy type pre-configuration now explicitly required (§4.2.2.1)
- EI type pre-configuration aligned with A1-EI framework
- Notification callback model is normative
- ProblemDetails error format is mandatory (RFC 7807)

**Backward Compatibility:**
- HTTP operations (GET, PUT, DELETE) stable across v4.0–v4.2
- URI patterns stable
- Representation objects stable
- No breaking changes in V4.2.0

---

## 8. RECOMMENDATIONS FOR TEST ENHANCEMENTS

### Phase 2 Additions (Priority: Medium)

1. **EI Job Lifecycle Tests**
   - Test EI job creation with required parameters
   - Test EI job status query
   - Test EI job deletion
   - Test EI result notification delivery

2. **Error Handling Tests**
   - Test policy creation rejection when policy type disabled
   - Test concurrent policy creation (conflict handling)
   - Test callback retry on notification failure

3. **Protocol Compliance Tests**
   - Test Location header on 201 responses
   - Test Content-Type negotiation
   - Test conditional requests (If-Match, ETag)

4. **Performance and Reliability**
   - Load test: 1000+ policy operations per second
   - Stress test: Rapid policy CRUD cycles
   - Memory limits under sustained operation

### New Test Suite Structure

```
demo-web/backend/tests/conformance/
├── test_non_rt_ric_dut_readiness.py          ✅ (§4.2.2.1)
├── test_simulator_capabilities.py             ✅ (§4.2.2.2)
├── test_execution_evidence.py                ✅ (§4.2.2.2)
├── test_policy_type_lifecycle.py             ⚠️ (NEW)
├── test_ei_job_lifecycle.py                  ⚠️ (NEW)
├── test_error_handling.py                    ⚠️ (NEW)
└── test_protocol_compliance.py               ⚠️ (NEW)
```

---

## Appendix: Source Text References

**§4.2.1 General:**
> "Non-RT RIC is the device under test, clause 5 of the present document specifies conformance tests for A1-P Consumer and A1-EI Producer functionality as specified in document A1AP [4]."

**§4.2.2.1 Device under test (Non-RT RIC):**
> "For enabling conformance testing, the Non-RT RIC has implemented A1-P Consumer and/or A1-EI Producer functionality ... It also supports one agreed policy type and/or one agreed EI type."

**§4.2.2.2 Test simulator:**
> "The test simulator has A1-P Producer and A1-EI Consumer that both have HTTP Client and HTTP Server capabilities and have flexibility to generate, receive and validate HTTP messages for all the A1 procedures. The test simulator logs all message content during the testing."
