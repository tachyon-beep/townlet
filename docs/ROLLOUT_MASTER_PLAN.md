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
  observation baseline) and emit per-sample metrics (`*_metrics.json`).

## Gaps & Roadmap
1. **Real Policy Outputs in Rollouts** *(Complete)*
   - Log softmax probabilities and value heads for each captured frame.
2. **Deterministic Scenario Catalog** *(In Progress)*
   - Provide scripted configs to generate labelled replay datasets.
3. **Rollout Validation & Regression** *(Planned)*
   - Add pytest automation to run capture scripts on scenarios and verify schema + metrics.
4. **Tooling Enhancements** *(Planned)*
   - CLI options for filtered manifests, per-agent slicing, compression.

## Scripted Scenario Analysis
See `docs/ROLLOUT_SCENARIOS.md` for detailed proposals on scenario configs, capture strategy, and
validation hooks.

## Validation Checklist
- `python -m pytest tests/test_training_replay.py tests/test_ppo_utils.py tests/test_training_cli.py tests/test_config_loader.py`
- `python scripts/capture_rollout.py CONFIG --ticks N --output OUTPUT_DIR`
- Inspect generated NPZ/JSON: ensure non-zero log-probs/value_preds when torch available.

## Next Steps
- Finalise scripted scenario specification and integrate into CI/regression suite.
- Evaluate storage requirements for scenario manifests and plan for sample rotation.
