# WP1 Status

**Current state (2025-10-11)**
- Port protocols and registry scaffolding remain in place, and `WorldContext` now supports DTO observation envelopes. The default world factory rejects the legacy `runtime=` shortcut and always returns a context-backed adapter; `DefaultWorldAdapter` is context-only (legacy `.world_state`/runtime handles removed) with dedicated tests in `tests/adapters/test_default_world_adapter.py`.
- `SimulationLoop` resolves world/policy/telemetry components exclusively through the factories (with injectable overrides for tests), consumes DTO envelopes directly from `WorldContext.observe`, and routes console telemetry via dispatcher events (T4.2b). Queue, employment, and job snapshots are sourced via `WorldContext.export_*` helpers (legacy `_collect_*` collectors retired); `loop.tick` emits a DTO-backed `global_context` snapshot consumed across the telemetry pipeline, `TelemetryAggregator`/`StreamPayloadBuilder` accept the context payload, and console/CLI/observer consumers rely on dispatcher DTO data. Regression bundle (`pytest tests/telemetry/test_aggregation.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py -q`) captures the DTO path. The modular smoke in `tests/core/test_sim_loop_modular_smoke.py` covers DTO envelopes plus console routing on default providers.
- `WorldContext` parity sweeps: new regression tests (`tests/test_world_context.py`, `tests/world/test_world_context_parity.py`) ensure queue metrics/state, relationship snapshots/metrics, economy exports, and per-agent `episode_tick` counters match the modular services (run via `pytest tests/world/test_world_context_parity.py -q`). Documentation (`WC_A_tick_flow.md`, `WC_E_observation_mapping.md`) now reflects the modular implementation.
- **New 2025-10-11:** T4.4c landed — `loop.health` now emits a structured DTO-aware payload (`transport` + embedded `global_context` + `summary` metrics). Telemetry publisher/dispatcher, UI dashboards, and CLI helpers read the structured data first, and the dedicated regression bundle (`pytest tests/test_sim_loop_health.py tests/telemetry/test_event_dispatcher.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py tests/test_telemetry_watch.py -q`) passes on the new schema. Historical alias-only payloads are converted into the summary during ingest.
- **New 2025-10-11 (cont.):** T4.4d completed — failure events now mirror the health schema (structured transport/context block + summary, optional cached health snapshot). Regression bundle (`pytest tests/test_sim_loop_health.py tests/test_run_simulation_cli.py tests/telemetry/test_event_dispatcher.py tests/test_telemetry_worker_health.py tests/test_telemetry_internal_metrics.py tests/test_console_commands.py tests/test_conflict_telemetry.py -q`) covers the new payload.
- **New 2025-10-11:** T1.4 + T1.5 landed — factory/unit tests now assert DTO observation envelopes/events and invalid provider inputs raise `ConfigurationError`; missing config continues to raise `TypeError`.
- **New 2025-10-11:** T5.1–T5.3 delivered — `townlet.testing` exposes dummy world/policy/telemetry implementations wired through factory providers and guarded by `tests/test_ports_surface.py`.
- **New 2025-10-11:** T5.4 delivered — `tests/helpers/dummy_loop.py` builds a dummy loop harness and `tests/core/test_sim_loop_with_dummies.py` exercises two-tick DTO parity, console routing, and health telemetry using the new providers (regression: `pytest tests/test_ports_surface.py tests/core/test_sim_loop_with_dummies.py -q`).
- **New 2025-10-11:** Telemetry stub compatibility locked down — factory/port registries are restored after tests so the built-in `stub` provider continues to return `StubTelemetrySink`. The new regression `tests/test_telemetry_stub_compat.py` ensures console snapshots, snapshot saves, and demo seeding succeed under both stdout and stub transports (and surfaces the stub warning banner), preventing Stage 6 DTO payloads from regressing when transports swap.
- **New 2025-10-11:** Console services are now provided by the factory and owned by orchestration. `WorldComponents` carries the service, the loop holds a reference, and `TelemetryPublisher` captures dispatcher-emitted results (no `_console_results_batch` mirrors). Coverage across `tests/test_console_router.py`, `tests/test_console_commands.py`, `tests/test_console_dispatcher.py`, and `tests/test_telemetry_new_events.py` keeps the event-only flow honest.
- **New 2025-10-11 (add):** T1.3 finished — `create_world` no longer accepts legacy service kwargs; the default provider constructs lifecycle/perturbation plumbing internally and exposes them through the adapter for the loop to reuse.
- **New 2025-10-11:** Step 7 metadata guard landed — `tests/test_factory_registry.py::test_simulation_loop_provider_metadata` now asserts `SimulationLoop.provider_info` reflects the resolved world/policy/telemetry providers, and the stub-path test verifies `policy_provider_name` / `telemetry_provider_name` continue to drive the `is_stub_*` helpers.
- **New 2025-10-11:** Factory fallbacks upgraded — the optional `pytorch` and `http` providers now surface stub adapters when dependencies are missing, keeping `SimulationLoop` port-neutral while still reporting the requested provider in `provider_info` for audits and tests.
- **New 2025-10-11:** T6.2 delivered — loop/factory/type hints now point to `townlet.ports.world.WorldRuntime`. The legacy `WorldRuntimeProtocol` alias has been retired. Port surface tests (`pytest tests/test_factory_registry.py tests/test_core_protocols.py tests/test_ports_surface.py -q`) assert the contract.
- **New 2025-10-11:** T6.3 delivered — `tests/core/test_world_port_imports.py` guards against reintroducing the old alias anywhere under core/factories/orchestration/testing/telemetry.
- Console routing always flows through `ConsoleRouter`, with buffered commands dropped (and logged) if the router is unavailable; telemetry ingestion happens through `console.result` events, and legacy `record_console_results` shims stay unused. Snapshot commands now return structured results derived from `SnapshotState`. The DTO regression subset (`pytest tests/telemetry/test_aggregation.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py -q`) is part of the routine validation.
- WC3 (telemetry/policy DTO work) unlocked the observation pipeline and telemetry guards (`tests/core/test_no_legacy_observation_usage.py`, `tests/test_telemetry_surface_guard.py`). Outstanding WP3C items (training adapters, DTO-only parity sweeps) still block the final removal of remaining legacy world handles.

- Execute T4.4d to reshape loop failure payloads (structured transport/context + doc refresh) now that health events are DTO-first.
- T5.x coverage complete: dummy providers, loop smokes, and `tests/orchestration/test_console_health_smokes.py`
  now guard console routing and health monitor metrics via the dummy harness (regression: `pytest`
  `tests/test_ports_surface.py tests/core/test_sim_loop_with_dummies.py tests/orchestration/test_console_health_smokes.py -q`).
- PB-A locked in the revised `WorldRuntime` port contract (`PB_port_contract.md`). PB-B/C executed on 2025-10-11: adapters/dummies no longer expose `queue_console`, `SimulationLoop` relies solely on DTO pathways, and port surface tests confirm the lean contract. Next PB steps (PB-D/E/F) will swap loop imports to `townlet.ports.world.WorldRuntime`, add guard tests, and prune the deprecated protocol alias. Update documentation (ADR-001, console/monitor ADR, WP1 README/status) after the port cleanup convergence.

**Blocking dependency (2025-10-11 insight, updated)**
- WP1 finalisation (Step 8 and telemetry docs/ADR refresh) now depends on WP3
  Stage 6 completing the remaining close-out tasks (ruff/mypy sweep,
  documentation refresh, release comms). The full `pytest` suite is green after
  the port-registry restoration, so coordinate the lint/type/doc work with WP3
  before locking Step 8.
- **WP1↔︎WP3 handoff (execute post Stage 6):**
  1. `SimulationLoop`, `PolicyController`, and adapters must emit policy identity/variant updates solely via dispatcher events (`policy.metadata`, `policy.possession`, `policy.anneal.update`). No direct calls to `TelemetrySink.update_policy_identity` or `set_runtime_variant`; extend `tests/test_telemetry_surface_guard.py` to enforce.
  2. DTO envelopes are the only observation payload delivered to policy/training paths. `SimulationLoop.policy_controller.decide` should require an `ObservationEnvelope`, and guard tests (`tests/core/test_no_legacy_observation_usage.py`, policy parity smokes) must fail if a legacy observation dict is requested.
  3. Telemetry/ADR docs capture the dispatcher-driven identity flow and reference the DTO schema appendix. Release notes highlight removal of legacy identity getters and the DTO-only requirement for downstream consumers.

**Close-out sequence (post WP3 Stage 6)**
1. Update dispatcher identity flow & DTO guard tests (per handoff above).
2. Run full regression sweep: `pytest`, `ruff check src tests`, `mypy src`.
3. Refresh ADR-001, console/monitor ADR, WP1 README/status, and publish release notes summarising port + DTO changes.

**Legacy caller inventory (updated 2025-10-10)**
- Policy:
  - `PolicyController` owns ctx-reset/anneal hooks; decision path still hands the legacy `WorldState` into scripted backends. Switch to DTO-only requests once WP3C Stage 3D/Stage 5 land.
  - Training orchestrator now streams DTO frames, but replay exports keep the legacy translator until downstream consumers ingest the new JSON artefacts.
- Telemetry:
  - Loop identity (`runtime.variant`, `policy_info`) still mutated directly; convert these to dispatcher events post-WP3C.
  - Console history is still sourced from telemetry for parity; once DTO-only command routing is validated, drop the getter usage.
  - Health/failure events now include structured DTO payloads with a `summary` block; documentation refresh remains to highlight the new schema and the legacy alias fallback for archived data (tracked under T4.4 follow-ups).
- World:
- Direct `WorldState` mutations (pending intent/agent state writes) remain; replace them with `ConsoleRouter` queues and `WorldContext` helpers once DTO guardrails are in place.
  - Provider metadata is correct, but the default loop retains `self.world` for legacy observers; plan to cull after WP3 Stage 5 removes the observation dict.

Keep this file in sync with WP2/WP3 dependencies as Step 8 progresses.

---

## WP3 Stage 6 Recovery Completion (2025-10-13)

**✅ UNBLOCKED**: WP3 Stage 6 Recovery (WP3.1) has been completed, clearing all blockers for WP1 Step 8.

**What was completed:**
- Console queue shim (`queue_console_command` / `export_console_buffer`) fully removed
- Adapter escape hatches cleaned up (4 deprecated properties removed)
- `ObservationBuilder` retired (1059 lines deleted, replaced with modular encoders)
- All test suites passing: Console (63/63), Adapters (15/15), Observations (24/24), Policy (16/16), DTO Parity (2/2)
- Guard tests updated to prevent reintroduction of legacy patterns

**Impact on WP1:**
- Ports-and-adapters pattern is now complete (no legacy shortcuts remain)
- DTO-only observation flow established (ObservationBuilder eliminated)
- Console routing fully event-based (queue shim removed)
- Adapter surface cleaned (no escape hatches to legacy internals)

**Next Steps for WP1 Step 8:**
1. Update dispatcher identity flow & DTO guard tests
2. Run full regression sweep: `pytest`, `ruff check src tests`, `mypy src`
3. Refresh ADR-001, console/monitor ADR, WP1 README/status
4. Publish release notes summarising port + DTO changes

See `docs/architecture_review/WP_NOTES/WP3.1/` for comprehensive recovery documentation.
