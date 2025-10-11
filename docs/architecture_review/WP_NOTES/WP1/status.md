# WP1 Status

**Current state (2025-10-11)**
- Port protocols and registry scaffolding remain in place, and `WorldContext` now supports DTO observation envelopes. The default world factory rejects the legacy `runtime=` shortcut and always returns a context-backed adapter; `DefaultWorldAdapter` is context-only (legacy `.world_state`/runtime handles removed) with dedicated tests in `tests/adapters/test_default_world_adapter.py`.
- `SimulationLoop` resolves world/policy/telemetry components exclusively through the factories (with injectable overrides for tests), consumes DTO envelopes directly from `WorldContext.observe`, and now routes console telemetry via dispatcher events (T4.2b). Queue, employment, and job snapshots are sourced via `WorldContext.export_*` helpers (legacy `_collect_*` collectors retired); `loop.tick` emits a DTO-backed `global_context` snapshot consumed across the telemetry pipeline, `TelemetryAggregator`/`StreamPayloadBuilder` accept the context payload, and console/CLI/observer consumers now rely on dispatcher DTO data (regression bundle covers the new path). Remaining T4.4b work is documentation hygiene before moving to failure payload cleanup. The modular smoke in `tests/core/test_sim_loop_modular_smoke.py` covers DTO envelopes plus console routing on default providers.
- **New 2025-10-11:** T4.4c landed — `loop.health` now emits a structured DTO-aware payload (`transport` + embedded `global_context`) alongside alias fields for backwards compatibility. Telemetry publisher/dispatcher, UI dashboards, and CLI helpers read the structured data first, and the dedicated regression bundle (`pytest tests/test_sim_loop_health.py tests/telemetry/test_event_dispatcher.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py tests/test_telemetry_watch.py -q`) passes on the new schema.
- **New 2025-10-11 (cont.):** T4.4d completed — failure events now mirror the health schema (structured transport/context block, alias fallback, optional cached health snapshot). Regression bundle (`pytest tests/test_sim_loop_health.py tests/test_run_simulation_cli.py tests/telemetry/test_event_dispatcher.py tests/test_telemetry_worker_health.py tests/test_telemetry_internal_metrics.py tests/test_console_commands.py tests/test_conflict_telemetry.py -q`) covers the new payload.
- **New 2025-10-11 (add):** T1.3 finished — `create_world` no longer accepts legacy service kwargs; the default provider constructs lifecycle/perturbation plumbing internally and exposes them through the adapter for the loop to reuse.
- Console routing always flows through `ConsoleRouter`, with buffered commands dropped (and logged) if the router is unavailable; telemetry ingestion happens through `console.result` events, and legacy `record_console_results` shims stay unused. Snapshot commands now return structured results derived from `SnapshotState`. The DTO regression subset (`pytest tests/telemetry/test_aggregation.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py -q`) is part of the routine validation.
- WC3 (telemetry/policy DTO work) unlocked the observation pipeline and telemetry guards (`tests/core/test_no_legacy_observation_usage.py`, `tests/test_telemetry_surface_guard.py`). Outstanding WP3C items (training adapters, DTO-only parity sweeps) still block the final removal of remaining legacy world handles.

- Execute T4.4d to reshape loop failure payloads (structured transport/context + doc refresh) now that health events are DTO-first.
- Deliver T5.x dummy world/policy/telemetry providers and associated loop/console/health-monitor smokes.
- Update documentation (ADR-001, console/monitor ADR, WP1 README/status) after the adapter/loop cleanup converges.

**Legacy caller inventory (updated 2025-10-10)**
- Policy:
  - `PolicyController` owns ctx-reset/anneal hooks; decision path still hands the legacy `WorldState` into scripted backends. Switch to DTO-only requests once WP3C Stage 3D/Stage 5 land.
  - Training orchestrator now streams DTO frames, but replay exports keep the legacy translator until downstream consumers ingest the new JSON artefacts.
- Telemetry:
  - Loop identity (`runtime.variant`, `policy_info`) still mutated directly; convert these to dispatcher events post-WP3C.
  - Console history is still sourced from telemetry for parity; once DTO-only command routing is validated, drop the getter usage.
  - Health/failure events now include structured DTO payloads; retire alias fields once dashboards/CLI migrate (tracked under T4.4 follow-ups).
- World:
- Direct `WorldState` mutations (pending intent/agent state writes) remain; replace them with `ConsoleRouter` queues and `WorldContext` helpers once DTO guardrails are in place.
  - Provider metadata is correct, but the default loop retains `self.world` for legacy observers; plan to cull after WP3 Stage 5 removes the observation dict.

Keep this file in sync with WP2/WP3 dependencies as Step 8 progresses.
