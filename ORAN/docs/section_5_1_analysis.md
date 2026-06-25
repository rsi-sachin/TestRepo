# TS 103 987 Section 5.1 Analysis

Document: `ts_103987v040300p.pdf`

## Scope of Section 5.1

Section 5.1 is the introduction to the A1 services covered by the specification.

It states that the present document defines APIs for:

- **A1-P**: A1 policy management service
- **A1-EI**: A1 enrichment information service

It also explicitly says that **A1-ML is not defined in this document**.

The section establishes the service model used by the spec:

- **Service Consumer** sends requests
- **Service Producer** sends responses and notifications
- The producer owns the resources that the consumer operates on
- Consumer and producer are protocol roles, not network-direction labels

## Interpretation

This section is mainly a scope and interaction model, not a detailed procedure definition.

The practical meaning is:

- Implementations should model A1 services as separate service domains
- Request handling, response handling, and notifications should be producer-centered
- The tool should support A1-P and A1-EI as first-class service types
- A1-ML should remain out of scope unless a later specification explicitly defines it

## Existing Modules and Features to Reuse

The following parts of the tool already provide a strong base for section 5.1 work:

- **FastAPI router pattern** for service-specific endpoints
- **WebSocket streaming infrastructure** for live request/response output
- **Execution service pattern** for launching and monitoring external processes
- **Demo/history data flow** for cataloging and tracking operations
- **Pydantic model structure** for typed service and response objects
- **Frontend tab-based shell** for adding service-specific workflows without redesigning the whole UI

## New Modules and Features to Add

To fully support the section 5.1 service model, the tool should add the following:

- **A1 service registry module**
  - Central place to define supported services: A1-P and A1-EI
  - Keep A1-ML marked as unsupported / not defined

- **A1 service role model**
  - Explicit consumer/producer representation
  - Useful for request routing, notifications, and resource ownership

- **A1-P service module**
  - Policy management operations
  - Policy type, policy object, policy status handling

- **A1-EI service module**
  - Enrichment information operations
  - EI job lifecycle and related payloads

- **Service capability discovery**
  - Ability to report which A1 services are available
  - Prevents unsupported service calls from reaching the execution layer

- **Service-specific validation**
  - Validate that requests match the consumer/producer role expectations
  - Enforce that producer-owned resources are not mutated from the wrong side

- **UI service selector**
  - Let the user choose A1-P or A1-EI explicitly
  - Hide A1-ML unless future requirements add it

- **Service-aware test generation**
  - Generate separate test flows for policy management and enrichment info
  - Keep service metadata attached to generated tests

## Recommended Decision Point

If the goal is to support section 5.1 cleanly, the minimum implementation should include:

1. A service registry with A1-P and A1-EI
2. A consumer/producer role model
3. Separate service modules for A1-P and A1-EI
4. UI support for selecting those services

If the tool is still in an early phase, A1-ML should not be added now because the spec explicitly excludes it from this document.

## Implementation Notes

- Keep A1-P and A1-EI modular so future clauses can extend each service independently
- Treat consumer/producer as protocol roles in code and UI text
- Reuse shared transport and execution infrastructure instead of duplicating it for each service
- Add clear unsupported-service handling for anything outside the defined scope

## Short Conclusion

Section 5.1 defines the service boundary for the rest of the spec.

For the tool, the important action is to support **A1-P** and **A1-EI** as explicit modules/features and to leave **A1-ML** out of scope for now.