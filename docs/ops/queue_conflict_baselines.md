# Queue Conflict Telemetry Baselines

| Scenario | Mode | Rollout Ticks | Queue Conflict Events | Intensity Sum | Notes |
| --- | --- | --- | --- | --- | --- |
| queue_conflict | mixed (replay→rollout) | 40 | 32.0 | 52.75 | Captured via `capture_rollout.py` then `run_training.py --mode mixed`; store log `tmp/phase4/qc/ppo_log.jsonl`. |
| employment_punctuality | mixed (replay→rollout) | 60 | 39.0 | 58.50 | Captured during baseline run to observe cross-scenario telemetry; log `tmp/phase4/employment/ppo_mixed.jsonl`. |
| observation_baseline | rollout | 20 | 0.0 | 0.00 | Control scenario (no conflicts); canonical sample `docs/samples/ppo_conflict_telemetry.jsonl`. |

Use these values as guards when evaluating mixed-mode rollout runs. Watch thresholds can be set slightly below these baselines (e.g., `--queue-events-min 25`, `--queue-intensity-min 45`).
