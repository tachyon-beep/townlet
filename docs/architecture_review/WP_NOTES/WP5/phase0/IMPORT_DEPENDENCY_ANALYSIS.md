# WP5 Phase 0.4: Import Dependency Analysis

**Date**: 2025-10-14
**Status**: In Progress

---

## Objective

Map import dependencies of the `stability` package to identify circular dependencies, boundary violations, and coupling patterns before beginning refactoring work in Phase 3.1.

---

## Current Stability Package Structure

```
src/townlet/stability/
├── __init__.py          (8 lines)   - Package exports
├── monitor.py           (450 lines)  - StabilityMonitor (5 analyzers)
└── promotion.py         (270 lines)  - PromotionManager
```

**Total**: 728 lines

---

## Internal Dependency Graph

### Within Stability Package

```
stability/__init__.py
  ├─→ .monitor.StabilityMonitor
  └─→ .promotion.PromotionManager

stability/monitor.py
  ├─→ townlet.config.SimulationConfig
  ├─→ townlet.utils.coerce.{coerce_float, coerce_int}
  ├─→ collections.deque
  └─→ collections.abc.{Iterable, Mapping}

stability/promotion.py
  ├─→ townlet.config.SimulationConfig
  ├─→ townlet.utils.coerce.{coerce_int}
  ├─→ json
  ├─→ collections.deque
  ├─→ collections.abc.Mapping
  └─→ pathlib.Path
```

**Key Finding**: No circular dependencies within stability package itself ✅

---

## External Dependencies (Inbound)

### Who imports from stability?

```
Core Loop:
  src/townlet/core/sim_loop.py
    ├─→ stability.monitor.StabilityMonitor
    └─→ stability.promotion.PromotionManager

Snapshot System:
  src/townlet/snapshots/state.py
    ├─→ stability.monitor.StabilityMonitor
    └─→ stability.promotion.PromotionManager

Console Commands:
  src/townlet/console/handlers.py
    └─→ stability.promotion.PromotionManager

Training Orchestration:
  src/townlet/policy/training_orchestrator.py
    └─→ stability.promotion.PromotionManager

  src/townlet/policy/training/services/promotion.py
    └─→ stability.promotion.PromotionManager

Adapter (Legacy):
  src/townlet/adapters/world_default.py
    ├─→ stability.monitor.StabilityMonitor
    └─→ stability.promotion.PromotionManager

World Runtime:
  src/townlet/world/runtime.py
    ├─→ stability.monitor.StabilityMonitor
    └─→ stability.promotion.PromotionManager
```

**Total Importers**: 7 modules (6 unique after deduplication)

---

## Configuration Coupling

### StabilityMonitor Config Dependencies

`StabilityMonitor.__init__(config: SimulationConfig)` extracts:

```python
# From config.stability (StabilityConfig)
config.stability.affordance_fail_threshold      → int
config.stability.lateness_threshold             → int
config.stability.starvation                     → StarvationCanaryConfig
config.stability.reward_variance                → RewardVarianceCanaryConfig
config.stability.option_thrash                  → OptionThrashCanaryConfig
config.stability.promotion                      → PromotionGateConfig

# From config.employment
config.employment.enforce_job_loop              → bool

# From config.conflict.rivalry
config.conflict.rivalry.avoid_threshold         → float
```

**Config Files Coupled**:
- `src/townlet/config/rewards.py` (StabilityConfig, all 4 canary configs)
- `src/townlet/config/core.py` (employment.enforce_job_loop)
- `src/townlet/config/conflict.py` (rivalry.avoid_threshold)

### PromotionManager Config Dependencies

`PromotionManager.__init__(config: SimulationConfig)` extracts:

```python
# From config.stability.promotion
config.stability.promotion.window_ticks         → int
config.stability.promotion.required_passes      → int
config.stability.promotion.allowed_alerts       → tuple[str, ...]
```

**Config Files Coupled**:
- `src/townlet/config/rewards.py` (PromotionGateConfig)

---

## Data Flow Analysis

### StabilityMonitor.track() Input Surface

```python
def track(
    *,
    tick: int,                                    # Current tick number
    rewards: dict[str, float],                    # Agent rewards
    terminated: dict[str, bool],                  # Termination flags
    queue_metrics: dict[str, int] | None,         # Fairness queue stats
    embedding_metrics: dict[str, float] | None,   # Observation embedding stats
    job_snapshot: dict[str, dict[str, object]] | None,  # Employment state
    events: Iterable[dict[str, object]] | None,   # Affordance events
    employment_metrics: dict[str, object] | None, # Exit queue stats
    hunger_levels: dict[str, float] | None,       # Agent hunger values
    option_switch_counts: dict[str, int] | None,  # Option switching counts
    rivalry_events: Iterable[dict[str, object]] | None,  # Rivalry escalations
) -> None:
```

**Input Sources** (traced from `sim_loop.py:790`):
- `tick` ← loop.tick
- `rewards` ← RewardEngine.compute()
- `terminated` ← LifecycleManager.evaluate()
- `queue_metrics` ← PolicyController.queue_metrics()
- `embedding_metrics` ← ObservationService.embedding_metrics()
- `job_snapshot` ← EmploymentService.snapshot()
- `events` ← WorldRuntime.events buffer
- `employment_metrics` ← EmploymentService.exit_queue_metrics()
- `hunger_levels` ← {agent_id: agent.hunger for ...}
- `option_switch_counts` ← PolicyController.option_switch_counts()
- `rivalry_events` ← RivalryService.recent_events()

**Coupling Level**: HIGH (11 distinct data sources from 6 different subsystems)

### PromotionManager.update_from_metrics() Input Surface

```python
def update_from_metrics(
    self,
    metrics: dict[str, object],                   # From StabilityMonitor.latest_metrics()
    *,
    tick: int,                                    # Current tick number
) -> None:
```

**Input Sources**:
- `metrics["promotion"]` ← StabilityMonitor promotion window state
- `tick` ← loop.tick

**Coupling Level**: LOW (single dependency on StabilityMonitor)

---

## Circular Dependency Risk Assessment

### Current Architecture (No Circles) ✅

```
SimulationLoop
  ├──> StabilityMonitor.track()
  └──> PromotionManager.update_from_metrics()
         └──> (depends on StabilityMonitor.latest_metrics())

SnapshotManager
  ├──> StabilityMonitor.export_state()
  ├──> StabilityMonitor.import_state()
  ├──> PromotionManager.export_state()
  └──> PromotionManager.import_state()
```

**Direction**: One-way dependency flow (loop → stability, never stability → loop) ✅

### Phase 3.1 Extraction Risk ⚠️

When extracting 5 analyzers from `StabilityMonitor`, risk of introducing:

1. **Analyzer Cross-Dependencies**: Alert Aggregator (#5) depends on outputs from Starvation (#1), Reward Variance (#2), and Option Thrash (#3)
2. **Promotion Window Dependency**: Promotion Window Evaluator (#4) depends on Alert Aggregator (#5)
3. **Config Fragmentation**: Each analyzer needs different config slices

**Mitigation Strategy**:
- Extract independent analyzers first (#1, #2, #3)
- Extract Alert Aggregator (#5) second (aggregates #1-#3)
- Extract Promotion Window (#4) last (depends on #5)
- Pass config slices to analyzer constructors (don't hold whole SimulationConfig)

---

## Boundary Violations

### Tight Coupling with SimulationLoop

**Issue**: `StabilityMonitor.track()` has 11 parameters sourced from 6 subsystems
**Impact**: Any change to rewards, lifecycle, employment, policy, or observations requires updating StabilityMonitor signature
**Severity**: HIGH

**Example Violation** (sim_loop.py:790-802):
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

**Recommendation**: Introduce DTO to encapsulate stability inputs (similar to ObservationDTO)

### Config Coupling Across Multiple Files

**Issue**: StabilityMonitor depends on 3 config files (rewards, core, conflict)
**Impact**: Changes to employment or rivalry config can break stability monitoring
**Severity**: MEDIUM

**Recommendation**: Consolidate all stability config into single location (already exists as `StabilityConfig`, but needs enforcement)

---

## Safe Extraction Order for Phase 3.1

Based on dependency analysis, recommended extraction order:

### Stage 1: Independent Analyzers (Parallel Extraction)
1. **Starvation Analyzer** → `src/townlet/stability/analyzers/starvation.py`
   - Inputs: `tick`, `hunger_levels`, `terminated`
   - Config: `StarvationCanaryConfig`
   - Output: `starvation_incidents: int`, alert: `"starvation_spike"`

2. **Reward Variance Analyzer** → `src/townlet/stability/analyzers/reward_variance.py`
   - Inputs: `tick`, `rewards`
   - Config: `RewardVarianceCanaryConfig`
   - Output: `variance: float | None`, `mean: float | None`, alert: `"reward_variance_spike"`

3. **Option Thrash Analyzer** → `src/townlet/stability/analyzers/option_thrash.py`
   - Inputs: `tick`, `option_switch_counts`, `active_agent_count`
   - Config: `OptionThrashCanaryConfig`
   - Output: `switch_rate: float | None`, alert: `"option_thrash_detected"`

### Stage 2: Aggregator (Depends on Stage 1)
4. **Alert Aggregator** → `src/townlet/stability/analyzers/alert_aggregator.py`
   - Inputs: All analyzer alerts + direct sources (queue, employment, affordance, rivalry)
   - Config: `StabilityConfig` (thresholds only)
   - Output: `alerts: list[str]`

### Stage 3: Promotion Window (Depends on Stage 2)
5. **Promotion Window Evaluator** → `src/townlet/stability/analyzers/promotion_window.py`
   - Inputs: `tick`, `alerts` (from Aggregator)
   - Config: `PromotionGateConfig`
   - Output: `pass_streak`, `candidate_ready`, `last_result`

### Stage 4: Refactored Monitor (Orchestrates Stages 1-3)
6. **StabilityMonitor** → `src/townlet/stability/monitor.py` (refactored)
   - Role: Orchestrator that delegates to 5 analyzers
   - Maintains backward-compatible API
   - Handles state export/import

---

## Import Structure After Extraction (Target)

```
src/townlet/stability/
├── __init__.py
├── monitor.py                    (orchestrator, ~100 lines)
├── promotion.py                  (unchanged, 270 lines)
└── analyzers/
    ├── __init__.py
    ├── starvation.py             (~80 lines)
    ├── reward_variance.py        (~60 lines)
    ├── option_thrash.py          (~60 lines)
    ├── alert_aggregator.py       (~120 lines)
    └── promotion_window.py       (~50 lines)
```

**Total**: ~740 lines (similar to current, but better organized)

**LOC Breakdown**:
- Independent analyzers: 200 lines (3 files)
- Dependent analyzers: 170 lines (2 files)
- Orchestrator: 100 lines (monitor.py)
- Promotion manager: 270 lines (promotion.py, unchanged)
- Tests: 600+ lines (test_monitor_characterization.py)

---

## Boundary Interface Recommendations

### Recommendation 1: Stability Input DTO

Create `StabilityInputDTO` to encapsulate the 11-parameter surface:

```python
@dataclass
class StabilityInputDTO:
    """Encapsulates all inputs to stability monitoring."""
    tick: int
    rewards: dict[str, float]
    terminated: dict[str, bool]
    hunger_levels: dict[str, float]
    option_switch_counts: dict[str, int]
    queue_metrics: dict[str, int] | None = None
    embedding_metrics: dict[str, float] | None = None
    job_snapshot: dict[str, dict[str, object]] | None = None
    events: Iterable[dict[str, object]] | None = None
    employment_metrics: dict[str, object] | None = None
    rivalry_events: Iterable[dict[str, object]] | None = None
```

**Benefits**:
- Single parameter instead of 11
- Version stability (can add fields without breaking signature)
- Type safety at boundary

**Drawback**: Adds indirection (one more type to maintain)

**Decision**: DEFER to Phase 3.1 (not required for extraction, but nice-to-have)

### Recommendation 2: Config Slice Pattern

Each analyzer receives only its config slice:

```python
class StarvationAnalyzer:
    def __init__(self, config: StarvationCanaryConfig) -> None:
        self._config = config
        # ...
```

**Benefits**:
- Clear dependency boundaries
- Easier testing (minimal config mocking)
- No hidden config coupling

**Decision**: ADOPT in Phase 3.1 (required for clean extraction)

---

## Risk Matrix

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Circular dependency during extraction | HIGH | LOW | Extract in stages (independent → dependent) |
| Breaking snapshot compatibility | HIGH | MEDIUM | Maintain export/import format, add characterization tests |
| Config coupling fragmentation | MEDIUM | MEDIUM | Use config slice pattern |
| Test suite regression | MEDIUM | LOW | 18 characterization tests must pass unchanged |
| Performance degradation | LOW | LOW | Orchestration overhead minimal (~5 method calls) |

---

## Action Items for Phase 3.1

1. ✅ **Pre-extraction**: Create `src/townlet/stability/analyzers/` directory
2. ✅ **Stage 1**: Extract Starvation, Reward Variance, Option Thrash analyzers
3. ✅ **Stage 2**: Extract Alert Aggregator
4. ✅ **Stage 3**: Extract Promotion Window Evaluator
5. ✅ **Stage 4**: Refactor monitor.py to orchestrate 5 analyzers
6. ✅ **Validation**: Run 18 characterization tests (must pass unchanged)
7. ✅ **Validation**: Run full test suite (must pass)
8. ✅ **Documentation**: Update architecture docs with new structure

---

## Change Log

| Date | Activity | Notes |
|------|----------|-------|
| 2025-10-14 | Import dependency analysis | Mapped internal/external dependencies, identified no circular deps |
| 2025-10-14 | Data flow analysis | Documented 11-parameter input surface, config coupling |
| 2025-10-14 | Extraction order planning | Defined 4-stage extraction strategy |

---

## Next Steps

1. ⬜ Complete Phase 0.4 (this document)
2. ⬜ Phase 0.5: Security Baseline Scan
3. ⬜ Phase 0.6: Rollback Plan Finalization
4. ⬜ Phase 3.1: Begin analyzer extraction following safe order
