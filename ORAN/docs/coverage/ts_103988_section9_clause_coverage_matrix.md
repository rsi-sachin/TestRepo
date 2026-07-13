# TS 103 988 Section 9 Clause Coverage Matrix

Document: ORAN/docs/ts_103988v090000p.pdf (v9.0.0)
Scope: section9
Trace context: ORAN-FTM-022, ORAN-FTM-021, ORAN-FTM-003, ORAN-FTM-004
Last updated: 2026-07-13

## Clause Matrix

| Clause | Current coverage | Covered by | Gaps | Action |
|---|---|---|---|---|
| 9.1.1 | partial | demo-web/backend/app/services/a1_enrichment_service.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py | No explicit major-version compatibility assertions | modify |
| 9.1.2.1 | covered | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py | None in current slice | none |
| 9.1.2.2 | partial | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py | No direct common-schema linkage or compatibility-behavior assertions | modify |
| 9.1.2.3 | partial | demo-web/backend/app/services/a1_enrichment_service.py | No dedicated assertion that exposed schema metadata embeds the EI type ID exactly as required | modify |
| 9.2.1.1 | covered | demo-web/backend/app/services/a1_enrichment_service.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py | None in current slice | none |
| 9.2.1.2.2 | partial | demo-web/backend/app/models/oran.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py | No explicit rejection coverage for unsupported scope members | modify |
| 9.2.1.3.1 | partial | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py; demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py | Upper-bound and extra-field negatives not yet covered | modify |
| 9.2.1.3.2 | partial | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py | No invalid-enum, empty-array, or alias-conflict tests | modify |
| 9.2.1.3.3 | covered | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py | None in current slice | none |
| 9.2.1.3.4 | partial | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py; demo-web/backend/tests/unit/services/test_a1_enrichment_service.py | Point, polygon, and point-uncertainty-circle coverage now exists, but the full discriminator matrix remains incomplete for the remaining geo-location and velocity subtype payloads | modify |

## Coverage Summary

- covered: 3
- partial: 7
- missing: 0

## Validation Evidence

1. verification summary: ORAN/docs/coverage/ts_103988_section9_verification_run_summary.md
2. junit: ORAN/docs/coverage/evidence/ts103988-section9-20260713164329/pytest_junit.xml
3. config snapshot: ORAN/docs/coverage/evidence/ts103988-section9-20260713164329/run_config_snapshot.json
4. protocol/message evidence: ORAN/docs/coverage/evidence/ts103988-section9-20260713164329/protocol_message_evidence.md
5. requirement linkage: ORAN/docs/coverage/evidence/ts103988-section9-20260713164329/requirement_registry_linkage.md

## Gate Note

Section 9 remains fail-closed because seven clause entries still require `action=modify`, even though the spec-faithful `UEGeoandVel` validation slice now includes explicit point, polygon, and point-uncertainty-circle result coverage alongside the persisted evidence artifact set.
