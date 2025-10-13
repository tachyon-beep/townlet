# World Package Architecture

This diagram shows the actual implemented structure of the `townlet/world/` package following WP2 (World Modularisation).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SimulationLoop                       │
│                   (orchestrates)                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              WorldRuntime (façade)                      │
│         src/townlet/world/runtime.py                    │
│                                                         │
│  Methods:                                               │
│  - tick(console_ops, actions) → RuntimeStepResult      │
│  - observe() → ObservationEnvelope                     │
│  - agents() → Iterable[str]                            │
│  - snapshot() → SnapshotState                          │
└────────────┬────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────┐
             │                                             │
             ▼                                             ▼
┌─────────────────────────┐              ┌─────────────────────────┐
│     WorldContext         │              │      WorldState        │
│  world/core/context.py   │              │   world/grid.py        │
│                          │              │                         │
│  - Aggregates systems    │              │  - Agent snapshots     │
│  - Coordinates tick      │              │  - Grid/spatial        │
│  - Builds observations   │              │  - Relationships       │
└────────┬─────────────────┘              │  - Employment          │
         │                                │  - Economy             │
         │                                └────────────────────────┘
         │
         ├────────────────┬────────────────┬──────────────┐
         │                │                │              │
         ▼                ▼                ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│   Systems    │ │ Observations │ │ Affordances │ │   Actions    │
│  systems/    │ │ observations/│ │affordances/ │ │  actions.py  │
│              │ │              │ │             │ │              │
│ • employment │ │ • encoders/  │ │ • runtime   │ │ • validation │
│ • economy    │ │   - map      │ │ • handlers  │ │ • apply      │
│ • relations  │ │   - features │ │             │ │              │
│ • queues     │ │   - social   │ │             │ │              │
│ • perturb    │ │ • service    │ │             │ │              │
└──────────────┘ └──────────────┘ └─────────────┘ └──────────────┘
```

## Package Structure

```
townlet/world/
  runtime.py              # WorldRuntime façade (main entry point)
  grid.py                 # WorldState (agent snapshots, spatial, etc.)
  state.py                # State store helpers
  actions.py              # Action validation/application
  events.py               # Domain event dispatcher
  employment.py           # Employment subsystem
  relationships.py        # Social relationships
  rivalry.py              # Rivalry tracking
  spatial.py              # Spatial utilities
  rng.py                  # RNG seeding and management

  core/                   # Core abstractions
    context.py            # WorldContext (aggregates systems)
    runtime_adapter.py    # Adapter protocol for world access

  systems/                # Per-tick domain systems
    affordances.py        # Action affordance resolution
    economy.py            # Economic simulation
    employment.py         # Job/shift management
    perturbations.py      # Event scheduling
    queues.py             # Resource queue management
    relationships.py      # Relationship updates
    base.py               # System protocol

  observations/           # Observation encoding
    service.py            # WorldObservationService
    encoders/             # Modular encoders
      map.py              # Map tensor encoding
      features.py         # Feature vector encoding
      social.py           # Social snippet encoding
    cache.py              # Spatial caching
    context.py            # Agent observation context
    interfaces.py         # Encoder protocols
    views.py              # Observation view helpers

  affordances/            # Action system
    runtime.py            # Affordance runtime
    service.py            # Affordance service facade
    core.py               # Core affordance logic

  dto/                    # Data transfer objects (migrated to townlet/dto/)
    observation.py        # ObservationEnvelope, AgentObservationDTO (compatibility shim)
    factory.py            # DTO construction helpers

  agents/                 # Agent lifecycle
    registry.py           # Agent registration and lookup
    snapshot.py           # Agent state serialization
    lifecycle/            # Lifecycle management
      service.py          # Lifecycle service
    employment.py         # Employment state
    personality.py        # Personality traits
    relationships_service.py  # Relationship management
    nightly_reset.py      # Daily state resets

  console/                # Console command integration
    bridge.py             # Telemetry bridge for console
    handlers.py           # Console command handlers

  economy/                # Economy subsystem
    service.py            # Economy simulation service

  perturbations/          # Perturbation system
    service.py            # Perturbation scheduling service

  queue/                  # Queue management
    manager.py            # Queue manager
    conflict.py           # Queue conflict resolution

  hooks/                  # Affordance hooks
    default.py            # Default hook implementations
```

## Key Design Patterns

### Façade Pattern
- `WorldRuntime` acts as a façade, providing a simplified interface to the complex world subsystem
- Hides internal complexity from SimulationLoop
- Coordinates tick sequencing and state management

### System Aggregation
- `WorldContext` aggregates domain systems (employment, economy, relationships, etc.)
- Each system is responsible for a specific domain concern
- Systems are invoked during tick processing in a specific order

### Modular Observations
- Observation encoding is decomposed into modular encoders (map, features, social)
- Each encoder focuses on a specific aspect of observations
- Encoders are combined by `WorldObservationService`

### DTO Boundaries
- Observations cross boundaries as `ObservationEnvelope` DTOs
- World snapshots use typed DTOs from `townlet/dto/`
- Internal state remains in domain objects

## Data Flow

### Tick Sequence
1. SimulationLoop calls `WorldRuntime.tick()`
2. WorldRuntime applies console operations
3. WorldRuntime applies policy actions
4. WorldRuntime delegates to WorldContext for domain logic
5. WorldContext invokes systems in order:
   - Lifecycle (respawns)
   - Perturbations (events)
   - Actions/Affordances (agent actions)
   - Daily reset (if tick % ticks_per_day == 0)
   - Lifecycle evaluation (terminations)
6. WorldRuntime collects events and returns RuntimeStepResult

### Observation Flow
1. SimulationLoop calls `WorldRuntime.observe()`
2. WorldRuntime delegates to WorldContext
3. WorldContext uses `WorldObservationService`
4. ObservationService invokes encoders (map, features, social)
5. Encoders access WorldState through context
6. ObservationService builds ObservationEnvelope DTO
7. DTO returned to SimulationLoop

## Related Documents

- `ADR-002: World Modularisation` - Architectural decision record
- `WP2.md` - Work package tasking and requirements
- `ADR-001: Port and Factory Registry` - Port protocol definitions
- `ADR-003: DTO Boundary` - Typed DTO boundaries
