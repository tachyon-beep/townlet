# World Package Architecture

**Created**: 2025-10-14
**Status**: ✅ COMPLETE
**Phase**: WP4.1 Phase 3 (Documentation)

---

## Executive Summary

This document provides a comprehensive architectural overview of the `townlet/world/` package, including module relationships, tick pipeline flow, and system responsibilities.

**Package Stats**:
- **72 Python modules** across 14 subdirectories
- **8 domain systems** (affordances, economy, employment, perturbations, queues, relationships)
- **3 observation encoders** (map, features, social)
- **13 services** aggregated in WorldContext

---

## Module Relationship Diagram

```
                    ┌──────────────────────────────────────┐
                    │      SimulationLoop (core/)          │
                    │  Orchestrates sim tick sequence      │
                    └──────────────┬───────────────────────┘
                                   │ uses (via port)
                                   ▼
                    ┌──────────────────────────────────────┐
                    │   WorldRuntime Protocol (ports/)     │
                    │  Defines contract (minimal surface)  │
                    └──────────────┬───────────────────────┘
                                   │ implemented by
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  WorldRuntime Façade (world/runtime.py)             │
│  • Stateful coordination                                            │
│  • Buffers console ops + policy actions                             │
│  • Implements port protocol methods                                 │
│  • Delegates to WorldContext                                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │ delegates to
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              WorldContext Aggregator (world/core/context.py)        │
│  • Aggregates 13 domain services                                    │
│  • Orchestrates tick pipeline                                       │
│  • Builds observation envelopes (DTOs)                              │
│  • Manages RNG streams                                              │
└─────────────┬───────────────────────────────────────────────────────┘
              │ coordinates
              │
      ┌───────┴───────┬───────────┬───────────┬───────────┬───────────┐
      │               │           │           │           │           │
      ▼               ▼           ▼           ▼           ▼           ▼
┌──────────┐   ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐
│  Queue   │   │Affordance│ │Lifecycle│ │Employment│ │Relations│ │Economy │
│ Manager  │   │ Service  │ │ Service │ │  Coord  │ │ Service │ │Service │
└──────────┘   └──────────┘ └─────────┘ └─────────┘ └─────────┘ └────────┘
      │               │           │           │           │           │
      └───────────────┴───────────┴───────────┴───────────┴───────────┘
                                   │ all operate on
                                   ▼
                    ┌──────────────────────────────────────┐
                    │     WorldState (world/grid.py)       │
                    │  • Agent snapshots (position, needs) │
                    │  • Spatial grid (48×48 tiles)        │
                    │  • Objects (fridges, beds, etc.)     │
                    │  • Economy state (prices, inventory) │
                    │  • Employment records                │
                    │  • Relationship graph                │
                    └──────────────┬───────────────────────┘
                                   │ wrapped by
                                   ▼
                    ┌──────────────────────────────────────┐
                    │  WorldRuntimeAdapter (core/)         │
                    │  Read-only view for observations     │
                    └──────────────┬───────────────────────┘
                                   │ used by
                                   ▼
                    ┌──────────────────────────────────────┐
                    │   ObservationService (observations/) │
                    │  • Coordinates encoder invocation    │
                    │  • Builds ObservationEnvelope DTOs   │
                    └──────────────┬───────────────────────┘
                                   │ delegates to
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
         ┌─────────────┐    ┌─────────────┐   ┌─────────────┐
         │ MapEncoder  │    │FeaturesEnc  │   │SocialEncoder│
         │ (9×9 tiles) │    │(scalars)    │   │(friends)    │
         └─────────────┘    └─────────────┘   └─────────────┘
```

---

## Tick Pipeline Data Flow

Each simulation tick follows a 9-stage pipeline implemented by `WorldContext.tick()`:

```
┌────────────────────────────────────────────────────────────────────┐
│ TICK N                                                             │
└────────────────────────────────────────────────────────────────────┘
   │
   ├─► [1] Console Operations
   │     └─ Apply buffered commands (spawn, teleport, etc.)
   │        → WorldContext.console.apply(console_operations)
   │        → Returns: console_results
   │
   ├─► [2] Lifecycle Spawns
   │     └─ Replace terminated agents (population maintenance)
   │        → LifecycleManager.process_respawns(world, tick)
   │        → Respects cooldowns (120 ticks) and exit caps (2/day)
   │
   ├─► [3] Perturbations
   │     └─ Trigger scheduled events (price spikes, outages, meets)
   │        → PerturbationScheduler.tick(world, tick)
   │        → Events expire after duration
   │
   ├─► [4] Policy Actions
   │     └─ Stage actions from policy backend
   │        → action_provider(world, tick) → actions_map
   │        → Validation against agent capabilities
   │
   ├─► [5] Affordance Resolution
   │     └─ Execute actions via affordance system
   │        → AffordanceSystem.process_actions(state, actions, rng)
   │        → Precondition checks → Handler execution → Side effects
   │        → Hot-reloadable from configs/affordances/core.yaml
   │
   ├─► [6] Nightly Reset (conditional: tick % ticks_per_day == 0)
   │     └─ Daily economy/utility updates
   │        → NightlyResetService.apply(world)
   │        → Restock inventory, reset meters, update shifts
   │
   ├─► [7] Lifecycle Evaluation
   │     └─ Check termination conditions
   │        → LifecycleManager.evaluate(world, tick)
   │        → Collapse (needs > 0.95) / Eviction (wallet < min) / Unemployment
   │        → Returns: terminated, termination_reasons
   │
   ├─► [8] Domain Events
   │     └─ Collect events emitted during tick
   │        → world.drain_events()
   │        → Returns: events (for telemetry)
   │
   └─► [9] Return Result
         └─ Package RuntimeStepResult
            → console_results, events, actions, terminated, termination_reasons
```

### Data Flow Summary

**Inputs**:
- `tick: int` — Current simulation tick
- `console_operations: list[ConsoleCommandEnvelope]` — Buffered console commands
- `prepared_actions: dict[str, object]` — Policy actions for agents

**Outputs**:
- `RuntimeStepResult`:
  - `console_results: list[ConsoleCommandResult]` — Console command outcomes
  - `events: list[dict[str, object]]` — Domain events from subsystems
  - `actions: dict[str, object]` — Applied actions (for debugging)
  - `terminated: dict[str, bool]` — Terminated agent IDs
  - `termination_reasons: dict[str, str]` — Termination causes

**Side Effects**:
- `WorldState` mutations (agent positions, needs, inventory, relationships, etc.)
- RNG stream advancement (deterministic)
- Event emission (synchronous dispatch)

---

## System Responsibilities

The world package is organized into domain systems, each responsible for a specific aspect of the simulation:

| System | Module | Purpose | Key Operations |
|--------|--------|---------|----------------|
| **Affordances** | `systems/affordances.py` | Action resolution | Validate preconditions, execute handlers, track outcomes |
| **Economy** | `systems/economy.py` | Economic state | Pricing updates, inventory management, supply/demand |
| **Employment** | `systems/employment.py` | Job tracking | Shift windows, punctuality scoring, wage calculation |
| **Perturbations** | `systems/perturbations.py` | Event scheduling | Schedule price spikes, outages, arranged meets |
| **Queues** | `systems/queues.py` | Resource management | Queue rotation, ghost steps, cooldowns, conflict detection |
| **Relationships** | `systems/relationships.py` | Social dynamics | Trust decay, familiarity growth, rivalry intensity |

### System Protocol

All systems implement a common `SystemStep` protocol ([systems/base.py:25-42](../../../src/townlet/world/systems/base.py#L25-L42)):

```python
class SystemStep(Protocol):
    """Protocol for per-tick world systems."""

    def __call__(self, ctx: SystemContext) -> None:
        """Execute this system's tick logic."""
        ...
```

**SystemContext** provides:
- `state: ModularWorldState` — Mutable world state
- `rng: RngStreamManager` — Deterministic RNG streams
- `events: EventDispatcher` — Event emission sink

This protocol enables:
- **Composability**: Systems can be added/removed from pipeline
- **Testability**: Each system testable in isolation
- **Determinism**: RNG passed explicitly, not global state

---

## Package Structure (Detailed)

### Core Modules (Top-Level)

```
world/
├── runtime.py              # WorldRuntime façade (main entry point)
├── grid.py                 # WorldState (agent snapshots, spatial state)
├── state.py                # State store helpers
├── actions.py              # Action validation/application
├── events.py               # Domain event dispatcher
├── employment.py           # Employment subsystem (legacy, being refactored)
├── relationships.py        # Social relationships
├── rivalry.py              # Rivalry intensity tracking
├── spatial.py              # Spatial utilities (grid, neighborhoods)
├── rng.py                  # Deterministic RNG seeding
├── preconditions.py        # Affordance precondition evaluation
```

**Key files**:
- `runtime.py` — Implements `WorldRuntime` port protocol, delegates to `WorldContext`
- `grid.py` — 2700+ lines, core world state (target for future refactoring)
- `events.py` — Synchronous event dispatcher for telemetry integration

### core/ — Core Abstractions

```
core/
├── context.py              # WorldContext (aggregates 13 services)
└── runtime_adapter.py      # Read-only adapter for observations
```

**WorldContext** ([context.py:48-495](../../../src/townlet/world/core/context.py#L48-L495)):
- Aggregates: QueueManager, AffordanceService, 3× Employment services, LifecycleService, RelationshipService, EconomyService, PerturbationService, ConsoleService
- Orchestrates tick pipeline
- Builds observation envelopes
- Manages RNG streams (world, events, policy)

### systems/ — Domain Systems

```
systems/
├── base.py                 # SystemProtocol, SystemContext
├── affordances.py          # Action affordance resolution
├── economy.py              # Economic simulation
├── employment.py           # Job/shift management
├── perturbations.py        # Event scheduling
├── queues.py               # Resource queue management
└── relationships.py        # Relationship updates
```

All systems implement `SystemStep` protocol and receive `SystemContext` each tick.

### observations/ — Observation Encoding

```
observations/
├── service.py              # WorldObservationService (coordinator)
├── cache.py                # Spatial caching for performance
├── context.py              # Agent observation context
├── interfaces.py           # Encoder protocols
├── views.py                # Observation view helpers
└── encoders/
    ├── map.py              # Map tensor encoding (9×9 local grids)
    ├── features.py         # Feature vector encoding (scalars, needs)
    └── social.py           # Social snippet encoding (friends, rivals)
```

**Observation Variants**:
- **Full**: 9×9 map + scalars + social snippet (~500-800 floats)
- **Hybrid**: Slimmer map with directional fields to key targets
- **Compact**: No map; distilled vectors only (distances, bearings, flags)

Variant selection is baked into `config_id` and policy hash.

### affordances/ — Action System

```
affordances/
├── core.py                 # Core affordance logic
├── runtime.py              # Affordance runtime (state management)
└── service.py              # Affordance service façade
```

**Hot-Reloadable**: Actions defined in `configs/affordances/core.yaml`
**Declarative**: YAML schema defines preconditions, handlers, duration, cooldowns

### agents/ — Agent Lifecycle

```
agents/
├── registry.py             # Agent registration and lookup
├── snapshot.py             # Agent state serialization (Pydantic)
├── employment.py           # Employment state tracking
├── personality.py          # Personality traits
├── relationships_service.py # Relationship management
├── nightly_reset.py        # Daily state resets
├── interfaces.py           # Agent protocols
└── lifecycle/
    └── service.py          # LifecycleService (spawns, terminations)
```

**AgentSnapshot** ([agents/snapshot.py:18-61](../../../src/townlet/world/agents/snapshot.py#L18-L61)):
- Pydantic model capturing agent state
- Fields: agent_id, position, needs, wallet, job, relationships, inventory

### console/ — Console Command Integration

```
console/
├── bridge.py               # Telemetry bridge for console access
└── handlers.py             # Console command handlers (world-specific)
```

**Console commands**: spawn, teleport, adjust_needs, set_wallet, arrange_meet, etc.
**Buffering**: Commands queued by telemetry, applied each tick

### economy/ — Economy Subsystem

```
economy/
└── service.py              # EconomyService (pricing, inventory)
```

**Responsibilities**: Item pricing, inventory restocking, supply/demand simulation

### perturbations/ — Perturbation Scheduling

```
perturbations/
└── service.py              # PerturbationService (event scheduling)
```

**Event types**: Price spikes, blackouts, water outages, arranged meets
**Fairness**: Bounded event frequency, cooldowns, suppression during city-wide events

### queue/ — Queue Management

```
queue/
├── manager.py              # QueueManager (resource queues)
└── conflict.py             # Queue conflict resolution
```

**Queue rotation**: Ghost steps, cooldowns, conflict detection
**Resources**: Fridges, beds, showers, toilets

### hooks/ — Affordance Hooks

```
hooks/
└── default.py              # Default hook implementations
```

**Hook examples**: shower (hygiene +0.2), sleep (energy +0.3), eat (hunger -0.4)

### dto/ — Data Transfer Objects

```
dto/
├── factory.py              # DTO construction helpers
└── observation.py          # Compatibility shim (migrated to townlet/dto/)
```

**Note**: Observation DTOs migrated to top-level `townlet/dto/observations.py` in WP3.

---

## Module Count by Subsystem

| Subsystem | Files | Purpose |
|-----------|-------|---------|
| **Core** | 11 | Runtime, state, actions, events, spatial, RNG |
| **Systems** | 7 | Domain tick pipeline systems |
| **Observations** | 9 | Observation encoding (service + 3 encoders) |
| **Affordances** | 3 | Action system |
| **Agents** | 9 | Agent lifecycle, employment, relationships |
| **Console** | 2 | Console command integration |
| **Economy** | 1 | Economic simulation |
| **Perturbations** | 1 | Event scheduling |
| **Queues** | 2 | Resource queue management |
| **Hooks** | 1 | Affordance handler implementations |
| **DTO** | 2 | Data transfer objects |
| **Legacy** | 24 | Top-level modules (some being refactored) |
| **Total** | **72** | Complete world package |

---

## Determinism Guarantees

The world package maintains **three independent RNG streams** for reproducibility:

1. **`world`** — World state updates (decay, economy, spatial)
2. **`events`** — Perturbation scheduler (event timing, targets)
3. **`policy`** — Policy decisions (epsilon-greedy, action selection)

**Seeding**:
- Derived from `config_id` via `SimulationLoop._derive_seed()` ([sim_loop.py:1541](../../../src/townlet/core/sim_loop.py#L1541))
- Each stream seeded independently: `world_seed = base_seed`, `events_seed = base_seed + 1`, `policy_seed = base_seed + 2`

**Snapshot Integration**:
- All three RNG streams captured in snapshots
- `RngStreamManager` serializes/deserializes RNG state
- Deterministic replay: Load snapshot → restore RNG streams → resume tick

**Testing**:
- `tests/test_utils_rng.py` validates RNG determinism
- `tests/test_sim_loop_snapshot.py` validates snapshot round-trip

---

## Design Patterns

### 1. Port-and-Adapter Pattern

**WorldRuntime Protocol** (port) → **WorldRuntime Concrete** (adapter) → **WorldContext** (implementation)

Benefits:
- Dependency inversion (SimulationLoop depends on abstraction)
- Testability (can inject stub/mock implementations)
- Swappable backends (default, dummy, scripted)

### 2. Façade Pattern

**WorldRuntime** hides complexity of WorldContext and subsystems behind simple interface:
- `tick()` — Advance simulation
- `observe()` — Get observations
- `apply_actions()` — Stage actions
- `snapshot()` — Capture state

### 3. Aggregator Pattern

**WorldContext** aggregates 13 services and coordinates their interactions:
- No circular dependencies
- Each service owns its domain
- Context mediates cross-service communication

### 4. Strategy Pattern

**ObservationService** coordinates encoder invocation based on configured variant:
- **full** → MapEncoder + FeaturesEncoder + SocialEncoder
- **hybrid** → MapEncoder (slim) + FeaturesEncoder + SocialEncoder
- **compact** → FeaturesEncoder (distilled) only

### 5. Command Pattern

**Console commands** encapsulated as `ConsoleCommandEnvelope` objects:
- Buffered by telemetry
- Validated before execution
- Results captured in `ConsoleCommandResult`

### 6. Observer Pattern

**Domain events** emitted via `EventDispatcher`:
- Subsystems emit events (action.executed, agent.terminated, etc.)
- Telemetry observes events
- Synchronous dispatch (no async complexity)

---

## Evolution from Original Spec

ADR-002 originally specified a **flat structure**:

```
world/
  context.py           # WorldRuntime façade
  state.py             # State store
  spatial.py           # Grid operations
  agents.py            # Agent lifecycle
  actions.py           # Action validation
  observe.py           # Observation views
  systems/             # Domain systems
  events.py            # Domain events
  rng.py               # RNG streams
```

**Actual implementation** evolved into **hierarchical structure** with 14 subdirectories:

**Why better**:
1. **Scalability**: Flat structure became unwieldy as subsystems grew
2. **Discoverability**: Related modules grouped by domain
3. **Testability**: Each package independently testable
4. **Modularity**: Clear boundaries between subsystems
5. **Maintainability**: Easier navigation for contributors

All deviations documented in [ADR-002:270-344](../../../docs/architecture_review/ADR/ADR-002%20-%20World%20Modularisation.md#L270-L344).

---

## Related Documents

- [ADR-001: Port and Factory Registry](../../ADR/ADR-001%20-%20Port%20and%20Factory%20Registry.md) — Port protocol pattern
- [ADR-002: World Modularisation](../../ADR/ADR-002%20-%20World%20Modularisation.md) — World package specification
- [ADR-003: DTO Boundary](../../ADR/ADR-003%20-%20DTO%20Boundary.md) — DTO enforcement at boundaries
- [CONTEXT_RUNTIME_RECONCILIATION.md](./CONTEXT_RUNTIME_RECONCILIATION.md) — Runtime/Context architecture analysis
- [CLAUDE.md](../../../../CLAUDE.md) — Development guide with world package overview

---

## Acceptance Criteria

- ✅ Complete package structure documented (72 modules, 14 subdirectories)
- ✅ Module relationship diagram created
- ✅ Tick pipeline data flow documented (9 stages)
- ✅ System responsibilities cataloged (6 systems)
- ✅ Design patterns identified (6 patterns)
- ✅ Determinism guarantees explained (3 RNG streams)
- ✅ Evolution from original spec documented
- ✅ Module count by subsystem provided

**Phase 3 Task 3.3**: **COMPLETE** ✅
