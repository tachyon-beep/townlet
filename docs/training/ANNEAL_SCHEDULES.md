# Anneal Schedules (BC ↔ PPO)

## Config Structure
```
training:
  bc:
    manifest: data/bc_datasets/manifests/idle_curated.json
    learning_rate: 0.001
    batch_size: 64
    epochs: 5
  anneal_accuracy_threshold: 0.9
  anneal_enable_policy_blend: false
  anneal_schedule:
    - cycle: 0
      mode: bc
      epochs: 5
      bc_weight: 1.0
    - cycle: 1
      mode: ppo
      epochs: 2
    - cycle: 2
      mode: bc
      epochs: 3
      bc_weight: 0.5
    - cycle: 3
      mode: ppo
      epochs: 2
```

- `bc_weight` indicates intended influence of BC phase (telemetry only; planning aid).
- `anneal_accuracy_threshold` triggers rollback if BC accuracy drops below the threshold.
- `anneal_enable_policy_blend`: set to `true` to allow runtime action blending based on the anneal ratio (defaults to false for safe rollout).

## Running the Schedule
```python
from townlet.config import load_config
from townlet.policy.runner import TrainingHarness

config = load_config(Path("configs/examples/poc_hybrid.yaml"))
harness = TrainingHarness(config)
results = harness.run_anneal(log_dir=Path("logs/anneal"))
print(results)
```

Each entry in `results` contains metrics per cycle.
- BC entries: `accuracy`, `loss`, `passed`, `bc_weight`
- PPO entries: full PPO epoch summary (`loss_total`, `transitions`, etc.)

## Rollback Behaviour
If a BC stage `passed` flag is `False`, the harness flags the stage with `rolled_back` and stops the
schedule. Hook this into snapshot/rollback workflows (Phase 5.4) to restore previous checkpoints.

## Operational Logging
When `log_dir` is provided, results are stored in `anneal_results.json`. Emit summary metrics to ops dashboards.

## Future Extensions
- Mixed control (percentage of environment steps delegated to BC vs PPO) — planned.
- Automated anneal simulator to evaluate schedules pre-deployment.
- Telemetry integration (Phase 5.4) for drift monitoring.
