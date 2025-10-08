# WP1 Implementation Plan — Ports & Factory Registry

This plan enumerates the concrete steps for implementing Work Package 1. Keep it updated as tasks complete.

## 0. Prerequisites
- Ensure plan prerequisites documented in `tasks.md` are complete (✔ done).
- Keep ADR-001 and WP1 tasking open for reference.

## 1. Define Port Protocols
1.1. Create `src/townlet/ports/` package (`__init__.py`, `world.py`, `policy.py`, `telemetry.py`).
1.2. Implement protocol classes per ADR-001:
    - `WorldRuntime` with methods: `reset`, `tick`, `agents`, `observe`, `apply_actions`, `snapshot`.
    - `PolicyBackend` with `on_episode_start`, `decide`, `on_episode_end`.
    - `TelemetrySink` with `start`, `stop`, `emit_event`, `emit_metric`.
1.3. Add docstrings + type hints; ensure no forbidden symbols (WP1 tests will enforce this).
1.4. Export protocols via `ports/__init__.py` for easy import.

## 2. Build Adapters & Orchestration Services
2.1. Create `src/townlet/adapters/` package and modules:
    - `world_default.py`: compose legacy world implementation with an internal `ObservationBuilder`; ensure `snapshot()` returns tick metadata and domain events consumed by monitors.
    - `policy_scripted.py`: wrap `PolicyRuntime` to expose only port methods; emit any additional telemetry (hashes, anneal ratios) via events rather than getters.
    - `telemetry_stdout.py`: wrap `TelemetryPublisher` purely as a sink (`start`, `stop`, `emit_event`, `emit_metric`), removing getter-based access.
2.2. Add orchestration services:
    - `orchestration/console.py` providing `ConsoleRouter` (handles command queues, invokes world actions/queries, emits `console.result` events).
    - `orchestration/health.py` providing `HealthMonitor` (consumes snapshots/events, maintains rolling metrics, emits metrics via telemetry).
2.3. Ensure adapters/services perform necessary translation (e.g., DTO ↔ legacy dict) without expanding port surfaces.
2.4. Provide registration decorators or helper functions linking adapters to factory registry (see Step 3).

## 3. Implement Registry Modules
3.1. Add `src/townlet/factories/` package with:
    - `registry.py`: shared decorator/utilities, underlying storage, `ConfigurationError`.
    - `world_factory.py`, `policy_factory.py`, `telemetry_factory.py`: domain-specific creation functions.
3.2. Register built-in providers (`default`, `scripted`, `stdout`) plus stubs/dummies (`dummy`, `stub`) per ADR.
3.3. Guard optional dependencies (Torch, httpx) with fallback logic similar to current registry.
3.4. Update module-level exports for convenience (e.g., `create_world` functions).

## 4. Refactor Composition Root & Tick Pipeline
4.1. Update `src/townlet/core/sim_loop.py` (and `core/__init__.py`, helper utilities) to import the new factories instead of `core.factory_registry`.
4.2. Replace `resolve_world/policy/telemetry` calls with `create_world/policy/telemetry`, explicitly constructing legacy runtime components (world state, policy runtime, publisher) before passing them to the factories until the adapters can self-construct.
4.3. Ensure the loop interacts with returned ports (reset/tick/observe/apply_actions/snapshot, policy decide/on_episode_end, telemetry emit) rather than calling legacy methods. For areas not yet ported (e.g., observation builder, telemetry getters), wrap via temporary bridges and document follow-up tasks for WP2/WP3.
4.4. Instantiate orchestration services (`ConsoleRouter`, `HealthMonitor`) but gate their usage behind feature flags or incremental integration so we avoid destabilising existing flows. Initial step: prepare hooks without removing legacy console/telemetry behaviour.
4.5. Maintain existing behaviour (anneal settings, policy identity, stability monitors) during the transition; record where telemetry getters remain so they can be removed in later work packages.
4.6. Update helper functions (`policy_provider_name`, `is_stub_policy`, etc.) to reference the new provider plumbing and keep `provider_info` coherent.

## 5. Introduce Dummy/Test Utilities
5.1. Create `src/townlet/testing/dummies.py` with `DummyWorld`, `DummyPolicy`, `DummyTelemetry` implementing the new ports.
5.2. Register dummy providers in the factories under keys (`"dummy"`, `"stub"`).
5.3. Ensure dummy telemetry satisfies port lifecycle but is lightweight (no threads).

## 6. Testing
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

## 7. Documentation & ADR Updates
7.1. Update ADR-001 if implementation details differ slightly (e.g., provider keys, behaviour notes).
7.2. Document console/health monitor design in a new ADR (`ADR-00X - Console and Monitoring`) referencing the architect guidance.
7.3. Amend WP1 tasking if minor clarifications arise during implementation.
7.4. Document new registry usage and orchestration services in developer docs or README snippet.

## 8. Cleanup & Verification
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
