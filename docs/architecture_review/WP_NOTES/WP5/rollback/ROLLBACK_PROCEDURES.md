# WP5 Rollback Procedures

**Purpose**: Quick reference for rolling back WP5 phases if issues occur
**Last Updated**: 2025-10-14

---

## General Rollback Strategy

### Git Branch Strategy

```bash
# Work on feature branches off main
main
├── wp5-phase0-risk-reduction
├── wp5-phase1-rng-security
├── wp5-phase2-quality-gates
├── wp5-phase3-modularization
├── wp5-phase4-boundaries
└── wp5-phase5-polish

# Each phase branch contains:
# - Baseline tag at branch creation
# - Incremental commits per activity
# - Final tag when phase complete
```

### Rollback Principles

1. **Fast Rollback** - Any phase should rollback in <1 hour
2. **Test-Driven** - Rollback when tests fail or metrics drift
3. **Documented** - Record why rollback occurred for retry
4. **Safe** - Baseline tests must pass after rollback

---

## Phase 0: Risk Reduction Rollback

**Trigger**: N/A - Phase 0 establishes baselines only
**Risk Level**: 🟢 NONE

**Notes**:
- Phase 0 creates artifacts, doesn't modify code
- If baselines are incorrect, regenerate them
- No rollback needed

---

## Phase 1: Security Hardening Rollback

### 1.1: RNG Migration Rollback

**Trigger**: Snapshot compatibility tests fail OR deterministic replay broken
**Risk Level**: 🔴 HIGH
**Estimated Rollback Time**: 30 minutes

**Symptoms**:
- `test_snapshot_rng_roundtrip.py` failing
- `test_rng_golden.py` detecting sequence changes
- Snapshots can't be loaded
- Simulation produces different results after reload

**Rollback Procedure**:

```bash
# 1. Create rollback checkpoint
git tag wp5-phase1-rollback-$(date +%Y%m%d-%H%M%S)

# 2. Revert RNG implementation
git checkout main -- src/townlet/utils/rng.py
git checkout main -- src/townlet/world/core/context.py

# 3. Revert snapshot changes
git checkout main -- src/townlet/snapshots/state.py
git checkout main -- src/townlet/snapshots/migrations.py

# 4. Remove new tests (keep for future retry)
git stash push tests/test_rng_security.py tests/test_snapshot_migration_pickle.py

# 5. Verify baseline tests pass
pytest tests/test_rng_golden.py tests/test_snapshot_rng_roundtrip.py

# 6. Commit rollback
git commit -m "Rollback Phase 1.1: RNG migration - snapshot compatibility issues"

# 7. Document failure reason
echo "Rollback reason: [DESCRIBE WHAT BROKE]" >> docs/architecture_review/WP_NOTES/WP5/phase1/ROLLBACK_LOG.md
```

**Post-Rollback**:
- Analyze test failures to understand root cause
- Review RNG state structure (MT19937 internals)
- Consider alternative JSON schema
- Retry with fixes

**Verification**:
- [ ] All baseline tests passing
- [ ] Snapshots load correctly
- [ ] Simulation deterministic
- [ ] No regression in other tests

---

### 1.2: CI Security Integration Rollback

**Trigger**: CI blocking legitimate changes OR too many false positives
**Risk Level**: 🟡 MEDIUM
**Estimated Rollback Time**: 15 minutes

**Symptoms**:
- CI failing on every PR
- Bandit flagging acceptable code
- pip-audit blocking safe dependencies

**Rollback Procedure**:

```bash
# 1. Remove CI configuration
git checkout main -- .github/workflows/security.yml

# 2. Remove bandit config
git checkout main -- pyproject.toml  # Only [tool.bandit] section

# 3. Commit rollback
git commit -m "Rollback Phase 1.2: CI security - too many false positives"

# 4. Document for tuning
echo "Need to adjust error budget and exceptions" >> docs/architecture_review/WP_NOTES/WP5/phase1/ROLLBACK_LOG.md
```

**Post-Rollback**:
- Tune bandit configuration (add skips)
- Adjust pip-audit thresholds
- Document exceptions with rationale
- Retry with refined config

---

## Phase 2: Quality Gates Rollback

### 2.1: Mypy Strict Rollback

**Trigger**: Mypy strict blocks valid code OR requires extensive refactoring
**Risk Level**: 🟡 MEDIUM
**Estimated Rollback Time**: 30 minutes per package

**Symptoms**:
- Mypy strict revealing deep architectural issues
- Too many `type: ignore` comments needed
- Blocking development velocity

**Rollback Procedure**:

```bash
# Rollback specific package (example: world)
# 1. Revert mypy.ini changes for package
git diff main mypy.ini  # Review changes
git checkout main -- mypy.ini

# 2. Revert type annotation changes
git checkout main -- src/townlet/world/

# 3. Keep useful type hints (manual review)
# - Review git diff
# - Cherry-pick obvious improvements
# - Discard invasive changes

# 4. Commit rollback
git commit -m "Rollback mypy strict for world package - needs more gradual approach"
```

**Post-Rollback**:
- Use gradual typing (fewer type: ignore)
- Start with easier packages first
- Document patterns for other packages
- Retry with incremental approach

---

## Phase 3: Final Modularization Rollback

### 3.1: Stability Analyzer Extraction Rollback

**Trigger**: Metrics drift >1% from baseline OR telemetry events changed
**Risk Level**: 🟡 MEDIUM
**Estimated Rollback Time**: 1 hour

**Symptoms**:
- `test_monitor_characterization.py` failing
- Stability metrics don't match baseline
- Telemetry events missing or different
- Promotion logic behaving differently

**Rollback Procedure**:

```bash
# 1. Create rollback checkpoint
git tag wp5-phase3-analyzer-rollback-$(date +%Y%m%d-%H%M%S)

# 2. Revert to monolithic monitor
git checkout main -- src/townlet/stability/monitor.py

# 3. Remove analyzer directory
rm -rf src/townlet/stability/analyzers/
git add src/townlet/stability/

# 4. Revert test changes
git checkout main -- tests/stability/

# 5. Run characterization tests against baseline
pytest tests/stability/test_monitor_characterization.py --compare-baseline

# 6. Commit rollback
git commit -m "Rollback Phase 3.1: Analyzer extraction - metrics drift detected"

# 7. Document which analyzer caused drift
echo "Issue: [WHICH ANALYZER] producing [METRIC] different by [%]" >> docs/architecture_review/WP_NOTES/WP5/phase3/ROLLBACK_LOG.md
```

**Post-Rollback**:
- Review metric calculations in extracted analyzers
- Compare line-by-line with monolithic version
- Fix calculation bugs
- Retry with corrected implementation

**Verification**:
- [ ] Characterization tests pass
- [ ] Metrics match baseline exactly
- [ ] Telemetry events identical
- [ ] Promotion logic unchanged

---

### 3.2: Telemetry Publisher Slimming Rollback

**Trigger**: Publisher functionality broken OR tests failing
**Risk Level**: 🟢 LOW
**Estimated Rollback Time**: 30 minutes

**Symptoms**:
- Telemetry events not emitted
- Worker lifecycle issues
- Queue backpressure not working

**Rollback Procedure**:

```bash
# 1. Revert publisher changes
git checkout main -- src/townlet/telemetry/publisher.py

# 2. Remove new worker module
rm -f src/townlet/telemetry/worker.py
git add src/townlet/telemetry/worker.py

# 3. Verify telemetry tests
pytest tests/ -k telemetry

# 4. Commit rollback
git commit -m "Rollback Phase 3.2: Publisher slimming - functionality broken"
```

---

## Phase 4: Boundary Enforcement Rollback

### 4.1: Import-Linter Rollback

**Trigger**: Too many legacy violations (>50) OR contracts too restrictive
**Risk Level**: 🟢 LOW
**Estimated Rollback Time**: 15 minutes

**Symptoms**:
- Import-linter finding 50+ violations
- Contracts blocking valid cross-package imports
- Requires extensive refactoring to fix

**Rollback Procedure**:

```bash
# 1. Remove import-linter config
rm -f .importlinter
git add .importlinter

# 2. Remove CI integration
git checkout main -- .github/workflows/lint.yml

# 3. Save violations list for future
mv docs/architecture_review/WP5_import_violations.txt \
   docs/architecture_review/WP5_import_violations_DEFERRED.txt

# 4. Commit rollback
git commit -m "Rollback Phase 4.1: Import-linter - too many legacy violations"

# 5. Document for gradual adoption
echo "Need to fix violations incrementally before enforcement" >> docs/architecture_review/WP_NOTES/WP5/phase4/ROLLBACK_LOG.md
```

**Post-Rollback**:
- Fix violations gradually (not all at once)
- Implement "no new violations" policy first
- Add contracts incrementally
- Retry when violations reduced

---

## Phase 5: Config & Docs Polish Rollback

**Trigger**: Config changes breaking tests OR imports broken
**Risk Level**: 🟢 LOW
**Estimated Rollback Time**: 15 minutes

**Symptoms**:
- Config validation failing
- Import errors from config changes
- Tests can't load config

**Rollback Procedure**:

```bash
# 1. Revert config changes
git checkout main -- src/townlet/config/

# 2. Verify config tests
pytest tests/test_config*.py

# 3. Commit rollback
git commit -m "Rollback Phase 5: Config cleanup - import issues"
```

---

## Rollback Decision Matrix

| Phase | Risk Level | Rollback Time | Complexity | Retry Strategy |
|-------|------------|---------------|------------|----------------|
| **Phase 0** | 🟢 NONE | N/A | Simple | Regenerate baselines |
| **Phase 1.1** | 🔴 HIGH | 30 min | Complex | Fix RNG schema, retry |
| **Phase 1.2** | 🟡 MEDIUM | 15 min | Simple | Tune error budget |
| **Phase 2.1** | 🟡 MEDIUM | 30 min/pkg | Medium | Gradual typing |
| **Phase 3.1** | 🟡 MEDIUM | 1 hour | Complex | Fix metrics, retry |
| **Phase 3.2** | 🟢 LOW | 30 min | Simple | Fix functionality |
| **Phase 4.1** | 🟢 LOW | 15 min | Simple | Fix violations first |
| **Phase 5** | 🟢 LOW | 15 min | Simple | Incremental changes |

---

## Rollback Checklist

When executing rollback:

- [ ] Tag current state before rollback
- [ ] Revert specific files (not entire branch)
- [ ] Run relevant tests to verify rollback
- [ ] Document rollback reason in ROLLBACK_LOG.md
- [ ] Commit rollback with descriptive message
- [ ] Notify team of rollback
- [ ] Schedule post-mortem to understand failure
- [ ] Plan retry with fixes

---

## Rollback Log

Track all rollbacks here:

| Date | Phase | Reason | Resolution | Time Lost |
|------|-------|--------|------------|-----------|
| - | - | - | - | - |

*No rollbacks yet (Phase 0 not started)*

---

## Lessons Learned

After each rollback, document lessons:

### What Went Wrong
- TBD

### What We'll Do Differently
- TBD

### Preventative Measures
- TBD

---

## Emergency Rollback

**If something breaks production or main branch**:

```bash
# Nuclear option: Revert entire WP5
git checkout main
git branch -D wp5-phase[X]
git tag wp5-emergency-rollback-$(date +%Y%m%d-%H%M%S)

# Verify everything works
pytest
python scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 10

# Notify team immediately
```

**Use only if**:
- Multiple phases have cascading failures
- Critical bug affecting main branch
- No time for careful selective rollback

---

## Contact

For rollback assistance:
- Review this document first
- Check phase-specific ROLLBACK_LOG.md
- Escalate if rollback doesn't resolve issue
