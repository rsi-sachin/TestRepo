# Requirement Registry Linkage - TS 103 988 Section 9

| Clause | Trace IDs | Primary code scope | Current evidence | Status |
|---|---|---|---|---|
| 9.1.1 | ORAN-FTM-022 | demo-web/backend/app/services/a1_enrichment_service.py | canonical-id unit/API tests | partial |
| 9.1.2.1 | ORAN-FTM-022, ORAN-FTM-021 | demo-web/backend/app/models/oran.py | focused EI status model coverage | covered |
| 9.1.2.2 | ORAN-FTM-022 | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py | compound job-definition validation | partial |
| 9.1.2.3 | ORAN-FTM-022 | demo-web/backend/app/services/a1_enrichment_service.py | schema metadata `$id` exposure | partial |
| 9.2.1.1 | ORAN-FTM-022 | demo-web/backend/app/services/a1_enrichment_service.py | canonical `EiTypeId` storage assertions | covered |
| 9.2.1.2.2 | ORAN-FTM-022 | demo-web/backend/app/models/oran.py | scope wrapper enforcement | partial |
| 9.2.1.3.1 | ORAN-FTM-022 | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py | positive create-path plus key negative checks | partial |
| 9.2.1.3.2 | ORAN-FTM-022 | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py | canonical constraints property-name validation | partial |
| 9.2.1.3.3 | ORAN-FTM-022, ORAN-FTM-021 | demo-web/backend/app/models/oran.py | generic EI status schema reuse | covered |
| 9.2.1.3.4 | ORAN-FTM-022 | demo-web/backend/app/models/oran.py; demo-web/backend/app/services/a1_enrichment_service.py | result-array and first discriminator checks | partial |

Open follow-up:

1. Add clause-tagged tests to close partial statuses for 9.1.1, 9.1.2.2, 9.1.2.3, 9.2.1.2.2, 9.2.1.3.1, 9.2.1.3.2, and 9.2.1.3.4.
