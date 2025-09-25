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

## Running PPO with Captured Scenarios

```bash
# Capture rollout samples (kitchen breakfast example)
python scripts/capture_rollout.py configs/scenarios/kitchen_breakfast.yaml --output tmp/kitchen

# Run PPO against captured manifest/metrics
python scripts/run_training.py configs/scenarios/kitchen_breakfast.yaml \
  --train-ppo --capture-dir tmp/kitchen --epochs 2 --ppo-log tmp/kitchen/ppo_log.jsonl
```

Use `--ppo-log-frequency` to thin the NDJSON output (e.g., `--ppo-log-frequency 5` to log every
fifth epoch) and `--ppo-log-max-entries` to rotate large logs (producing suffixes such as
`ppo_log.jsonl.1`).

`TrainingHarness.run_ppo` consumes the capture directory via `--capture-dir`,
loading both `rollout_sample_manifest.json` and `rollout_sample_metrics.json`
to seed baseline comparisons in the PPO epoch logs.

### Telemetry Schema Quick Reference

- Epoch logs (`telemetry_version` 1.1) surface loss components, baseline metrics,
  and conflict aggregates (`conflict.rivalry_*`).
- Inspect `docs/samples/ppo_conflict_telemetry.jsonl` for a canonical
  NDJSON record containing the required keys.
- Run `python scripts/ppo_telemetry_plot.py` to plot `loss_total` and
  `kl_divergence` (falls back to textual summaries if matplotlib is absent).
- Validate new logs with `python scripts/validate_ppo_telemetry.py <log> [--baseline docs/samples/ppo_conflict_telemetry.jsonl] [--relative]` — version 1.1 requires cycle IDs, data modes, entropy/grad maxima, and streaming offsets.
- Watch long runs with `python scripts/telemetry_watch.py <log> --follow --kl-threshold 0.2 --grad-threshold 5.0 --entropy-threshold -0.2 --reward-corr-threshold -0.5` to surface regressions quickly (use `--json` for machine-readable alerts).
- Generate operator summaries with `python scripts/telemetry_summary.py <log> [--baseline docs/samples/ppo_conflict_telemetry.jsonl] --format markdown` before filing status reports.
- For exploratory analysis open `docs/notebooks/telemetry_quicklook.ipynb` in Jupyter or VS Code.

For early Phase 4 work, the training CLI now supports lightweight rollout capture with optional PPO
integration:

```bash
python scripts/run_training.py configs/examples/poc_hybrid.yaml \
  --rollout-ticks 50 --rollout-save-dir tmp/rollout_stub \
  --rollout-auto-seed-agents --train-ppo --epochs 1 \
  --ppo-log tmp/rollout_stub/ppo.jsonl
```

This leverages `TrainingHarness.run_rollout_ppo` and `RolloutBuffer` to capture trajectories,
persist manifests/metrics, and immediately feed PPO via the in-memory dataset.

## Refreshing Golden Metrics

The regression suite (`tests/test_rollout_capture.py`,
`tests/test_training_replay.py::test_training_harness_run_ppo_on_capture`) compares
captures against the canonical metrics stored in
`docs/samples/rollout_scenario_stats.json`. Refresh the baselines whenever
scenario behaviour changes:

1. Capture fresh metrics for each scripted scenario (exclude `_template.yaml`):
   ```bash
   source .venv/bin/activate
   python scripts/capture_rollout_suite.py \
     configs/scenarios/kitchen_breakfast.yaml \
     configs/scenarios/queue_conflict.yaml \
     configs/scenarios/employment_punctuality.yaml \
     configs/scenarios/rivalry_decay.yaml \
     configs/scenarios/observation_baseline.yaml \
     --output-root tmp/rollout_refresh --compress
   ```
2. Preview the merge with the helper script (skipping `_template.yaml` by default):
   ```bash
   python scripts/merge_rollout_metrics.py tmp/rollout_refresh --dry-run
   ```
   When satisfied, rerun without `--dry-run` (or point `--output` at a staging
   file) to update `docs/samples/rollout_scenario_stats.json` while preserving
   the `{scenario -> sample -> metrics}` layout.
3. Re-run the regression tests to confirm the new baselines:
   ```bash
   python -m pytest tests/test_rollout_capture.py
   python -m pytest tests/test_training_replay.py -k capture
   ```
4. Remove the temporary capture directory (`rm -rf tmp/rollout_refresh`) once the
   golden stats are updated.

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
