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

## Train PPO
1. Execute training with captured data:
   ```bash
   python scripts/run_training.py configs/scenarios/<scenario>.yaml \
     --train-ppo --capture-dir captures/<scenario> --epochs 2 --ppo-log logs/<scenario>_ppo.jsonl
   ```
2. Inspect epoch logs for `baseline_*` fields and loss metrics.

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
