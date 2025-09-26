# Rollout→PPO Checklist

## Capture
1. Run scenario capture:
   ```bash
   python scripts/capture_rollout.py configs/scenarios/<scenario>.yaml \
     --output captures/<scenario> --compress
   ```
2. Verify artefacts:
   - `rollout_sample_manifest.json`
   - `rollout_sample_metrics.json`
   - `rollout_sample_*.npz/json`
   - Alternatively, use `python scripts/run_training.py <config> --rollout-ticks N --rollout-save-dir tmp/<scenario>`
     (add `--rollout-auto-seed-agents` for quick smoke captures)
     (new `RolloutBuffer` scaffolding; produces the same manifest/metrics format).

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
   - Optionally tail the run with `python scripts/telemetry_watch.py logs/<scenario>_ppo.jsonl --follow --kl-threshold 0.2 --grad-threshold 5.0 --entropy-threshold -0.2 --reward-corr-threshold -0.5 --queue-events-min 25 --queue-intensity-min 45 --late-help-min 1 --shift-takeover-max 1 --shared-meal-min 0 --chat-quality-min 0.0` (adjust per scenario using the table in `docs/ops/queue_conflict_baselines.md`). Add `--json` for automation.
   - Produce run summaries with `python scripts/telemetry_summary.py logs/<scenario>_ppo.jsonl --format markdown` (add `--baseline docs/samples/ppo_conflict_telemetry.jsonl` when comparing against canon).
   - Thin or rotate logs with `--ppo-log-frequency` (e.g., `--ppo-log-frequency 5`) and
     `--ppo-log-max-entries` to cap file size (creates suffixes like `.1`, `.2`).

## Regression
1. Update golden stats if scenario behaviour intentionally changes:
   ```bash
   python scripts/capture_rollout_suite.py \
     configs/scenarios/*.yaml --output-root tmp_suite --compress
   python scripts/merge_rollout_metrics.py tmp_suite --dry-run
   python scripts/merge_rollout_metrics.py tmp_suite
   ```
2. Run regression tests:
   ```bash
   pytest tests/test_rollout_capture.py
   pytest tests/test_training_replay.py -k capture
   ```
   (The PPO capture test parameterises across all scripted scenarios and validates
   baseline metrics against the golden stats; see
   `docs/rollout/ROLLOUT_CAPTURE_GUIDE.md#refreshing-golden-metrics` for the update
   procedure.)

## Notes
- Scenario captures are deterministic (torch seeding handled in `PolicyRuntime`).
- CI runs `tests/test_rollout_capture.py` separately; keep capture runtimes short.
