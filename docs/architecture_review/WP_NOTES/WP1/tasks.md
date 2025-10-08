# WP1 Working Tasks

## 1. Map Simulation Loop Surface
- [x] Scan `src/townlet/core/sim_loop.py` for:
  - [x] Methods invoked on world runtime (e.g., `bind_world`, `apply_actions`, `tick`, `snapshot`).
  - [x] Methods invoked on policy backend (decision, lifecycle, diagnostics).
  - [x] Methods invoked on telemetry sink (publish, console, metrics accessors).
  - [x] Note optional hooks / attributes guarded by `hasattr` or feature flags.
  - [x] Record findings in `README.md` (ports vs adapter candidate list).

## 2. Inspect Current Implementations
- [x] World
  - [x] Inventory key entry points under `src/townlet/world/**` (runtime adapter, grid, observations glue).
  - [x] Identify methods needed to satisfy port (and what extra responsibilities must move to adapters).
- [x] Policy
  - [x] Review `policy/runner.py` for current runtime interface.
  - [x] Review `policy/training_orchestrator.py` for console/telemetry hooks that may need adapters.
- [x] Telemetry
  - [x] Review `telemetry/publisher.py`, aggregation, transport to catalogue methods and side effects.
  - [x] Note any console/auth/workers pieces that should live behind adapters.

## 3. Understand Composition Mechanisms
- [x] Read `src/townlet/core/factory_registry.py` to understand current provider resolution.
- [x] Check where registries are populated (policy/telemetry/world modules).
- [x] Inspect configs (`configs/examples/*.yml`) for provider keys and options.
- [x] Document migration considerations for new `townlet/factories/*.py` modules.

## 4. Audit Existing Stubs & Tests
- [x] Catalogue dummy/stub providers:
  - [x] `townlet/policy/fallback.py`
  - [x] `townlet/telemetry/fallback.py`
  - [x] Confirm absence of world dummy implementation.
- [x] List existing tests exercising stubs (e.g., `tests/test_policy_backend_selection.py`).
- [x] Identify gaps new dummies/tests must fill per WP1 deliverables.

## 5. Tooling & Gate Check
- [x] Confirm `pyproject.toml` includes `pydantic` or decide on alternative.
- [x] Check existing `mypy.ini`/`pyproject` settings for strictness expectations.
- [x] Verify lint and type targets for new modules (`src/townlet/ports`, `factories`, `testing`).
- [x] Note any pre-commit hooks or CI jobs relevant to WP1.

## 6. Documentation Alignment
- [ ] Keep `docs/architecture_review/WP_TASKINGS/WP1.md` open; ensure tasks map 1:1.
- [ ] Cross-reference ADR-001 for method names and registry keys.
- [ ] Note dependencies with WP2/WP3 docs to avoid divergence.
- [ ] Update `README.md` findings section as decisions solidify.

Maintain this checklist during WP1 implementation.
