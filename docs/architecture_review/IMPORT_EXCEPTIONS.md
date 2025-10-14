# Import Boundary Exceptions Registry

**Status**: Phase 0.4 (WP5 Phase 4 Risk Reduction)
**Date**: 2025-10-15
**Purpose**: Document legitimate architectural dependencies that are exceptions to import-linter contracts

---

## Overview

This document registers import violations that are **intentional architectural decisions** and should be allowed as exceptions in the import-linter configuration. Each exception is documented with:

- **Violation**: The import that violates a contract
- **Contract**: Which boundary contract it violates
- **Rationale**: Why this import is architecturally sound
- **ADR Reference**: Related Architecture Decision Record (if applicable)
- **Decision**: Exception status (GRANDFATHER, REFACTOR_LATER, etc.)

---

## Exception Categories

### 1. Protocol Concrete Type References (ADR-001)

**Contract Violated**: Port Independence
**Rationale**: Port protocols need to reference concrete types for type hints in protocol definitions. This is by design per ADR-001 (Ports & Adapters pattern).

#### Exception 1.1: ports.world → world.grid
```python
# File: src/townlet/ports/world.py (line 22)
from townlet.world.grid import WorldState
```
**Rationale**: `WorldRuntime` protocol returns `WorldState` - the protocol must reference the concrete type for proper typing.

**Decision**: ✅ **GRANDFATHER** - Intentional from ADR-001

---

#### Exception 1.2: ports.world → world.runtime
```python
# File: src/townlet/ports/world.py
from townlet.world.runtime import WorldRuntime
```
**Rationale**: Port protocol references the concrete implementation type for factory resolution.

**Decision**: ✅ **GRANDFATHER** - Intentional from ADR-001

---

### 2. Dependency Inversion (ADR-001)

**Contract Violated**: Layered Architecture
**Rationale**: Core orchestration coordinates domain adapters through port protocols. This is the dependency inversion pattern from ADR-001.

#### Exception 2.1: core.sim_loop → ports.policy
```python
# File: src/townlet/core/sim_loop.py (line 37)
from townlet.ports.policy import PolicyBackendProtocol
```
**Rationale**: SimulationLoop coordinates policy backend through protocol interface.

**Decision**: ✅ **GRANDFATHER** - Intentional from ADR-001

---

#### Exception 2.2: core.sim_loop → ports.world
```python
# File: src/townlet/core/sim_loop.py (line 40)
from townlet.ports.world import WorldRuntime
```
**Rationale**: SimulationLoop coordinates world runtime through protocol interface.

**Decision**: ✅ **GRANDFATHER** - Intentional from ADR-001

---

#### Exception 2.3: core.sim_loop → ports.telemetry
```python
# File: src/townlet/core/sim_loop.py (line 38)
from townlet.ports.telemetry import TelemetrySinkProtocol
```
**Rationale**: SimulationLoop coordinates telemetry sink through protocol interface.

**Decision**: ✅ **GRANDFATHER** - Intentional from ADR-001

---

#### Exception 2.4: core.factory_registry → ports.world
```python
# File: src/townlet/core/factory_registry.py
from townlet.ports.world import WorldRuntime
```
**Rationale**: Factory registry resolves implementations to port protocols.

**Decision**: ✅ **GRANDFATHER** - Intentional from ADR-001

---

### 3. Composition Relationships

**Contract Violated**: Layered Architecture
**Rationale**: Parent objects own child objects through composition. These are legitimate ownership relationships, not architectural violations.

#### Exception 3.1: world.runtime → lifecycle.manager
```python
# File: src/townlet/world/runtime.py (line 24)
from townlet.lifecycle.manager import LifecycleManager
```
**Rationale**: WorldRuntime **owns** LifecycleManager as a composed component.

**Decision**: ✅ **GRANDFATHER** - Composition relationship

---

#### Exception 3.2: world.runtime → stability.monitor
```python
# File: src/townlet/world/runtime.py (line 25)
from townlet.stability.monitor import StabilityMonitor
```
**Rationale**: WorldRuntime **owns** StabilityMonitor as a composed component.

**Decision**: ✅ **GRANDFATHER** - Composition relationship

---

#### Exception 3.3: world.runtime → stability.promotion
```python
# File: src/townlet/world/runtime.py (line 26)
from townlet.stability.promotion import PromotionManager
```
**Rationale**: WorldRuntime **owns** PromotionManager as a composed component.

**Decision**: ✅ **GRANDFATHER** - Composition relationship

---

#### Exception 3.4: world.core.context → lifecycle.manager
```python
# File: src/townlet/world/core/context.py (line 26)
from townlet.lifecycle.manager import LifecycleManager
```
**Rationale**: WorldContext **owns** LifecycleManager as a composed component.

**Decision**: ✅ **GRANDFATHER** - Composition relationship

---

### 4. Snapshot Serialization (Cross-Cutting Concern)

**Contract Violated**: Snapshot Boundaries, Layered Architecture
**Rationale**: Snapshots serialize state from ALL subsystems - this is their purpose as a cross-cutting concern. They must import what they serialize.

#### Exception 4.1: snapshots.state → world.grid
```python
# File: src/townlet/snapshots/state.py (line 42)
from townlet.world.grid import WorldState, InteractiveObject
```
**Rationale**: Snapshot serialization requires access to WorldState for capturing world state.

**Decision**: ✅ **GRANDFATHER** - Snapshots are cross-cutting serialization layer

---

#### Exception 4.2: snapshots.state → world.core.runtime_adapter
```python
# File: src/townlet/snapshots/state.py (line 41)
from townlet.world.core.runtime_adapter import ensure_world_adapter
```
**Rationale**: Snapshot serialization needs adapter to extract world state consistently.

**Decision**: ✅ **GRANDFATHER** - Snapshots are cross-cutting serialization layer

---

#### Exception 4.3: snapshots.state → world.agents.snapshot
```python
# File: src/townlet/snapshots/state.py (line 40)
from townlet.world.agents.snapshot import AgentSnapshot
```
**Rationale**: Snapshot serialization captures agent snapshots.

**Decision**: ✅ **GRANDFATHER** - Snapshots are cross-cutting serialization layer

---

#### Exception 4.4: snapshots.state → world.rng
```python
# File: src/townlet/snapshots/state.py (line 43)
from townlet.world.rng import RngStreamManager
```
**Rationale**: Snapshot serialization captures RNG state for deterministic replay.

**Decision**: ✅ **GRANDFATHER** - Snapshots are cross-cutting serialization layer

---

#### Exception 4.5: snapshots.state → lifecycle.manager
```python
# File: src/townlet/snapshots/state.py (line 32)
from townlet.lifecycle.manager import LifecycleManager
```
**Rationale**: Snapshot serialization captures lifecycle state.

**Decision**: ✅ **GRANDFATHER** - Snapshots are cross-cutting serialization layer

---

#### Exception 4.6: snapshots.state → stability.monitor
```python
# File: src/townlet/snapshots/state.py (line 46)
from townlet.stability.monitor import StabilityMonitor
```
**Rationale**: Snapshot serialization captures stability metrics.

**Decision**: ✅ **GRANDFATHER** - Snapshots are cross-cutting serialization layer

---

#### Exception 4.7: snapshots.state → stability.promotion
```python
# File: src/townlet/snapshots/state.py (line 47)
from townlet.stability.promotion import PromotionManager
```
**Rationale**: Snapshot serialization captures promotion state.

**Decision**: ✅ **GRANDFATHER** - Snapshots are cross-cutting serialization layer

---

#### Exception 4.8: snapshots.state → scheduler.perturbations
```python
# File: src/townlet/snapshots/state.py (line 33)
from townlet.scheduler.perturbations import PerturbationScheduler
```
**Rationale**: Snapshot serialization captures perturbation scheduler state.

**Decision**: ✅ **GRANDFATHER** - Snapshots are cross-cutting serialization layer

---

### 5. Indirect Dependencies (Acceptable)

**Contract Violated**: Various
**Rationale**: Indirect imports through intermediary modules. These are acceptable architectural dependencies.

#### Exception 5.1: policy → snapshots (indirect)
```python
# Chain: policy → config → config.loader → snapshots.migrations
```
**Rationale**: Policy modules import config, which imports config.loader, which imports snapshots.migrations for migration registration. This is an indirect dependency through configuration, not a direct coupling.

**Decision**: ✅ **GRANDFATHER** - Indirect dependency through config layer, acceptable

---

#### Exception 5.2: core.sim_loop → telemetry.publisher
```python
# File: src/townlet/core/sim_loop.py
from townlet.telemetry.publisher import TelemetryPublisher
```
**Rationale**: SimulationLoop **owns** TelemetryPublisher for event emission coordination.

**Decision**: ✅ **GRANDFATHER** - SimulationLoop is the orchestration layer that legitimately owns telemetry

---

## Summary

**Total Exceptions**: 21 (as of Phase 0.4)

**By Category**:
- Protocol Concrete Types: 2
- Dependency Inversion: 4
- Composition: 4
- Snapshot Serialization: 8
- Indirect Dependencies: 2
- Other Orchestration: 1

**By Decision**:
- ✅ GRANDFATHER: 21
- ⏸️ REFACTOR_LATER: 0

---

## How to Add New Exceptions

When adding a new exception to the registry:

1. **Identify the violation** - Run import-linter and identify the specific import
2. **Determine the category** - Protocol, Composition, Cross-Cutting, etc.
3. **Document the rationale** - WHY is this import architecturally sound?
4. **Reference ADRs** - Link to relevant Architecture Decision Records
5. **Make a decision** - GRANDFATHER (allow permanently) or REFACTOR_LATER (tech debt)
6. **Update import-linter config** - Add the exception to `.importlinter` file

---

## Related Documents

- `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md` - Ports & Adapters pattern
- `docs/architecture_review/ADR/ADR-002 - World Modularisation.md` - World package structure
- `docs/architecture_review/ADR/ADR-003 - DTO Boundary.md` - DTO consolidation strategy
- `docs/architecture_review/WP5_PHASE4_violation_assessment.md` - Detailed violation analysis

---

**End of Import Exceptions Registry**
