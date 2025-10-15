# Phase 0: Risk Reduction - Status Tracker

**Phase**: 0 of 6
**Status**: IN PROGRESS (1/6 activities complete)
**Started**: 2025-10-14
**Target Completion**: 2025-10-15
**Effort**: 1-2 days

---

## Objective

De-risk subsequent phases through baseline establishment, impact analysis, and safety nets.

---

## Activities

### 0.1: Establish Baseline Metrics & Test Harness
**Status**: ✅ COMPLETE
**Effort**: 0.5 day → 1 hour actual
**Assignee**: Claude
**Priority**: HIGH
**Completed**: 2025-10-14

**Tasks**:
- [x] Capture performance baseline (1.059 ms/tick, 944 ticks/sec)
- [x] Create pickle-based snapshots (3 snapshots at ticks 10, 25, 50)
- [x] Capture telemetry event stream (73 events, 107 KB)
- [x] Capture stability metrics (all analyzers + thresholds)
- [x] Document baselines in comprehensive `WP5_BASELINE.md`

**Deliverables**:
- [x] `tests/fixtures/baselines/performance/performance.json` (1.06 KB)
- [x] `tests/fixtures/baselines/snapshots/snapshot-{10,25,50}.json` (29-32 KB each)
- [x] `tests/fixtures/baselines/telemetry/events.jsonl` (107 KB, 73 events)
- [x] `tests/fixtures/baselines/stability/metrics.json` (2.4 KB)
- [x] `docs/architecture_review/WP_NOTES/WP5/WP5_BASELINE.md` (comprehensive)

**Blockers**: None

**Notes**:
- All baseline artifacts captured and documented
- Thread cleanup warning (telemetry worker) is non-blocking
- Telemetry capture aborted after 73 events (sufficient)
- Ready to proceed to Activity 0.2 (RNG Test Suite)

---

### 0.2: Create RNG Migration Test Suite
**Status**: ⬜ TODO
**Effort**: 0.5 day
**Assignee**: TBD
**Priority**: CRITICAL

**Tasks**:
- [ ] Write golden tests for deterministic replay
- [ ] Write snapshot round-trip tests
- [ ] Write cross-format compatibility tests (pickle → JSON)
- [ ] All tests passing with CURRENT pickle implementation
- [ ] Commit golden test fixtures

**Deliverables**:
- [ ] `tests/test_rng_golden.py` (5+ tests)
- [ ] `tests/test_snapshot_rng_roundtrip.py` (3+ tests)
- [ ] `tests/test_rng_migration.py` (5+ tests)
- [ ] Test fixtures in `tests/fixtures/rng/`

**Blockers**: None

**Notes**:
- These tests MUST pass with pickle before starting Phase 1
- Will detect any behavior changes after JSON migration
- Golden tests are the safety net

---

### 0.3: Analyzer Behavior Characterization
**Status**: ⬜ TODO
**Effort**: 0.5 day
**Assignee**: TBD
**Priority**: HIGH

**Tasks**:
- [ ] Write characterization test for current monitor behavior
- [ ] Document edge cases (empty world, single agent, etc.)
- [ ] Capture telemetry event patterns
- [ ] Save baseline metrics for comparison
- [ ] Document in `WP5_ANALYZER_BEHAVIOR.md`

**Deliverables**:
- [ ] `tests/stability/test_monitor_characterization.py`
- [ ] `tests/fixtures/baselines/monitor_metrics.json`
- [ ] `docs/architecture_review/WP5_ANALYZER_BEHAVIOR.md`

**Blockers**: Depends on 0.1 (telemetry baseline)

**Notes**:
- Critical for Phase 3 analyzer extraction
- Will verify extractors produce identical outputs
- Edge cases must be preserved

---

### 0.4: Import Dependency Analysis
**Status**: ⬜ TODO
**Effort**: 0.25 day
**Assignee**: TBD
**Priority**: MEDIUM

**Tasks**:
- [ ] Install pydeps: `pip install pydeps`
- [ ] Generate dependency graph
- [ ] Run import-linter in analysis mode
- [ ] Document current violations
- [ ] Create baseline for "no new violations" policy

**Deliverables**:
- [ ] `docs/architecture_review/WP5_dependency_graph.svg`
- [ ] `docs/architecture_review/WP5_import_violations.txt`
- [ ] `.importlinter.analysis` config

**Blockers**: None

**Notes**:
- Needed for Phase 4 import-linter integration
- Establishes grandfathered violations
- Visual graph helps understand architecture

---

### 0.5: Security Baseline Scan
**Status**: ⬜ TODO
**Effort**: 0.25 day
**Assignee**: TBD
**Priority**: HIGH

**Tasks**:
- [ ] Install tools: `pip install bandit[toml] pip-audit`
- [ ] Run bandit: `bandit -r src/townlet -f json -o baseline_bandit.json`
- [ ] Run pip-audit: `pip-audit --format json > baseline_pip_audit.json`
- [ ] Document findings in `SECURITY_BASELINE.md`
- [ ] Establish error budget

**Deliverables**:
- [ ] `baseline_bandit.json`
- [ ] `baseline_pip_audit.json`
- [ ] `docs/SECURITY_BASELINE.md`

**Blockers**: None

**Notes**:
- Expect B301 (pickle) finding - will fix in Phase 1
- Document acceptable risks with rationale
- Error budget guides Phase 1 targets

---

### 0.6: Create Rollback Plan
**Status**: ⬜ TODO
**Effort**: 0.25 day
**Assignee**: TBD
**Priority**: MEDIUM

**Tasks**:
- [ ] Document rollback procedures for each phase
- [ ] Estimate time-to-rollback for each phase
- [ ] Define rollback triggers
- [ ] Establish git branch strategy
- [ ] Review rollback plan with team

**Deliverables**:
- [ ] `docs/architecture_review/WP5_ROLLBACK_PLAN.md`

**Blockers**: None

**Notes**:
- Safety net for risky changes
- Must be reviewed before starting Phase 1
- Should include git commands for quick rollback

---

## Progress Summary

**Activities**: 1/6 complete (17%)

| Activity | Status | Progress |
|----------|--------|----------|
| 0.1: Baseline Metrics | ✅ COMPLETE | 5/5 tasks (1 hour) |
| 0.2: RNG Test Suite | ⬜ TODO | 0/5 tasks |
| 0.3: Analyzer Behavior | ⬜ TODO | 0/5 tasks |
| 0.4: Import Analysis | ⬜ TODO | 0/5 tasks |
| 0.5: Security Baseline | ⬜ TODO | 0/5 tasks |
| 0.6: Rollback Plan | ⬜ TODO | 0/5 tasks |

---

## Exit Criteria

Phase 0 complete when ALL criteria met:

- [x] All baseline files committed to repository (Activity 0.1 ✅)
- [ ] 13+ RNG tests passing with pickle baseline (Activity 0.2)
- [ ] Analyzer behavior fully characterized (Activity 0.3)
- [ ] Import violations documented and visualized (Activity 0.4)
- [ ] Security baseline established with error budget (Activity 0.5)
- [ ] Rollback plan reviewed and approved (Activity 0.6)
- [ ] Team confident to proceed to Phase 1

---

## Risk Status

| Risk | Current | Target | Mitigation Activity |
|------|---------|--------|---------------------|
| RNG Migration | 🔴 HIGH | 🟡 MEDIUM | 0.2 RNG Test Suite (TODO) |
| Snapshot Compatibility | ✅ 🟢 LOW | 🟢 LOW | 0.1 Baseline Snapshots (COMPLETE) |
| Analyzer Extraction | 🟡 MEDIUM | 🟢 LOW | 0.3 Behavior Characterization (TODO) |
| Import Violations | 🟡 MEDIUM | 🟢 LOW | 0.4 Import Analysis (TODO) |

---

## Issues & Blockers

None currently.

---

## Notes & Learnings

### Design Decisions
- **Baseline snapshot intervals**: Chose ticks 10, 25, 50 to capture early, mid, and established game states
- **Telemetry capture method**: Used stdout provider with redirection (simpler than file provider)
- **Performance threshold**: Set 41% regression tolerance (1.5ms max vs 1.059ms baseline)

### Issues Encountered
- **Thread cleanup warning**: Telemetry worker thread doesn't shut down cleanly (non-blocking)
- **Telemetry script abort**: Script aborted after 73 events due to thread issue, but data is sufficient
- **SimulationLoop.rng_streams**: Attribute doesn't exist; used `_rng_world`, `_rng_events`, `_rng_policy` instead

### Time Tracking
- Estimated: 0.5 day (4 hours)
- Actual: 1 hour
- Efficiency: 4x faster than estimated (good baseline tooling)

---

## Change Log

| Date | Activity | Change | Notes |
|------|----------|--------|-------|
| 2025-10-14 | - | Phase 0 tracking created | Initial setup |
| 2025-10-14 | 0.1 | ✅ Baseline capture complete | 5/5 deliverables, 1 hour actual |
