# Adapter Surface Cleanup Plan

## Background
Stage 6 reports that adapters no longer expose internal implementations (e.g. `ScriptedPolicyAdapter.backend`, `SimulationLoop.policy_controller`, `DefaultWorldAdapter.context`). These properties remain in the repository, enabling legacy access to world/policy internals and complicating DTO-only enforcement.

## Current State Audit
- `SimulationLoop._build_policy_components` relies on `ScriptedPolicyAdapter.backend` to construct `PolicyController` (`src/townlet/core/sim_loop.py:404-418`).
- `SimulationLoop.policy_controller` property exposes the controller facade (`src/townlet/core/sim_loop.py:460-465`).
- `DefaultWorldAdapter` still exposes `context` and other transitional properties (`src/townlet/adapters/world_default.py:94-131`).
- Orchestration/tests reach through these helpers (e.g. policy possession checks, world context fixtures).
- Docs (WP3 status) claim these surfaces were already removed, indicating intended end-state.

## Implementation Plan

### 1. Capability Mapping
1.1 Audit current usages with `rg "\.policy_controller" src tests` and
    `rg "\.backend" src tests`.
1.2 For each hit, categorise: read-only metadata access, control operations, or
    test-only assertions.
1.3 Define replacement APIs:
    - Policy metadata: extend `PolicyComponents` to expose
      `decision_backend.latest_policy_snapshot()` and other needed methods via
      explicit methods.
    - Control hooks (anneal ratio, possession): ensure `SimulationLoop` forwards
      to controller internally and expose targeted methods (`set_anneal_ratio`,
      etc.) already on the loop.
    - Tests requiring internals: design fixtures returning lightweight stubs or
      dataclasses rather than the adapter objects.

### 2. SimulationLoop Refactor
2.1 In `_build_policy_components`, stop reading `policy_port.backend`; instead,
    require `create_policy` to return both `port` and `controller` (adjust port
    factory as needed).
2.2 Remove the `policy_controller` property entirely; replace internal uses with
    `_policy_controller` (private) and add targeted public methods (`set_anneal_ratio`,
    `active_policy_hash`, etc.) that proxy safely.
2.3 Update snapshot helpers to obtain policy metadata via an injected
    `PolicyInfoProvider` interface rather than the controller property.
2.4 Acceptance: `rg "policy_controller" src/townlet/core/sim_loop.py` only
    shows private attribute usage.

### 3. ScriptedPolicyAdapter Cleanup
3.1 Remove `backend` property and `_world_provider` attribute.
3.2 Replace `attach_world` with a DTO-friendly service registration (e.g.
    handing in `WorldObservationService`).
3.3 Update `decide` to pull any required world data from the provided DTO
    envelope, failing fast if data missing.
3.4 Update adapter tests to assert the property is absent (`hasattr` check).

### 4. DefaultWorldAdapter Slimming
4.1 Remove `.context`, `.lifecycle_manager`, `.perturbation_scheduler` from the
    public API.
4.2 Introduce dedicated helper functions in tests that require lifecycle or
    perturbation handles (e.g. `tests/helpers/world_adapter.py`).
4.3 Update runtime code to access lifecycle/perturbations via dedicated
    services, not adapter properties.
4.4 Acceptance: `rg "\.context" src/townlet/adapters/world_default.py` returns
    only internal usage; no external references remain.

### 5. Consumer Migration
5.1 Update `townlet/orchestration/policy.py` to construct `PolicyController`
    directly using new factory outputs.
5.2 Refactor tests that reach into adapter internals; replace with DTO fixtures
    or direct backend references.
5.3 Update scripts (training harnesses, demos) to use new APIs.

### 6. Guard Rails & Docs
6.1 Add `tests/test_adapter_public_surface.py` verifying forbidden attributes
    raise `AttributeError`.
6.2 Document the intended public surface in module docstrings and `README`s.
6.3 Update architecture notes to reflect new contracts.

### 7. Validation Sequence
- `rg "\.policy_controller" src tests`
- `rg "\.backend" src tests`
- `pytest tests/adapters/ -q`
- `pytest tests/orchestration/test_policy_controller_dto_guard.py -q`
- `pytest tests/core/test_sim_loop_modular_smoke.py tests/core/test_sim_loop_with_dummies.py -q`

## Validation Checklist
- [ ] `pytest tests/adapters/ -q`
- [ ] Policy integration suites: `pytest tests/policy/test_scripted_behavior_dto.py tests/policy/test_training_orchestrator_capture.py tests/orchestration/test_policy_controller_dto_guard.py -q`
- [ ] Simulation loop smokes: `pytest tests/core/test_sim_loop_modular_smoke.py tests/core/test_sim_loop_with_dummies.py -q`
- [ ] `grep` confirms removal of the deprecated attributes (e.g. `rg "\.policy_controller" src/ tests/`).

## Risks & Mitigations
- **Hidden consumers:** internal tooling may still rely on adapter internals; create a temporary compatibility report by instrumenting attribute access before removal.
- **Test brittleness:** fixtures that patch adapter state may need redesign; allocate time to build helper factories.
- **PolicyController lifecycle:** ensure training harness still receives the controller when required; if necessary, expose a targeted accessor via the policy provider instead of the loop.

## Dependencies
- Console queue dismantling must be complete to avoid refactoring code that still depends on the shim.
- ObservationBuilder retirement (workstream 3) depends on adapters offering DTO-only data, so must follow this cleanup.
