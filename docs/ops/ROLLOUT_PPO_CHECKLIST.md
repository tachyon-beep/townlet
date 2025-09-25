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
     (new `RolloutBuffer` scaffolding; produces the same manifest/metrics format).

## Train PPO
1. Execute training with captured data:
   ```bash
   python scripts/run_training.py configs/scenarios/<scenario>.yaml \
     --train-ppo --capture-dir captures/<scenario> --epochs 2 --ppo-log logs/<scenario>_ppo.jsonl
   ```
2. Inspect epoch logs for `baseline_*` fields and loss metrics.
   - Confirm `telemetry_version` is `1` and `kl_divergence` is numeric (see
     sample in `docs/samples/ppo_epoch_log.jsonl`).
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
   `docs/ROLLOUT_CAPTURE_GUIDE.md#refreshing-golden-metrics` for the update
   procedure.)

## Notes
- Scenario captures are deterministic (torch seeding handled in `PolicyRuntime`).
- CI runs `tests/test_rollout_capture.py` separately; keep capture runtimes short.
