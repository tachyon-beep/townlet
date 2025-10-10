# WP3 Pre-Compact Brief — 2025-10-09

Latest context snapshot so we can resume quickly after memory compaction.

## Current State
- Telemetry pipeline is fully event-driven; legacy writer APIs removed.
- HTTP transport now posts dispatcher events (`transport.py`), guard tests lock
  the surface (`tests/test_telemetry_surface_guard.py`).
- DTO Step 1 complete:
  - `dto_observation_inventory.md` documents every `WorldState` consumer and the
    proposed DTO field types/optional rules.
  - `dto_example_tick.json` + `dto_sample_tick.json` provide baseline payloads.
  - `dto_worldstate_usage.json` auto-extracted usage map for converters.
- DTO schema models scaffolded in `src/townlet/world/dto/observation.py` and re-exported through `townlet.world.dto` (`DTO_SCHEMA_VERSION = "0.1.0"`); `build_observation_envelope` factory + `tests/world/test_observation_dto_factory.py` validate JSON readiness, and `SimulationLoop` caches/attaches the DTO payload to `loop.tick` events (`observations_dto`).
  Envelope now includes queue rosters, running affordances, and relationship metrics. `PolicyRuntime` consumes cached DTO data via `DTOWorldView`; scripted behaviour now reads queue/affordance/relationship info from the DTO view and emits guardrail requests as events (legacy fallbacks remain for missing envelopes). `WorldContext.tick` now routes combined actions through `affordances.process_actions` (extracted from the legacy world), `queues.step` handles ghost-step conflicts, and `advance_running_affordances` completes hand-overs via the runtime service—keeping scripted parity while we finish migrating the remaining employment/economy hooks under WP3B.

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
  - **WP3B**: modular system reattachment + bridge removal (next focus: migrate employment/economy
    systems so we can drop `resolve_affordances` entirely, unblocking WP1 Step 8).
  - **WP3C**: DTO parity expansion with ML validation and legacy observation retirement.
  - These unblock **WP1** (simulation loop cleanup) and **WP2** (world adapter parity) so we can
    ship the composition-root refactor once DTO-only decisions are verified under WP3C.
