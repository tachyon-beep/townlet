# WP3C – DTO Parity Expansion & ML Validation

**Purpose:** Deliver DTO-only policy/telemetry paths, validate them against scripted and ML-backed
scenarios, and retire the final legacy observation plumbing so WP1/WP2 composition work can ship.

---

## Stage 0 – Pre-flight Analysis & Baselines

- [x] Re-run the scripted baseline (`configs/examples/poc_hybrid.yaml`) capturing:
  - Legacy observation batches + DTO envelope dumps for 10 ticks (`docs/architecture_review/WP_NOTES/WP3/dto_parity/legacy_baseline.jsonl`,
    `docs/architecture_review/WP_NOTES/WP3/dto_parity/dto_baseline.jsonl`).
  - Reward breakdown history, queue metrics, policy metadata, rivalry events, and stability metrics.
- [x] Inspect current ML training configs (`configs/training/*.yml`) to confirm feature dimensions,
  map sizes, and action vocab expected by PPO/BC trainers. *(Baseline dimensions recorded in `dto_parity/ml_dimensions.txt`.)*
- [ ] Document outstanding schema gaps discovered during WP3A (e.g. per-agent needs, job context,
  inventory, DTO queue promotions) in `dto_observation_inventory.md` and map each to a source.
- [x] Freeze current `dto_example_tick.json` + `dto_sample_tick.json` snapshots to ease diffs after
  schema changes.

---

## Stage 1 – Schema & Converter Expansion

**Goal:** Extend `ObservationEnvelope` so it encodes everything scripted/ML paths still fetch from
`WorldState`.

1. **Per-agent DTO additions**
   - Add `position`, `needs`, `job`, `inventory`, `personality`, `pending_intent`, and `queue_state`
     fields to `AgentObservationDTO` (`src/townlet/world/dto/observation.py`).
   - Source data from `ObservationBuilder`:
     - Needs & wallet already live in `metadata["compact"]`; upgrade `_build_metadata` to surface a
       stable structure (position, needs, wallet, pending_action, rivalry flags).
     - Job context from employment service (access via `world_adapter.employment_snapshot()` or new
       helper returning job_id, lateness counters, attendance ratios).
   - Record new optional keys and update Pydantic validators + `DTO_SCHEMA_VERSION` (bump to `0.2.0`).

2. **Global context additions**
   - Extend `GlobalObservationDTO` with:
     - `employment_snapshot` (exits today, queue length, job roster summary).
     - `queue_affinity_metrics` (ghost-step counts, rivalry boosts) pulled from queue conflict tracker.
     - `economy_snapshot` (basket_cost, restock cadence) from `economy.step`.
     - `anneal_context` (option commit ticks, blend ratio) from `BehaviorBridge`.
   - Update `build_observation_envelope` so it populates the new fields, normalising dataclasses via
     `_to_builtin`.

3. **Converters & fixtures**
   - Update `tests/world/test_observation_dto_factory.py` to assert presence/type of new fields.
   - Refresh `dto_example_tick.json` / `dto_sample_tick.json` with the expanded envelope.
   - Document schema bump and field semantics in `docs/architecture_review/WP_NOTES/WP3/dto_observation_inventory.md`.

4. **Risk controls**
   - Add a schema changelog table to `dto_observation_inventory.md`.
   - Guard tests: add `tests/world/test_observation_dto_schema_version.py` ensuring fixtures and
     `DTO_SCHEMA_VERSION` stay in sync.

---

## Stage 2 – Parity Harness Enhancements (Scripted Path)

1. **Harness expansion** *(Completed)*
   - [x] `tests/core/test_sim_loop_dto_parity.py` now compares per-agent needs, wallets, and job
     payloads between DTO envelopes and recorded world snapshots (stored in
     `agent_state_history`/`job_snapshot_history`).
   - [x] Verifies reward totals, queue metrics, economy snapshot, queue affinity metrics, and anneal
     context against the recorded world history.
   - [x] PRs can rely on the parity test failing if DTO fields drift.

2. **Fixture-backed regression** *(Partially manual)*
   - [x] Stage 0 captured baselines under `docs/architecture_review/WP_NOTES/WP3/dto_parity`; parity
     test references in-memory captures (no additional module required).
   - [ ] Optional future work: add diff utility if we start snapshotting to disk for CI.

3. **Telemetry hooks** *(Deferred to Stage 5)*
   - Pending legacy observation removal; will assert `loop.tick` payloads once Stage 5 executes.

4. **Risk mitigation**
   - [x] `pytest tests/core/test_sim_loop_dto_parity.py -q` integrated into the workflow for schema
     changes (manual for now).
   - [ ] Automate fixture hash tracking once DTO-only flow stabilises (Stage 6 candidate).

---

## Stage 3 – Policy & Training Adapter Migration

**Objective:** Move policy decision + training code onto DTO-only data, keeping scripted parity and
preserving telemetry output until Stage 5 retires the legacy payloads.

### Stage 3A – Policy runtime wiring
*Status: completed 2025-10-10 — runtime/controller wiring landed; legacy observation batches now emit warnings.*
1. **Catalogue current usage**
   - Search for `_policy_observation_batch`, `observations_batch`, and `world.agents` reads inside
     `SimulationLoop`, `PolicyRuntime`, `PolicyController`, and scripted behaviours.
   - Document any remaining direct `WorldState` reads in `WP3B_trace_notes.md` so we can verify
     they are covered by DTO helpers before removal.
2. **Simulation loop provider**
   - Update `_action_provider` inside `SimulationLoop.step` so DTO envelopes are always constructed
     before policy calls and become the primary payload passed to controllers/backends.
   - Guard the legacy `observations` mapping: keep it available during Stage 3 but mark it as
     deprecated in log output when accessed.
3. **Policy runtime state**
   - Replace `_latest_envelope` with a typed `ObservationEnvelopeCache` storing the DTO plus derived
     helper views (sorted agent list, anneal context, action vocab). Expose this via
     `PolicyRuntime.latest_envelope()` for diagnostics.
   - Adjust `PolicyRuntime.decide` signature and call sites so DTO envelopes are required; thread the
     existing `world` reference only for mutation shims that will emit events.
4. **Policy controller surface**
   - Ensure `PolicyController.decide` forwards DTO envelopes to backends and raises a clear error if
     a backend requests `world` without declaring DTO support. Implement a temporary feature flag
     allowing ML paths to opt-in gradually.

### Stage 3B – DTO world view & scripted behaviour parity
*Status: completed 2025-10-10 — DTO view exposes agent snapshots; scripted behaviour + bridge consume DTO data with guard tests in place.*

1. **DTOWorldView enrichment (`src/townlet/policy/dto_view.py`)**
   - Build an `DTOAgentSnapshot` helper (SimpleNamespace or dataclass) capturing needs, wallet, inventory,
     job context, personality traits, pending intent, and metadata derived from `ObservationEnvelope.agents`.
   - Add lookup APIs:
     - `agent_snapshot(agent_id)` returning the DTO-backed snapshot (fallback to legacy world if missing).
     - `iter_agent_snapshots()` yielding `(agent_id, snapshot)` pairs in sorted order.
     - `agent_position(agent_id)`, `agent_needs(agent_id)`, and `pending_intent(agent_id)` convenience accessors.
     - `agents_at_position(position)` to support chat/avoid logic without scanning `world.agents`.
   - Preserve existing queue/relationship views but expose DTO-derived `queue_affinity_metrics` where available.
   - Ensure legacy fallbacks remain guarded (log once when invoked) so we can track stragglers prior to Stage 5.

2. **Behavior bridge integration (`src/townlet/policy/behavior_bridge.py`)**
   - Require a non-null `DTOWorldView` in `decide_agent` and downstream helpers; tighten type hints and early error if
     it is absent (policy runtime now guarantees availability after Stage 3A).
   - Thread the DTO view through blend/guardrail hooks so scripted behaviour no longer needs direct `WorldState` access
     during decision making (policy action provider may still receive the legacy world for now).
   - Add docstrings/TODO markers wherever we still rely on legacy affordance metadata so Stage 5 clean-up is explicit.

3. **Scripted policy audit (`src/townlet/policy/behavior.py`, `src/townlet/policy/scripted.py`)**
   - Route snapshot, rival, and agent iteration logic through the DTO helpers:
     - Replace `world.agents[...]` lookups with `dto_world.agent_snapshot(...)`.
     - Swap queue/relationship checks to DTO-first access, logging or falling back only when DTO data is absent.
     - Abstract object lookups (`_find_object_of_type`) so DTO pathways can provide overrides later; document remaining
       legacy dependencies (e.g., `world.objects`) with TODOs for Stage 5.
   - Ensure pending-intent bookkeeping and guardrail calls operate purely on DTO-provided identifiers.

4. **Targeted tests (`tests/policy/test_scripted_behavior_dto.py`)**
   - Construct DTO fixtures from `dto_example_tick.json` to validate:
     - Pending intent promotion uses DTO queue state even when the legacy queue manager raises (regression guard).
     - Rivalry/chat logic iterates over DTO agent snapshots (configure world stub to raise if `agents` is accessed).
     - Behaviour returns stable intents for DTO-only worlds (world stub lacking agent data).
   - Patch existing behaviour tests, if needed, to inject DTO views and keep parity.

5. **Documentation / tracking**
   - Update `WP3B_trace_notes.md` with the new DTO-backed access patterns and list any residual legacy hooks.
   - Record the change in `status.md` / `pre_compact_brief.md` once tests pass; flag remaining Stage 3C blockers.

### Stage 3C – Trajectory and training plumbing
1. **Trajectory service** *(completed 2025-10-10)*
   - `TrajectoryService.flush_transitions` now accepts DTO envelopes (and optional legacy batches) and
     consumes agent tensors plus anneal context directly from the `ObservationEnvelope`.
   - Added regression coverage in `tests/policy/test_trajectory_service_dto.py` to ensure DTO frames
     carry action/reward data and anneal context without touching legacy world state.
2. **Training orchestrator** *(completed 2025-10-10)*
   - `capture_rollout` now instantiates a fresh `SimulationLoop` per run, consumes DTO-backed
     trajectory frames, and relies on telemetry events for metrics (no `loop.observations` access).
   - Added DTO regression coverage (`tests/policy/test_training_orchestrator_capture.py`) via stubbed
     loops, ensuring collected frames expose map/features and anneal context.
3. **Backends and dataset builders**
   - [x] Embed DTO agent/global context into trajectory frame metadata so replay samples retain
     needs, wallet, job, queue, and pending intent details alongside `dto_schema_version`.
   - [x] Persist anneal context and DTO metadata in `frames_to_replay_sample` so PPO/BC datasets see
     the richer envelope-derived information while keeping existing tensor shapes unchanged.
   - [ ] Where legacy format is still required for external files, introduce a thin translator that
     consumes DTOs and produces the older schema solely for export, with TODO to drop after Stage 5.

### Stage 3D – Surface/port adjustments
1. **Ports and stubs** *(completed 2025-10-10)*
   - Update the `PolicyBackend` protocol (`townlet/policy/api.py`) and stub implementations to make
     DTO support explicit. Emit a `DeprecationWarning` if the stub consumes `observations` instead of
     the DTO envelope.
2. **Telemetry events** *(completed 2025-10-10)*
   - Emit `policy.metadata`, `policy.possession`, and `policy.anneal.update` events directly from
     DTO-derived data, ensuring the event dispatcher gets fed without needing world lookups.

### Stage 3E – Regression safety net
1. **Parities** *(completed 2025-10-10)*
   - DTO parity harness exercised via `pytest tests/core/test_sim_loop_dto_parity.py -q`;
     results archived in `docs/architecture_review/WP_NOTES/WP3/dto_parity/`.
2. **Targeted tests** *(completed 2025-10-10)*
   - Added DTO enforcement smoke (`tests/orchestration/test_policy_controller_dto_guard.py`) and
     telemetry policy-event coverage (`tests/core/test_sim_loop_policy_events.py`,
     `tests/telemetry/test_policy_events.py`).
3. **Rollout capture** *(completed 2025-10-10)*
   - `tests/policy/test_training_orchestrator_capture.py` continues to validate DTO rollouts while
     the new telemetry policy events remain available for downstream consumers.

**Risks & mitigations**
- Torch optionality: gate new ML-dependent tests with `pytest.importorskip("torch")` and mark them
  `@pytest.mark.slow` to keep core CI lean.
- Behaviour drift: keep Stage 2 parity fixtures up to date and diff outputs in review; capture a new
  baseline only after confirming DTO parity.
- External consumers: note in documentation that the legacy observation dict is deprecated but still
  available until Stage 5, so downstream tooling has a transition window.

---

## Stage 4 – ML Smoke Scenario

1. **Test harness** *(completed 2025-10-10)*
   - `tests/policy/test_dto_ml_smoke.py` runs a ≤5 tick SimulationLoop capture and feeds DTO vs legacy
     feature tensors through a random-weight torch network, asserting logits/actions remain aligned.
     Torch is imported lazily via `pytest.importorskip`.

2. **Metrics validation** *(completed 2025-10-10)*
   - Smoke test verifies finite reward streams while DTO-derived policy events are active; failures
     surface via numpy assertions.

3. **Automation** *(completed 2025-10-10)*
   - Added `tox -e ml` profile (see `tox.ini`) running the DTO smoke test; document in WP notes.

4. **Risk prep** *(completed 2025-10-10)*  
   - Checked in `configs/training/dto_smoke.yaml` (10-tick scripted rollout, stub telemetry) and
     drafted migration guidance in `docs/architecture_review/WP_NOTES/WP3/dto_migration.md`.

---

## Stage 5 – Legacy Observation Retirement

1. **SimulationLoop cleanup**
   - Remove `self._policy_observation_batch`, stop storing `observations` in tick artifacts, and
     delete the legacy `observations` entry from telemetry payloads.
   - Drop `observations` from `TickArtifacts` (update tests using it).

2. **Telemetry publisher**
   - Ensure no event emitter (`TelemetryPublisher`, sinks) references `observations` or legacy reward
     getters. Update guard tests to fail if `telemetry.emit_event(..., observations=...)` reappears.

3. **World adapters**
   - Remove `LegacyWorldRuntime.tick` fallback paths relying on `WorldState.apply_actions`.
   - Confirm `create_world` providers no longer return legacy handles needed solely for observations.

4. **External surfaces**
   - Update CLI tools/training scripts relying on `loop.observations` (e.g., `policy/training_orchestrator.py`)
     to use DTO events or `loop._policy_observation_envelope`.

5. **Regression sweep**
   - Run full test suite (`pytest -q`), lint, and mypy to catch stragglers referencing removed
     attributes.

---

## Stage 6 – Guard Rails, Docs, & Release Notes

1. **Tests & linters**
   - Add `tests/core/test_no_legacy_observation_usage.py` scanning for prohibited imports (`ObservationBuilder` direct usage outside allowed modules).
   - Extend `tests/test_telemetry_surface_guard.py` to ensure `loop.tick` payloads lack legacy fields.

2. **Documentation**
   - Update WP1/WP2/WP3 status + `pre_compact_brief.md` summarising DTO-only status.
   - Refresh ADR-001 (policy/telemetry pipeline) with DTO schema v0.2.0 and parity guarantees.
   - Add migration notes for downstream consumers (telemetry dashboards, training notebooks) in
     `docs/architecture_review/WP_NOTES/WP3/dto_migration.md`.

3. **Release checklist**
   - Note schema bump & parity results in CHANGELOG.
   - Notify analytics/ML stakeholders about DTO-only changeover and sample payloads.

---

## Exit Criteria

- DTO schema v0.2.0 (or later) validated by parity fixtures and schema guard tests.
- Scripted parity harness passes comparing DTO vs legacy on needs, queue metrics, rewards, and policy
  metadata without reading legacy observation blobs.
- ML smoke test executes successfully using DTO inputs; training orchestrator/traj services ingest DTOs.
- `SimulationLoop`, telemetry, and policy adapters no longer emit or expect legacy observation payloads.
- Documentation and tasks updated to reflect DTO-only operation; regression guards in place to prevent
  reintroducing legacy pathways.
