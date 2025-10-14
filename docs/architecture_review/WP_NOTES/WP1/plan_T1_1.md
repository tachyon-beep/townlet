# Plan – T1.1 / T3.x WorldContext Builder (2025-10-10)

## Goal
Replace the legacy world construction path with a modular `WorldContext` pipeline so `create_world` can return a runtime that already satisfies the WP1 port. This unblocks T1.2/T2.x and the remaining Step 7 work.

## Current State
- `world_factory._build_default_world` instantiates `WorldState`, wraps it in `LegacyWorldRuntime`, and injects an `ObservationBuilder` before returning `DefaultWorldAdapter`.
- `WorldState.__post_init__` already wires services (queue manager, employment, relationships, economy, perturbations) and attaches `WorldContext` to `self.context`, but callers still interact with the legacy runtime facade.
- `WorldContext` now implements `reset`, `tick`, `apply_actions`, `snapshot`, and DTO-supporting `observe`; the simulation loop can consume `context.observe` when the service is present.

## Execution Steps
1. **Builder helper**
   - Implement a factory function (e.g., `build_world_context(config: SimulationConfig, *, rng: Random | None, opts...) -> WorldContext`) that mirrors `WorldState.from_config` but returns the context and associated state/services.
   - Ensure RNG seeding, lifecycle, perturbations, and observations are initialised consistently with the legacy path.
2. **Factory integration**
   - Update `townlet.factories.world_factory._build_default_world` to call the new builder instead of creating `LegacyWorldRuntime`.
   - Adjust kwargs (`lifecycle`, `perturbations`, `ticks_per_day`, etc.) so callers pass configuration options rather than pre-built services.
   - Provide backward-compatible errors when legacy-only kwargs are supplied.
3. **Adapter refresh**
   - Update `DefaultWorldAdapter` to accept a `WorldContext` (or port implementation) directly and expose only the port methods (no `.world_state`).
   - Keep a thin compatibility layer so existing tests pass while we migrate remaining callers.
4. **Observation service wiring**
   - Ensure the context receives an observation service (re-using `ObservationBuilder` internally). Remove the loop-side bootstrap once Step 7 is complete.
5. **Testing**
   - Add unit tests under `tests/factories/test_world_factory.py` validating that `create_world()` returns a context-backed adapter emitting DTO envelopes.
   - Extend world/loop smokes to cover the new provider path.
6. **Documentation**
   - Update WP1 status/implementation plan with progress notes and capture any follow-up tasks (adapter removal, dummy providers).

## Risks / Considerations
- `SimulationLoop` still expects legacy attributes (`self.world` etc.); while migrating, maintain compatibility by exposing the underlying `WorldState` via adapter if required.
- Dummy/stub world providers need equivalent builders; plan to add them immediately after the default path works.
- Coordinate with WP3 tasks to ensure DTO schema updates remain aligned when the context becomes authoritative.
\n- Status: Executed 2025-10-10. Factory returns modular context adapter with observation service; legacy runtime path retained for compatibility.
