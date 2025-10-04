# M3 Legacy Runtime Decision Plan

**Status:** Option B executed — legacy runtime path removed and facade is now the sole implementation (2025-??-??).

## Current Usage Inventory

- **Runtime selection in core loop**: Prior to removal, `SimulationLoop._legacy_runtime_enabled()` consulted `use_legacy_runtime` or `TOWNLET_LEGACY_RUNTIME` to toggle implementations. The helper and supporting code were deleted in the 2025-??-?? cleanup.
- **CLI entry points**: `scripts/run_simulation.py` and `scripts/observer_ui.py` previously exposed `--runtime {auto,facade,legacy}`; the toggle has been dropped and the CLI now always runs the facade.
- **Tests**: `tests/test_simulation_loop_runtime.py` now verifies that the facade is always selected and that the legacy env var is ignored.
- **Documentation/plan**: References in `docs/engineering/WORLDSTATE_REFACTOR.md` and `GRID_REFACTOR_PLAN.md` were updated to record the retirement of the flag.

## Decision Drivers

1. **Operational need** – Confirm whether any downstream jobs (training, observer dashboards, regression sims) still require the legacy tick path for stability.
2. **Support cost** – Maintaining dual code paths doubles validation overhead (every regression must run in both modes) and complicates future refactors.
3. **Rollout guarantees** – Removing the flag without a rollback plan increases risk during production rollouts; conversely, keeping it without documentation risks accidental regressions when engineers assume the facade is always active.

## Option A – Retain the Flag (Long-term Support)

Tasks:
- Document the official support policy in `docs/engineering/WORLDSTATE_REFACTOR.md` (when to use each mode, known differences, validation checklist).
- Expand automated coverage to run representative smoke tests in both modes (extend `tests/test_simulation_loop_runtime.py`, add integration marker for dual-mode execution).
- Update `GRID_REFACTOR_PLAN.md` and release notes to reflect the decision; include instructions for enabling legacy mode in ops runbooks.
- Establish a regression matrix (e.g., nightly CI job) that executes key suites with `TOWNLET_LEGACY_RUNTIME=1` to prevent bit-rot.

Risks: ongoing maintenance burden, slower validation cycles, higher complexity for future refactors touching `SimulationLoop` or `WorldState`.

## Option B – Retire the Flag (Facade as sole runtime)

Tasks (completed):
- [x] Remove the environment flag plumbing from `SimulationLoop`, CLI scripts, and supporting utilities.
- [x] Simplify CLI switches to accept only the facade and drop `--runtime`.
- [x] Rewrite tests so the legacy path is no longer exercised; ensure the env flag is ignored.
- [x] Update documentation to announce removal and point to the facade as the only supported runtime.
- [x] Run validation (pytest + CLI smokes) prior to merge.

Risks: mitigated by validation; any future rollback would rely on git tags/branches rather than a runtime flag.

## Recommended Evaluation Steps (Common to Both Options)

Completed alongside the Option B execution: stakeholder confirmation, parity runs, decision capture in `GRID_REFACTOR_PLAN.md`, validation reruns, and audit updates.

## Immediate Next Actions

None.
