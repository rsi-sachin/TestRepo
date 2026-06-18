# ORAN TODO Index - Parallel Feature Tracks

Project: Extend demo-web with O-RAN A1 test generation and simulator creation capabilities
Last Updated: June 2026
Tracking Mode: ORAN-only split with 2 feature TODO files

## Feature Files

- [Feature 1 TODO - Specification Ingestion and Test Plan JSON](TODO-F1-spec-ingestion.md)
- [Feature 2 TODO - Component Simulator via TDD](TODO-F2-simulator-tdd.md)

## Feature Linkage

- Feature 1 is upstream and produces normalized JSON test plan data with test-case, component, and module targets.
- Feature 2 is downstream and must select simulator targets only from Feature 1 outputs.
- Dependency flow: Feature 1 output -> Feature 2 target selection -> TDD simulator implementation.

## Feature Status Snapshot

| Feature | Status |
|---|---|
| Feature 1: Specification Ingestion and Test Plan JSON | IN PROGRSES |
| Feature 2: Component Simulator via TDD | NOT STARTED |

## Notes

- This is a compact index-only file.
- Detailed legacy sections have been moved into the feature TODO files.
