# WP-C Phase 0 – World Subsystem Recon

## Snapshot

- `src/townlet/world/grid.py` = 2,047 LOC. Hosts hook registry, agent/object dataclasses, spatial index, and the monolithic `WorldState` implementation that manages console IO, queueing, employment, relationships, affordances, telemetry events, RNG, economy, and snapshot/observation plumbing.
- Supporting modules:
  - `world/runtime.py`: façade coordinating tick sequencing between `SimulationLoop` and `WorldState` (drains console commands, applies actions, runs perturbations, resolves affordances, nightly resets, lifecycle evaluation, event drain).
  - `world/console_bridge.py`: dedicated command router/result buffer used by `WorldState.apply_console`.
  - `world/queue_manager.py` & `world/queue_conflict.py`: fairness/ghost-step engine plus telemetry-friendly conflict tracker.
  - `world/affordances.py` & `world/affordance_runtime_service.py`: runtime wrapper that still relies heavily on `WorldState` internals via `AffordanceRuntimeContext`.

## Responsibilities Observed in `WorldState`

| Concern | Key Methods / Attributes | Notes |
| --- | --- | --- |
| Console ingestion & routing | `_console` (`ConsoleService`), `_console_controller` (from `install_world_console_handlers`), `apply_console`, `consume_console_results` | Relies on `console_bridge.ConsoleBridge` for dedupe/history; handlers expect full `WorldState` access. |
| Queue management | `queue_manager` (`QueueManager`), `_queue_conflicts` (`QueueConflictTracker`), `_sync_reservation`, `_handle_blocked` | Queue events mutate relationships and emit telemetry via `_emit_event`; reservations mirrored onto `InteractiveObject.occupied_by` and spatial index. |
| Affordances & hooks | `_affordance_service` (`AffordanceRuntimeService`), `_apply_affordance_effects`, `resolve_affordances`, `_load_affordance_definitions`, `HookRegistry` | Context object injects mutable maps (`objects`, `affordances`, `_running_affordances`), queue manager, event emitters, and need decay callbacks. |
| Agents & employment | `agents`, `_job_keys`, `add_agent`, `_assign_job_if_missing`, `employment` (`EmploymentCoordinator`), `_employment_runtime` | Employment coordinator emits events via `_emit_event`; rivalry/relationship ledgers live on `WorldState`. |
| Relationships & rivalry | `_relationship_ledgers`, `_relationship_churn`, `_rivalry_ledgers`, methods like `update_relationship`, `record_chat_success`, `record_queue_conflict` | Queue conflict tracker feeds back into relationship updates. |
| Observation & policy context | `embedding_allocator`, `request_ctx_reset`, `consume_ctx_reset_requests`, `agent_snapshots_view`, `running_affordances_snapshot` | Supplies observation builder and policy runtime with preprocessed snapshots. |
| Telemetry & events | `_pending_events`, `_emit_event`, `drain_events`, queue/relationship telemetry helpers (`relationship_churn_snapshot`, `queue_metrics_snapshot`) | Telemetry expects specific payload shapes; events drained each tick by `WorldRuntime`. |
| Snapshot & RNG | `snapshot`, `export_state`, `import_state`, `_rng` + `attach_rng`, `_rng_state`, store stock export/import | `SimulationLoop` uses these during snapshot save/load; RNG state must remain serialisable. |
| Economy/utility | `apply_utility_outage`, `_recompute_price_spikes`, `economy_settings`, etc. | Suggests future `world/economy/` split. |

## External Contracts & Touch Points

- `SimulationLoop` expects `WorldState.from_config`, `.apply_console`, `.consume_console_results`, `.apply_actions`, `.resolve_affordances`, `.apply_nightly_reset`, `.drain_events`, and `.tick` mutation. (`src/townlet/core/sim_loop.py:170-204` & `world/runtime.py`)
- `LifecycleManager` interacts via `world.runtime.WorldRuntime`, but lifecycle evaluation mutates `WorldState` directly (respawn, termination reasons). Any façade must preserve hooks: `process_respawns`, `evaluate`, `termination_reasons`.
- Telemetry snapshot import/export relies on `snapshot_from_world` (`src/townlet/snapshots/state.py`) calling `WorldState.export_state`, queue snapshots, relationship churn aggregations, etc. Stubs for telemetry must remain stable.
- Training orchestrator pulls policy provider metadata and depends on `WorldState.running_affordances_snapshot`, `consume_ctx_reset_requests`, and `RolloutBuffer` integration.
- Console tests (`tests/test_console_*`), queue tests (`tests/test_world_queue_integration.py`), conflict scenarios, behaviour profiles, and telemetry snapshots all instantiate `WorldState` directly—refactor must provide backward compatible import surface or shim.

## Identified Shared State / Mutation Hotspots

- Multiple subsystems mutate agent snapshots: affordance outcomes, employment runtime callbacks, relationship updates, utility/economy adjustments. Shared `AgentSnapshot.needs` & `inventory` dictionaries are the canonical state.
- Queue manager uses `WorldState` callbacks (`_sync_reservation`, `record_queue_conflict`) to keep `InteractiveObject` flags and relationship ledgers in sync; separation requires an explicit reservation interface.
- Console handlers currently access `WorldState` internals freely (employment, perturbations, snapshots). When extracted, the controller will need a well-defined access layer (likely via `WorldContext`).
- RNG state is threaded through multiple features (affordance sampling, employment, perturbations). A central RNG service within the new core package should own seeding & snapshotting.

## Proposed Package Boundaries (refined)

1. `world/core/`
   - `WorldContext` façade exposing orchestrated services (`agents`, `queue`, `affordances`, `employment`, `relationships`, `rng`, `events`).
   - Shared dataclasses (`AgentSnapshot`, `InteractiveObject`) and spatial index utilities.
2. `world/console/`
   - Console bridge, handlers, controller wiring, command schemas. Depends on core façade only.
3. `world/queue/`
   - Queue manager + conflict tracker, fairness metrics, telemetry adapters.
4. `world/agents/`
   - Registry helpers, relationship/rivalry ledgers, employment coordinator/runtime integration, need decay, economy utilities.
5. `world/affordances/`
   - Runtime service, manifest loading, hook dispatch, effect application; consumes queue and agent services through interfaces.
6. `world/observations/`
   - Observation and context-reset adapters, embedding allocator coordination, snapshots for policy/telemetry.
7. (Optional follow-up) `world/economy/` for utility & price spike logic once core extracted.

## Risks & Invariants for Subsequent Phases

- Preserve snapshot compatibility (`export_state` / `import_state` payloads, queue/affordance history) to avoid breaking saved games and regression tests.
- Maintain event schema used by telemetry (`_emit_event` payloads such as `queue_conflict`, `employment_exit`, `narration`). Schema drift must be coordinated with UI and tests in `tests/test_conflict_telemetry.py`, etc.
- Ensure `WorldRuntime.tick` continues to operate without behavioural regressions; unit tests around queue fairness, behaviour personalities, employment loops should be run after each extraction step.
- Stub-aware behaviour (when optional extras disabled) now flows through `townlet.core.utils` helpers—refactor must keep these surfaces accessible.
- Employment, rivalry, and economy subsystems rely on implicit ordering. Moving them into modules should preserve sequencing (e.g., employment reset before agent removal).

## Next Deliverables

- Finalise `WorldContext` interface sketch and dependency graph for each new package.
- Draft migration checklist (remove direct imports, update tests/docs) in upcoming Phase 1 planning doc.
- Confirm stakeholders (console UI, telemetry, training) on expected touch points before code moves.

## Phase 1 Scaffold Summary

- Implemented `WorldContext` façade (`src/townlet/world/core/context.py`) and exposed it via `SimulationLoop.world_context` for downstream consumers.
- Added placeholder packages:
  - `world/core/`, `world/console/`, `world/queue/`, `world/agents/`, `world/observations/` currently re-export legacy implementations while providing stable import paths.
  - `world/affordances/` requires converting `affordances.py` into a package; defer until logic extraction to avoid circular imports.
- Created `tests/test_world_context.py` to verify façade parity with `WorldState` (agents/objects views, event emission, console access).
- Next steps: migrate console/queue modules to depend on `WorldContext` in place of direct `WorldState` attribute access and extend telemetry/snapshot helpers to accept the façade.
