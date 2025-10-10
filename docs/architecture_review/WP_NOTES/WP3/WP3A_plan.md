# WP3A – Policy DTO Detachment

Purpose: Finalise the policy/DTO migration under WP3 by removing direct
`WorldState` dependencies from policy logic, expanding parity coverage, and
retiring legacy telemetry artefacts.

## Objectives

1. Provide DTO-derived views for policy behaviours/guardrails so the controller
   no longer reads `WorldState` internals.
2. Prove behavioural parity (actions + reward breakdowns) across legacy and
   DTO-driven paths for scripted and ML-backed scenarios.
3. Remove legacy observation emission and world wiring once policy detachment
   succeeds, updating telemetry/docs accordingly.

## Work Breakdown

### A. DTO Access Layer

1. **Current-state audit**
   - Enumerate `WorldState` attributes used by `PolicyRuntime`, `BehaviorBridge`,
     scripted behaviours, guardrail helpers, and telemetry metadata.
     - Scripted behaviour (`src/townlet/policy/behavior.py`): `world.agents`,
       `world.queue_manager.active_agent/queue_snapshot`,
       `world.affordance_runtime.running_affordances`, `world.tick`,
       `world.objects`, `world.rivalry_value/should_avoid`,
       `world.relationship_tie`, `world.queue_manager`, various job config hooks.
     - Guardrails (`PolicyRuntime._apply_relationship_guardrails`):
       `world.rivalry_should_avoid`, `world.record_chat_failure`,
       `world.record_relationship_guard_block`.
     - Behavior bridge (`BehaviorBridge.decide_agent`): requires queue state,
       running affordances, relationship avoidance, anneal RNG, possession state.
     - Metadata (`SimulationLoop` policy identity/promotion): relies on
       `PolicyRuntime` snapshots, option switch counts, possessed agents.
      - `PolicyRuntime._apply_relationship_guardrails`: mutates/reads
        relationship avoidance helpers (`record_chat_failure`,
        `record_relationship_guard_block`, `rivalry_should_avoid`).
     - Telemetry consumers occasionally call
       `loop.policy.possessed_agents/consume_option_switch_counts` (already DTO
       friendly) but world-derived metrics (relationships, queues) still route
       through legacy getters.
   - Categorise usages: relationships, queue snapshots, employment metrics,
     RNG, agent inventory, etc.
   - *Risk reduction*: capture sample DTO envelopes highlighting missing fields;
     consult behaviour owners to confirm requirements.
   - Identify data gaps relative to current DTO envelope: no queue roster,
     running affordance listing, direct relationship tie metrics, or mutation
     pathways (`record_chat_failure`, `record_relationship_guard_block`).

2. **Adapter design**
    - Propose DTO-derived view classes (e.g., `DTOWorldView`, relationship/queue
      facades) sourcing data from the cached envelope + auxiliary services.
      * Candidate additions to the envelope:
        - Queue rosters and active agent metadata (from
          `queue_manager.export_state()`).
        - Running affordance descriptors (object id → agent/affordance).
        - Relationship tie metrics / rivalry scores per agent pair.
        - Mutation channels for guardrails (emit events instead of calling
          `record_chat_failure` / `record_relationship_guard_block`).
   - Define fallback strategy while legacy world references remain.
   - *Research*: confirm envelope contains (or can source) all required metrics;
     identify new DTO fields if gaps exist (e.g., queue rosters, running
     affordances, relationship tie strengths, guardrail mutation hooks).

3. **Implementation**
   - **Schema updates** *(done — queue/affordance/relationship context added)*
     - Extend DTO envelope builder with queue roster/running affordance data and
       relationship metrics; adjust parity tests accordingly. *(Done in
       `src/townlet/world/dto/observation.py` & `src/townlet/world/dto/factory.py`.)*
     - Provide migration notes for downstream consumers when schema changes.
   - **Adapter scaffolding**
     - Implement DTO-backed world view classes (`DTOWorldView`, guardrail helpers)
       leveraging the enriched envelope + auxiliary services (e.g.,
       `world_port` snapshots for write paths during transition). *(Initial
       version in `src/townlet/policy/dto_view.py`; exposes queue manager,
       affordance runtime, relationship tie helpers with legacy fallbacks.)*
  - **Behaviour refactor**
    - Update scripted behaviours/guardrails to consume DTO adapters; fall back
      to legacy world access behind a feature flag until parity confirmed.
      *(Scripted behaviour now pulls queue/affordance/relationship data from
      `DTOWorldView`; legacy world is only used when envelopes are absent.)*
  - **Mutation/event pipeline**
    - Replace direct calls to `world.record_*` guardrail helpers with DTO/port
      emitted events consumed by telemetry or downstream logic. *(Done via
      `policy.guardrail.request` events handled in `WorldState`; `WorldContext`
      still replays legacy `apply_actions` + `resolve_affordances` for parity and
      should be retired once modular systems are complete.)*
   - **Risk mitigation & rollout**
     - Gate adapter usage via config flag; monitor payload size impacts; ensure
       schema version is bumped when envelope structure changes.

4. **Unit/Integration tests**
   - Add focused tests covering adapter outputs, guardrail decisions, and
     anneal blending using DTO data.
   - Update existing behaviour tests to run against adapter-driven data.

### B. Parity Expansion

1. **Harness enhancement**
   - Extend `tests/core/test_sim_loop_dto_parity.py` to compare reward
     breakdown components, anneal/option metadata, and queue/relationship
     snapshots between DTO and legacy paths.
   - Add fixtures capturing DTO snapshots for deterministic assertions.

2. **Scenario coverage**
   - Scripted: run multiple configs (idle, conflict-heavy) and assert equality.
   - ML-backed: execute a short PPO/BC rollout (or replay) using DTO-fed
     decisions, compare action/reward logs vs legacy.
   - *Research*: identify minimal ML scenarios that exercise critical code paths
     without long runtimes.

3. **Results documentation**
   - Store parity outputs/logs in `tmp/` or docs for review.
   - Summarise findings in WP3 docs, noting any residual discrepancies.

### C. Telemetry & Cleanup

1. **Legacy field removal**
   - Drop `observations`/legacy world emission from `loop.tick` once parity
     passes.
   - Remove world supplier hooks/legacy caches from `PolicyController` and
     telemetry sinks.

2. **Documentation updates**
   - Refresh WP1/WP2/WP3 notes, ADRs, and migration guides to reflect DTO-only
     policy flow and telemetry changes.
   - Provide upgrade checklist for downstream consumers (dashboards, CLI,
     trainers).

3. **Validation sweep**
   - Run `pytest` (full), `ruff`, `mypy`, and representative training runs.
   - Capture output summaries, filing regression tickets if deviations appear.

4. **Rollout readiness**
   - Coordinate with dependent teams before merging breaking changes.
   - Plan fallbacks (feature flags or revert paths) in case DTO-only rollout hits
     unexpected issues.

## Risk/Dependencies
- ML policy paths may require additional DTO fields; coordinate with WP2 if new
  adapters are needed.
- Ensure downstream telemetry consumers (dashboards, CLI) are ready for DTO-only
  payloads before removing legacy fields.

## Deliverables
- DTO adapter module(s) with unit tests.
- Updated parity harness (actions + rewards) with recorded outputs.
- Simulation loop and docs reflecting DTO-only policy flow.
