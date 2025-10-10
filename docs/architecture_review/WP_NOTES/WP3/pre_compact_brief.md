# WP3 Pre-Compact Brief — 2025-10-09

Latest context snapshot so we can resume quickly after memory compaction.

## Current State
- Telemetry pipeline is fully event-driven; legacy writer APIs removed and
  guard tests protect the dispatcher surface (`tests/test_telemetry_surface_guard.py`).
- DTO Step 1 complete:
  - `dto_observation_inventory.md` documents every `WorldState` consumer and the
    proposed DTO field types/optional rules.
  - `dto_example_tick.json` + `dto_sample_tick.json` provide baseline payloads.
  - `dto_worldstate_usage.json` auto-extracted usage map for converters.
- DTO schema models scaffolded in `src/townlet/world/dto/observation.py` and re-exported through `townlet.world.dto` (`DTO_SCHEMA_VERSION = "0.1.0"`); `build_observation_envelope` factory + `tests/world/test_observation_dto_factory.py` validate JSON readiness, and `SimulationLoop` caches/attaches the DTO payload to `loop.tick` events (`observations_dto`).
  Envelope now includes queue rosters, running affordances, and relationship metrics. `PolicyRuntime` consumes cached DTO data via `DTOWorldView`; scripted behaviour now reads queue/affordance/relationship info from the DTO view and emits guardrail requests as events (legacy fallbacks remain for missing envelopes). `WorldContext.tick` routes combined actions through `affordances.process_actions`, `queues.step` handles ghost-step conflicts, and `advance_running_affordances` completes hand-overs via the runtime service.
- Modular system suite (WP3B) is done: `employment.step`, `economy.step`, and `relationships.step` execute each tick, `_apply_need_decay` only invokes employment/economy fallbacks when services are absent, and `affordances.step` no longer calls `state.resolve_affordances`. Targeted unit suites (`tests/world/test_systems_{affordances,queues,employment,economy,relationships}.py`) plus `pytest tests/world -q` hold the regression line.

## Outstanding Work (DTO Rollout)
1. Move policy metadata/ML adapters onto DTO batches and stream
   `policy.metadata`/`policy.possession`/`policy.anneal.update` events.
2. Extend parity harness to cover reward breakdown comparisons and run at least
   one ML-backed scenario (short PPO/BC run) to prove DTO-only parity.
3. Remove legacy observation payloads / world supplier hooks once parity and
   adapters land; update telemetry/docs and notify downstream consumers.
4. Document schema & parity results in WP1/WP2 once DTO rollout complete.

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
