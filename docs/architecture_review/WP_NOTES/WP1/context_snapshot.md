# WP1 Context Snapshot — 2025-10-11

This snapshot captures the state of WP1 after the recent port/WorldContext cleanup
so the next session can resume without re-auditing.

## What’s Done
- **WorldContext orchestration**: `WorldContext.tick` now owns action staging,
  console execution, modular system steps, nightly reset cadence, and
  per-agent `episode_tick` updates. Tests `tests/test_world_context.py` and
  `tests/world/test_world_context_parity.py` verify the behaviour against legacy
  expectations.
- **Observation pipeline**: `WorldContext.observe` produces DTO envelopes
  (per-agent needs/wallet/job/inventory/pending intent) and global snapshots.
  The loop consumes these envelopes directly (fallback removed). Documentation is
  captured in `WC_A_tick_flow.md` and `WC_E_observation_mapping.md`.
- **Console path**: `ConsoleRouter.enqueue` no longer mirrors commands through
  `runtime.queue_console`; `SimulationLoop` passes envelopes directly into
  `runtime.tick(console_operations=...)`. Adapters/dummy runtimes treat
  `queue_console` as obsolete. `tests/test_console_router.py` and
  `tests/orchestration/test_console_health_smokes.py` cover the router-only flow.
- **Port contract**: `townlet.ports.world.WorldRuntime` is the sole runtime port;
  the legacy alias in `core.interfaces` has been removed. Guard test
  `tests/core/test_world_port_imports.py` prevents reintroduction of the old
  import. `PB_port_contract.md` describes the current API.
- **Dummy providers**: `townlet.testing` exposes dummy world/policy/telemetry
  implementations. Smokes `tests/core/test_sim_loop_with_dummies.py` and
  `tests/test_ports_surface.py` validate the port surfaces and DTO flow.
- **Telemetry payloads**: `loop.tick` emits DTO-backed `global_context`, while
  `loop.health`/`loop.failure` now expose structured payloads (transport +
  DTO context + summary metrics) without legacy alias fields. Summary values
  replace the former `telemetry_*` keys, and publisher/client fallbacks convert
  older alias-based payloads on ingest.

## Remaining WP1 Work
1. **Telemetry documentation refresh**: update ADR-001, console/monitor docs,
   and WP1 README/status to describe the new `summary` payload and the alias
   fallback path for historical data.
2. **Policy identity/events**: migrate remaining identity updates off direct
   world/telemetry mutation (emit through dispatcher events) in coordination with
   WP3 Stage 6.
3. **Regression sweep**: after the documentation and dispatcher work, run full
   `pytest`, `mypy`, and `ruff` to ensure no stragglers.
4. **Release notes**: summarise the port/telemetry changes for downstream teams
   (tie into Stage 6 deliverables).

## Useful Regression Commands
- DTO + console telemetry bundle:
  `pytest tests/telemetry/test_aggregation.py tests/test_telemetry_surface_guard.py \
          tests/test_console_events.py tests/test_console_commands.py \
          tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py \
          tests/orchestration/test_console_health_smokes.py \
          tests/test_console_router.py tests/core/test_sim_loop_modular_smoke.py \
          tests/core/test_sim_loop_with_dummies.py -q`
- World context & parity:
  `pytest tests/test_world_context.py tests/world/test_world_context_parity.py \
          tests/core/test_sim_loop_dto_parity.py -q`

## Dependencies
- WP2 cleanup depends on completing WP3 Stage 6 (DTO-only policy/training adapters).
- Telemetry alias removal should align with the Stage 6 documentation release so
  dashboards/CLI have a migration window.

Keep this snapshot handy after compaction to resume WP1 follow-up work quickly.
