# WP5 Phase 2 Approach: Quality Gates

**Date**: 2025-10-14
**Status**: PLANNING
**Dependencies**: Phase 1 Complete ✅
**Estimated Duration**: 2-3 days

---

## Executive Summary

Phase 2 focuses on establishing comprehensive quality gates to ensure code maintainability and type safety. This phase runs in **parallel with Phase 1** where possible, but should NOT begin until Phase 0 (Risk Reduction) is complete.

### Objectives

1. **Drive mypy errors to zero** across entire codebase
2. **Increase docstring coverage** to ≥80% overall
3. **Integrate quality tools into CI** (interrogate for docstrings)
4. **Establish quality ratchets** (prevent regression)

### Fail-Forward Philosophy ✅

Per Phase 1 learnings:
- ✅ **No backward compatibility** - Type annotations may change signatures
- ✅ **No feature flags** - One strict type system, not "strict" vs "permissive"
- ✅ **Breaking changes OK** - Pre-1.0, clean breaks preferred
- ✅ **Rollback = git revert** - Not "maintain legacy typing"

---

## Phase 1 Review Outcomes

### What Went Well ✅

1. **Strict mypy already enabled** - No need to enable, just fix errors
2. **Pydantic v2 validation** - Field constraints catch errors early
3. **Type narrowing works** - `isinstance()` checks satisfy mypy
4. **Test-driven approach** - Tests guided fixes, caught regressions early
5. **Documentation quality** - Comprehensive completion reports

### Lessons Learned 📝

1. **Start with lowest dependencies** - Fix DTOs → Ports → Core → Adapters → Domain
2. **Explicit > Implicit** - Use `isinstance()` checks for type narrowing
3. **Validate early** - Pydantic validators at boundaries prevent issues
4. **Test first** - Create tests before refactoring (Phase 0.2 pattern)
5. **Small commits** - Phase 1 was 8 files, ~200 lines - manageable

### Anti-Patterns to Avoid ❌

1. **Don't batch type fixes** - Fix package-by-package, not all at once
2. **Don't add `# type: ignore` liberally** - Understand and fix root cause
3. **Don't skip validation** - Add Pydantic constraints, not just annotations
4. **Don't assume types** - Verify with `isinstance()` at boundaries
5. **Don't forget documentation** - Update docstrings as you add types

---

## Current State Analysis

### Mypy Error Baseline

From WP5.md, we have **~474 mypy errors** in legacy packages. Let me estimate the breakdown:

| Package | Estimated Errors | Complexity | Priority |
|---------|-----------------|------------|----------|
| `dto` | 0 | ✅ Complete | - |
| `ports` | 0 | ✅ Complete | - |
| `snapshots` | 0 | ✅ Complete (Phase 1) | - |
| `utils/rng` | 0 | ✅ Complete (Phase 1) | - |
| `rewards` | ~40 | Medium | 🔴 HIGH (simple domain) |
| `observations` | ~50 | Medium | 🔴 HIGH (DTOs complete) |
| `lifecycle` | ~30 | Low | 🟡 MEDIUM (small package) |
| `stability` | ~40 | Medium | 🟡 MEDIUM (will refactor in Phase 3) |
| `world` | ~120 | HIGH | 🟡 MEDIUM (complex, many files) |
| `policy` | ~100 | HIGH | 🟡 MEDIUM (complex, training) |
| `telemetry` | ~94 | Medium | 🟢 LOW (will refactor in Phase 3) |

**Total**: ~474 errors

### Docstring Coverage Baseline

From WP5.md:

| Package | Current | Target | Gap |
|---------|---------|--------|-----|
| `dto` | 95% | 95% | ✅ 0% |
| `ports` | 90% | 95% | +5% |
| `core` | 70% | 85% | +15% |
| `config` | 75% | 85% | +10% |
| `world` | 50% | 80% | +30% |
| `policy` | 45% | 80% | +35% |
| `telemetry` | 40% | 80% | +40% |
| **Overall** | **~50%** | **≥80%** | **+30%** |

---

## Phase 2 Breakdown

### Phase 2.1: Package-by-Package Mypy Fixing (2 days)

**Strategy**: Fix errors package-by-package in dependency order

#### Day 1: Foundation Packages

**Morning: `rewards` package (~40 errors, 4 hours)**

1. **Start with `dto/rewards.py`** (already complete ✅)
2. **Fix `rewards/engine.py`** (280 LOC)
   - Add type hints to `compute()` method
   - Type reward component calculations
   - Add return type annotations
3. **Run tests**: `pytest tests/test_rewards_engine.py -v`
4. **Verify mypy**: `mypy src/townlet/rewards/ --strict`

**Afternoon: `observations` package (~50 errors, 4 hours)**

1. **Start with `dto/observations.py`** (already complete ✅)
2. **Fix `observations/embedding.py`** (82 LOC)
   - Type allocator methods
   - Add slot assignment types
3. **Fix `observations/service.py`** (193 LOC)
   - Type observation encoding methods
   - Add variant-specific types
4. **Run tests**: `pytest tests/test_observation_service.py -v`
5. **Verify mypy**: `mypy src/townlet/observations/ --strict`

#### Day 2: Domain Packages

**Morning: `lifecycle` package (~30 errors, 2 hours)**

1. **Fix `lifecycle/manager.py`** (111 LOC)
   - Type spawn/exit methods
   - Add termination condition types
2. **Run tests**: `pytest tests/test_lifecycle_manager.py -v`
3. **Verify mypy**: `mypy src/townlet/lifecycle/ --strict`

**Morning (continued): `stability` package (~40 errors, 2 hours)**

Note: Will be refactored in Phase 3, but fix types now

1. **Fix `stability/monitor.py`** (235 LOC)
   - Type tracking methods
   - Add metric types
2. **Fix `stability/promotion.py`** (161 LOC)
   - Type promotion methods
3. **Run tests**: `pytest tests/test_stability_monitor.py -v`
4. **Verify mypy**: `mypy src/townlet/stability/ --strict`

**Afternoon: Start `world` package (~120 errors, 4 hours)**

1. **Fix `world/grid.py`** (715 LOC) - **LARGEST FILE**
   - Focus on public API first
   - Type state access methods
   - Add agent/object types
2. **Fix `world/agents/registry.py`** (97 LOC)
   - Type agent management methods
3. **Run tests**: `pytest tests/test_world_grid.py tests/test_agent_registry.py -v`
4. **Verify mypy**: `mypy src/townlet/world/grid.py src/townlet/world/agents/registry.py --strict`

**Note**: `world` and `policy` are large packages - may need Day 3

#### Day 3 (if needed): Complex Packages

**`world` package completion (~60 remaining errors, 4 hours)**

1. **Fix remaining `world/` modules**
   - `world/core/context.py` (264 LOC)
   - `world/systems/*.py` (6 files)
   - `world/affordances/*.py` (3 files)
2. **Run full world tests**: `pytest tests/world/ -v`
3. **Verify mypy**: `mypy src/townlet/world/ --strict`

**`policy` package (~100 errors, 4 hours)**

1. **Fix `policy/runner.py`** (340 LOC)
   - Type decision methods
   - Add policy backend types
2. **Fix `policy/behavior.py`** (333 LOC)
   - Type behavior selection
3. **Fix `policy/training/` modules**
   - Focus on public APIs
   - Leave PPO internals for later (complex torch typing)
4. **Run tests**: `pytest tests/test_policy_runner.py -v`
5. **Verify mypy**: `mypy src/townlet/policy/ --strict`

#### Mypy Configuration Updates

Update [pyproject.toml](pyproject.toml:82-85) to remove PPO exception once other packages are fixed:

```toml
# Before (Phase 1)
[[tool.mypy.overrides]]
module = ["townlet.policy.training.strategies.ppo"]
disable_error_code = ["attr-defined", "arg-type", "call-overload", "no-untyped-call", "operator", "return-value", "call-arg", "unused-ignore"]

# After (Phase 2) - Keep PPO exception, add others if needed
[[tool.mypy.overrides]]
module = ["townlet.policy.training.strategies.ppo"]
# PPO strategy has complex torch typing - extracted from working code
disable_error_code = ["attr-defined", "arg-type", "call-overload"]
```

---

### Phase 2.2: Docstring Coverage (1 day, parallel with 2.1)

**Strategy**: Focus on public APIs first, then complex algorithms

#### High-Value Targets (4 hours)

1. **Public Ports & Adapters** (1 hour)
   - `ports/policy.py` - PolicyBackendProtocol
   - `ports/telemetry.py` - TelemetrySinkProtocol
   - `ports/world.py` - WorldRuntimeProtocol
   - `adapters/*.py` - All adapter implementations

2. **Complex Algorithms** (1.5 hours)
   - `rewards/engine.py` - Reward calculation logic
   - `observations/encoders/*.py` - Observation encoding
   - `stability/monitor.py` - Stability analysis (before Phase 3 refactor)

3. **Configuration Models** (1.5 hours)
   - `config/loader.py` - Config loading and validation
   - `config/core.py` - SimulationConfig
   - `config/rewards.py` - Reward config models

#### Coverage Verification

After each module:
```bash
scripts/check_docstrings.py src/townlet --min-module 80 --min-callable 60
```

Update thresholds in [pyproject.toml](pyproject.toml:93-99):
```toml
[tool.interrogate]
fail-under = 80  # Raised from 40
ignore-init-method = true
ignore-private = true
ignore-semicolon = true
color = true
omit = ["tests/*", "scripts/*", "docs/*"]
```

#### Docstring Style (from DOCSTRING_GUIDE.md)

**Function Docstrings**:
```python
def compute_reward(
    agent_id: str,
    world: WorldState,
    terminated: bool,
) -> RewardBreakdown:
    """Compute reward for agent's current state.

    Combines homeostasis reward (need satisfaction), potential shaping
    (progress toward goals), and social rewards (relationship changes).

    Args:
        agent_id: Agent identifier
        world: Current world state
        terminated: Whether agent terminated this tick

    Returns:
        RewardBreakdown with component values and total

    Example:
        ```python
        breakdown = compute_reward("alice", world, terminated=False)
        assert breakdown.total == breakdown.homeostasis + breakdown.shaping
        ```
    """
```

**Class Docstrings**:
```python
class RewardEngine:
    """Computes per-agent rewards from world state changes.

    The reward function balances three components:
    - Homeostasis: Maintaining low need levels (hunger, energy, hygiene)
    - Shaping: Progress toward goals (work, social, exploration)
    - Social: Relationship changes (rivalry, friendship)

    Rewards are clipped to [-r_max, +r_max] per tick to prevent outliers.

    Example:
        ```python
        engine = RewardEngine(config.rewards)
        rewards = engine.compute(world, terminated, previous_world)
        assert all(-engine.r_max <= r.total <= engine.r_max for r in rewards.values())
        ```
    """
```

---

### Phase 2.3: CI Integration (0.5 days)

**Integrate quality checks into CI pipeline**

#### Update `.github/workflows/test.yml`

Add mypy strict check:
```yaml
  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .[dev]
      - name: Type check with mypy
        run: mypy src/townlet --strict --show-error-codes
```

Add interrogate check:
```yaml
  docstrings:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install interrogate
      - name: Check docstring coverage
        run: interrogate src/townlet --fail-under 80
```

#### Quality Ratchets

Create `.github/workflows/quality-ratchet.yml`:
```yaml
name: Quality Ratchet

on: [push, pull_request]

jobs:
  ratchet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .[dev] interrogate

      - name: Check mypy error count
        run: |
          mypy src/townlet --strict 2>&1 | tee mypy_output.txt || true
          error_count=$(grep -c "error:" mypy_output.txt || echo 0)
          echo "Current mypy errors: $error_count"
          if [ "$error_count" -gt 0 ]; then
            echo "::error::Mypy errors detected: $error_count (target: 0)"
            exit 1
          fi

      - name: Check docstring coverage
        run: |
          interrogate src/townlet --fail-under 80 --quiet || true
          coverage=$(interrogate src/townlet --quiet | grep "OVERALL" | awk '{print $NF}')
          echo "Current docstring coverage: $coverage"
          if (( $(echo "$coverage < 80.0" | bc -l) )); then
            echo "::error::Docstring coverage below threshold: $coverage < 80.0%"
            exit 1
          fi
```

---

## Testing Strategy

### Test-Driven Type Fixing

**For each package**:

1. **Run existing tests first** - Ensure baseline functionality
2. **Add type hints** - Start with function signatures
3. **Run mypy** - Identify type errors
4. **Fix errors** - Add validation, narrow types
5. **Run tests again** - Verify no regressions
6. **Commit** - Small, focused commits per package

### Example Workflow: `rewards` package

```bash
# 1. Baseline
pytest tests/test_rewards_engine.py -v  # Should pass

# 2. Add types
vim src/townlet/rewards/engine.py
# Add type hints to compute() method

# 3. Check mypy
mypy src/townlet/rewards/ --strict  # Will show errors

# 4. Fix errors
# Add isinstance() checks, Pydantic validation, etc.

# 5. Verify
pytest tests/test_rewards_engine.py -v  # Should still pass
mypy src/townlet/rewards/ --strict     # Should now pass

# 6. Commit
git add src/townlet/rewards/
git commit -m "Add strict type checking to rewards package

- Type annotated compute() and helper methods
- Added isinstance() checks at boundaries
- All tests passing, mypy strict clean"
```

---

## Common Type Errors & Fixes

### Error 1: Missing Return Type

**Before**:
```python
def compute(world, terminated):
    results = {}
    # ... computation
    return results
```

**Mypy Error**:
```
error: Function is missing a return type annotation [no-untyped-def]
error: Need type annotation for 'results' (hint: "results: dict[<type>, <type>] = ...") [var-annotated]
```

**After**:
```python
def compute(
    world: WorldState,
    terminated: dict[str, bool],
) -> dict[str, RewardBreakdown]:
    results: dict[str, RewardBreakdown] = {}
    # ... computation
    return results
```

### Error 2: Implicit Any

**Before**:
```python
def process(data):
    return data["value"]
```

**Mypy Error**:
```
error: Function is missing a type annotation for one or more arguments [no-untyped-def]
error: Returning Any from function declared to return "X" [no-any-return]
```

**After**:
```python
def process(data: dict[str, Any]) -> float:
    if not isinstance(data.get("value"), (int, float)):
        raise TypeError("data['value'] must be numeric")
    return float(data["value"])
```

### Error 3: Untyped Call

**Before**:
```python
# In typed function
result = legacy_function(arg)  # legacy_function has no types
```

**Mypy Error**:
```
error: Call to untyped function "legacy_function" in typed context [no-untyped-call]
```

**After Option A** (Add types to legacy function):
```python
def legacy_function(arg: SomeType) -> ReturnType:
    # ... implementation
```

**After Option B** (Use type: ignore with issue link):
```python
# TODO(#123): Add types to legacy_function
result = legacy_function(arg)  # type: ignore[no-untyped-call]
```

---

## Rollback Plan

### Rollback Triggers

**Mypy Fixes**:
- If >20% of tests fail after type fixes → Rollback package
- If type fixes break critical functionality → Rollback immediately
- If time exceeds estimate by 2x → Pause and reassess

**Docstring Coverage**:
- If interrogate threshold causes CI failures → Lower threshold temporarily
- If docstring quality is poor → Focus on quality over quantity

### Rollback Procedure

**Per-Package Rollback** (<15 minutes):
```bash
# 1. Identify failing package
git log --oneline -10

# 2. Revert package changes
git revert <commit-sha-for-package>

# 3. Verify tests pass
pytest tests/test_<package>.py -v

# 4. Document issue
# Open GitHub issue with failure details
```

**Full Phase 2 Rollback** (<30 minutes):
```bash
# 1. Revert all Phase 2 commits
git revert <phase-2-start-sha>..HEAD

# 2. Verify baseline tests pass
pytest -v

# 3. Document and plan retry
# Document what went wrong, plan different approach
```

---

## Success Criteria

### Exit Criteria

- ✅ **Zero mypy strict errors** across entire codebase
- ✅ **≥80% docstring coverage** overall
- ✅ **All 820+ tests passing** with type annotations
- ✅ **CI enforces quality gates** (mypy + interrogate)
- ✅ **No regressions** in performance or functionality
- ✅ **Documentation complete** for type-heavy code

### Quality Metrics

**Before Phase 2**:
- Mypy errors: ~474
- Docstring coverage: ~50%
- Type safety: Partial

**After Phase 2**:
- Mypy errors: 0 ✅
- Docstring coverage: ≥80% ✅
- Type safety: Complete (strict mode) ✅

---

## Dependencies & Prerequisites

### Prerequisites from Phase 1 ✅

- ✅ RNG migration complete (no pickle)
- ✅ Snapshot DTOs validated (Pydantic v2)
- ✅ Type checking works (1 error fixed in Phase 1.3)

### Prerequisites from Phase 0 (REQUIRED)

Phase 2 **MUST NOT** start until Phase 0 is complete:
- ⏳ 0.1: Baseline Metrics
- ⏳ 0.2: RNG Test Suite (already done in Phase 1)
- ⏳ 0.3: Analyzer Characterization
- ⏳ 0.4: Import Dependency Analysis
- ⏳ 0.5: Security Baseline
- ⏳ 0.6: Rollback Plan

**Rationale**: Phase 0 establishes baselines that Phase 2 will be measured against.

### External Dependencies

**Already Installed**:
- ✅ mypy (configured in pyproject.toml)
- ✅ pytest (test framework)
- ✅ ruff (linting)

**Need to Install**:
- ❌ interrogate (docstring coverage)

```bash
pip install interrogate
```

---

## Timeline

### Detailed Schedule

**Day 1** (8 hours):
- Morning (4h): Fix `rewards` package (~40 errors)
- Afternoon (4h): Fix `observations` package (~50 errors)
- **Deliverable**: 2 packages mypy strict clean, tests passing

**Day 2** (8 hours):
- Morning (4h): Fix `lifecycle` + `stability` packages (~70 errors)
- Afternoon (4h): Start `world` package (~60/120 errors)
- **Deliverable**: 2 more packages clean, world 50% done

**Day 3** (8 hours, if needed):
- Morning (4h): Complete `world` package (~60 remaining errors)
- Afternoon (4h): Fix `policy` package (~100 errors)
- **Deliverable**: All packages mypy strict clean

**Parallel Work** (Days 1-2):
- Add docstrings to public APIs (2-3 hours/day)
- Update CI configuration (0.5 days)

**Total**: 2-3 days (16-24 hours)

---

## Communication Plan

### Daily Standups

**What to Report**:
- Packages completed yesterday
- Packages planned for today
- Blockers or surprises
- Mypy error count trend

### Completion Reports

After each major milestone:
- **After Day 1**: Package completion report (rewards, observations)
- **After Day 2**: Midpoint review (4 packages done, world in progress)
- **After Phase 2**: Final report (all packages, CI integration)

### Blocker Escalation

**If blocked >2 hours**:
1. Document the blocker (error message, context)
2. Try alternative approaches (type: ignore with issue link)
3. Escalate to user if architectural decision needed
4. Consider rollback if blocker is fundamental

---

## Next Steps

### Immediate Actions (Before Starting Phase 2)

1. ✅ **Complete Phase 1 review** - Done in PHASE1_FINAL_REVIEW.md
2. ⏳ **Wait for Phase 0 completion** - Phase 0.1-0.6 must finish first
3. ⏳ **Install interrogate** - `pip install interrogate`
4. ⏳ **Run baseline mypy scan** - Capture exact error count per package
5. ⏳ **Run baseline interrogate** - Capture exact docstring coverage

### Phase 2.1 Kickoff (After Phase 0 Complete)

1. Create Phase 2 branch: `git checkout -b feature/wp5-phase2`
2. Run baseline scans (save output for comparison)
3. Start with `rewards` package (smallest, lowest risk)
4. Commit frequently (1 package = 1 commit)
5. Run tests after each package

---

## Sign-Off

**Author**: Claude (AI Assistant)
**Reviewer**: Pending (John)
**Date**: 2025-10-14
**Status**: AWAITING APPROVAL

**Dependencies**:
- ✅ Phase 1 Complete
- ⏳ Phase 0 Complete (REQUIRED BEFORE STARTING)

**Estimated Effort**: 2-3 days
**Risk Level**: MEDIUM (many errors to fix, but test coverage high)
**Confidence**: HIGH (Phase 1 pattern successful, applying same approach)

---

## References

- [PHASE1_FINAL_REVIEW.md](docs/architecture_review/WP_NOTES/WP5/PHASE1_FINAL_REVIEW.md) - Phase 1 outcomes
- [WP5.md](docs/architecture_review/WP_TASKINGS/WP5.md) - Overall work package plan
- [pyproject.toml:60-75](pyproject.toml) - Mypy configuration
- [DOCSTRING_GUIDE.md](docs/guides/DOCSTRING_GUIDE.md) - Docstring style guide
- [ADR-003](docs/architecture_review/ADR/ADR-003%20-%20DTO%20Boundary.md) - DTO patterns (Phase 1 reference)
