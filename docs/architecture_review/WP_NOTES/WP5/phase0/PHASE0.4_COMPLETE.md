# WP5 Phase 0.4: Import Dependency Analysis - COMPLETE

**Date Completed**: 2025-10-14
**Duration**: ~0.25 days (~2 hours)
**Status**: ✅ COMPLETE

---

## Objective

Map import dependencies of the `stability` package to identify circular dependencies, boundary violations, and coupling patterns before beginning refactoring work in Phase 3.1.

---

## Deliverables

### 1. Import Dependency Map ✅

**File**: `docs/architecture_review/WP_NOTES/WP5/phase0/IMPORT_DEPENDENCY_ANALYSIS.md`

**Key Findings**:
- ✅ **No circular dependencies** within stability package
- ✅ **7 external importers** identified (6 unique modules)
- ⚠️ **HIGH coupling** with SimulationLoop (11-parameter input surface)
- ⚠️ **MEDIUM coupling** with config system (3 config files)

### 2. Data Flow Analysis ✅

**StabilityMonitor.track() Input Surface**:
```
11 parameters sourced from 6 different subsystems:
  ├─ rewards            ← RewardEngine
  ├─ terminated         ← LifecycleManager
  ├─ queue_metrics      ← PolicyController
  ├─ embedding_metrics  ← ObservationService
  ├─ job_snapshot       ← EmploymentService
  ├─ events             ← WorldRuntime
  ├─ employment_metrics ← EmploymentService
  ├─ hunger_levels      ← World state (direct)
  ├─ option_switch_counts ← PolicyController
  └─ rivalry_events     ← RivalryService
```

**Impact**: High coupling creates fragility—any change to these subsystems may require updating StabilityMonitor

### 3. Safe Extraction Order ✅

Defined 4-stage extraction strategy for Phase 3.1:

**Stage 1** (Parallel extraction):
1. Starvation Analyzer (independent)
2. Reward Variance Analyzer (independent)
3. Option Thrash Analyzer (independent)

**Stage 2**:
4. Alert Aggregator (depends on Stage 1 outputs)

**Stage 3**:
5. Promotion Window Evaluator (depends on Stage 2)

**Stage 4**:
6. Refactor StabilityMonitor to orchestrate all 5 analyzers

### 4. Config Coupling Analysis ✅

**StabilityMonitor Config Dependencies**:
- `config.stability.*` (8 fields from StabilityConfig)
- `config.employment.enforce_job_loop` (1 field)
- `config.conflict.rivalry.avoid_threshold` (1 field)

**Total**: 10 config fields from 3 different config modules

**Recommendation**: Use **config slice pattern**—each analyzer receives only its required config section

---

## Key Findings

### 1. No Circular Dependencies ✅

```
stability/
  ├─ monitor.py    → config, utils.coerce
  ├─ promotion.py  → config, utils.coerce
  └─ __init__.py   → monitor, promotion

External importers (one-way):
  SimulationLoop        → stability.{monitor, promotion}
  SnapshotManager       → stability.{monitor, promotion}
  ConsoleHandlers       → stability.promotion
  TrainingOrchestrator  → stability.promotion
```

**Verdict**: Clean dependency tree, safe to refactor ✅

### 2. High Coupling with SimulationLoop ⚠️

**Issue**: `StabilityMonitor.track()` requires 11 parameters from 6 subsystems

**Risk**: Changes to rewards, lifecycle, employment, policy, or observations require stability updates

**Mitigation Options**:
1. **Introduce StabilityInputDTO** (encapsulate 11 params into single object)
2. **Accept high coupling** (stability is inherently cross-cutting concern)

**Decision**: DEFER to Phase 3.1 (extraction first, DTO later if needed)

### 3. Config Fragmentation Across 3 Files

**Issue**: StabilityMonitor needs config from:
- `config/rewards.py` (StabilityConfig + 4 canary configs)
- `config/core.py` (employment.enforce_job_loop)
- `config/conflict.py` (rivalry.avoid_threshold)

**Risk**: Hidden coupling—changes to employment or rivalry config can break stability

**Mitigation**: Pass config slices to analyzer constructors (not full SimulationConfig)

**Example**:
```python
# ✅ Good (config slice)
class StarvationAnalyzer:
    def __init__(self, config: StarvationCanaryConfig):
        self._config = config

# ❌ Bad (full config)
class StarvationAnalyzer:
    def __init__(self, config: SimulationConfig):
        self._config = config.stability.starvation  # Hidden coupling!
```

### 4. State Management Complexity

**Discovered**: 14 distinct state fields across 5 analyzers must be preserved in snapshots
- Starvation: 3 collections (streaks dict, active set, incidents deque)
- Reward Variance: 1 deque
- Option Thrash: 1 deque
- Promotion Window: 7 scalar fields
- Alert Aggregator: 2 fields (latest alert + list)

**Impact**: Extraction must maintain exact export/import format for backward compatibility

---

## Boundary Violations

### Violation 1: 11-Parameter Input Surface (HIGH Severity)

**Location**: `sim_loop.py:790-802` → `stability.track(...)`

**Problem**: StabilityMonitor is tightly coupled to 6 subsystems via method parameters

**Evidence**:
```python
self.stability.track(
    tick=self.tick,
    rewards=rewards,                        # From rewards/engine.py
    terminated=terminated,                  # From lifecycle/manager.py
    queue_metrics=queue_metrics,            # From policy/runner.py
    embedding_metrics=embedding_metrics,    # From observations/embedding.py
    job_snapshot=job_snapshot,              # From world/employment.py
    events=events,                          # From world/runtime.py
    employment_metrics=employment_metrics,  # From world/employment.py
    hunger_levels=hunger_levels,            # Direct from world state
    option_switch_counts=option_switch_counts,  # From policy/runner.py
    rivalry_events=rivalry_events,          # From world/relationships.py
)
```

**Recommendation**: Consider `StabilityInputDTO` in future refactor (not blocking for Phase 3.1)

### Violation 2: Config Coupling Across Multiple Files (MEDIUM Severity)

**Problem**: Stability reads from 3 different config modules

**Evidence**:
- StabilityMonitor reads `config.employment.enforce_job_loop` (from config/core.py)
- StabilityMonitor reads `config.conflict.rivalry.avoid_threshold` (from config/conflict.py)
- Both fields outside of `config.stability.*` namespace

**Recommendation**: Adopt config slice pattern to make coupling explicit

---

## Risk Assessment

| Risk | Severity | Likelihood | Impact | Mitigation |
|------|----------|------------|--------|------------|
| Circular dependency during extraction | HIGH | LOW | Deadlock in imports | Extract in stages (independent → dependent) |
| Breaking snapshot compatibility | HIGH | MEDIUM | Users lose saved games | Maintain exact export/import format + tests |
| Config coupling fragmentation | MEDIUM | MEDIUM | Hidden dependencies | Config slice pattern |
| Test regression during extraction | MEDIUM | LOW | Behavior changes | 18 characterization tests must pass unchanged |
| Performance degradation | LOW | LOW | Slower tick processing | Orchestration overhead ~5 method calls (negligible) |
| Import cycle with new analyzers | LOW | LOW | Module import failure | Follow safe extraction order |

**Overall Risk**: LOW-MEDIUM (well-mitigated by characterization tests and staged extraction)

---

## Extraction Readiness

### Pre-Conditions ✅

- ✅ No circular dependencies in current codebase
- ✅ All external importers identified
- ✅ Config dependencies mapped
- ✅ Data flow documented
- ✅ 18 characterization tests in place

### Safe Extraction Order Defined ✅

**Stage 1** (Independent analyzers—can extract in parallel):
1. `analyzers/starvation.py` (80 lines)
   - Input: tick, hunger_levels, terminated
   - Config: StarvationCanaryConfig
   - Output: starvation_incidents, alert

2. `analyzers/reward_variance.py` (60 lines)
   - Input: tick, rewards
   - Config: RewardVarianceCanaryConfig
   - Output: variance, mean, alert

3. `analyzers/option_thrash.py` (60 lines)
   - Input: tick, option_switch_counts, active_agent_count
   - Config: OptionThrashCanaryConfig
   - Output: switch_rate, alert

**Stage 2** (Depends on Stage 1):
4. `analyzers/alert_aggregator.py` (120 lines)
   - Input: All analyzer alerts + direct sources
   - Config: StabilityConfig (thresholds)
   - Output: alerts list

**Stage 3** (Depends on Stage 2):
5. `analyzers/promotion_window.py` (50 lines)
   - Input: tick, alerts
   - Config: PromotionGateConfig
   - Output: pass_streak, candidate_ready, last_result

**Stage 4** (Orchestration):
6. Refactor `monitor.py` (~100 lines)
   - Role: Orchestrate 5 analyzers
   - Maintain backward-compatible API
   - Delegate to analyzers

**Validation**:
- ✅ Run 18 characterization tests (must pass unchanged)
- ✅ Run full test suite
- ✅ Verify snapshot export/import round-trip

---

## Recommendations for Phase 3.1

### Required (Blocking)

1. **Use config slice pattern**: Pass only required config section to each analyzer
   ```python
   StarvationAnalyzer(config.stability.starvation)  # ✅
   StarvationAnalyzer(config)                        # ❌
   ```

2. **Maintain exact state format**: Export/import must match current format for backward compatibility

3. **Follow extraction order**: Independent analyzers first, then dependent ones

4. **Validate with characterization tests**: All 18 tests must pass unchanged

### Optional (Nice-to-Have)

1. **Introduce StabilityInputDTO**: Encapsulate 11-parameter surface (can defer to later refactor)

2. **Consolidate config**: Move `employment.enforce_job_loop` and `rivalry.avoid_threshold` into `StabilityConfig` (breaking change, defer)

3. **Add analyzer protocols**: Define `CanaryAnalyzer` and `WindowEvaluator` protocols for type safety (defer)

---

## Files Created

1. `docs/architecture_review/WP_NOTES/WP5/phase0/IMPORT_DEPENDENCY_ANALYSIS.md` - Full analysis
2. `docs/architecture_review/WP_NOTES/WP5/phase0/PHASE0.4_COMPLETE.md` - This completion report

---

## Acceptance Criteria

- ✅ Map all imports within stability package (no circular deps found)
- ✅ Identify all external importers (7 modules, 6 unique)
- ✅ Document config coupling (10 fields from 3 config modules)
- ✅ Define safe extraction order (4-stage plan)
- ✅ Assess boundary violations (2 violations: HIGH + MEDIUM severity)
- ✅ Create risk matrix (5 risks identified, all mitigated)

**Status**: ALL CRITERIA MET ✅

---

## Phase 3.1 Readiness

**Overall Status**: READY ✅

Phase 0.4 has successfully mapped the import landscape and identified safe extraction paths. Key findings:

1. **No circular dependencies** in current code (clean foundation)
2. **Safe extraction order defined** (independent → dependent)
3. **Config coupling documented** (use config slice pattern)
4. **Boundary violations identified** (high coupling acceptable for cross-cutting concern)
5. **18 characterization tests ready** (golden baseline for validation)

**Confidence Level**: HIGH (clean dependency tree + comprehensive test coverage)

**Blocker Status**: NONE (ready to proceed with Phase 3.1 extraction)

---

## Next Phase: 0.5 Security Baseline Scan

With import dependencies mapped and extraction order defined, proceed to Phase 0.5 to establish security baseline before beginning refactoring work.

---

## Lessons Learned

1. **Stability is inherently cross-cutting**: The 11-parameter input surface reflects that stability monitoring requires data from many subsystems—this is not a design flaw, but the nature of the domain.

2. **Config coupling is real but manageable**: Using config slice pattern makes dependencies explicit and testable.

3. **No circular deps is gold**: Clean import tree makes extraction straightforward—no need for complex dependency injection or refactoring existing code.

4. **Characterization tests are insurance**: 18 tests covering all edge cases provide confidence that extraction won't break behavior.

---

## Time Breakdown

- Import mapping and analysis: 0.5 hours
- Data flow tracing: 0.5 hours
- Risk assessment and recommendations: 0.5 hours
- Documentation: 0.5 hours

**Total**: ~2 hours (within 0.25 day estimate)

---

## Sign-off

Phase 0.4 (Import Dependency Analysis) is **COMPLETE** and ready for Phase 3.1 extraction work.

All acceptance criteria met:
- ✅ Import structure mapped (no circular deps)
- ✅ External dependencies identified (7 importers)
- ✅ Config coupling documented (10 fields, 3 modules)
- ✅ Safe extraction order defined (4 stages)
- ✅ Boundary violations assessed (2 violations, mitigated)
- ✅ Risk matrix created (5 risks, all low-medium after mitigation)
