# Work Package: Manifest-Driven Affordance Preconditions & Hook Extensibility

## Objective
Enable gameplay designers to express affordance availability purely through manifest configuration by:
1. Evaluating `preconds` declared in YAML manifests at runtime.
2. Providing a general hook plug-in surface so new affordance hook names resolve without core code edits.
3. Documenting developer and ops workflows for new affordances (preconditions + hooks).

## Phase 1 — Preconditions Evaluation Engine
- **Step 1: Requirements & Schema Audit**
  - Review existing manifest files (`configs/affordances/**/*.yaml`) for current `preconds` usage.
  - Catalogue desired operators (e.g., equality, inequality, inventory checks, custom context). Confirm with design docs.
- **Step 2: Precondition DSL & Parser**
  - Define minimal expression grammar (e.g., `power_on == true`, `wallet >= 0.5`).
  - Implement parser/validator converting manifest strings into callable predicates.
  - Add parser unit tests covering valid/invalid expressions.
- **Step 3: Runtime Evaluation Integration**
  - Update `WorldState._start_affordance` (or helper) to evaluate preconditions before hook dispatch.
  - Provide evaluation context (agent snapshot, object, world tick, custom attributes).
  - On failure, short-circuit start and emit reason (e.g., `precondition_failed`).
- **Step 4: Hook Interop**
  - Ensure cancellation reasons bubble to hooks (`extra={"reason": "precondition_failed", "condition": "power_on == true"}`).
  - Allow hooks to override/augment decision if desired.
- **Step 5: Tests**
  - Add integration tests verifying preconditions block affordance start (success/failure cases).
  - Include regression for YAML load + evaluation pipeline.
- **Step 6: Telemetry & Console**
  - Emit telemetry events when preconditions fail (category `affordance_precondition_fail`).
  - Expose failure details in console `telemetry_snapshot` for ops visibility.

## Phase 2 — Hook Plug-in Ecosystem
- **Step 1: Discovery Strategy**
  - Decide on module resolution order: default hooks, environment variable (`TOWNLET_AFFORDANCE_HOOK_MODULES`), optional entry points.
  - Document how priority/ordering works.
- **Step 2: Error Handling & Observability**
  - Add logging around module import failures, duplicate hook registration, and handler errors (include stack traces behind debug flag).
  - Expose hook registry contents for diagnostics (`WorldState.list_affordance_hooks()`).
- **Step 3: Sample Modules & Templates**
  - Create `docs/samples/hooks/coffee_station.py` showcasing `register_hooks(new_world)` + simple handler.
  - Provide minimal test verifying `TOWNLET_AFFORDANCE_HOOK_MODULES=docs.samples.hooks.coffee_station` registers hook at runtime.
- **Step 4: Sandbox Testing**
  - Write scenario exercise enabling/disabling modules mid-run (if supported) to ensure deterministic behaviour.

## Phase 3 — Documentation & Ops Updates
- **Step 1: Manifest Authoring Guide**
  - Expand `docs/ops/OPS_HANDBOOK.md` and `docs/design/EMPLOYMENT...` (if applicable) with instructions for adding preconditions + hooks.
  - Include examples with expected telemetry/log outputs.
- **Step 2: Developer Guide**
  - Update engineering notes with API references (precondition DSL, hook plug-in API, troubleshooting).
  - Document unit/integration test patterns for new affordances.
- **Step 3: Tooling**
  - Extend `scripts/validate_affordances.py` to lint precondition syntax and flag unknown hook names.
  - Capture sample watcher/summary outputs demonstrating precondition failures as part of ops handbook.

## Phase 4 — Acceptance & Regression Plan
- Run end-to-end scenario(s) with new preconditions and custom hook modules.
- Verify telemetry, ops scripts, and docs reflect new behaviours.
- Update completion certificate / release notes once all steps pass review.

## Notes & Risks
- **Expression Complexity**: Keep DSL simple initially; defer nested expressions until needed.
- **Performance**: Precondition evaluation happens per affordance start—ensure parsed expressions are cached.
- **Security**: Avoid `eval`; use safe parsing to prevent arbitrary code execution.

