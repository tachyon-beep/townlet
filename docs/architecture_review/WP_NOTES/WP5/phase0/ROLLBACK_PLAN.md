# WP5 Rollback Plan

**Created**: 2025-10-14
**Version**: 1.0
**Status**: ACTIVE

---

## Executive Summary

This document defines rollback procedures for each risky change in WP5, establishing clear triggers, procedures, and recovery paths. The goal is to enable **confident refactoring** with the ability to quickly revert changes if issues arise.

**Pre-1.0 Philosophy: FAIL FORWARD** 🚀
- ✅ **No backward compatibility** - Clean breaks when migrating
- ✅ **No feature flags** - One implementation, not two
- ✅ **No dual codepaths** - pickle → JSON = full switch, no "support both"
- ✅ **Breaking changes OK** - Users on main expect movement
- ✅ **Rollback = git revert** - Not "keep old code around"

**Key Principles**:
1. **Fast rollback** - All procedures target <1 hour recovery time
2. **Clear triggers** - Objective criteria for when to rollback
3. **Documented steps** - No ambiguity during incident response
4. **Version control** - Git-based rollback strategy
5. **Test validation** - All rollbacks verified with test suite
6. **Clean breaks** - No backward compatibility burden

---

## Rollback Strategy Overview

### Git Branching Strategy

```
main
  ├─ feature/wp5-phase0-baselines  (Phase 0.1-0.6)
  ├─ feature/wp5-phase1-rng        (Phase 1.1-1.2)
  ├─ feature/wp5-phase2-quality    (Phase 2.1-2.2)
  ├─ feature/wp5-phase3-analyzers  (Phase 3.1-3.2)
  ├─ feature/wp5-phase4-boundaries (Phase 4.1)
  └─ feature/wp5-phase5-polish     (Phase 5.1-5.2)
```

**Rollback Pattern**:
1. Each phase on separate feature branch
2. Merge to main only after phase acceptance criteria met
3. Rollback = revert merge commit or checkout pre-merge main
4. Cherry-pick fixes to new attempt branch

### Automated Rollback Detection

```yaml
# .github/workflows/wp5_safety.yml
name: WP5 Safety Checks

on: [push, pull_request]

jobs:
  baseline_comparison:
    runs-on: ubuntu-latest
    steps:
      - name: Run performance baseline
        run: python scripts/benchmark_tick.py --compare-to=baseline_perf.txt

      - name: Check for regression
        run: |
          if [ $PERF_DELTA -gt 5 ]; then
            echo "::error::Performance regression detected: ${PERF_DELTA}%"
            exit 1
          fi

      - name: Run characterization tests
        run: pytest tests/stability/test_monitor_characterization.py --strict

      - name: Snapshot compatibility
        run: pytest tests/test_snapshot_rng_roundtrip.py --strict
```

---

## Phase 0: Risk Reduction Rollback

**Phase 0 is low-risk** (baseline capture only), but rollback procedures are provided for completeness.

### Phase 0 Rollback Triggers

| Trigger | Criteria | Action |
|---------|----------|--------|
| Baseline invalid | Tests fail against captured baseline | Re-run Phase 0 |
| Storage overflow | Baseline files > 1GB | Reduce baseline size |

### Phase 0 Rollback Procedure

**Time to Rollback**: <15 minutes

```bash
# Phase 0 creates artifacts, no code changes
# If baseline invalid, simply re-run:

# 1. Delete invalid baselines
rm -rf tests/fixtures/baselines/

# 2. Re-run baseline capture
pytest tests/test_baseline_capture.py --save-baselines

# 3. Commit new baselines
git add tests/fixtures/baselines/
git commit -m "Re-capture baselines for WP5"
```

**Validation**:
```bash
# Verify baselines are valid
pytest tests/test_baseline_validation.py
```

---

## Phase 1: Security Hardening Rollback

### Phase 1.1: RNG Migration Rollback

**Risk Level**: HIGH (pickle → JSON encoding change)

#### Rollback Triggers

| Trigger | Criteria | Action |
|---------|----------|--------|
| **Snapshot incompatibility** | `test_snapshot_rng_roundtrip.py` fails | IMMEDIATE ROLLBACK |
| **Determinism failure** | `test_rng_golden.py` fails | IMMEDIATE ROLLBACK |
| **Performance regression** | Tick time >5% slower | ROLLBACK if critical |
| **Migration failures** | >10% of snapshots fail to migrate | ROLLBACK |

#### Rollback Procedure

**Time to Rollback**: <30 minutes

**Step 1: Revert Code Changes**
```bash
# Identify RNG migration commits
git log --oneline --grep="RNG" --since="2025-10-14"

# Revert RNG changes
git revert <commit-hash-rng-json>
git revert <commit-hash-snapshot-updates>

# Or revert entire feature branch merge
git revert -m 1 <merge-commit-hash>
```

**Step 2: Restore Pickle Implementation**
```bash
# Checkout pre-migration version
git checkout feature/wp5-phase1-rng~1 -- src/townlet/utils/rng.py
git checkout feature/wp5-phase1-rng~1 -- src/townlet/snapshots/state.py

# Remove migration code
git rm src/townlet/snapshots/migrations/rng_pickle_to_json.py
```

**Step 3: Verify Rollback**
```bash
# Run snapshot tests
pytest tests/test_snapshot_manager.py -v
pytest tests/test_rng_golden.py -v
pytest tests/test_snapshot_rng_roundtrip.py -v

# Verify bandit accepts pickle (with documented exception)
bandit -r src/townlet/utils/rng.py
```

**Step 4: Document Failure**
```bash
# Create rollback report
cat > docs/architecture_review/WP_NOTES/WP5/ROLLBACK_REPORT_PHASE1.md <<'EOF'
# Phase 1.1 RNG Migration Rollback

**Date**: $(date +%Y-%m-%d)
**Trigger**: [Describe trigger]
**Root Cause**: [Analyze what went wrong]

## Failure Analysis
- Test failures: [List failed tests]
- Error messages: [Include error output]
- Hypothesis: [Why did it fail?]

## Rollback Verification
- [x] Code reverted to pickle implementation
- [x] All snapshot tests passing
- [x] Performance within baseline

## Retry Strategy
- [ ] Fix identified issue
- [ ] Add additional test coverage
- [ ] Retry with safer migration path
EOF
```

**Step 5: Commit Rollback**
```bash
git add .
git commit -m "Rollback: Revert RNG migration to pickle (Phase 1.1)

See docs/architecture_review/WP_NOTES/WP5/ROLLBACK_REPORT_PHASE1.md for details."
```

#### Alternative: Partial Rollback (Keep JSON, Revert Migration)

If JSON encoding works but automatic migration fails:

```bash
# Keep new encode_rng_state_json / decode_rng_state_json
# Revert only the auto-migration logic

git revert <commit-hash-auto-migration>

# Manual migration path:
# 1. Load old snapshot (pickle)
# 2. User manually converts via CLI tool
# 3. Save new snapshot (JSON)
```

---

### Phase 1.2: Security CI Rollback

**Risk Level**: MEDIUM (CI changes, not runtime code)

#### Rollback Triggers

| Trigger | Criteria | Action |
|---------|----------|--------|
| **CI blocking legitimate PRs** | False positives >50% | ROLLBACK |
| **CI performance** | CI time >30 min | ROLLBACK |
| **Dependency issues** | bandit/pip-audit install failures | ROLLBACK |

#### Rollback Procedure

**Time to Rollback**: <15 minutes

```bash
# Remove security workflow
git rm .github/workflows/security.yml

# Remove bandit config
git checkout HEAD~1 -- pyproject.toml

# Commit rollback
git commit -m "Rollback: Remove security CI (Phase 1.2)

Security scanning moved to manual process until issues resolved."
```

**Alternative: Downgrade to Warning-Only**

Instead of full rollback, make security checks non-blocking:

```yaml
# .github/workflows/security.yml
jobs:
  bandit:
    continue-on-error: true  # Don't block PR
    steps:
      - run: bandit -r src/townlet || echo "::warning::Bandit found issues"
```

---

## Phase 2: Quality Gates Rollback

### Phase 2.1: Mypy Strict Rollback

**Risk Level**: MEDIUM (type checking, not runtime behavior)

#### Rollback Triggers

| Trigger | Criteria | Action |
|---------|----------|--------|
| **Build breakage** | CI blocks all PRs | IMMEDIATE ROLLBACK |
| **Development velocity** | PRs take >2x longer | ROLLBACK package-by-package |
| **Type: ignore abuse** | >100 new type: ignore comments | ROLLBACK to gradual |

#### Rollback Procedure (Per-Package)

**Time to Rollback**: <30 minutes per package

```bash
# Example: Rollback world package to non-strict

# 1. Update mypy config
cat > mypy-rollback.ini <<'EOF'
[mypy-townlet.world.*]
check_untyped_defs = False  # Downgrade from strict
disallow_untyped_defs = False
EOF

# 2. Merge with main mypy config
cat mypy-rollback.ini >> pyproject.toml

# 3. Verify builds pass
mypy src/townlet/

# 4. Document rollback
echo "world" >> docs/architecture_review/WP5_MYPY_ROLLBACK_PACKAGES.txt

# 5. Commit
git add pyproject.toml docs/architecture_review/WP5_MYPY_ROLLBACK_PACKAGES.txt
git commit -m "Rollback: Downgrade world package from mypy strict

Package requires additional type annotations before strict mode."
```

**Full Rollback** (all packages):

```bash
# Revert to pre-Phase 2 mypy config
git checkout feature/wp5-phase2-quality~1 -- pyproject.toml

# Remove type: ignore comments (optional)
# NOTE: Only if comments added as part of Phase 2
git diff feature/wp5-phase2-quality~1..HEAD -- "*.py" | \
  grep "type: ignore" | \
  # (Manual review and removal if needed)
```

---

### Phase 2.2: Docstring Coverage Rollback

**Risk Level**: LOW (documentation only, no code changes)

#### Rollback Triggers

| Trigger | Criteria | Action |
|---------|----------|--------|
| **CI blocking PRs** | Docstring check fails frequently | Adjust threshold |
| **Developer friction** | Complaints about pedantic checks | Lower target |

#### Rollback Procedure

**Time to Rollback**: <10 minutes

```bash
# Lower docstring coverage threshold
cat >> pyproject.toml <<'EOF'
[tool.interrogate]
fail-under = 50  # Downgrade from 80
EOF

# Or remove CI check entirely
git diff HEAD~5 -- .github/workflows/lint.yml | \
  grep -A5 "interrogate" | \
  # (Remove interrogate step)

git commit -m "Rollback: Lower docstring threshold to 50%"
```

**Alternative: Make Non-Blocking**

```yaml
# .github/workflows/lint.yml
- name: Check docstrings
  continue-on-error: true  # Warning only
  run: interrogate src/townlet/
```

---

## Phase 3: Final Modularization Rollback

### Phase 3.1: Stability Analyzer Extraction Rollback

**Risk Level**: HIGH (architectural change with behavior risk)

#### Rollback Triggers

| Trigger | Criteria | Action |
|---------|----------|--------|
| **Metrics drift** | Characterization tests fail | IMMEDIATE ROLLBACK |
| **Telemetry changes** | Events differ from baseline | IMMEDIATE ROLLBACK |
| **Performance regression** | Tick time >5% slower | ROLLBACK |
| **Test failures** | Any stability test fails | IMMEDIATE ROLLBACK |

#### Rollback Procedure

**Time to Rollback**: <1 hour

**Step 1: Restore Monolithic Monitor**
```bash
# Checkout pre-extraction version
git checkout feature/wp5-phase3-analyzers~1 -- src/townlet/stability/monitor.py

# Remove extracted analyzer directory
git rm -r src/townlet/stability/analyzers/

# Remove analyzer tests
git rm tests/stability/test_*_analyzer.py
```

**Step 2: Update Imports**
```bash
# Find files importing from analyzers
grep -r "from townlet.stability.analyzers" src/townlet/

# Revert imports to monolithic monitor
# (Manual step: update import statements)
```

**Step 3: Verify Rollback**
```bash
# Run characterization tests against baseline
pytest tests/stability/test_monitor_characterization.py \
  --compare-to=tests/fixtures/baselines/monitor_metrics.json

# Run full stability test suite
pytest tests/test_stability_monitor.py -v

# Check telemetry unchanged
python scripts/run_simulation.py configs/examples/poc_hybrid.yaml \
  --ticks 100 --telemetry-path rollback_telemetry.jsonl

diff tests/fixtures/baselines/telemetry_events.jsonl rollback_telemetry.jsonl
```

**Step 4: Document Failure**
```markdown
# docs/architecture_review/WP_NOTES/WP5/ROLLBACK_REPORT_PHASE3.md

## Analyzer Extraction Rollback

**Date**: 2025-10-XX
**Trigger**: Metrics drift detected

### Failed Analyzer
- **Analyzer**: [Which analyzer caused drift?]
- **Metric**: [Which metric changed?]
- **Baseline**: [Expected value]
- **Actual**: [Observed value]
- **Drift**: [Percentage difference]

### Root Cause Analysis
[Why did the extracted analyzer behave differently?]

### Retry Strategy
- [ ] Fix analyzer algorithm
- [ ] Add more granular characterization tests
- [ ] Extract one analyzer at a time (not all 5)
```

**Step 5: Commit Rollback**
```bash
git add .
git commit -m "Rollback: Revert stability analyzer extraction (Phase 3.1)

Metrics drift detected. See ROLLBACK_REPORT_PHASE3.md for details."
```

#### Alternative: Partial Rollback (Keep Some Analyzers)

If only one analyzer is problematic:

```bash
# Example: Rollback only reward variance analyzer
git checkout feature/wp5-phase3-analyzers~1 -- \
  src/townlet/stability/analyzers/reward_variance.py

# Revert monitor.py to use inline implementation for that analyzer
# (Manual code edit)

# Keep other analyzers
# Tests other 4 analyzers independently
```

---

### Phase 3.2: Telemetry Publisher Slimming Rollback

**Risk Level**: MEDIUM (refactor with behavioral risk)

#### Rollback Triggers

| Trigger | Criteria | Action |
|---------|----------|--------|
| **Telemetry failures** | Events not emitted | IMMEDIATE ROLLBACK |
| **Worker crashes** | Thread/async issues | IMMEDIATE ROLLBACK |
| **Performance regression** | Event processing >10% slower | ROLLBACK |

#### Rollback Procedure

**Time to Rollback**: <45 minutes

```bash
# Restore pre-refactor publisher
git checkout feature/wp5-phase3-analyzers~1 -- \
  src/townlet/telemetry/publisher.py

# Remove extracted worker module
git rm src/townlet/telemetry/worker.py

# Verify rollback
pytest tests/test_telemetry_publisher.py -v
pytest tests/test_telemetry_stream_smoke.py -v

# Commit
git commit -m "Rollback: Restore monolithic TelemetryPublisher (Phase 3.2)"
```

---

## Phase 4: Boundary Enforcement Rollback

### Phase 4.1: Import-Linter Rollback

**Risk Level**: LOW (static analysis, not runtime)

#### Rollback Triggers

| Trigger | Criteria | Action |
|---------|----------|--------|
| **Too many violations** | >50 legacy violations | ROLLBACK |
| **False positives** | Legitimate imports blocked | Adjust contracts |
| **CI performance** | Import checking adds >5min to CI | ROLLBACK |

#### Rollback Procedure

**Time to Rollback**: <15 minutes

**Option 1: Remove import-linter entirely**
```bash
# Remove config
git rm .importlinter

# Remove CI integration
git diff HEAD~3 -- .github/workflows/lint.yml | \
  grep -B5 -A10 "import-linter" | \
  # (Remove import-linter step)

git commit -m "Rollback: Remove import-linter (Phase 4.1)

Too many legacy violations. Will address in future work."
```

**Option 2: Make non-blocking (warning only)**
```yaml
# .github/workflows/lint.yml
- name: Check import boundaries
  continue-on-error: true
  run: import-linter --config .importlinter || echo "::warning::Import violations detected"
```

**Option 3: Loosen contracts**
```ini
# .importlinter
[importlinter:contract:layers]
# Add exceptions for legacy violations
ignore_imports =
    townlet.world -> townlet.telemetry  # Legacy event emission
    townlet.config -> townlet.snapshots  # Legacy validation
```

---

## Phase 5: Config & Documentation Polish Rollback

**Risk Level**: VERY LOW (documentation changes)

### Phase 5 Rollback

Phase 5 changes are documentation-only and require minimal rollback:

```bash
# Revert documentation updates
git checkout feature/wp5-phase5-polish~1 -- docs/

# Revert config cross-import fixes (if causing issues)
git checkout feature/wp5-phase5-polish~1 -- src/townlet/config/

git commit -m "Rollback: Revert Phase 5 documentation updates"
```

---

## Emergency Rollback: Full WP5 Revert

**LAST RESORT**: If multiple phases fail or cause critical issues.

### Emergency Procedure

**Time to Rollback**: <2 hours

```bash
# 1. Identify pre-WP5 commit
git log --oneline --grep="WP5" -1

PRE_WP5_COMMIT=$(git rev-parse feature/wp5-phase0-baselines~1)

# 2. Create emergency rollback branch
git checkout -b emergency/rollback-wp5 main

# 3. Revert all WP5 merges
git revert -m 1 <merge-phase5>
git revert -m 1 <merge-phase4>
git revert -m 1 <merge-phase3>
git revert -m 1 <merge-phase2>
git revert -m 1 <merge-phase1>
git revert -m 1 <merge-phase0>

# Or hard reset (loses WP5 work)
# git reset --hard $PRE_WP5_COMMIT

# 4. Verify pre-WP5 tests pass
pytest

# 5. Force push to main (DANGEROUS)
# git push --force origin main

# Or merge rollback branch
git checkout main
git merge emergency/rollback-wp5
git push origin main
```

### Emergency Validation

```bash
# Verify codebase is stable
pytest --maxfail=10  # Stop after 10 failures

# Check baseline metrics
python scripts/benchmark_tick.py --compare-to=baseline_perf.txt

# Verify snapshots load
pytest tests/test_snapshot_manager.py
```

### Emergency Communication

```markdown
# INCIDENT REPORT: WP5 Emergency Rollback

**Date**: 2025-10-XX
**Severity**: CRITICAL
**Status**: RESOLVED (via rollback)

## Issue
[Describe catastrophic failure requiring full WP5 rollback]

## Impact
- [ ] Production simulation broken
- [ ] All tests failing
- [ ] Data loss risk

## Root Cause
[What went wrong?]

## Rollback Actions
- Reverted all WP5 phases
- Restored pre-WP5 commit: ${PRE_WP5_COMMIT}
- Verified all tests passing

## Prevention
- [ ] Add more comprehensive integration tests
- [ ] Smaller, incremental changes
- [ ] Longer soak time between phases

## Retry Plan
[How will WP5 be re-attempted more safely?]
```

---

## Rollback Decision Matrix

| Phase | Risk | Rollback Trigger | Time to Rollback | Validation |
|-------|------|------------------|------------------|------------|
| **0.1-0.6** | LOW | Baseline invalid | <15 min | Re-run baseline capture |
| **1.1** | HIGH | Snapshot incompatibility | <30 min | Snapshot + golden tests |
| **1.2** | MEDIUM | CI blocking PRs | <15 min | CI runs successfully |
| **2.1** | MEDIUM | Build breakage | <30 min | mypy passes |
| **2.2** | LOW | Developer friction | <10 min | Interrogate threshold lowered |
| **3.1** | HIGH | Metrics drift | <1 hour | Characterization tests pass |
| **3.2** | MEDIUM | Telemetry failures | <45 min | Telemetry tests pass |
| **4.1** | LOW | Too many violations | <15 min | Import-linter removed |
| **5.1-5.2** | VERY LOW | N/A | <10 min | Revert docs |

---

## Rollback Best Practices

### Before Rollback

1. **Capture evidence**
   ```bash
   # Save test output
   pytest > rollback_test_output.txt 2>&1

   # Save error logs
   cp *.log rollback_logs/

   # Save metrics
   python scripts/benchmark_tick.py > rollback_perf.txt
   ```

2. **Notify team**
   - Post in #townlet-dev channel
   - Update GitHub issue
   - Document in rollback report

3. **Create rollback branch**
   ```bash
   git checkout -b rollback/phase-X-$(date +%Y%m%d) main
   ```

### During Rollback

1. **Work on rollback branch** (not main)
2. **Commit frequently** (document each revert step)
3. **Test after each revert** (ensure stability restored)
4. **Document everything** (rollback report)

### After Rollback

1. **Verify all tests pass**
   ```bash
   pytest --maxfail=1  # Stop at first failure
   ```

2. **Compare to baseline**
   ```bash
   python scripts/benchmark_tick.py --compare-to=baseline_perf.txt
   diff <(pytest) tests/fixtures/baselines/test_output.txt
   ```

3. **Merge rollback to main**
   ```bash
   git checkout main
   git merge --no-ff rollback/phase-X-$(date +%Y%m%d)
   git push origin main
   ```

4. **Create rollback report** (see templates above)

5. **Plan retry**
   - Analyze root cause
   - Add missing tests
   - Break into smaller changes
   - Set soak time between attempts

---

## Rollback Validation Checklist

After any rollback, verify:

- [ ] All 820+ tests passing
- [ ] No mypy errors
- [ ] Performance within 5% of baseline
- [ ] Snapshots load correctly
- [ ] Telemetry events match baseline
- [ ] No new bandit findings
- [ ] CI pipeline green
- [ ] Documentation consistent with code state

---

## Change Log

| Date | Phase | Action | Outcome |
|------|-------|--------|---------|
| 2025-10-14 | - | Rollback plan created | Ready for WP5 execution |
| | | | |

---

## Sign-off

**Rollback Plan Status**: APPROVED

This rollback plan provides:
- ✅ Clear triggers for each phase
- ✅ Step-by-step procedures
- ✅ Time-to-rollback estimates
- ✅ Validation checklists
- ✅ Emergency procedures

**Confidence Level**: HIGH

All WP5 phases have documented rollback paths with <1 hour recovery time.

**Ready for WP5 Execution**: YES
