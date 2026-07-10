# Requirement Registry Linkage - TS 103 988 Section 5

Run: ts103988-section5-20260710132538

## Trace IDs

1. ORAN-FTM-020
2. ORAN-FTM-002
3. ORAN-FTM-003
4. ORAN-FTM-007

## Requirement to Test Mapping

1. REQ-TS103988-5-GENERIC-COMMON-TYPES
   - demo-web/backend/tests/conformance/test_ts103988_section5_common_types.py::test_section5_clause5_service_summaries_expose_type_catalogs
2. REQ-TS103988-5.1-JSON-ENCODING-RANGE
   - demo-web/backend/tests/unit/services/test_a1_policy_service.py::test_policy_scope_rejects_invalid_encoded_attribute_values
   - demo-web/backend/tests/interface/api/test_oran_a1_policy_api.py::test_policy_create_rejects_invalid_section5_encoded_scope_attribute
3. REQ-TS103988-5.2-TYPE-DEFINITION-VERSION
   - demo-web/backend/tests/unit/services/test_phase2_spec_parsing.py::test_cross_reference_uses_ts103988_status_code_enrichment
   - demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py::test_a1ei_service_summary_exposes_ts103988_type_definition_catalog
