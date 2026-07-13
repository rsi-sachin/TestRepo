# Requirement Registry Linkage - TS 103 983 Section 5

Run: ts103983-section5-20260702

- ORAN-FTM-001: A1 service selection and registry
  - Coverage references:
    - demo-web/backend/tests/module/oran/test_ts103983_section5_module_concurrency.py
- ORAN-FTM-002: A1 policy service
  - Coverage references:
    - demo-web/backend/tests/conformance/test_ts103983_section5_a1_functions.py
    - demo-web/backend/tests/nonfunctional/parameter/test_ts103983_section5_parameter_passing.py
- ORAN-FTM-003: A1 enrichment service
  - Coverage references:
    - demo-web/backend/tests/conformance/test_ts103983_section5_a1_functions.py
    - demo-web/backend/tests/nonfunctional/memory/test_ts103983_section5_ei_memory_behavior.py
    - demo-web/backend/tests/nonfunctional/load/test_ts103983_section5_ei_load.py
    - demo-web/backend/tests/nonfunctional/stress/test_ts103983_section5_ei_stress.py
- ORAN-FTM-004: ORAN API router and service-aware endpoints
  - Coverage references:
    - demo-web/backend/tests/interface/api/test_ts103983_section5_interface_faults.py
    - demo-web/backend/tests/e2e/test_ts103983_section5_reconciliation_e2e.py
- ORAN-FTM-016: TS 103 983 section 5 enrichment coverage
  - Coverage references:
    - ORAN/docs/coverage/ts_103983_section5_clause_coverage_matrix.md
    - demo-web/backend/tests/conformance/test_ts103983_section5_a1_functions.py
