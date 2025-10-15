# WP5 Phase 0.2: RNG Migration Test Suite - Status

**Date Started**: 2025-10-14
**Status**: IN PROGRESS (50% complete)
**Purpose**: Create comprehensive test suite to ensure RNG migration preserves determinism

---

## Overview

Phase 0.2 creates a safety net of golden tests that MUST pass with the current pickle-based RNG implementation before migrating to JSON in Phase 1.1. Any failures after migration indicate determinism was broken.

---

## Test Suite Progress

### ✅ Golden Tests (6/6 tests created)

**File**: `tests/test_rng_golden.py`
**Status**: Created, 1/6 passing

| Test | Status | Purpose |
|------|--------|---------|
| `test_rng_determinism_from_tick_10` | ⚠️ NEEDS HASH | Load snapshot-10, advance 10 ticks, verify world hash |
| `test_rng_determinism_from_tick_25` | ⚠️ NEEDS HASH | Load snapshot-25, advance 15 ticks, verify world hash |
| `test_rng_determinism_from_tick_50` | ⚠️ NEEDS HASH | Load snapshot-50, advance 20 ticks, verify world hash |
| `test_rng_stream_independence` | ⚠️ NEEDS RUN | Verify world/events/policy RNG streams are independent |
| `test_rng_determinism_repeated_replay` | ⚠️ NEEDS RUN | Verify replaying snapshot twice gives identical results |
| `test_rng_state_serialization_roundtrip` | ✅ PASSING | Verify encode→decode preserves RNG state |

**Next Steps**:
1. Run golden tests to capture reference hashes
2. Update tests with captured hashes
3. Verify all 6 tests pass consistently

---

### ⬜ Snapshot Round-trip Tests (0/3 tests)

**File**: `tests/test_snapshot_rng_roundtrip.py` (NOT CREATED)
**Status**: TODO

Planned tests:
- `test_snapshot_roundtrip_tick_10` - Save→Load snapshot, verify identical state
- `test_snapshot_roundtrip_tick_25` - Same at different game state
- `test_snapshot_roundtrip_rng_independence` - Verify RNG state isolation

**Purpose**: Ensure snapshot save/load cycle preserves RNG state perfectly

---

### ⬜ Migration Compatibility Tests (0/5 tests)

**File**: `tests/test_rng_migration.py` (NOT CREATED)
**Status**: TODO

Planned tests:
- `test_pickle_to_json_conversion` - Convert pickle RNG → JSON RNG, verify equivalence
- `test_json_rng_determinism` - Verify JSON-based RNG produces same sequence as pickle
- `test_json_rng_snapshot_compatibility` - Verify JSON RNG snapshots work with old pickles
- `test_json_encode_decode_roundtrip` - JSON-specific serialization test
- `test_migration_preserves_world_hash` - End-to-end migration verification

**Purpose**: These tests will FAIL initially (JSON RNG doesn't exist yet). They become the acceptance criteria for Phase 1.1.

---

## Test Infrastructure

### Helper Functions

```python
def compute_world_hash(loop: SimulationLoop) -> str:
    """Compute deterministic hash of world state.

    Captures:
    - Agent positions, needs, cash
    - Object positions and types
    - Economy settings
    - Tick counter
    """
```

**Design Decision**: Hash includes sufficient state to detect RNG divergence without being brittle to config changes.

---

## Baseline Snapshots

Tests use pickle-based snapshots from Phase 0.1:
- `tests/fixtures/baselines/snapshots/snapshot-10.json` (29 KB) - Early game
- `tests/fixtures/baselines/snapshots/snapshot-25.json` (32 KB) - Mid game
- `tests/fixtures/baselines/snapshots/snapshot-50.json` (32 KB) - Established game

All 3 snapshots verified to exist and load successfully.

---

## Phase 0.2 Exit Criteria

- [ ] 6/6 golden tests passing with pickle RNG
- [ ] 3/3 round-trip tests passing
- [ ] 5/5 migration tests created (will fail - that's expected)
- [ ] All test fixtures committed to repository
- [ ] Test suite documented in this file

**Current Progress**: 1/14 tests passing (7%)

---

## Known Issues

### Issue 1: Golden Hash Placeholders

**Description**: Golden tests currently use placeholder hashes:
```python
expected_hash = "GOLDEN_HASH_TICK_10_PLUS_10"  # Placeholder
```

**Fix**: Run tests to capture actual hashes, update test file with real values

**Workaround**: Tests currently print hash and skip assertion if placeholder detected

---

### Issue 2: Telemetry Thread Cleanup

**Description**: Test runs end with thread cleanup warning:
```
Fatal Python error: _enter_buffered_busy: could not acquire lock for <_io.BufferedWriter name='<stdout>'>
at interpreter shutdown, possibly due to daemon threads
```

**Impact**: Non-blocking - tests complete successfully, warning occurs during cleanup

**Root Cause**: Telemetry worker thread doesn't shut down cleanly

**Action**: Document as known issue, fix not required for Phase 0.2 completion

---

## Time Tracking

- **Estimated**: 0.5 day (4 hours)
- **Actual**: 2 hours (so far)
- **Remaining**: ~2 hours (round-trip + migration tests)

---

## Change Log

| Date | Activity | Progress |
|------|----------|----------|
| 2025-10-14 | Created test_rng_golden.py | 6 golden tests, 1/6 passing |

---

## Next Session TODO

1. **Capture Golden Hashes**:
   ```bash
   .venv/bin/pytest tests/test_rng_golden.py::TestRNGDeterminism::test_rng_determinism_from_tick_10 -v -s
   # Copy hash from output
   # Update test file with actual hash
   # Repeat for tick 25 and tick 50
   ```

2. **Create Round-trip Tests** (`tests/test_snapshot_rng_roundtrip.py`):
   - Test snapshot save→load preserves RNG state
   - Test across all 3 baseline snapshots

3. **Create Migration Tests** (`tests/test_rng_migration.py`):
   - Write tests that will guide Phase 1.1 JSON implementation
   - Tests should FAIL initially - that's the design

4. **Run Full Suite**:
   ```bash
   .venv/bin/pytest tests/test_rng_*.py -v
   ```

5. **Commit Test Suite**:
   ```bash
   git add tests/test_rng_*.py tests/fixtures/baselines/
   git commit -m "WP5 Phase 0.2: Add RNG migration golden test suite"
   ```
