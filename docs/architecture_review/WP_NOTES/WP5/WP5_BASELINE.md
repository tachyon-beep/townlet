# WP5 Phase 0.1: Baseline Metrics Capture

**Date**: 2025-10-14
**Purpose**: Establish regression detection baselines for WP5 refactoring activities
**Status**: ✅ COMPLETE

## Overview

Phase 0.1 captured baseline metrics across four dimensions to enable regression detection during WP5 execution:

1. **Performance Baseline** - Tick throughput and latency
2. **Snapshot Baseline** - Pickle-based snapshots for RNG migration testing
3. **Telemetry Baseline** - Event stream for analyzer behavior characterization
4. **Stability Baseline** - Metrics for stability monitor behavior verification

## 1. Performance Baseline

**Captured**: `tests/fixtures/baselines/performance/performance.json`

### Metrics

| Metric | Value | Threshold |
|--------|-------|-----------|
| Average Tick Time | 1.059 ms | ≤ 1.5 ms (41% tolerance) |
| Throughput | 944.29 ticks/sec | ≥ 650 ticks/sec |

### Observations

- Telemetry buffer exceeded 256KB during 100-tick run (expected behavior with stdout transport)
- Thread cleanup warning at shutdown (telemetry worker thread - non-blocking)
- Console auth disabled warnings present (expected in test environment)
- Multiple telemetry global_context snapshot fallbacks occurred

### Regression Detection

Performance tests should verify:
- Average tick time does not exceed **1.5ms** (41% regression tolerance)
- No significant degradation in p95/p99 latencies
- Throughput remains above **650 ticks/second**

**Command to reproduce**:
```bash
.venv/bin/python scripts/benchmark_tick.py configs/examples/poc_hybrid.yaml --ticks 100
```

---

## 2. Snapshot Baseline

**Captured**: `tests/fixtures/baselines/snapshots/snapshot-{10,25,50}.json`

### Files

| Snapshot | Tick | Size | Purpose |
|----------|------|------|---------|
| `snapshot-10.json` | 10 | 29 KB | Early-game state (initial needs decay) |
| `snapshot-25.json` | 25 | 32 KB | Mid-game state (agents engaging with objects) |
| `snapshot-50.json` | 50 | 32 KB | Established state (employment shifts, social interactions) |

### RNG Streams Captured

Each snapshot contains three pickle-encoded RNG streams:
- `world` - World state updates (decay, economy)
- `events` - Perturbation scheduler
- `policy` - Policy decisions

### Usage in WP5

These pickle-based snapshots will be used in **Phase 1.1 (RNG Migration)** to verify:

1. **Deterministic Replay**: Load snapshot → advance N ticks → verify world state matches
2. **Migration Compatibility**: Convert pickle → JSON → reload → verify equivalence
3. **Golden Tests**: Snapshot-based regression tests for RNG determinism

**Test Strategy**:
```python
# Phase 1.1: RNG Migration Golden Test
def test_rng_migration_preserves_determinism():
    # 1. Load pickle-based baseline snapshot
    snapshot_mgr = SnapshotManager(Path("tests/fixtures/baselines/snapshots"))
    snapshot_pickle = snapshot_mgr.load(Path("snapshot-10.json"), config)

    # 2. Advance 10 ticks and capture world state
    loop_pickle = SimulationLoop(config)
    loop_pickle.restore_snapshot(snapshot_pickle)
    for _ in range(10):
        loop_pickle.step()
    state_pickle = capture_world_hash(loop_pickle.world)

    # 3. Convert to JSON-based RNG encoding
    snapshot_json = migrate_rng_to_json(snapshot_pickle)

    # 4. Replay with JSON encoding
    loop_json = SimulationLoop(config)
    loop_json.restore_snapshot(snapshot_json)
    for _ in range(10):
        loop_json.step()
    state_json = capture_world_hash(loop_json.world)

    # 5. Verify equivalence
    assert state_pickle == state_json, "RNG migration broke determinism"
```

---

## 3. Telemetry Baseline

**Captured**: `tests/fixtures/baselines/telemetry/events.jsonl` (107 KB, 73 events)

### Event Types

| Event Type | Count | Description |
|------------|-------|-------------|
| `snapshot` | 1 | Full world snapshot at tick 1 |
| `diff` | 25 | Incremental world state changes (ticks 2-26) |

### Event Schema

**Snapshot Event** (tick 1):
```json
{
  "schema_version": "0.9.7",
  "tick": 1,
  "runtime_variant": "facade",
  "payload_type": "snapshot",
  "queue_metrics": {...},
  "embedding_metrics": {...},
  "employment": {...},
  "conflict": {...},
  "relationships": {...},
  "stability": {...},
  "promotion": {...},
  "perturbations": {...}
}
```

**Diff Event** (ticks 2+):
```json
{
  "schema_version": "0.9.7",
  "tick": N,
  "payload_type": "diff",
  "changes": {
    "conflict": {...},
    "stability": {...}
  }
}
```

### Usage in WP5

Telemetry events will be used in **Phase 0.3 (Analyzer Behavior Characterization)**:

1. **Replay baseline events** through StabilityMonitor to capture analyzer outputs
2. **Extract 5 analyzer behaviors** for modularization in Phase 3.1:
   - Starvation detector
   - Reward variance tracker
   - Option thrash detector
   - Queue conflict analyzer
   - Promotion evaluator
3. **Create characterization tests** to verify modularized analyzers match original behavior

---

## 4. Stability Baseline

**Captured**: `tests/fixtures/baselines/stability/metrics.json`

### Metrics Snapshot (Tick 3)

```json
{
  "metrics": {
    "starvation_incidents": 0,
    "starvation_window_ticks": 1000,
    "option_switch_rate": 0.0,
    "option_samples": 3,
    "reward_variance": null,
    "reward_mean": null,
    "reward_samples": 0,
    "queue_totals": {
      "cooldown_events": 0,
      "ghost_step_events": 0,
      "rotation_events": 0
    },
    "queue_deltas": {
      "cooldown_events": 0,
      "ghost_step_events": 0,
      "rotation_events": 0
    },
    "rivalry_events": [],
    "alerts": []
  }
}
```

### Thresholds Configured

| Analyzer | Threshold | Window | Purpose |
|----------|-----------|--------|---------|
| **Starvation** | max_incidents=0, hunger>0.05 | 1000 ticks | Detect chronic hunger |
| **Reward Variance** | max_variance=0.25 | 1000 ticks | Detect reward instability |
| **Option Thrash** | max_switch_rate=0.25 | 600 ticks | Detect option flapping |
| **Affordance Fail** | threshold=5 | - | Detect repeated failures |
| **Lateness** | threshold=3 | - | Detect employment issues |

### Promotion State

```json
{
  "state": "monitoring",
  "pass_streak": 0,
  "required_passes": 2,
  "candidate_ready": false,
  "current_release": {"config_id": "v1.3.0"}
}
```

---

## Baseline Completeness Checklist

- [x] **Performance baseline** captured (1.059 ms/tick)
- [x] **Snapshot baseline** captured (3 snapshots at ticks 10, 25, 50)
- [x] **Telemetry baseline** captured (73 events, 107 KB)
- [x] **Stability baseline** captured (metrics + thresholds)
- [x] **Baseline documentation** created (this file)

---

## Next Steps (Phase 0.2)

**Activity**: Create RNG Migration Test Suite
**Input**: Baseline snapshots from Phase 0.1
**Output**: 13+ golden tests for RNG determinism

**Test Categories**:
1. **Golden Tests** (5+) - Deterministic replay from snapshots
2. **Round-trip Tests** (3+) - Pickle → JSON → Pickle equivalence
3. **Migration Tests** (5+) - Backward compatibility with pickle-based snapshots

**Exit Criteria**:
- All golden tests passing with pickle-based RNG
- Test harness ready for JSON migration in Phase 1.1
- Documented test strategy for RNG migration rollback

---

## Rollback Information

**Baseline Artifacts Location**: `tests/fixtures/baselines/`

**Rollback Procedure**: No rollback needed - Phase 0.1 is read-only baseline capture

**Verification**:
```bash
# Verify all baseline artifacts exist
test -f tests/fixtures/baselines/performance/performance.json && \
test -f tests/fixtures/baselines/snapshots/snapshot-10.json && \
test -f tests/fixtures/baselines/snapshots/snapshot-25.json && \
test -f tests/fixtures/baselines/snapshots/snapshot-50.json && \
test -f tests/fixtures/baselines/telemetry/events.jsonl && \
test -f tests/fixtures/baselines/stability/metrics.json && \
echo "✓ All baseline artifacts present" || echo "✗ Missing baseline artifacts"
```

---

## Phase 0.1 Completion Summary

**Status**: ✅ **COMPLETE**
**Duration**: ~1 hour
**Artifacts**: 7 files (performance.json, 3 snapshots, events.jsonl, metrics.json, WP5_BASELINE.md)
**Blockers**: None
**Risks Mitigated**:
- ✅ RNG migration regression risk → Baseline snapshots for golden tests
- ✅ Performance regression risk → Tick throughput baseline
- ✅ Stability analyzer behavior risk → Telemetry event stream for characterization

**Ready for Phase 0.2**: Create RNG Migration Test Suite
