# WP2 Status

- Planning/analysis (Steps 0–1) completed: responsibilities mapped, ADR alignment confirmed, observation strategy decided (wrap existing builder initially).
- Package skeleton (Step 2) created with placeholder modules (`context`, `state`, `spatial`, `agents`, `actions`, `observe`, `events`, `rng`, `systems`).
- Stateless helper extraction (Step 3) complete: spatial index and observation helpers migrated, event dispatcher formalised with unit tests.
- Step 4 in progress: enriched `AgentRegistry` with metadata/tick bookkeeping and implemented the new `WorldState` container (RNG seeding, ctx-reset queue, event buffering). Unit tests cover both modules.
- Step 5 kickoff: action schema/validation implemented with interim apply pipeline (`move`/`noop` mutations, structured events, invalid handling) plus unit coverage.
- Step 6 complete: world context now orchestrates queue, affordance, employment, relationship, economy, and perturbation systems using the modular pipeline; RNG streams are sourced from `RngStreamManager`, and the legacy `WorldState` exposes the port-friendly views (`agent_records_view`, `event_dispatcher`, `emit_event`) required by the new action pipeline. `WorldRuntime.tick` recognises the new facade, and parity tests cover queue reservation helpers plus the systems modules.
- WP1 Step 4 (loop refactor) deferred to this work package.
- Next: begin Step 7 (adapter & factory integration) so the simulation loop resolves the modular world context directly and the remaining legacy shims can be removed.

Update as tasks progress.

## Latest Progress (WorldContext integration)
- `WorldContext.tick` now mirrors the legacy runtime sequencing end-to-end: console draining, perturbation advance, modular action pipeline, ordered system execution, nightly reset, lifecycle evaluation, and event aggregation. Results are returned as `RuntimeStepResult`, so both direct tests and the legacy runtime path succeed.
- Legacy `WorldState` exposes the new port surface (`agent_records_view`, `event_dispatcher`, `emit_event`, `rng_seed`) and routes event emission through `EventDispatcher`, keeping telemetry/console expectations intact while enabling modular systems to emit structured events.
- Queue reservation helpers and the new systems modules (`queues`, `affordances`, `employment`, `relationships`, `economy`, `perturbations`) are wired into the context; dedicated unit suites under `tests/world/test_systems_*.py` plus `tests/test_world_context.py` now pass.
- World runtime detects when `context.tick` already returns a `RuntimeStepResult`, avoiding double construction and preserving compatibility with existing composition code.
