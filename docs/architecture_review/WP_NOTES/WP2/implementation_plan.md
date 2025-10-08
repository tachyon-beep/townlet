# WP2 Implementation Plan — World Modularisation

This plan breaks down Work Package 2 into concrete steps. Update it as tasks complete.

## 0. Prerequisites
- WP1 ports/adapters/factories scaffolding in place (done).
- Simulation loop still uses legacy world runtime; Step 4 in WP1 is deferred until WP2 delivers the new world context.

## 1. Deep-dive & Design (analysis phase)
1.1. Catalogue responsibilities in `townlet/world/grid.py`, `world/runtime.py`, `world/observations/*`, console hooks, telemetry hooks, RNG, persistence.
1.2. Document interactions with external systems (simulation loop, observation builder, telemetry publisher, policy runtime).
1.3. Confirm ADR-002 expectations (module boundaries, event model, RNG policy) and reconcile with current behaviour.
1.4. Decide a migration strategy for observations: retain existing ObservationBuilder temporarily and bridge into `observe.py`, or reimplement the minimal required view.
1.5. Produce a target module map (state, spatial, agents, actions, systems, events, rng) and map each current responsibility to a destination.

## 2. Package Skeleton & Types
2.1. Create `townlet/world/` submodules (`__init__`, `context.py`, `state.py`, `spatial.py`, `agents.py`, `actions.py`, `observe.py`, `events.py`, `rng.py`, `systems/__init__.py`).
2.2. Define public types (dataclasses, protocols, type aliases) and export minimal placeholders so imports compile.
2.3. Add basic unit test placeholders to ensure package loads successfully (focus on import cycles).

## 3. Extract Stateless/Pure Components
3.1. Move spatial helpers and geometry calculations into `spatial.py`; write unit tests covering neighbourhood queries, bounds, occupancy logic.
3.2. Extract observation assembly logic that does not mutate state into `observe.py`; create fixtures mirroring existing observation builder outputs for a tiny world.
3.3. Introduce `events.py` with dataclasses/Enum for domain events and a simple dispatcher interface.

## 4. Build Core State & Agent Management
4.1. Implement `WorldState` dataclass (tick, RNG seeds, registries) plus methods for reset/load/snapshot in `state.py`.
4.2. Create `agents.py` to handle add/remove/lookup logic; ensure tests cover uniqueness and update semantics.
4.3. Thread `WorldState` ownership through existing world runtime to prepare for replacement.

## 5. Action Pipeline
5.1. Define action schema/validation in `actions.py` (accepting dict payloads for now, upgradeable to DTOs later).
5.2. Implement the apply pipeline (validate → resolve → mutate state → emit events).
5.3. Add unit tests covering valid/invalid actions and resulting state changes.

## 6. Systems & Tick Orchestration
6.1. For each domain system (employment, relationships, economy, queues, perturbations) create a module under `systems/` with a `step(state, ctx)` signature.
6.2. Implement `rng.py` providing seeded RNG builders and helper utilities.
6.3. Assemble `WorldContext` in `context.py`: holds `WorldState`, RNG, registered systems, exposes `reset/tick/agents/observe/apply_actions/snapshot` per `WorldRuntime` protocol.
6.4. Ensure `tick()` emits events via the dispatcher and returns a serialisable snapshot.

## 7. Adapter & Factory Integration
7.1. Update `DefaultWorldAdapter` (from WP1) to wrap the new `WorldContext` instead of the legacy runtime.
7.2. Update `world_factory` so `create_world()` constructs `WorldContext.from_config(...)` and registers providers accordingly.
7.3. Provide compatibility shims for legacy world usage (tests, CLI) until the simulation loop is refactored in Step 8.

## 8. Composition Root & Loop Update
8.1. Revive WP1 Step 4: modify `SimulationLoop` and helpers to use `create_world` and interact strictly via the port (`WorldRuntime` methods).
8.2. Integrate `ConsoleRouter` and `HealthMonitor` in a minimal viable form: world emits events; router/monitor consume them without relying on telemetry getters.
8.3. Update helper utilities (`policy_provider_name`, etc.) to the new provider plumbing.
8.4. Ensure backward compatibility for console/telemetry flows during transition (e.g., maintain legacy APIs until WP3 DTO adoption).

## 9. Cleanup & Legacy Removal
9.1. Deprecate and remove obsolete modules (`world/grid.py`, `world/runtime.py`, etc.) or turn them into thin shims pointing to the new package.
9.2. Update imports across the codebase to the new module locations.
9.3. Ensure build/test scripts, configs, and docs reference `townlet.world.*` instead of legacy modules.

## 10. Testing & Documentation
10.1. Implement unit tests for each new module (spatial, agents, actions, systems, rng, observe).
10.2. Add integration tests: deterministic small world run, event emission checks, world snapshot round-trips.
10.3. Update existing tests (observation builder, telemetry, loop smoke tests) to work with the new structure.
10.4. Refresh ADR-002 with final module map, event schema, determinism policy, migration notes.
10.5. Update developer docs/README/architecture review to explain the new world package and orchestration flow.

## 11. Quality Gates & Final Verification
11.1. Run `ruff` and `mypy` over new/changed modules; add mypy overrides where necessary.
11.2. Run the full pytest suite (including golden snapshot tests) to confirm regression-free behaviour.
11.3. Prepare change summary documenting remaining TODOs (e.g., DTO adoption in WP3).

Keep this plan updated as work progresses.
