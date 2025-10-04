# Milestone M3 Code Audit (Phase 3 Cleanup)

## Outstanding Defects

1. **Observation helpers breach encapsulation (Medium).** `townlet.world.observation` operates directly on `WorldState` internals such as `_objects_by_position` and `_active_reservations` (`src/townlet/world/observation.py:27-133`), contradicting the facade goal and complicating further refactors.
2. **Tests depend on private employment hooks (Low).** Multiple fixtures call `_assign_jobs_to_agents` with `type: ignore[attr-defined]` (`tests/test_console_dispatcher.py:43`, `tests/test_console_commands.py:579`, `tests/test_employment_loop.py:32`, plus other telemetry tests), so Phase 3 cleanup cannot drop the shim without breaking coverage.

## Remediation Plan

### 1. Legacy Runtime Decision (completed)
- Legacy runtime toggle removed; facade runtime is now the only supported path. Future work only needs to ensure facade regressions are covered by the standard suite.
- Added read-only `WorldState` accessors (`active_reservations_view`, `agent_snapshots_view`, `objects_by_position_view`) with coverage in `tests/test_world_state_accessors.py` to support the observation boundary cleanup.

### 2. Observation Boundary Hardening (completed)
- `WorldState` now exposes read-only views consumed by `townlet.world.observation`, observation builder, and reward engine tests.
- Tests updated to use queue manager/state refresh helpers instead of poking private attributes, and the engineering doc records the accessor contract.

### 3. Public Employment Test Hooks (1–2 days)
- Provide sanctioned helpers or fixtures for employment setup (e.g., expose `world.employment.assign_jobs_to_agents(world)` or add factory fixtures per test module).
- Migrate all tests currently using `_assign_jobs_to_agents` to the public surface and remove the `type: ignore` annotations.
- Decide whether to keep `_assign_jobs_to_agents` as a public method or replace it entirely; ensure no test depends on private attributes afterward.
- Run the affected pytest modules plus `ruff`/`mypy` to confirm the suite stays green.

### 4. Fixture & Documentation Refresh (completed)
- Observation NPZ baselines regenerated (`tests/data/observations/baseline_*.npz`) using the accessor-backed helpers.
- Telemetry snapshot captured for reference in `tmp/obs_phase3/telemetry.jsonl`; no schema changes detected.
- `docs/engineering/WORLDSTATE_REFACTOR.md` updated to reflect the new boundary and fixture refresh.

### Closure Criteria
- All remediation tasks complete with clean pytest, `ruff`, and `mypy` runs.
- Telemetry/observation baselines regenerated and archived where Phase 0 expects them.
- Documentation (`GRID_REFACTOR_PLAN.md`, `docs/engineering/WORLDSTATE_REFACTOR.md`, and related guides) updated to reflect the resolved state.
- Milestone M3 Phase 3 marked as completed with sign-off notes referencing the validation evidence above.
