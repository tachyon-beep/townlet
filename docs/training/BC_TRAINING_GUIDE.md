# Behaviour Cloning Training Guide (Draft)

## Overview
Behaviour cloning (BC) trains a supervised policy from curated scripted trajectories. This guide
summarises configuration, commands, and evaluation checkpoints.

## Data Pipeline
1. **Capture** scripted runs:
   ```bash
   python scripts/capture_scripted.py configs/examples/poc_hybrid.yaml --scenario idle --ticks 200 --output data/bc_datasets/captures/idle
   ```
2. **Curate** trajectories:
   ```bash
   python scripts/curate_trajectories.py data/bc_datasets/captures/idle --output data/bc_datasets/manifests/idle_curated.json --min-timesteps 20 --min-reward 0.0
   ```
3. Record dataset info in `data/bc_datasets/README.md` (tags, version, checksum).

## Training
Example snippet (until integrated with the main harness):
```python
from townlet.policy import BCTrainer, BCTrainingConfig, BCTrajectoryDataset, load_bc_samples
from townlet.policy.models import ConflictAwarePolicyConfig

samples = load_bc_samples(Path("data/bc_datasets/manifests/idle_curated.json"))
dataset = BCTrajectoryDataset(samples)
policy_cfg = ConflictAwarePolicyConfig(feature_dim=dataset._features.shape[1], map_shape=(dataset._maps.shape[1], dataset._maps.shape[2], dataset._maps.shape[3]), action_dim=int(dataset._actions.max() + 1))
trainer = BCTrainer(BCTrainingConfig(learning_rate=1e-3, batch_size=64, epochs=10), policy_cfg)
metrics = trainer.fit(dataset)
```
*(In-code helper to compute map shape forthcoming; use dataset shapes for now.)*

## Evaluation
- `BCTrainer.evaluate(dataset)` returns accuracy over the dataset.
- `evaluate_bc_policy(model, dataset)` can run standalone evaluations (returns accuracy & sample count).
- Target: ≥90% accuracy vs scripted policy (tunable per scenario).

## Telemetry / Ops
- Emit evaluation metrics (accuracy, reward_sum) into ops dashboards (Phase 5.2-T5).
- Store evaluation JSON alongside manifests for drift tracking.

## TODO
- Integrate BC trainer into main training harness/CLI.
- Expose evaluation & telemetry commands.
- Document anneal schedule once Phase 5.3 lands.
- See `docs/training/ANNEAL_SCHEDULES.md` for anneal configuration guidance.
