# Conflict-Aware PPO Integration Work Package

## Objective
Integrate the replay dataset + batching pipeline with initial PPO training scaffolding so conflict-aware signals (rivalry features, queue events) influence rollout and learning loops. Provide instrumentation and validation to ensure PPO batches reflect the new telemetry.

## Scope
- `townlet.policy.runner` PPO harness scaffolding.
- Replay dataloader → PPO buffer plumbing, basic loss computation stub.
- Telemetry validation during training runs, logging rivalry stats per epoch.
- Docs covering end-to-end conflict-aware training workflow.

## Deliverables
1. PPO training stub consuming `ReplayDataset` batches, computing dummy losses, and logging conflict feature summaries.
2. Replay manifest validation in CLI to ensure conflict-required fields before launching training.
3. Enhanced telemetry instrumentation: during training, record queue_conflict stats and rivalry feature histograms.
4. Documentation updates and pytest coverage for PPO stub execution with replay batches.

## Tasks
1. **API Design**
   - Define minimal PPO harness interface (`TrainingHarness.run_ppo`) using the existing runtime/loop.
   - Specify expected batch dict (maps, features, metadata) for future learner.
2. **Implementation**
   - Build PPO stub that iterates replay dataset, normalises conflict features (optional), and accumulates dummy loss.
   - Extend CLI with `--train-ppo` switch pointing to manifest/config for quick smoke.
3. **Telemetry & Logging**
   - Log per-epoch rivalry stats, queue conflict summaries; optionally export NDJSON for post-hoc analysis.
4. **Validation**
   - Add pytest ensuring PPO stub runs without NaNs, logs expected metrics.
   - Update docs (`IMPLEMENTATION_NOTES`, training guide) with PPO usage instructions.

## Risks
| Risk | Impact | Mitigation |
| --- | --- | --- |
| PPO stub diverges from future implementation | Medium | Keep stub modular and documented; align interfaces early. |
| Replay batches overwhelm memory during PPO | Medium | Use streaming loader + gradient accumulation; test on sample manifests. |
| Telemetry logging noisy | Low | Add sampling / summary statistics. |

## Risk Reduction
- Prototype PPO stub on replay manifest before real policies.
- Validate streaming loader path under PPO to ensure no memory creep.

## Success Criteria
- `python scripts/run_training.py ... --train-ppo --replay-manifest ...` runs, logs rivalry stats per epoch, and exits gracefully.
- Tests cover PPO stub run with sample manifest.
- Documentation reflects conflict-aware PPO loop.

## Phase Tracking
- Phase 1 (Model + Config) — Completed (config + torch guard + network stub)
- Phase 2 (Loss/Optimizer) — TODO
- Phase 3 (Telemetry/Logging) — TODO
- Phase 4 (Validation & Docs) — TODO
