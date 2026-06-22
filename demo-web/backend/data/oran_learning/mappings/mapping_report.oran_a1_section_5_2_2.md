# Mapping Report: oran-a1-s5_2_2-20260618-001

## Inputs
- Source docs:
  - ORAN/docs/ts_103987v040300p.pdf
  - ORAN/docs/List 1 Module Names.md
  - ORAN/TODO-F2-simulator-tdd.md
- Section refs:
  - ETSI TS 103 987, 5.2.2 (5.2.2.1 to 5.2.2.4)
- Optional test_id: null

## Required Modules
- NON_RT_RIC
- NEAR_RT_RIC
- SMO
- ORAN_INT_INFO_SOURCE
- O_CU_CP
- O_CU_DP
- O_DU
- O_ENODEB

## Function Plan

### Interface: A1-P
- Layer: Route
  - Action: modify
  - Functions:
    - post_simulator_a1_policy
- Layer: Route
  - Action: create
  - Functions:
    - list_simulator_a1_policy_types
    - get_simulator_a1_policy_type
    - put_simulator_a1_policy
    - list_simulator_a1_policy_ids
    - get_simulator_a1_policy_by_type
    - delete_simulator_a1_policy
    - get_simulator_a1_policy_status
    - notify_simulator_a1_policy_status
- Layer: Service
  - Action: extend
  - Functions:
    - list_policy_types
    - get_policy_type
    - is_supported_policy_type
    - upsert_policy
    - list_policy_ids
    - delete_policy
    - get_policy_status
    - append_policy_feedback
- Layer: Runtime
  - Action: extend
  - Functions:
    - callback_subscription state tracking in upsert_policy
    - policy_status lifecycle updates in append_policy_feedback
- Layer: Persistence
  - Action: extend
  - Functions:
    - in-memory policy storage by /policytypes/{policyTypeId}/policies/{policyId}

## Linkage Chains
1. a1_policytype_create_replace_flow
- route validates A1-P role pair NON_RT_RIC -> NEAR_RT_RIC
- route validates PolicyObject does not expose Near-RT internal function mapping
- service checks supported policy type and upserts policy at policy-type scoped key
- runtime updates PolicyStatusObject and callback subscription metadata

2. a1_policy_status_notification_flow
- route receives feedback notification payload
- service appends feedback and refreshes last_evaluated_at
- status endpoint returns updated PolicyStatusObject to consumer queries

## Verification Checks
- Functional roles enforce A1-P Consumer (NON_RT_RIC) to Producer (NEAR_RT_RIC).
- Both policy type discovery and schema retrieval exist via GET /policytypes resources.
- Policy resources use section-defined URI structure:
  - /policytypes
  - /policytypes/{policyTypeId}
  - /policytypes/{policyTypeId}/policies/{policyId}
  - /policytypes/{policyTypeId}/policies/{policyId}/status
- Callback URI (notificationDestination) is accepted and persisted when policy is created.
- PolicyObject rejects internal function details in request payload.

## Deferred Scope
- A1-EI service behavior (section 5.3)
- A1-ML service behavior
- JSON-schema strict validation against A1TD objects

## Confidence
- Level: high
- Rationale: Section 5.2.2 explicitly states role placement, URI resources, representation objects, and policy principles, enabling deterministic route/service mapping.
- Manual review required: false
