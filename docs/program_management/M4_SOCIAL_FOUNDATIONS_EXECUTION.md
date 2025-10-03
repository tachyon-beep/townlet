# Milestone M4 — Social Foundations Execution Plan

This document tracks end-to-end delivery of **Milestone M4 – Social Foundations** as defined in the Townlet roadmap. It decomposes the milestone into phases, steps, and executable tasks, and records baseline risk assessments per phase.

- **Milestone Goal:** Persist relationship state, expose social context in observations/telemetry, introduce Phase C1 social rewards, and guard narration volume per the conceptual design snapshots (`docs/program_management/snapshots/CONCEPTUAL_DESIGN.md`).
- **Exit Criteria:**
  - Social ties (trust/familiarity/rivalry) persist through snapshots and influence observations, rewards, and telemetry.
  - Observer UI surfaces social overlays fed by new telemetry.
  - Chat reward taps (Phase C1) operate under guardrails with regression coverage.
  - Narration throttle and dedupe prevent spam while preserving key story beats.
  - QA and ops artefacts updated; CI enforces new acceptance checks.

Each phase below lists numbered steps (S) and tasks (T). Acceptance criteria include required tests and documentation updates. Risk assessments appear immediately after the task list for that phase.

## Phase 4.1 – Relationship Systems

**Phase Objective:** Implement the persistent relationship lattice with decay, eviction, and personality hooks.

### Step 4.1-S1 – Relationship Store Foundations
- **Task 4.1-T1:** Implement capped per-agent tie storage (`trust`, `familiarity`, `rivalry`) with clamp-to-[-1,1] and configurable capacity (default 6).
  - *Acceptance:* Unit tests cover insert/update/eviction, clamp behaviour, and weakest-tie replacement.
- **Task 4.1-T2:** Integrate personality modifiers (`extroversion`, `forgiveness`, `ambition`) into relationship delta application.
  - *Acceptance:* Property tests confirm modifiers respect design multipliers; documentation snippet added to `docs/world/RELATIONSHIP_MODEL.md`.

### Step 4.1-S2 – Event Wiring & Persistence
- **Task 4.1-T3:** Wire event-driven deltas (chat success/failure, queue actions, shared meals, work conflicts) into the relationship manager.
  - *Acceptance:* Integration test simulating scripted events verifies expected tie deltas; telemetry reflects applied updates.
- **Task 4.1-T4:** Persist relationships through snapshot save/load and seed initial ties via config flag.
  - *Acceptance:* Snapshot round-trip test validates deterministic restoration; configuration schema updated; release notes in `docs/ops/CHANGELOG.md`.

#### Phase 4.1 Risk Assessment
| Risk ID | Description | Probability | Impact | Mitigation / Tasks | Trigger / Owner |
|---------|-------------|-------------|--------|--------------------|-----------------|
| 4.1-R1 | Relationship eviction logic causes churn, destabilising trust metrics. | Medium | High | Add soak test tracking tie churn; expose debug telemetry for evictions (Task 4.1-T3 follow-up). | Eviction rate > 20% per sim day triggers review / Systems lead |
| 4.1-R2 | Snapshot persistence misses new relationship fields leading to data loss. | Low | High | Extend snapshot schema tests; add schema version bump and backward-compat check (Task 4.1-T4). | QA detects mismatch or CI snapshot test failure / Storage owner |
| 4.1-R3 | Personality multipliers introduce instability in reward shaping. | Medium | Medium | Gate multipliers behind `features.relationship_modifiers`; include toggle tests verifying baseline parity. | KPI drift in soak run >10% vs control / RL lead |

##### Mitigation Notes (2025-09-29)
- Introduced `RelationshipChurnAccumulator` telemetry helper (`src/townlet/telemetry/relationship_metrics.py`) and coverage in `tests/test_relationship_metrics.py` to quantify eviction churn and feed soak harness dashboards.
- `TelemetryPublisher.latest_relationship_metrics()` now exposes relationship payloads, enabling ops tooling to monitor eviction spikes during Phase 4.1 development.
- Snapshot schema now persists relationship ledgers with schema bump + guard rails (`src/townlet/snapshots/state.py`, `tests/test_snapshot_manager.py`), preventing silent data loss during save/load.
- Snapshot schema now encodes trust/familiarity/rivalry tuples (schema v1.1) so personality-aware deltas round-trip correctly across persistence.
- Simulation loop integrates the snapshot helpers, persisting agent/object state so runs can resume without divergence (`src/townlet/core/sim_loop.py`, `tests/test_sim_loop_snapshot.py`).
- Snapshot schema v1.2 now captures queue manager, embedding allocator, employment queues, lifecycle counters, and RNG state to keep resumed runs deterministic (`src/townlet/snapshots/state.py`, `tests/test_snapshot_manager.py`).
- Observer telemetry schema bumped to 0.6.0 with relationship snapshots + delta stream; dashboard renders the change log (`src/townlet/telemetry/publisher.py`, `src/townlet_ui/telemetry.py`, `docs/telemetry/TELEMETRY_CHANGELOG.md`).
- Telemetry caches and console buffers persist across snapshots, and policy runtime/perturbation state resets prevent duplicate transitions on resume (`src/townlet/telemetry/publisher.py`, `src/townlet/core/sim_loop.py`).
- Personality multipliers gated behind `features.relationship_modifiers` with parity/behaviour tests (`src/townlet/config/loader.py`, `src/townlet/agents/relationship_modifiers.py`, `tests/test_relationship_personality_modifiers.py`).
- Rivalry-ledger evictions now feed churn metrics directly via `WorldState.relationship_metrics_snapshot()` (`src/townlet/world/grid.py`, `src/townlet/world/rivalry.py`, `tests/test_relationship_metrics.py`).
- Relationship ledger scaffolding and update APIs landed (`src/townlet/world/relationships.py`, `src/townlet/world/grid.py`, `tests/test_relationship_ledger.py`), enabling symmetric trust/familiarity/rivalry storage and observation wiring.
- Queue events now drive ledger deltas: ghost-step conflicts raise rivalry while polite handovers boost trust/familiarity (`src/townlet/world/grid.py`, `tests/test_relationship_metrics.py::test_queue_events_modify_relationships`).
- Shared meals and employment shift dynamics are wired into relationship deltas (`shared_meal`, `took_my_shift`, `helped_when_late`) with regression coverage (`src/townlet/world/grid.py`, `tests/test_relationship_metrics.py`).
- Chat outcomes are exposed via `record_chat_success`/`record_chat_failure` to support Phase 4.3 social reward hooks, with tests covering ledger effects (`src/townlet/world/grid.py`, `tests/test_relationship_metrics.py::test_chat_outcomes_adjust_relationships`).
- Relationship modifiers now flow through the world ledger so extroversion/forgiveness/ambition adjust deltas when the feature flag is enabled (`src/townlet/world/grid.py`, `tests/test_relationship_integration.py`).
- Shared meal and employment events now tag relationship updates with explicit event codes, preparing downstream reward hooks and analytics (`src/townlet/world/grid.py`).

## Phase 4.2 – Social Observations & Telemetry

**Phase Objective:** Surface relationship context within agent observations and telemetry streams.

### Step 4.2-S1 – Observation Surface
- **Task 4.2-T1:** Extend observation builder with top-K social snippet tensors (id embeddings + trust/fam/riv) and local rivalry/trust aggregates.
  - *Acceptance:* Tensor layout documented; unit test verifies shape/content; golden fixture added under `tests/data/observations/social_snippet.npz`.
- **Task 4.2-T2:** Update config gating (`observations.variant`) to fail fast if social snippet unsupported by policy hash.
  - *Acceptance:* Config loader raises `NotImplementedError`; regression test asserts failure path.

### Step 4.2-S2 – Telemetry & UI Hooks
- **Task 4.2-T3:** Publish relationship snapshots and delta events through telemetry stream, version bumping schema.
  - *Acceptance:* `telemetry_version` incremented; validator updated; docs in `docs/telemetry/RELATIONSHIP_FEED.md`.
- **Task 4.2-T4:** Coordinate with Observer UI work package to consume new telemetry; add contract tests to UI client stub.
  - *Acceptance:* Mock UI test ensures overlay renders sample payload; API reference updated.

**Prep Notes:** see `M4_PHASE4_2_PREP.md` for snippet layout, profiling targets, and open questions logged prior to implementation.

##### Progress Notes (2025-09-29)
- Observation config now exposes `social_snippet` controls and the hybrid builder emits structured tie vectors with rivalry fallbacks (`src/townlet/config/loader.py`, `src/townlet/observations/builder.py`).
- Regression coverage added for snippet gating and vector sizing (`tests/test_observations_social_snippet.py`).
- Added profiling helper `scripts/profile_observation_tensor.py` and captured baseline dimensions for `configs/examples/poc_hybrid.yaml` (feature_dim 68, map 4×11×11, trust aggregates 0.0 pending richer events).
- PPO telemetry now reports social interaction metrics (shared meals, late-help assists, shift takeovers, chat success/failure quality) and watcher/summary tooling exposes thresholds for them (`src/townlet/policy/runner.py`, `scripts/telemetry_watch.py`, `scripts/telemetry_summary.py`).
- Mixed-soak benchmarks captured for queue_conflict, employment_punctuality (incl. extended runs), rivalry_decay, kitchen_breakfast, and observation_baseline; social counters currently surface only in employment punctuality (`late_help_events ≈ 1`). Results and thresholds recorded in `docs/ops/queue_conflict_baselines.md` with artefacts under `artifacts/phase4/*/`.
- Observer dashboard (`scripts/observer_ui.py`) now renders relationship churn (window, evictions, top owners/reasons) via telemetry snapshot support (`src/townlet/console/handlers.py`, `src/townlet_ui/telemetry.py`, `src/townlet_ui/dashboard.py`).

#### Phase 4.2 Risk Assessment
| Risk ID | Description | Probability | Impact | Mitigation / Tasks | Trigger / Owner |
|---------|-------------|-------------|--------|--------------------|-----------------|
| 4.2-R1 | Observation tensor size causes PPO instability or latency. | Medium | High | Profile tensor size; add config to limit top-K; run PPO smoke with new snippet (Task 4.3-T3 dependency). | PPO step time increases >15% | RL lead |
| 4.2-R2 | Telemetry consumers break due to schema bump. | Low | High | Announce schema change; provide migration guide; stage deploy with dual-publish flag. | Observer UI fails contract tests | Observability lead |
| 4.2-R3 | Embedding ID reuse leaks stale relationships into telem/obs. | Medium | Medium | Enforce ID cooldown logic; add telemetry assertions for reused IDs. | Reused ID detected within cooldown window | Simulation lead |

## Phase 4.3 – Social Rewards & Policy Hooks

**Phase Objective:** Introduce Phase C1 chat rewards with robust guardrails and training validation.

### Step 4.3-S1 – Reward Engine Enhancements
- **Task 4.3-T1:** Implement Phase C1 reward formula (`chat_base`, `coeff_trust`, `coeff_fam`) with clamp and need override guards.
  - *Acceptance:* Unit tests cover reward computation across trust/fam bounds and need override scenarios.
- **Task 4.3-T2:** Extend reward guardrails to block positive rewards within the configured termination window and ensure social rewards respect global clip.
  - *Acceptance:* Regression test using scripted eviction verifies guardrail enforcement; documentation in `docs/policy/REWARD_ENGINE.md`.

**Status:** Completed — RewardEngine consumes chat success events, applies the Phase C1 formula,
respects the need override, and enforces the termination window guardrail. Regression coverage lives
in `tests/test_reward_engine.py` and `tests/test_relationship_metrics.py`.

### Step 4.3-S2 – Training Validation & Scheduling
- **Task 4.3-T3:** Run PPO smoke + drift suite on social scenarios (baseline vs new rewards) with golden metrics.
  - *Acceptance:* New metrics stored under `tests/golden/ppo_social/`; CI check ensures metric drift within tolerance.
- **Task 4.3-T4:** Add config schedule toggling Phase C1 rewards (feature flag, schedule hook) and document rollout procedure.
  - *Acceptance:* Ops checklist updated; automation script `scripts/manage_phase_c.py` created; training harness respects flag.

**Status:** Completed — deterministic social PPO regression added in
`tests/test_training_replay.py::test_ppo_social_chat_drift` with golden metrics under
`tests/golden/ppo_social/baseline.json`. Training configs now expose
`training.social_reward_stage_override` / `training.social_reward_schedule`, applied by the harness, and
the new `scripts/manage_phase_c.py` helper plus OPS handbook guidance document the rollout procedure.

#### Phase 4.3 Risk Assessment
| Risk ID | Description | Probability | Impact | Mitigation / Tasks | Trigger / Owner |
|---------|-------------|-------------|--------|--------------------|-----------------|
| 4.3-R1 | Social rewards create runaway positive feedback loops in training. | Medium | High | Monitor PPO drift metrics; implement early stopping if variance spikes (Task 4.3-T3). | Reward variance > 2× baseline | RL lead |
| 4.3-R2 | Feature flag rollout misconfigured causing production regressions. | Low | High | Document staged rollout; add dry-run CLI validating flag state before enablement. | Flag enabled without soak approval | Ops lead |
| 4.3-R3 | Guardrail conflicts with existing reward clipping. | Medium | Medium | Add combined tests; review reward aggregation order in code. | CI test `test_reward_guardrails` fails | Policy engineer |

## Phase 4.4 – Narration & Experience Controls

**Phase Objective:** Regulate narration output and align Observer UI overlays with new social signals.

### Step 4.4-S1 – Narration Control Logic
- **Task 4.4-T1:** Implement narration rate limiter (per category + global cooldown) with dedupe of repeated events.
  - *Acceptance:* Unit tests simulate burst narrations; verify throttling behaviour; configuration documented.
- **Task 4.4-T2:** Add priority tagging so critical events bypass limiter within configured allowance.
  - *Acceptance:* Integration test ensures queue conflict arguments still surface; telemetry flags priority.

**Status:** Completed — `NarrationRateLimiter` enforces global/category cooldowns, dedupe, and window caps,
with priority bypass for ghost-step conflicts. Telemetry snapshots now include narration state and per-tick
entries, driven by configurable `telemetry.narration` settings. Coverage lives in
`tests/test_telemetry_narration.py`, and the telemetry changelog documents schema 0.7.0.

### Step 4.4-S2 – Experience Integration
- **Task 4.4-T3:** Extend Observer UI backlog tasks to overlay relationship status/narration context; align API contracts.
  - *Acceptance:* Updated user stories in Observer UI work package; shared design snapshot appended.
- **Task 4.4-T4:** Update ops handbook with narration troubleshooting and response runbook.
  - *Acceptance:* `docs/ops/OPS_HANDBOOK.md` includes new section; training material refreshed.

**Status:** Completed — Observer dashboard now renders a Narrations panel (priority conflicts highlighted),
`TelemetryClient` parses schema 0.7 payloads with narration entries/state, and the ops handbook documents
throttle tuning plus troubleshooting steps.

#### Phase 4.4 Risk Assessment
| Risk ID | Description | Probability | Impact | Mitigation / Tasks | Trigger / Owner |
|---------|-------------|-------------|--------|--------------------|-----------------|
| 4.4-R1 | Over-throttling hides critical narration cues. | Medium | Medium | Implement priority bypass and ops tuning guide (Task 4.4-T2/T4). | Ops reports missed critical events | Experience lead |
| 4.4-R2 | UI backlog dependency delays milestone exit. | Medium | High | Align sprint planning; provide mock payloads early (Task 4.2-T4). | UI tasks slip two sprints | Delivery lead |
| 4.4-R3 | Telemetry watcher thresholds misaligned with new narration volume. | Low | Medium | Update watcher defaults; add CI test to assert thresholds. | Watcher alerts spike post rollout | Observability lead |

Mitigation outcome: R1 addressed via priority bypass + ops guidance; R2 mitigated with delivered dashboard overlays; R3 covered by updated watcher thresholds and narration tests.

## Phase 4.5 – QA, Ops, and Risk Controls

**Phase Objective:** Finalise validation, documentation, and governance to close Milestone M4.

### Step 4.5-S1 – Risk & Governance
- **Task 4.5-T1:** Re-baseline risk register entries for milestone and parent work packages; document mitigations executed.
  - *Acceptance:* `docs/program_management/MASTER_PLAN_PROGRESS.md` updated with risk status.
- **Task 4.5-T2:** Schedule stakeholder go/no-go review with artefact summary (training metrics, UI demo, ops checklist).
  - *Acceptance:* Meeting notes stored under `docs/program_management/snapshots/`; decision logged.

**Status:** Completed — Master plan tracker refreshed (2025-09-30) with updated risks/decision points; go/no-go
prep bundle logged in `docs/program_management/snapshots/M4_GO_NO_GO_PREP.md` plus invite/checklist snapshots;
decision recorded in `M4_GO_NO_GO_DECISION.md` with follow-up action items.

### Step 4.5-S2 – Quality Gates & Reporting
- **Task 4.5-T3:** Extend CI to run social scenario suite, telemetry validator, and narration throttle tests.
  - *Acceptance:* `.github/workflows/ci.yml` updated; dry-run executed; badges reflect new checks.
- **Task 4.5-T4:** Compile acceptance report and update `MASTER_PLAN_PROGRESS.md` to mark M4 complete.
  - *Acceptance:* `docs/rollout/M4_SOCIAL_FOUNDATIONS_ACCEPTANCE.md` created with metrics, tests run, and artefacts.

**Status:** Completed — CI workflow updated with social telemetry/UI test step (local runtime <1 s) and
artefact upload retained; acceptance report refreshed (`docs/rollout/ROLLOUT_PHASE4_ACCEPTANCE.md`) capturing
schema 0.7.0, social rewards, narration work; master plan progress lists M4 as closed.

#### Phase 4.5 Risk Assessment
| Risk ID | Description | Probability | Impact | Mitigation / Tasks | Trigger / Owner |
|---------|-------------|-------------|--------|--------------------|-----------------|
| 4.5-R1 | CI pipeline duration exceeds acceptable window after adding tests. | Medium | Medium | Parallelise social suites; mark long tests `@pytest.mark.slow`; add nightly job for extended soak. | CI runtime > 20 min | QA owner |
| 4.5-R2 | Stakeholder review uncovers unmet acceptance criteria late. | Medium | High | Share interim demos; maintain checklist in acceptance report (Task 4.5-T2/T4). | Review feedback requests major changes | Delivery lead |
| 4.5-R3 | Documentation lag leaves ops unprepared for rollout. | Low | High | Enforce doc updates as task acceptance; include docs in CI lint (Task 4.5-T3). | Ops rejects go-live due to missing docs | Doc steward |

---

**Change Log**
- 2025-09-29: Initial execution plan drafted.
- 2025-09-29: Risk mitigation 4.1-R1 instrumentation scaffolding added (relationship churn telemetry + publisher hook).
- 2025-09-29: Risk mitigation 4.1-R2 snapshot schema implemented with round-trip tests.
- 2025-09-29: Risk mitigation 4.1-R3 feature flag + personality modifier parity suite added.
