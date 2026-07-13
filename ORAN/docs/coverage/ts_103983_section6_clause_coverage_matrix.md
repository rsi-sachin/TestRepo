# TS 103 983 Section 6 Clause Coverage Matrix

Document: `ORAN/docs/ts_103983v040000p.pdf` (v4.0.0)
Scope: Section 6, signalling procedures of the A1 interface
Trace context: ORAN-FTM-017 (with foundational overlap from ORAN-FTM-001/002/003/004)

## Matrix

| Section 6 clause | Clause intent | Existing ORAN trace IDs | Existing code/test mapping | Coverage status | Notes |
|---|---|---|---|---|---|
| 6.1 General | Procedure usage is defined in A1UCR/A1AP; implementation should expose procedure families | ORAN-FTM-017 | A1-P and A1-EI procedure families exposed in `demo-web/backend/app/api/oran.py`; interface tests in `demo-web/backend/tests/interface/api/test_oran_a1_policy_api.py` and `demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py` | Partial | Section-level intent is covered through concrete 6.2 and 6.3 procedures; no standalone 6.1 executable test case. |
| 6.2 Policy related procedures | Support policy type/policy lifecycle/status and notifications | ORAN-FTM-017, ORAN-FTM-002, ORAN-FTM-004 | Policy type/status/policy CRUD/status procedures in `demo-web/backend/app/api/oran.py`; service logic in `demo-web/backend/app/services/a1_policy_service.py`; interface tests in `demo-web/backend/tests/interface/api/test_oran_a1_policy_api.py` | Covered | Includes explicit policy type status query and notify callback proxy operations added for section-6 closure. |
| 6.2 - Query policy type identifiers | List supported policy types | ORAN-FTM-017 | `GET /a1/policytypes` in `demo-web/backend/app/api/oran.py`; tests in `demo-web/backend/tests/interface/api/test_oran_a1_policy_api.py` | Covered | Existing behavior retained. |
| 6.2 - Query policy type | Fetch one policy type | ORAN-FTM-017 | `GET /a1/policytypes/{policy_type_id}` in `demo-web/backend/app/api/oran.py`; tests in `demo-web/backend/tests/interface/api/test_oran_a1_policy_api.py` | Covered | Existing behavior retained. |
| 6.2 - Query policy type status | Fetch one policy type status | ORAN-FTM-017 | `GET /a1/policytypes/{policy_type_id}/status` in `demo-web/backend/app/api/oran.py`; `get_policy_type_status` in `demo-web/backend/app/services/a1_policy_service.py`; tests in `demo-web/backend/tests/interface/api/test_oran_a1_policy_api.py` | Covered | Newly implemented for section-6 gap closure. |
| 6.2 - Notify policy type status | Notify policy type status to callback URI | ORAN-FTM-017 | `POST /a1/policytypes/{policy_type_id}/status/notify` in `demo-web/backend/app/api/oran.py`; `notify_policy_type_status` in `demo-web/backend/app/services/a1_policy_service.py`; tests in `demo-web/backend/tests/interface/api/test_oran_a1_policy_api.py` | Covered | OpenAPI callback contract included in endpoint definition. |
| 6.2 - Create/query/update/delete/query status/notify status policy | Policy lifecycle and status procedures | ORAN-FTM-017, ORAN-FTM-002 | Existing policy endpoints and notification helper in `demo-web/backend/app/api/oran.py` and `demo-web/backend/app/services/a1_policy_service.py`; interface/conformance coverage | Covered | Existing implementation reused; no behavior regression expected. |
| 6.3 Enrichment information transfer procedures | Support EI discovery, EI job control, status, notification, and result delivery | ORAN-FTM-017, ORAN-FTM-003, ORAN-FTM-004 | EI type/job/status/result procedures in `demo-web/backend/app/api/oran.py`; service logic in `demo-web/backend/app/services/a1_enrichment_service.py`; interface tests in `demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py` | Covered | Includes explicit EI type status query and notify callback proxy operations added for section-6 closure. |
| 6.3 - Query EI type identifiers/query EI type | EI type discovery | ORAN-FTM-017 | `GET /a1/eitypes` and `GET /a1/eitypes/{ei_type_id}`; interface tests | Covered | Existing behavior retained. |
| 6.3 - Query EI type status | Fetch one EI type status | ORAN-FTM-017 | `GET /a1/eitypes/{ei_type_id}/status` in `demo-web/backend/app/api/oran.py`; `get_ei_type_status` in `demo-web/backend/app/services/a1_enrichment_service.py`; tests in `demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py` | Covered | Newly implemented for section-6 gap closure. |
| 6.3 - Notify EI type status | Notify EI type status to callback URI | ORAN-FTM-017 | `POST /a1/eitypes/{ei_type_id}/status/notify` in `demo-web/backend/app/api/oran.py`; `notify_ei_type_status` in `demo-web/backend/app/services/a1_enrichment_service.py`; tests in `demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py` | Covered | OpenAPI callback contract included in endpoint definition. |
| 6.3 - EI job control/status and result delivery | EI job lifecycle procedures | ORAN-FTM-017, ORAN-FTM-003 | Existing EI job endpoints and status/result notification helpers in API + service; interface/conformance coverage | Covered | Existing implementation reused; no behavior regression expected. |
| 6.4 ML model related procedures | No ML model procedures listed in TS 103 983 | ORAN-FTM-017 | A1-ML out-of-scope declaration in `demo-web/backend/app/services/a1_policy_service.py` and `demo-web/backend/app/services/a1_enrichment_service.py` | Covered | Clause is satisfied by specification wording (no required procedure list). |

## Summary

- The previously identified functional section-6 gaps for policy-type-status and EI-type-status procedures are now implemented.
- Remaining work is primarily governance/verification hardening: keep section-6 matrix and regression evidence updated when endpoint behavior changes.
