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
  1. T4.3 closed (2025-10-10): simulation loop now relies on `WorldContext.export_*` for queue/employment/job data; remaining work under this issue is T4.4 (telemetry/failure docs).
  2. Update failure telemetry/doc pathways (ADR-001, console/monitor ADR) once the loop emits failures purely via ports.
  3. Keep loop/component overrides in place for testing, but ensure the default path never rebuilds legacy services.

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
