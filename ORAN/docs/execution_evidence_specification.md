# Execution Evidence Completeness Specification

**Document:** Mandatory Evidence Checks for TS 103 989 §4.2.1–4.2.2 Conformance Test Runs  
**Date:** 2026-06-30  
**Scope:** Evidence collection, validation, and verdict assignment  
**Source:** TS 103 989 §4.2.1–4.2.2, TS 103 987 (A1 Interface)

---

## Overview

Each conformance test run must capture complete evidence to ensure deterministic verdict assignment and full traceability. Evidence comprises HTTP message logs, header/body validation results, and explicit verdict reasoning tied to specification sections.

---

## 1. HTTP Message Log Capture

**Requirement:** Capture all HTTP request/response pairs with full metadata.

### 1.1 Mandatory Fields per HTTP Exchange

Every HTTP exchange (request + response) must be logged with the following JSON structure:

```json
{
  "exchange_id": "uuid-or-sequence-number",
  "test_case_id": "test_case_ref",
  "timestamp": "ISO-8601-datetime",
  "request": {
    "method": "GET|PUT|POST|DELETE",
    "uri": "/v1/policytypes/...",
    "headers": {
      "Content-Type": "application/json",
      "X-Trace-ID": "..."
    },
    "body": "{...JSON...}",
    "body_size_bytes": 1024
  },
  "response": {
    "status_code": 200,
    "headers": {
      "Content-Type": "application/json",
      "Location": "/v1/policytypes/{id}/policies/{id}",
      "X-Trace-ID": "..."
    },
    "body": "{...JSON...}",
    "body_size_bytes": 2048,
    "response_time_ms": 42.5
  },
  "validation": {
    "schema_valid": true,
    "status_code_expected": true,
    "headers_complete": true
  }
}
```

### 1.2 Log Storage and Organization

| Aspect | Specification |
|---|---|
| **Storage Format** | JSON Lines (one JSON object per line) or JSON Array |
| **File Naming** | `{test_case_id}_{timestamp}.jsonl` or `conformance_run_{run_id}.jsonl` |
| **Retention Policy** | Persist for minimum 30 days; archive for compliance audit |
| **Accessibility** | Logs must be queryable by test case ID, timestamp range, or HTTP method |

---

## 2. Header Validation Requirements

**Requirement:** Validate HTTP response headers conform to specification.

### 2.1 Mandatory Response Headers per Operation

| Operation | Status | Mandatory Headers | Validation Check |
|---|---|---|---|
| GET /policytypes | 200 | `Content-Type`, `X-Trace-ID` (if used) | Type = `application/json`; Trace-ID present if configured |
| GET /policytypes/{id} | 200 | `Content-Type` | Type = `application/json` |
| PUT /policies (create) | 201 | `Location`, `Content-Type` | Location = `/v1/policytypes/{id}/policies/{id}` |
| PUT /policies (update) | 200 | `Content-Type` | Type = `application/json` |
| DELETE /policies | 204 | None (no body) | No body in response |
| Error Response | 400/404/500 | `Content-Type` | Type = `application/json` (for ProblemDetails) |

### 2.2 Optional but Recommended Headers

| Header | Recommended Value | Test Purpose |
|---|---|---|
| `Cache-Control` | `no-cache` or `no-store` | Verify cache policy enforcement |
| `Retry-After` | Integer seconds (if 503) | Verify rate-limiting guidance |
| `X-RIC-Request-ID` | Correlation ID | Trace request across systems |

### 2.3 Header Validation Evidence

For each response header check:

```json
{
  "test_case_id": "test_case_ref",
  "exchange_id": "uuid",
  "header_validations": [
    {
      "header_name": "Content-Type",
      "expected_value": "application/json",
      "actual_value": "application/json",
      "status": "PASS"
    },
    {
      "header_name": "Location",
      "expected_value": "/v1/policytypes/{id}/policies/{id}",
      "actual_value": "/v1/policytypes/policy-type-1/policies/policy-id-1",
      "status": "PASS",
      "notes": "URI pattern matched"
    }
  ]
}
```

---

## 3. Response Body Validation

**Requirement:** Validate HTTP response bodies conform to JSON Schema and TS 103 987 representation objects.

### 3.1 Representation Object Schemas

Each response body must conform to one of the following schemas per TS 103 987:

#### 3.1.1 PolicyTypeObject

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "policyTypeId": { "type": "string", "minLength": 1 },
    "schemaVersion": { "type": "string" },
    "schema": {
      "type": "object",
      "description": "JSON Schema for this policy type"
    }
  },
  "required": ["policyTypeId", "schema"],
  "additionalProperties": false
}
```

**Validation Evidence:**
```json
{
  "test_case_id": "...",
  "response_object_type": "PolicyTypeObject",
  "schema_validation": {
    "valid": true,
    "errors": []
  },
  "field_checks": [
    { "field": "policyTypeId", "present": true, "type_match": true },
    { "field": "schema", "present": true, "type_match": true }
  ]
}
```

#### 3.1.2 PolicyObject

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "policyTypeId": { "type": "string" },
    "policyId": { "type": "string" },
    "policyData": { "type": "object" }
  },
  "required": ["policyTypeId", "policyId", "policyData"],
  "additionalProperties": false
}
```

**Validation Evidence:**
```json
{
  "test_case_id": "...",
  "response_object_type": "PolicyObject",
  "schema_validation": {
    "valid": true,
    "errors": []
  },
  "field_checks": [
    { "field": "policyTypeId", "present": true, "value": "policy-type-1" },
    { "field": "policyId", "present": true, "value": "policy-id-1" },
    { "field": "policyData", "present": true, "type_match": true }
  ]
}
```

#### 3.1.3 PolicyStatusObject

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "status": { "type": "string", "enum": ["UNDEFINED", "OK", "FAILED"] },
    "statusReason": { "type": "string" }
  },
  "required": ["status"],
  "additionalProperties": false
}
```

#### 3.1.4 ProblemDetails (RFC 7807)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "type": "string", "format": "uri-reference" },
    "title": { "type": "string" },
    "status": { "type": "integer", "minimum": 100, "maximum": 599 },
    "detail": { "type": "string" },
    "instance": { "type": "string", "format": "uri-reference" }
  },
  "required": ["status"],
  "additionalProperties": false
}
```

**Validation Evidence:**
```json
{
  "test_case_id": "...",
  "response_object_type": "ProblemDetails",
  "schema_validation": {
    "valid": true,
    "errors": []
  },
  "error_checks": [
    { "field": "type", "present": true, "format": "uri-reference" },
    { "field": "status", "present": true, "value": 400 },
    { "field": "detail", "present": true, "value": "Invalid policy data" }
  ]
}
```

---

## 4. Deterministic Verdict Assignment

**Requirement:** Assign test verdict based on explicit specification-linked reasoning.

### 4.1 Verdict Outcomes

| Verdict | Meaning | Example |
|---|---|---|
| **PASS** | All checks pass; behavior conforms to spec | GET /policytypes returns 200 + valid PolicyTypeObject array |
| **FAIL** | At least one check fails; behavior violates spec | PUT /policies returns 200 instead of expected 201 for new resource |
| **INCONCLUSIVE** | Test could not execute or determine result | HTTP timeout; simulator unreachable; test infrastructure error |

### 4.2 Verdict Evidence Structure

```json
{
  "test_case_id": "test_policy_query_001",
  "execution_timestamp": "2026-06-30T12:34:56Z",
  "test_section_reference": "TS 103 989 §4.2.1, TS 103 987 §5.2.3.2",
  "test_intent": "Verify GET /policytypes returns all available policy types",
  "verdict": "PASS",
  "verdict_reason": "HTTP 200 received with valid PolicyTypeObject array",
  "checks_performed": [
    {
      "check_id": "1",
      "check_description": "HTTP status code = 200",
      "expected": 200,
      "actual": 200,
      "result": "PASS",
      "spec_reference": "TS 103 987 §5.2.3.3"
    },
    {
      "check_id": "2",
      "check_description": "Response body is valid JSON",
      "expected": "valid JSON",
      "actual": "valid JSON",
      "result": "PASS"
    },
    {
      "check_id": "3",
      "check_description": "Response conforms to PolicyTypeObject schema",
      "expected": "schema conformance",
      "actual": "schema conformance",
      "result": "PASS",
      "spec_reference": "TS 103 987 §5.2.2.3"
    }
  ],
  "evidence_artifacts": [
    {
      "artifact_type": "http_message_log",
      "file_path": "logs/test_policy_query_001_20260630_123456.jsonl",
      "size_bytes": 4096
    },
    {
      "artifact_type": "schema_validation_report",
      "file_path": "reports/test_policy_query_001_schema_validation.json",
      "size_bytes": 512
    }
  ]
}
```

### 4.3 Failure Evidence Structure

For failed tests, capture detailed failure context:

```json
{
  "test_case_id": "test_policy_create_002",
  "verdict": "FAIL",
  "verdict_reason": "HTTP status code 200 received instead of expected 201 for new resource creation",
  "failing_check": {
    "check_id": "1",
    "check_description": "HTTP status code for new resource = 201",
    "expected": 201,
    "actual": 200,
    "result": "FAIL",
    "spec_reference": "TS 103 987 §5.2.4.3 (Create policy)"
  },
  "root_cause_analysis": {
    "hypothesis": "Simulator or DUT incorrectly treats new policy as update",
    "suggested_investigation": [
      "Verify policyId generation logic",
      "Check simulator state tracking for duplicate detection",
      "Review HTTP mapping table in TS 103 987 §5.2.4.1"
    ]
  },
  "evidence_artifacts": [
    {
      "artifact_type": "http_message_log",
      "file_path": "logs/test_policy_create_002_20260630_124500.jsonl",
      "problematic_exchange": "exchange_id: 12345",
      "size_bytes": 2048
    }
  ]
}
```

---

## 5. Execution Evidence Completeness Checklist

For each test run, verify:

- [ ] **Message Logs:** All HTTP exchanges captured with request/response metadata
- [ ] **Header Validation:** All response headers checked against specification
- [ ] **Body Validation:** Response body JSON conforms to schema
- [ ] **Verdict Assignment:** Verdict (PASS/FAIL/INCONCLUSIVE) assigned with explicit reason
- [ ] **Spec Reference:** Verdict reason includes TS section identifier (e.g., "TS 103 987 §5.2.3")
- [ ] **Evidence Traceability:** All artifacts linked to test case ID and execution timestamp
- [ ] **Artifact Organization:** Logs and reports stored in consistent, queryable location

---

## 6. Evidence Retention and Audit Trail

| Requirement | Specification |
|---|---|
| **Retention Duration** | Minimum 30 days; archive for compliance audit (recommend 1 year) |
| **Audit Trail** | Preserve test case ID, timestamp, verdict, and reason for all runs |
| **Change Log** | Track modifications to verdict or evidence (if reanalyzed) with reason and timestamp |
| **Access Control** | Restrict modifications to evidence; allow read access for analysis |

---

## 7. Conformance Report Template

**Final conformance report must include:**

```json
{
  "conformance_run_id": "run-20260630-001",
  "date": "2026-06-30",
  "spec_section": "TS 103 989 §4.2.1–4.2.2",
  "dut_name": "Non-RT RIC",
  "dut_version": "v1.0",
  "test_environment": {
    "simulator_version": "v1.0",
    "test_harness_version": "v1.0",
    "python_version": "3.13"
  },
  "test_summary": {
    "total_test_cases": 26,
    "passed": 26,
    "failed": 0,
    "inconclusive": 0,
    "pass_rate": "100%"
  },
  "evidence_summary": {
    "total_http_exchanges": 78,
    "log_files": [
      "logs/conformance_run_20260630_001.jsonl"
    ],
    "schema_validation_reports": [
      "reports/schema_validation_20260630_001.json"
    ]
  },
  "verdict": "CONFORM",
  "conformance_statement": "DUT successfully demonstrates conformance to TS 103 989 §4.2.1–4.2.2 conformance requirements.",
  "sign_off": {
    "test_engineer": "John Doe",
    "date": "2026-06-30",
    "signature": "digital-signature-or-hash"
  }
}
```

---

## Notes

- Evidence must be **deterministic and reproducible**: re-running the same test should produce identical evidence (within timestamp precision).
- All evidence must be **machine-readable** for automated analysis and trending.
- Verdict assignment must be **traceable to specification sections** for audit and certification purposes.
