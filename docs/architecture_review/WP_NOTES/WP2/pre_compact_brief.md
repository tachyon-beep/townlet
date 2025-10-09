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
- **Step 5 (action pipeline scaffolding):**
  - Action schema/validation implemented (`Action`, `ActionValidationError`) with coercion for supported kinds and detailed error reporting (`tests/world/test_actions.py`).
  - Interim apply pipeline updates agent snapshots/records for implemented kinds (`move`, `noop`), emits structured events (including invalid/pending markers), and leaves hooks for future system integration.
- **Step 6 (systems orchestration):**
  - `WorldContext.tick` now sequences console → actions → modular systems → nightly reset → lifecycle evaluation and returns `RuntimeStepResult`.
  - Event flow is unified via `EventDispatcher`; legacy `WorldState` exposes `emit_event`, `event_dispatcher`, and `agent_records_view` to satisfy the modular pipeline while keeping telemetry compatibility.
  - System modules (`queues`, `affordances`, `employment`, `relationships`, `economy`, `perturbations`) execute inside the context using the shared `SystemContext`; unit suites under `tests/world/test_systems_*.py` plus `tests/test_world_context.py` are green.
- Docs updated (`analysis.md`, `tasks.md`, `README.md`, `status.md`) to reflect the above.

## Remaining (per implementation plan)
1. **Step 7 – Adapter & factory integration:** update `DefaultWorldAdapter`/`world_factory` so the simulation loop resolves the modular `WorldContext` provider by default.
2. **Step 8 – Composition root:** revive WP1 Step 4 (SimulationLoop refactor, console router, health monitor, removal of telemetry getters) once the new context is the default world provider.
3. **Step 9–11:** cleanup legacy modules, comprehensive test/docs update, final QA.

## Key decisions to remember
- Observation builder remains external for now; `WorldContext.observe()` will call into it until WP3.
- Console/telemetry services (ConsoleRouter/HealthMonitor) will be integrated during the SimulationLoop refactor after the world package is in place.
- No DTOs yet; still using dict payloads for observations and events.

## Current Git state
- All relevant files added (`townlet/world/spatial.py`, `townlet/world/observe.py`, etc.).
- Tests added under `tests/world/`.
- Pending tasks tracked in `tasks.md` (State/agents extraction is next).

## Next steps immediately after compaction
1. Start Step 7 by wiring the factory/provider layer to build `WorldContext` directly (drop the compatibility adapter hand-off in `WorldRuntime`).
2. Prepare the composition-root refactor plan (console router + health monitor) now that tick orchestration parity is in place.
3. Maintain the new test coverage (`pytest tests/world -q` + `pytest tests/test_world_context.py -q`) as integration proceeds.
