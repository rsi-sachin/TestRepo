# TS 103 988 Section 8 Clause Coverage Matrix

Document: ORAN/docs/ts_103988v090000p.pdf (v9.0.0)
Scope: section8
Trace context: ORAN-FTM-003, ORAN-FTM-004, ORAN-FTM-020, ORAN-FTM-021
Last updated: 2026-07-13

## Clause Matrix

| Clause | Current coverage | Covered by | Gaps | Action |
|---|---|---|---|---|
| 8.1 | partial | demo-web/backend/tests/unit/services/test_a1_enrichment_service.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py; demo-web/backend/app/services/a1_enrichment_service.py | No Section 8-specific requirement mapping, typed data-model contract, or clause-tagged evidence. | modify |
| 8.2.1 | partial | demo-web/backend/tests/unit/services/test_a1_enrichment_service.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py | No strict callback simple-type validation and no JsonSchema meta-schema validation evidence. | modify |
| 8.2.2.1 | partial | demo-web/backend/tests/unit/services/test_a1_enrichment_service.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py; demo-web/backend/tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py | No strict JobStatusType enum model or invalid-value rejection evidence. | modify |
| 8.2.2.2 | missing | none | No GadShapeType enum model, service validation, or API negative tests. Blocked by implementation gap. | add |
| 8.2.2.3 | missing | none | No VelocityDescType enum model, service validation, or API negative tests. Blocked by implementation gap. | add |
| 8.3.1 | missing | demo-web/backend/tests/conformance/test_ts103988_section5_common_types.py | No typed ScopeIdentifier or UEGeoandVel structured model. Blocked by implementation gap. | add |
| 8.3.2.1 | missing | none | No typed job-definition statement model or clause-tagged validation. Blocked by implementation gap. | add |
| 8.3.2.2 | missing | none | No GeoLocationType discriminator validation, granularity/reporting validation, or typed job-definition payload checks. Blocked by implementation gap. | add |
| 8.3.3.1 | missing | none | No typed job-result statement model or clause-tagged validation. Blocked by implementation gap. | add |
| 8.3.3.2 | missing | none | No VelocityType discriminator validation or typed UE geo-location and velocity result validation. Blocked by implementation gap. | add |
| 8.3.4.1 | missing | none | No typed constraints statement model. Blocked by implementation gap. | add |
| 8.3.4.2 | missing | none | No supportedGadShapes or supportedVelocityDescs constraints-object validation. Blocked by implementation gap. | add |
| 8.4.1 | partial | demo-web/backend/app/models/oran.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py | EiTypeObject exists but does not expose all Section 8 schema attributes with spec-aligned names or typed constraints linkage. | modify |
| 8.4.2.1 | partial | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py | EiJobObject exists but jobDefinition remains an untyped dict with no Section 8 discriminator enforcement. | modify |
| 8.4.2.2 | partial | demo-web/backend/app/services/a1_enrichment_service.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py | Allowed ScopeIdentifier combinations are not represented or validated. | modify |
| 8.4.3 | partial | demo-web/backend/app/models/oran.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py; demo-web/backend/tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py | EiJobStatusObject exists, but strict JobStatusType conformance is not enforced. | modify |
| 8.4.4 | partial | demo-web/backend/app/models/oran.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py | EiJobResultObject is a generic jobResult wrapper, not a typed Section 8 result object. | modify |
| 8.4.5 | missing | none | No EiJobConstraintsObject model or tests. Blocked by implementation gap. | add |
| 8.5 | partial | demo-web/backend/app/api/oran.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py | Binary-data non-applicability is only implicitly true; there is no clause-tagged evidence or explicit negative contract. | modify |

## Implemented Test Targets

1. demo-web/backend/tests/unit/services/test_a1_enrichment_service.py (existing reusable current-state coverage)
2. demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py (existing reusable current-state coverage)
3. demo-web/backend/tests/conformance/test_ei_job_operations.py (existing reusable current-state coverage)
4. demo-web/backend/tests/conformance/test_ts103983_section5_ei_lifecycle_resilience.py (existing reusable current-state coverage)
5. demo-web/backend/tests/conformance/test_ts103988_section5_common_types.py (existing reusable current-state coverage)
6. demo-web/backend/tests/interface/api/test_ts103988_section5_interface_faults.py (existing reusable current-state coverage)
7. demo-web/backend/app/models/oran.py (new typed Section 8 model coverage anchor)
8. demo-web/backend/app/services/a1_enrichment_service.py (new typed Section 8 validation anchor)

## Coverage Summary

- covered: 0
- partial: 10
- missing: 11

## Validation Evidence

1. verification summary: ORAN/docs/coverage/ts_103988_section8_verification_run_summary.md
2. junit: ORAN/docs/coverage/evidence/ts103988-section8-20260713161022/pytest_junit.xml
3. config snapshot: ORAN/docs/coverage/evidence/ts103988-section8-20260713161022/run_config_snapshot.json
4. protocol/message evidence: ORAN/docs/coverage/evidence/ts103988-section8-20260713161022/protocol_message_evidence.md
5. requirement linkage: ORAN/docs/coverage/evidence/ts103988-section8-20260713161022/requirement_registry_linkage.md

## Gate Note

Section 8 remains fail-closed because multiple clause entries still require action=add or action=modify, but a first typed `UEGeoandVel` validation slice is now implemented for create/update and strict status-value handling.