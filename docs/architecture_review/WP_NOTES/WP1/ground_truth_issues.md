# WP1 Ground Truth Issues (2025-10-10)

Direct code inspection shows WP1 Step 7 and related deliverables remain incomplete. Each item below lists the issue and decomposes remediation tasks required to finish the work.

## 1. Legacy world factory path still active
- **Status (2025-10-10):** Resolved. `_build_default_world` now requires a `WorldContext` and rejects the legacy `runtime=` shortcut; factory tests enforce the contract.

## 2. DefaultWorldAdapter is a legacy bridge
- **Status (2025-10-10):** Resolved. `DefaultWorldAdapter` is now context-only, and the `.world_state` escape hatch plus legacy runtime delegation have been removed (tests cover the context path).

## 3. WorldContext is unimplemented
- **Issue:** `WorldContext` methods still raise `NotImplementedError` (`src/townlet/world/context.py:11-38`), leaving no modular runtime for the factory to return.
- **Remediation tasks:**
  1. Port the WP2 tick orchestration into `WorldContext`, exposing `reset/tick/agents/observe/apply_actions/snapshot` with DTO outputs.
  2. Wire modular systems/services inside the context and ensure deterministic RNG handling.
  3. Provide unit/system tests that exercise the new context and compare against legacy behaviour for parity.

## 4. SimulationLoop remains tied to legacy runtime
- **Issue:** Loop builds `WorldState`, `LifecycleManager`, `PerturbationScheduler`, and an `ObservationBuilder` itself, then calls `runtime.queue_console` (`src/townlet/core/sim_loop.py:215-319`, `src/townlet/core/sim_loop.py:450`). Step 8 factory/composition refactor never happened.
- **Remediation tasks:**
  1. Refactor `_build_components` to resolve world/policy/telemetry exclusively via the port factories and operate through their minimal surfaces.
  2. Route console commands strictly via `ConsoleRouter`/event emission and remove direct `queue_console` usage.
  3. Ensure policy decisions consume cached DTO envelopes and backfill loop smoke tests covering the modular pipeline.

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
