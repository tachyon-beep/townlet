# WP2 Pre-Compact Brief (2025-10-09)

This note captures the exact state of WP2 before memory compaction so upcoming work can resume smoothly.

## Completed
- **Planning (Steps 0–1):**
  - Catalogued responsibilities in `world/grid.py`, `world/runtime.py`, observation builder.
  - Documented couplings (console/telemetry/observations/RNG) and confirmed ADR-002 alignment.
  - Strategy for observations: wrap existing `ObservationBuilder` inside the new context until DTOs arrive in WP3.
- **Skeleton setup (Step 2):** created placeholder modules under `townlet/world/` (`context`, `state`, `spatial`, `agents`, `actions`, `observe`, `events`, `rng`, `systems/__init__`).
- **Step 3 (stateless extraction):**
  - `WorldSpatialIndex` moved into `townlet.world.spatial`; `WorldState` now imports the new class.
  - Observation helper functions (`local_view`, `find_nearest_object_of_type`) moved into `townlet.world.observe`; `world/observations/views.py` re-exporting.
  - Domain event primitives implemented in `townlet.world.events` with unit tests (`tests/world/test_events.py`).
  - Unit tests added: `tests/world/test_spatial.py`, `tests/world/test_observe_helpers.py`.
- **Step 4 (state/agents foundations):**
  - `AgentRegistry` upgraded with created/updated tick tracking, metadata, and read-only views (`tests/world/test_agents_registry.py`).
  - New `WorldState` container manages RNG seeding/state, ctx-reset queue, event buffering, and serialisable snapshots (`tests/world/test_world_state.py`).
- Docs updated (`analysis.md`, `tasks.md`, `README.md`, `status.md`) to reflect the above.

## Remaining (per implementation plan)
1. **Step 5 – Action pipeline:** define action schemas and mutation logic, plus tests.
2. **Step 6 – Systems & tick orchestration:** break out employment/economy/etc. into `systems/*`, flesh out `rng.py`, implement `WorldContext` methods.
3. **Step 7 – Adapter & factory integration:** update `DefaultWorldAdapter`/`world_factory` to return the new `WorldContext`.
4. **Step 8 – Composition root:** once world context is live, revive WP1 Step 4 (SimulationLoop refactor, console router, health monitor, removal of telemetry getters).
5. **Step 9–11:** cleanup legacy modules, comprehensive test/docs update, final QA.

## Key decisions to remember
- Observation builder remains external for now; `WorldContext.observe()` will call into it until WP3.
- Console/telemetry services (ConsoleRouter/HealthMonitor) will be integrated during the SimulationLoop refactor after the world package is in place.
- No DTOs yet; still using dict payloads for observations and events.

## Current Git state
- All relevant files added (`townlet/world/spatial.py`, `townlet/world/observe.py`, etc.).
- Tests added under `tests/world/`.
- Pending tasks tracked in `tasks.md` (State/agents extraction is next).

## Next steps immediately after compaction
1. Progress Step 5 by designing the action schema and validator utilities.
2. Ensure existing tests continue to pass (`pytest tests/world/test_events.py tests/world/test_spatial.py tests/world/test_observe_helpers.py tests/world/test_agents_registry.py tests/world/test_world_state.py`, plus focused suites as functionality moves).
