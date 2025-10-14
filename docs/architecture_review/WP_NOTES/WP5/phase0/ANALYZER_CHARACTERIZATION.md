# WP5 Phase 0.3: Stability Analyzer Behavior Characterization

**Date Started**: 2025-10-14
**Status**: IN PROGRESS
**Purpose**: Document current StabilityMonitor behavior before extracting analyzers in Phase 3.1

---

## Overview

The `StabilityMonitor` (449 LOC) currently contains 5 distinct analyzers embedded in a monolithic class. Phase 3.1 will extract these into separate, testable, and reusable components.

This document characterizes the behavior of each analyzer to ensure the extracted versions produce identical outputs.

---

## Identified Analyzers

### 1. Starvation Analyzer
**Lines**: 262-296 (`_update_starvation_state`)
**State**: `_starvation_streaks`, `_starvation_active`, `_starvation_incidents`

**Purpose**: Detects agents with critically low hunger (< threshold) for sustained periods

**Algorithm**:
```python
1. Prune old incidents outside rolling window (window_ticks)
2. For each agent with hunger_levels:
   a. If hunger ≤ hunger_threshold:
      - Increment streak counter
      - If streak ≥ min_duration_ticks AND not already active:
        * Record incident (tick, agent_id)
        * Mark agent as active
   b. Else:
      - Clear streak
      - Remove from active set
3. Clear terminated agents from tracking
4. Return total incident count
```

**Configuration**:
- `hunger_threshold`: 0.05 (5% hunger remaining)
- `min_duration_ticks`: 30 (sustained starvation)
- `window_ticks`: 1000 (rolling window)
- `max_incidents`: 0 (alert if ANY incidents)

**Alert**: `"starvation_spike"` when `incidents > max_incidents`

**Edge Cases**:
- Agent terminates → clear streak and active status
- Hunger rises above threshold → reset streak immediately
- Same agent can re-trigger if hunger drops again after recovery

---

### 2. Reward Variance Analyzer
**Lines**: 298-322 (`_update_reward_samples`)
**State**: `_reward_samples` (deque of (tick, reward) tuples)

**Purpose**: Detects high variability in reward signals (unstable policy)

**Algorithm**:
```python
1. Prune old samples outside rolling window (window_ticks)
2. Add all new rewards to sample deque
3. If no samples: return (None, None, 0)
4. Calculate mean: sum(values) / count
5. Calculate variance: sum((value - mean)²) / count
6. Return (variance, mean, count)
```

**Configuration**:
- `window_ticks`: 1000
- `max_variance`: 0.25
- `min_samples`: 20 (don't alert until sufficient data)

**Alert**: `"reward_variance_spike"` when `variance > max_variance AND samples ≥ min_samples`

**Edge Cases**:
- Empty rewards dict → no samples added (valid for some ticks)
- Single sample → variance = 0
- All rewards identical → variance = 0

---

### 3. Option Thrash Analyzer
**Lines**: 333-359 (`_update_option_samples`)
**State**: `_option_samples` (deque of (tick, rate) tuples)

**Purpose**: Detects excessive option switching (policy thrashing)

**Algorithm**:
```python
1. Prune old samples outside rolling window (window_ticks)
2. If option_switch_counts provided:
   a. Sum all switch counts
   b. Divide by active agent count (or len(option_switch_counts) if count=0)
   c. Append (tick, rate) to samples
3. If no samples: return None
4. Return average rate across window
```

**Configuration**:
- `window_ticks`: 600
- `max_switch_rate`: 0.25 (25% of agents switching per tick)
- `min_samples`: 10

**Alert**: `"option_thrash_detected"` when `rate > max_switch_rate AND samples ≥ min_samples`

**Edge Cases**:
- `active_agent_count = 0` → use 1 to avoid division by zero
- Empty `option_switch_counts` → skip sample for this tick
- Rate calculated as total_switches / agents (normalized per-agent rate)

---

### 4. Promotion Window Evaluator
**Lines**: 66-88 (`_finalise_promotion_window`, `_update_promotion_window`)
**State**: `_promotion_*` fields (7 fields)

**Purpose**: Tracks multi-window pass streaks for A/B promotion decisions

**Algorithm**:
```python
# Update (called every tick)
1. Check if current window expired (tick ≥ window_end)
2. If expired, finalize window:
   a. If no disallowed alerts: pass_streak++, last_result="pass"
   b. Else: pass_streak=0, last_result="fail"
   c. candidate_ready = (pass_streak ≥ required_passes)
   d. Start new window
3. Check alerts for this tick:
   - If any disallowed alert: mark window as failed
```

**Configuration**:
- `window_ticks`: 1000 (evaluation window size)
- `required_passes`: 2 (consecutive passing windows)
- `allowed_alerts`: List of non-fatal alerts

**Outputs**:
- `candidate_ready`: bool (true if streak ≥ required_passes)
- `pass_streak`: int (consecutive passing windows)
- `last_result`: "pass" | "fail" | None
- `window_start`: int (tick of current window start)

**Edge Cases**:
- Multiple windows can finalize in single tick (catch-up logic)
- Allowed alerts don't break streak
- Window 0-1000, 1000-2000, etc. (non-overlapping)

---

### 5. Alert Aggregator
**Lines**: 91-223 (`track()` main method)
**State**: `latest_alerts`, `latest_alert`

**Purpose**: Collects alerts from multiple sources into unified alert list

**Alert Sources**:

| Alert | Condition | Source |
|-------|-----------|--------|
| `queue_fairness_pressure` | ghost_step ≥ 5 OR rotation ≥ 5 | Queue metrics delta |
| `embedding_reuse_warning` | reuse_warning flag set | Embedding metrics |
| `affordance_failures_exceeded` | fail_count > threshold | Event stream |
| `lateness_spike` | total_late_ticks > threshold | Job snapshot |
| `employment_exit_queue_overflow` | pending > limit | Employment metrics |
| `employment_exit_backlog` | pending > 0 (soft alert) | Employment metrics |
| `starvation_spike` | From analyzer #1 | Starvation analyzer |
| `option_thrash_detected` | From analyzer #3 | Option thrash analyzer |
| `reward_variance_spike` | From analyzer #2 | Reward variance analyzer |
| `rivalry_spike` | high_intensity events ≥ 5 | Rivalry events |

**Aggregation Logic**:
```python
1. Collect alerts from all sources
2. Update promotion window with alert list
3. Store in latest_alerts (list) and latest_alert (first or None)
4. Include in _latest_metrics dict
```

**Edge Cases**:
- Multiple alerts can fire simultaneously (not mutually exclusive)
- `employment_exit_backlog` only fires if no other alerts (special case)
- Alert order matters for `latest_alert` (first in list)

---

## Data Flow

```
track() inputs
  ↓
┌─────────────────────────────────────────┐
│  Alert Aggregator (#5)                  │
│  ┌───────────────────────────────────┐  │
│  │ Queue fairness checker            │  │
│  │ Embedding reuse checker           │  │
│  │ Affordance failure counter        │  │
│  │ Lateness checker                  │  │
│  │ Employment queue checker          │  │
│  │ Rivalry intensity checker         │  │
│  └───────────────────────────────────┘  │
│         ↓                                │
│  ┌───────────────────────────────────┐  │
│  │ Starvation Analyzer (#1)          │  │
│  │ → incidents count                 │  │
│  └───────────────────────────────────┘  │
│         ↓                                │
│  ┌───────────────────────────────────┐  │
│  │ Option Thrash Analyzer (#3)       │  │
│  │ → option_rate                     │  │
│  └───────────────────────────────────┘  │
│         ↓                                │
│  ┌───────────────────────────────────┐  │
│  │ Reward Variance Analyzer (#2)      │  │
│  │ → variance, mean, count           │  │
│  └───────────────────────────────────┘  │
│         ↓                                │
│  Promotion Window Evaluator (#4)        │
│  ← all alerts                            │
└─────────────────────────────────────────┘
  ↓
latest_metrics output
```

---

## State Management

### Export State Format
```python
{
    "starvation_streaks": {agent_id: int},
    "starvation_active": [agent_id, ...],
    "starvation_incidents": [[tick, agent_id], ...],
    "reward_samples": [[tick, value], ...],
    "option_samples": [[tick, rate], ...],
    "latest_metrics": {...},
    "promotion": {
        "window_start": int,
        "window_failed": bool,
        "pass_streak": int,
        "candidate_ready": bool,
        "last_result": str | None,
        "last_evaluated_tick": int | None,
    }
}
```

### Import State Validation
- All fields optional with safe defaults
- Type coercion for all numeric values
- List/dict type checking before iteration
- Tuple unpacking with length validation

---

## Testing Strategy for Phase 3.1

### Characterization Tests (Phase 0.3)
Create tests that capture current behavior:
```python
def test_starvation_analyzer_behavior():
    """Golden test: verify starvation detection matches current behavior."""
    # Use telemetry baseline from Phase 0.1
    # Replay events through current StabilityMonitor
    # Capture outputs for each tick
    # These outputs become the acceptance criteria
```

### Equivalence Tests (Phase 3.1)
After extraction, verify identical behavior:
```python
def test_extracted_starvation_analyzer_matches_baseline():
    """Verify extracted analyzer produces identical output."""
    # Replay same events through extracted StarvationAnalyzer
    # Compare outputs to Phase 0.3 golden baseline
    # Must match exactly
```

---

## Dependencies Between Analyzers

**Independent Analyzers** (can be extracted separately):
- Starvation Analyzer (#1)
- Reward Variance Analyzer (#2)
- Option Thrash Analyzer (#3)

**Dependent Analyzers** (require others):
- Promotion Window Evaluator (#4) - depends on Alert Aggregator (#5) outputs
- Alert Aggregator (#5) - depends on #1, #2, #3 outputs

**Extraction Order** (Phase 3.1):
1. Extract #1, #2, #3 (independent analyzers)
2. Extract #5 (aggregator) - compose with #1, #2, #3
3. Extract #4 (promotion) - compose with #5

---

## Configuration Coupling

All analyzers read from `SimulationConfig.stability`:
- `StarvationConfig` → Analyzer #1
- `RewardVarianceConfig` → Analyzer #2
- `OptionThrashConfig` → Analyzer #3
- `PromotionConfig` → Analyzer #4
- Various thresholds → Analyzer #5

**Design Decision**: Pass config sections to analyzer constructors (avoid global config)

---

## Edge Cases Discovered During Characterization (Phase 0.3)

### Critical Timing Behaviors

**Starvation Incident Timing (Off-by-One)**
- **Expected**: Incident triggers at tick 30 (after 30 ticks of low hunger)
- **Actual**: Incident triggers at tick 29
- **Reason**: Streak counter increments first (`streak = get()+1`), THEN checks `streak >= 30`
- **Impact**: At tick 0-28, streak builds to 29. At tick 29, streak becomes 30 and incident fires.
- **Extraction requirement**: Preserve this exact behavior (don't "fix" it)

**Promotion Window Finalization**
- **Expected**: Window [0, 1000) finalizes during tick 999
- **Actual**: Window finalizes at tick 1000 (when `tick >= window_end`)
- **Reason**: `while tick >= window_end:` condition in `_update_promotion_window`
- **Impact**: Windows are [0, 1000), [1000, 2000), etc. but finalize on tick 1000, 2000, etc.
- **Extraction requirement**: Must replicate exact finalization timing

### Alert Aggregator Quirks

**Queue Fairness Delta Baseline**
- **Expected**: First call has no baseline, shouldn't alert
- **Actual**: First call uses `previous_queue_metrics.get(key)` which returns `None`, coerced to 0
- **Result**: Delta from 0 to N (where N ≥ 5) triggers alert on first call
- **Impact**: Queue fairness pressure can alert on very first tick if metrics ≥ 5
- **Extraction requirement**: Preserve `last_queue_metrics or {}` pattern

**Employment Exit Backlog Special Case**
- **Behavior**: `employment_exit_backlog` alert only fires if `not alerts` (line 152)
- **Reason**: It's a "soft" alert that shouldn't mask more serious issues
- **Impact**: If any other alert fires, backlog alert is suppressed
- **Extraction requirement**: Alert aggregator must maintain this conditional logic

**Default Allowed Alerts**
- **Expected**: Some alerts like `employment_exit_backlog` might be allowed by default
- **Actual**: `allowed_alerts = ()` (empty tuple) by default
- **Impact**: ALL alerts break promotion streak unless explicitly configured
- **Extraction requirement**: Don't assume any alerts are allowed

### Analyzer Sample Tracking

**Reward Variance Sample Count**
- **Observed**: `min_samples` checks `len(self._reward_samples)`, not number of ticks
- **Impact**: With 30 agents × 10 ticks = 300 samples, alert fires (300 ≥ min_samples=20)
- **Clarification**: Each agent's reward each tick is a separate sample in the deque
- **Extraction requirement**: Sample granularity is per-agent-per-tick, not per-tick

**Option Thrash Zero Agents**
- **Observed**: With empty `option_switch_counts`, a sample is still added: `rate = 0 / 1 = 0.0`
- **Reason**: `agents_considered = 1` when count is 0 (line 440-441)
- **Impact**: Zero agents produces rate of 0.0, not `None`
- **Extraction requirement**: Must preserve division-by-zero guard behavior

### State Export/Import

**JSON Round-trip Compatibility**
- **Observed**: `export_state()` → dict → JSON → dict → `import_state()` preserves state exactly
- **Key conversions**:
  - Deques → lists of [tick, value] pairs
  - Sets → lists
  - All numeric values coerced via `coerce_int`/`coerce_float`
- **Extraction requirement**: Maintain backward compatibility with existing snapshot format

---

## Next Steps (Phase 0.3)

1. ✅ Identify 5 analyzers and document algorithms
2. ✅ Create characterization test with telemetry baseline
3. ✅ Capture golden outputs for each analyzer
4. ✅ Document edge cases discovered during testing
5. ⬜ Create extraction design document for Phase 3.1

---

## Phase 3.1 Extraction Design Preview

**Proposed Structure**:
```
src/townlet/stability/analyzers/
├── __init__.py
├── base.py                  # AnalyzerProtocol
├── starvation.py            # StarvationAnalyzer
├── reward_variance.py       # RewardVarianceAnalyzer
├── option_thrash.py         # OptionThrashAnalyzer
├── alert_aggregator.py      # AlertAggregator
└── promotion_window.py      # PromotionWindowEvaluator
```

**Composition in StabilityMonitor**:
```python
class StabilityMonitor:
    def __init__(self, config):
        self._starvation = StarvationAnalyzer(config.stability.starvation)
        self._reward_variance = RewardVarianceAnalyzer(config.stability.reward_variance)
        self._option_thrash = OptionThrashAnalyzer(config.stability.option_thrash)
        self._alert_aggregator = AlertAggregator(...)
        self._promotion = PromotionWindowEvaluator(config.stability.promotion)

    def track(self, **kwargs):
        # Delegate to analyzers
        incidents = self._starvation.update(...)
        variance, mean, count = self._reward_variance.update(...)
        option_rate = self._option_thrash.update(...)
        alerts = self._alert_aggregator.collect(...)
        self._promotion.update(tick, alerts)
```

---

## LOC Reduction Estimate

Current: 449 LOC monolithic class

After extraction:
- `starvation.py`: ~40 LOC
- `reward_variance.py`: ~30 LOC
- `option_thrash.py`: ~30 LOC
- `alert_aggregator.py`: ~80 LOC
- `promotion_window.py`: ~40 LOC
- `base.py`: ~20 LOC
- `monitor.py` (composition): ~80 LOC

**Total**: ~320 LOC across 7 files
**Reduction**: 29% fewer lines, but better separation of concerns

---

## Change Log

| Date | Activity | Notes |
|------|----------|-------|
| 2025-10-14 | Analyzed StabilityMonitor | Identified 5 analyzers, documented algorithms |
| 2025-10-14 | Created characterization tests | 18 tests covering all 5 analyzers + edge cases, all passing |
| 2025-10-14 | Documented edge cases | 7 critical behaviors discovered through testing |
