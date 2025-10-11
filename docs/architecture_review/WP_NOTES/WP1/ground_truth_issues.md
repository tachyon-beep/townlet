# WP1 Ground Truth Issues (2025-10-10)

Direct code inspection shows WP1 Step 7 and related deliverables remain incomplete. Each item below lists the issue and decomposes remediation tasks required to finish the work.

## 1. Legacy world factory path still active
- **Status (2025-10-10):** Resolved. `_build_default_world` now requires a `WorldContext` and rejects the legacy `runtime=` shortcut; factory tests enforce the contract.

## 2. DefaultWorldAdapter is a legacy bridge
- **Status (2025-10-10):** Resolved. `DefaultWorldAdapter` is now context-only, and the `.world_state` escape hatch plus legacy runtime delegation have been removed (tests cover the context path).

## 3. WorldContext is unimplemented
- **Status (2025-10-10):** `WorldContext` now drives modular ticks, DTO observations, and snapshot exports; unit coverage exists. Remaining follow-ups focus on tightening deterministic RNG instrumentation and finishing parity tests called out under T3.x/T4.3.
- **Remediation tasks:**
  1. Close out T3.x parity checks to ensure DTO snapshots match legacy baselines under stress scenarios (queues, rivalries, perturbations).
  2. Audit remaining direct `WorldState` mutations in the loop/policy stack and replace them with context helpers.

## 4. SimulationLoop remains tied to legacy runtime
- **Issue:** Factory/adapter wiring now supply modular components, and `runtime.queue_console` is gone, but the loop still holds legacy collectors (queue/economy snapshots, reward helpers) and documents failure handling via inline code.
- **Remediation tasks:**
  1. T4.3 closed (2025-10-10): simulation loop now relies on `WorldContext.export_*` for queue/employment/job data; `loop.tick` emits a DTO `global_context`, but the telemetry aggregator/UI/CLI surfaces still need to migrate before we can drop legacy world references (remaining T4.4b work).
  2. T4.4b status (2025-10-10): publisher + aggregator ingest DTO `global_context`, console/CLI/observer pipelines are migrated, and regression suites cover the DTO path. Remaining items focus on documentation and the follow-on health/failure payload cleanup.
     - `TelemetryPublisher._ingest_loop_tick` populates queue/employment/job/economy/utilities directly from `global_context`, logging once when mandatory fields are missing; `_capture_affordance_runtime` accepts DTO running/reservation payloads. Once downstream consumers stabilise, retire the adapter fallbacks.
     - `TelemetryAggregator.collect_tick` defers to `StreamPayloadBuilder` with `global_context` data; internal callers no longer supply duplicated kwargs.
     - Console router snapshot, `TelemetryClient.from_console`, observer dashboard panels, CLI helpers, and conflict telemetry tests all rely on DTO fixtures (`tests/helpers/telemetry.build_global_context`). Regression bundle (`pytest tests/telemetry/test_aggregation.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py`) exercises the migrated surfaces.
     - Documentation/ADR refresh still pending to describe the DTO-first telemetry flow once the remaining failure/snapshot work lands.
  3. T4.4c status (2025-10-11): loop health events now emit the structured DTO payload (transport snapshot + embedded `global_context`) with alias fields retained for compatibility.
     - `SimulationLoop._build_health_payload` derives metrics from `_build_transport_status` and DTO exports (scheduler counts only used as a fallback); alias values mirror the previous scalar fields.
     - `TelemetryPublisher` caches deep copies of the structured payload, `TelemetryEventDispatcher` prefers the embedded context for queue history, and UI/CLI helpers read the structured block before falling back to aliases. Regression suite covering health/telemetry surfaces passes.
     - Follow-up: document alias deprecation timeline and remove legacy keys after dashboards/CLI migrate (tracked under T4.4d/T4.4 cleanup).
  3. Update failure telemetry/doc pathways (ADR-001, console/monitor ADR) once the loop emits failures purely via ports. *(Structured payload shipped under T4.4d; doc refresh/alias deprecation remains outstanding.)*
  4. Keep loop/component overrides in place for testing, but ensure the default path never rebuilds legacy services.

## 5. Missing dummy providers and promised tests
- **Issue:** There is no `townlet/testing` package or dummy provider suite; none of the WP1 Step 6/8 tests exist (`tests/test_ports_surface.py`, `tests/test_loop_with_dummies.py`, etc.).
- **Remediation tasks:**
  1. Add lightweight dummy implementations for world/policy/telemetry under `src/townlet/testing/` and register them in the factories.
  2. Create the promised test suites (port surface contract, loop with dummies, console router, health monitor smokes).
  3. Integrate these tests into CI to guard the new architecture seams.

## 6. Port boundaries still leak legacy types
- **Issue:** `WorldRuntime` port references `WorldState` and exposes `queue_console`; the loop continues to rely on the broader `core.interfaces.WorldRuntimeProtocol` (`src/townlet/ports/world.py:15-41`, `src/townlet/core/interfaces.py:23-114`).
- **Remediation tasks:**
  1. Narrow the port signatures to DTO-based contracts (remove `WorldState`/console coupling) and document the reduced API.
  2. Update adapters and loop orchestration to conform to the minimal port surface, removing dependence on `core.interfaces` legacy protocols.
  3. Add type-level and runtime guard tests ensuring only the port contracts are imported from the loop.
  4. **T6.1 Inventory (2025-10-11):** `WorldRuntime` and `WorldRuntimeProtocol` currently expose:
     - `reset(seed)` (with optional RNG seed)
     - `tick(tick, console_operations, action_provider(world_state, tick), policy_actions)` returning `RuntimeStepResult`
     - `agents()`, `observe(agent_ids)`, `apply_actions(actions)`
     - `snapshot(config, telemetry, stability, promotion, rng_streams, identity)`
     - `queue_console(operations)`
     - Adapter-only helpers (`bind_world`, `bind_world_adapter`) on `WorldRuntimeProtocol`
     Major consumers:
     - `SimulationLoop`: calls `queue_console`, supplies `action_provider(self.world, tick)`, expects `RuntimeStepResult` actions/events/terminated maps, and invokes `runtime.snapshot(...)`. The loop also binds the runtime via `bind_world` when world replacements occur.
     - `ConsoleRouter`: directly calls `queue_console` and expects `snapshot()` to return a serialisable object for results.
     - `TelemetryPublisher`: `WorldRuntime.snapshot` used during snapshots; `RuntimeStepResult` events fed into telemetry ingestion.
     - Factories/adapters: `DefaultWorldAdapter` inherits `WorldRuntime`, exposing the full port; dummy runtime and test harness rely on the same signature.
     - Tests (`test_core_protocols`, `test_factory_registry`, dummy smokes) enforce the current method set.
     Coupling hotspots:
     - `action_provider` still typed against `WorldState`, preventing DTO-only separation.
     - Console pathway depends on world exposing `queue_console` rather than routing purely via `ConsoleRouter`.
     - Port defined twice (ports + core interfaces); loop imports the broader `WorldRuntimeProtocol` from `core.interfaces`.
