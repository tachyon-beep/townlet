# WP1 Implementation Plan — Ports & Factory Registry

This plan enumerates the concrete steps for implementing Work Package 1. Keep it updated as tasks complete.

## 0. Prerequisites
- Ensure plan prerequisites documented in `tasks.md` are complete (✔ done).
- Keep ADR-001 and WP1 tasking open for reference.

**Status snapshot (2025-10-09).** Steps 1–3, 5, and 6 are complete; unit coverage exists for ports, registry, and the new modular world context (`pytest tests/world -q`, `pytest tests/test_world_context.py -q`). The remaining effort is the composition refactor (Step 7 / Step 8 below).

## 1. Define Port Protocols (✔ done)
1.1. Create `src/townlet/ports/` package (`__init__.py`, `world.py`, `policy.py`, `telemetry.py`).
1.2. Implement protocol classes per ADR-001:
    - `WorldRuntime` with methods: `reset`, `tick`, `agents`, `observe`, `apply_actions`, `snapshot`.
    - `PolicyBackend` with `on_episode_start`, `decide`, `on_episode_end`.
    - `TelemetrySink` with `start`, `stop`, `emit_event`, `emit_metric`.
1.3. Add docstrings + type hints; ensure no forbidden symbols (WP1 tests will enforce this).
1.4. Export protocols via `ports/__init__.py` for easy import.

## 2. Build Adapters & Orchestration Services (✔ done / orchestration pending Step 8)
2.1. Create `src/townlet/adapters/` package and modules:
    - `world_default.py`: compose legacy world implementation with an internal `ObservationBuilder`; ensure `snapshot()` returns tick metadata and domain events consumed by monitors.
    - `policy_scripted.py`: wrap `PolicyRuntime` to expose only port methods; emit any additional telemetry (hashes, anneal ratios) via events rather than getters.
    - `telemetry_stdout.py`: wrap `TelemetryPublisher` purely as a sink (`start`, `stop`, `emit_event`, `emit_metric`), removing getter-based access.
2.2. Add orchestration services:
    - `orchestration/console.py` providing `ConsoleRouter` (handles command queues, invokes world actions/queries, emits `console.result` events).
    - `orchestration/health.py` providing `HealthMonitor` (consumes snapshots/events, maintains rolling metrics, emits metrics via telemetry).
2.3. Ensure adapters/services perform necessary translation (e.g., DTO ↔ legacy dict) without expanding port surfaces.
2.4. Provide registration decorators or helper functions linking adapters to factory registry (see Step 3).

## 3. Implement Registry Modules (✔ done)
3.1. Add `src/townlet/factories/` package with:
    - `registry.py`: shared decorator/utilities, underlying storage, `ConfigurationError`.
    - `world_factory.py`, `policy_factory.py`, `telemetry_factory.py`: domain-specific creation functions.
3.2. Register built-in providers (`default`, `scripted`, `stdout`) plus stubs/dummies (`dummy`, `stub`) per ADR.
3.3. Guard optional dependencies (Torch, httpx) with fallback logic similar to current registry.
3.4. Update module-level exports for convenience (e.g., `create_world` functions).

## 4. Refactor Composition Root & Tick Pipeline (superseded by Step 7/8 plan)
- Replaced by the detailed Step 7/8 tasks below; the original outline remains for traceability.

## 5. Introduce Dummy/Test Utilities (✔ done)
5.1. Create `src/townlet/testing/dummies.py` with `DummyWorld`, `DummyPolicy`, `DummyTelemetry` implementing the new ports.
5.2. Register dummy providers in the factories under keys (`"dummy"`, `"stub"`).
5.3. Ensure dummy telemetry satisfies port lifecycle but is lightweight (no threads).

## 6. Testing (initial suites ✔, additional Step 8 suites pending)
6.1. Add tests:
    - `tests/test_ports_surface.py` (forbidden symbols, method presence).
    - `tests/test_factories.py` (provider resolution, error paths, fallback behaviour).
    - `tests/test_console_router.py` (command routing/emit `console.result`).
    - `tests/test_health_monitor.py` (snapshot/events → metrics emitted).
    - `tests/test_world_observe_integration.py` (observation profile selection).
    - `tests/test_loop_with_dummies.py` (smoke test using dummy providers).
    - `tests/test_loop_without_telemetry_getters.py` (ensure loop does not call `latest_*`).
    - `tests/test_loop_with_adapters_smoke.py` (default providers; mark slow if needed).
6.2. Update existing tests affected by registry changes (e.g., fallback tests) to use new factory APIs and orchestration services.
6.3. Run targeted `pytest` on new suites, then full suite.

## 7. Documentation & ADR Updates (in progress alongside Step 8)
7.1. Update ADR-001 if implementation details differ slightly (e.g., provider keys, behaviour notes).
7.2. Document console/health monitor design in a new ADR (`ADR-00X - Console and Monitoring`) referencing the architect guidance.
7.3. Amend WP1 tasking if minor clarifications arise during implementation.
7.4. Document new registry usage and orchestration services in developer docs or README snippet.

## 8. Cleanup & Verification (finalisation pass once Step 8 lands)
8.1. Run `ruff check src tests` and fix lint.
8.2. Run `mypy src/townlet/ports src/townlet/factories src/townlet/adapters src/townlet/testing` (and broader if needed).
8.3. Ensure git status clean apart from intentional changes.
8.4. Update `WP_NOTES/WP1/README.md` with final findings/decisions.
8.5. Prepare summary for PR (change highlights, tests run).

Use this plan to track implementation progress. Update checkboxes or add subsections as tasks complete.

## Additional Considerations (cross-check)
- `townlet/core/__init__.py` re-exports factory helpers; must be updated to point at new factory modules and optionally deprecate legacy `resolve_*` helpers.
- `townlet/core/utils.py` relies on `provider_info` fields from `SimulationLoop`; ensure these remain populated (or provide alternative) after refactor.
- Telemetry/stability features should operate via snapshots/events and orchestration services; confirm no telemetry getter usage remains after introducing `ConsoleRouter` and `HealthMonitor`.

## 7. Factory Integration & Composition Root (next focus)
1. **Factory wiring**
   - Update `townlet.factories.world_factory.create_world` so the default provider instantiates `WorldContext`, passing through configuration, queue/relationship/economy services, and the new RNG/event plumbing.
   - Align dummy/stub world providers with the new context (ensure `tests/test_loop_with_dummies.py` can be added without bespoke shims).
   - Refresh `WorldRuntimeAdapter` so downstream consumers (`world_adapter`, telemetry, policy) interact with the modular facade.
2. **Simulation loop refactor**
   - Replace `resolve_*` helper usage with `create_world/policy/telemetry`; remove the legacy registry helpers after the swap.
   - Instantiate `ConsoleRouter` and `HealthMonitor` from the orchestration layer; route console inputs through the router and emit health metrics via `TelemetrySink.emit_metric`.
   - Remove all telemetry `latest_*` pulls from the loop; rely on events + health monitor output.
   - Keep provider metadata (`policy_provider_name`, stub checks) coherent after the factory changes.
3. **Testing**
   - Add loop smokes: dummy providers, default providers (mark slow if necessary), console router, health monitor, telemetry getter guard.
   - Unit test the new orchestration helpers (`tests/test_console_router.py`, `tests/test_health_monitor.py`).
   - Extend existing factory/port tests if signatures change.
4. **Documentation**
   - Update ADR-001 with the new default provider flow; draft the console/monitor ADR once implementations land.
   - Record migration guidance for downstream consumers (console, telemetry, policy training) in `README.md` / status notes.

### Step 8 — Incremental Simulation Loop Refactor Plan

**Phase 0 – Baseline**
- Capture current behaviour/tests: `pytest tests/test_sim_loop.py` (if present), loop smokes (run a few ticks via `scripts/run_simulation.py` with stdout telemetry). Document key metrics/console behaviour to compare after each phase.

**Phase 1 – Factory swap (complete 2025-10-09)**
1. `SimulationLoop._build_components()` now resolves dependencies exclusively via `create_world/create_policy/create_telemetry`, keeping the legacy instances behind adapters for parity.
2. Legacy `resolve_*` helpers remain for callers outside the loop but are no longer used during loop construction; plan removal once downstream scripts adopt the factories.
3. `provider_info` reflects the registry providers and existing loop tests (`tests/test_simulation_loop_runtime.py`) continue to pass.
4. Follow-up: capture a lightweight smoke test exercising the new factory path once telemetry/policy migrations settle.

**Phase 2 – Integrate ConsoleRouter & HealthMonitor without removing legacy behaviour**
1. `ConsoleRouter` and `HealthMonitor` are now instantiated by the loop and fed every tick. Console commands drain from telemetry into the router (still mirrored into `runtime.queue_console` for parity) and health metrics are emitted via the telemetry port.
2. Outstanding work:
   - Eliminate reliance on `runtime.queue_console` by executing commands solely through the router and world port.
   - Remove direct calls to `record_console_results` / `record_health_metrics` once downstream consumers depend on router events + monitor metrics.
3. Tests:
   - `tests/test_console_router.py` added to cover basic enqueue/dispatch paths.
   - TODO: add targeted health monitor unit tests and loop smoke once telemetry getters are retired.

**Phase 3 – Shift telemetry consumption to events/metrics**
1. Telemetry getters have been removed from `SimulationLoop.step`; queue/employment/job metrics and rivalry events come directly from the world adapter, and the loop emits a `loop.tick` event via the telemetry port (stdout adapter translates this back into `publish_tick` for legacy consumers).
2. Follow-ups:
   - Replace `record_console_results` / `record_health_metrics` / `record_loop_failure` with event-driven emissions once the telemetry sink exposes streaming equivalents (targeted for the telemetry rework in WP3).
   - Add a guard test `tests/test_telemetry_getters_removed.py` to ensure getter usage does not regress.
3. Stability monitor now operates on locally computed metrics; keep parity checks in place until the new sink lands.

**Phase 4 – Clean-up & docs**
1. Remove deprecated code in `core/factory_registry.py` (legacy `resolve_*` helpers) once all call sites use the factories.
2. Update helper utilities (`policy_provider_name`, `is_stub_policy`, etc.) to read from the new metadata.
3. Documentation:
   - Extend ADR-001 with provider factory usage examples.
   - Finalise the console/health ADR summarising the new orchestration pipeline.
   - Update WP1 notes with migration instructions for downstream teams (policy trainer, telemetry, console UI).
4. Final test sweep: full `pytest`, targeted smokes (`scripts/run_simulation.py` for a few ticks), and lint/type checks (`ruff`, `mypy`).
