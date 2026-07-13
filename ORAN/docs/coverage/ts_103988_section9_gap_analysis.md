# TS 103 988 Section 9 Gap Analysis

Document: ORAN/docs/ts_103988v090000p.pdf (v9.0.0)
Scope: section9
Last updated: 2026-07-13

## Routing Audit

- selected_primary_skill: document-analysis-a1td
- selected_secondary_skills: document-cross-reference-analysis
- why_selected: Section 9 is a data-model and JSON-schema definition section for A1-EI types, not an HTTP/resource procedure section.
- protocol_markers_detected: []
- post_analysis_handoff_status: not_requested
- post_analysis_handoff_target: post-analysis-test-policy-orchestration
- post_analysis_handoff_reason: Analysis only. No implementation, testing, or coverage-closure request was made in this task.

## Section Summary

Section 9 defines the normative A1-EI type layer on top of the generic A1-EI data model:

- `9.1.1` defines EI type identification and compatibility rules.
- `9.1.2.1` defines the generic EI job status schema with `ENABLED` and `DISABLED`.
- `9.1.2.2` ties EI job definition schemas to the common data types schema from clause 7.1 and to the same compatibility rules.
- `9.1.2.3` requires the EI type identifier to be embedded in the JSON Schema `$id`.
- `9.2.1` defines one concrete EI type: `ORAN_UEGeoandVel_3.0.1`.
- `9.2.1.2.2` limits the allowed scope combination for `UEGeoandVelEIDescription` to a single `ueId`.
- `9.2.1.3.1` defines the EI job definition schema with top-level `scope` and `ueGeoandVelEIDescription` objects.
- `9.2.1.3.2` defines the EI job constraints schema with `supportedGadShapes` and optional `supportedVelocityTypes`.
- `9.2.1.3.3` reuses the generic EI job status schema.
- `9.2.1.3.4` defines the EI job result schema as an array of typed result objects with discriminator-driven `geoLocation` and `velocity` payloads.

## Normative Findings

1. EI types are versioned SemVer identifiers. Compatibility is defined by matching typename plus matching major version.
2. The concrete EI type identifier is `ORAN_UEGeoandVel_3.0.1`, not just `UEGeoandVel`.
3. The EI job definition is a compound object. It requires:
   - `scope.ueId`
   - `ueGeoandVelEIDescription.gadShape`
   - `ueGeoandVelEIDescription.granularityPeriod` in the range 1..60000
   - `ueGeoandVelEIDescription.reportingPeriod` in the range 1..60000
   - `ueGeoandVelEIDescription.reportingAmount` in the range 1..3600000
   - optional `ueGeoandVelEIDescription.velocityDesc`
4. The allowed scope combination is explicit: `ueId=1`, `groupId=0`, `sliceId=0`, `qosId=0`, `cellId=0`.
5. The constraints schema requires `ueGeoandVelEIConstraints.supportedGadShapes` and optionally allows `supportedVelocityTypes`.
6. The result schema is not a single object. It is an array of result objects, each with discriminator-based `geoLocation` and `velocity` subtype resolution.
7. Section 9 reuses the common A1TD schema base URI and common `UeId` definition instead of redefining those primitives locally.

## Current Repository Coverage

The repository already contains a partial Section 9 implementation surface introduced during Section 8 A1-EI work:

- `demo-web/backend/app/models/oran.py` defines `JobStatusType`, `GadShapeType`, `VelocityDescType`, `UeGeoAndVelEIDescription`, `UeGeoAndVelEIConstraints`, and `UeGeoAndVelEIResult`.
- `demo-web/backend/app/services/a1_enrichment_service.py` exposes a `UEGeoandVel` EI type and validates typed job definitions, constraints, and result payloads.
- `demo-web/backend/tests/unit/services/test_a1_enrichment_service.py` and `demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py` cover basic create-path validation and invalid `gadShape` rejection.

This means Section 9 is not greenfield in the repo, but the current implementation is only a first typed slice and does not yet match the normative schema exactly.

## Gap Assessment

| Clause | Expected by TS 103 988 Section 9 | Current repo state | Status |
|---|---|---|---|
| 9.1.1 | EI type identity and SemVer compatibility via full `EiTypeId` | Catalog exposes `UEGeoandVel` with version `3.0.1`, but not the spec identifier `ORAN_UEGeoandVel_3.0.1` as the runtime EI type ID | Partial |
| 9.1.2.1 | Generic EI job status schema with `ENABLED` and `DISABLED` | `JobStatusType` and `EiJobStatusObject` align with spec values | Covered |
| 9.1.2.2 | EI job definitions linked to common data types and common scope schema | Current typed job definition omits the top-level `scope` object and common-schema linkage | Missing |
| 9.1.2.3 | EI type identifier embedded in schema `$id` | Service metadata includes simplified schema titles/required fields, not the full spec `$id` contract | Partial |
| 9.2.1.1 | EI type ID `ORAN_UEGeoandVel_3.0.1` | Service key is `UEGeoandVel` | Missing |
| 9.2.1.2.2 | Only `scope.ueId` allowed | Current create-path model does not represent or validate `scope` at all | Missing |
| 9.2.1.3.1 | Compound EI job definition with `scope` and `ueGeoandVelEIDescription` | Current API accepts only the inner description fields directly under `jobDefinition` | Missing |
| 9.2.1.3.1 | Numeric bounds: 1..60000, 1..60000, 1..3600000 | Current validator only checks values are greater than zero | Partial |
| 9.2.1.3.2 | Constraints object with `supportedGadShapes` and `supportedVelocityTypes` | Model uses `supportedVelocityDescs`, which does not match the spec property name | Missing |
| 9.2.1.3.3 | Reuse generic status schema | Current model reuse is aligned | Covered |
| 9.2.1.3.4 | Result is an array of typed result objects with discriminator-specific geo/velocity schemas | Current validator accepts one generic object and does not enforce per-discriminator payload shape | Missing |

## Code Mapping

- Existing implementation anchors:
  - `demo-web/backend/app/models/oran.py`
  - `demo-web/backend/app/services/a1_enrichment_service.py`
  - `demo-web/backend/tests/unit/services/test_a1_enrichment_service.py`
  - `demo-web/backend/tests/interface/api/test_oran_a1_ei_api.py`
- Closest existing traceability row:
  - `ORAN-FTM-021` covers TS 103 988 Section 8 A1-EI data model work.
- Traceability blocker for future implementation:
  - There is no dedicated trace row for TS 103 988 Section 9. Any follow-up code work should add a new `ORAN/docs/feature_traceability_map.md` row before implementation, because `ORAN-FTM-021` is explicitly scoped to Section 8.

## Recommended Follow-Up

1. Add a new traceability row for TS 103 988 Section 9 before any production code changes.
2. Refactor the `UEGeoandVel` EI job definition model to match the compound Section 9 schema shape with explicit `scope` and `ueGeoandVelEIDescription` objects.
3. Enforce the exact numeric ranges and the single-`ueId` scope constraint from `9.2.1.2.2`.
4. Rename the constraints payload field from `supportedVelocityDescs` to `supportedVelocityTypes` or provide strict spec-aligned aliasing.
5. Model EI job results as an array payload with discriminator-aware shape validation for both `geoLocation` and `velocity`.
6. Expose full schema metadata including the spec `$id` and the canonical `ORAN_UEGeoandVel_3.0.1` identifier.

## Bottom Line

Section 9 is partially implemented through the recent typed `UEGeoandVel` work, but the current repo state is schema-inspired rather than schema-faithful. The strongest gaps are the missing compound `scope` wrapper, the non-canonical EI type identifier, the constraints property-name mismatch, and the absence of array/discriminator-accurate result validation.