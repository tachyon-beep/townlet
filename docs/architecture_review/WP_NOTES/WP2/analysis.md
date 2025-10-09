# WP2 Analysis Notes

_Last updated: 2025-10-09_

## Legacy World Responsibilities (initial pass)
- `world/grid.py`
  - Owns mutable world state (agent registry, interactive objects, queues, utilities, employment/economy snapshots, RNG state) plus helper types (`HookRegistry`, `InteractiveObject`, etc.).
  - Embeds console support (`ConsoleService`, history buffers, handler installation).
  - Drives affordance runtime, relationships, employment coordination, queue conflict tracking, nightly resets, and direct mutation of agent snapshots.
  - Exposes snapshot/restore helpers, relationship metrics/overlays, rivalry events, policy snapshots, and telemetry-friendly structures (e.g., `latest_*`).
- `world/runtime.py`
  - Façade consumed by `SimulationLoop`: buffers console commands, stages policy actions, advances perturbations, evaluates lifecycle termination, and returns `RuntimeStepResult` (console results, events, termination flags, action payloads).
  - Relies directly on `WorldState` from `grid.py`; inherits console/telemetry coupling.
- `world/observations/*` & `townlet/observations/builder.py`
  - Observation builder constructs per-agent tensors by drilling into world adapter (agent snapshots, embedding allocator, spatial cache). Responsible for feature engineering, metadata, social snippets.
- Telemetry/policy touchpoints
  - `TelemetryPublisher` calls directly into world adapters (`relationship_snapshot`, `queue_manager.metrics()`, `consume_rivalry_events`, etc.) and maintains many `latest_*` caches.
  - `PolicyRuntime` depends on world adapter for agent snapshots, embedding allocator, rivalry info, and context reset callbacks.
  - `SimulationLoop` stitches everything together by calling world runtime, observation builder, rewards engine, telemetry publisher, and stability monitor.

## Key Couplings to Address
- Console: embedded in `grid.py`/`WorldRuntime`; should move to orchestration (`ConsoleRouter`). World ought to emit domain events rather than manipulating console buffers directly.
- Telemetry: reliance on `latest_*` getters must be replaced by event/metric emission so the monitoring layer (`HealthMonitor`) can derive insights without pulling from world.
- Observations: current builder is tightly coupled with world internals. For WP2 we likely wrap the builder within `WorldContext.observe()` to avoid breaking policy/telemetry, then refactor internals incrementally.
- RNG/determinism: RNG streams are scattered across world/services; need a central `rng.py` to seed and provide reproducible generators consumed by systems/actions.
- Systems ordering: tick flow currently lives in `WorldRuntime.tick()` interleaving console, perturbations, affordances, lifecycle, events. New modular design must make this explicit and testable.

## Dependencies & Risks
- **SimulationLoop:** still uses legacy `WorldRuntime` and expects console buffering and observation builder outputs. WP2 must deliver a `WorldContext` that satisfies `WorldRuntime` port while preserving behaviour until WP3 DTO adoption.
- **Observation Builder:** moving it wholesale may be too large; consider wrapping existing builder inside `WorldContext.observe()` initially, then refactor into modular `observe.py`.
- **Telemetry Publisher:** expects rich snapshots (`relationship_snapshot`, `latest_queue_metrics`, etc.). Need to ensure events/snapshot data remain available or provide compatibility layer until WP3.
- **Testing:** golden snapshots and loop smoke tests rely on current shapes. Any structural changes must update fixtures accordingly.
- **ADR alignment:** ADR-002 expects a world package with context façade, modular systems, events, and central RNG. Current analysis confirms feasibility; ensure final design documents deviations (e.g., temporary reuse of `ObservationBuilder`).

## Open Questions
1. Observations: we will retain the existing `ObservationBuilder` for the initial cut by wrapping it inside `WorldContext.observe()`; longer term WP3 will replace this with DTO-driven pipelines. Need to confirm this interim approach keeps telemetry/policy paths stable.
2. Systems ordering: define and document the per-tick order (e.g., console → actions → affordances → employment → relationships → economy → perturbations → nightly reset) and ensure events reflect that sequence.
3. Console migration: in WP2 world should expose event hooks (e.g., `ConsoleEvent`); need a plan for bridging existing console commands until `ConsoleRouter` takes over completely.
4. Telemetry metrics: decide which metrics move to `HealthMonitor` vs remain in snapshot (e.g., queue lengths, rivalry events). Ensure the snapshot structure continues to satisfy telemetry publisher until WP3 replaces it.
5. Persistence/Snapshots: evaluate how snapshot/load flows (currently in `grid.py`) translate to the new `WorldState`/context modules.

## Preliminary Module Mapping
| Legacy Responsibility | Target Module(s) | Notes |
| --- | --- | --- |
| Agent registry & metadata | `agents.py`, `state.py` | `WorldState` owns agent store; `agents.py` exposes management helpers |
| Spatial index / occupancy | `spatial.py` | Provides neighbourhood queries for observations/actions |
| Actions / affordance execution | `actions.py`, `systems/affordances.py` | Validate payloads, update state, emit events |
| Employment, economy, relationships systems | `systems/` submodules | Each implements `step(state, ctx)` |
| Queue conflict tracking | `systems/queues.py` (or integrated with actions) | Must emit queue metrics events |
| RNG management | `rng.py` | Provides seeded generators per subsystem |
| Event emission | `events.py` | Defines event dataclasses & dispatcher |
| Console integration | (removed from world; handled by orchestration) | World emits events/requests only |
| Snapshot/load logic | `state.py`, potential `snapshot.py` helper | Preserve existing persistence semantics |
| Observation assembly | `observe.py` (wrapping legacy builder initially) | Bridges to `ObservationBuilder` until refactor |
| World façade | `context.py` | Implements `WorldRuntime` port |

## Next Steps
- Complete mapping of responsibilities to new modules (update once analysis finishes).
- Finalise strategy for observations/telemetry to avoid blocking on WP3.
- Flesh out implementation plan items with concrete module/function names once design solidified.
