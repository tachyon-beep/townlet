# WP3 Pre-Compact Brief — 2025-10-10

Latest context snapshot so we can resume quickly after memory compaction.

## Current State
- Telemetry pipeline is fully event-driven; legacy writer APIs removed and
  guard tests protect the dispatcher surface (`tests/test_telemetry_surface_guard.py`).
- DTO schema v0.2.0 shipped:
  - `dto_observation_inventory.md` updated with the expanded per-agent/global fields.
  - `dto_example_tick.json` & `dto_sample_tick.json` regenerated under the new schema.
  - Converter (`build_observation_envelope`) now injects per-agent needs/wallet/inventory/job/personality/queue state and global employment/economy/anneal snapshots. Coverage in `tests/world/test_observation_dto_factory.py` ensures regressions fail fast.
  - `SimulationLoop` populates the richer envelope each tick (captures agent snapshots, employment metrics, economy snapshot, queue affinity metrics, anneal context).
- DTO parity harness (Stage 2) expanded: `tests/core/test_sim_loop_dto_parity.py` cross-checks DTO vs recorded legacy data (needs, wallet, jobs, queue metrics, economy snapshot, anneal context). Stage 0 baselines live under `docs/architecture_review/WP_NOTES/WP3/dto_parity/`.
- Modular system suite (WP3B) is done: `employment.step`, `economy.step`, and `relationships.step` execute each tick, `_apply_need_decay` only invokes employment/economy fallbacks when services are absent, and `affordances.step` no longer calls `state.resolve_affordances`. Targeted unit suites (`tests/world/test_systems_{affordances,queues,employment,economy,relationships}.py`) plus `pytest tests/world -q` hold the regression line.
- Stage 3A wiring landed: `SimulationLoop` now bootstraps DTO envelopes before policy decisions, logs whenever legacy observation batches are consumed, and pushes envelopes into the policy backend cache. `PolicyRuntime` tracks envelopes via `ObservationEnvelopeCache`, and `PolicyController` enforces DTO-aware adapters (raises if providers reject the envelope).
- Stage 3B completed: `DTOWorldView` exposes DTO agent snapshots/iterators, scripted behaviour decisions run entirely off DTO data (with fallback logging), and regression tests (`tests/policy/test_scripted_behavior_dto.py`) cover pending intent promotion, chat selection, and rivalry guardrails.
- Stage 3C progressing: `TrajectoryService.flush_transitions` accepts DTO envelopes (preserving map/features/anneal payloads), the training orchestrator captures DTO-backed rollouts (`tests/policy/test_trajectory_service_dto.py`, `tests/policy/test_training_orchestrator_capture.py`), and policy adapters/controller/runtime now operate DTO-only (legacy observation batches removed from the loop path).
- Stage 3C dataset enrichment: trajectory frames now inject DTO agent context (needs, wallet, job, queue state, pending intent) and schema metadata so replay exports (`frames_to_replay_sample`) preserve anneal context and DTO provenance without altering tensor shapes.
- DTO export bridge: `RolloutBuffer` emits DTO-native JSON artefacts next to legacy `.npz` captures, updating manifests so external consumers can swap to DTO files ahead of Stage 5 removal of the translator.
- Stage 3D progressing: `PolicyBackend` ports/backends now advertise DTO support, `resolve_policy_backend` validates the capability, the stub backend raises a `DeprecationWarning` if legacy observation batches are provided without a DTO envelope, and `SimulationLoop` streams `policy.metadata` / `policy.possession` / `policy.anneal.update` events via the dispatcher.
- Stage 3E safeguards added: DTO parity harness re-run, policy controllers guard against missing envelopes, telemetry policy-event smokes land, and rollout capture tests continue to validate DTO trajectory plumbing.
- Stage 4 kickoff: ML smoke test (`tests/policy/test_dto_ml_smoke.py`) runs a torch-backed parity check between DTO and legacy feature tensors; automation and PPO config packaging remain TODO.
- Stage 5 update: `SimulationLoop` now emits DTO-only payloads, `TelemetryPublisher` ingests dispatcher events with policy metadata and DTO envelopes, and observer/conflict telemetry tests drive the dispatcher directly (legacy `_ingest_loop_tick` shim removed). DTO dashboards pull from the new caches (`latest_policy_metadata_snapshot`, `latest_observation_envelope`), leaving Stage 6 guard/doc work and world adapter cleanup as the remaining follow-ups.
- Stage 6 guardrails kicking off: `tests/core/test_no_legacy_observation_usage.py` blocks new ObservationBuilder/legacy payload references in runtime code, the telemetry surface guard asserts DTO envelopes/metadata on each tick, and the default world adapter now fronts the runtime without exposing `legacy_runtime`; ML parity + documentation remain before sign-off.

## Outstanding Work (DTO Rollout)
1. Schedule Stage 6 regression sweep: run full `pytest`, `ruff check`, and `mypy`, then drop remaining world adapter shims once DTO-only consumers are confirmed.
2. Extend parity harness to cover reward breakdown comparisons and run at least
   one ML-backed scenario (short PPO/BC run) to prove DTO-only parity.
3. Document schema & parity results in WP1/WP2 once DTO rollout completes; broadcast release notes/CHANGELOG for DTO-only telemetry.

## Notes / Reminders
- Use sorted agent IDs + shared action vocab from `BehaviorBridge` when
  encoding DTOs.
- Relationships/RNG gaps: combine telemetry caches with
  `WorldRuntimeAdapter.relationships_snapshot()` and `WorldState.rng_seed()`.
- Keep `dto_example_tick.json` updated whenever schema changes; regression
  tests will rely on it.
- Follow up work packages:
  - **WP3C**: DTO parity expansion with ML validation and legacy observation retirement (next).
  - These unblock **WP1** (simulation loop cleanup) and **WP2** (world adapter parity) so we can
    ship the composition-root refactor once DTO-only decisions are verified.
