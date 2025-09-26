# Queue Conflict Telemetry Baselines

| Scenario | Mode | Rollout Ticks | Queue Conflict Events | Intensity Sum | Notes |
| --- | --- | --- | --- | --- | --- |
| queue_conflict | mixed (replay→rollout) | 40 | 32.0 | 52.75 | Captured via `capture_rollout.py` then `run_training.py --mode mixed`; log `artifacts/phase4/queue_conflict/ppo_mixed.jsonl`. |
| employment_punctuality | mixed (replay→rollout) (baseline) | 60 | 39.0 | 58.50 | Baseline for employment scenario; log `artifacts/phase4/employment_punctuality/ppo_mixed.jsonl`. |
| rivalry_decay | mixed (replay→rollout) | 50 | 32.0 | 48.00 | Rivalry scenario; log `artifacts/phase4/rivalry_decay/ppo_mixed.jsonl`. |
| observation_baseline | rollout | 30 | 0.0 | 0.00 | Control scenario; log `artifacts/phase4/observation_baseline/ppo_rollout.jsonl`. |

Use these targets to configure `telemetry_watch.py --queue-events-min` and
`--queue-intensity-min` thresholds. Set guardrails ~10–15% below the tabled values unless
intentionally exploring lower conflict pressure.
