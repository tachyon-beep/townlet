# WP2 Analysis Notes

_Last updated: 2025-10-09_

## Legacy World Responsibilities (initial pass)
- `world/grid.py`
  - Owns mutable world state (agents, objects, queues, utilities, RNG) and a large set of helper types (`InteractiveObject`, `HookRegistry`, etc.).
  - Handles console integration (`ConsoleService`, history buffers, command handlers).
  - Directly drives affordance runtime, employment services, relationships, economy, perturbations, queue tracking, nightly resets.
  - Exposes snapshot/restore helpers, relationship metrics, rivalry events, policy snapshot metadata, and telemetry-friendly structures.
- `world/runtime.py`
  - Acts as a façade for the simulation loop: queues console ops, applies policy actions, advances tick, emits `RuntimeStepResult` (console results, events, terminated flags).
  - Still depends on `WorldState` from `grid.py` and therefore inherits all the cross-cutting concerns.
- `world/observations/*` & `townlet/observations/builder.py`
  - Builder assembles observation tensors by reaching into world adapters; heavy coupling with grid internals and embedding allocator.
- Telemetry/policy touchpoints
  - Telemetry publisher consumes direct world APIs (`relationship_snapshot`, `queue_manager`, etc.) and calls into world to fetch metrics/events.
  - Policy runtime relies on world adapter for agent snapshots and embedding allocator.

## Key Couplings to Address
- Console: needs to move out of world modules; world should emit events/requests that ConsoleRouter interprets.
- Telemetry: current world exposes many `latest_*` style helpers indirectly (via telemetry publisher). Future design should emit domain events + metrics for orchestration to consume.
- Observations: builder currently lives outside world; decide whether WP2 keeps builder external (and wires `WorldContext.observe()` to call it) or gradually inlines compact features.
- RNG/determinism: world/grid currently owns RNG streams per subsystem; need a centralised `rng.py` to manage seeds and reproducibility paths.

## Dependencies & Risks
- **SimulationLoop:** still uses legacy `WorldRuntime` and expects console buffering and observation builder outputs. WP2 must deliver a `WorldContext` that satisfies `WorldRuntime` port while preserving behaviour until WP3 DTO adoption.
- **Observation Builder:** moving it wholesale may be too large; consider wrapping existing builder inside `WorldContext.observe()` initially, then refactor into modular `observe.py`.
- **Telemetry Publisher:** expects rich snapshots (`relationship_snapshot`, `latest_queue_metrics`, etc.). Need to ensure events/snapshot data remain available or provide compatibility layer until WP3.
- **Testing:** golden snapshots and loop smoke tests rely on current shapes. Any structural changes must update fixtures accordingly.

## Open Questions
1. What minimal observation representation is required for policy/telemetry today? Can we reuse the existing builder to avoid regressions until WP3 introduces DTOs?
2. Which subsystems should be considered “systems” in the new pipeline (employment, economy, perturbations, affordances, stability) and in what order should they run each tick?
3. How will we migrate console handlers? Do we provide a small shim that publishes events for ConsoleRouter until WP3 refactors CLI tooling?
4. How do we transition telemetry metrics that currently read world state via adapters (`queue_manager.metrics()`, etc.)? Do we compute them inside `HealthMonitor`, or expose them via snapshot/events?

## Next Steps
- Complete mapping of responsibilities to new modules (update once analysis finishes).
- Finalise strategy for observations/telemetry to avoid blocking on WP3.
- Flesh out implementation plan items with concrete module/function names once design solidified.
