# WP1 Pre-Compact Brief — 2025-10-10

## Current Focus
- WP1 remediation continues; world factory and adapter operate solely on `WorldContext`, with adapter coverage added in `tests/adapters/test_default_world_adapter.py` to lock in `reset`/`tick`/`observe` semantics.
- T4.4b is midway through: the loop emits a DTO-first `global_context`, `TelemetryPublisher._ingest_loop_tick`/`_capture_affordance_runtime` now populate snapshots directly from it, `TelemetryAggregator`/`StreamPayloadBuilder` accept the context payload, and console snapshot wiring prefers dispatcher data before falling back to legacy getters.
  - Regression suites (`tests/telemetry/test_aggregation.py`, `tests/test_telemetry_surface_guard.py`, `tests/test_console_commands.py`) cover the DTO ingestion path.
  - Remaining T4.4b work: migrate observer/dashboard/CLI consumers to the DTO context (with refreshed fixtures) and update telemetry docs once those surfaces no longer invoke `latest_*` getters.
- `tests/core/test_sim_loop_modular_smoke.py` continues to verify DTO envelopes plus console telemetry on default providers; broader UI/CLI tests still exercise the legacy pathway until the DTO migration lands.

## Strategic Guidance
The broader intent is to finish the port-first composition root so the simulation loop, factories, and telemetry stack behave as a thin orchestration shell. Every remaining task should move us toward deterministic, DTO-native ports: no legacy `WorldState` reach-ins, deterministic RNG management owned by the context, and console/telemetry flows expressed purely as events. Keep the end goal in mind—when WP1 closes, downstream packages must be able to plug into world/policy/telemetry ports without encountering legacy shims or hidden state.

## Outstanding Work
- T5.x: add dummy world/policy/telemetry providers plus loop/console/health-monitor smokes.
- T4.4: telemetry flow now fully DTO-driven.
  - **T4.4b remainder:** documentation refresh + guard notes now that publisher/aggregator/UI/CLI tests are DTO-only.
  - **T4.4c:** completed 2025-10-11 — health payload now includes structured `transport`/`global_context` data with alias fallbacks (see `T4_4c_health_schema.md` for schema details).
  - **T4.4d:** completed 2025-10-11 — failure payload mirrors the health schema (structured transport/context, alias block, optional health snapshot); see `T4_4d_failure_schema.md`. Alias removal deferred until dashboards/CLI migrate.
- **T1.3:** completed 2025-10-11 — world factory no longer accepts legacy service kwargs; lifecycle/perturbation wiring is owned by the provider and loop callers rely on adapter accessors.
- **T1.4/T1.5:** completed 2025-10-11 — factory tests assert DTO observation envelopes/events and invalid providers raise `ConfigurationError`; missing config continues to raise `TypeError`.
- Documentation & parity: expand DTO parity harness/tests for the context (T3.x), refresh ADRs, and capture the strategic changes in WP1/WP2/WP3 briefs once the remaining tasks converge.

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
