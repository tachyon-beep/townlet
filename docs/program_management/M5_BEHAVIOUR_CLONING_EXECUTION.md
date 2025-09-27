# M5 – Behaviour Cloning & Anneal Execution Plan (2025-09-30)

**Milestone Objective:** Introduce a behaviour-cloning (BC) pathway fed by curated scripted trajectories, blend BC with PPO via scheduled anneal/rollout cycles, and ensure guardrails (drift monitoring, rollback triggers) protect live training.

## Phase Breakdown

### Phase 5.1 – Trajectory Capture Foundations
**Goal:** Produce high-quality scripted trajectories with reproducible curation pipeline.

#### Step 5.1-S1 – Capture Tooling & Schema
- **Task 5.1-T1:** Design trajectory schema (observations, actions, rewards, metadata).
  - Subtasks:
    1. Define NPZ/JSON structure aligned with existing replay samples.
    2. Document schema in `docs/rollout/TRAJECTORY_CAPTURE.md`.
    3. Update lint/tests to validate schema (unit parser).
- **Task 5.1-T2:** Build capture CLI (`scripts/capture_scripted.py`).
  - Subtasks:
    1. Implement scripted policy hooks (config-driven) for scenarios.
    2. Expose CLI options: scenario, ticks, output dir, metadata tags.
    3. Unit test CLI entrypoint (dry-run) + integration test with short scenario.

**Status (2025-09-30):**
- T1 complete — schema documented (`docs/rollout/TRAJECTORY_CAPTURE.md`), synthetic round-trip test (`tests/test_bc_capture_prototype.py`).
- T2 complete — capture CLI (`scripts/capture_scripted.py`) with idle scripted policy, default agent seeding, metadata/tags support; regression test (`tests/test_capture_scripted_cli.py`).

#### Step 5.1-S2 – Curation & Quality Metrics
- **Task 5.1-T3:** Define quality metrics (coverage, reward, constraint violations).
- **Task 5.1-T4:** Build curation script (`scripts/curate_trajectories.py`) to filter/label captures.
- **Task 5.1-T5:** Establish dataset catalogue (`data/bc_datasets/README.md`) with versioning + metadata.

**Status (2025-09-30):**
- T3 complete — quality metrics documented in `docs/rollout/TRAJECTORY_CAPTURE.md` (timesteps, reward sum, mean reward, constraint hooks).
- T4 complete — curation CLI implemented (`scripts/curate_trajectories.py`) with regression test (`tests/test_curate_trajectories.py`).
- T5 complete — dataset catalogue scaffolded at `data/bc_datasets/README.md` with workflow guidance.
- 2025-09-30 update — production idle dataset (`idle_v1_production`) captured and catalogued under `data/bc_datasets/captures/idle_v1`.

**Phase 5.1 Risk Assessment**
| Risk ID | Description | Probability | Impact | Mitigation / Tasks | Trigger / Owner |
|---------|-------------|-------------|--------|--------------------|-----------------|
| 5.1-R1 | Scripted policies produce low-quality trajectories (coverage gaps). | Medium | High | Define quality metrics, reject low-score captures, iterate scripted policies. | Dataset coverage < target | RL lead |
| 5.1-R2 | Capture tooling introduces schema drift vs replay samples. | Low | Medium | Schema doc + unit tests; reuse existing replay utilities. | Parser/test failures | DevEx |
| 5.1-R3 | Dataset versioning confusion. | Low | Medium | Catalogue with checksums + metadata, documentation in repo. | Missing provenance | Ops lead |

**Risk Reduction Activities**
- Build synthetic trajectory set to validate pipeline before full capture run.
- Schedule review with RL lead to assess scripted policies prior to bulk capture.

### Phase 5.2 – Behaviour Cloning Training Harness
**Goal:** Implement BC training workflows and validate performance vs scripted policies.

#### Risk Reduction (Pre-Phase)
- Prototype trainer on synthetic dataset to confirm convergence and uncover preprocessing mismatches.
  - Build tiny dataset (e.g., deterministic actions) and run one training epoch (noting loss -> ~0).
- Peer review BC architecture versus scripted policy behaviours (walkthrough with RL lead).
- Validate curated dataset manifest contains required metadata (quality metrics, tags).

**Status:** Synthetic trainer prototype implemented via `tests/test_bc_trainer.py` (overfit toy dataset).
Peer review + dataset manifest validation scheduled post-code drop.

#### Step 5.2-S1 – BC Model & Trainer
- **Task 5.2-T1:** Define BC model architecture (reuse PPO policy where feasible).
- **Task 5.2-T2:** Implement BC trainer (loss function, batching, checkpoints).
- **Task 5.2-T3:** Unit tests for trainer (overfitting on toy dataset) + smoke test using curated trajectories.

**Status:** Completed — `src/townlet/policy/bc.py` provides BC dataset loader + trainer reusing
`ConflictAwarePolicyNetwork`; tests (`tests/test_bc_trainer.py`) confirm convergence and evaluation.

#### Step 5.2-S2 – Evaluation & Metrics
- **Task 5.2-T4:** Build evaluation harness comparing BC vs scripted policy (accuracy ≥90%).
- **Task 5.2-T5:** Introduce BC drift dashboard (metrics exported to telemetry/ops).

**Status:** Completed — `BCTrainer.evaluate` + `evaluate_bc_policy` produce accuracy metrics; ops workflow
captures evaluation summaries via `scripts/bc_metrics_summary.py`. BC training guide added (`docs/training/BC_TRAINING_GUIDE.md`).

**Phase 5.2 Risk Assessment**
| Risk ID | Description | Probability | Impact | Mitigation / Tasks | Trigger / Owner |
|---------|-------------|-------------|--------|--------------------|-----------------|
| 5.2-R1 | BC model fails to reach accuracy target. | Medium | High | Hyperparameter sweeps, augment dataset, fallback to hybrid architecture. | Accuracy < 90% | RL lead |
| 5.2-R2 | Trainer diverges due to inconsistent preprocessing. | Low | Medium | Reuse replay normalization, tests to assert dataset/model alignment. | Loss NaN | DevEx |
| 5.2-R3 | Evaluation harness lacks coverage; false confidence. | Medium | Medium | Include multiple scenarios, measure per-behaviour metrics. | Evaluation gaps | QA |

**Risk Reduction Activities**
- Early prototyping with small dataset to validate convergence.
- Peer review of BC architecture vs scripted policy behaviours.

### Phase 5.3 – Anneal Scheduler & Mixed Control
**Goal:** Alternate BC and PPO control via configurable schedule, with rollback guardrails.

#### Step 5.3-S1 – Scheduler Implementation
- **Task 5.3-T1:** Extend training harness to support anneal schedule (BC ↔ PPO cycles).
- **Task 5.3-T2:** Implement rollout blending (percentage of BC control per cycle).
- **Task 5.3-T3:** Config schema updates (`training.anneal_schedule`).

**Status:** Completed — training harness `run_anneal` supports BC↔PPO schedules, config adds
`training.bc` + `training.anneal_schedule`/`anneal_accuracy_threshold`; see
`docs/training/ANNEAL_SCHEDULES.md` and regression `tests/test_training_anneal.py`.

#### Step 5.3-S2 – Guardrails & Rollback
- **Task 5.3-T4:** Define drift metrics (reward, policy divergence) to monitor during anneal.
- **Task 5.3-T5:** Implement rollback trigger (revert to last safe checkpoint on drift breach).
- **Task 5.3-T6:** Document ops playbook for anneal rollout (checklist, thresholds).

**Status:** Completed — BC accuracy threshold gating in `run_anneal` (configurable), results logged to
`anneal_results.json`; operational guidance captured in `docs/training/ANNEAL_SCHEDULES.md` (includes
rollback notes / thresholds).

**Phase 5.3 Risk Assessment**
| Risk ID | Description | Probability | Impact | Mitigation / Tasks | Trigger / Owner |
|---------|-------------|-------------|--------|--------------------|-----------------|
| 5.3-R1 | Anneal destabilises training (oscillation between BC/PPO). | Medium | High | Gradual schedule, monitor drift metrics, rollback trigger. | Drift metric breach | RL lead |
| 5.3-R2 | Rollback fails to restore safe state. | Low | High | Reuse snapshot system, test rollback in CI/nightly soak. | Rollback test failure | Ops lead |
| 5.3-R3 | Schedule config misapplied in production. | Medium | Medium | Provide CLI validation, document schedule examples. | Config validation error | DevEx |

**Risk Reduction Activities**
- Dry runs on staging environment before enabling anneal in production.
- Build automated anneal simulator to test schedules quickly.

### Phase 5.4 – End-to-End Validation & Ops Readiness
**Goal:** Package BC/anneal workflows with documentation, ops guides, and CI coverage.

- **Task 5.4-T1:** Create BC/anneal acceptance report (similar to Phase 4).
- **Task 5.4-T2:** Update ops handbook with BC dataset management, anneal procedures, rollback drill instructions.
- **Task 5.4-T3:** Extend CI: BC trainer unit tests, anneal schedule smoke test, dataset schema lint.
- **Task 5.4-T4:** Stakeholder go/no-go review (dataset owners, ops, RL).

**Status (2025-09-30 update):** Completed — acceptance smoke run (idle_v1) archived, ops playbooks updated, CI guardrails in place, and go/no-go decision recorded (see `docs/certificates/M5_BC_ANNEAL_ACCEPTANCE.md`).

### Phase 5.5 – Anneal Promotion Governance (In progress)
**Goal:** Surface anneal health in telemetry/ops tooling and prepare promotion controls.

- **Task 5.5.b-S1** (Telemetry pipeline) — ✅ `PPO_TELEMETRY_VERSION` bumped to 1.2; logs now emit `anneal_*` metrics (BC accuracy, thresholds, drift flags). Watcher/summary CLIs consume the new fields.
- **Task 5.5.b-S2** (Dashboard UX) — ✅ Observer UI adds an Anneal panel with BC gauges and drift alerts; guide updated.

**Phase 5.4 Risk Assessment**
| Risk ID | Description | Probability | Impact | Mitigation / Tasks | Trigger / Owner |
|---------|-------------|-------------|--------|--------------------|-----------------|
| 5.4-R1 | Dataset version drift between environments. | Medium | Medium | Checksums in CI, dataset version pin in configs. | Version mismatch | Ops lead |
| 5.4-R2 | CI runtime becomes excessive. | Medium | Medium | Parallelize BC tests, move long runs to nightly jobs. | CI > 25 min | QA |
| 5.4-R3 | Documentation lag (BC/anneal procedures unclear). | Low | High | Treat docs as acceptance criteria, ops rehearsal before go-live. | Ops feedback | Delivery lead |

## Risk Reduction Summary
- Synthetic dataset + mini BC trainer prototype (Phases 5.1/5.2) to de-risk convergence.
- Synthetic trajectory prototype (`tests/test_bc_capture_prototype.py`) validates capture schema round-trip.
- Scripted policy review brief (`docs/program_management/snapshots/M5_SCRIPTED_POLICY_BRIEF.md`) outlines behaviours/metrics for RL alignment before bulk capture.
- Automated anneal simulator & rollback rehearsal to de-risk scheduler (Phase 5.3).
- Anneal schedule harness (`run_anneal`) with accuracy threshold guard + logging; test coverage in `tests/test_training_anneal.py`.
- Dataset versioning with checksums + CI lint to prevent drift (Phase 5.4).
- Early stakeholder review of BC/anneal plan before full implementation.

## Artefact & Documentation Plan
- `docs/rollout/TRAJECTORY_CAPTURE.md` — capture schema/guidelines (Phase 5.1).
- `docs/training/BC_TRAINING_GUIDE.md` — BC trainer usage, evaluation metrics (Phase 5.2).
- `docs/training/ANNEAL_SCHEDULES.md` — schedule configs, rollback triggers, ops checklists (Phase 5.3/5.4).
- `docs/program_management/M5_BEHAVIOUR_CLONING_EXECUTION.md` — execution log (this doc).

## Exit Criteria
- BC dataset catalogue published with quality metrics and reproducible curation pipeline.
- BC trainer achieves ≥90% accuracy on curated scenarios; evaluation harness + CI coverage.
- Anneal schedule configurable via training config; rollback guard tested and documented.
- Ops handbook updated; acceptance report (Phase 5.4) signed off.
