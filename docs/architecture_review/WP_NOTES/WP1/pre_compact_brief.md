# WP1 Pre-Compact Brief — 2025-10-11

## Current Focus
- WP1 remediation continues; world factory and adapter operate solely on `WorldContext`, with adapter coverage added in `tests/adapters/test_default_world_adapter.py` to lock in `reset`/`tick`/`observe` semantics.
- T4.4b completed: the loop emits a DTO-first `global_context`, publisher/aggregator/CLI/observer consumers rely on dispatcher DTO data, and documentation now references the DTO flow. Regression bundle (`pytest tests/telemetry/test_aggregation.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py -q`) is recorded.
- `tests/core/test_sim_loop_modular_smoke.py` continues to verify DTO envelopes plus console telemetry on default providers; broader UI/CLI tests still exercise the legacy pathway until the DTO migration lands.

## Strategic Guidance
The broader intent is to finish the port-first composition root so the simulation loop, factories, and telemetry stack behave as a thin orchestration shell. Every remaining task should move us toward deterministic, DTO-native ports: no legacy `WorldState` reach-ins, deterministic RNG management owned by the context, and console/telemetry flows expressed purely as events. Keep the end goal in mind—when WP1 closes, downstream packages must be able to plug into world/policy/telemetry ports without encountering legacy shims or hidden state.

## Outstanding Work
- Immediate focus: unblock WP3 Stage 6 so its regression sweep can run clean.
  The unfinished WP1/WP2 refactor fallout currently breaks the full suite; fix or
  finish those changes so `pytest` passes.
- Once WP3 Stage 6 is complete (full suite + ruff + mypy + docs), return here to
  finish Step 8 (documentation refresh, dispatcher-based policy identity events,
  full regression sweep, release notes).

## WorldContext Summary
- Modular tick orchestration, observation envelopes, and snapshot exports now live entirely inside `WorldContext`. Tests (`tests/test_world_context.py`, `tests/world/test_world_context_parity.py`) verify action staging, nightly reset cadence, and per-agent `episode_tick` updates.
- Documentation refreshed (`WC_A_tick_flow.md`, `WC_E_observation_mapping.md`); remaining loop references to `WorldState` are read-only metrics collection (`hunger_levels`, etc.).

## Dependences / Notes
- Context wiring currently depends on the factory ensuring `observation_service` is configured; adapter.observe now proxies DTO envelopes directly from the context and adapter tests guard the behaviour.
- Telemetry/policy DTO work (WP3) remains active—keep schema alignment in mind while removing residual legacy helpers, especially around RNG determinism and policy snapshot events.

## Helpful Paths
- Factory tests: `tests/factories/test_world_factory.py`
- World context tests: `tests/test_world_context.py`, `tests/world/test_world_context_observe.py`
- Simulation loop parity: `tests/core/test_sim_loop_dto_parity.py`
- Modular smoke: `tests/core/test_sim_loop_modular_smoke.py`

Use this as reorientation after compaction.

## Telemetry Health Inventory Update (2025-10-11 23:45)
- Health payloads now emit the structured schema: top-level `duration_ms`, nested `transport` (queue/backlog/workers), and embedded DTO `global_context` snapshots, while retaining alias fields (`telemetry_*`, `perturbations_*`, `employment_exit_queue`, `tick_duration_ms`) for backward compatibility.
- Metrics derive exclusively from `_build_transport_status` and DTO exports, removing the legacy `self.world.employment.exit_queue_length()` call. Scheduler counts serve only as defensive fallback when context data is missing.
- Telemetry publisher caches deep copies of the structured payload (`latest_health_status` exposes transport/global context), dispatcher queue history prefers the embedded context, and UI/CLI helpers pull queue/perturbation metrics from the structured fields before falling back to aliases.
- Regression bundle (`pytest tests/test_sim_loop_health.py tests/telemetry/test_event_dispatcher.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py tests/test_telemetry_watch.py -q`) passes on the new schema; alias removal is deferred until downstream dashboards migrate.
