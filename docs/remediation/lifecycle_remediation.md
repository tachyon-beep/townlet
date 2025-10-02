# Lifecycle Remediation Plan

## Milestone LR1 — Core Lifecycle Fidelity

### Phase LR1.1 — Spawn & Lifecycle Loop Audit - COMPLETE

- Step LR1.1.a — Map existing lifecycle transitions
  - Task: Document spawn → employment queue → affordance → decay → exit/death flow, noting gaps.
  - Task: Review `LifecycleManager` for respawn handling and pending TODOs.
- Step LR1.1.b — Implement missing lifecycle mechanics
  - Task: Add configurable respawn delay window and tests.
  - Task: Ensure employment exits trigger proper telemetry and state reset.
  - Task: Verify shelter/home routing and nightly reset of agent state.
    - Subtasks:
    1. Extend lifecycle plan so agents track a `home_position` at spawn/respawn. ✅
    2. Implement nightly reset routine that returns agents home and restores baseline state. ✅
    3. Emit telemetry/event for nightly resets and document operator workflow. ✅
    4. Add regression tests (spawn assigns home, nightly reset moves/refreshes agents). ✅

### Phase LR1.2 — Needs & Affordance Effects ✅

- Step LR1.2.a — Align need decay and thresholds
  - Task: Cross-check decay rates against reward design; add regression tests.
  - Task: Clamp need values at spawn and after affordances.
- Step LR1.2.b — Finish affordance effects
  - Task: Ensure manifest-driven needs and wallet deltas apply with clamping (complete via `_apply_affordance_effects`).
  - Task: Confirm hook-based social effects (e.g., shared meal trust/familiarity boosts) remain covered by tests (`tests/test_relationship_metrics.py::test_shared_meal_updates_relationship`).
  - Task: Document affordance DSL and success/failure coverage (`docs/design/AFFORDANCE_EFFECTS.md`, `tests/test_world_queue_integration.py`).

### Phase LR1.3 — Queue & Rivalry Integration ✅

- Step LR1.3.a — Queue fairness tuning
  - Task: Validate ghost-step/rotation logic under load; add metrics tests (see `tests/test_queue_metrics.py`).
  - Task: Update docs with fairness parameter rationale (`docs/ops/QUEUE_FAIRNESS_TUNING.md`).
- Step LR1.3.b — Rivalry lifecycle wiring
  - Task: Ensure rivalry events feed back into reward/telemetry loops (telemetry test added in `tests/test_telemetry_new_events.py`).
  - Task: Add rivalry regression scenarios for conflict-heavy cycles (`tests/test_conflict_scenarios.py::test_rivalry_decay_scenario_tracks_events`).

## Milestone LR2 — Reward & Observation Alignment

### Phase LR2.1 — Reward Shaping Completion

- Step LR2.1.a — Implement documented reward taps
  - Task: Add punctuality, wages, social bonuses, penalties; update tests. ✅ (tests/test_reward_engine.py)
  - Task: Hook reward guardrails (clip_per_tick/episode) with coverage. ✅ (tests/test_reward_engine.py)
  - Note: Existing coverage lives in `tests/test_reward_engine.py`; expand with terminal penalty, wage/guardrail regression cases.
  - Telemetry reference: `docs/telemetry/TELEMETRY_CHANGELOG.md` 0.9.3 entry and `docs/samples/telemetry_stream_sample.jsonl` refreshed for `terminal_penalty`. ✅
  - Task: Integrate terminal penalties (`faint_penalty`, `eviction_penalty`) into reward aggregation and telemetry breakdown; add regression coverage. ✅ (src/townlet/rewards/engine.py, docs/samples/telemetry_stream_sample.jsonl)
  - Task: Confirm wage/punctuality taps reuse employment context correctly and document assumptions to avoid double-counting with wallet deltas. ✅ (docs/policy/REWARD_ENGINE.md)
  - Task: Author reward model design notes (`docs/design/REWARD_MODEL.md`) capturing tap weights, guardrails, and failure semantics for ops/reference. ✅
- Step LR2.1.b — Reward validation tooling
  - Task: Extend reward summary script for ops to inspect components. ✅ (scripts/reward_summary.py, tests/test_reward_summary.py)
  - Task: Document reward breakdown expectations in design. ✅ (docs/design/REWARD_MODEL.md)

### Phase LR2.2 — Observation Consistency

- Step LR2.2.a — Validate tensor completeness
  - Task: Ensure needs, queue status, lifecycle flags present in observations. ✅ (tests/test_observation_builder.py)
  - Task: Add observation regression tests for spawn/death/respawn scenarios. ✅ (tests/test_observation_builder.py::test_observation_respawn_resets_features)
- Step LR2.2.b — Context reset handling
  - Task: Confirm `ctx_reset_flag` toggles on possession, teleport, death. ✅ (tests/test_observation_builder.py::test_ctx_reset_flag_on_teleport_and_possession)
  - Task: Document observation contract in QA checklist. ✅ (docs/testing/QA_CHECKLIST.md)

## Milestone LR3 — Promotion & Governance Automation

### Phase LR3.1 — Promotion Gate Automation (builds on Phase 7.1)

- Step LR3.1.a — Finalize automation hooks
  - Task: Integrate promotion metrics into CI/nightly reporting. ✅ (`.github/workflows/ci.yml`, `.github/workflows/anneal_rehearsal.yml`)
  - Task: Validate golden suite & anneal outputs feed promotion decisions. ✅ (`scripts/run_anneal_rehearsal.py`, promotion evaluate workflows)
- Step LR3.1.b — Policy swap/governance workflow
  - Task: Implement runtime policy swap command with safety checks. ✅ (`src/townlet/console/handlers.py`, `src/townlet/stability/promotion.py`, tests)
  - Task: Update ops runbook for promote/rollback flow. ✅ (`docs/ops/OPS_HANDBOOK.md`)

### Phase LR3.2 — Golden Rollout Suite

- Step LR3.2.a — Scenario catalog finalization
  - Task: Define golden scenarios, document expected metrics. ✅ (`docs/rollout/GOLDEN_SCENARIOS.md`)
  - Task: Add versioned manifest under `artifacts/m7/golden_runs/`. ✅ (`artifacts/m7/golden_runs/manifest.json`)
- Step LR3.2.b — Automation & diff tooling
  - Task: Enhance capture/diff scripts with policy/config metadata. ✅ (`scripts/capture_rollout.py`, `scripts/merge_rollout_metrics.py`, tests)
  - Task: Wire suite into CI with artifact retention. ✅ (`.github/workflows/ci.yml`)

### Phase LR3.3 — Governance Documents

- Step LR3.3.a — Draft data/privacy policy
  - Task: Produce privacy/data handling doc per documentation plan. ✅ (`docs/policy/DATA_PRIVACY_POLICY.md`)
  - Task: Review with stakeholders for sign-off. ✅ (approvals requested; see `docs/program_management/APPROVAL_LOG.md`).
- Step LR3.3.b — Capture outstanding approvals
  - Task: Record observer UI usability decision & audio toggle resolution. ✅ (`docs/program_management/APPROVAL_LOG.md`).
  - Task: Update master progress tracker with approvals and deferrals. ✅ (`docs/program_management/MASTER_PLAN_PROGRESS.md`).

## Milestone LR4 — Training Harness & UI Readiness

### Phase LR4.1 — RL Harness Stability

- Step LR4.1.a — PPO/BC pipeline hardening
  - Task: Validate advantage, GAE, logging, and error handling paths. ✅ (`src/townlet/policy/runner.py:889`–`1114`, `scripts/validate_ppo_telemetry.py:19`–`118`)
  - Task: Add unit tests covering rollout, replay, and anneal cycles. ✅ (`tests/test_training_replay.py`, `tests/test_training_anneal.py`, `tests/test_rollout_buffer.py`)
- Step LR4.1.b — Option commitment implementation
  - Task: Enforce 15-tick option lock per design; add tests. ✅ (`src/townlet/policy/runner.py:109`–`220`, `tests/test_policy_anneal_blend.py:1`–`132`, `tests/test_training_replay.py:839`–`909`)
  - Task: Document policy runner behavior in design notes. ✅ (`docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md:103`–`115`, `docs/telemetry/TELEMETRY_CHANGELOG.md:5`)

### Phase LR4.2 — Operator UI Enhancements

- Step LR4.2.a — Audio control support
  - Task: Implement dashboard audio toggle & config wiring.
  - Task: Update ops docs with audio workflow.
- Step LR4.2.b — Promotion visibility
  - Task: Ensure Promotion Gate panel surfaces gate status & reasons.
  - Task: Add observer usability checklist capturing promotion review steps.

## Work Package — Test Stabilisation & Golden Refresh (Post-LR1)

- **Phase TS.0 — Catalogue & Gate**
  - Task: Record every currently failing pytest target with intended behaviour vs. implementation status.
  - Task: Mark genuinely deferred scenarios with explicit skips so CI enforces the active scope only.
- **Phase TS.1 — Behaviour Parity**
  - Step TS.1.a — Rival avoidance in scripted behaviour (LR1.3 alignment).
    - Task: Ensure scripted queue decisions respect rivalry thresholds.
    - Task: Reinstate `tests/test_behavior_rivalry.py` expectations.
  - Step TS.1.b — Scripted capture policy surface.
    - Task: Mirror required `PolicyRuntime` APIs in the scripted adapter so capture CLI tests pass.
- **Phase TS.2 — Observation Fixtures (LR2.2 dependency)**
  - Task: Regenerate social snippet golden (`tests/data/observations/social_snippet_gold.npz`) with current builder.
  - Task: Document regeneration command path for future changes.
- **Phase TS.3 — Tooling & CLI Contract**
  - Task: Align promotion CLI flag expectations between `scripts/promotion_evaluate.py` and tests/docs.
  - Task: Update watcher/capture goldens only when runtime behaviour changes are signed off.
- **Phase TS.4 — CI Guardrails**
  - Task: Ensure standard pytest invocation uses `PYTHONPATH=src:.` and runs clean on the trimmed test set.
  - Task: Publish `docs/qa/TEST_STATUS.md` (or equivalent) so future work re-enables deferred tests intentionally.
