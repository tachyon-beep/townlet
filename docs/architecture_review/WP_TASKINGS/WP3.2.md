# Work Package 3.2: Snapshot DTO Consolidation

**Status**: DRAFT
**Author**: Claude Code
**Date**: 2025-10-14
**Dependencies**: WP3.1 (Complete), WP4 (Complete)
**Target**: Complete WP3 DTO boundary by consolidating snapshot persistence

---

## Executive Summary

WP3.2 completes the DTO boundary initiative by **replacing the SnapshotState dataclass with SimulationSnapshot Pydantic DTO**. This eliminates dict-soup in snapshot persistence, provides full validation, and establishes a reference pattern for future DTO consolidations.

**Key Metrics**:

- **Lines Changed**: ~600 (400 conversions, 200 deletions)
- **Files Modified**: ~20
- **Tests Affected**: ~35 snapshot tests
- **Estimated Duration**: 1-2 days focused work
- **Risk Level**: Medium (comprehensive test coverage mitigates)

**Deliverables**:

1. `snapshot_from_world()` returns `SimulationSnapshot`
2. `apply_snapshot_to_world()` accepts `SimulationSnapshot`
3. `SnapshotManager` uses Pydantic serialization
4. Port protocol enforces DTO boundary
5. Legacy `SnapshotState` deleted
6. ADR-003 authored

---

## Motivation

### Current State (Post-WP4)

The codebase has **dual snapshot implementations**:

**SimulationSnapshot** (Pydantic DTO, 223 lines):

```python
class SimulationSnapshot(BaseModel):
    config_id: str
    tick: int
    agents: dict[str, AgentSummary]         # ✅ Typed DTO
    lifecycle: LifecycleSnapshot            # ✅ Nested DTO
    perturbations: PerturbationSnapshot     # ✅ Nested DTO
    # ... 11 nested DTOs total
```

**SnapshotState** (dataclass, 256 lines):

```python
@dataclass
class SnapshotState:
    config_id: str
    tick: int
    agents: dict[str, dict[str, Any]]       # ❌ Dict soup
    lifecycle: dict[str, Any]               # ❌ Dict soup
    perturbations: dict[str, Any]           # ❌ Dict soup
    # ... untyped dicts everywhere
```

### Problems with Current State

1. **Type Safety**: No validation on snapshot save/load
2. **Inconsistency**: Observations/Telemetry/Policy use DTOs, snapshots don't
3. **Maintainability**: Dict structures are undocumented
4. **Duplication**: Two parallel implementations (223 + 256 = 479 lines)

### Benefits of Consolidation

1. **Full Validation**: Pydantic catches corruption on load
2. **Type Safety**: Nested DTOs are self-documenting
3. **Consistency**: All boundaries use DTOs (Observations ✅, Telemetry ✅, Policy ✅, Snapshots ✅)
4. **Pattern Exemplar**: Reference implementation for future consolidations
5. **Code Reduction**: Delete 256 lines of dataclass + dict building

---

## Scope

### In Scope

**Core Conversion** (Required):

- Rewrite `snapshot_from_world()` to construct `SimulationSnapshot`
- Rewrite `apply_snapshot_to_world()` to extract from `SimulationSnapshot`
- Update `SnapshotManager.save()` to use `model_dump()`
- Update `SnapshotManager.load()` to use `model_validate()`
- Update `WorldRuntime.snapshot()` return type
- Update port protocol signature
- Delete `SnapshotState` class and methods

**Testing & Validation** (Required):

- Fix all snapshot tests (~35 tests)
- Add Pydantic validation tests
- Test snapshot round-trip (save → load → verify)
- Test migration compatibility

**Documentation** (Required):

- Author ADR-003: DTO Boundary Strategy
- Document consolidation pattern in CLAUDE.md
- Update snapshot documentation

### Out of Scope

- Changes to snapshot schema version (stays 1.6)
- Migration to/from legacy snapshots (handled by existing migration system)
- Performance optimization (snapshots are infrequent)
- Changes to RNG handling or world state structure

### Non-Goals

- Changing snapshot file format (still JSON)
- Removing backward compatibility (legacy snapshots still load)
- Modifying subsystem export_state() methods (keep dict interface internally)

---

## Implementation Plan

### Phase 0: Risk Reduction & Validation (2-3 hours)

**Objective**: Audit current state to validate assumptions and de-risk implementation

---

**Stage 0.1: Audit Snapshot Test Patterns** (0.5 hours)

**Objective**: Understand how tests currently use SnapshotState

**Tasks**:

1. Count snapshot-related test files: `grep -r "SnapshotState" tests/ --files-with-matches | wc -l`
2. Analyze test construction patterns (direct instantiation? Factory helpers?)
3. Analyze test assertion patterns (attribute access? dict-like? nested?)
4. Identify common test fixtures and their structure
5. Document conversion effort per test pattern type

**Expected Findings**:

- Exact test count (estimated ~35, verify actual)
- Most common assertion patterns (e.g., `snapshot.agents["alice"]["position"]`)
- Fixture construction patterns
- Edge cases (None handling, optional fields, etc.)

**Deliverable**: `WP3.2_TEST_AUDIT.md` with:

- Test count breakdown
- Pattern frequency analysis
- Conversion complexity estimate per pattern
- Edge cases requiring special attention

**Gate Condition**: Test patterns documented, no surprises found

---

**Stage 0.2: Validate Export/Import Field Mappings** (1 hour)

**Objective**: Verify subsystem export_state() outputs match DTO schemas

**Tasks**:

1. **LifecycleManager**: Compare `export_state()` output vs `LifecycleSnapshot` fields
2. **PerturbationScheduler**: Compare `export_state()` output vs `PerturbationSnapshot` fields
3. **AffordanceRuntime**: Compare `export_state()` output vs `AffordanceSnapshot` fields
4. **EmbeddingAllocator**: Compare `export_state()` output vs `EmbeddingSnapshot` fields
5. **StabilityMonitor**: Compare `export_state()` output vs `StabilitySnapshot` fields
6. **PromotionManager**: Compare `export_state()` output vs `PromotionSnapshot` fields
7. **TelemetryPublisher**: Compare `export_state()` output vs `TelemetrySnapshot` fields
8. **QueueManager**: Compare `export_state()` output vs `QueueSnapshot` fields
9. **Employment**: Compare `export_state()` output vs `EmploymentSnapshot` fields

**Method**:

```python
# For each subsystem:
# 1. Read export_state() implementation
# 2. Extract dict keys and value types
# 3. Compare against DTO field names and types
# 4. Flag mismatches (missing keys, wrong types, extra keys)
```

**Expected Mismatches**:

- Optional fields might be absent in some exports
- Type coercions (int vs float, list vs tuple)
- Nested structure differences
- Field name variations (snake_case consistency)

**Deliverable**: `WP3.2_FIELD_MAPPING.md` with:

- Per-subsystem field mapping table
- Type mismatches requiring coercion
- Missing fields requiring defaults
- Extra fields to ignore

**Gate Condition**: All field mappings validated, conversion strategy for mismatches documented

---

**Stage 0.3: Verify DTO Default Values** (0.5 hours)

**Objective**: Ensure DTO defaults match actual code behavior

**Tasks**:

1. Check `AgentSummary.last_late_tick: int = -1` — Does code use -1 or None?
2. Check `AgentSummary.shift_state: str = "pre_shift"` — Is this the actual default?
3. Check `LifecycleSnapshot.employment_day: int = -1` — Matches lifecycle.py:26?
4. Check `StabilitySnapshot` list fields — Empty list [] or None?
5. Check all `Field(default_factory=dict)` — Ever None in practice?
6. Grep for initialization patterns in subsystem code

**Method**:

```bash
# Example: Check last_late_tick default
grep -r "last_late_tick" src/townlet --include="*.py" -A2 -B2
# Look for assignments: last_late_tick = -1 | None | 0
```

**Expected Findings**:

- Most defaults match (AgentSnapshot uses same values)
- Potential mismatches requiring DTO schema adjustment
- Optional vs required field decisions

**Deliverable**: List of confirmed defaults + any required DTO schema changes

**Gate Condition**: All DTO defaults verified against code, schema adjusted if needed

---

**Stage 0.4: Test Current Snapshot Round-Trip** (0.5 hours)

**Objective**: Establish baseline behavior before changes

**Tasks**:

1. Run snapshot tests: `pytest tests/test_snapshot_manager.py -v`
2. Run integration tests: `pytest tests/test_sim_loop_snapshot.py -v`
3. Create manual test: Save snapshot mid-simulation → Load → Verify RNG determinism
4. Document any existing flakiness or known issues
5. Capture baseline performance (snapshot save/load time)

**Method**:

```python
# Manual baseline test
def test_baseline_snapshot_round_trip():
    loop = SimulationLoop(config)
    loop.run_for(100)
    snapshot1 = loop.save_snapshot()

    loop.load_snapshot(snapshot1)
    loop.run_for(100)

    # Verify determinism
    assert loop.tick == 200
```

**Expected Findings**:

- All tests currently passing (baseline: 806/806)
- Performance baseline (e.g., save=50ms, load=80ms)
- Any existing edge cases or known issues

**Deliverable**: Baseline test results + performance metrics

**Gate Condition**: Current tests all passing, baseline documented

---

**Stage 0.5: Analyze Migration System Integration** (0.5 hours)

**Objective**: Understand how migrations interact with snapshot structure

**Tasks**:

1. Read `snapshots/migrations.py` — How does MigrationRegistry work?
2. Read existing migrations — Do they operate on SnapshotState or dict?
3. Check: Can migrations operate on Pydantic model_dump() dicts?
4. Verify: Will existing migrations still work after DTO conversion?
5. Test: Apply a migration to a dict, then construct SimulationSnapshot

**Method**:

```python
# Test migration compatibility
snapshot_dict = {...}  # Legacy format
migrated_dict = migration_registry.apply_path(path, snapshot_dict, config)
snapshot_dto = SimulationSnapshot.model_validate(migrated_dict)  # Should work
```

**Expected Findings**:

- Migrations operate on dict layer (below DTO)
- SnapshotManager.load() converts dict → DTO after migrations
- No changes needed to migration system

**Deliverable**: Migration compatibility analysis

**Gate Condition**: Migration system compatibility confirmed, no blocker found

---

**Stage 0.6: Map Import Dependency Graph** (0.5 hours)

**Objective**: Identify all files importing SnapshotState and their relationships

**Tasks**:

1. Find all imports: `grep -r "from townlet.snapshots.state import SnapshotState" src/ tests/ --files-with-matches`
2. Find all imports: `grep -r "from townlet.snapshots import SnapshotState" src/ tests/ --files-with-matches`
3. Build dependency graph (which files depend on which)
4. Identify optimal update order (leaf nodes first)
5. Flag circular dependencies if any

**Expected Findings**:

- ~15-20 files importing SnapshotState
- Clear dependency order: tests → runtime → ports → core
- No circular dependencies

**Deliverable**: `WP3.2_IMPORT_GRAPH.md` with:

- Complete list of files to update
- Optimal update order
- Estimated effort per file

**Gate Condition**: Import graph complete, update order determined

---

**Stage 0.7: Validate Against Real Snapshot Files** (0.5 hours)

**Objective**: Test our DTO schema against actual persisted snapshots

**Tasks**:

1. Find example snapshot files: `find . -name "snapshot-*.json" | head -3`
2. Load snapshot JSON and extract state dict
3. Attempt to construct SimulationSnapshot from dict: `SimulationSnapshot.model_validate(state_dict)`
4. Document validation errors (field mismatches, type errors, etc.)
5. Adjust DTO schema if needed (relax constraints, add missing fields)

**Method**:

```python
import json
from pathlib import Path
from townlet.dto import SimulationSnapshot

# Load real snapshot
snapshot_file = Path("snapshots/snapshot-12345.json")
data = json.loads(snapshot_file.read_text())
state_dict = data["state"]

# Try to construct DTO
try:
    snapshot = SimulationSnapshot.model_validate(state_dict)
    print("✅ DTO schema matches real data")
except ValidationError as e:
    print(f"❌ Validation errors: {e}")
    # Analyze and document required schema adjustments
```

**Expected Findings**:

- Minor schema adjustments needed (optional fields, type coercions)
- Most fields validate successfully
- Clear list of schema fixes before Phase 1

**Deliverable**: Validation report + list of required DTO schema adjustments

**Gate Condition**: DTO schema validated against real data, adjustments made, re-validation passes

---

**Phase 0 Summary**

**Total Time**: 2-3 hours
**Deliverables**:

1. `WP3.2_TEST_AUDIT.md` — Test pattern analysis
2. `WP3.2_FIELD_MAPPING.md` — Subsystem field mappings
3. DTO schema adjustments based on real data
4. Baseline test results + performance metrics
5. Migration compatibility confirmation
6. `WP3.2_IMPORT_GRAPH.md` — Update order strategy

**Risk Reduction**:

- ✅ Accurate test effort estimate
- ✅ Field mapping mismatches identified upfront
- ✅ DTO schema validated against real data
- ✅ Migration system compatibility verified
- ✅ Import update order optimized
- ✅ No surprises during Phase 1 implementation

**Gate Condition**: All Stage 0 deliverables complete, no blockers found, team approves proceeding to Phase 1

---

### Phase 1: Core Conversion (4-6 hours)

**Stage 1.1: Rewrite `snapshot_from_world()`** (2 hours)

**Objective**: Build `SimulationSnapshot` from world state

**Tasks**:

1. Update function signature: `-> SimulationSnapshot`
2. Convert agent dict building → `AgentSummary` construction
3. Convert queue dict → `QueueSnapshot` construction
4. Convert employment dict → `EmploymentSnapshot` construction
5. Convert lifecycle dict → `LifecycleSnapshot` construction
6. Convert perturbations dict → `PerturbationSnapshot` construction
7. Convert affordances dict → `AffordanceSnapshot` construction
8. Convert embeddings dict → `EmbeddingSnapshot` construction
9. Convert stability dict → `StabilitySnapshot` construction
10. Convert promotion dict → `PromotionSnapshot` construction
11. Convert telemetry dict → `TelemetrySnapshot` construction
12. Convert identity dict → `IdentitySnapshot` construction
13. Convert migrations dict → `MigrationSnapshot` construction
14. Return `SimulationSnapshot` with all nested DTOs

**Implementation Pattern**:

```python
# OLD (dict soup)
agents_payload: dict[str, dict[str, Any]] = {}
for agent_id, agent_snapshot in adapter.agent_snapshots_view().items():
    agents_payload[agent_id] = {
        "position": list(agent_snapshot.position),
        "needs": dict(agent_snapshot.needs),
        # ... 15 more dict assignments
    }

# NEW (DTO construction)
from townlet.dto.world import AgentSummary

agents: dict[str, AgentSummary] = {}
for agent_id, agent_snapshot in adapter.agent_snapshots_view().items():
    agents[agent_id] = AgentSummary(
        agent_id=agent_id,
        position=agent_snapshot.position,
        needs=agent_snapshot.needs,
        # ... Pydantic validates all fields
    )
```

**Gate Condition**: Function compiles, returns `SimulationSnapshot`, mypy clean

---

**Stage 1.2: Rewrite `apply_snapshot_to_world()`** (1.5 hours)

**Objective**: Extract data from `SimulationSnapshot` to restore world

**Tasks**:

1. Update function signature: `snapshot: SimulationSnapshot`
2. Extract agents from `AgentSummary` DTOs
3. Extract queues from `QueueSnapshot`
4. Extract employment from `EmploymentSnapshot`
5. Extract lifecycle from `LifecycleSnapshot`
6. Extract perturbations from `PerturbationSnapshot`
7. Extract affordances from `AffordanceSnapshot`
8. Extract embeddings from `EmbeddingSnapshot`
9. Extract stability from `StabilitySnapshot` (dict for now)
10. Extract promotion from `PromotionSnapshot` (dict for now)

**Implementation Pattern**:

```python
# OLD (dict extraction)
for agent_id, payload in snapshot.agents.items():
    position = tuple(payload.get("position", (0, 0)))
    needs = dict(payload.get("needs", {}))
    # ... manual dict.get() with defaults

# NEW (DTO extraction)
for agent_id, agent_dto in snapshot.agents.items():
    position = agent_dto.position  # Already tuple
    needs = agent_dto.needs        # Already dict
    # ... type-safe access, no defaults needed
```

**Gate Condition**: Function compiles, accepts `SimulationSnapshot`, mypy clean

---

**Stage 1.3: Update `apply_snapshot_to_telemetry()`** (0.5 hours)

**Objective**: Extract telemetry state from `SimulationSnapshot`

**Tasks**:

1. Update function signature: `snapshot: SimulationSnapshot`
2. Extract telemetry from `TelemetrySnapshot` → dict for import_state()
3. Extract stability metrics from `StabilitySnapshot.latest_metrics`
4. Extract identity from `IdentitySnapshot` → dict for update_policy_identity()
5. Extract migrations from `MigrationSnapshot`

**Gate Condition**: Function compiles, mypy clean

---

**Stage 1.4: Update `SnapshotManager`** (1 hour)

**Objective**: Use Pydantic serialization instead of dataclass methods

**Tasks**:

1. Update `save()` signature: `state: SimulationSnapshot`
2. Replace `state.as_dict()` → `state.model_dump()`
3. Update `load()` return type: `-> SimulationSnapshot`
4. Replace `SnapshotState.from_dict()` → `SimulationSnapshot.model_validate()`
5. Handle Pydantic validation errors with clear messages

**Implementation Pattern**:

```python
# OLD (dataclass)
def save(self, state: SnapshotState) -> Path:
    document = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "state": state.as_dict(),  # Manual dict building
    }

# NEW (Pydantic)
def save(self, state: SimulationSnapshot) -> Path:
    document = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "state": state.model_dump(),  # Pydantic serialization
    }
```

**Gate Condition**: Manager compiles, save/load signatures updated, mypy clean

---

### Phase 2: Protocol & Ports (1 hour)

**Stage 2.1: Update Port Protocol** (0.5 hours)

**Objective**: Enforce DTO boundary in WorldRuntime protocol

**Tasks**:

1. Update `ports/world.py`: `def snapshot(...) -> SimulationSnapshot`
2. Remove `SnapshotState` import
3. Add `SimulationSnapshot` import from `townlet.dto`

**Implementation**:

```python
# ports/world.py
from townlet.dto import SimulationSnapshot

class WorldRuntime(Protocol):
    def snapshot(
        self,
        *,
        config: Any | None = None,
        telemetry: TelemetrySinkProtocol | None = None,
        stability: Any | None = None,
        promotion: Any | None = None,
        rng_streams: Mapping[str, Any] | None = None,
        identity: Mapping[str, object] | None = None,
    ) -> SimulationSnapshot: ...  # DTO enforced
```

**Gate Condition**: Protocol updated, mypy clean

---

**Stage 2.2: Update Adapter Implementations** (0.5 hours)

**Objective**: Update concrete implementations to return `SimulationSnapshot`

**Tasks**:

1. Update `world/runtime.py`: `WorldRuntime.snapshot()` → `SimulationSnapshot`
2. Update `adapters/world_default.py`: `snapshot()` → `SimulationSnapshot`
3. Update `testing/dummy_world.py`: `snapshot()` → `SimulationSnapshot`
4. Import `SimulationSnapshot` from `townlet.dto`

**Gate Condition**: All implementations return `SimulationSnapshot`, mypy clean

---

### Phase 3: Import Migration (1 hour)

**Stage 3.1: Update Imports** (1 hour)

**Objective**: Replace all `SnapshotState` imports with `SimulationSnapshot`

**Files to Update** (~15 files):

```
src/townlet/snapshots/__init__.py
src/townlet/core/sim_loop.py
src/townlet/world/runtime.py
src/townlet/adapters/world_default.py
src/townlet/testing/dummy_world.py
tests/test_snapshot_manager.py
tests/test_sim_loop_snapshot.py
tests/test_snapshot_migrations.py
# ... ~10 more test files
```

**Implementation Pattern**:

```python
# OLD
from townlet.snapshots.state import SnapshotState

# NEW
from townlet.dto import SimulationSnapshot
```

**Gate Condition**: All imports updated, no `SnapshotState` references, mypy clean

---

### Phase 4: Testing & Validation (2-3 hours)

**Stage 4.1: Fix Snapshot Tests** (1.5 hours)

**Objective**: Update test assertions for Pydantic DTOs

**Expected Failures** (~35 tests):

- `test_snapshot_manager.py` (~8 tests)
- `test_sim_loop_snapshot.py` (~5 tests)
- `test_snapshot_migrations.py` (~6 tests)
- Integration tests using snapshots (~16 tests)

**Common Fixes**:

```python
# OLD (dataclass attribute access)
assert snapshot.agents["agent_1"]["position"] == (5, 5)

# NEW (DTO attribute access)
assert snapshot.agents["agent_1"].position == (5, 5)
```

**Gate Condition**: All snapshot tests passing (806+ tests)

---

**Stage 4.2: Add DTO Validation Tests** (0.5 hours)

**Objective**: Test Pydantic validation catches errors

**New Tests**:

```python
def test_simulation_snapshot_validates_required_fields():
    """SimulationSnapshot rejects missing required fields."""
    with pytest.raises(ValidationError):
        SimulationSnapshot()  # Missing config_id, tick, agents, etc.

def test_simulation_snapshot_validates_agent_summary():
    """AgentSummary validates position tuple."""
    with pytest.raises(ValidationError):
        AgentSummary(
            agent_id="alice",
            position="invalid",  # Should be tuple[int, int]
            needs={},
            wallet=100.0,
        )

def test_snapshot_round_trip_preserves_data():
    """Save → load preserves all data."""
    original = SimulationSnapshot(...)
    data = original.model_dump()
    restored = SimulationSnapshot.model_validate(data)
    assert restored == original
```

**Gate Condition**: Validation tests passing, coverage maintained

---

**Stage 4.3: Integration Testing** (1 hour)

**Objective**: Verify full snapshot workflow

**Test Scenarios**:

1. **Save/Load Round-Trip**: Create world → save → load → verify identical
2. **Migration Compatibility**: Load legacy JSON snapshot → convert to DTO
3. **RNG Determinism**: Save RNG streams → restore → verify same sequence
4. **Partial Snapshots**: Test with missing optional fields (defaults applied)
5. **Validation Errors**: Test corrupted snapshot JSON (Pydantic catches)

**Gate Condition**: All integration tests passing, no regressions

---

### Phase 5: Cleanup & Documentation (1-2 hours)

**Stage 5.1: Delete Legacy Code** (0.5 hours)

**Objective**: Remove replaced `SnapshotState` implementation

**Tasks**:

1. Delete `SnapshotState` class from `snapshots/state.py`
2. Delete `SnapshotState.as_dict()` method
3. Delete `SnapshotState.from_dict()` method
4. Remove `@dataclass` import if unused
5. Update `snapshots/__init__.py` exports

**Verification**:

```bash
grep -r "SnapshotState" src/ tests/  # Should find 0 matches
grep -r "as_dict" src/townlet/snapshots/  # Should find 0 matches
grep -r "from_dict" src/townlet/snapshots/  # Should find 0 matches
```

**Gate Condition**: No `SnapshotState` references remain, all tests pass

---

**Stage 5.2: Author ADR-003** (1 hour)

**Objective**: Document DTO boundary strategy and consolidation pattern

**Structure**:

```markdown
# ADR-003: DTO Boundary Strategy

## Status: Accepted

## Context
Need typed boundaries between subsystems (observations, telemetry, snapshots)

## Decision
Use Pydantic v2 DTOs for all inter-subsystem boundaries

## Consequences
+ Type safety via validation
+ Self-documenting interfaces
+ Consistent serialization
- Overhead for infrequent operations (acceptable)

## Implementation Pattern
[Document the consolidation pattern used in WP3.2]

## Reference Implementation
WP3.2 snapshot consolidation (SimulationSnapshot)
```

**Gate Condition**: ADR-003 committed, reviewed

---

**Stage 5.3: Update Documentation** (0.5 hours)

**Objective**: Document changes in CLAUDE.md and guides

**Tasks**:

1. Update CLAUDE.md "Snapshots" section
2. Update "Common Patterns" → "Snapshot compatibility"
3. Add "DTO Consolidation Pattern" section
4. Update architecture diagrams if needed

**Content**:

```markdown
## DTO Consolidation Pattern (Reference: WP3.2)

When consolidating legacy dict-based interfaces to Pydantic DTOs:

1. **Create nested DTOs** for each subsystem (Lifecycle, Perturbations, etc.)
2. **Top-level DTO** composes nested DTOs
3. **Conversion layer** builds DTOs from export_state() dicts
4. **Restoration layer** extracts dicts from DTOs for import_state()
5. **Port protocols** enforce DTO types
6. **Delete legacy** dataclass/dict builders

See `SimulationSnapshot` in `townlet/dto/world.py` for reference.
```

**Gate Condition**: Documentation updated, examples tested

---

## Risk Assessment

### High Risk

**None identified** — Comprehensive test coverage mitigates snapshot corruption risks.

### Medium Risk

1. **Test Breakage Cascade** (Likelihood: High, Impact: Medium)
   - **Mitigation**: Fix tests incrementally per stage, checkpoint after each phase
   - **Rollback**: Git revert if >50% tests fail

2. **Pydantic Validation Too Strict** (Likelihood: Medium, Impact: Low)
   - **Mitigation**: Use `Field(default_factory=...)` for optional fields
   - **Rollback**: Relax validation constraints if needed

3. **Migration Compatibility** (Likelihood: Low, Impact: Medium)
   - **Mitigation**: Keep schema version 1.6, test legacy snapshot loading
   - **Rollback**: Migration shim if needed

### Low Risk

1. **Performance Regression** (Likelihood: Low, Impact: Very Low)
   - **Mitigation**: Snapshots are infrequent (explicit saves only)
   - **Impact**: Even 2x slower is negligible

---

## Testing Strategy

### Unit Tests

**New Tests** (~10 tests):

- `test_simulation_snapshot_validates_fields()` — Required field validation
- `test_agent_summary_validates_types()` — Type validation
- `test_lifecycle_snapshot_defaults()` — Default values
- `test_perturbation_snapshot_nested()` — Nested DTO validation
- `test_snapshot_model_dump_json()` — JSON serialization
- `test_snapshot_model_validate_dict()` — Dict deserialization
- `test_snapshot_immutability()` — Frozen behavior
- `test_snapshot_mutation_after_restore()` — Unfrozen after load

**Modified Tests** (~35 tests):

- All tests in `test_snapshot_manager.py` — Update assertions
- All tests in `test_sim_loop_snapshot.py` — Update fixtures
- All tests in `test_snapshot_migrations.py` — Update validation

### Integration Tests

**Scenarios**:

1. **Full Save/Load Cycle**: 100-tick simulation → save → load → continue 100 more ticks → verify determinism
2. **Legacy Snapshot Loading**: Load JSON from previous schema → validate conversion
3. **RNG Stream Capture**: Save mid-simulation → load → verify RNG state identical
4. **Partial Snapshots**: Test with minimal required fields → verify defaults applied
5. **Corrupted Snapshots**: Invalid JSON → verify Pydantic ValidationError with clear message

### Regression Tests

**Existing Test Suite** (806 tests):

- All must pass after conversion
- No coverage drop (maintain 85%+)
- No performance regression in CI (<5% slowdown acceptable)

---

## Rollback Plan

### Checkpoint Strategy

**Commit after each phase**:

1. Commit after Phase 1 (core conversion) — "WP3.2: Core snapshot DTO conversion"
2. Commit after Phase 2 (protocols) — "WP3.2: Port protocol DTO enforcement"
3. Commit after Phase 3 (imports) — "WP3.2: Import migration complete"
4. Commit after Phase 4 (testing) — "WP3.2: Tests passing"
5. Commit after Phase 5 (cleanup) — "WP3.2: Legacy code removed, docs complete"

### Rollback Triggers

**Abort if**:

- More than 50% of tests fail after Phase 4.1
- Mypy errors exceed 10 after any stage
- Pydantic validation blocks valid snapshots
- Performance regression >20% (unlikely but critical)

### Rollback Procedure

1. `git revert <phase-commit>` — Revert to last good checkpoint
2. Analyze failure root cause
3. Create targeted fix branch
4. Re-attempt phase with fix

### Compatibility Shim (If Needed)

If rollback impossible due to external dependencies:

```python
# snapshots/compat.py
def snapshot_state_to_dto(state: SnapshotState) -> SimulationSnapshot:
    """Convert legacy SnapshotState to SimulationSnapshot."""
    return SimulationSnapshot.model_validate(state.as_dict())

def dto_to_snapshot_state(dto: SimulationSnapshot) -> SnapshotState:
    """Convert SimulationSnapshot to legacy SnapshotState."""
    return SnapshotState.from_dict(dto.model_dump())
```

---

## Dependencies

### Prerequisites

- ✅ WP3.1 complete (observation DTOs migrated)
- ✅ WP4 complete (policy DTOs exist)
- ✅ `SimulationSnapshot` DTOs authored (223 lines, committed)

### Blocking

**None** — WP3.2 is self-contained

### Blocked By WP3.2

- ADR-003 authoring (blocked until pattern documented)
- Future DTO consolidations (blocked until exemplar complete)

---

## Success Criteria

### Must Have (Gate Conditions)

1. ✅ `snapshot_from_world()` returns `SimulationSnapshot`
2. ✅ `apply_snapshot_to_world()` accepts `SimulationSnapshot`
3. ✅ `SnapshotManager` uses Pydantic serialization
4. ✅ Port protocol enforces DTO boundary
5. ✅ All 806+ tests passing
6. ✅ Mypy clean (0 errors)
7. ✅ Test coverage maintained (≥85%)
8. ✅ Legacy `SnapshotState` deleted
9. ✅ ADR-003 authored and committed
10. ✅ Documentation updated

### Should Have (Quality Goals)

1. ✅ Validation tests for Pydantic DTOs
2. ✅ Integration test for save/load round-trip
3. ✅ Legacy snapshot loading test
4. ✅ DTO consolidation pattern documented

### Could Have (Stretch Goals)

1. ⭕ Performance benchmarks (before/after)
2. ⭕ Snapshot schema evolution guide
3. ⭕ Migration from schema 1.5 → 1.6 documented

---

## Timeline Estimate

**Total Duration**: 1-2 days focused work

### Optimistic (1 day)

- Phase 1: 4 hours
- Phase 2: 1 hour
- Phase 3: 0.5 hours
- Phase 4: 1.5 hours
- Phase 5: 1 hour
- **Total**: 8 hours

### Realistic (1.5 days)

- Phase 1: 6 hours
- Phase 2: 1 hour
- Phase 3: 1 hour
- Phase 4: 2.5 hours
- Phase 5: 1.5 hours
- **Total**: 12 hours

### Pessimistic (2 days)

- Phase 1: 8 hours (complex subsystem edge cases)
- Phase 2: 1.5 hours
- Phase 3: 1.5 hours
- Phase 4: 4 hours (extensive test fixes)
- Phase 5: 2 hours
- **Total**: 17 hours

---

## Open Questions

1. **Q**: Should we add a `ticks_per_day` field to `SimulationSnapshot`?
   **A**: Yes, already included in DTO (line 168)

2. **Q**: What about `_RespawnTicket` in lifecycle?
   **A**: Keep internal to LifecycleManager, not persisted in snapshots

3. **Q**: Handle Pydantic v1 → v2 migration?
   **A**: N/A, codebase already uses Pydantic v2

4. **Q**: Should DTOs be frozen after construction?
   **A**: No, `frozen=False` to allow mutation during restoration (line 163)

5. **Q**: Validate RNG stream format?
   **A**: No, keep as opaque `str`, validation happens in decode_rng_state()

---

## References

**Related Documents**:

- ADR-001: Port and Factory Registry
- ADR-002: World Modularisation
- ADR-004: Policy Training DTOs (reference implementation)
- WP3: Typed DTO Boundary
- WP3.1: Stage 6 Recovery
- WP4: Policy Training Strategies

**Code References**:

- `src/townlet/dto/world.py:137-196` — SimulationSnapshot definition
- `src/townlet/snapshots/state.py:54-257` — Legacy SnapshotState (to be replaced)
- `src/townlet/dto/policy.py` — Policy DTOs (similar pattern)

**External Resources**:

- [Pydantic v2 Documentation](https://docs.pydantic.dev/)
- [Pydantic model_dump() API](https://docs.pydantic.dev/usage/exporting_models/)
- [Pydantic model_validate() API](https://docs.pydantic.dev/usage/models/#helper-functions)

---

## Approval

**Author**: Claude Code
**Reviewer**: TBD
**Status**: DRAFT (Awaiting approval to proceed)

---

**End of WP3.2 Specification**
