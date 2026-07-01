---
name: document-section-to-simulator-module-mapping
description: "Convert selected ORAN spec sections and diagram notes into concrete simulator module/function linkages and TDD-ready mapping outputs."
argument-hint: "spec section(s), protocol/interface keywords, and optional Feature-1 JSON"
user-invocable: true
---

# Document Section To Simulator Module Mapping

## Purpose
Create repeatable, high-confidence mappings from document sections to:
- required modules,
- functions to create or modify,
- linkages between functions across same or different modules,
- TDD verification targets.

This skill is ORAN-first and optimized for Feature-2 simulator implementation.

## Primary Inputs
- Section extracts and figure notes (example: Non_RT_RIC_A1_Interface_Design)
- Module taxonomy (List 1 Module Names)
- Feature-2 TDD constraints (TODO-F2-simulator-tdd)
- Optional upstream Feature-1 JSON fields:
  - test_id
  - component_targets
  - module_targets
  - expected_results
  - protocol_or_interface

## Output Artifacts
1. Mapping report (markdown)
2. Mapping manifest (json)

## Procedure
1. Normalize source section content
- Keep section identifier, title, and key behavioral statements.
- Convert diagram role arrows into directional text.

2. Infer interface and role model
- Identify A1, O1, E2, or Generic Functional API scope.
- Resolve consumer/producer directionality and request/response semantics.

3. Resolve required modules
- Apply deterministic List-1 mapping rules.
- Preserve module identifiers exactly as List-1 names.

4. Resolve function responsibilities
- Map each interface behavior to route layer, service layer, runtime primitives, and persistence responsibilities.
- Tag each function as create, modify, or extend.

5. Build linkage graph
- Same-module linkage: route -> service -> persistence/state update.
- Cross-module linkage: orchestrator dispatch using protocol_or_interface and module_targets.
- Event linkage: state transitions, timers, alerts, buffers, and output streaming hooks.

6. Emit report and manifest
- Report includes rationale and confidence notes.
- Manifest is machine-readable for TDD scaffolding and traceability.

7. Validate and score
- Ensure every interface statement has at least one module pair and function group.
- Flag ambiguous mappings with manual-review_required=true.

8. Improve ruleset after run
- Log misses and refinements.
- Version mapping rules when behavior changes.

## ORAN-First Scope Guardrails
- Primary simulator module for current phase: NEAR_RT_RIC.
- Other modules remain orchestrator-controlled stubs unless explicitly promoted.
- Feature-2 initial focus: A1-P, O1, E2.
- A1-EI stays deferred unless explicitly requested.

## Confidence Heuristics
- High confidence:
  - direct interface keyword + explicit module roles in source text.
- Medium confidence:
  - interface keyword present but roles implied by architecture conventions.
- Low confidence:
  - generalized statements without concrete role or endpoint context.

## Quality Checklist
- Module identifiers match List-1 exactly.
- Mapping manifest includes test_id when available.
- Function groups include linkage chains and verification checks.
- Deferred scope items are explicitly tagged.

## Reuse And Learning
- Keep rules in mapping_rules.oran.v1.json.
- Record each run delta in run_improvement_log.md.
- When rules change materially, copy to next version file (v2, v3) with change note.

## Mandatory Traceability Gate
- Before proposing code changes from section-to-module mappings, map findings to Trace IDs in `ORAN/docs/feature_traceability_map.md`.
- If no matching Trace ID exists, stop and request traceability mapping alignment first.
