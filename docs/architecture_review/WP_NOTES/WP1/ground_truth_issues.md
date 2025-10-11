# WP1 Ground Truth Issues (2025-10-10)

Direct code inspection shows WP1 Step 7 and related deliverables remain incomplete. Each item below lists the issue and decomposes remediation tasks required to finish the work.

## 1. Legacy world factory path still active
- **Status (2025-10-10):** Resolved. `_build_default_world` now requires a `WorldContext` and rejects the legacy `runtime=` shortcut; factory tests enforce the contract.

## 2. DefaultWorldAdapter is a legacy bridge
- **Status (2025-10-10):** Resolved. `DefaultWorldAdapter` is now context-only, and the `.world_state` escape hatch plus legacy runtime delegation have been removed (tests cover the context path).

## 3. WorldContext is unimplemented
- **Status (2025-10-10):** `WorldContext` now drives modular ticks, DTO observations, and snapshot exports; unit coverage exists. Remaining follow-ups focus on tightening deterministic RNG instrumentation and finishing parity tests called out under T3.x/T4.3.
- **Remediation tasks:**
  1. T3.x parity checks covered (`tests/world/test_world_context_parity.py`) ensuring queue metrics, relationship snapshots, and economy exports match the underlying services.
  2. Audit remaining direct `WorldState` mutations in the loop/policy stack and replace them with context helpers.

## 4. SimulationLoop remains tied to legacy runtime
- **Issue:** Factory/adapter wiring now supply modular components, and `runtime.queue_console` is gone, but the loop still holds legacy collectors (queue/economy snapshots, reward helpers) and documents failure handling via inline code.
- **Remediation tasks:**
  1. T4.3 closed (2025-10-10): simulation loop now relies on `WorldContext.export_*` for queue/employment/job data; `loop.tick` emits a DTO `global_context` snapshot consumed end-to-end.
  2. T4.4b closed (2025-10-11): publisher/aggregator/UI/CLI consumers rely exclusively on DTO `global_context`, documentation reflects the flow (ADR-001, WP1 status/pre-brief), and regression bundle (`pytest tests/telemetry/test_aggregation.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py -q`) is recorded.
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
- **Issue:** The port still carries `WorldState`-typed `action_provider` callbacks, but the console bridge has been removed (PB-C) and the legacy `WorldRuntimeProtocol` alias is gone.
- **Remediation tasks:**
  1. Continue narrowing the port to DTO-only data (replace the `WorldState`-typed `action_provider` once WP3 Stage 6 delivers DTO adapters).
  2. Deprecate/remove the remaining adapter-only helpers (`bind_world`, `bind_world_adapter`) after the final composition-root refactor.
  3. Maintain the static guard (`tests/core/test_world_port_imports.py`) so no new imports of the old alias reappear.
  4. Track console/docs clean-up for alias removal and DTO-only identity events (see T4.4 follow-ups).
