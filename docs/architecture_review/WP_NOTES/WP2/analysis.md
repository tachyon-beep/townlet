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
| Event emission | `events.py` | Defines event dataclasses & dispatcher; listeners can tap into buffered stream |
| Console integration | (removed from world; handled by orchestration) | World emits events/requests only |
| Snapshot/load logic | `state.py`, potential `snapshot.py` helper | Preserve existing persistence semantics |
| Observation assembly | `observe.py` (wrapping legacy builder initially) | Bridges to `ObservationBuilder` until refactor |
| World façade | `context.py` | Implements `WorldRuntime` port |

## Step 3 audit notes

- Reviewed remaining helpers in `world/grid.py`; most rely on mutable services (employment, queues, lifecycle) and are deferred to Steps 4–6 alongside the wider refactor.
- Formalised the event schema (`events.py`) so later steps can route telemetry/console signals without revisiting stateless plumbing.

## Step 4 design outline

- `agents.py` will offer a `MutableMapping`-compatible `AgentRegistry` that stores rich `AgentRecord` entries (snapshot + created/updated ticks + metadata) while exposing familiar helpers (`add`, `discard`, `values_map`). Callbacks on mutate events will let the world state keep spatial indices/RNG caches in sync.
- `state.py` will host the new `WorldState` dataclass anchored on `SimulationConfig`, seeded RNG state, the `AgentRegistry`, and lightweight context flags (ctx-reset queue, metadata). Convenience methods (`register_agent`, `remove_agent`, `agent_snapshots_view`, `snapshot`) provide the compatibility layer required by the runtime adapter and observation builder until the full `WorldContext` arrives.
- Reset semantics: `WorldState.reset(seed)` re-initialises RNG state, clears agents/objects/metadata, and repopulates deterministic seeds while leaving config untouched. RNG exposure remains via `rng`/`rng_state` helpers so existing deterministic tests can be ported.
- Unit coverage: one suite will target the registry (callbacks, overwrite semantics, immutable views) and another the state container (reset behaviour, ctx-reset queue, snapshot isolation).

## Step 4 progress notes

- `townlet.world.agents.registry.AgentRegistry` now records created/updated ticks plus metadata in `AgentRecord`, exposes read-only views, and retains callback hooks for spatial indexes. Tests: `tests/world/test_agents_registry.py`.
- `townlet.world.state.WorldState` manages RNG seeding/state, ctx-reset queues, event buffering, and serialisable snapshots while delegating agent storage to the new registry. Tests: `tests/world/test_world_state.py`.

## Step 5 design outline

- Define a strict action schema under `townlet.world.actions`: limited kinds (`move`, `request`, `start`, `release`, `chat`, `blocked`, `noop`) captured by an `ActionKind` Literal and an `Action` dataclass (`agent_id`, `kind`, `payload`, optional `duration`).
- Validation will normalise raw payloads, enforce required keys (e.g., `position` for `move`, `object` for queue/affordance interactions, `target` for `chat`), clamp numeric fields, and emit `ActionValidationError` with actionable messages.
- The application pipeline will operate in four stages: validate → resolve targets (future integration point for queue/affordance systems) → mutate world state (e.g., update agent position, last-action metadata) → emit domain events via `WorldState.emit_event`. For non-yet-implemented kinds we’ll emit `action.pending` events so later steps can hook in concrete mutations.
- Unit coverage will include: validation success/failure cases, safe handling of unknown agents, mutation side effects (position/last-action updates), and event payload integrity.

## Step 5 progress notes

- Implemented `Action`, `ActionValidationError`, and normalisation helpers in `townlet.world.actions`, covering supported kinds with payload coercion and detailed error messaging.
- `apply_actions` now updates agent snapshots/records for implemented kinds (`move`, `noop`), emits structured events (including invalid/pending markers), and defers richer mutations to upcoming systems. Tests: `tests/world/test_actions.py`.

## Step 6 outcomes (systems & orchestration)

- `SystemContext` and the RNG stream manager (`RngStreamManager`) orchestrate queues → affordances → employment → relationships → economy → perturbations for every tick. Each system module delegates to the existing services while emitting structured events via the shared dispatcher.
- `world.actions.apply_actions` now operates on the shared action schema, updates agent records, and emits `action.*` events consumed by downstream telemetry/tests.
- The legacy `WorldState` gained the port-friendly surface (`agent_records_view`, `emit_event`, `event_dispatcher`, `rng_seed`), allowing both the modular context and existing consumers to observe consistent state.
- Unit suites under `tests/world/test_systems_*.py` exercise the helper functions, while `tests/test_world_context.py` validates end-to-end tick execution, console routing, nightly reset delegation, and action application.
- `WorldRuntime.tick` recognises the modular result object, so the simulation loop can continue using the legacy runtime while the new facade is incrementally adopted.

## Step 7 design outline (WorldContext orchestration & factories)

- WorldContext will own the active `WorldState`, a `RngStreamManager`, the action dispatcher (wrapping `world.actions`), and an ordered tuple of system steps returned by `systems.default_systems()` (queues → affordances → employment → relationships → economy → perturbations).
- `reset()` will reseed RNG streams, clear action queues, call `state.reset(seed)` and prime systems (e.g., rebuild spatial index, refresh reservations).
- `apply_actions()` will validate/normalise inputs via `actions.validate_actions`, emit invalid events, and enqueue the resulting actions for execution in the next `tick()`.
- `tick()` will perform: drain pending console commands, apply validated actions via `actions.apply_actions`, execute system steps in order, process nightly reset cadence, emit domain events, and return a structured snapshot for telemetry.
- Tests: unit tests mocking individual system delegates to assert call ordering, plus an integration smoke test that runs a mini tick (console → actions → systems) and verifies events/RNG determinism.
- Extract domain systems from `world/grid.py` into focused modules under `townlet.world.systems`:
  - `queues` — wrap `QueueManager`, `QueueConflictTracker`, reservation syncing, and queue metrics/event emission.
  - `affordances` — coordinate start/release/resolve via `AffordanceRuntimeService`, exposing hooks to record need decay, reservation state, and instrumentation flags.
  - `employment` — handle job assignment, shift transitions, nightly reset triggers (glue around `EmploymentService`/`LifecycleService`).
  - `relationships` — expose rivalry/relationship updates, decay, and telemetry snapshots.
  - `economy`/`perturbations` — capture price targets, basket metrics, and perturbation scheduling (may co-locate if tightly coupled).
- Introduce a lightweight orchestration context (`SystemContext` struct) carried through system steps, giving access to RNG streams, event dispatcher, action outcomes, and shared caches.
- Implement `townlet.world.rng` utilities to manage named RNG streams per system (e.g., `rng.pick("affordances")`) seeded from `WorldState`.
- Flesh out `WorldContext` to own `WorldState`, system instances, action pipeline wiring, and tick sequencing (`reset`, `apply_actions`, `tick`, `snapshot`, `observe`), ensuring ordering matches ADR-002 (console → policy actions → systems → events → nightly reset).
- Unit and integration coverage:
  - Per-system unit tests for deterministic behaviour (e.g., queue reservations, affordance start success, employment shift transitions with stub state).
  - `WorldContext` tick smoke test verifying system order, event emission, and world state transitions given a minimal configuration stub.
- Migration plan:
  - Phase 1: extract pure helpers/state resets into new modules with shims in `grid.py` (world continues to delegate).
  - Phase 2: rewire legacy methods (`apply_actions`, `resolve_affordances`, `apply_nightly_reset`, etc.) to call the new system modules.
  - Phase 3: finalise `WorldContext` implementation and update factories to instantiate it instead of the legacy runtime.
- Remaining legacy touchpoints to port:
  - **Queues** (`grid.py:821-979`): action handling for `request/blocked`, `_sync_reservation`, `_record_queue_conflict`, chat success/failure events, rivalry conflict registration, queue manager snapshots.
  - **Affordances** (`grid.py:825-915`, `grid.py:1248-1287`): runtime `start/release/handle_blocked`, need decay via `_apply_affordance_effects`, manifest loading.
  - **Relationships** (`grid.py:1080-1204`): relationship updates, rivalry ledgers, chat event integration, guard blocks.
  - **Employment** (`grid.py:1365-1486`): nightly reset integration, job assignment, employment service context helpers, shift state transitions, exit tracking.
  - **Economy/Perturbations** (`grid.py:1483-1536`): basket metrics, restocking, price spikes, utility outages, arranged meets, economy snapshots.
  - **Nightly reset** (`grid.py:396-450`, `grid.py:1365-1376`): service wiring, apply/reset sequences.

- Established foundational scaffolding: `SystemContext`, named RNG streams (`RngStreamManager`), and system modules under `townlet.world.systems` now exercised by the world context and unit suites.

## Next Steps

- Catalogue the remaining legacy system functions that still call directly into `world/grid.py` and plan the factory/world-provider swap (WP1 Step 4 resumption).
- Identify migration steps for factories and the simulation loop so `WorldContext` becomes the default provider (move away from compatibility shims).
- Begin documenting the event schema and RNG stream usage so downstream consumers (telemetry, console router, health monitor) can adopt the modular surface without relying on legacy getters.
