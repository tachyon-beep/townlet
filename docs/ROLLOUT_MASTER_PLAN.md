# Rollout & Replay Capture Master Plan

## Objective
Build a reproducible pipeline to capture live Townlet rollouts, transform them into
generalised replay samples, and feed them into PPO training/testing workflows.

## Current Capabilities
- `PolicyRuntime` buffers per-agent action/reward/done data and logs policy log-probs + value
  predictions via on-demand torch networks.
- `frames_to_replay_sample` converts buffered frames into NPZ/JSON packages with multi-step
  tensors and metadata (action lookup, timesteps, bootstrapped value baselines).
- `scripts/capture_rollout.py` runs the simulation loop for configurable tick counts, optionally
  seeding placeholder agents, and emits per-agent samples plus a manifest. Usage/documentation is
  covered in `docs/ROLLOUT_CAPTURE_GUIDE.md`.
- Replay ingestion path fully supports multi-step trajectories for PPO (`TrainingHarness.run_ppo`).
- Scenario configs under `configs/scenarios/` define deterministic object/agent layouts with
  scripted schedules (kitchen breakfast rush, queue conflict, employment punctuality, rivalry decay,
  observation baseline) and emit per-sample metrics (`*_metrics.json`). CI runs
  `tests/test_rollout_capture.py` to exercise these captures against golden
  metrics in `docs/samples/rollout_scenario_stats.json`.
- `scripts/run_training.py` accepts `--capture-dir` to ingest captured manifests/metrics, wire them
  into `ReplayDatasetConfig.from_capture_dir`, and surface baseline logs (`baseline_reward_*`,
  `baseline_log_prob_mean`) during PPO.
- Use `--ppo-log-frequency` and `--ppo-log-max-entries` to control NDJSON volume when running longer
  training jobs (logs rotate to `<name>.1`, `<name>.2`, ... when capped).
- Regression tests parameterise PPO-on-capture runs across all scripted scenarios
  (`tests/test_training_replay.py::test_training_harness_run_ppo_on_capture`).
- Operational runbook lives in `docs/ops/ROLLOUT_PPO_CHECKLIST.md`.
- PPO epoch telemetry sample (`telemetry_version` 1) is published under
  `docs/samples/ppo_epoch_log.jsonl` for dashboard consumers.
  Use `scripts/ppo_telemetry_plot.py` for a quick visualization of loss/KL trends.
- `TrainingHarness.capture_rollout` + `RolloutBuffer` provide a CLI-assisted rollout capture path
  (`--rollout-ticks` / `--rollout-save-dir`) ahead of full Phase 4 integration.

## Phase 2 Hardening Status — PPO Integration
- **Dataset plumbing:** capture CLI now serialises per-sample metrics, and replay datasets hydrate
  those metrics, exposing dataset-level baselines.
- **Training harness:** PPO epochs emit `baseline_*` telemetry derived from captured metrics for
  drift comparison and logging to JSONL.
- **Automation:** CI keeps scenario captures exercised via `tests/test_rollout_capture.py`; PPO
  smoke tests rely on torch availability and are skipped otherwise.
- **Telemetry tests:** PPO JSONL logs are schema-checked during scenario regression to ensure
  baseline metrics and conflict telemetry remain stable (`tests/test_training_replay.py`).

### How to Run Scenario-Based PPO
1. Capture scenarios (single config or suite) – see
   `docs/ROLLOUT_CAPTURE_GUIDE.md#running-ppo-with-captured-scenarios`.
2. Train via `scripts/run_training.py CONFIG --train-ppo --capture-dir <capture>` to replay captured
   batches with optional shuffling/seed flags.
3. Inspect PPO logs for the `baseline_*` fields to ensure replay parity. Follow the ops checklist
   for regression updates (`docs/ops/ROLLOUT_PPO_CHECKLIST.md`).

## Gaps & Roadmap
1. **Scenario Catalog Maintenance** *(Ongoing)*
   - Extend coverage beyond current five exemplars; document new additions alongside metrics.
2. **Rollout Validation & Regression** *(Complete for baseline scenarios / Ongoing for new ones)*
   - Keep golden stats in `docs/samples/rollout_scenario_stats.json` synchronised with intentional
     behaviour changes; refresh via capture suite CLI.
3. **Tooling Enhancements** *(Planned)*
   - CLI options for filtered manifests, per-agent slicing, compression (partial: compression done).
4. **Phase 3 – Telemetry Enhancements** *(Upcoming)*
   - Enrich PPO telemetry schema and dashboards beyond baseline comparisons.

## Scripted Scenario Analysis
See `docs/ROLLOUT_SCENARIOS.md` for detailed proposals on scenario configs, capture strategy, and
validation hooks.

## Validation Checklist
- `python -m pytest tests/test_training_replay.py`
- `python -m pytest tests/test_ppo_utils.py`
- `python -m pytest tests/test_training_cli.py`
- `python -m pytest tests/test_config_loader.py`
- `python scripts/capture_rollout.py CONFIG --ticks N --output OUTPUT_DIR`
- Inspect generated NPZ/JSON: ensure non-zero log-probs/value_preds when torch available.

## Next Steps
- Finalise scripted scenario specification and integrate into CI/regression suite.
- Evaluate storage requirements for scenario manifests and plan for sample rotation.
