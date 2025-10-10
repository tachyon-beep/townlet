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
  Envelope now includes queue rosters, running affordances, and relationship metrics.

## Outstanding Work (DTO Rollout)
1. Integrate the converter into world/policy paths and extend validation harness
   (parity checks now cover DTO tensor parity; next add action/reward parity and world-state detachment).
2. Update scripted policy path to consume DTOs and emit telemetry events.
3. Extend to ML/training adapters, then remove `runtime.queue_console` + legacy
   world mutations.
4. Document schema & parity results in WP1/WP2 once DTO rollout complete.

## Notes / Reminders
- Use sorted agent IDs + shared action vocab from `BehaviorBridge` when
  encoding DTOs.
- Relationships/RNG gaps: combine telemetry caches with
  `WorldRuntimeAdapter.relationships_snapshot()` and `WorldState.rng_seed()`.
- Keep `dto_example_tick.json` updated whenever schema changes; regression
  tests will rely on it.
