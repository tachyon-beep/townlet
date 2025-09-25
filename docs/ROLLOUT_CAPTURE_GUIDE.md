# Rollout Capture Guide

This guide explains how to record live simulation trajectories and convert them into
replay samples for the PPO training harness.

## CLI Usage

```bash
python scripts/capture_rollout.py CONFIG --ticks 200 --output samples/rollout --auto-seed-agents
```

For scenario configs (under `configs/scenarios/`), the `scenario.ticks` value is
used automatically, and per-agent schedules defined in the config drive the
rollout via the scenario behavior controller.

Key options:
- `CONFIG`: path to a simulation YAML file.
- `--ticks`: number of simulation ticks to run before exporting frames.
- `--output`: directory where NPZ/JSON samples and a manifest will be written.
- `--agent`: optionally filter capture to a single agent id.
- `--prefix`: filename prefix for generated samples and manifest.
- `--auto-seed-agents`: create placeholder agents (alice/bob) if the config
  does not spawn any, useful for smoke-testing capture in empty worlds.

The script writes one sample per agent with map/features stacked over the
captured timesteps and produces `<prefix>_manifest.json` referencing NPZ/JSON
assets.

Additionally, `<prefix>_metrics.json` summarises per-sample statistics such as
timesteps, reward totals, average log-probs/value predictions, rivalry stats,
and action distributions to simplify scenario tuning.

## From Frames to Replay Batches

`PolicyRuntime` buffers actions/rewards/done flags after each tick. When
`SimulationLoop.step` builds observations, the runtime flushes per-agent frames.
`scripts/capture_rollout.py` calls `PolicyRuntime.collect_trajectory()` and
converts those frames to replay samples via
`townlet.policy.replay.frames_to_replay_sample`.

Each frame contributes:
- `map`: observation map of shape `(channels, height, width)`
- `features`: 1D hybrid feature vector
- `action`: serialized primitive action (converted to an integer id)
- `reward`: scalar reward for the tick
- `done`: termination flag

The assembled replay sample stores:
- `map`: stacked maps `(timesteps, channels, height, width)`
- `features`: stacked features `(timesteps, feature_dim)`
- `actions`: integer ids `(timesteps,)`
- `old_log_probs`: placeholder zeros (to be replaced once policy logits are
  logged)
- `value_preds`: zeros with an extra bootstrap element `(timesteps + 1,)`
- `rewards`: scalar rewards `(timesteps,)`
- `dones`: termination flags `(timesteps,)`
- `metadata`: feature names, timestep counts, action lookup table, etc.

## Next Steps

- Integrate real policy logits/value predictions into the trajectory frames so
  replay samples contain accurate `old_log_probs`/`value_preds`.
- Expand capture tooling with deterministic scenarios (e.g., scripted agents) to
  generate labelled datasets for regression tests.
