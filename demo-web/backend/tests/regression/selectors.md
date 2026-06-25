# Regression Selectors for Commit 94006fa

## Targeted smoke run

```powershell
cd demo-web/backend
pytest -q \
  tests/component/api/test_problem_details_component.py \
  tests/unit/services/test_a1_policy_service.py \
  tests/unit/services/test_a1_service_registry.py \
  tests/interface/api/test_oran_a1_policy_api.py \
  tests/module/oran/test_a1_service_flow.py \
  tests/feature/test_a1_service_selection_feature.py \
  tests/e2e/test_a1_policy_workflow_e2e.py
```

## Non-functional perspectives

```powershell
cd demo-web/backend
pytest -q \
  tests/nonfunctional/parameter/test_a1_policy_parameter_passing.py \
  tests/nonfunctional/load/test_a1_policy_load.py \
  tests/nonfunctional/stress/test_a1_policy_stress.py \
  tests/nonfunctional/memory/test_a1_policy_memory_behavior.py
```

## Full changed-area run

```powershell
cd demo-web/backend
pytest -q \
  tests/component/api/test_problem_details_component.py \
  tests/unit/services/test_a1_policy_service.py \
  tests/unit/services/test_a1_service_registry.py \
  tests/interface/api/test_oran_a1_policy_api.py \
  tests/module/oran/test_a1_service_flow.py \
  tests/feature/test_a1_service_selection_feature.py \
  tests/e2e/test_a1_policy_workflow_e2e.py \
  tests/nonfunctional/parameter/test_a1_policy_parameter_passing.py \
  tests/nonfunctional/load/test_a1_policy_load.py \
  tests/nonfunctional/stress/test_a1_policy_stress.py \
  tests/nonfunctional/memory/test_a1_policy_memory_behavior.py
```
