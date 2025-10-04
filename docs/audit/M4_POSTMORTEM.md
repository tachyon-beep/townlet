# Milestone M4 – Post-mortem Notes

## Lessons Learned
- Eliminating the legacy runtime was simpler once observation accessors were in place; investing in the accessor boundary up front reduced downstream cleanup.
- Observation fixture regeneration is fast, so keeping the commands documented (`scripts/run_simulation.py` + ObservationBuilder script) helps future contributors verify parity quickly.
- `mypy` debt remains the primary blocker for full type coverage; future phases should focus on `src/townlet/observations/builder.py` and employment modules.

## Metrics / Validation Snapshot
- Telemetry smoke run (`scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 500`) shows `runtime_variant="facade"`, no schema differences vs Phase 3 baselines (`tmp/obs_phase3/` directory).
- Observation NPZ fixtures refreshed on 2025-??-??; hashes recorded in `tests/data/observations/` comments.
- Critical pytest suites (observation, employment, telemetry) executed successfully as part of rollout sign-off.

## Cleanup Follow-ups
- No rollout feature flags remain; rollback relies on git tags noted in `docs/audit/M4_ROLLOUT_PLAN.md`.
- Tick-health logging remains useful for future monitoring; no temporary logging to remove.
- Design notes updated (`docs/engineering/WORLDSTATE_REFACTOR.md`); audit and plan documents now reflect completed phases.
