# Employment Loop Docs & Test Checklist

Use this checklist when landing employment-loop changes.

- [ ] Updated design references (`docs/design/EMPLOYMENT_ATTENDANCE_BRIEF.md`, `docs/design/EMPLOYMENT_EXIT_CAP_MATRIX.md`) if behaviour shifts.
- [ ] `docs/engineering/IMPLEMENTATION_NOTES.md` entry added with date + scope summary.
- [ ] `docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md` / `docs/ops/OPS_HANDBOOK.md` synced with new telemetry or console fields.
- [ ] Added/updated pytest coverage (unit + smoke where applicable).
- [ ] Ran `python scripts/run_employment_smoke.py ... --enforce-job-loop` and archived metrics if logic changed.
- [ ] (Optional) Reran `scripts/console_dry_run.py` when console surfaces change.

## Observation Updates (Hybrid Variant)
- [ ] Updated `docs/design/OBSERVATION_TENSOR_SPEC.md` and noted schema impact.
- [ ] Added/updated observation unit tests and sample fixtures.
- [ ] Regenerated `docs/samples/observation_hybrid_sample.npz` if tensor layout changed.
- [ ] Documented changes in `docs/engineering/IMPLEMENTATION_NOTES.md` and architecture guide.
- [ ] Run `python scripts/observer_ui.py <config> --ticks 1 --refresh 0` to confirm dashboard rendering (or run `pytest tests/test_observer_ui_script.py`).

Keep this file linked from contributor docs and reference during PR review.
