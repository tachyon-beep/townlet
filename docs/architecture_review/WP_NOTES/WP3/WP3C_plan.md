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

1. **Harness expansion**
   - Upgrade `tests/core/test_sim_loop_dto_parity.py`:
     - Compare per-agent needs, wallet, job fields, queue state, and relationship info between DTO
       and legacy maps.
     - Validate reward breakdowns component-wise (use numpy tolerances).
     - Assert DTO `global_context` promotion/economy snapshots match telemetry/stability caches.
   - Factor common snapshot capture utilities into `tests/core/dto_parity_utils.py`.

2. **Fixture-backed regression**
   - Load baseline fixtures captured in Stage 0 to ensure DTO payloads remain stable across refactors.
   - On failure, diff the JSON dumps to highlight changes (helpful for code reviews).

3. **Telemetry hooks**
   - Extend parity harness to inspect emitted `loop.tick` events (via stub telemetry sink) verifying
     that `observations_dto` contains the enriched envelope and that the legacy `observations`
     reference is no longer required (post Stage 5).

4. **Risk mitigation**
   - Run `pytest tests/core/test_sim_loop_dto_parity.py -q` after every schema change.
   - Track baseline hashes for DTO fixtures so CI alerts on unreviewed schema churn.

---

## Stage 3 – Policy & Training Adapter Migration

**Objective:** Move policy decision + training code onto DTO-only data, keeping scripted parity.

1. **PolicyController / PolicyRuntime**
   - Update `_action_provider` in `SimulationLoop._tick_impl` to pass only the DTO envelope to the
     controller. Replace `observations_batch` usage with DTO-derived data.
   - Store per-tick DTO envelopes in `PolicyRuntime` and expose them via `policy.port.decide`.
   - Make `PolicyController.decide` raise if the backend requests legacy `world` access (after guard).

2. **BehaviorBridge & Scripted Behaviour**
   - Enhance `DTOWorldView` with helpers providing:
     - Agent lookup (position, needs, inventory) compiled from DTO global context.
     - Object roster / affordance availability; inject from legacy world until we emit DTO
       object snapshots (mark TODO).
   - Refactor `ScriptedBehavior` methods to read from `dto_world` first, using the fallback `world`
     only for object lookups until Stage 5.

3. **TrajectoryService & Training flows**
   - Change `TrajectoryService.flush_transitions` signature to accept DTO agents:
     convert `AgentObservationDTO` payloads into frames (features/map remain identical).
   - Update PPO/BC trainers (`policy/models`, `policy/backends/pytorch/bc.py`,
     `policy/backends/pytorch/ppo_utils.py`) to accept DTO frames.
   - Adjust `PolicyTrainingOrchestrator.capture_rollout` & `run_rollout_ppo` so they no longer read
     from `loop.observations` but pull data from DTO envelopes and telemetry events.

4. **Port interfaces**
   - Update `townlet/ports/policy.PolicyBackend.decide` docstring to emphasise DTO usage.
   - Ensure fallback stub (`StubPolicyBackend`) logs when DTO envelopes are ignored (short-term for
     backward compatibility).

5. **Testing**
   - Add unit tests for `TrajectoryService` verifying DTO → frame conversion.
   - Update scripted behaviour tests (if any) to inject DTO views (create targeted fixtures).

6. **Risks**
   - ML extras might not be available in CI: keep adapter updates behind optional imports and gate
     tests with `pytest.importorskip("torch")`.
   - Behaviour parity: run scripted parity harness (Stage 2) immediately after adapter changes.

---

## Stage 4 – ML Smoke Scenario

1. **Test harness**
   - Implement `tests/policy/test_dto_ml_smoke.py`:
     - Use PPO checkpoint (or random-weight network) for ≤30 ticks via SimulationLoop + policy
       backend.
     - Capture actions/rewards under legacy + DTO pathways, compare with tolerances.
   - Mock Torch when unavailable by marking the test `@pytest.mark.slow` and skipping if
     `torch_available()` is false.

2. **Metrics validation**
   - Ensure the smoke test exercises guardrail events, queue promotions, and reward accumulation so
     DTO fields touched by ML flows (e.g., option commits, anneal metadata) stay covered.

3. **Automation**
   - Wire the smoke test into the `ml` tox environment (if present) and document how to run it
     locally (`tox -e ml -- -k dto_ml_smoke`).

4. **Risk prep**
   - Provide a lightweight PPO config (`configs/training/dto_smoke.yml`) to keep runtime < 90s.
   - If parity fails, dump diffing logs (actions, logits) for triage.

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
