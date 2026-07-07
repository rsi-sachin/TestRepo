# TS 103983 Section 5 Protocol and Message Evidence

## A1-P Policy Content Taxonomy Evidence (5.1.5)

- Validation profile: `objective_resource_v1` in `demo-web/backend/app/services/a1_policy_service.py`
- Accepted category payloads:
  - `category=objective` with non-empty `objective` object
  - `category=resource` with non-empty `resource` object
- Rejected payloads:
  - unknown `category`
  - category payload missing required object (`objective` or `resource`)
- Evidence tests:
  - `demo-web/backend/tests/unit/services/test_a1_policy_service.py`
  - `demo-web/backend/tests/interface/api/test_oran_a1_policy_api.py`

## A1-EI Push Delivery Evidence (5.2.5, 5.2.5.1)

- Callback request contract:
  - Header `Content-Type: application/json` for status and result callbacks
- Failure semantics:
  - callback HTTP non-success status marks EI job state as `DISABLED`
  - deterministic non-buffering/no-internal-retry behavior (one callback attempt per invocation)
- Evidence tests:
  - `demo-web/backend/tests/unit/services/test_a1_enrichment_service.py`
  - `demo-web/backend/tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py`

## Verification Outcome

- Focused section-5 closure regression result: `61 passed`
