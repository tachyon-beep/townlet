# WP3.1 WS2: Adapter Surface Cleanup - Detailed Execution Plan

**Status**: Ready for Execution
**Complexity**: Medium (estimated 30-45 min)
**Risk Level**: Medium (touches SimulationLoop core)
**Created**: 2025-10-13

---

## Executive Summary

Remove adapter escape hatch properties (`.context`, `.lifecycle_manager`, `.perturbation_scheduler`, `.backend`) by completing the ports-and-factories pattern. SimulationLoop currently uses `getattr()` to extract these from adapters; we'll refactor to use structured component returns instead.

**Gate Condition**: 0 references to escape hatch properties in src/, all adapter tests passing

---

## Current State Analysis

### Escape Hatch Properties (4 total)

1. **DefaultWorldAdapter.context** (src/townlet/adapters/world_default.py:175-179)
   ```python
   @property
   def context(self) -> WorldContext:
       """Expose the underlying world context (for orchestration/testing hooks)."""
       return self._context
   ```

2. **DefaultWorldAdapter.lifecycle_manager** (src/townlet/adapters/world_default.py:160-164)
   ```python
   @property
   def lifecycle_manager(self) -> LifecycleManager:
       if self._lifecycle is None:
           raise RuntimeError("Lifecycle manager unavailable on default world adapter")
       return self._lifecycle
   ```

3. **DefaultWorldAdapter.perturbation_scheduler** (src/townlet/adapters/world_default.py:166-170)
   ```python
   @property
   def perturbation_scheduler(self) -> PerturbationScheduler:
       if self._perturbations is None:
           raise RuntimeError("Perturbation scheduler unavailable on default world adapter")
       return self._perturbations
   ```

4. **ScriptedPolicyAdapter.backend** (src/townlet/adapters/policy_scripted.py:72-76)
   ```python
   @property
   def backend(self) -> PolicyBackendProtocol:
       """Expose the wrapped legacy backend for transitional call sites."""
       return self._backend
   ```

### Active Usage Sites (14 total)

#### SimulationLoop (7 uses) - CRITICAL
**File**: src/townlet/core/sim_loop.py

1. **Line 111** - `_build_default_world_components()`
   ```python
   context = getattr(world_port, "context", None)
   ```

2. **Line 121** - `_build_default_world_components()`
   ```python
   lifecycle = getattr(world_port, "lifecycle_manager", None)
   ```

3. **Line 124** - `_build_default_world_components()`
   ```python
   perturbations = getattr(world_port, "perturbation_scheduler", None)
   ```

4. **Line 147** - `_build_default_policy_components()`
   ```python
   backend_attr = getattr(policy_port, "backend", None)
   ```

5. **Line 243** - `_build_components()`
   ```python
   context = getattr(self._world_port, "context", None)
   ```

6. **Line 212** - `_require_world_context()`
   ```python
   context = getattr(self._world_port, "context", None)
   ```

7. **Line 1081** - `_try_context_observe()`
   ```python
   context = self._world_context or getattr(self._world_port, "context", None)
   ```

#### Test Files (7 uses across 3 files)

1. **tests/factories/test_world_factory.py** (2 uses)
   - Line: `assert adapter.lifecycle_manager.config is base_config`
   - Line: `assert adapter.perturbation_scheduler.config is base_config`

2. **tests/world/test_world_factory_integration.py** (1 use)
   - Line: `assert world_runtime.lifecycle_manager.config is config`

3. **tests/helpers/modular_world.py** (4 uses)
   - Line 56: `lifecycle = adapter.lifecycle_manager`
   - Line 57: `perturbations = adapter.perturbation_scheduler`
   - Line 61: `context=adapter.context`
   - Line 97: `context = getattr(adapter, "context", None)`
   - Line 109: `lifecycle = adapter.lifecycle_manager`
   - Line 110: `perturbations = adapter.perturbation_scheduler`

**Total**: 14 references (7 in src/, 7 in tests/)

---

## Target State

### New Factory Signatures

#### World Factory
**Current**: Returns `WorldRuntime` (adapter)
**Target**: Returns `WorldRuntime` with accessible components

**Options**:
- **Option A**: Extend `WorldRuntime` protocol with component accessors
- **Option B**: Return tuple `(WorldRuntime, WorldComponents)`
- **Option C**: Make `WorldComponents` dataclass available from adapter

**Selected**: Option C - Add `components()` method to adapters

#### Policy Factory
**Current**: Returns `PolicyBackend` (adapter)
**Target**: Policy backend directly available without `.backend` property

**Solution**: Already have `PolicyComponents` dataclass, SimulationLoop should use it directly

### Adapter Changes

1. **DefaultWorldAdapter** - Remove 3 properties, add `components()` method
2. **ScriptedPolicyAdapter** - Remove `.backend` property (keep `_backend` private)

### SimulationLoop Changes

Update `_build_default_world_components()` and `_build_default_policy_components()` to not rely on adapter properties.

---

## Implementation Sequence

### Phase 1: Add Component Accessor Methods (Non-Breaking)

**Objective**: Add new methods alongside existing properties

#### Step 1.1: Add `components()` to DefaultWorldAdapter
```python
def components(self) -> dict[str, Any]:
    """Return adapter components for loop initialization."""
    return {
        "context": self._context,
        "lifecycle": self._lifecycle,
        "perturbations": self._perturbations,
    }
```

**Files Modified**:
- `src/townlet/adapters/world_default.py`

**Validation**: None required (additive change)

#### Step 1.2: Update WorldRuntime Protocol (Optional)
Add optional `components()` method signature to protocol if needed for type safety.

**Files Modified**:
- `src/townlet/ports/world.py` (if protocol update needed)

**Validation**: `mypy src/townlet/adapters/world_default.py`

---

### Phase 2: Migrate SimulationLoop to Use New Pattern

**Objective**: Update SimulationLoop to use component accessors instead of properties

#### Step 2.1: Update `_build_default_world_components()`

**File**: `src/townlet/core/sim_loop.py`

**Changes**:
```python
# Before (lines 111-126):
context = getattr(world_port, "context", None)
if context is None:
    raise RuntimeError("World provider did not supply a context-backed adapter")
# ... more getattr calls ...

# After:
components = getattr(world_port, "components", None)
if callable(components):
    comp_dict = components()
    context = comp_dict.get("context")
    lifecycle = comp_dict.get("lifecycle")
    perturbations = comp_dict.get("perturbations")
else:
    # Fallback to legacy property access (for compatibility)
    context = getattr(world_port, "context", None)
    lifecycle = getattr(world_port, "lifecycle_manager", None)
    perturbations = getattr(world_port, "perturbation_scheduler", None)

if context is None:
    raise RuntimeError("World provider did not supply a context-backed adapter")
if lifecycle is None:
    raise RuntimeError("World provider did not expose lifecycle manager")
if perturbations is None:
    raise RuntimeError("World provider did not expose perturbation scheduler")
```

**Validation**:
```bash
pytest tests/core/test_sim_loop_with_dummies.py tests/core/test_sim_loop_modular_smoke.py -v
```

#### Step 2.2: Update Other SimulationLoop Context Access

**Locations**:
- Line 243 (`_build_components`) - Already has `self._world_context` cached
- Line 212 (`_require_world_context`) - Uses cached `self._world_context` first
- Line 1081 (`_try_context_observe`) - Uses cached `self._world_context` first

**Strategy**: These already use cached `self._world_context` as primary; the `getattr()` calls are fallbacks. After Step 2.1, the cache will be populated correctly.

**No changes needed** (fallback paths already handle None gracefully)

#### Step 2.3: Update Policy Backend Access

**File**: `src/townlet/core/sim_loop.py` (line 147)

**Change**:
```python
# Before:
backend_attr = getattr(policy_port, "backend", None)
if backend_attr is not None:
    decision_backend = backend_attr
    controller = PolicyController(backend=decision_backend, port=policy_port)
else:
    decision_backend = policy_port

# After:
# ScriptedPolicyAdapter wraps PolicyRuntime; we already have direct access
# via the backend parameter passed to create_policy, just use that
decision_backend = policy_backend  # Already have this from line 140
controller = PolicyController(backend=decision_backend, port=policy_port)
```

**Wait** - need to review actual structure here. Let me check the actual code pattern.

**Validation**:
```bash
pytest tests/core/test_sim_loop_with_dummies.py -v
```

---

### Phase 3: Update Test Fixtures

**Objective**: Update test helpers and assertions to use new patterns

#### Step 3.1: Update tests/helpers/modular_world.py

**Changes** (6 locations):
```python
# Lines 56-57: from_config method
adapter = create_world(world=state, config=config)
comp_dict = adapter.components()
lifecycle = comp_dict["lifecycle"]
perturbations = comp_dict["perturbations"]
context = comp_dict["context"]

# Lines 97-110: world_components method
adapter = create_world(world=self.state, config=self.config)
comp_dict = adapter.components()
context = comp_dict.get("context")
if context is None:
    raise RuntimeError("World adapter missing context")
# ... rest of method
```

**Validation**:
```bash
pytest tests/helpers/ -v
```

#### Step 3.2: Update tests/factories/test_world_factory.py

**Changes** (2 locations):
```python
# Before:
assert adapter.lifecycle_manager.config is base_config
assert adapter.perturbation_scheduler.config is base_config

# After:
comp = adapter.components()
assert comp["lifecycle"].config is base_config
assert comp["perturbations"].config is base_config
```

**Validation**:
```bash
pytest tests/factories/test_world_factory.py -v
```

#### Step 3.3: Update tests/world/test_world_factory_integration.py

**Changes** (1 location):
```python
# Before:
assert world_runtime.lifecycle_manager.config is config

# After:
comp = world_runtime.components()
assert comp["lifecycle"].config is config
```

**Validation**:
```bash
pytest tests/world/test_world_factory_integration.py -v
```

---

### Phase 4: Remove Escape Hatch Properties

**Objective**: Remove the deprecated properties now that all usage sites are migrated

#### Step 4.1: Remove Properties from DefaultWorldAdapter

**File**: `src/townlet/adapters/world_default.py`

**Remove**:
- Lines 160-164: `lifecycle_manager` property
- Lines 166-170: `perturbation_scheduler` property
- Lines 175-179: `context` property

**Validation**:
```bash
rg "\.lifecycle_manager|\.perturbation_scheduler|adapter\.context" src/ --type py
# Should return 0 matches
```

#### Step 4.2: Remove Property from ScriptedPolicyAdapter

**File**: `src/townlet/adapters/policy_scripted.py`

**Remove**:
- Lines 72-76: `backend` property

**Keep**:
- `self._backend` private attribute (used internally)

**Validation**:
```bash
rg "policy.*\.backend|adapter\.backend" src/ --type py
# Should return 0 matches (except in comments/docs)
```

---

### Phase 5: Final Validation

#### Step 5.1: Run Full Test Suite

```bash
# Adapter tests
pytest tests/adapters/ -v

# Core simulation loop tests
pytest tests/core/test_sim_loop_with_dummies.py tests/core/test_sim_loop_modular_smoke.py -v

# Factory tests
pytest tests/factories/test_world_factory.py tests/world/test_world_factory_integration.py -v

# World context tests
pytest tests/test_world_context.py tests/world/test_world_context_observe.py -v
```

#### Step 5.2: Verify No Escape Hatch References

```bash
rg "\.context[^a-zA-Z]" src/townlet/adapters/ --type py
rg "\.lifecycle_manager" src/ --type py
rg "\.perturbation_scheduler" src/ --type py
rg "policy.*\.backend" src/ --type py
```

**Expected**: 0 matches in src/ (except internal adapter implementation)

#### Step 5.3: Type Check

```bash
mypy src/townlet/adapters/ src/townlet/core/sim_loop.py
```

---

## Validation Checkpoints

### Gate 1: After Phase 1 (Additive Changes)
- [ ] New `components()` method added
- [ ] No test failures
- [ ] Type checking passes

### Gate 2: After Phase 2 (SimulationLoop Migration)
- [ ] Core loop tests passing (test_sim_loop_with_dummies.py, test_sim_loop_modular_smoke.py)
- [ ] No regressions in loop behavior
- [ ] Context caching working correctly

### Gate 3: After Phase 3 (Test Migration)
- [ ] All 3 test files updated
- [ ] Test helpers working with new pattern
- [ ] Factory tests passing

### Gate 4: After Phase 4 (Property Removal)
- [ ] Properties removed from adapters
- [ ] 0 escape hatch references in src/
- [ ] All adapter tests passing

### Gate 5: Final (Complete Validation)
- [ ] Full test suite passing
- [ ] Type checking clean
- [ ] No references to escape hatch properties in src/

---

## Risk Assessment

### High Risk Areas

1. **SimulationLoop._build_components()** - Core initialization path
   - **Risk**: Breaking loop construction
   - **Mitigation**: Incremental changes with fallback paths, test after each step

2. **Context caching in SimulationLoop** - Multiple access points
   - **Risk**: None/stale context causing observation failures
   - **Mitigation**: Existing fallback logic already handles this

3. **Test helper assumptions** - ModularTestWorld widely used
   - **Risk**: Cascading test failures
   - **Mitigation**: Update helper first, validate before removing properties

### Medium Risk Areas

1. **Policy backend extraction** - Less clear pattern
   - **Risk**: Controller construction might fail
   - **Mitigation**: Review actual code flow before refactoring

2. **Type safety** - Optional getattr patterns
   - **Risk**: mypy might complain about changed access patterns
   - **Mitigation**: Run mypy after each phase

### Low Risk Areas

1. **Property removal** - Final cleanup step
   - **Risk**: Minimal (all callsites already migrated)
   - **Mitigation**: Grep verification before removal

---

## Rollback Strategy

### Phase-by-Phase Rollback

**If Gate 1 Fails**: Revert Phase 1 commits (additive changes)
**If Gate 2 Fails**: Revert Phase 2 commits (SimulationLoop changes)
**If Gate 3 Fails**: Revert Phase 3 commits (test changes)
**If Gate 4 Fails**: Revert Phase 4 commits (property removal)

### Emergency Rollback

```bash
# Full rollback to pre-WS2 state
git log --oneline | head -10  # Find last WS1.4 commit
git reset --hard <ws1.4-commit-hash>
```

**Last safe commit**: ffce7d0 (WP3.1 WS1.4)

---

## Commits Plan

### Commit 1: Add Component Accessors (Phase 1)
```
WP3.1 WS2.1: Add component accessor methods to adapters

Add `components()` method to DefaultWorldAdapter to expose
context, lifecycle, and perturbations without property access.
This is a non-breaking additive change to prepare for escape
hatch property removal.

Changes:
- Add DefaultWorldAdapter.components() returning dict with
  context, lifecycle, perturbations
- No breaking changes; existing properties remain functional

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit 2: Migrate SimulationLoop (Phase 2)
```
WP3.1 WS2.2: Migrate SimulationLoop to use component accessors

Update SimulationLoop to use adapter.components() method instead
of direct property access. Maintains fallback to legacy property
access for compatibility during transition.

Changes:
- Update _build_default_world_components() to use components()
- Update policy backend access pattern
- Maintain backward compatibility via fallback paths

Test Results:
- Core loop tests passing ✓
- No behavioral regressions ✓

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit 3: Update Test Fixtures (Phase 3)
```
WP3.1 WS2.3: Update test fixtures for component accessor pattern

Migrate test helpers and factory tests to use new component
accessor pattern instead of adapter escape hatch properties.

Changes:
- Update tests/helpers/modular_world.py (6 locations)
- Update tests/factories/test_world_factory.py (2 locations)
- Update tests/world/test_world_factory_integration.py (1 location)

Test Results:
- Factory tests: passing ✓
- World integration tests: passing ✓
- Helper tests: passing ✓

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit 4: Remove Escape Hatch Properties (Phase 4)
```
WP3.1 WS2.4: Remove adapter escape hatch properties

Complete adapter surface cleanup by removing transitional
properties. All access now goes through component accessors
or direct constructor injection.

Changes:
- Remove DefaultWorldAdapter.context property
- Remove DefaultWorldAdapter.lifecycle_manager property
- Remove DefaultWorldAdapter.perturbation_scheduler property
- Remove ScriptedPolicyAdapter.backend property

Verification:
- 0 escape hatch references in src/ ✓
- Full test suite passing ✓
- Gate condition met ✓

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Notes

### Policy Backend Pattern

Need to clarify: In `_build_default_policy_components()`, we create `PolicyRuntime` then pass it to `create_policy()` which wraps it in `ScriptedPolicyAdapter`. The adapter's `.backend` property exposes the wrapped runtime.

**Current flow**:
```python
policy_backend = PolicyRuntime(config=self.config)  # Line 140
policy_port = create_policy(provider="scripted", backend=policy_backend, ...)  # Line 141
backend_attr = getattr(policy_port, "backend", None)  # Line 147 - extracts the wrapped runtime
controller = PolicyController(backend=backend_attr, port=policy_port)  # Line 150
```

**Target flow**:
```python
policy_backend = PolicyRuntime(config=self.config)
policy_port = create_policy(provider="scripted", backend=policy_backend, ...)
# PolicyController can use policy_backend directly since we already have it
controller = PolicyController(backend=policy_backend, port=policy_port)
```

This works because we already have `policy_backend` in scope before wrapping.

### WorldState.context Pattern

`WorldState` has a `.context` attribute (not a property) that holds `WorldContext`. This is **not** an escape hatch - it's the legitimate data model relationship. Only the **adapter** property `DefaultWorldAdapter.context` is an escape hatch.

**Keep**: `WorldState.context` (legitimate model attribute)
**Remove**: `DefaultWorldAdapter.context` (adapter escape hatch)

---

## Time Estimates

- **Phase 1**: 5 min (simple addition)
- **Phase 2**: 10 min (careful SimulationLoop changes)
- **Phase 3**: 10 min (test fixture updates)
- **Phase 4**: 5 min (property removal)
- **Phase 5**: 10 min (full validation)

**Total**: 40 min (plus contingency for issues)

---

## Success Criteria

- [ ] 0 references to `.lifecycle_manager`, `.perturbation_scheduler`, `.context`, or `.backend` properties in src/
- [ ] All adapter tests passing
- [ ] Core simulation loop tests passing
- [ ] Type checking clean
- [ ] No behavioral regressions
- [ ] 4 commits documenting incremental migration
