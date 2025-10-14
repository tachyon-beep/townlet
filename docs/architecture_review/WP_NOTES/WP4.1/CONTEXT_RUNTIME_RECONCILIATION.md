# Context/Runtime Architecture Reconciliation

**Created**: 2025-10-14
**Status**: ✅ COMPLETE
**Phase**: WP4.1 Phase 2 (Documentation)

---

## Executive Summary

The Townlet world layer uses **two distinct architectural components** that work together to implement the port-and-adapter pattern:

1. **`WorldRuntime`** ([src/townlet/world/runtime.py](../../../src/townlet/world/runtime.py)) — Public façade implementing the `WorldRuntime` protocol from `ports/world.py`
2. **`WorldContext`** ([src/townlet/world/core/context.py](../../../src/townlet/world/core/context.py)) — Internal aggregator coordinating world subsystems

**There is NO `townlet/world/context.py` stub file** — it was never created during WP1/WP2 implementation. The ADR-002 specification mentioned it, but the actual implementation evolved into the refined structure documented below.

**Conclusion**: No action required. The architecture is clean, well-factored, and follows best practices.

---

## Problem Statement

During WP4.1 Phase 0 risk assessment, architectural confusion was noted in the planning documents regarding "three context/runtime concepts":

1. ❌ `townlet/world/context.py` — **Does not exist** (only mentioned in ADR-002 spec)
2. ✅ `townlet/world/core/context.py` — **Real implementation** (`WorldContext` class)
3. ✅ `townlet/world/runtime.py` — **Port implementation** (`WorldRuntime` class)

This document reconciles the spec vs implementation gap and documents the actual architecture.

---

## Architecture Analysis

### 1. The Port Protocol: `WorldRuntime` (ports/world.py)

**Purpose**: Define the contract between simulation loop and world implementations.

**Location**: [src/townlet/ports/world.py:27-99](../../../src/townlet/ports/world.py#L27-L99)

**Key characteristics**:
- Structural protocol (`@runtime_checkable`)
- Enforces DTO boundaries (`ObservationEnvelope`, `SimulationSnapshot`)
- Minimal contract: `bind_world()`, `agents()`, `observe()`, `apply_actions()`, `tick()`, `snapshot()`
- Used by `SimulationLoop` for type checking

**Documentation quality**: ⭐⭐⭐⭐⭐ Excellent
- Clear docstrings
- Explains structural typing pattern
- References ADR-001 and ADR-003
- Notes naming convention (protocol and implementation share name)

### 2. The Concrete Implementation: `WorldRuntime` (world/runtime.py)

**Purpose**: Stateful façade sequencing world operations each tick.

**Location**: [src/townlet/world/runtime.py:51-233](../../../src/townlet/world/runtime.py#L51-L233)

**Key responsibilities**:
- Implements `WorldRuntime` protocol via structural typing
- Buffers console operations and policy actions
- Delegates to `WorldContext` when available (line 196-232)
- Provides legacy fallback for direct `WorldState` access (line 197-220)
- Exposes `observe()` and `snapshot()` methods

**Delegation pattern** (line 222-232):
```python
context = getattr(world, "context", None)
if context is None:
    # Legacy path: direct WorldState manipulation
    ...
else:
    # Modern path: delegate to WorldContext
    result = context.tick(...)
```

**Documentation quality**: ⭐⭐⭐⭐ Good
- Clear module docstring
- Explains stateful buffering
- Could add more detail on delegation pattern

### 3. The Internal Aggregator: `WorldContext` (world/core/context.py)

**Purpose**: Aggregate world subsystems and orchestrate tick execution.

**Location**: [src/townlet/world/core/context.py:48-495](../../../src/townlet/world/core/context.py#L48-L495)

**Key responsibilities**:
- Aggregates 13 services (queue_manager, affordance_service, employment, lifecycle, etc.)
- Implements `tick()` method (line 231-303) with full systems pipeline
- Implements `observe()` method (line 149-229) building `ObservationEnvelope` DTOs
- Exports subsystem snapshots for telemetry
- Manages RNG streams

**Composition** (dataclass fields):
- `state: WorldState` — Core world state
- `queue_manager: QueueManager` — Queue conflict tracking
- `affordance_service: AffordanceRuntimeService` — Action resolution
- `employment_*: EmploymentCoordinator/Runtime/Service` — Job tracking (3 services)
- `lifecycle_service: LifecycleService` — Spawning/termination
- `relationships: RelationshipService` — Social dynamics
- `economy_service: EconomyService` — Economy state
- `perturbation_service: PerturbationService` — Event scheduling
- `observation_service: ObservationServiceProtocol` — Observation building
- `systems: tuple[SystemStep, ...]` — System tick pipeline

**Documentation quality**: ⭐⭐⭐ Moderate
- Basic module docstring
- Methods lack detailed docstrings
- Could document aggregation pattern more explicitly

### 4. The Adapter: `WorldRuntimeAdapter` (world/core/runtime_adapter.py)

**Purpose**: Provide read-only view over `WorldState` for observations/policy.

**Location**: [src/townlet/world/core/runtime_adapter.py:44-216](../../../src/townlet/world/core/runtime_adapter.py#L44-L216)

**Key responsibilities**:
- Implements `WorldRuntimeAdapterProtocol`
- Wraps `WorldState` with read-only accessors
- Provides embedding allocator adapter
- Used by observation service to access world state safely

**Helper function** (line 192-213):
```python
def ensure_world_adapter(
    world: WorldRuntimeAdapterProtocol | WorldState | WorldContext,
) -> WorldRuntimeAdapterProtocol:
    """Return a runtime adapter, wrapping world when necessary."""
```

Automatically wraps `WorldState` or `WorldContext.state` into adapter.

**Documentation quality**: ⭐⭐⭐⭐ Good
- Clear module docstring ("read-only runtime adapter")
- Explains purpose

---

## Usage Patterns

### Pattern 1: SimulationLoop → WorldRuntime (Port Contract)

**File**: [src/townlet/core/sim_loop.py:40](../../../src/townlet/core/sim_loop.py#L40)

```python
from townlet.ports.world import WorldRuntime  # Protocol

class SimulationLoop:
    runtime: WorldRuntime | None = None  # Port contract
```

The simulation loop depends on the **protocol**, not the concrete implementation. This enables:
- Dependency inversion (depends on abstraction)
- Testability (can inject stub implementations)
- Multiple world backends (default, scripted, API-based)

### Pattern 2: WorldRuntime → WorldContext (Delegation)

**File**: [src/townlet/world/runtime.py:196-232](../../../src/townlet/world/runtime.py#L196-L232)

```python
context = getattr(world, "context", None)
if context is None:
    # Legacy: direct WorldState manipulation
    world.tick = tick
    world.apply_actions(prepared_actions)
    ...
else:
    # Modern: delegate to WorldContext
    result = context.tick(
        tick=tick,
        console_operations=queued_ops,
        prepared_actions=prepared_actions,
        lifecycle=lifecycle,
        perturbations=perturbations,
        ticks_per_day=self._ticks_per_day,
    )
```

The runtime checks if `world` has a `context` attribute, and if so, delegates all tick operations to `WorldContext`.

### Pattern 3: WorldContext → Systems Pipeline

**File**: [src/townlet/world/core/context.py:264-271](../../../src/townlet/world/core/context.py#L264-L271)

```python
system_ctx = SystemContext(
    state=cast("ModularWorldState", state),
    rng=rng_manager,
    events=dispatcher,
)
for step in self.systems or ():
    step(system_ctx)
```

The context executes a pipeline of domain systems (affordances, economy, employment, etc.) each tick.

### Pattern 4: Observation Service → WorldRuntimeAdapter

**File**: [src/townlet/world/core/context.py:168](../../../src/townlet/world/core/context.py#L168)

```python
adapter = ensure_world_adapter(cast(AdapterSource, self.state))
raw_batch = self.observation_service.build_batch(adapter, terminated_map)
```

The observation service accesses world state via the read-only adapter, not directly.

---

## Dependency Graph

```
┌───────────────────────────────────────────────────────────────┐
│                      SimulationLoop                           │
│                 (src/townlet/core/sim_loop.py)                │
└───────────────────────────────┬───────────────────────────────┘
                                │ depends on
                                ▼
                   ┌────────────────────────────┐
                   │   WorldRuntime (Protocol)  │
                   │  (src/townlet/ports/world.py) │
                   └────────────────────────────┘
                                ▲
                                │ implemented by
                                │
                   ┌────────────────────────────┐
                   │   WorldRuntime (Concrete)  │
                   │  (src/townlet/world/runtime.py) │
                   └────────────┬───────────────┘
                                │ delegates to
                                ▼
                   ┌────────────────────────────┐
                   │       WorldContext         │
                   │ (src/townlet/world/core/context.py) │
                   └────────────┬───────────────┘
                                │ aggregates
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
      ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
      │QueueManager │  │Affordance    │  │Lifecycle     │
      │             │  │Service       │  │Service       │
      └─────────────┘  └──────────────┘  └──────────────┘
                │               │               │
                └───────────────┴───────────────┘
                                │ operates on
                                ▼
                   ┌────────────────────────────┐
                   │        WorldState          │
                   │   (src/townlet/world/grid.py)  │
                   └────────────┬───────────────┘
                                │ wrapped by
                                ▼
                   ┌────────────────────────────┐
                   │   WorldRuntimeAdapter      │
                   │ (src/townlet/world/core/runtime_adapter.py) │
                   └────────────────────────────┘
                                ▲
                                │ used by
                   ┌────────────────────────────┐
                   │   ObservationService       │
                   └────────────────────────────┘
```

---

## Decision: No Changes Required

After thorough investigation, **no code or structural changes are needed**. The architecture is sound:

### Reasons to Keep Current Structure

1. **Clean Separation of Concerns**
   - Port protocol defines contract
   - Concrete runtime implements port
   - Internal context aggregates subsystems
   - Adapter provides read-only views

2. **Follows Best Practices**
   - Port-and-adapter pattern (ADR-001)
   - Dependency inversion (SimulationLoop depends on protocol)
   - Façade pattern (WorldRuntime hides complexity)
   - Aggregator pattern (WorldContext composes services)

3. **No Orphaned Code**
   - `townlet/world/context.py` never existed
   - All modules are actively used
   - No dead imports or stubs

4. **Good Evolution Path**
   - ADR-002 specified flat structure
   - Implementation refined into subdirectories
   - Better organization without breaking principles

### What About ADR-002?

ADR-002 mentions `world/context.py` as the runtime façade, but the actual implementation is:
- `world/runtime.py` — Façade (implements port)
- `world/core/context.py` — Internal aggregator

This is a **better design** than the original spec because:
- Separates port implementation from internal aggregation
- Allows `WorldContext` to focus on subsystem coordination
- `WorldRuntime` handles buffering and port contract
- More modular and testable

**Recommendation**: Update ADR-002 to reflect actual implementation (Phase 3 of WP4.1).

---

## Naming Convention Clarification

### Why "WorldRuntime" Appears Twice

The name `WorldRuntime` appears in two places:
1. **Protocol** — `townlet.ports.world.WorldRuntime`
2. **Concrete class** — `townlet.world.runtime.WorldRuntime`

This is **intentional and correct** per PEP 544 (structural typing):
- Different namespaces prevent confusion
- Concrete class naturally fulfills protocol contract
- Common pattern in typed Python (e.g., `typing.Sequence` vs `collections.abc.Sequence`)

The port protocol documentation explicitly notes this (line 40-46 in ports/world.py):
```python
"""
Naming Convention:
    The concrete implementation class shares the name "WorldRuntime" with this protocol.
    This is intentional and works correctly because:
    1. Structural typing allows this pattern (PEP 544)
    2. Different namespaces prevent confusion (ports.world vs world.runtime)
    3. The concrete class naturally fulfills the protocol contract
    4. The adapter pattern cleanly wraps the concrete implementation
"""
```

### Why "Context" Appears in Two Places

The name `Context` appears in:
1. **WorldContext** — `townlet.world.core.context.WorldContext` (internal aggregator)
2. **SystemContext** — `townlet.world.systems.base.SystemContext` (system execution context)

These are **different concepts**:
- `WorldContext` aggregates services and orchestrates ticks
- `SystemContext` provides execution context for domain systems (state, RNG, events)

No confusion because:
- Different fully-qualified names
- Different purposes (aggregator vs execution context)
- Clear from usage patterns

---

## References

### Related ADRs
- [ADR-001: Port and Factory Registry](../../ADR/ADR-001%20-%20Port%20and%20Factory%20Registry.md) — Port protocol pattern
- [ADR-002: World Modularisation](../../ADR/ADR-002%20-%20World%20Modularisation.md) — Original world structure spec (needs update)
- [ADR-003: DTO Boundary](../../ADR/ADR-003%20-%20DTO%20Boundary.md) — DTO enforcement at boundaries

### Key Files
- [src/townlet/ports/world.py](../../../src/townlet/ports/world.py) — Port protocol
- [src/townlet/world/runtime.py](../../../src/townlet/world/runtime.py) — Concrete implementation
- [src/townlet/world/core/context.py](../../../src/townlet/world/core/context.py) — Internal aggregator
- [src/townlet/world/core/runtime_adapter.py](../../../src/townlet/world/core/runtime_adapter.py) — Read-only adapter
- [src/townlet/core/sim_loop.py](../../../src/townlet/core/sim_loop.py) — Consumer of port

---

## Acceptance Criteria

- ✅ Documented why "three concepts" are actually two
- ✅ Explained port vs implementation pattern
- ✅ Clarified WorldRuntime vs WorldContext roles
- ✅ Documented delegation patterns
- ✅ Confirmed no orphaned code
- ✅ Decision: Keep current structure (no changes)
- ✅ Identified ADR-002 update as Phase 3 task

**Phase 2 Task 2.2**: **COMPLETE** ✅
