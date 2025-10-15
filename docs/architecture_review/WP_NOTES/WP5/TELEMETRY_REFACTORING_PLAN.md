# WP5 Telemetry Package: Mypy Strict Compliance Plan

**Priority**: STRATEGIC (User-designated high priority)
**Status**: PLANNING
**Date**: 2025-10-14
**Work Package**: WP5 (Final Hardening and Quality Gates)

---

## Executive Summary

The telemetry package has **189 mypy strict errors** across 6 files (~5,000 LOC), representing **72% of all remaining type errors** in the codebase. This plan details a phased approach to achieve 100% mypy strict compliance for the telemetry system.

### Quick Stats

| Metric | Value |
|--------|-------|
| Total errors | 189 |
| Files affected | 6 |
| Lines of code | ~5,000 |
| Estimated effort | 12-16 hours (1.5-2 days) |
| Complexity | HIGH |
| Risk level | MEDIUM |

### Error Distribution

| File | Errors | % of Total | Priority |
|------|-------:|----------:|----------|
| `publisher.py` | 164 | 87% | P0 (Critical) |
| `aggregation/aggregator.py` | 13 | 7% | P1 (High) |
| `transform/transforms.py` | 5 | 3% | P2 (Medium) |
| `fallback.py` | 5 | 3% | P2 (Medium) |
| `worker.py` | 2 | 1% | P3 (Low) |

---

## Architecture Overview

### Current State

The telemetry system follows a **layered pipeline architecture**:

```
SimulationLoop
    ↓
TelemetrySinkProtocol (port interface)
    ↓
TelemetryPublisher (main implementation)
    ↓
┌─────────────────────────────────────┐
│ Aggregation Layer                   │
│  - TelemetryAggregator              │
│  - StreamPayloadBuilder             │
│  - Collector modules                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Transform Layer                     │
│  - SchemaValidationTransform        │
│  - EnsureFieldsTransform            │
│  - RedactFieldsTransform            │
│  - SnapshotEventNormalizer          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Transport Layer                     │
│  - TelemetryWorkerManager           │
│  - TransportBuffer                  │
│  - Stdout/File/TCP transports       │
└─────────────────────────────────────┘
```

### Key Components

**TelemetryPublisher** (`publisher.py`):
- Main telemetry sink implementation
- Implements `TelemetrySinkProtocol` (43 methods)
- Manages state caching for latest snapshots (20+ cached dictionaries)
- Orchestrates aggregation → transform → transport pipeline
- Handles console command buffering and authentication
- **Size**: ~1,500 LOC (30% of telemetry package)

**TelemetryAggregator** (`aggregation/aggregator.py`):
- Collects world state and builds telemetry events
- Interfaces with `StreamPayloadBuilder` for structured payloads
- Handles KPI history tracking
- **Size**: ~400 LOC

**Transform Pipeline** (`transform/transforms.py`):
- Schema validation using JSON schemas
- Field redaction for sensitive data
- Event normalization and formatting
- **Size**: ~600 LOC

**Worker Manager** (`worker.py`):
- Background thread management for async telemetry
- Buffering and backpressure handling
- Retry logic and error recovery
- **Size**: ~300 LOC

---

## Error Analysis

### Error Categories

Categorized by type and fix complexity:

#### Category A: Object Type Narrowing (40% - 76 errors)

**Issue**: Accessing attributes/methods on `object` type without narrowing

**Pattern**:
```python
# Current (fails mypy strict)
payload = dict(some_object)  # object type
value = float(some_object)   # object type
items = some_object.items()  # object has no attribute "items"

# Fix needed
if not isinstance(some_object, dict):
    raise TypeError(...)
payload = dict(some_object)  # Now mypy knows it's a dict
```

**Files affected**:
- `publisher.py`: ~60 occurrences
- `aggregation/aggregator.py`: ~10 occurrences
- `transform/transforms.py`: ~6 occurrences

**Estimated effort**: 4-6 hours

---

#### Category B: Mapping vs dict Mismatches (25% - 47 errors)

**Issue**: Functions accept `Mapping[str, Any]` but code tries to mutate with `setdefault()`, `update()`, etc.

**Pattern**:
```python
# Current (fails mypy strict)
def process(snapshot: Mapping[str, Any]) -> None:
    snapshot.setdefault("key", {})  # Mapping has no attribute "setdefault"

# Fix option 1: Change signature to dict
def process(snapshot: dict[str, Any]) -> None:
    snapshot.setdefault("key", {})

# Fix option 2: Convert to dict internally
def process(snapshot: Mapping[str, Any]) -> None:
    working_snapshot = dict(snapshot)
    working_snapshot.setdefault("key", {})
```

**Files affected**:
- `publisher.py`: ~40 occurrences (mostly in state caching methods)
- `aggregation/aggregator.py`: ~7 occurrences

**Decision needed**: Should telemetry methods accept immutable `Mapping` or mutable `dict`?

**Recommendation**: Use `dict` for internal state, `Mapping` for protocol boundaries

**Estimated effort**: 3-4 hours

---

#### Category C: Protocol Signature Mismatches (15% - 28 errors)

**Issue**: Implementation methods don't match protocol signatures

**Pattern**:
```python
# Protocol (TelemetrySinkProtocol)
def emit_event(self, event: TelemetryEventDTO) -> None:
    ...

# Implementation (StubTelemetrySink)
def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
    # Signature mismatch!
    ...
```

**Files affected**:
- `fallback.py`: 5 errors (stub implementation out of sync)
- `publisher.py`: ~20 errors (method signature drift)
- `aggregation/aggregator.py`: ~3 errors

**Root cause**: Protocol evolved but implementations not updated

**Fix approach**:
1. Audit all `TelemetrySinkProtocol` methods
2. Update stub and concrete implementations to match
3. Add protocol runtime checks with `isinstance()`

**Estimated effort**: 2-3 hours

---

#### Category D: Type Alias Misuse (10% - 19 errors)

**Issue**: Incorrect use of type aliases or missing type parameters

**Pattern**:
```python
# Current
transforms: list[object] = []  # Should be list[TelemetryTransformProtocol]
schema_by_kind: dict[str, object] = {}  # Should be dict[str, CompiledSchema]

# Fix
transforms: list[TelemetryTransformProtocol] = []
schema_by_kind: dict[str, CompiledSchema] = {}
```

**Files affected**:
- `publisher.py`: ~15 errors
- `transform/transforms.py`: ~4 errors

**Estimated effort**: 1-2 hours

---

#### Category E: Unreachable Code (5% - 10 errors)

**Issue**: Mypy determines some code is unreachable due to type narrowing

**Pattern**:
```python
# Current
if isinstance(value, dict):
    return process_dict(value)
if value:  # Unreachable! (mypy knows value is dict or None from context)
    return process_other(value)
```

**Files affected**:
- `publisher.py`: ~6 errors
- `worker.py`: ~2 errors
- `fallback.py`: ~2 errors

**Fix approach**: Remove dead code or fix logic flow

**Estimated effort**: 1 hour

---

#### Category F: Any Propagation (5% - 9 errors)

**Issue**: Returning `Any` from functions declared to return specific types

**Pattern**:
```python
# Current
def get_snapshot() -> dict[str, float]:
    return some_any_value  # Returning Any from function declared to return dict[str, float]

# Fix
def get_snapshot() -> dict[str, float]:
    result = some_any_value
    if not isinstance(result, dict):
        return {}
    return {k: float(v) for k, v in result.items()}
```

**Files affected**:
- `publisher.py`: ~6 errors
- `aggregation/aggregator.py`: ~3 errors

**Estimated effort**: 1-2 hours

---

## Phased Implementation Plan

### Phase 1: Protocol Alignment (3-4 hours)

**Goal**: Fix all protocol signature mismatches and ensure implementations satisfy protocols

**Tasks**:
1. **Audit TelemetrySinkProtocol** (30 min)
   - Document all 43 method signatures
   - Identify which methods have DTO vs dict parameters
   - Check if return types are correct

2. **Fix fallback.py** (1 hour)
   - Update `StubTelemetrySink.emit_event()` signature to match protocol
   - Add stub implementations for missing protocol methods
   - Verify all 5 errors resolved

3. **Fix publisher.py protocol mismatches** (1.5-2 hours)
   - Update method signatures to match protocol
   - Fix ~20 protocol-related errors
   - Add `assert isinstance()` checks where needed

4. **Fix aggregator.py protocol mismatches** (30 min)
   - Update `collect_tick()` signature
   - Fix parameter type mismatches (~3 errors)

**Deliverables**:
- Protocol compliance checklist
- Fixed stub implementation
- ~28 errors resolved

**Risk**: LOW - Mechanical fixes, clear requirements

---

### Phase 2: Type Narrowing (4-6 hours)

**Goal**: Add proper type narrowing for all `object` → concrete type conversions

**Tasks**:
1. **Create type guard helpers** (1 hour)
   ```python
   def ensure_dict(value: object, context: str) -> dict[str, Any]:
       if not isinstance(value, dict):
           raise TypeError(f"{context}: expected dict, got {type(value)}")
       return value

   def ensure_float(value: object, context: str) -> float:
       if not isinstance(value, (int, float)):
           raise TypeError(f"{context}: expected float, got {type(value)}")
       return float(value)
   ```

2. **Fix publisher.py object narrowing** (2-3 hours)
   - Add type narrowing for ~60 `object` access errors
   - Use helper functions for consistency
   - Focus on state caching methods

3. **Fix aggregator.py object narrowing** (1 hour)
   - Add type narrowing for ~10 errors
   - Focus on `StreamPayloadBuilder.build()` call sites

4. **Fix transforms.py object narrowing** (1 hour)
   - Add type narrowing for ~6 errors
   - Focus on schema validation logic

**Deliverables**:
- Type guard helper module
- ~76 errors resolved

**Risk**: MEDIUM - Requires understanding data flow, potential runtime errors if assumptions wrong

---

### Phase 3: Mapping/Dict Consistency (3-4 hours)

**Goal**: Resolve all Mapping vs dict type mismatches

**Tasks**:
1. **Design decision: Internal types** (30 min)
   - Document which methods need mutable vs immutable
   - Create migration guide for method signatures

   **Recommendation**:
   - Protocol boundaries: `Mapping[str, T]` (immutable)
   - Internal state: `dict[str, T]` (mutable)
   - Snapshot returns: `Mapping[str, T]` (immutable view)

2. **Fix publisher.py Mapping mismatches** (2-2.5 hours)
   - Update ~40 method calls/assignments
   - Change signatures where appropriate
   - Use `dict()` conversion where needed

3. **Fix aggregator.py Mapping mismatches** (30-60 min)
   - Update ~7 method calls
   - Align with protocol signatures

**Deliverables**:
- Type consistency guidelines doc
- ~47 errors resolved

**Risk**: LOW-MEDIUM - Mostly mechanical, but need to ensure no unintended side effects

---

### Phase 4: Type Aliases & Cleanup (2-3 hours)

**Goal**: Fix type alias misuse, unreachable code, and Any propagation

**Tasks**:
1. **Fix type alias usage** (1 hour)
   - Replace `object` with proper type aliases
   - Add type parameters where missing
   - ~19 errors resolved

2. **Remove unreachable code** (30-60 min)
   - Audit unreachable blocks
   - Remove or fix logic errors
   - ~10 errors resolved

3. **Fix Any propagation** (30-60 min)
   - Add type narrowing before returns
   - Use type guards for validation
   - ~9 errors resolved

**Deliverables**:
- ~38 errors resolved
- Cleaner, more maintainable code

**Risk**: LOW - Mostly cleanup work

---

### Phase 5: Integration & Testing (1-2 hours)

**Goal**: Verify all fixes, run tests, ensure no regressions

**Tasks**:
1. **Mypy verification** (15 min)
   ```bash
   .venv/bin/mypy src/townlet/telemetry --strict
   # Target: 0 errors
   ```

2. **Test suite execution** (30 min)
   ```bash
   pytest tests/test_telemetry_*.py -xvs
   pytest tests/test_observer_ui_dashboard.py -xvs
   ```

3. **Smoke test simulation** (15 min)
   ```bash
   python scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 100 --stream-telemetry
   ```

4. **Documentation updates** (30 min)
   - Update PHASE2 completion report
   - Document any architectural changes
   - Update CLAUDE.md if patterns changed

**Deliverables**:
- 0 mypy strict errors in telemetry package
- All tests passing
- Updated documentation

**Risk**: MEDIUM - Integration issues may surface

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing functionality | MEDIUM | HIGH | Run tests after each phase; smoke test simulation |
| Type narrowing assumptions wrong | MEDIUM | HIGH | Add comprehensive isinstance checks; graceful failures |
| Protocol changes affect other code | LOW | HIGH | Audit all TelemetrySinkProtocol usage before changes |
| Performance regression | LOW | MEDIUM | Profile telemetry hot paths before/after |
| Thread safety issues | LOW | HIGH | Review worker.py changes carefully; existing locks should be sufficient |

### Schedule Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Errors harder to fix than estimated | MEDIUM | MEDIUM | Focus on high-value fixes; use type: ignore for edge cases |
| Unforeseen dependencies | MEDIUM | MEDIUM | Complete Phase 1 first to understand scope |
| Testing reveals issues | MEDIUM | HIGH | Allocate buffer time in Phase 5 |

### Rollback Plan

If issues arise during implementation:

1. **Immediate**: Revert to last passing commit
   ```bash
   git revert HEAD~N  # Revert last N commits
   ```

2. **Recovery time**: <1 hour (all changes in feature branch)

3. **Fallback option**: Use `type: ignore` comments strategically
   - Mark complex sections with `# type: ignore[<error-code>]  # TODO: Fix in Phase X`
   - Continue with other phases
   - Revisit marked sections in separate effort

---

## Effort Estimation

### By Phase

| Phase | Hours | Confidence |
|-------|------:|------------|
| Phase 1: Protocol Alignment | 3-4 | HIGH |
| Phase 2: Type Narrowing | 4-6 | MEDIUM |
| Phase 3: Mapping/Dict | 3-4 | HIGH |
| Phase 4: Aliases/Cleanup | 2-3 | HIGH |
| Phase 5: Integration/Testing | 1-2 | MEDIUM |
| **Total** | **13-19** | **MEDIUM** |

**Recommended estimate**: 16 hours (2 full days)

### By Category

| Category | Errors | Hours | $/Error |
|----------|-------:|------:|--------:|
| Object narrowing | 76 | 4-6 | 4-5 min |
| Mapping/dict | 47 | 3-4 | 4-5 min |
| Protocol mismatches | 28 | 3-4 | 6-9 min |
| Type aliases | 19 | 1 | 3 min |
| Unreachable | 10 | 1 | 6 min |
| Any propagation | 9 | 1-2 | 7-13 min |

**Average**: ~5 minutes per error (factoring in testing & integration)

---

## Success Criteria

### Phase Completion

Each phase is considered complete when:
- ✅ All targeted errors resolved (mypy --strict passes for affected files)
- ✅ All tests passing (no regressions)
- ✅ Code review shows no degradation in readability
- ✅ Smoke test confirms telemetry still works

### Final Completion

Project is complete when:
- ✅ `mypy src/townlet/telemetry --strict` reports **0 errors**
- ✅ All telemetry tests passing (17+ test files)
- ✅ Simulation runs successfully with telemetry enabled
- ✅ Documentation updated with new patterns
- ✅ No performance regressions (telemetry overhead <2%)

---

## Dependencies & Prerequisites

### Before Starting

1. **Complete Phase 2 Option A** ✅ (Done - world, policy models, small packages)
2. **Review TelemetryEventDTO definition** - Ensure DTO structure is stable
3. **Document current test coverage** - Baseline for regression detection
4. **Create feature branch** - `feature/wp5-telemetry-types`

### External Dependencies

- None identified (telemetry is self-contained)

### Blocking Issues

- None identified

---

## Alternative Approaches

### Option A: Full Type Safety (Recommended)

**What**: Implement all 5 phases as described above

**Pros**:
- Complete type safety
- Better maintainability
- Catches bugs at compile time
- Aligns with WP5 goals

**Cons**:
- 16 hours effort
- Requires careful testing
- May surface hidden bugs

**Recommendation**: ✅ **USE THIS** - Strategic priority, worth the investment

---

### Option B: Hybrid Approach

**What**: Fix Categories A-C (80% of errors), defer D-F with type: ignore

**Pros**:
- 10-12 hours effort (25% faster)
- Core safety achieved
- Lower risk

**Cons**:
- Technical debt remains
- May need revisiting later

**Recommendation**: ⚠️ Use only if schedule pressure

---

### Option C: Minimal Compliance

**What**: Fix only protocol mismatches and critical type errors

**Pros**:
- 4-6 hours effort (60% faster)
- Unblocks other work

**Cons**:
- High technical debt
- Frequent type: ignore usage
- Lower code quality

**Recommendation**: ❌ Not recommended - defeats WP5 purpose

---

## Next Steps

### Immediate (Before Starting)

1. **User approval** - Confirm this plan aligns with strategic priorities
2. **Schedule allocation** - Block 2 full days for this work
3. **Create feature branch** - `git checkout -b feature/wp5-telemetry-types`
4. **Baseline metrics** - Capture test coverage and performance

### Phase 1 Kickoff

1. Audit TelemetrySinkProtocol (30 min)
2. Create Phase 1 checklist from audit
3. Begin with fallback.py (lowest risk)
4. Verify with mypy after each file

### Monitoring Progress

- Update this document after each phase
- Track errors remaining: `mypy src/townlet/telemetry --strict | tail -1`
- Run tests after each phase: `pytest tests/test_telemetry_*.py`

---

## Appendix A: File Details

### publisher.py (164 errors - 87%)

**Size**: 1,586 LOC
**Complexity**: Very High
**Key methods**: 43 protocol methods + internal helpers

**Error breakdown**:
- Object narrowing: 60 errors (37%)
- Mapping/dict: 40 errors (24%)
- Protocol mismatches: 20 errors (12%)
- Type aliases: 15 errors (9%)
- Unreachable: 6 errors (4%)
- Any propagation: 6 errors (4%)
- Other: 17 errors (10%)

**Hot spots** (methods with most errors):
1. `_extract_latest_snapshots()` - ~30 errors (object narrowing)
2. `latest_*()` accessor methods - ~25 errors (return type mismatches)
3. `import_state()` - ~15 errors (Mapping/dict)
4. `emit_event()` - ~10 errors (DTO handling)

---

### aggregation/aggregator.py (13 errors - 7%)

**Size**: 412 LOC
**Complexity**: Medium
**Key methods**: `collect_tick()`, `record_console_results()`

**Error breakdown**:
- Object narrowing: 10 errors (77%)
- Protocol mismatches: 3 errors (23%)

**Hot spots**:
1. `collect_tick()` - ~8 errors (parameter type mismatches)
2. `_build_payload()` - ~5 errors (object narrowing)

---

### transform/transforms.py (5 errors - 3%)

**Size**: 623 LOC
**Complexity**: Medium
**Key methods**: Schema validation, field redaction

**Error breakdown**:
- Object narrowing: 6 errors (100%)

**Hot spots**:
1. `SchemaValidationTransform.process()` - ~3 errors
2. `RedactFieldsTransform.process()` - ~2 errors

---

### fallback.py (5 errors - 3%)

**Size**: 186 LOC
**Complexity**: Low
**Key methods**: Stub implementations

**Error breakdown**:
- Protocol mismatches: 5 errors (100%)

**Issue**: `StubTelemetrySink.emit_event()` signature doesn't match protocol

**Fix**: Simple signature update

---

### worker.py (2 errors - 1%)

**Size**: 304 LOC
**Complexity**: Medium
**Key methods**: Background worker management

**Error breakdown**:
- Unreachable: 2 errors (100%)

**Issue**: Dead code in error handling paths

---

## Appendix B: Quick Reference

### Mypy Commands

```bash
# Check telemetry package
.venv/bin/mypy src/townlet/telemetry --strict --show-error-codes

# Check single file
.venv/bin/mypy src/townlet/telemetry/publisher.py --strict --show-error-codes

# Count errors by type
.venv/bin/mypy src/townlet/telemetry --strict --show-error-codes 2>&1 | \
  grep "error:" | cut -d: -f3- | sort | uniq -c | sort -rn
```

### Test Commands

```bash
# Run all telemetry tests
pytest tests/test_telemetry_*.py -xvs

# Run specific test
pytest tests/test_telemetry_client.py::test_event_emission -xvs

# Coverage report
pytest tests/test_telemetry_*.py --cov=src/townlet/telemetry --cov-report=html
```

### Smoke Test

```bash
# Quick simulation with telemetry
python scripts/run_simulation.py configs/examples/poc_hybrid.yaml \
  --ticks 100 --stream-telemetry | head -50
```

---

## Sign-Off

**Status**: READY FOR APPROVAL
**Estimated effort**: 16 hours (2 days)
**Confidence**: MEDIUM-HIGH
**Risk**: MEDIUM
**Priority**: STRATEGIC (user-designated)

**Recommendation**: Proceed with **Option A (Full Type Safety)** as the strategic value justifies the investment.

**Next action**: Await user approval, then begin Phase 1 (Protocol Alignment)
