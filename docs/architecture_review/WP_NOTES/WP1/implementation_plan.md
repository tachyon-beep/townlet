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

## 2. Build Adapters
2.1. Create `src/townlet/adapters/` package and modules:
    - `world_default.py`: wrap existing `WorldRuntime` or façade, satisfying `WorldRuntime` protocol; handle console queueing internally.
    - `policy_scripted.py`: wrap `PolicyRuntime` (scripted backend) to expose only port methods; translate legacy hooks as needed.
    - `telemetry_stdout.py`: wrap `TelemetryPublisher`, map port methods to publisher operations; manage start/stop.
2.2. Ensure adapters perform any necessary translation (e.g., convert DTOs to legacy dicts where required for now).
2.3. Provide registration decorators or helper functions linking adapters to factory registry (see Step 3).

## 3. Implement Registry Modules
3.1. Add `src/townlet/factories/` package with:
    - `registry.py`: shared decorator/utilities, underlying storage, `ConfigurationError`.
    - `world_factory.py`, `policy_factory.py`, `telemetry_factory.py`: domain-specific creation functions.
3.2. Register built-in providers (`default`, `scripted`, `stdout`) plus stubs/dummies (`dummy`, `stub`) per ADR.
3.3. Guard optional dependencies (Torch, httpx) with fallback logic similar to current registry.
3.4. Update module-level exports for convenience (e.g., `create_world` functions).

## 4. Refactor Composition Root
4.1. Update `src/townlet/core/sim_loop.py` to import new ports + factories (instead of `resolve_*`).
4.2. Replace `factory_registry` usage with calls to `create_world/policy/telemetry`.
4.3. Ensure loop only depends on port protocols (no direct adapter imports).
4.4. Maintain existing functionality (anneal settings, telemetry identity updates) via adapter-provided helpers or by fetching from adapters as needed.
4.5. Update helper functions (`policy_provider_name`, `is_stub_policy`, etc.) to use new factory registry infrastructure if they currently rely on `factory_registry`.
4.6. Ensure stability/promotion metrics remain available—adapt loop or adapters to supply required data without expanding port methods (e.g., adapters may retain `latest_*` access internally while loop consumes combined DTO payloads).

## 5. Introduce Dummy/Test Utilities
5.1. Create `src/townlet/testing/dummies.py` with `DummyWorld`, `DummyPolicy`, `DummyTelemetry` implementing the new ports.
5.2. Register dummy providers in the factories under keys (`"dummy"`, `"stub"`).
5.3. Ensure dummy telemetry satisfies port lifecycle but is lightweight (no threads).

## 6. Testing
6.1. Add tests:
    - `tests/test_ports_surface.py` (forbidden symbols, method presence).
    - `tests/test_factories.py` (provider resolution, error paths, fallback behaviour).
    - `tests/test_loop_with_dummies.py` (smoke test using dummy providers).
    - `tests/test_loop_with_adapters_smoke.py` (default providers; mark slow if needed).
6.2. Update existing tests affected by registry changes (e.g., fallback tests) to use new factory APIs.
6.3. Run `pytest` focused on new tests, then full suite.

## 7. Documentation & ADR Updates
7.1. Update ADR-001 if implementation details differ slightly (e.g., provider keys, behaviour notes).
7.2. Amend WP1 tasking if minor clarifications arise during implementation.
7.3. Document new registry usage in developer docs (if applicable) or add README snippet.

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
- Telemetry/stability features currently depend on `latest_*` accessors. Adapters must continue to satisfy loop/stability needs—either by exposing a compatibility layer within adapters or by refactoring consumers to rely on emitted events. Plan Step 4 should include explicit sub-task to route stability/promotions inputs without reintroducing forbidden port APIs.
