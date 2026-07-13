# TS 103 988 Section 9 Protocol and Message Evidence

1. The service now normalizes the route alias `UEGeoandVel` to the canonical Section 9 EI type identifier `ORAN_UEGeoandVel_3.0.1` before storage and status handling.
2. The `UEGeoandVel` job definition now requires the compound Section 9 shape with `scope.ueId` and `ueGeoandVelEIDescription`.
3. Numeric bounds for `granularityPeriod`, `reportingPeriod`, and `reportingAmount` are enforced at the model layer.
4. The constraints payload now exposes the canonical Section 9 property `supportedVelocityTypes`, while still accepting the legacy internal field name for compatibility.
5. The result validator now requires a non-empty array for the Section 9-specific result payload and rejects malformed entries before callback delivery.
6. Focused API tests confirm that missing `scope` and invalid `gadShape` values are rejected with deterministic `application/problem+json` error responses.
