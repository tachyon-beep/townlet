# Implementation Notes

## 2025-10-22 — Observation Variant Parity & Tooling
- `ObservationBuilder` now emits full/compact variants using shared feature
  initialisation and enriches metadata with `map_shape`, channel listings, and a
  `social_context` block that records configured slot counts, filled slots, and
  whether relationships or rivalry fallbacks supplied the data. Unsupported
  variants raise a clear error instead of returning dummy tensors.
- CLI tooling was updated to preserve and surface the richer metadata:
  `scripts/capture_scripted.py` stores the original observation metadata in each
  replay frame, `scripts/run_replay.py` renders variant/map/social context when
  inspecting samples, and `scripts/profile_observation_tensor.py` summarises
  social slot usage across ticks. Replay datasets should be regenerated to pick
  up the schema bump.
- Social snippet fixtures were consolidated under `tests/helpers/social.py` so
  observation tests seed relationship ledgers consistently. New assertions lock
  the metadata contract for hybrid/full/compact variants and ensure the golden
  social sample still matches the ADR spec.
- Reward engine and telemetry now track social interactions: chat failures incur
  penalties, rivalry avoidance pays a configurable bonus, and telemetry exports
  `social_events` plus a `relationship_summary` (top friends/rivals with churn
  metrics). Dashboards should be refreshed to visualise the new fields.

## 2025-10-19 — Needs & Affordance Effects Alignment
- `AgentSnapshot` now clamps and backfills core needs (`hunger`, `hygiene`, `energy`) so
  affordance effects always apply within [0, 1].
- Added regression tests for need decay, lifecycle thresholds, and affordance success/failure
  flows (`tests/test_need_decay.py`, `tests/test_world_queue_integration.py`).
- `eat_meal` harness coverage now asserts hunger/energy gains and wallet deductions while failed
  releases keep needs untouched.

## 2025-10-19 — Home Routing & Nightly Reset
- Agents persist a `home_position`; console spawn and respawn paths hydrate it for nightly routing.
- `WorldState.apply_nightly_reset` returns agents home, tops up needs, clears employment flags, and
  emits an `agent_nightly_reset` event (`src/townlet/world/grid.py`).
- Simulation loop triggers the reset based on observation day length; regression tests cover direct
  world invocation and the loop integration (`tests/test_world_nightly_reset.py`).

## 2025-10-21 — Affordance Hook Hardening
- Configuration now exposes `affordances.runtime.hook_allowlist` and
  `allow_env_hooks` to control which modules register affordance hooks. The
  default allowlist contains only `townlet.world.hooks.default` for safe
  startup.
- `WorldState` validates requested modules against the allowlist, optionally
  appending environment overrides when enabled, and records accepted/rejected
  modules for observability. Rejections emit structured log warnings with the
  failure reason (not in allowlist, import error, missing `register_hooks`, etc.).
- `townlet.world.hooks.load_modules` now guards against import/registration
  failures so a bad module cannot partially register and crash later. It returns
  detailed results used by telemetry/logs.
- Example configs updated to illustrate the new allowlist, and tests cover
  allowlisted modules, env gating, and rejection paths
  (`tests/test_affordance_hook_security.py`). Operators must migrate any
  environment-managed hook modules into the allowlist before upgrading.

## 2025-09-30 — Affordance Manifest Hardening
- Replaced ad-hoc YAML parsing with `load_affordance_manifest` helper that validates ids, preconditions/hook structure, numeric fields, and emits SHA-256 checksums for auditing.
- `WorldState` now records manifest metadata (`path`, `checksum`, counts) and exposes it via `affordance_manifest_metadata()` so telemetry and console surfaces report the active manifest.
- Added CLI `scripts/validate_affordances.py` to lint manifests locally/CI (`--strict` enforces discovery); outputs checksum + entry counts for observability.
- Telemetry publisher exports `latest_affordance_manifest()` and console snapshots include manifest summary to unblock ops validation prior to go-live.
- Pytest coverage: `tests/test_affordance_manifest.py` for loader edge cases and `tests/test_cli_validate_affordances.py` for CLI recursion/error handling.
- Affordance hooks now load via plug-in modules (`townlet.world.hooks`). Set `TOWNLET_AFFORDANCE_HOOK_MODULES="your.module,another.module"` to auto-register project-specific hooks without modifying `WorldState`.

## 2025-09-24 — Queue & Affordance Integration
- Added `QueueManager`-driven affordance execution in `WorldState`; actions now request/start/release objects and ghost-step failures clear running affordances.
- Introduced lightweight `AffordanceSpec` and `InteractiveObject` tracking for tests; effects apply to agent needs and wallet when duration completes.
- Telemetry already captures queue + embedding metrics; stability monitor now consumes embedding warnings.
- Next: flesh out affordance registry loading from YAML and propagate object/affordance hooks to console + telemetry observers.

## 2025-09-24 — Affordance YAML Loader
- `SimulationConfig` now points at `affordances.affordances_file`; `WorldState` loads specs on init via embedded YAML reader.
- Tests updated to confirm default `use_shower` affordance exists and to override effects for deterministic assertions.
- Affordance YAML now supports object definitions (`type: object`), automatically registering interactive objects.
- Remaining work: extend schema with queue node positions and wire hook events into telemetry.

## 2025-09-24 — Affordance Events & Telemetry
- World emits `affordance_start` / `affordance_finish` / `affordance_fail` events when reservations change state.
- Telemetry publisher captures the event batch each tick; stability monitor can inspect them via `latest_events`.
- Event stream subscriber added for console/ops surfaces so handlers can poll latest events.
- Stability monitor now raises `affordance_failures_exceeded` when event count exceeds `stability.affordance_fail_threshold`.
- Next: expose streaming over CLI and log event-derived alerts in ops handbook.

## 2025-09-24 — Needs Loop & Reward Engine
- Added per-tick need decay driven by `rewards.decay_rates`, applied after affordance resolution.
- Replaced reward stub with homeostasis + survival tick, including clip enforcement and termination guard.
- Lifecycle manager now terminates agents when hunger collapses, enabling M0 exit checks.
- Tests cover decay, reward maths, and stability alerts for affordance failures.
- Introduced basic economy parameters (`economy.*`), deducting meal costs and fridge stock on `eat_meal` affordances.
- Job scheduler assigns agents round-robin across `jobs.*`, tracks shift windows, applies wage income, and enforces location-based punctuality with lateness penalties/events.
- Telemetry now emits job snapshots and stability raises `lateness_spike` when lateness exceeds `stability.lateness_threshold`.
- Expanded economy loop: fridge/stove stock management, meal purchasing/cooking costs, and wage counters in job snapshots.
- Observer payload now carries job/economy snapshots for planning; tests ensure schema stability (including basket costs).
- Console router exposes `telemetry_snapshot` so ops agents can fetch job/economy payloads.
- Behavior controller scaffold (`ScriptedBehavior`) chooses intents with move/request/start primitives; thresholds configurable via `behavior.*`.
- Added `rest_sleep` affordance and scripted pathing to beds so energy recovery works alongside cooking/eating loops; restocks emit telemetry events.
- Introduced behavior configuration scaffold (`behavior.*`) and restock hooks as foundation for scripted decision logic.

## 2025-09-24 — Employment Loop Design Artifacts (Draft)
- Authored `docs/design/EMPLOYMENT_ATTENDANCE_BRIEF.md` outlining shift state machine, wage gating, telemetry fields, and validation plan.
- Created `docs/design/EMPLOYMENT_EXIT_CAP_MATRIX.md` recommending hybrid per-agent + daily exit caps with console review workflow.
- Awaiting approvals from architecture, product, and ops leads before implementation; risk register items R1/R4 remain open until sign-off.

## 2025-09-25 — Employment Loop Hardening (Phase 1)
- Added `employment.*` config node with grace/absence tuning, exit caps, queue limits, and enforcement flag.
- Implemented world-level shift state machine (on-time/late/absent), wage gating, lateness/absence penalties, and telemetry fields (`shift_state`, `attendance_ratio`, `late_ticks_today`, `wages_withheld`, `exit_pending`).
- Lifecycle now manages hybrid unemployment exit queue (per-agent absence threshold + daily cap) with manual approvals, review window auto-releases, and telemetry events.
- Telemetry publisher exposes employment metrics; stability monitor raises `employment_exit_backlog` / `employment_exit_queue_overflow` alerts; console adds `employment_status` + `employment_exit` commands for ops overrides.
- Design approvals: architecture + product sign-off captured in design briefs (ops N/A).
- New pytest coverage: `tests/test_employment_loop.py` (attendance) and console command regressions.
- Risk R2 smoke validation: `python scripts/run_employment_smoke.py configs/examples/poc_hybrid.yaml --ticks 1000` with and without `--enforce-job-loop` recorded zero alerts/pending exits; metrics captured in `employment_smoke_metrics.json`.
- Telemetry schema bumped to `0.2.0`; console snapshots now include `schema_version`, employment snapshots versioned; updated docs and tests to lock consumer expectations.
- Added telemetry consumer tooling: `scripts/telemetry_check.py` validator, sample payload `docs/samples/telemetry_snapshot_0.2.0.json`, and schema change log (`docs/telemetry/TELEMETRY_CHANGELOG.md`).
- Console router now emits schema compatibility warnings when shards report newer versions; tests cover warning copy.
- Console dry run executed (`scripts/console_dry_run.py`); validated employment commands and documented procedure in `docs/guides/CONSOLE_DRY_RUN.md`.
- Added employment docs/tests checklist (`docs/EMPLOYMENT_DOCS_TEST_CHECKLIST.md`) and referenced in Ops handbook to institutionalise doc + test updates (addresses Risk R6).
- Benchmarked tick duration with and without employment enforcement (`scripts/benchmark_tick.py`); 1,000-tick runs averaged 4–5µs per tick with <25% delta, within guardrail for R7.
- Implemented hybrid observation tensor encoding (map + feature vector) per `docs/design/OBSERVATION_TENSOR_SPEC.md`; added tests and local view helper.
- Added telemetry client library & console dashboard (`townlet_ui.telemetry`, `townlet_ui.dashboard`); new CLI `scripts/observer_ui.py` renders employment KPIs, map preview, and supports approve/defer overrides.
- Drafted observation tensor spec (`docs/design/OBSERVATION_TENSOR_SPEC.md`) outlining hybrid feature layout, pending approvals.

- Observer UI usability dry run recorded (`docs/samples/observer_ui_output.txt`); feedback logged in `docs/OBSERVER_UI_FEEDBACK.md` (requests map legend, highlights).
- Dashboard performance probe: baseline tick 5µs vs 200-tick run with dashboard 0.63s total (~3.2ms/tick).
- Added asynchronous console command executor (`townlet_ui.commands.ConsoleCommandExecutor`) to future-proof approve/defer interactions; tests cover error handling.
- Dashboard UX refinements: employment backlog badge, on-shift highlighting, tick timestamps, optional coordinate labels, and `--focus-agent` flag; concurrency executor now logs failures.

## 2025-09-26 — Conflict Telemetry & Observation Signals
- Rivalry ledger extended with intensity knobs (`ghost_step_boost`, `handover_boost`, `queue_length_boost`) and slower decay to tune conflict growth.
- `WorldState._record_queue_conflict` now emits `queue_conflict` events for ghost steps/handovers, updates rivalry ledgers, and clamps intensity.
- Hybrid observation tensors gained `rivalry_max` / `rivalry_avoid_count` features so training clients can read conflict pressure; sample refreshed in `docs/samples/observation_hybrid_sample.npz`.
- Added `scripts/run_replay.py` helper to inspect observation/telemetry samples; telemetry snapshot for conflict (`docs/samples/telemetry_conflict_snapshot.json`) captured.
- Updated telemetry schema log to 0.3.0, architecture guide, and observation spec to document new conflict signals.


## 2025-09-26 — Replay Dataset & Training Harness
- Added conflict-aware replay dataset configuration (`ReplayDatasetConfig`) with manifest parsing, batching, and shape validation.
- Training harness now supports `run_replay_dataset` and CLI options (`--replay-manifest`, batching knobs) for conflict-aware batch playback.
- Replay utilities enforce rivalry feature presence and expose per-batch rivalry stats; schema guard tests added.
- Introduced `docs/samples/replay_manifest.json` and streaming iterator support for replay datasets; CLI `--replay-manifest` path exercises batching/shuffle/drop-last combos.
- PPO stub integrated with replay dataloader: `TrainingHarness.run_ppo` iterates batches, logs loss/rivalry stats, and CLI exposes `--train-ppo`. Added `ppo` config scaffold and conflict-aware Torch network placeholder (requires torch install).

## 2025-09-26 — PPO Integration Plan
- Plan drafted for conflict-aware PPO evolution: Torch network, PPO loss pipeline, telemetry hooks.
- Execution underway (Phase 1).

## 2025-09-26 — PPO Torch Scaffolding
- Added `PPOConfig` schema, replay manifest batching, torch policy placeholder, and CLI hooks (`--train-ppo`, JSONL logging).
- Tests cover torch availability guard and forward pass when torch installed.
- Next: wire real PPO loss/optimizer with telemetry NDJSON and integrate live rollouts.

## 2025-09-27 — Replay Training Schema & PPO Overrides
- Replay samples now encode training-critical arrays (`actions`, `old_log_probs`, `value_preds`, `rewards`, `dones`) alongside maps/features; loader enforces presence and homogeneous shapes.
- `ReplayBatch` exposes stacked training arrays so GAE/PPO losses can consume offline data without ad-hoc synthesis; tests cover schema guards and streaming/manifest loading.
- CLI supports PPO hyperparameter overrides (`scripts/run_training.py --ppo-*` flags) while keeping YAML defaults authoritative—overrides materialise a `PPOConfig` when absent.
- Added tests for override plumbing to guarantee flags stay in sync with config schema.

## 2025-09-27 — PPO Loss & Optimizer Integration (Phase 2)
- Implemented torch-based PPO loop: GAE computation, advantage normalisation, clipped policy/value losses, entropy bonus, and gradient clipping now drive optimisation in `TrainingHarness.run_ppo`.
- Added `townlet.policy.ppo.utils` with reusable helpers (`compute_gae`, `policy_surrogate`, `clipped_value_loss`, etc.) and unit coverage to guard loss math.
- Training harness builds a policy network from replay metadata, derives action space from samples, and logs per-epoch metrics (loss components, clip fraction, advantage stats, grad norms, conflict telemetry averages) with NDJSON `telemetry_version` 1 entries including `kl_divergence` and baseline comparisons. Use `--ppo-log-frequency` / `--ppo-log-max-entries` to manage log volume; `scripts/ppo_telemetry_plot.py` provides a quick-look plotter for JSONL output. `TrainingHarness.capture_rollout` + `RolloutBuffer` scaffolding capture trajectories ahead of Phase 4 live integration, sharing the same manifest/metrics format as `capture_rollout.py` and now returning an in-memory dataset so PPO can consume captured rollouts without temporary files.
- Replay samples/documentation refreshed; canonical NPZ manifests include bootstrap value predictions for GAE, multi-step sequences, and metadata tracks timestep alignment.

- `PolicyRuntime` now buffers per-agent actions/rewards/done flags each tick and exposes `collect_trajectory` for downstream tooling; `SimulationLoop.step` flushes observations into this buffer automatically.
- Added `frames_to_replay_sample` helper to convert collected frames into replay-ready tensors (map/features stacked per timestep, action IDs + lookup, logged policy log-probs/value baselines) so multi-step rollouts feed the PPO harness without bespoke scripts.
- Tests cover trajectory capture → sample conversion (`tests/test_training_replay.py::test_policy_runtime_collects_frames`), ensuring schema guardrails hold for generated sequences.
- Scenario configs and capture suite automation (`configs/scenarios/*.yaml`, `scripts/capture_rollout_suite.py`) plus regression tests (`tests/test_rollout_capture.py`) compare generated samples against golden metrics (`docs/samples/rollout_scenario_stats.json`).

## 2025-09-27 — Rollout→PPO Prototype (Phase 4 pre-work)
- `TrainingHarness.run_rollout_ppo` captures a short rollout, builds an in-memory dataset, and feeds PPO in one shot; CLI mirrors this with `--rollout-ticks` + `--train-ppo` (+ optional `--rollout-auto-seed-agents`).
- Scenario helpers (`apply_scenario`, `ScenarioBehavior`) shared by CLI/harness guarantee consistent seeded behaviour; auto seeding is opt-in and emits a clear error when configs lack agents.
- `apply_scenario` now synthesises lightweight affordance stubs when schedules reference entries missing from the active manifest (duration defaults to the agent's job window or 30 ticks). The runtime logs each `scenario.affordance_stub` creation so scenario authors can migrate the affordance into a manifest when ready.
- Runtime inspection tooling: `scripts/inspect_affordances.py` surfaces the running set from either a snapshot (`--snapshot`) or live config (`--config`, `--ticks`) and supports `--json` output for automation.
- `RolloutBuffer.build_dataset` recomputes metrics when missing and carries aggregate baseline stats so telemetry comparisons still work.
- Regression coverage: `tests/test_training_replay.py::test_training_harness_run_rollout_ppo`, `tests/test_training_replay.py::test_training_harness_run_rollout_ppo_multiple_cycles`, `tests/test_training_replay.py::test_training_harness_rollout_capture_and_train_cycles`, and buffer tests ensure the new path remains stable over repeated capture→train cycles and alternating capture→train loops.
- Added guardrails for metrics edge cases: `tests/test_rollout_buffer.py::test_rollout_buffer_empty_build_dataset_raises` and `tests/test_rollout_buffer.py::test_rollout_buffer_single_timestep_metrics` validate error handling and baseline aggregation for empty and single-timestep captures.
- Telemetry schema coverage: `tests/test_training_replay.py::test_training_harness_ppo_conflict_telemetry` asserts PPO logs emit conflict aggregates (rivalry mean/max, avoid counts) with the expected NDJSON layout.
- Tooling: `scripts/validate_ppo_telemetry.py` checks NDJSON schema and reports per-epoch/aggregate drift (absolute + optional relative), `scripts/telemetry_watch.py` tails runs with alert thresholds (`kl`, `loss`, `grad`, `entropy`, `reward_adv_corr`, hygiene/rest counters) and can emit JSON for hooks, `scripts/telemetry_summary.py` generates text/markdown/JSON summaries (including utility/shower/sleep metrics), and `docs/notebooks/telemetry_quicklook.ipynb` offers quick-loss visualisation updated for telemetry_version 1.1 fields.
