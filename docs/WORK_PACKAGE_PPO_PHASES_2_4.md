# PPO Integration Roadmap — Phases 2–4

## Overview
This document captures the detailed plan for evolving the conflict-aware PPO training stack across the remaining phases. Each phase is broken into concrete tasks and steps to ensure repeatable execution and clear ownership.

## Overall Risks
| Risk | Description | Mitigation | Severity |
| --- | --- | --- | --- |
| Torch dependency | Missing/incorrect torch version blocks training | Provide install guards, document required version | Medium |
| Replay schema drift | Observation features change, breaking loader | Schema guards/tests, validation CLI | Medium |
| Resource usage | PPO on CPU may be slow | Document requirements, allow streaming + small batch | Medium |
| Telemetry volume | NDJSON logs grow quickly | Include sampling/configurable frequency | Low |


---

## Phase 2 — PPO Loss & Optimizer Integration
**Goal:** Implement full PPO training loop leveraging replay batches, including policy/value losses, entropy bonus, advantage estimation, and optimizer state management.
**Risk Level:** High
**Status:** ✅ Completed (2025-09-27) — PPO loop, rollout ingestion, telemetry schema/tests, drift analytics tooling, and ops documentation delivered. Future tweaks (e.g., richer dashboards) feed into Phase 3.
| Risk | Impact | Mitigation | Severity |
| --- | --- | --- | --- |
| Loss instability | Incorrect advantage or loss math can destabilise training | Unit tests with synthetic data; validate gradients | High |
| Gradient explosion | Large gradients during replay batches | Gradient clipping (`max_grad_norm`), learning-rate guard | Medium |
| Config drift | Missing hyperparameters in config cause runtime errors | Expand tests validating PPOConfig defaults | Medium |

### Tasks & Steps
1. **Hyperparameter & Config Alignment**
   - Extend `PPOConfig` with additional knobs: `max_grad_norm`, `value_clip`, `advantage_normalization`, `num_mini_batches`.
   - Update config loader tests to cover new fields; document defaults.

2. **Advantage & Target Computation**
   - Implement GAE (Generalized Advantage Estimation) utility handling replay batches (requires metadata for rewards, values, dones when we move to rollout).
   - Provide helper to normalize advantages when configured.

3. **Loss Functions**
   - Implement clipped surrogate policy loss, value loss (with optional clipping), entropy bonus.
   - Structure losses to return scalar totals plus components for logging.

4. **Optimizer State & Training Loop**
   - Instantiate Adam (or configurable optimizer) using `learning_rate` from `PPOConfig`.
   - Add gradient clipping (`max_grad_norm`), zeroing, and step scheduling (future hook).
   - Support multiple epochs and mini-batch shuffling over replay dataset.

5. **Unit & Integration Tests**
   - Add deterministic test feeding synthetic logits/values to validate loss math.
   - Smoke test training loop on replay manifest ensuring loss decreases over epochs (or at least stays finite).

6. **CLI/Logging Updates**
   - Extend PPO CLI to surface new hyperparameters (e.g., `--max-grad-norm`).
   - Log loss components, advantage stats, gradient norms per epoch.

### Deliverables
- Updated `TrainingHarness.run_ppo` performing real optimization on replay data.
- Loss/optimizer utilities with unit coverage.
- Documentation updates describing PPO hyperparameters and workflow.

---

## Phase 3 — Telemetry & NDJSON Logging Enhancements
**Risk Level:** Medium
**Status:** ✅ Completed (2025-09-28) — telemetry_version 1.1 schema, streaming cycle IDs, validator/watch/summary tooling, CI harness validation, and operator docs delivered.
**Goal:** Provide rich training telemetry for queue conflicts and rivalry signals, enabling dashboards and analytics.
| Risk | Impact | Mitigation | Severity |
| --- | --- | --- | --- |
| Log volume | NDJSON grows quickly, affecting disk | Allow sampling frequency and file rotation | Medium |
| Schema mismatch | Consumers fail to parse new telemetry fields | Document schema, provide validator tests | Medium |
| Performance overhead | Logging slows training loop | Buffer writes, allow disabling telemetry | Low |

### Tasks & Steps
**Risk Level:** High
1. **Telemetry Schema Definition**
   - Define NDJSON schema for training telemetry (epoch summary, per-batch stats) including conflict metrics.
   - Update `TELEMETRY_CHANGELOG.md` and training guide.

2. **Logging Implementation**
   - Add NDJSON writer that records per-epoch loss components, conflict averages, and KL/clip fractions.
   - Include queue conflict aggregates from replay batches (collected via `ReplayBatch.conflict_stats`).

3. **Visualization Hooks**
   - Provide sample JSONL/NDJSON files in `docs/samples/` with instructions on plotting (e.g., via notebooks or CLI).

4. **Validation Tests**
- Add pytest ensuring log files contain expected keys and parse cleanly.
- Optionally create CLI flag `--ppo-ndjson` to specify NDJSON output path.

**Status Notes:**
- Telemetry schema test (`tests/test_training_replay.py::test_training_harness_ppo_conflict_telemetry`)
  runs in CI to guard rivalry metrics and NDJSON shape.
- `scripts/validate_ppo_telemetry.py` now reports per-epoch/aggregate drift (with optional relative deltas) and is executed in CI against the canonical sample; version 1.1 rules cover cycle IDs, data modes, entropy/grad maxima, and streaming offsets.
- CI harness run captures a fresh scenario (`capture_rollout.py`) and validates the generated PPO log so telemetry_version 1.1 stays enforced during pipeline runs.
- Regression coverage added in `tests/test_telemetry_validator.py` to guard validator behaviour on both valid and missing-conflict scenarios.
- `scripts/telemetry_watch.py` tails PPO logs with thresholded alerts; `docs/notebooks/telemetry_quicklook.ipynb` offers quick-look visualisation for operators.
- `scripts/telemetry_summary.py` generates text/markdown/JSON summaries (per-epoch extremes, drift vs baseline) for ops reports.
- Sample epoch log with conflict metrics is published at
  `docs/samples/ppo_conflict_telemetry.jsonl` and referenced throughout the
  capture guide and ops checklist.
- Schema upgrade draft (`docs/design/PPO_TELEMETRY_SCHEMA_PLAN.md`) enumerates
  v1.1 fields (epoch duration, cycle IDs, entropy/grad maxima, data mode) and
  compatibility steps.

5. **Documentation**
   - Update `IMPLEMENTATION_NOTES`, `ARCHITECTURE_INTERFACES`, and training guide with telemetry instructions.

### Deliverables
- NDJSON logging path for PPO runs.
- Samples + validation scripts/tests.
- Docs referencing telemetry workflow.

---

## Phase 4 — Live Rollout Integration & Documentation Finalisation
**Risk Level:** High
**Goal:** Connect PPO training with live simulation rollouts, ensuring conflict telemetry influences on-policy data, and wrap documentation for stakeholders.
| Risk | Impact | Mitigation | Severity |
| --- | --- | --- | --- |
| Simulation drift | Live rollouts diverge from replay assumptions | Start with short rollouts, compare telemetry vs replay | High |
| Performance | Rollout + training strain CPU | Support configurable rollout length, streaming, optional GPU | High |
| Operational complexity | More steps to run training pipelines | Provide documentation, scripts, automation | Medium |
| Rollout buffer leak | Long alternating runs exhaust memory | Reuse SimulationLoop/PolicyRuntime where possible, monitor memory, add cleanup hooks | Medium |
| Telemetry backlog | Streaming log/NDJSON rotation can't keep up | Monitor `log_stream_offset`, add watch thresholds, run soak tests (10+ cycles) | Medium |
| CI runtime creep | Capture + PPO validation extends pipeline duration | Keep harness iterations short (ticks/epochs) and cache staging artifacts | Low |
| Schema regressions | Future tweaks break v1.1 controls | Validator tests cover v1.1 and back-compat, CI run generates fresh logs | Medium |

### Tasks & Steps
**Risk Level:** High
1. **Environment Runner Integration**
   - Implement rollout buffer capturing transitions from `PolicyRuntime` → environment.
   - Ensure observations include conflict features; rewards/advantages computed from live data.
   - *Pre-work (Complete):* `RolloutBuffer` scaffolding and `TrainingHarness.capture_rollout` added to capture/save trajectories without PPO integration. In-memory dataset path (`build_dataset`) allows rollout captures to feed PPO directly (no manifest required).
   - Scenario coverage plan: use `queue_conflict`, `employment_punctuality`, `rivalry_decay`, and `observation_baseline` (plus `kitchen_breakfast` for soak tests). For each scenario, capture to `artifacts/phase4/<scenario>` and archive summaries (`ppo_*.jsonl`, `watch.jsonl`, `summary.md`). Verify agents spawn without auto-seed. Capture queue conflict events/intensity from telemetry for rollout datasets and record baselines (`docs/ops/queue_conflict_baselines.md`).
   - *Status (2025-09-29):* Completed mixed-mode captures for queue_conflict, employment_punctuality, rivalry_decay, and rollout control; artefacts summarised in `docs/ROLLOUT_PHASE4_ACCEPTANCE.md` and checked into `artifacts/phase4/`.

2. **Replay vs. Rollout Modes**
   - Allow `TrainingHarness` to switch between replay-only (offline) and rollout (online) modes.
   - Provide config/CLI flags to toggle modes and specify rollout length.
   - `training.source` governs defaults (`replay`/`rollout`/`mixed`); CLI override via `--mode` with supporting flags (`--rollout-ticks`, `--capture-dir`, `--replay-manifest`).

3. **Telemetry Bridge**
   - During rollouts, collect queue conflict events via telemetry subscriber; aggregate for logging. *(Complete — RolloutBuffer records counts/intensity and PPO telemetry emits `queue_conflict_*` fields; validator/tests updated.)*
   - Ensure training telemetry (Phase 3) captures both replay and rollout runs. *(Covered by v1.1 schema + endurance tests; watcher/summary tooling verifies outputs.)*

4. **End-to-End Validation** *(Phase 4)*
   - Smoke test training harness performing short rollouts and PPO updates, verifying no crashes and telemetry output present. *(Complete via queue_conflict/employment/rivalry/baseline runs.)*
   - Add documentation on running live rollouts, config prerequisites (torch, hardware considerations). *(Complete — `docs/OPS_HANDBOOK.md` mixed-mode workflow, checklist refresh.)*
   - Execute alternating capture→PPO cycles (≥10) per primary scenario, store summaries (`telemetry_summary.py`) and watcher logs for audit. *(Initial mixed-mode cycles captured; endurance soak remains a follow-up task.)*

5. **Documentation & Certificates** *(Ongoing)*
   - Update `MASTER_PLAN_PROGRESS`, training guide, ops docs. *(Complete — ops handbook, master plan, acceptance report refreshed.)*
   - Issue completion certificate upon acceptance. *(Complete — see `docs/COMPLETION_CERTIFICATE_PPO_PHASE2_4.md`.)*

### Deliverables
- PPO training harness capable of live rollouts with conflict-aware telemetry.
- Updated docs and samples demonstrating full workflow.
- Final milestone certificate for PPO integration.

---

**Prepared by:** Townlet Engineering Team — PPO Integration Task Force
## Briefing Snapshot (Pre-Compact Reference)
- **Torch Environment:** `torch 2.8.0+cpu` installed in `.venv`; guard remains for environments without torch.
- **Replay Assets:** Manifests/samples live in `docs/samples/` (`observation_hybrid_sample_{base,conflict_high,conflict_low}.npz/json`, `replay_manifest.json`).
- **Config:** `PPOConfig` currently exposes learning rate, clipping, loss coefficients, epochs, batch size; Phase 2 will extend with GAE/grad knobs.
- **Harness State:** `TrainingHarness.run_ppo` logs epoch summaries, writes JSONL when `--ppo-log` provided; optimization still placeholder (mean feature loss).
- **Open Tasks:**
  - None. Soak harness and drift analytics captured under `artifacts/phase4/queue_conflict_soak/`.
- **Risks to Monitor:** loss instability, telemetry volume, rollout performance.
- **Command Cheatsheet:**
  - Replay validation: `python scripts/run_replay.py <sample> --validate`.
  - PPO stub smoke: `python scripts/run_training.py configs/examples/poc_hybrid.yaml --replay-manifest docs/samples/replay_manifest.json --train-ppo --epochs 2 --ppo-log docs/samples/ppo_log.jsonl`.
