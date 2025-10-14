# Work Package 5: Final Hardening & Quality Gates

**Status**: NOT STARTED
**Created**: 2025-10-14
**Depends On**: WP1-4, WP4.1 (all complete)
**Goal**: Complete remaining security, quality, and modularity work to achieve 100% architectural refactoring
**Effort Estimate**: 9-12 days

---

## Executive Summary

WP5 consolidates all remaining architectural work identified in both the Remediation Plan (WP0-6) and Architecture Review 2 (WP#1-8). This work package focuses on:

1. **Security hardening** - Replace pickle-based RNG serialization (⚠️ RCE risk)
2. **Quality gates** - Integrate bandit/pip-audit into CI, drive mypy errors to zero
3. **Final modularization** - Extract stability analyzers, slim telemetry publisher
4. **Boundary enforcement** - Configure import-linter contracts
5. **Documentation polish** - Increase docstring coverage to 80%+, eliminate config cross-imports

**Current State**: Core architecture 98% complete (820 tests passing, 85% coverage)
**Target State**: 100% complete with production-ready security posture and quality gates

---

## Context & Motivation

### What's Already Complete ✅

**Major Refactoring (WP0-4, WP4.1)**:
- ✅ Ports & adapters pattern with factory registry
- ✅ Modular world package (grid.py: 2,535 LOC → 716 LOC, 72% reduction)
- ✅ Modular telemetry pipeline (publisher.py: 2,190 LOC → 1,375 LOC, 37% reduction)
- ✅ Strategy-based policy training (orchestrator.py: 984 LOC → 70 LOC, 93% reduction)
- ✅ DTO boundaries with Pydantic v2 (observations, policy, snapshots, rewards, telemetry)
- ✅ Comprehensive architecture documentation (4 ADRs, WP4.1 diagrams)

**Test Coverage**:
- ✅ 820 tests passing, 1 skipped
- ✅ 85% code coverage
- ✅ Optional dependencies handled gracefully ([ml], [api] extras)

### What Remains 🟡

**From Remediation Plan (WP5-6)**:
- 🟡 Config loader: Some cross-imports remain, docstring coverage ~70-80%
- 🟡 Quality gates: ~474 mypy errors in legacy packages, bandit/pip-audit not in CI
- 🟡 Observability: Optional prometheus/websocket adapters

**From Architecture Review 2 (WP#1, WP#7, WP#8)**:
- ❌ **WP#1**: RNG still uses pickle (⚠️ security risk)
- ❌ **WP#7**: StabilityMonitor not decomposed (449 LOC monolith)
- ❌ **WP#8**: No import boundary enforcement
- 🟡 **WP#3**: TelemetryPublisher still large (1,375 LOC, target <200 LOC coordinator)

---

## Objectives

### Primary Goals

1. **Eliminate security vulnerabilities** - Replace pickle-based RNG serialization
2. **Complete quality gates** - Zero mypy errors, bandit/pip-audit in CI
3. **Finish modularization** - Extract stability analyzers, slim telemetry publisher
4. **Enforce boundaries** - Import-linter contracts in CI
5. **Polish documentation** - 80%+ docstring coverage, clean config imports

### Exit Criteria

- ✅ All security scans pass (bandit zero medium findings, pip-audit clean)
- ✅ Zero mypy errors across entire codebase
- ✅ All components <200 LOC (coordinator pattern)
- ✅ Import-linter contracts pass in CI
- ✅ Docstring coverage ≥80% overall
- ✅ No config cross-imports to world/snapshot
- ✅ All 820+ tests passing
- ✅ ADR published for import boundaries

---

## Work Items

### Phase 0: Risk Reduction (1-2 days) 🛡️ FOUNDATION

**Objective**: De-risk subsequent phases through baseline establishment, impact analysis, and safety nets

This preparatory phase ensures we can execute Phases 1-5 safely with clear rollback paths and monitoring.

---

#### 0.1: Establish Baseline Metrics & Test Harness

**Objective**: Capture current state metrics for comparison after refactoring
**Effort**: 0.5 day

**Baseline Captures**:

1. **Performance Baseline**
   ```bash
   # Capture current tick performance
   python scripts/benchmark_tick.py configs/examples/poc_hybrid.yaml --iterations 100 > baseline_perf.txt

   # Capture observation encoding time
   python scripts/profile_observation_tensor.py configs/examples/poc_hybrid.yaml > baseline_obs.txt
   ```

2. **Snapshot Compatibility Baseline**
   ```bash
   # Create test snapshots with current pickle-based RNG
   pytest tests/test_snapshot_manager.py --save-baseline-snapshots

   # These will be used to verify backward compatibility after RNG migration
   ```

3. **Telemetry Output Baseline**
   ```bash
   # Capture telemetry event stream for stability analyzer refactor
   python scripts/run_simulation.py configs/examples/poc_hybrid.yaml \
     --ticks 100 --telemetry-path baseline_telemetry.jsonl
   ```

4. **Stability Metrics Baseline**
   ```bash
   # Run simulation and capture all stability metrics
   pytest tests/test_stability_monitor.py --capture-metrics > baseline_stability.json
   ```

**Deliverables**:
- `tests/fixtures/baselines/` directory with:
  - `performance.json` — Tick times, observation encoding times
  - `snapshots/` — 3-5 pickle-based snapshots for compatibility testing
  - `telemetry_events.jsonl` — Event stream for analyzer comparison
  - `stability_metrics.json` — Stability analyzer outputs

**Acceptance Criteria**:
- ✅ Baseline files committed to repository
- ✅ Documented in `docs/WP5_BASELINE.md`
- ✅ CI job to regenerate baselines on demand

---

#### 0.2: Create RNG Migration Test Suite

**Objective**: Build comprehensive test suite BEFORE changing RNG implementation
**Effort**: 0.5 day

**Test Coverage**:

1. **Golden Tests** — Deterministic replay verification
   ```python
   # tests/test_rng_golden.py
   def test_rng_deterministic_replay():
       """Verify RNG produces identical sequences after encode/decode."""
       rng = random.Random(42)

       # Generate sequence
       original_sequence = [rng.random() for _ in range(1000)]

       # Encode state
       state = rng.getstate()
       encoded = encode_rng_state(state)

       # Decode and continue
       decoded = decode_rng_state(encoded)
       rng2 = random.Random()
       rng2.setstate(decoded)

       # Should produce identical next values
       continued_sequence = [rng2.random() for _ in range(1000)]

       assert continued_sequence == original_sequence[1000:2000]
   ```

2. **Snapshot Round-Trip Tests**
   ```python
   # tests/test_snapshot_rng_roundtrip.py
   def test_snapshot_rng_preserves_sequences(baseline_snapshot):
       """Verify snapshot save/load preserves RNG sequences."""
       # Load baseline snapshot (pickle-based)
       snapshot = SnapshotManager.load(baseline_snapshot)

       # Run 100 ticks
       loop = SimulationLoop.from_snapshot(snapshot)
       tick_results_before = [loop.step() for _ in range(100)]

       # Save and reload
       new_snapshot_path = loop.save_snapshot()
       loop2 = SimulationLoop.from_snapshot(new_snapshot_path)

       # Next 100 ticks should be identical
       tick_results_after = [loop2.step() for _ in range(100)]

       assert tick_results_before == tick_results_after
   ```

3. **Cross-Format Compatibility Tests**
   ```python
   # tests/test_rng_migration.py
   def test_pickle_to_json_migration():
       """Verify pickle snapshots can be migrated to JSON."""
       # Load old pickle snapshot
       old_snapshot = load_pickle_snapshot("baseline_snapshot_pickle.json")

       # Apply migration
       migrator = RNGMigration()
       new_snapshot = migrator.apply(old_snapshot)

       # Both should produce identical sequences
       loop1 = SimulationLoop.from_snapshot(old_snapshot)
       loop2 = SimulationLoop.from_snapshot(new_snapshot)

       for _ in range(100):
           result1 = loop1.step()
           result2 = loop2.step()
           assert result1 == result2
   ```

**Deliverables**:
- `tests/test_rng_golden.py` — 5+ deterministic replay tests
- `tests/test_snapshot_rng_roundtrip.py` — 3+ snapshot tests
- `tests/test_rng_migration.py` — 5+ migration tests
- All tests passing with CURRENT pickle implementation

**Acceptance Criteria**:
- ✅ 13+ new RNG tests passing with pickle baseline
- ✅ Tests will detect any behavior changes after JSON migration
- ✅ Golden test fixtures committed

---

#### 0.3: Analyzer Behavior Characterization

**Objective**: Document current StabilityMonitor behavior BEFORE extraction
**Effort**: 0.5 day

**Characterization Activities**:

1. **Trace Current Behavior**
   ```python
   # tests/stability/test_monitor_characterization.py
   def test_monitor_output_characterization(snapshot):
       """Document exact metrics produced by current monitor."""
       monitor = StabilityMonitor(config)
       loop = SimulationLoop.from_snapshot(snapshot)

       metrics_log = []
       for _ in range(100):
           loop.step()
           metrics = monitor.get_metrics()
           metrics_log.append(metrics)

       # Save for comparison after refactor
       with open("baseline_monitor_metrics.json", "w") as f:
           json.dump(metrics_log, f)
   ```

2. **Identify Edge Cases**
   ```python
   # Document edge cases that must be preserved
   def test_monitor_edge_cases():
       """Test monitor behavior in corner cases."""
       # Empty world
       # Single agent
       # All agents starving
       # Rapid population churn
       # etc.
   ```

3. **Telemetry Event Characterization**
   ```python
   def test_monitor_telemetry_events(snapshot):
       """Capture all telemetry events emitted by monitor."""
       # Record event types, payloads, frequencies
       # Will verify after extraction that events unchanged
   ```

**Deliverables**:
- `tests/stability/test_monitor_characterization.py` — Behavior documentation tests
- `tests/fixtures/baselines/monitor_metrics.json` — Expected outputs
- `docs/architecture_review/WP5_ANALYZER_BEHAVIOR.md` — Documented edge cases

**Acceptance Criteria**:
- ✅ Current monitor behavior fully characterized
- ✅ Edge cases documented
- ✅ Baseline metrics captured for comparison

---

#### 0.4: Import Dependency Analysis

**Objective**: Map current import dependencies BEFORE adding import-linter
**Effort**: 0.25 day

**Analysis Activities**:

1. **Generate Dependency Graph**
   ```bash
   # Install pydeps
   pip install pydeps

   # Generate full dependency graph
   pydeps src/townlet --max-bacon 2 --cluster \
     -o docs/architecture_review/WP5_dependency_graph.svg
   ```

2. **Identify Existing Violations**
   ```bash
   # Run import-linter in analysis mode (don't fail)
   import-linter --config .importlinter.analysis --no-strict

   # Output: Current violations to be grandfathered
   ```

3. **Document Cross-Package Imports**
   ```bash
   # Find all cross-package imports
   grep -r "from townlet\." src/townlet/config/ | \
     grep -E "world|snapshot|policy|telemetry" > config_violations.txt
   ```

**Deliverables**:
- `docs/architecture_review/WP5_dependency_graph.svg` — Visual import graph
- `docs/architecture_review/WP5_import_violations.txt` — Current violations list
- `.importlinter.analysis` — Analysis-only config

**Acceptance Criteria**:
- ✅ Dependency graph visualized
- ✅ All existing violations documented
- ✅ Baseline established for "no new violations" policy

---

#### 0.5: Security Baseline Scan

**Objective**: Run bandit/pip-audit locally BEFORE CI integration
**Effort**: 0.25 day

**Baseline Scans**:

1. **Bandit Baseline**
   ```bash
   pip install bandit[toml]
   bandit -r src/townlet -f json -o baseline_bandit.json

   # Document current findings
   # - B301: pickle usage (EXPECTED, will fix in Phase 1)
   # - Any others?
   ```

2. **pip-audit Baseline**
   ```bash
   pip install pip-audit
   pip-audit --format json > baseline_pip_audit.json

   # Document current vulnerabilities
   # - Known CVEs in dependencies
   # - Acceptable risk or upgrade needed?
   ```

3. **Create Error Budget**
   ```markdown
   # docs/SECURITY_BASELINE.md

   ## Pre-WP5 Security Status

   ### Bandit Findings
   - B301 (pickle): 2 instances — KNOWN, will fix in Phase 1
   - B404 (subprocess): 1 instance — ACCEPTABLE (simulation script)

   ### pip-audit Findings
   - numpy CVE-2021-41495: ACCEPTABLE (test dependency only)

   ## Error Budget
   - Phase 1 must eliminate B301
   - New findings: BLOCK
   ```

**Deliverables**:
- `baseline_bandit.json` — Current security findings
- `baseline_pip_audit.json` — Current dependency vulnerabilities
- `docs/SECURITY_BASELINE.md` — Documented acceptable risk

**Acceptance Criteria**:
- ✅ Security baseline documented
- ✅ Error budget established
- ✅ Phase 1 targets clear (eliminate B301)

---

#### 0.6: Create Rollback Plan

**Objective**: Document rollback procedures for each risky change
**Effort**: 0.25 day

**Rollback Procedures**:

```markdown
# docs/architecture_review/WP5_ROLLBACK_PLAN.md

## Phase 1: RNG Migration Rollback

**Trigger**: Snapshot compatibility tests fail

**Procedure**:
1. Revert `src/townlet/utils/rng.py` to pickle version
2. Revert `src/townlet/snapshots/state.py` changes
3. Remove migration from `snapshots/migrations.py`
4. Verify baseline tests pass
5. Document failure reason for retry

**Time to Rollback**: <30 minutes

## Phase 3: Analyzer Extraction Rollback

**Trigger**: Metrics drift detected (>1% deviation from baseline)

**Procedure**:
1. Revert `stability/` package to monolithic version
2. Remove `stability/analyzers/` directory
3. Run characterization tests against baseline
4. Document which analyzer caused drift

**Time to Rollback**: <1 hour

## Phase 4: Import-Linter Rollback

**Trigger**: Too many legacy violations (>50)

**Procedure**:
1. Remove `.importlinter` config
2. Remove CI integration
3. Document violations for future fix
4. Continue with other WP5 phases

**Time to Rollback**: <15 minutes
```

**Deliverables**:
- `docs/architecture_review/WP5_ROLLBACK_PLAN.md` — Documented procedures
- Git branch strategy for safe rollback

**Acceptance Criteria**:
- ✅ Rollback documented for each phase
- ✅ Time-to-rollback estimated
- ✅ Team aware of rollback triggers

---

### Phase 0 Summary

**Total Effort**: 1-2 days
**Value**: De-risks 9-13 days of subsequent work

**Deliverables**:
- ✅ Baseline metrics captured
- ✅ Comprehensive RNG test suite (13+ tests)
- ✅ Analyzer behavior characterized
- ✅ Import dependencies mapped
- ✅ Security baseline established
- ✅ Rollback plan documented

**Risk Reduction**:
- 🔴 RNG Migration: HIGH → MEDIUM (golden tests + migration suite)
- 🟡 Analyzer Extraction: MEDIUM → LOW (behavior characterized)
- 🟡 Import-Linter: MEDIUM → LOW (violations documented)
- 🔴 Snapshot Compatibility: HIGH → LOW (baseline snapshots + round-trip tests)

**Acceptance Criteria**:
- ✅ All baseline files committed
- ✅ All Phase 0 tests passing (13+ RNG tests)
- ✅ Documentation complete (5 docs)
- ✅ Team confident to proceed to Phase 1

---

### Phase 1: Security Hardening (2-3 days) ⚠️ HIGH PRIORITY

#### 1.1: Replace Pickle-Based RNG Serialization

**Objective**: Eliminate RCE risk from `pickle.loads()` in snapshot RNG state
**Files**: `src/townlet/utils/rng.py`, `src/townlet/world/core/context.py`
**Effort**: 2-3 days

**Current Implementation**:
```python
# src/townlet/utils/rng.py:13
def encode_rng_state(state: tuple[object, ...]) -> str:
    return base64.b64encode(pickle.dumps(state)).decode("ascii")

# src/townlet/utils/rng.py:19
def decode_rng_state(payload: str) -> tuple[object, ...]:
    state = pickle.loads(base64.b64decode(payload.encode("ascii")))
    return tuple(state)
```

**Security Risk**:
- Medium severity - RCE if snapshot payloads are untrusted
- `pickle.loads()` can execute arbitrary code
- No integrity checks or signature verification

**Target Implementation**:
```python
import json
import hmac
import hashlib
from typing import Any

def encode_rng_state(state: tuple[object, ...], secret_key: bytes | None = None) -> str:
    """Encode RNG state as signed JSON.

    Args:
        state: Python random state tuple (version, internalstate, gauss_next)
        secret_key: Optional HMAC key for integrity verification

    Returns:
        Base64-encoded JSON with HMAC signature

    Format:
        {
            "version": 3,
            "state": [...],  # 625-element MT19937 state array
            "gauss_next": null | float,
            "signature": "hex_hmac_sha256"  # if secret_key provided
        }
    """
    # Convert tuple to JSON-serializable dict
    version, internalstate, gauss_next = state
    state_array = list(internalstate)  # (624,) array + position

    payload = {
        "version": version,
        "state": state_array,
        "gauss_next": gauss_next,
    }

    # Add HMAC signature if key provided
    if secret_key:
        message = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
        payload["signature"] = signature

    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")


def decode_rng_state(payload: str, secret_key: bytes | None = None) -> tuple[Any, ...]:
    """Decode signed JSON RNG state.

    Args:
        payload: Base64-encoded JSON from encode_rng_state
        secret_key: Optional HMAC key for integrity verification

    Returns:
        Python random state tuple

    Raises:
        ValueError: If signature verification fails or format invalid
        TypeError: If decoded state is not valid structure
    """
    try:
        data = json.loads(base64.b64decode(payload.encode("ascii")).decode("utf-8"))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid RNG state encoding: {e}") from e

    # Verify signature if key provided
    if secret_key:
        if "signature" not in data:
            raise ValueError("RNG state missing signature")

        signature = data.pop("signature")
        message = json.dumps(data, sort_keys=True).encode("utf-8")
        expected = hmac.new(secret_key, message, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, expected):
            raise ValueError("RNG state signature verification failed")

    # Reconstruct tuple structure
    version = data["version"]
    state_array = tuple(data["state"])
    gauss_next = data["gauss_next"]

    if version != 3:
        raise ValueError(f"Unsupported RNG version: {version}")

    return (version, state_array, gauss_next)
```

**Migration Strategy**:
1. Add new JSON-based encoder/decoder alongside pickle versions
2. Update `SnapshotManager` to use JSON for new snapshots
3. Keep pickle decoder for legacy snapshot compatibility
4. Add migration in `snapshots/migrations.py` to convert old snapshots
5. Deprecation warning when loading pickle-based snapshots
6. Remove pickle code in v1.1 (after migration period)

**Testing**:
- Unit tests for encode/decode round-trip
- Signature verification tests (valid/invalid/missing)
- Corruption detection tests (modified payload)
- Migration tests (pickle → JSON)
- Bandit regression test (zero medium findings)

**Acceptance Criteria**:
- ✅ New snapshots use JSON encoding
- ✅ Legacy pickle snapshots load with deprecation warning
- ✅ Signature verification optional but recommended
- ✅ `bandit src/townlet/utils/rng.py` reports zero medium findings
- ✅ All snapshot tests passing
- ✅ Documentation updated with security guidance

---

#### 1.2: Add Security Scanning to CI

**Objective**: Integrate bandit and pip-audit into CI pipeline
**Files**: `.github/workflows/*.yml`, `pyproject.toml`
**Effort**: 1 day

**Current State**:
- ❌ No bandit in CI (security linting)
- ❌ No pip-audit in CI (dependency vulnerability scanning)
- ✅ Ruff and mypy exist but don't block on all packages

**Target CI Stages**:
```yaml
# .github/workflows/security.yml
name: Security Scans

on: [push, pull_request]

jobs:
  bandit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install bandit[toml]
      - run: bandit -r src/townlet -c pyproject.toml

  pip-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pip-audit
      - run: pip-audit --require-hashes --desc
```

**Bandit Configuration** (`pyproject.toml`):
```toml
[tool.bandit]
exclude_dirs = ["tests/", "scripts/", "docs/"]
skips = ["B101"]  # assert_used - acceptable in simulation code

# Error budget: Start with baseline, drive to zero
[tool.bandit.assert_used]
exclude = ["**/test_*.py", "tests/**"]
```

**Error Budget Policy**:
- **Bandit**: Zero medium/high findings allowed (low findings case-by-case)
- **pip-audit**: Zero critical/high vulnerabilities (medium with documented exceptions)
- **Exceptions**: Document in `docs/SECURITY.md` with rationale and mitigation

**Acceptance Criteria**:
- ✅ Bandit runs on every PR
- ✅ pip-audit runs on every PR
- ✅ CI blocks on security findings above threshold
- ✅ Error budget documented
- ✅ Exception process in SECURITY.md

---

### Phase 2: Quality Gates (2-3 days)

#### 2.1: Drive Mypy Errors to Zero

**Objective**: Eliminate all ~474 mypy errors in legacy packages
**Files**: All packages not yet strict
**Effort**: 2 days

**Current State**:
- ✅ `core`, `ports`, `dto` — mypy strict passing
- 🟡 `world`, `policy`, `telemetry`, `rewards`, etc. — ~474 errors

**Strategy**:
1. **Package-by-package approach** (not big-bang)
2. **Prioritize by dependency order** (dto → ports → core → adapters → domain)
3. **Use gradual typing** - Add `# type: ignore` with issue tracker comments where needed
4. **Target strict mode** for all packages eventually

**Phases**:
- **Week 1**: `rewards`, `observations`, `snapshots` (core domain)
- **Week 2**: `world`, `policy` (complex domains)
- **Week 3**: `telemetry`, `stability` (infrastructure)

**Common Mypy Fixes**:
```python
# Before
def compute(world, terminated):  # Missing type hints
    results = {}  # Implicit Any

# After
def compute(
    world: WorldState,
    terminated: dict[str, bool],
) -> dict[str, RewardBreakdown]:
    results: dict[str, RewardBreakdown] = {}
```

**Acceptance Criteria**:
- ✅ Zero mypy errors in all packages
- ✅ `mypy --strict src/townlet` passes
- ✅ CI enforces mypy strict on all packages
- ✅ No new type: ignore comments without issue links

---

#### 2.2: Increase Docstring Coverage

**Objective**: Achieve 80%+ docstring coverage overall
**Files**: All modules
**Effort**: 1 day (ongoing)

**Current State**:
- 🟡 Overall coverage ~40-50%
- 🟡 Config package ~70-80%
- ✅ DTO package ~95%

**Targets by Package**:
| Package | Current | Target |
|---------|---------|--------|
| `dto` | 95% | 95% |
| `ports` | 90% | 95% |
| `core` | 70% | 85% |
| `config` | 75% | 85% |
| `world` | 50% | 80% |
| `policy` | 45% | 80% |
| `telemetry` | 40% | 80% |
| **Overall** | **~50%** | **≥80%** |

**Prioritize**:
1. Public APIs (ports, adapters, factories)
2. Complex algorithms (reward engine, observation encoders)
3. Configuration models (config package)

**Style Guide**: `docs/guides/DOCSTRING_GUIDE.md`

**Acceptance Criteria**:
- ✅ Overall docstring coverage ≥80%
- ✅ All public APIs documented
- ✅ CI checks docstring coverage with `interrogate`
- ✅ Threshold ratchets: New code must maintain/improve coverage

---

### Phase 3: Final Modularization (3-4 days)

#### 3.1: Extract Stability Analyzers

**Objective**: Decompose `StabilityMonitor` into 5 analyzer classes
**Files**: `src/townlet/stability/monitor.py` → `stability/analyzers/*.py`
**Effort**: 3 days

**Current State**:
- ❌ `monitor.py` is 449 LOC monolith
- ❌ All analysis inline in `track()` method
- ❌ No separate analyzer tests

**Target Architecture**:
```
stability/
├── monitor.py              # <100 LOC - coordinator only
├── analyzers/
│   ├── __init__.py
│   ├── base.py            # Analyzer protocol
│   ├── fairness.py        # Fairness analyzer
│   ├── starvation.py      # Starvation detector
│   ├── rivalry.py         # Rivalry tracker
│   ├── reward_variance.py # Reward variance analyzer
│   └── option_thrash.py   # Option thrashing detector
└── promotion.py           # Promotion manager (already exists)
```

**Analyzer Protocol**:
```python
from typing import Protocol
from townlet.world.grid import WorldState
from townlet.dto.telemetry import TelemetryEventDTO

class StabilityAnalyzer(Protocol):
    """Analyzer that computes a stability metric from world state."""

    def analyze(self, world: WorldState, tick: int) -> float:
        """Compute metric value for current tick.

        Args:
            world: Current world state
            tick: Current simulation tick

        Returns:
            Metric value (0.0-1.0, higher is more stable)
        """
        ...

    def emit_telemetry(self, tick: int) -> TelemetryEventDTO | None:
        """Emit telemetry event if metric crosses threshold.

        Args:
            tick: Current simulation tick

        Returns:
            TelemetryEventDTO if event should be emitted, else None
        """
        ...

    def reset(self) -> None:
        """Reset analyzer state (e.g., for new simulation)."""
        ...
```

**Refactored Monitor**:
```python
class StabilityMonitor:
    """Coordinates stability analyzers and aggregates metrics."""

    def __init__(self, config: StabilityConfig):
        self.analyzers: list[StabilityAnalyzer] = [
            FairnessAnalyzer(config.fairness),
            StarvationDetector(config.starvation),
            RivalryTracker(config.rivalry),
            RewardVarianceAnalyzer(config.reward_variance),
            OptionThrashDetector(config.option_thrash),
        ]
        self._latest_metrics: dict[str, float] = {}

    def track(self, world: WorldState, tick: int) -> None:
        """Update all analyzers with current world state."""
        for analyzer in self.analyzers:
            metric_value = analyzer.analyze(world, tick)
            metric_name = analyzer.__class__.__name__.lower()
            self._latest_metrics[metric_name] = metric_value

    def get_metrics(self) -> dict[str, float]:
        """Return latest metric values from all analyzers."""
        return dict(self._latest_metrics)

    def emit_telemetry(self, tick: int) -> list[TelemetryEventDTO]:
        """Collect telemetry events from all analyzers."""
        events = []
        for analyzer in self.analyzers:
            event = analyzer.emit_telemetry(tick)
            if event:
                events.append(event)
        return events
```

**Testing**:
- Unit tests for each analyzer (mocked world state)
- Integration tests for monitor coordination
- Telemetry emission tests
- Rolling window tests (24h metrics)

**Acceptance Criteria**:
- ✅ 5 analyzer classes extracted (<200 LOC each)
- ✅ `monitor.py` reduced to <100 LOC coordinator
- ✅ Each analyzer has ≥5 unit tests
- ✅ Integration tests pass
- ✅ Telemetry events unchanged (backward compatible)

---

#### 3.2: Slim Telemetry Publisher

**Objective**: Further decompose `publisher.py` to <200 LOC coordinator
**Files**: `src/townlet/telemetry/publisher.py`
**Effort**: 1 day

**Current State**:
- 🟡 `publisher.py` is 1,375 LOC (down from 2,190, but still large)
- ✅ Aggregator, Transform, Transport exist as separate modules
- 🟡 Publisher still contains worker management, queue handling, lifecycle

**Target Architecture**:
```python
# publisher.py <200 LOC - coordinator only
class TelemetryPublisher:
    """Lightweight coordinator for telemetry pipeline."""

    def __init__(self, config: TelemetryConfig):
        self.aggregator = TelemetryAggregator(config.aggregation)
        self.transform = TransformPipeline(config.transform)
        self.transport = TransportCoordinator(config.transport)
        self.worker = TelemetryWorker(config.worker)  # NEW
        self.event_dispatcher = EventDispatcher()

    def start_worker(self) -> None:
        """Delegate to worker manager."""
        self.worker.start()

    def stop_worker(self) -> None:
        """Delegate to worker manager."""
        self.worker.stop()

    # ... delegate other methods to components
```

**Extract to New Module** (`telemetry/worker.py`):
- Worker lifecycle management
- Queue handling
- Backpressure logic
- Thread/async coordination

**Acceptance Criteria**:
- ✅ `publisher.py` reduced to <200 LOC
- ✅ `worker.py` created with worker management (<300 LOC)
- ✅ All telemetry tests passing
- ✅ No behavioral changes

---

### Phase 4: Boundary Enforcement (1-2 days)

#### 4.1: Configure Import-Linter

**Objective**: Enforce architectural boundaries with import-linter
**Files**: `.importlinter`, `pyproject.toml`, CI config
**Effort**: 1-2 days

**Import Contracts**:
```ini
# .importlinter
[importlinter]
root_package = townlet

[importlinter:contract:layers]
name = Layered architecture
type = layers
layers =
    dto
    ports
    core
    adapters
    (world | policy | telemetry | rewards)

[importlinter:contract:dto-independence]
name = DTOs are independent
type = independence
modules =
    townlet.dto.observations
    townlet.dto.policy
    townlet.dto.rewards
    townlet.dto.telemetry
    townlet.dto.world

[importlinter:contract:no-world-to-policy]
name = World does not import policy
type = forbidden
source_modules =
    townlet.world
forbidden_modules =
    townlet.policy

[importlinter:contract:no-policy-to-telemetry]
name = Policy does not import telemetry
type = forbidden
source_modules =
    townlet.policy
forbidden_modules =
    townlet.telemetry
```

**Exception Process** (`docs/architecture_review/IMPORT_EXCEPTIONS.md`):
```markdown
# Import Boundary Exceptions

## Approved Exceptions

| Source | Target | Rationale | Approved By | Date |
|--------|--------|-----------|-------------|------|
| `world.grid` | `telemetry.events` | Grid emits domain events | ADR-001 | 2025-10-14 |

## Exception Request Process

1. Open GitHub issue with `import-exception` label
2. Justify why exception is necessary
3. Propose alternative if possible
4. ADR author review required
5. Document in this file when approved
```

**CI Integration**:
```yaml
# .github/workflows/lint.yml
- name: Check import boundaries
  run: |
    pip install import-linter
    import-linter --config .importlinter
```

**Acceptance Criteria**:
- ✅ Import-linter configured with 4+ contracts
- ✅ All contracts pass in CI
- ✅ Exception process documented
- ✅ CI blocks on new boundary violations
- ✅ ADR published (ADR-005: Import Boundaries)

---

### Phase 5: Config & Documentation Polish (1 day)

#### 5.1: Eliminate Config Cross-Imports

**Objective**: Remove remaining config → world/snapshot imports
**Files**: `src/townlet/config/loader.py`, config modules
**Effort**: 0.5 day

**Current Issues**:
- 🟡 Some config validation imports world types
- 🟡 Loader has runtime dependency on snapshot

**Target**: Config should only import from `dto`, `typing`, `pydantic`

**Acceptance Criteria**:
- ✅ No config imports from `world`, `snapshots`, `policy`, `telemetry`
- ✅ Config validation uses DTOs only
- ✅ Import-linter contract enforces this

---

#### 5.2: Documentation Updates

**Objective**: Update all docs to reflect 100% completion
**Files**: Various docs
**Effort**: 0.5 day

**Updates Required**:
- ✅ `WP_COMPLIANCE_ASSESSMENT.md` — Mark WP5 complete
- ✅ `CLAUDE.md` — Update progress to 100%
- ✅ Create `docs/SECURITY.md` — Security posture documentation
- ✅ Create `ADR-005 - Import Boundaries.md`
- ✅ Update `ARCHITECTURE_REVIEW_2_WORK_PACKAGES.md` — Mark all complete

**Acceptance Criteria**:
- ✅ All docs reflect 100% completion
- ✅ Security guidance documented
- ✅ Import boundary ADR published

---

## Dependencies

### Prerequisites (Must Be Complete)

- ✅ WP1: Core Interfaces (100%)
- ✅ WP2: World Modularization (100%)
- ✅ WP3: Telemetry Pipeline (90%)
- ✅ WP4: Policy Backends (100%)
- ✅ WP4.1: Gap Closure (100%)

### External Dependencies

- Python 3.11+
- Pydantic v2
- pytest, mypy, ruff (already installed)
- **New**: bandit, pip-audit, import-linter, interrogate

---

## Testing Strategy

### Test Additions

**Security Tests**:
- `tests/test_rng_security.py` — RNG encoding/decoding, signature verification
- `tests/test_snapshot_migration_pickle.py` — Pickle → JSON migration

**Analyzer Tests**:
- `tests/stability/test_fairness_analyzer.py`
- `tests/stability/test_starvation_detector.py`
- `tests/stability/test_rivalry_tracker.py`
- `tests/stability/test_reward_variance_analyzer.py`
- `tests/stability/test_option_thrash_detector.py`
- `tests/stability/test_monitor_coordination.py`

**Boundary Tests**:
- `tests/test_import_boundaries.py` — Verify import-linter contracts

### Regression Testing

- ✅ All 820+ existing tests must pass
- ✅ No performance regression (tick time within 5%)
- ✅ Snapshot compatibility (old snapshots load)

---

## Risk Assessment

### High Risk

1. **RNG Migration Breaking Snapshots** 🔴
   - **Mitigation**: Keep pickle decoder for legacy compatibility
   - **Rollback**: Revert to pickle if migration fails

2. **Mypy Strict Breaking Builds** 🟡
   - **Mitigation**: Package-by-package rollout with type: ignore escape hatch
   - **Rollback**: Revert specific package to non-strict

### Medium Risk

3. **Stability Analyzer Extraction Changing Metrics** 🟡
   - **Mitigation**: Extensive integration tests, compare outputs before/after
   - **Rollback**: Revert to monolithic monitor if metrics drift

4. **Import-Linter Finding Legacy Violations** 🟡
   - **Mitigation**: Start with current state as baseline, prevent new violations
   - **Rollback**: Remove contracts if too many legacy exceptions needed

### Low Risk

5. **Docstring Coverage Targets Too Aggressive** 🟢
   - **Mitigation**: Adjust targets based on actual effort
   - **Rollback**: Lower thresholds if necessary

---

## Deliverables

### Code

1. `src/townlet/utils/rng.py` — JSON-based RNG encoding (pickle deprecated)
2. `src/townlet/stability/analyzers/*.py` — 5 analyzer classes
3. `src/townlet/telemetry/worker.py` — Worker lifecycle manager
4. `.importlinter` — Import boundary contracts
5. `.github/workflows/security.yml` — Bandit + pip-audit CI

### Documentation

6. `docs/SECURITY.md` — Security posture and guidance
7. `docs/architecture_review/ADR/ADR-005 - Import Boundaries.md`
8. `docs/architecture_review/IMPORT_EXCEPTIONS.md` — Exception registry
9. Updated `WP_COMPLIANCE_ASSESSMENT.md` — 100% completion
10. Updated `CLAUDE.md` — 100% progress

### Tests

11. `tests/test_rng_security.py` — RNG security tests
12. `tests/stability/test_*_analyzer.py` — 5 analyzer test files
13. `tests/test_import_boundaries.py` — Boundary verification

---

## Timeline Estimate

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| **Phase 0: Risk Reduction** | 1-2 days | None (MUST be first) |
| **Phase 1: Security** | 2-3 days | Phase 0 complete (baselines + test suite) |
| **Phase 2: Quality** | 2-3 days | Phase 0 complete (parallel with Phase 1) |
| **Phase 3: Modularization** | 3-4 days | Phase 1 complete (RNG migration) |
| **Phase 4: Boundaries** | 1-2 days | Phase 3 complete (all modules stable) |
| **Phase 5: Polish** | 1 day | Phase 4 complete |
| **TOTAL** | **10-15 days** | Sequential with some parallelism |

**Optimistic**: 10 days (Phase 0 + parallel work)
**Realistic**: 12 days (Phase 0 + serial execution)
**Pessimistic**: 15 days (Phase 0 + issues/rework)

**Phase 0 Investment ROI**:
- 1-2 days upfront
- Saves 2-3 days in rework/debugging
- Reduces rollback risk by 60-70%
- Net benefit: 0-1 days faster + higher confidence

---

## Success Metrics

### Quantitative

- ✅ Zero pickle usage in RNG code
- ✅ Zero bandit medium/high findings
- ✅ Zero pip-audit critical/high vulnerabilities
- ✅ Zero mypy errors (100% strict passing)
- ✅ ≥80% docstring coverage overall
- ✅ All components <200 LOC (except PPO strategy at 360 LOC)
- ✅ Import-linter 100% passing
- ✅ 820+ tests passing
- ✅ Code coverage ≥85%

### Qualitative

- ✅ Production-ready security posture
- ✅ Maintainable codebase (small modules, well-tested)
- ✅ Documented architecture (ADRs, diagrams)
- ✅ Enforced boundaries (import-linter)
- ✅ Comprehensive documentation (80%+ docstrings)

---

## Conclusion

WP5 represents the **final 12-15%** of architectural refactoring work, consolidating all remaining tasks from both the Remediation Plan (WP0-6) and Architecture Review 2 (WP#1-8). Upon completion:

- **100% architectural refactoring** complete
- **Production-ready security** posture (no pickle, signed RNG, security scanning)
- **Quality gates enforced** (mypy strict, bandit, pip-audit)
- **Modular architecture** (all components <200 LOC)
- **Documented boundaries** (import-linter, ADR-005)
- **Comprehensive docs** (80%+ docstrings, security guide)

This work package enables a **v1.0 release** with confidence in the codebase's security, maintainability, and architectural integrity.

---

## References

- `docs/architecture_review/WP_TASKINGS/WP_COMPLIANCE_ASSESSMENT.md` — Current status
- `docs/architecture_review/ARCHITECTURE_REVIEW_2_REMEDIATION_PLAN.md` — Remediation WP0-6
- `docs/architecture_review/ARCHITECTURE_REVIEW_2_WORK_PACKAGES.md` — Review 2 WP#1-8
- `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md`
- `docs/architecture_review/ADR/ADR-002 - World Modularisation.md`
- `docs/architecture_review/ADR/ADR-003 - DTO Boundary.md`
- `docs/architecture_review/ADR/ADR-004 - Policy Training Strategies.md`
