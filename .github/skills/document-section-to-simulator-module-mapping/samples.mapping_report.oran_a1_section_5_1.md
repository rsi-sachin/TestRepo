# Mapping Report: oran-a1-s5_1-20260618-001

## Inputs
- Source docs:
  - ORAN/docs/Non_RT_RIC_A1_Interface_Design.md
  - ORAN/docs/List 1 Module Names.md
  - ORAN/TODO-F2-simulator-tdd.md
- Section refs:
  - Section 5.1 and Figure 5.1-1
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
- Layer: Service
  - Action: create
  - Functions:
    - create_policy
    - update_policy
    - get_policy
    - delete_policy
    - notify_policy_status

### Interface: O1
- Layer: Service
  - Action: create
  - Functions:
    - publish_alarm
    - acknowledge_alarm
    - clear_alarm
    - get_alarm_history

### Interface: E2
- Layer: Service
  - Action: create
  - Functions:
    - ingest_e2_event
    - queue_e2_message
    - process_e2_message
    - send_e2_response

### Interface: ORCHESTRATOR
- Layer: Service
  - Action: create
  - Functions:
    - execute_scenario
    - resolve_module_targets
    - dispatch_by_interface
    - set_execution_mode

## Linkage Chains
1. same_module_route_to_service
- api route accepts validated request
- service resolves interface behavior
- persistence records object lifecycle
- runtime state is updated

2. cross_module_orchestrated_dispatch
- orchestrator receives scenario command
- module targets are resolved
- interface service dispatch occurs
- target module state transition is persisted

## Verification Checks
- A1-P mapping uses NON_RT_RIC -> NEAR_RT_RIC role pair.
- O1 mapping captures monitoring/alarms to SMO.
- E2 mapping captures RAN nodes to NEAR_RT_RIC interactions.
- Deferred scope is explicit.

## Deferred Scope
- A1-EI behavior implementation
- A1-ML API definition

## Confidence
- Level: high
- Rationale: direct role statements in section text and figure, reinforced by List-1 module taxonomy.
- Manual review required: false
