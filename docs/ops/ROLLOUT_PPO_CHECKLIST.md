# Rollout→PPO Checklist

## Capture
1. Preferred multi-scenario sweep (keeps metrics aligned with CI):
   ```bash
   python scripts/capture_rollout_suite.py \
     configs/scenarios/kitchen_breakfast.yaml \
   # Each capture directory now emits a manifest/metrics pair containing capture metadata
     configs/scenarios/queue_conflict.yaml \
     configs/scenarios/employment_punctuality.yaml \
     configs/scenarios/rivalry_decay.yaml \
     configs/scenarios/observation_baseline.yaml \
     --output-root tmp/rollout_refresh --compress
   ```
2. Inspect the per-scenario folders under `tmp/rollout_refresh/<scenario>/` and confirm:
   - `rollout_sample_manifest.json`
   - `rollout_sample_metrics.json`
   - `rollout_sample_*.npz/json`
3. Single-scenario spot captures remain available while iterating:
   ```bash
   python scripts/capture_rollout.py configs/scenarios/<scenario>.yaml      --output captures/<scenario> --compress
   ```
   Manifest files now include a `metadata` block (config id, scenario name, capture timestamp); keep these committed alongside per-agent entries.
   Add `--auto-seed-agents` for smoke captures without scripted agents, or
   use `python scripts/run_training.py <config> --rollout-ticks N --rollout-save-dir tmp/<scenario>`
   when you need the `RolloutBuffer` scaffolding.

## Train PPO
1. Execute training with captured data:
 ```bash
  python scripts/run_training.py configs/scenarios/<scenario>.yaml \
    --mode replay --train-ppo --capture-dir captures/<scenario> --epochs 2 --ppo-log logs/<scenario>_ppo.jsonl
  ```
2. Inspect epoch logs for `baseline_*` fields, conflict telemetry, and loss metrics.
   - Confirm `telemetry_version` is `1.1`, `kl_divergence` is numeric, and
     `conflict.rivalry_*` keys are present (see sample in
     `docs/samples/ppo_conflict_telemetry.jsonl`).
   - Run `python scripts/validate_ppo_telemetry.py logs/<scenario>_ppo.jsonl --relative` to enforce schema and baseline drift bounds (per-epoch/aggregate deltas + relative percentages). Version 1.1 requires extra fields (`epoch_duration_sec`, `data_mode`, `cycle_id`, `batch_entropy_mean/std`, `grad_norm_max`, `kl_divergence_max`, `reward_advantage_corr`, `rollout_ticks`, `log_stream_offset`).
   - Optionally tail the run with `python scripts/telemetry_watch.py logs/<scenario>_ppo.jsonl --follow --kl-threshold 0.2 --grad-threshold 5.0 --entropy-threshold -0.2 --reward-corr-threshold -0.5 --queue-events-min 25 --queue-intensity-min 45 --late-help-min 1 --shift-takeover-max 1 --shared-meal-min 0 --chat-quality-min 0.0 --utility-outage-max 0 --shower-complete-min 1 --sleep-complete-min 1` (adjust per scenario using the table in `docs/ops/queue_conflict_baselines.md`). Add `--json` for automation.
   - Produce run summaries with `python scripts/telemetry_summary.py logs/<scenario>_ppo.jsonl --format markdown` (add `--baseline docs/samples/ppo_conflict_telemetry.jsonl` when comparing against canon).
   - Thin or rotate logs with `--ppo-log-frequency` (e.g., `--ppo-log-frequency 5`) and
     `--ppo-log-max-entries` to cap file size (creates suffixes like `.1`, `.2`).

## Regression
1. Merge refreshed metrics into the golden JSON (dry-run first to review changes):
   ```bash
   python scripts/merge_rollout_metrics.py tmp/rollout_refresh --dry-run
   python scripts/merge_rollout_metrics.py tmp/rollout_refresh
   ```
2. Run regression tests:
   ```bash
   pytest tests/test_rollout_capture.py
   pytest tests/test_training_replay.py -k capture
   ```
   The capture test parameterises across all scripted scenarios and validates
   against `docs/samples/rollout_scenario_stats.json`.
3. CI mirrors this workflow via the **Capture rollout goldens** step. The
   follow-on drift check fails when any metric diverges by more than 2% (or
   an absolute 1e-6). The captured metrics are uploaded as the
   `rollout-golden-metrics` artifact—download it when reviewing discrepancies.
4. Treat an unexpected drift as a hold: investigate the scenario change, revert
   the behaviour, or intentionally refresh the golden metrics after sign-off.

## Notes
- Scenario captures are deterministic (torch seeding handled in `PolicyRuntime`).
- CI runs `tests/test_rollout_capture.py` separately; keep capture runtimes short.
- For behaviour cloning & anneal acceptance:
  1. Ensure production dataset manifest/checksum entries exist (`data/bc_datasets/versions.json`).
  2. Recompute checksums before training (see Ops Handbook helper); block rollout if mismatched.
  3. Run `python - <<'PY'` harness snippet to execute `run_bc_training` against the manifest; confirm
     accuracy ≥ configured threshold.
  4. Run `TrainingHarness.run_anneal` with `log_dir=artifacts/m5/acceptance/logs` and archive
     `anneal_results.json` + summary (include watcher output, dashboard screenshots if available).
  5. Perform rollback drill by raising `anneal_accuracy_threshold`; document outcome in
     `docs/certificates/M5_BC_ANNEAL_ACCEPTANCE.md`.
  6. Package release bundle:
     - Dataset artefacts: manifest + checksums + `audit_bc_datasets.py` report.
     - Anneal artefacts: `anneal_results.json`, `telemetry_summary` markdown, dashboard capture.
     - Decision log: signed acceptance report, go/no-go notes.
  7. If watcher or rehearsal exits with `HOLD`, freeze promotion, run `telemetry_watch.py --anneal-bc-min 0.9 --anneal-loss-max 0.1` on the log, and log remediation steps; `FAIL` requires rollback.
