# ADR 0002: World Modularisation

## Status

Accepted

## Context

Townlet's world logic currently lives inside a single god-module (`world/grid.py`) that mixes grid
state, agent bookkeeping, action handling, per-tick systems, telemetry hooks, and randomness.
WP1 created the `WorldRuntime` port so the simulation loop can depend on behaviour contracts. The
port now lives in `townlet.ports.world`; the legacy `WorldRuntimeProtocol` alias in
`townlet.core.interfaces` has been removed.
acting as a deprecated alias during migration), but the concrete world implementation still exposes
sprawling concerns that are hard to test and evolve.
the concrete world implementation still exposes sprawling concerns that are hard to test and evolve.

We need a modular world package that keeps domain responsibilities isolated, emits domain events for
observers such as telemetry, and drives all mutation through a deterministic tick pipeline.

## Decision

- Create `townlet/world/` as the home for world runtime code. The minimum layout is:

  ```
  townlet/world/
    __init__.py
    context.py           # structural WorldRuntime façade
    state.py             # authoritative world state containers
    actions.py           # action schema, validation, apply pipeline
    observe.py           # read-only observation builders
    agents.py            # agent registry and lifecycle helpers
    spatial.py           # grid utilities, neighbourhood lookups
    systems/             # per-tick domain systems (employment, economy, etc.)
      __init__.py
      ...
    events.py            # domain events + dispatcher
    rng.py               # deterministic random helpers
    errors.py            # world-specific exceptions
  ```

- `context.WorldContext` composes these collaborators and provides the methods required by
  `WorldRuntime` (`reset`, `tick`, `agents`, `observe`, `apply_actions`, `snapshot`). Structural
  typing is sufficient; subclassing the protocol is optional.

- The tick pipeline follows a strict order:

  1. Intake actions via `actions.apply(state, actions_map, rng)` (validation + side effects).
  2. Run registered systems (`systems.default_pipeline()` yields callables).
  3. Capture emitted domain events (synchronous dispatch stored on the context).
  4. Increment the tick counter and expose snapshots via `snapshot()`.

- Determinism requirements:

  * `rng.make(seed: int | None)` returns a reproducible RNG.
  * `WorldContext.reset(seed)` creates a fresh state and RNG; identical seeds yield identical
    tick sequences in tests.

- Domain code must not import telemetry, CLI, HTTP, or policy modules. Any non-domain behaviour is
  delegated to adapters layered on top of `WorldRuntime`.

- Provide dummy/test helpers in `townlet/testing/dummies.py` so loop-level tests can exercise the
  modular world without heavy dependencies.
- Observation services now live inside the context (`WorldObservationService`) and wrap
  the legacy builder during migration; adapters should depend on the context API
  rather than constructing `ObservationBuilder` instances directly.


- Register `WorldContext` as the default provider in the world factory (`create_world`). Legacy
  world modules are retired once references are migrated.

## Module Map

```
WorldContext (context.py)
├── WorldState (state.py)
├── RNG (rng.py)
├── Action pipeline (actions.py)
│   └── emits Events (events.py)
├── Systems pipeline (systems/__init__.py)
│   └── individual systems (systems/*.py)
├── Agent registry (agents.py)
├── Spatial utilities (spatial.py)
└── Observations (observe.py)
    └── consumes state/agents/spatial
```

## Tick Pipeline Specification

Each world tick follows a deterministic sequence implemented in `WorldRuntime.tick()` (façade in `world/runtime.py`) which delegates to `WorldContext` (in `world/core/context.py`):

### Pre-Tick Stage
1. **Console Operations**: Apply buffered console commands
   - Commands queued by telemetry/UI via `ConsoleRouter`
   - Execute administrative operations (spawn agents, teleport, adjust needs, etc.)
   - Results captured and returned in `RuntimeStepResult.console_results`

### Lifecycle Stage
2. **Process Respawns**: Replace terminated agents if population is below target
   - Managed by `LifecycleManager`
   - Maintains configured population targets
   - Applies respawn cooldowns and exit caps

### Perturbation Stage
3. **Trigger Events**: Apply scheduled perturbations
   - Price spikes, utility outages, arranged social meets
   - Managed by `PerturbationScheduler`
   - Events expire after configured duration

### Action Stage
4. **Policy Actions**: Apply staged agent actions
   - Actions from `PolicyController.decide()` or direct `action_provider`
   - Validated against world state and agent capabilities
   - Staged via `apply_actions()`, applied during `tick()`

5. **Resolve Affordances**: Process action outcomes
   - Check preconditions (`world/preconditions.py`)
   - Apply state mutations via affordance handlers (`world/affordances/`)
   - Generate side effects and domain events
   - Hot-reloadable from `configs/affordances/core.yaml`

### Daily Reset Stage (Conditional)
6. **Nightly Reset**: Execute daily updates if `tick % ticks_per_day == 0`
   - Economy restocking (food/goods)
   - Utility meter resets (power/water)
   - Employment shift schedule updates
   - Daily exit quota resets

### Lifecycle Evaluation Stage
7. **Evaluate Terminations**: Check agent failure conditions
   - **Collapse**: Needs exceed threshold (> 0.95 for critical needs)
   - **Eviction**: Wallet falls below minimum threshold
   - **Unemployment**: No job assigned + grace period expired
   - Subject to exit caps (max 2/day) and cooldowns (120 ticks)

### Post-Tick Stage
8. **Drain Events**: Collect domain events emitted during tick
   - Events from affordances, lifecycle, employment, relationships
   - Consumed by telemetry for monitoring
   - Cleared after each tick

9. **Return Result**: Package `RuntimeStepResult`
   - `console_results`: Results of executed console commands
   - `events`: Domain events from this tick
   - `actions`: Actions as applied (for debugging)
   - `terminated`: List of terminated agent IDs
   - `termination_reasons`: Dict mapping agent → termination reason

### Data Flow Summary
- **Input**: `console_operations`, `policy_actions` (or `action_provider` callback)
- **Output**: `RuntimeStepResult` (events, terminations, console results)
- **Side Effects**: `WorldState` mutations (agent positions, needs, inventory, etc.)

### Determinism Guarantees
- Three independent RNG streams: `world`, `events`, `policy`
- Seeded from `config_id` for reproducible simulation runs
- All three streams captured in snapshots for deterministic replay

## Consequences

- Smaller modules allow targeted unit tests (spatial math, action validation, system behaviour).
- Telemetry and policy code integrate via ports instead of reaching inside the world.
- Event-driven design enables future features (analytics, back-pressure) without modifying world
  internals.
- Refactors can happen per module (e.g., replacing the spatial grid) without destabilising the tick
  loop contract.
- Old imports must be updated to `townlet.world.context.WorldContext` or the factory; documentation
  and configs need matching updates.

## Actual Package Layout

**Updated**: 2025-10-13 (WP3.2 WS2)

The implemented structure evolved beyond the original specification to provide better organization as subsystems grew:

### Implemented Structure

```
townlet/world/
  __init__.py             # Package exports
  runtime.py              # WorldRuntime façade (main entry point)
  grid.py                 # WorldState (agent snapshots, spatial state)
  state.py                # State store helpers
  actions.py              # Action validation/application
  events.py               # Domain event dispatcher
  employment.py           # Employment subsystem
  relationships.py        # Social relationships
  rivalry.py              # Rivalry intensity tracking
  spatial.py              # Spatial utilities (grid, neighborhoods)
  rng.py                  # Deterministic RNG seeding
  preconditions.py        # Affordance precondition evaluation

  core/                   # Core abstractions
    __init__.py
    context.py            # WorldContext (aggregates systems)
    runtime_adapter.py    # Adapter protocol for world access

  systems/                # Per-tick domain systems
    __init__.py
    affordances.py        # Action affordance resolution
    economy.py            # Economic simulation
    employment.py         # Job/shift management
    perturbations.py      # Event scheduling
    queues.py             # Resource queue management
    relationships.py      # Relationship updates
    base.py               # System protocol

  observations/           # Observation encoding
    __init__.py
    service.py            # WorldObservationService
    encoders/             # Modular encoders
      __init__.py
      map.py              # Map tensor encoding (9×9 local grids)
      features.py         # Feature vector encoding (scalars, needs, etc.)
      social.py           # Social snippet encoding (friends, rivals)
    cache.py              # Spatial caching for performance
    context.py            # Agent observation context
    interfaces.py         # Encoder protocols
    views.py              # Observation view helpers

  affordances/            # Action system
    __init__.py
    runtime.py            # Affordance runtime
    service.py            # Affordance service facade
    core.py               # Core affordance logic

  dto/                    # Data transfer objects
    __init__.py
    observation.py        # Compatibility shim (migrated to townlet/dto/)
    factory.py            # DTO construction helpers

  agents/                 # Agent lifecycle and state
    __init__.py
    registry.py           # Agent registration and lookup
    snapshot.py           # Agent state serialization
    lifecycle/            # Lifecycle management
      __init__.py
      service.py          # LifecycleService
    employment.py         # Employment state tracking
    personality.py        # Personality traits
    relationships_service.py  # Relationship management
    nightly_reset.py      # Daily state resets
    interfaces.py         # Agent protocols

  console/                # Console command integration
    __init__.py
    bridge.py             # Telemetry bridge for console access
    handlers.py           # Console command handlers (world-specific)

  economy/                # Economy subsystem
    __init__.py
    service.py            # EconomyService (pricing, inventory)

  perturbations/          # Perturbation system
    __init__.py
    service.py            # PerturbationService (event scheduling)

  queue/                  # Queue management
    __init__.py
    manager.py            # QueueManager (resource queues)
    conflict.py           # Queue conflict resolution

  hooks/                  # Affordance hooks
    __init__.py
    default.py            # Default hook implementations (shower, sleep, etc.)
```

### Rationale for Deviations

#### 1. Subdirectory Organization

**Planned**: Flat module structure (all files in `world/`)
**Actual**: Hierarchical with `core/`, `systems/`, `observations/`, `affordances/`, `agents/`, etc.

**Rationale**:
- As subsystems grew, flat structure became unwieldy
- Related modules naturally grouped into packages
- Better navigation and discoverability
- Clearer separation of concerns

**Assessment**: Objectively better — easier to navigate, clear module responsibilities

#### 2. observations/ Package

**Planned**: Single `observe.py` module
**Actual**: Full `observations/` package with `encoders/` subdirectory

**Rationale**:
- WP3.1 encoder extraction required modular architecture
- Three observation variants (full, hybrid, compact) need separate encoders
- Encoders are independently testable and composable
- Service layer coordinates encoder invocation

**Assessment**: Objectively better — testable, modular, supports multiple observation variants

#### 3. systems/ Contents

**Planned**: `employment.py`, `relationships.py`, `economy.py`
**Actual**: Also includes `affordances.py`, `perturbations.py`, `queues.py`

**Rationale**:
- Additional domain systems emerged during implementation
- Each system has clear responsibilities and per-tick logic
- Systems follow common protocol (`SystemProtocol`)

**Assessment**: Appropriate — systems are cohesive and well-scoped

#### 4. dto/ Package

**Planned**: Not specified in original WP2
**Actual**: Observation DTOs created here, later migrated to top-level `townlet/dto/`

**Rationale**:
- WP3 DTO work naturally started in world package
- Observation DTOs needed for type safety
- Later migrated to `townlet/dto/observations.py` for cross-module access
- Compatibility shim remains for backward compatibility

**Assessment**: Acceptable — migration completed in WP3, shim provides compatibility

#### 5. affordances/ Package

**Planned**: Single `actions.py` module
**Actual**: Full `affordances/` package with runtime, service, and core logic

**Rationale**:
- Hot-reloadable YAML-based action system required more structure
- Declarative configuration in `configs/affordances/core.yaml`
- Runtime manages active affordance state
- Preconditions evaluated separately (`preconditions.py`)

**Assessment**: Objectively better — declarative, hot-reloadable, maintainable

#### 6. Additional Subdirectories

**Added**: `agents/`, `console/`, `economy/`, `perturbations/`, `queue/`, `hooks/`

**Rationale**:
- Each represents a cohesive subsystem with multiple related modules
- Prevents root-level clutter
- Clear ownership boundaries

**Assessment**: Objectively better — organized, navigable, maintainable

### Architecture Diagram

See `docs/architecture_review/diagrams/world_architecture.md` for visual representation.

## Implementation Notes

- Provide a fixture (or builder) that constructs a tiny deterministic world for tests.
- Maintain a canonical list of registered systems in `systems/__init__.py` to avoid import cycles.
- When serialising snapshots, stick to JSON-safe structures until WP3 introduces DTOs.

## Implementation Status

**Status**: COMPLETE (with architectural improvements)
**Completion Date**: 2025-10-13 (WP3.2 WS2)

### Delivered Components

- ✅ Modular world package in `townlet/world/` with hierarchical organization
- ✅ WorldRuntime façade in `world/runtime.py` (implements `WorldRuntime` port protocol)
- ✅ WorldContext system aggregator in `world/core/context.py`
- ✅ Modular systems package (`systems/`) with per-tick domain systems:
  - Affordances, economy, employment, perturbations, queues, relationships
  - All systems follow `SystemProtocol` contract
- ✅ Modular observations package (`observations/`) with encoder architecture:
  - Map encoder (9×9 local grids)
  - Features encoder (scalars, needs, inventory)
  - Social encoder (friends, rivals, relationships)
  - Observation service coordinating all encoders
- ✅ Affordances runtime with hot-reloadable YAML configuration (`configs/affordances/core.yaml`)
- ✅ Agent lifecycle management (`agents/`) with:
  - Registry, snapshots, employment, personality, relationships
  - Lifecycle service for spawns and terminations
  - Nightly reset for daily state updates
- ✅ Domain event system (`events.py`) with synchronous dispatch
- ✅ Deterministic RNG management (`rng.py`) with three independent streams
- ✅ Console command integration (`console/`) bridging telemetry and world
- ✅ Economy subsystem (`economy/`) with pricing and inventory management
- ✅ Perturbation scheduling (`perturbations/`) for bounded random events
- ✅ Queue management (`queue/`) with conflict resolution
- ✅ Affordance hooks (`hooks/`) with default implementations
- ✅ Comprehensive test coverage:
  - Observation builder tests (full/hybrid/compact variants)
  - System integration tests
  - Affordance runtime tests
  - World runtime tests
  - Deterministic RNG tests
- ✅ Architecture documentation:
  - World architecture diagram (`docs/architecture_review/diagrams/world_architecture.md`)
  - Tick pipeline specification (documented in this ADR)
  - Actual package layout with rationale (documented in this ADR)

### Deviations from Original Specification

The implementation evolved beyond the original WP2 specification in ways that objectively improve the architecture. All deviations are documented in the **"Actual Package Layout"** section above, with detailed rationale and assessment for each.

Key improvements include:
1. **Hierarchical organization** — Subdirectories for related modules instead of flat structure
2. **Modular observations** — Full `observations/` package with composable encoders
3. **Extended systems** — Additional domain systems (affordances, perturbations, queues)
4. **DTO migration** — Observation DTOs created and migrated to `townlet/dto/` for cross-module access
5. **Hot-reloadable affordances** — YAML-based action configuration with runtime reloading
6. **Cohesive subsystems** — agents/, console/, economy/, perturbations/, queue/, hooks/ packages

All deviations enhance modularity, testability, and maintainability without compromising the original architectural intent.

### Verification

- ✅ All world/observation tests passing
- ✅ Type checking clean (`mypy src/townlet/world/`)
- ✅ No circular dependencies
- ✅ WorldRuntime implements port protocol correctly
- ✅ WorldContext aggregates all systems cleanly
- ✅ Observation encoders produce valid DTOs
- ✅ Tick pipeline follows documented 9-stage sequence
- ✅ Three RNG streams maintained independently
- ✅ Domain events dispatched synchronously
- ✅ Affordances hot-reload without restart
- ✅ Architecture diagrams reflect actual implementation
- ✅ ADR-001 (Port and Factory Registry) integration complete
- ✅ ADR-003 (DTO Boundary) extends world observations with typed DTOs

## Related Documents

- `docs/architecture_review/WP_TASKINGS/WP1.md`
- `docs/architecture_review/WP_TASKINGS/WP2.md`
