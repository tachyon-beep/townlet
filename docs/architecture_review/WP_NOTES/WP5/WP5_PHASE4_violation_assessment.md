# WP5 Phase 4: Import Violation Assessment

**Date**: 2025-10-15
**Dry Run**: lint-imports --config .importlinter.analysis
**Result**: 1 kept, 6 broken contracts

---

## Executive Summary

**✅ EXCELLENT NEWS**: The `dto` package is 100% clean with **ZERO violations**!

**Violation Overview**:
- **Total Broken Contracts**: 6 of 7
- **Direct Violations**: ~15 (actual problematic imports)
- **Indirect Violations**: ~40+ (through long import chains)
- **Common Culprits**: `config.loader → snapshots`, `core.utils → fallbacks`, `ports.world → world implementations`

**Assessment Strategy**:
1. **Legitimate (Grandfather)**: Architectural dependencies that are intentional
2. **Easy Fix**: Can be fixed in <30 min with TYPE_CHECKING or protocol imports
3. **Medium Fix**: Requires moving code or refactoring (1-2 hours)
4. **Requires Refactoring**: Major work, defer to post-WP5

---

## Contract 1: DTO Independence ✅ PASSING

**Status**: ✅ **100% CLEAN**

All DTO modules are independent and import ZERO concrete packages. This is the result of excellent WP3 work!

**No violations to assess.**

---

## Contract 2: Layered Architecture 🔴 BROKEN

**Total Violations**: ~30 indirect violations

### Category: Legitimate Dependencies (Grandfather)

#### 1. ports.world → world.grid & world.runtime (DIRECT)

**Violation**: `townlet.ports.world -> townlet.world.grid` (l.22)

**Type**: Legitimate architectural dependency
**Reason**: Port protocol needs to import concrete types for type hints in protocol definition
**Decision**: **GRANDFATHER** - This is intentional from ADR-001

**Fix**: Not needed - this is by design. Ports define the contract, implementations (world.grid, world.runtime) satisfy it.

**Exception**: Add to `.importlinter`:
```ini
ignore_imports =
    townlet.ports.world -> townlet.world.grid  # ADR-001: Port protocol uses concrete types for hints
    townlet.ports.world -> townlet.world.runtime  # ADR-001: Port protocol uses concrete types for hints
```

---

#### 2. core → ports (DIRECT)

**Violations**:
- `townlet.core.sim_loop -> townlet.ports.policy` (l.37)
- `townlet.core.sim_loop -> townlet.ports.world` (l.40)
- `townlet.core.sim_loop -> townlet.ports.telemetry` (l.38)

**Type**: Legitimate architectural dependency
**Reason**: Core orchestration (sim_loop) coordinates adapters through port protocols
**Decision**: **GRANDFATHER** - This is the dependency inversion pattern from ADR-001

**Exception**: Add to `.importlinter`:
```ini
ignore_imports =
    townlet.core.sim_loop -> townlet.ports.*  # ADR-001: Core coordinates via port protocols
    townlet.core.factory_registry -> townlet.ports.world  # ADR-001: Factory resolves implementations
```

---

#### 3. ports → dto (DIRECT)

**Violations**:
- `townlet.ports.world -> townlet.dto.world` (l.21)
- `townlet.ports.world -> townlet.dto.observations` (l.16)
- `townlet.ports.telemetry -> townlet.dto.telemetry` (l.24)
- `townlet.ports.policy -> townlet.dto.observations` (l.17)

**Type**: Legitimate architectural dependency
**Reason**: Port protocols use DTOs for typed boundaries (ADR-003)
**Decision**: **GRANDFATHER** - This is intentional from ADR-003

**Note**: This reveals the layering config is WRONG. DTOs should be BELOW ports, not above!

**Fix**: Update `.importlinter.analysis` layering to:
```ini
layers =
    townlet.dto  # BOTTOM LAYER - shared data types
    townlet.ports  # Uses DTOs
    townlet.core  # Uses ports
    townlet.world | townlet.policy | townlet.telemetry | ...  # Domain adapters
```

---

#### 4. policy → world & policy → dto (DIRECT)

**Violations**:
- `townlet.policy.behavior -> townlet.world.grid` (l.17)
- `townlet.policy.runner -> townlet.dto.observations` (l.30)
- Multiple other policy → world and policy → dto imports

**Type**: Legitimate architectural dependency
**Reason**: Policy implementations need world state and DTOs to function
**Decision**: **GRANDFATHER** - Policy and world are at the same layer (both domain adapters)

**Note**: The layering config treats all domain packages as a single layer (using `|`), so policy→world is actually allowed!

**Fix**: No exception needed - config already allows this via `townlet.world | townlet.policy | ...`

---

###Category: Indirect Violations Through config.loader → snapshots

**Pattern**: Many packages → config → config.loader → snapshots

**Root Cause**: `config.loader` line 444 imports `snapshots` module

**Affected Packages**:
- lifecycle → config → snapshots
- telemetry → config → snapshots
- observations → config → snapshots
- rewards → config → snapshots
- benchmark → config → snapshots
- stability → config → snapshots
- policy → config → snapshots
- world → config → snapshots

**Type**: Legacy violation (architectural coupling)
**Reason**: Config loader validates snapshot paths at startup
**Decision**: **EASY FIX** - Move validation out of config.loader

**Fix Strategy** (30 minutes):
1. Extract snapshot path validation to `snapshots.validation` module
2. Config loader imports validation function (not full snapshots module)
3. This breaks the long import chain

**Impact**: Fixes ~8 indirect violations

---

### Category: Indirect Violations Through core.utils → fallbacks

**Pattern**: Many packages → core.utils → policy.fallback OR telemetry.fallback

**Root Cause**:
- `core.utils` line 8 imports `policy.fallback`
- `core.utils` line 9 imports `telemetry.fallback`

**Affected Packages**:
- world → snapshots → core.utils → policy.fallback
- policy → core.utils → telemetry.fallback
- config → snapshots → core.utils → policy.fallback
- ports → snapshots → core.utils → policy.fallback

**Type**: Legacy violation (convenience imports)
**Reason**: `core.utils` provides convenience access to fallback implementations
**Decision**: **EASY FIX** - Remove convenience imports, import directly where needed

**Fix Strategy** (15 minutes):
1. Remove `policy.fallback` and `telemetry.fallback` from `core.utils`
2. Update call sites to import directly

**Impact**: Fixes ~10 indirect violations

---

### Category: Legitimate Cross-Layer Dependencies

#### snapshots → world/policy/telemetry/stability/core

**Violations**: snapshots.state imports from many packages

**Type**: Legitimate architectural dependency
**Reason**: Snapshots serialize state from ALL subsystems - this is their purpose
**Decision**: **GRANDFATHER** - Snapshots are a special cross-cutting concern

**Fix**: Relax snapshot contract to allow necessary imports

**Exception**: Update snapshot contract:
```ini
[importlinter:contract:snapshot-boundaries]
name = Snapshots may import for serialization (not business logic)
type = forbidden
source_modules =
    townlet.snapshots
forbidden_modules =
    # Allow imports needed for state serialization
    # townlet.world.grid
    # townlet.world.runtime
    # ... (comment out forbidden modules that snapshots legitimately need)
```

**Note**: The current contract is TOO STRICT for snapshots. They need to import what they serialize.

---

### Category: Medium Fixes (1-2 hours each)

#### world.agents.relationships_service → telemetry.relationship_metrics

**Violation**: `townlet.world.agents.relationships_service -> townlet.telemetry.relationship_metrics` (l.14)

**Type**: Cross-boundary coupling (domain emitting specialized telemetry)
**Reason**: Relationship service emits relationship-specific metrics
**Decision**: **MEDIUM FIX** - Refactor to use generic telemetry events

**Fix Strategy** (1-2 hours):
1. Relationship service emits generic telemetry events (via port protocol)
2. Telemetry layer transforms generic events into relationship metrics
3. Removes direct dependency

**Impact**: Fixes 1 direct violation + cascading effects

**Priority**: Medium (improves architecture but not blocking)

---

#### world.grid → observations.embedding

**Violations**:
- `townlet.world.grid -> townlet.observations.embedding` (l.28)
- `townlet.world.core.runtime_adapter -> townlet.observations.embedding` (l.16)

**Type**: Cross-boundary coupling (world using observations)
**Reason**: World needs to allocate embeddings for agents
**Decision**: **MEDIUM FIX** - Refactor embedding allocation to separate service

**Fix Strategy** (1-2 hours):
1. Extract embedding allocation to `world.embeddings` module
2. Move embedding logic from observations to world
3. Observations only consumes embeddings (doesn't manage allocation)

**Impact**: Fixes 2 direct violations

**Priority**: Medium (cleaner separation but not urgent)

---

#### world.runtime → lifecycle.manager & stability.monitor

**Violations**:
- `townlet.world.runtime -> townlet.lifecycle.manager` (l.24)
- `townlet.world.runtime -> townlet.stability.monitor` (l.25)
- `townlet.world.runtime -> townlet.stability.promotion` (l.26)

**Type**: Composition dependencies (world owns lifecycle & stability)
**Reason**: World runtime coordinates lifecycle and stability systems
**Decision**: **LEGITIMATE** - These are composition relationships

**Exception**: Add to grandfather:
```ini
ignore_imports =
    townlet.world.runtime -> townlet.lifecycle.manager  # WorldRuntime owns lifecycle
    townlet.world.runtime -> townlet.stability.monitor  # WorldRuntime owns stability monitoring
    townlet.world.runtime -> townlet.stability.promotion  # WorldRuntime coordinates promotion
```

---

## Contract 3: World Must Not Import Policy 🔴 BROKEN

**Violation**: 1 indirect violation

### world → snapshots → core.utils → policy.fallback

**Type**: Indirect through convenience import
**Reason**: core.utils imports fallback for convenience
**Decision**: **EASY FIX** - Remove convenience import (see layered architecture assessment)

**Fix**: Already covered in "Indirect Violations Through core.utils → fallbacks" above

---

## Contract 4: Policy Must Not Import Telemetry 🔴 BROKEN

**Violations**: 6 indirect violations

### All violations through long import chains

**Pattern**: policy → core → telemetry OR policy → world → telemetry

**Type**: Indirect violations
**Reason**: Policy uses core utilities and world state, which transitively import telemetry
**Decision**: **MEDIUM PRIORITY** - Some indirect coupling acceptable

**Assessment**:
1. `policy.api -> core.factory_registry -> telemetry.fallback` - **EASY FIX** (remove convenience import)
2. `policy.behavior_bridge -> world.grid -> relationships -> telemetry.relationship_metrics` - **MEDIUM FIX** (see above)
3. `policy.scenario_utils -> core.sim_loop -> telemetry.publisher` - **GRANDFATHER** (sim_loop legitimately owns telemetry)
4. Other violations similar patterns

**Decision**: Most violations will be fixed by:
1. Removing convenience imports from core.utils
2. Grandfathering sim_loop → telemetry (intentional coordination)

---

## Contract 5: Config Must Only Import DTO 🔴 BROKEN

**Violations**: 4 violations all through config.loader → snapshots

### config.loader → snapshots chain

**Type**: All indirect through line 444
**Reason**: Config loader validates snapshot paths
**Decision**: **EASY FIX** - Already covered in layered architecture assessment

**Fix**: Extract snapshot validation (see above)

**Impact**: Fixes ALL 4 violations for this contract

---

## Contract 6: Port Independence 🔴 BROKEN

**Violations**: Multiple indirect violations

### ports.world → world implementations

**Type**: Legitimate (see layered architecture assessment)
**Decision**: **GRANDFATHER** - Ports must import concrete types for protocol hints

### Other indirect violations

**Type**: Cascading from config.loader → snapshots and core.utils → fallbacks
**Decision**: **EASY FIX** - Already covered above

---

## Contract 7: Snapshot Boundaries 🔴 BROKEN

**Violations**: Multiple violations importing world.grid and world.runtime

### Assessment

**Type**: Too strict - snapshots MUST import what they serialize
**Decision**: **RELAX CONTRACT** - Snapshots are a special cross-cutting concern

**Fix**: Redefine contract to allow necessary imports for serialization

---

## Summary & Recommendations

### Quick Wins (Fix in Phase 0.3) ⚡

1. **Remove core.utils convenience imports** (15 min)
   - Fixes ~10 indirect violations
   - Files: `core/utils.py` (remove lines 8-9)

2. **Extract snapshot validation from config.loader** (30 min)
   - Fixes ~8 indirect violations
   - Create: `snapshots/validation.py`
   - Update: `config/loader.py` line 444

3. **Fix layering order** (5 min)
   - dto should be BELOW ports, not above
   - Update: `.importlinter.analysis` layers

**Total Time**: ~50 minutes
**Total Impact**: ~20 violations fixed

---

### Contracts to Adjust

1. **Layered Architecture**: Reorder to dto → ports → core → domain
2. **Snapshot Boundaries**: Relax to allow serialization imports

---

### Exceptions to Grandfather

Add these to production `.importlinter`:

```ini
# ports → world (ADR-001: Protocol uses concrete types)
townlet.ports.world -> townlet.world.grid
townlet.ports.world -> townlet.world.runtime

# core → ports (ADR-001: Dependency inversion)
townlet.core.sim_loop -> townlet.ports.policy
townlet.core.sim_loop -> townlet.ports.world
townlet.core.sim_loop -> townlet.ports.telemetry
townlet.core.factory_registry -> townlet.ports.world

# world.runtime → lifecycle/stability (Composition)
townlet.world.runtime -> townlet.lifecycle.manager
townlet.world.runtime -> townlet.stability.monitor
townlet.world.runtime -> townlet.stability.promotion
```

**Total Exceptions**: ~9 legitimate architectural dependencies

---

### Medium-Priority Refactorings (Post-WP5)

1. **Relationship metrics decoupling** (1-2 hours)
2. **Embedding allocation extraction** (1-2 hours)

---

## Final Assessment

**Verdict**: ✅ **PHASE 4 IS VIABLE**

- **DTO package**: Perfect (0 violations)
- **Easy fixes**: ~20 violations can be fixed in ~1 hour
- **Legitimate exceptions**: ~9 architectural dependencies to grandfather
- **Contract adjustments**: 2 contracts need refinement
- **Post-WP5 work**: 2 medium refactorings identified but not blocking

**Recommendation**: **PROCEED** with Phase 0.3 (quick win fixes)

---

**End of Violation Assessment**
