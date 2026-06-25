# TS 103 987 Section 5.2.1 and 5.2.2 Skill-Based Analysis

Document: ts_103987v040300p.pdf  
Sections analyzed: 5.2.1, 5.2.2 (including 5.2.2.1 to 5.2.2.4 and status URI continuation)

## Workflow Skill Used

- Workflow entry skill: document-cross-reference-analysis
- Applied mode: single (section-focused)
- Orchestrated extraction lens: document-analysis-a1tp
- Dependency notes included from references to A1TD and A1GAP

## Extracted Requirements (Skill-Structured)

## 5.2.1 Introduction

- A1-P service operations are defined for policy types from A1TD.
- Implementation meaning: policy management is schema-driven and tightly coupled to policy type definitions.

## 5.2.2.1 Functional elements

- A1-P Consumer resides in Non-RT RIC.
- A1-P Producer resides in Near-RT RIC.
- Protocol is HTTP signaling with client/server roles on both sides.
- Policy procedures are realized as HTTP operations and JSON payloads.

Implementation meaning:
- Resource and operation ownership should be modeled producer-side.
- Consumer/producer are protocol semantics, not traffic-direction labels.

## 5.2.2.2 Policy representation

Normative principles extracted:
- A policy is a REST resource represented as PolicyObject.
- PolicyObject includes scope identifier and at least one policy statement.
- policyId appears in URI for single-policy operations.
- policyId is assigned by A1-P Consumer at creation.
- A1-P Producer cannot modify or delete a policy.
- Status and feedback notification subscription occurs at policy creation through callback URI.
- PolicyObject excludes internal Near-RT RIC function routing details.
- Producer exposes supported policy types and schemas.
- Consumer cannot create/modify/delete policy types.

Implementation meaning:
- Enforce ownership and mutability rules in service layer.
- Enforce schema validation against PolicyTypeObject.
- Treat callback URI as required lifecycle metadata during Create policy.

## 5.2.2.3 Representation objects

- PolicyTypeObject: schema for PolicyObject and PolicyStatusObject validation.
- PolicyObject: policy payload.
- PolicyStatusObject: enforcement status payload.
- ProblemDetails: structured payload for 4xx/5xx responses.

Implementation meaning:
- Add explicit ProblemDetails model and consistent API error shape.
- Validate policy payload and status payload with policy-type schemas.

## 5.2.2.4 Resource identifiers

Required resource hierarchy:
- /policytypes
- /policytypes/{policyTypeId}
- /policytypes/{policyTypeId}/policies
- /policytypes/{policyTypeId}/policies/{policyId}
- /policytypes/{policyTypeId}/policies/{policyId}/status
- notificationDestination callback URI (provided at policy creation)

Implementation meaning:
- Route architecture should be policyType-first and policy instance under that namespace.
- Callback endpoint metadata should be persisted with created policy object.

## Confidence and Priority (Skill Rules)

- Normative requirements with SHALL/MUST-style semantics from section rules: high confidence (0.90 to 0.96)
- Structural mapping and endpoint/resource implications: high confidence (0.86 to 0.93)
- Cross-document assumptions (A1TD schema details, A1GAP procedure depth): medium confidence (0.72 to 0.84)

Priority:
1. Critical: ownership constraints, schema validation, URI/resource hierarchy
2. High: callback handling, status representation, standardized error payload
3. Medium: advanced notification reliability semantics (retry/idempotency) not fully detailed in these clauses

## Source Code Implementation Details (Current State)

The current implementation already provides useful foundation:

- Service boundary and role definitions:
  - demo-web/backend/app/models/a1_service.py
  - demo-web/backend/app/services/a1_service_registry.py
- A1-P helper surface:
  - demo-web/backend/app/services/a1_policy_service.py
- ORAN API entry points:
  - demo-web/backend/app/api/oran.py
- Intelligent section analysis orchestration:
  - demo-web/backend/app/intelligent_document_parsing/services/document_analysis_service.py

### What is already aligned

- Service separation between A1-P and A1-EI is explicit.
- Consumer/producer role model exists and is exposed through API.
- Policy-oriented service helper exists for A1-P metadata and context.

### Gaps against 5.2.1 and 5.2.2

1) Missing explicit A1-P REST resource endpoints in API layer:
- No concrete route set for:
  - GET /policytypes
  - GET /policytypes/{policyTypeId}
  - GET/PUT/DELETE /policytypes/{policyTypeId}/policies/{policyId}
  - GET /policytypes/{policyTypeId}/policies/{policyId}/status

2) Missing explicit representation objects in models:
- No concrete PolicyTypeObject, PolicyObject, PolicyStatusObject, ProblemDetails models dedicated to clause 5.2.2.

3) Missing ownership rule enforcement API contract:
- Producer cannot modify/delete policy and consumer cannot manage policy types should be enforced in service-level guards.

4) Missing callback URI lifecycle handling:
- notificationDestination is not yet visible as required create-policy metadata with validation and persistence path.

5) Missing policy schema validation pipeline:
- PolicyObject validation against policy type schema requires integration with A1TD schema artifacts.

## Recommended Implementation (Concrete)

### 1. Add A1-P data models

Target file:
- demo-web/backend/app/models/a1_policy_models.py

Add:
- PolicyTypeObject
- PolicyObject
- PolicyStatusObject
- ProblemDetails
- CreatePolicyRequest (contains notification_destination and payload)

Validation points:
- policy_id non-empty
- policy_type_id non-empty
- policy statements list/object required
- notification destination URI format validation

### 2. Add A1-P service operations

Target file:
- demo-web/backend/app/services/a1_policy_service.py

Add methods:
- list_policy_types()
- get_policy_type(policy_type_id)
- create_or_replace_policy(policy_type_id, policy_id, policy_object, notification_destination)
- get_policy(policy_type_id, policy_id)
- delete_policy(policy_type_id, policy_id)
- get_policy_status(policy_type_id, policy_id)

Guards:
- enforce policy type mutability rules
- enforce producer-side ownership restrictions
- enforce policy object schema checks (through schema resolver)

### 3. Add API routes under ORAN router

Target file:
- demo-web/backend/app/api/oran.py

Suggested route group:
- /a1/policytypes
- /a1/policytypes/{policy_type_id}
- /a1/policytypes/{policy_type_id}/policies
- /a1/policytypes/{policy_type_id}/policies/{policy_id}
- /a1/policytypes/{policy_type_id}/policies/{policy_id}/status

Response contract:
- Return ProblemDetails for 4xx/5xx
- Return 404 for unknown policy type/policy id
- Return 400 for validation errors
- Keep status codes aligned with API definition clauses for A1-P operations

### 4. Add schema resolver integration

Target area:
- app/services/spec_parser_service.py (or new dedicated schema resolver service)

Purpose:
- Load policy type schemas from TS 103 988/A1TD-derived artifacts
- Validate PolicyObject and PolicyStatusObject against schema references in PolicyTypeObject

### 5. Add tests

Target files:
- demo-web/backend/tests/test_a1_policy_service.py
- demo-web/backend/tests/test_a1_policy_api.py

Test coverage:
- URI/resource mapping correctness
- ownership constraints and prohibited operations
- schema validation success/failure paths
- ProblemDetails payload for common 4xx/5xx cases
- notification destination validation and persistence

## Code-Level Blueprint

Model blueprint:
- class PolicyObject(BaseModel):
  - policy_id: str
  - scope: dict[str, Any]
  - statements: list[dict[str, Any]]

Service blueprint:
- def create_or_replace_policy(...):
  - assert policy_type exists
  - validate policy object against policy type schema
  - store callback URI
  - persist policy
  - return policy object

API blueprint:
- PUT /a1/policytypes/{policy_type_id}/policies/{policy_id}
  - body: PolicyObject + notification_destination
  - errors: ProblemDetails(400/404/409/500)

## End-State Definition for This Clause

Clause 5.2.1 and 5.2.2 implementation can be considered complete when:

1. A1-P route hierarchy mirrors specified resource identifiers.
2. Policy representation objects are implemented and validated.
3. Ownership and mutability constraints are enforced in service logic.
4. Callback URI for status/feedback is captured at policy creation.
5. Error responses consistently use ProblemDetails shape.
6. Tests verify all above behaviors, including negative paths.
