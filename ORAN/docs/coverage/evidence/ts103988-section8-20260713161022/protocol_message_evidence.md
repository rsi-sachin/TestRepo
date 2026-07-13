# TS 103 988 Section 8 Protocol and Message Evidence

Run ID: ts103988-section8-20260713161022

## Evidence Scope

This verification run exercised the current EI control-plane slice that exists in the repository:

1. EI job create, query, update, delete lifecycle.
2. EI job status object delivery semantics.
3. EI job result object delivery semantics.
4. Problem-details error handling for EI endpoints.
5. Section-5 catalog metadata exposure reused as dependency evidence.

## Message-Level Notes

1. Evidence is application-level rather than packet-level; the tested callbacks are generated through the in-repo FastAPI and service helpers.
2. The current implementation uses JSON request and callback payloads for EiJobObject, EiJobStatusObject, and EiJobResultObject.
3. No binary payload path was exercised, which is consistent with TS 103 988 Section 8.5 declaring binary data not applicable in this version.
4. No typed UEGeoandVel discriminator payloads were exercised because the repository does not yet implement the Section 8 typed unions and constraints objects.

## Limitation

This evidence supports current-state execution only. It does not close Section 8 clauses that require typed GadShapeType, VelocityDescType, GeoLocationType, VelocityType, ScopeIdentifier combinations, or EiJobConstraintsObject behavior.