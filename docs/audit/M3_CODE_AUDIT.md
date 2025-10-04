# Milestone M3 Code Audit (Phase 3 Cleanup)

## Outstanding Defects

1. **Legacy runtime toggle undecided (Medium).** `SimulationLoop`, CLI entry points, and tests still honour `TOWNLET_LEGACY_RUNTIME` (`src/townlet/core/sim_loop.py:110-140`, `scripts/run_simulation.py:33-53`, `scripts/observer_ui.py:63-81`, `tests/test_simulation_loop_runtime.py:45-52`). Phase 3 promised either retiring the flag or documenting long-term support, but neither has happened.
2. **Observation helpers breach encapsulation (Medium).** `townlet.world.observation` operates directly on `WorldState` internals such as `_objects_by_position` and `_active_reservations` (`src/townlet/world/observation.py:27-133`), contradicting the facade goal and complicating further refactors.
3. **Tests depend on private employment hooks (Low).** Multiple fixtures call `_assign_jobs_to_agents` with `type: ignore[attr-defined]` (`tests/test_console_dispatcher.py:43`, `tests/test_console_commands.py:579`, `tests/test_employment_loop.py:32`, plus other telemetry tests), so Phase 3 cleanup cannot drop the shim without breaking coverage.

## Remediation Plan

### 1. Legacy Runtime Decision (1–2 days)
- Inventory all references to `TOWNLET_LEGACY_RUNTIME` across code, docs, and tests.
- Align with stakeholders on whether to keep or retire the flag.
- **If keeping:** document behaviour in `docs/engineering/WORLDSTATE_REFACTOR.md`, add regression tests covering both modes (extend `tests/test_simulation_loop_runtime.py`), and capture rollout guidance in `GRID_REFACTOR_PLAN.md`.
- **If removing:** strip env plumbing from `SimulationLoop`, CLI scripts, and tests; collapse telemetry to a single runtime variant; refresh documentation and changelog.
- Validate by running targeted pytest suites and long-form simulation smoke in the surviving mode(s); archive results for milestone closure.

### 2. Observation Boundary Hardening (2–3 days)
- Design accessor methods or lightweight snapshots on `WorldState` to expose the data observation helpers need (objects-by-position, active reservations, agent snapshots).
- Update `townlet.world.observation` to use the new accessors instead of private attributes; adjust observation builder and reward engine imports as needed.
- Refresh observation-related tests (`tests/test_world_observation_helpers.py`, `tests/test_observation_builder.py`) and regenerate fixtures via the documented simulation commands.
- Record the new contract and usage expectations in `docs/engineering/WORLDSTATE_REFACTOR.md`, highlighting that helper modules no longer touch private internals.

### 3. Public Employment Test Hooks (1–2 days)
- Provide sanctioned helpers or fixtures for employment setup (e.g., expose `world.employment.assign_jobs_to_agents(world)` or add factory fixtures per test module).
- Migrate all tests currently using `_assign_jobs_to_agents` to the public surface and remove the `type: ignore` annotations.
- Decide whether to keep `_assign_jobs_to_agents` as a public method or replace it entirely; ensure no test depends on private attributes afterward.
- Run the affected pytest modules plus `ruff`/`mypy` to confirm the suite stays green.

### Closure Criteria
- All remediation tasks complete with clean pytest, `ruff`, and `mypy` runs.
- Telemetry/observation baselines regenerated and archived where Phase 0 expects them.
- Documentation (`GRID_REFACTOR_PLAN.md`, `docs/engineering/WORLDSTATE_REFACTOR.md`, and related guides) updated to reflect the resolved state.
- Milestone M3 Phase 3 marked as completed with sign-off notes referencing the validation evidence above.
