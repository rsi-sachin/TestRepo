# TS 103 988 Section 5 Protocol and Message Evidence

Run ID: ts103988-section5-20260710132538

## Section 5.1 Encoding Evidence

1. Policy scope encoding negative path is exercised and rejected when an invalid representative hex value is supplied (amfRegionId=ZZ).
2. Policy scope encoding positive path is exercised for representative encoded fields (ranUeId, amfRegionId, amfSetId, amfPointer, amfUeNgapId).
3. API layer returns ProblemDetails-style 400 response for invalid encoded scope payloads.

## Section 5.2 Type Definition Evidence

1. A1-P and A1-EI service summaries expose TS 103 988 section-5.2 type-definition catalog metadata.
2. EI identifier format validation rejects invalid eiTypeId lexical forms.
3. TS 103 988 status-code enrichment path is asserted in parser cross-reference unit coverage.

## Clause Mapping

- Clause 5: test_ts103988_section5_common_types.py::test_section5_clause5_service_summaries_expose_type_catalogs
- Clause 5.1: test_ts103988_section5_common_types.py::test_section5_clause5_1_rejects_invalid_policy_encoding_attribute
- Clause 5.2: test_phase2_spec_parsing.py::test_cross_reference_uses_ts103988_status_code_enrichment and test_ts103988_section5_common_types.py::test_section5_clause5_2_uses_type_definition_status_enrichment_path
