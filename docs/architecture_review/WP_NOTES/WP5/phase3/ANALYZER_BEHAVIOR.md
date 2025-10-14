# StabilityMonitor Analyzer Behavior Documentation

**Status**: Phase 3 Pre-Execution Risk Reduction
**Date**: 2025-10-14
**Purpose**: Document current monolithic monitor behavior BEFORE extraction

---

## Overview

The current `StabilityMonitor` (`src/townlet/stability/monitor.py`, 450 LOC) contains 5 distinct analyzer logics that will be extracted into separate classes in Phase 3.1.

This document maps the current code to the future analyzer architecture.

---

## Analyzer Mapping

### 1. **Fairness Analyzer** (Queue Conflict Detection)

**Current Location**: `monitor.py:111-126`

**Logic**:
```python
# Lines 111-126
fairness_delta = calculate queue event deltas (cooldown, ghost_step, rotation)
if ghost_step_events >= 5 or rotation_events >= 5:
    alerts.append("queue_fairness_pressure")
```

**Inputs**:
- `queue_metrics`: Current tick's queue metrics
- `previous_queue_metrics`: Last tick's queue metrics

**Outputs**:
- `fairness_delta`: Dict with cooldown, ghost_step, rotation event counts
- Alert: `"queue_fairness_pressure"` (threshold: 5 events)

**Threshold**: `_fairness_alert_limit = 5`

**Edge Cases**:
- Empty queue metrics → No alert
- First tick (no previous metrics) → Delta is 0

---

### 2. **Starvation Detector**

**Current Location**: `monitor.py:155-164, 352-386`

**Logic**:
```python
# Lines 352-386: _update_starvation_state()
For each agent:
    if hunger <= threshold (0.05):
        increment streak counter
        if streak >= min_duration (30 ticks) and not already active:
            add incident (tick, agent_id)
            mark as active
    else:
        reset streak, remove from active

# Lines 155-164: Alert check
if starvation_incidents > max_incidents:
    alerts.append("starvation_spike")
```

**Inputs**:
- `hunger_levels`: Dict[agent_id, hunger_value]
- `terminated`: Dict[agent_id, bool]
- `tick`: Current simulation tick

**State**:
- `_starvation_streaks`: Dict[agent_id, int] — Consecutive low-hunger ticks
- `_starvation_active`: Set[agent_id] — Currently starving agents
- `_starvation_incidents`: Deque[(tick, agent_id)] — Rolling window of incidents

**Outputs**:
- `starvation_incidents`: Count of incidents in rolling window
- Alert: `"starvation_spike"` (threshold: max_incidents from config)

**Config**:
- `hunger_threshold`: 0.05 (below = starving)
- `min_duration_ticks`: 30 (must be sustained)
- `window_ticks`: 1000 (rolling window for incidents)
- `max_incidents`: 0 (any incident triggers alert)

**Edge Cases**:
- Agent terminates → Clear from streaks and active set
- No agents → incidents = 0, no alert
- Window boundary → Old incidents expire

---

### 3. **Rivalry Tracker**

**Current Location**: `monitor.py:172-184`

**Logic**:
```python
# Lines 172-184
rivalry_events_list = filter and convert rivalry events to dicts
high_intensity = [e for e in rivalry_events if intensity >= avoid_threshold]
if len(high_intensity) >= 5:
    alerts.append("rivalry_spike")
```

**Inputs**:
- `rivalry_events`: Iterable[Dict] — Rivalry events from world
- `config.conflict.rivalry.avoid_threshold`: Intensity threshold (default: 0.8)

**Outputs**:
- `rivalry_events_list`: List of rivalry event dicts
- Alert: `"rivalry_spike"` (threshold: 5 high-intensity events)

**Threshold**: 5 events per tick

**Edge Cases**:
- Empty rivalry events → No alert
- All events below threshold → No alert

---

### 4. **Reward Variance Analyzer**

**Current Location**: `monitor.py:192-201, 388-412`

**Logic**:
```python
# Lines 388-412: _update_reward_samples()
# Add all agent rewards to rolling window
for agent_reward in rewards.values():
    _reward_samples.append((tick, reward))

# Remove samples outside window
cutoff = tick - window_ticks
while _reward_samples[0][0] <= cutoff:
    _reward_samples.popleft()

# Calculate variance
mean = sum(values) / len(values)
variance = sum((v - mean)^2 for v in values) / len(values)

# Lines 192-201: Alert check
if variance > max_variance and len(samples) >= min_samples:
    alerts.append("reward_variance_spike")
```

**Inputs**:
- `rewards`: Dict[agent_id, float]
- `tick`: Current simulation tick

**State**:
- `_reward_samples`: Deque[(tick, reward)] — Rolling window of rewards

**Outputs**:
- `reward_variance`: Float | None — Variance across window
- `reward_mean`: Float | None — Mean across window
- `reward_samples`: int — Sample count
- Alert: `"reward_variance_spike"`

**Config**:
- `window_ticks`: 1000
- `max_variance`: 0.25
- `min_samples`: 20

**Edge Cases**:
- No samples → variance = None, mean = None
- Single sample → variance = 0.0
- Window boundary → Old samples expire

---

### 5. **Option Thrash Detector**

**Current Location**: `monitor.py:166-190, 423-449`

**Logic**:
```python
# Lines 423-449: _update_option_samples()
# Calculate switch rate
total_switches = sum(option_switch_counts.values())
agents_considered = active_agent_count or len(option_switch_counts)
rate = total_switches / agents_considered
_option_samples.append((tick, rate))

# Remove samples outside window
cutoff = tick - window_ticks
while _option_samples[0][0] <= cutoff:
    _option_samples.popleft()

# Calculate average rate
average_rate = sum(rates) / len(rates)

# Lines 186-190: Alert check
if rate > max_switch_rate and len(samples) >= min_samples:
    alerts.append("option_thrash_detected")
```

**Inputs**:
- `option_switch_counts`: Dict[agent_id, int]
- `active_agent_count`: int

**State**:
- `_option_samples`: Deque[(tick, rate)] — Rolling window of switch rates

**Outputs**:
- `option_switch_rate`: Float | None — Average switch rate
- `option_samples`: int — Sample count
- Alert: `"option_thrash_detected"`

**Config**:
- `window_ticks`: 600
- `max_switch_rate`: 0.25
- `min_samples`: 10

**Edge Cases**:
- No option counts → rate = None
- Zero active agents → rate = None (or use 1 as denominator)
- Window boundary → Old samples expire

---

## Other Alert Sources (Not Analyzers)

### Embedding Reuse Warning
**Location**: `monitor.py:127-128`
```python
if embedding_metrics and embedding_metrics.get("reuse_warning"):
    alerts.append("embedding_reuse_warning")
```

### Affordance Failures
**Location**: `monitor.py:130-134`
```python
fail_count = count affordance_fail events
if fail_count > fail_threshold:
    alerts.append("affordance_failures_exceeded")
```

### Lateness Spike
**Location**: `monitor.py:136-145`
```python
lateness_total = sum(late_ticks_today for all agents)
if lateness_total > lateness_threshold:
    alerts.append("lateness_spike")
```

### Employment Queue Overflow
**Location**: `monitor.py:147-153`
```python
if pending > queue_limit:
    alerts.append("employment_exit_queue_overflow")
elif pending and not other_alerts:
    alerts.append("employment_exit_backlog")
```

---

## Extraction Plan

### Phase 3.1: Extract Analyzers

**Step 1**: Create analyzer protocol
```python
class StabilityAnalyzer(Protocol):
    def analyze(self, world: WorldState, tick: int) -> dict[str, Any]:
        """Compute metrics and return dict of metric_name -> value."""
        ...

    def check_alert(self, tick: int) -> str | None:
        """Return alert name if threshold exceeded, else None."""
        ...
```

**Step 2**: Extract each analyzer into `stability/analyzers/`:
- `fairness.py` → FairnessAnalyzer
- `starvation.py` → StarvationDetector
- `rivalry.py` → RivalryTracker
- `reward_variance.py` → RewardVarianceAnalyzer
- `option_thrash.py` → OptionThrashDetector

**Step 3**: Slim monitor to coordinator (<100 LOC):
```python
class StabilityMonitor:
    def __init__(self, config):
        self.analyzers = [
            FairnessAnalyzer(config),
            StarvationDetector(config),
            # ...
        ]

    def track(self, **kwargs):
        for analyzer in self.analyzers:
            metrics = analyzer.analyze(**kwargs)
            alert = analyzer.check_alert()
            # Aggregate
```

---

## Behavioral Invariants (MUST PRESERVE)

1. **Metric Names**: All current metric names must be preserved
2. **Alert Names**: All 10 alert names must remain unchanged
3. **Alert Thresholds**: Thresholds from config must produce same alerts
4. **Rolling Windows**: Window calculations must match exactly
5. **Edge Cases**: Empty world, single agent, etc. must behave identically

---

## Testing Strategy

**Before Extraction**:
- ✅ Baseline metrics captured (`test_monitor_baseline.py`)
- ✅ Edge cases documented (`test_monitor_edge_cases.py`)

**After Extraction**:
- Run `test_monitor_refactor_compatibility.py` to compare baseline
- All edge case tests must pass unchanged
- 100 tick deterministic replay must match baseline exactly

---

## Risks

**HIGH RISK**: Floating point precision in variance calculations
- **Mitigation**: Allow <0.1% tolerance in comparison test

**MEDIUM RISK**: Rolling window boundary conditions
- **Mitigation**: Edge case tests cover window transitions

**LOW RISK**: Alert ordering changes
- **Mitigation**: Alerts are unordered (use set comparison)

---

**End of Analyzer Behavior Documentation**
