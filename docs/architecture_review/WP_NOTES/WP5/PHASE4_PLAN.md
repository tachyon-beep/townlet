# WP5 Phase 4: Boundary Enforcement - EXECUTION PLAN

**Status**: READY TO START
**Created**: 2025-10-14
**Work Package**: WP5 (Final Hardening and Quality Gates)
**Phase**: Phase 4 (Boundary Enforcement)
**Dependencies**: Phase 2 (mypy complete), Phase 3 (modularization complete)
**Estimated Duration**: 1-2 days

---

## Executive Summary

Phase 4 introduces **import boundary enforcement** using import-linter to prevent architectural regressions. This phase establishes formal architectural contracts that will be enforced in CI, ensuring the modular architecture achieved in WP1-4 and WP5 Phases 2-3 cannot degrade over time.

**Key Objective**: Configure import-linter contracts that prevent cross-boundary violations while accommodating necessary grandfathered exceptions.

**Success Criteria**: All contracts passing in CI with documented exceptions for legitimate legacy dependencies.

---

## Phase Overview

### Objectives

1. **Map current import dependencies** - Establish baseline of all cross-package imports
2. **Configure import-linter contracts** - Define 5+ architectural contracts
3. **Document exceptions** - Create registry of legitimate boundary crossings
4. **Integrate with CI** - Block new violations in pull requests
5. **Publish ADR-005** - Document import boundary decisions

### Exit Criteria

- ✅ Import-linter configured with 5+ contracts
- ✅ All contracts passing (with documented exceptions)
- ✅ CI blocks on new boundary violations
- ✅ Exception registry documented
- ✅ ADR-005 published
- ✅ All 561/562 tests still passing
- ✅ Zero mypy errors maintained

### Time Estimate

- **Risk Reduction**: 0.5 days (4 hours)
- **Configuration**: 0.5 days (4 hours)
- **CI Integration**: 0.25 days (2 hours)
- **Documentation**: 0.25 days (2 hours)
- **Total**: 1.5 days (12 hours)

---

## Phase 0: Risk Reduction Activities (4 hours) 🛡️

### 0.1: Import Dependency Baseline (1.5 hours)

**Objective**: Map ALL current cross-package imports before adding enforcement

**Why This Matters**: Import-linter will fail on any violations. We need to know:
1. How many existing violations exist
2. Which violations are legitimate (need exceptions)
3. Which violations should be fixed vs grandfathered

**Activities**:

#### 1. Install Analysis Tools
```bash
pip install pydeps import-linter
```

#### 2. Generate Visual Dependency Graph
```bash
# Full codebase dependency graph
pydeps src/townlet --max-bacon 2 --cluster \
  --exclude "test_*" \
  -o docs/architecture_review/WP5_PHASE4_dependency_graph.svg

# Package-level view (cleaner)
pydeps src/townlet --max-bacon 1 --cluster \
  --only "townlet.*" \
  -o docs/architecture_review/WP5_PHASE4_package_dependencies.svg
```

**Expected Output**: SVG diagrams showing all import relationships

#### 3. Analyze DTO Package Dependencies
```bash
# DTOs should have ZERO dependencies on concrete packages
grep -r "^from townlet\." src/townlet/dto/ | \
  grep -vE "from townlet\.dto\." | \
  sort | uniq > docs/architecture_review/WP5_PHASE4_dto_violations.txt

# Expected: Empty file (DTOs are already clean per WP3)
```

#### 4. Analyze Config Package Dependencies
```bash
# Config should only import from dto, typing, pydantic
grep -r "^from townlet\." src/townlet/config/ | \
  grep -vE "from townlet\.(dto|config)\." | \
  sort | uniq > docs/architecture_review/WP5_PHASE4_config_violations.txt

# Expected: Some violations (to be fixed or grandfathered)
```

#### 5. Analyze World → Policy Dependencies
```bash
# World should NOT import policy
grep -r "^from townlet\.policy" src/townlet/world/ | \
  sort | uniq > docs/architecture_review/WP5_PHASE4_world_to_policy.txt

# Expected: Empty file (clean separation achieved in WP2)
```

#### 6. Analyze Policy → Telemetry Dependencies
```bash
# Policy should NOT import telemetry
grep -r "^from townlet\.telemetry" src/townlet/policy/ | \
  sort | uniq > docs/architecture_review/WP5_PHASE4_policy_to_telemetry.txt

# Expected: Empty file (clean separation achieved in WP4)
```

#### 7. Generate Import Matrix
```python
# scripts/analyze_imports.py (to be created)
"""Generate CSV matrix of all package-to-package imports."""

import ast
import os
from pathlib import Path
from collections import defaultdict

def find_imports(file_path: Path) -> set[str]:
    """Extract all townlet imports from a Python file."""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("townlet."):
                # Extract top-level package (e.g., "townlet.world")
                pkg = ".".join(node.module.split(".")[:2])
                imports.add(pkg)
    return imports

def main():
    src_dir = Path("src/townlet")
    packages = ["dto", "ports", "core", "config", "world", "policy",
                "telemetry", "rewards", "observations", "snapshots",
                "stability", "lifecycle", "benchmark", "agents"]

    # Build import matrix
    matrix = defaultdict(lambda: defaultdict(int))

    for pkg in packages:
        pkg_dir = src_dir / pkg
        if not pkg_dir.exists():
            continue

        for py_file in pkg_dir.rglob("*.py"):
            if py_file.name.startswith("test_"):
                continue

            imports = find_imports(py_file)
            for imported_pkg in imports:
                imported_name = imported_pkg.split(".")[1]
                if imported_name != pkg:
                    matrix[pkg][imported_name] += 1

    # Output CSV
    print("From/To," + ",".join(packages))
    for from_pkg in packages:
        row = [str(matrix[from_pkg][to_pkg]) for to_pkg in packages]
        print(f"{from_pkg}," + ",".join(row))

if __name__ == "__main__":
    main()
```

**Run Analysis**:
```bash
python scripts/analyze_imports.py > docs/architecture_review/WP5_PHASE4_import_matrix.csv
```

**Expected Output**: CSV showing counts of imports between each package pair

**Deliverables**:
- ✅ `WP5_PHASE4_dependency_graph.svg` - Full dependency graph
- ✅ `WP5_PHASE4_package_dependencies.svg` - Package-level view
- ✅ `WP5_PHASE4_dto_violations.txt` - DTO boundary violations (expected: 0)
- ✅ `WP5_PHASE4_config_violations.txt` - Config boundary violations
- ✅ `WP5_PHASE4_world_to_policy.txt` - World→Policy violations (expected: 0)
- ✅ `WP5_PHASE4_policy_to_telemetry.txt` - Policy→Telemetry violations (expected: 0)
- ✅ `WP5_PHASE4_import_matrix.csv` - Package-to-package import counts
- ✅ `scripts/analyze_imports.py` - Import analysis script

**Acceptance Criteria**:
- ✅ All baseline files generated
- ✅ Import violations quantified
- ✅ Visual dependency graphs saved

---

### 0.2: Import-Linter Dry Run (1 hour)

**Objective**: Test import-linter contracts in analysis mode BEFORE enforcing

**Why This Matters**: We need to see how many violations exist without breaking the build. This allows us to:
1. Calibrate contract strictness
2. Decide which violations to fix vs grandfather
3. Avoid surprise CI failures

**Activities**:

#### 1. Create Analysis-Only Config
```ini
# .importlinter.analysis
[importlinter]
root_package = townlet

[importlinter:contract:dto-independence]
name = DTOs must not import concrete packages
type = independence
modules =
    townlet.dto.observations
    townlet.dto.policy
    townlet.dto.rewards
    townlet.dto.telemetry
    townlet.dto.world

[importlinter:contract:layered-architecture]
name = Layered architecture (dto → ports → core → adapters → domain)
type = layers
layers =
    townlet.dto
    townlet.ports
    townlet.core
    (townlet.world | townlet.policy | townlet.telemetry | townlet.rewards)

[importlinter:contract:no-world-to-policy]
name = World must not import policy
type = forbidden
source_modules =
    townlet.world
forbidden_modules =
    townlet.policy

[importlinter:contract:no-policy-to-telemetry]
name = Policy must not import telemetry
type = forbidden
source_modules =
    townlet.policy
forbidden_modules =
    townlet.telemetry

[importlinter:contract:config-dto-only]
name = Config must only import DTO and typing
type = forbidden
source_modules =
    townlet.config
forbidden_modules =
    townlet.world
    townlet.policy
    townlet.telemetry
    townlet.snapshots
    townlet.rewards
```

#### 2. Run Dry Run
```bash
# Analysis mode (no strict enforcement)
import-linter --config .importlinter.analysis 2>&1 | \
  tee docs/architecture_review/WP5_PHASE4_linter_dry_run.txt

# Parse output to count violations per contract
```

#### 3. Categorize Violations

For each violation found:
1. **Legitimate architectural dependency** - Should be allowed, needs exception
2. **Legacy violation** - Should be fixed eventually, grandfather for now
3. **Easy fix** - Can be fixed immediately (<30 min), just do it
4. **Requires refactoring** - Needs significant work, defer to post-WP5

**Document in**: `docs/architecture_review/WP5_PHASE4_violation_assessment.md`

**Example Assessment**:
```markdown
## Violation Assessment

### Contract: config-dto-only

#### Violation 1: config.loader → snapshots.manager
- **Type**: Legacy violation
- **Reason**: Config loader needs to validate snapshot paths
- **Decision**: Grandfather with exception
- **Fix Plan**: Move validation to snapshots package (post-WP5)

#### Violation 2: config.models → world.grid
- **Type**: Easy fix
- **Reason**: Config imports WorldState for type hint
- **Decision**: Fix immediately
- **Fix**: Change to `from typing import TYPE_CHECKING` guard

### Contract: dto-independence

**Status**: ✅ No violations (as expected from WP3)

### Contract: no-world-to-policy

**Status**: ✅ No violations (clean separation achieved in WP2)
```

**Deliverables**:
- ✅ `.importlinter.analysis` - Analysis-only config
- ✅ `WP5_PHASE4_linter_dry_run.txt` - Dry run output
- ✅ `WP5_PHASE4_violation_assessment.md` - Categorized violations

**Acceptance Criteria**:
- ✅ Dry run completed without errors
- ✅ All violations categorized
- ✅ Exception strategy determined

---

### 0.3: Quick Win Fixes (1 hour)

**Objective**: Fix "easy" violations before adding contracts

**Why This Matters**: Reducing violation count upfront:
1. Makes contract configuration cleaner (fewer exceptions)
2. Improves architectural clarity
3. Demonstrates commitment to boundaries

**Target**: Fix 5-10 easy violations identified in dry run

**Common Easy Fixes**:

#### Pattern 1: Type Checking Guards
```python
# Before: Runtime import for type hint
from townlet.world.grid import WorldState

def process(world: WorldState) -> None:
    ...

# After: TYPE_CHECKING guard
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.world.grid import WorldState

def process(world: WorldState) -> None:
    ...
```

#### Pattern 2: Replace Concrete Import with Protocol
```python
# Before: Imports concrete TelemetryPublisher
from townlet.telemetry.publisher import TelemetryPublisher

def configure(telemetry: TelemetryPublisher) -> None:
    ...

# After: Import protocol from ports
from townlet.ports.telemetry import TelemetrySink

def configure(telemetry: TelemetrySink) -> None:
    ...
```

#### Pattern 3: Move Utility to Shared Module
```python
# Before: config imports world.utils.rng
from townlet.world.utils.rng import encode_rng_state

# After: Move rng to utils package
from townlet.utils.rng import encode_rng_state
```

**Process**:
1. Review `WP5_PHASE4_violation_assessment.md` "Easy fix" section
2. Apply fixes one at a time
3. Run tests after each fix: `pytest tests/ -x`
4. Run mypy after each fix: `mypy src --strict`
5. Commit each fix individually with descriptive message

**Deliverables**:
- ✅ 5-10 commits fixing easy violations
- ✅ Updated violation assessment showing remaining violations
- ✅ Tests still passing (561/562)
- ✅ Mypy still clean (0 errors)

**Acceptance Criteria**:
- ✅ Easy violations fixed
- ✅ No regressions introduced
- ✅ Commits documented with rationale

---

### 0.4: Exception Registry Setup (0.5 hours)

**Objective**: Create formal registry for grandfathered violations

**Why This Matters**: Transparency and accountability. Every architectural compromise should be:
1. Documented with rationale
2. Assigned an owner
3. Tracked for eventual resolution

**Create**: `docs/architecture_review/IMPORT_EXCEPTIONS.md`

**Template**:
```markdown
# Import Boundary Exceptions

## Overview

This document tracks legitimate exceptions to import-linter contracts. Each exception is documented with rationale, impact assessment, and resolution plan.

## Exception Request Process

1. Open GitHub issue with `import-exception` label
2. Fill out exception request template:
   - **Source Module**: Which module needs to import
   - **Target Module**: What it needs to import
   - **Contract**: Which import-linter contract this violates
   - **Rationale**: Why this dependency is necessary
   - **Alternatives Considered**: What other approaches were evaluated
   - **Impact**: How this affects architectural clarity
   - **Resolution Plan**: When/how this can be fixed (or "permanent")
3. ADR author review required
4. Approved exceptions documented in this file
5. Update `.importlinter` config with specific exception

## Active Exceptions

### Exception 1: config.loader → snapshots.manager

**Contract**: `config-dto-only` (config should only import dto)

**Source**: `src/townlet/config/loader.py:45`
**Target**: `townlet.snapshots.manager.SnapshotManager`

**Rationale**: Config loader needs to validate snapshot file paths during startup. This is a legitimate cross-boundary check that prevents invalid configuration from reaching runtime.

**Alternatives Considered**:
1. ❌ Move validation to snapshots package - Creates circular dependency
2. ❌ Use duck typing - Loses type safety
3. ✅ Accept exception - Minimal coupling, clear purpose

**Impact**: Low - Single import for validation only, no runtime dependency

**Approved By**: ADR-001 author (WP1 review)
**Date**: 2025-10-14

**Resolution Plan**: Consider extracting validation to shared `validation` package in future refactoring (post-WP5)

---

### Exception 2: world.grid → telemetry.events

**Contract**: `layered-architecture` (domain should not import adapters)

**Source**: `src/townlet/world/grid.py:112`
**Target**: `townlet.telemetry.events.emit_event`

**Rationale**: World state emits domain events for observability. This is the established telemetry pattern from WP2.

**Alternatives Considered**:
1. ❌ Dependency injection - Would require threading `emit_event` through 50+ method signatures
2. ✅ Accept exception - Clean observability pattern, well-established in codebase

**Impact**: Low - Telemetry is designed to be transparent to domain logic

**Approved By**: ADR-002 author (WP2 review)
**Date**: 2025-10-14

**Resolution Plan**: Permanent exception - This is the intentional observability pattern

---

## Exception Statistics

**Total Active Exceptions**: 2
**By Contract**:
- `config-dto-only`: 1
- `layered-architecture`: 1

**By Type**:
- Permanent (by design): 1
- Temporary (will fix): 1

---

## Resolved Exceptions

### [Example] config.models → world.grid (RESOLVED)

**Resolution**: Changed to TYPE_CHECKING guard
**Date Resolved**: 2025-10-14
**Commit**: abc123
```

**Deliverables**:
- ✅ `IMPORT_EXCEPTIONS.md` - Exception registry with template
- ✅ 2-5 initial exceptions documented (from dry run assessment)

**Acceptance Criteria**:
- ✅ Registry created with clear process
- ✅ All grandfathered violations documented
- ✅ Rationale and resolution plans provided

---

## Phase 0 Summary

**Total Time**: 4 hours
**Value**: De-risks 8 hours of contract configuration and CI integration

**Deliverables**:
- ✅ 7 baseline analysis files
- ✅ Visual dependency graphs (2 SVGs)
- ✅ Import analysis script
- ✅ Dry run assessment with categorized violations
- ✅ 5-10 easy violations fixed
- ✅ Exception registry established

**Risk Reduction**:
- 🔴 Surprise CI failures: HIGH → LOW (violations known and categorized)
- 🟡 Contract misconfiguration: MEDIUM → LOW (dry run validated)
- 🟡 Excessive exceptions: MEDIUM → LOW (easy fixes applied upfront)
- 🔴 Unclear violation resolution: HIGH → LOW (assessment and registry)

**Acceptance Criteria**:
- ✅ All baseline files committed
- ✅ Violations quantified and assessed
- ✅ Easy fixes applied (5-10 commits)
- ✅ Exception registry established
- ✅ Tests passing (561/562)
- ✅ Mypy clean (0 errors)

---

## Phase 1: Import-Linter Configuration (4 hours)

### 1.1: Create Production Config (1 hour)

**Objective**: Convert analysis config to enforcement config with exceptions

**Starting Point**: `.importlinter.analysis` from Phase 0

**Process**:

#### 1. Copy Analysis Config
```bash
cp .importlinter.analysis .importlinter
```

#### 2. Add Exceptions

For each grandfathered violation in `IMPORT_EXCEPTIONS.md`, add to config:

```ini
[importlinter:contract:config-dto-only]
name = Config must only import DTO and typing
type = forbidden
source_modules =
    townlet.config
forbidden_modules =
    townlet.world
    townlet.policy
    townlet.telemetry
    townlet.snapshots
    townlet.rewards

# Exceptions (see IMPORT_EXCEPTIONS.md)
ignore_imports =
    townlet.config.loader -> townlet.snapshots.manager  # Exception #1: Validation
```

#### 3. Add Layer Exceptions

```ini
[importlinter:contract:layered-architecture]
name = Layered architecture
type = layers
layers =
    townlet.dto
    townlet.ports
    townlet.core
    (townlet.world | townlet.policy | townlet.telemetry | townlet.rewards)

# Exceptions (see IMPORT_EXCEPTIONS.md)
ignore_imports =
    townlet.world.grid -> townlet.telemetry.events  # Exception #2: Domain events
```

#### 4. Validate Config
```bash
import-linter --config .importlinter
echo $?  # Should be 0 (success)
```

**Expected Output**: All contracts passing with documented exceptions

**Deliverables**:
- ✅ `.importlinter` - Production config with exceptions
- ✅ Config validated (all contracts passing)

**Acceptance Criteria**:
- ✅ `import-linter` passes locally
- ✅ All exceptions match registry
- ✅ No undocumented ignore_imports

---

### 1.2: Add Additional Contracts (2 hours)

**Objective**: Add more architectural contracts beyond the 5 basic ones

**Additional Contracts**:

#### Contract 6: DTO Purity (No External Imports)
```ini
[importlinter:contract:dto-purity]
name = DTOs must not import external packages (except pydantic, typing)
type = forbidden
source_modules =
    townlet.dto
forbidden_modules =
    numpy
    torch
    pandas
    # Allow pydantic, typing implicitly
```

**Rationale**: DTOs should be pure data containers without framework dependencies

#### Contract 7: Port Protocol Purity
```ini
[importlinter:contract:port-independence]
name = Port protocols must not import adapters
type = forbidden
source_modules =
    townlet.ports
forbidden_modules =
    townlet.world
    townlet.policy
    townlet.telemetry
    townlet.rewards
    townlet.snapshots
```

**Rationale**: Ports define contracts, adapters implement them. Reverse dependency is architectural violation.

#### Contract 8: Test Isolation
```ini
[importlinter:contract:no-test-imports]
name = Source code must not import test modules
type = forbidden
source_modules =
    townlet
forbidden_modules =
    tests
    pytest
```

**Rationale**: Production code should never import test utilities

#### Contract 9: Snapshot Independence
```ini
[importlinter:contract:snapshot-boundaries]
name = Snapshots must not import world/policy implementations
type = forbidden
source_modules =
    townlet.snapshots
forbidden_modules =
    townlet.world.grid
    townlet.policy.runner
    townlet.telemetry.publisher
```

**Rationale**: Snapshots operate on DTOs, not concrete implementations

**Deliverables**:
- ✅ 4 additional contracts configured
- ✅ All contracts passing
- ✅ Contracts documented in `.importlinter` with rationale comments

**Acceptance Criteria**:
- ✅ 9 total contracts enforced
- ✅ All passing with exceptions
- ✅ Each contract has clear rationale comment

---

### 1.3: Contract Testing (1 hour)

**Objective**: Verify contracts catch violations with negative tests

**Why This Matters**: Confirm contracts are working, not accidentally bypassed

**Create**: `tests/test_import_boundaries.py`

```python
"""Test that import-linter contracts are correctly configured.

This test suite verifies that architectural boundaries are enforced.
"""

import subprocess
import tempfile
from pathlib import Path


def test_import_linter_contracts_pass():
    """Verify all import-linter contracts pass."""
    result = subprocess.run(
        ["import-linter", "--config", ".importlinter"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Import contracts failed:\n{result.stdout}"


def test_dto_cannot_import_world():
    """Negative test: DTO importing world should be caught."""
    violation_code = """
from townlet.dto.observations import ObservationDTO
from townlet.world.grid import WorldState  # VIOLATION

def bad_function(world: WorldState) -> ObservationDTO:
    return ObservationDTO(...)
"""

    # Create temporary file with violation
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        dir="src/townlet/dto",
        delete=False,
    ) as f:
        f.write(violation_code)
        temp_path = Path(f.name)

    try:
        # Run import-linter (should fail)
        result = subprocess.run(
            ["import-linter", "--config", ".importlinter"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, "Contract did not catch violation"
        assert "dto-independence" in result.stdout
    finally:
        temp_path.unlink()


def test_config_cannot_import_policy():
    """Negative test: Config importing policy should be caught."""
    violation_code = """
from townlet.config.base import SimulationConfig
from townlet.policy.runner import PolicyRuntime  # VIOLATION

def bad_function(policy: PolicyRuntime) -> None:
    pass
"""

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        dir="src/townlet/config",
        delete=False,
    ) as f:
        f.write(violation_code)
        temp_path = Path(f.name)

    try:
        result = subprocess.run(
            ["import-linter", "--config", ".importlinter"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, "Contract did not catch violation"
        assert "config-dto-only" in result.stdout
    finally:
        temp_path.unlink()


def test_world_cannot_import_policy():
    """Negative test: World importing policy should be caught."""
    # Similar pattern to above tests
    pass


def test_exception_registry_matches_config():
    """Verify all ignore_imports in .importlinter are documented."""
    import configparser

    config = configparser.ConfigParser()
    config.read(".importlinter")

    # Extract all ignore_imports entries
    ignore_imports = []
    for section in config.sections():
        if "contract:" in section:
            if "ignore_imports" in config[section]:
                imports = config[section]["ignore_imports"].strip().split("\n")
                ignore_imports.extend(imports)

    # Load exception registry
    exceptions_md = Path("docs/architecture_review/IMPORT_EXCEPTIONS.md").read_text()

    # Verify each ignored import has a documented exception
    for ignored in ignore_imports:
        if not ignored.strip() or ignored.strip().startswith("#"):
            continue

        import_path = ignored.split("#")[0].strip()
        assert import_path in exceptions_md, (
            f"Ignored import {import_path} not documented in IMPORT_EXCEPTIONS.md"
        )
```

**Run Tests**:
```bash
pytest tests/test_import_boundaries.py -v
```

**Expected Output**: All tests pass, negative tests correctly fail during temp file phase

**Deliverables**:
- ✅ `tests/test_import_boundaries.py` - Contract validation tests
- ✅ 5+ test cases covering contracts and exceptions

**Acceptance Criteria**:
- ✅ Positive test (contracts pass) succeeds
- ✅ Negative tests (violations) correctly caught
- ✅ Exception registry validated against config

---

## Phase 2: CI Integration (2 hours)

### 2.1: GitHub Actions Workflow (1 hour)

**Objective**: Add import-linter to CI pipeline

**Create**: `.github/workflows/import-boundaries.yml`

```yaml
name: Import Boundary Enforcement

on:
  push:
    branches: [main, feature/**]
  pull_request:
    branches: [main]

jobs:
  import-linter:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install import-linter
        run: pip install import-linter

      - name: Check import boundaries
        run: |
          import-linter --config .importlinter
          echo "✅ All import contracts passed"

      - name: Upload contract report (on failure)
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: import-linter-report
          path: |
            .importlinter
            docs/architecture_review/IMPORT_EXCEPTIONS.md
```

**Test Workflow Locally** (using act or manual test):
```bash
# Create test violation
echo "from townlet.policy.runner import PolicyRuntime" >> src/townlet/dto/observations.py

# Run import-linter
import-linter --config .importlinter
# Should fail

# Revert test violation
git checkout src/townlet/dto/observations.py

# Run import-linter
import-linter --config .importlinter
# Should pass
```

**Deliverables**:
- ✅ `.github/workflows/import-boundaries.yml` - CI workflow
- ✅ Workflow tested locally
- ✅ Failure case validated

**Acceptance Criteria**:
- ✅ Workflow runs on push and PR
- ✅ Blocks on boundary violations
- ✅ Uploads helpful error reports on failure

---

### 2.2: Update Main CI Workflow (0.5 hours)

**Objective**: Integrate import-linter with existing lint workflow

**Modify**: `.github/workflows/lint.yml` (or existing lint workflow)

```yaml
name: Lint and Type Check

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      # Install dependencies
      - name: Install dependencies
        run: |
          pip install -e .[dev]
          pip install import-linter  # ADD THIS

      # Existing checks
      - name: Ruff lint
        run: ruff check src tests

      - name: Mypy type check
        run: mypy src --strict

      # NEW: Import boundary check
      - name: Import boundaries
        run: import-linter --config .importlinter
```

**Deliverables**:
- ✅ Updated lint workflow with import-linter
- ✅ Workflow tested in PR

**Acceptance Criteria**:
- ✅ Import-linter integrated with existing checks
- ✅ All checks passing in CI

---

### 2.3: Add Pre-Commit Hook (0.5 hours)

**Objective**: Catch violations before commit (optional but helpful)

**Modify**: `.pre-commit-config.yaml` (if exists, otherwise create)

```yaml
repos:
  # Existing hooks...

  - repo: local
    hooks:
      - id: import-linter
        name: Import Boundary Check
        entry: import-linter --config .importlinter
        language: python
        pass_filenames: false
        additional_dependencies: [import-linter]
```

**Test Hook**:
```bash
# Install pre-commit (if not already)
pip install pre-commit
pre-commit install

# Test with violation
echo "from townlet.world.grid import WorldState" >> src/townlet/dto/observations.py
git add src/townlet/dto/observations.py
git commit -m "Test"
# Should fail with import-linter error

# Revert
git checkout src/townlet/dto/observations.py
```

**Deliverables**:
- ✅ `.pre-commit-config.yaml` with import-linter hook
- ✅ Hook tested and working

**Acceptance Criteria**:
- ✅ Pre-commit hook catches violations locally
- ✅ Fast feedback (<5 seconds)

---

## Phase 3: Documentation (2 hours)

### 3.1: ADR-005: Import Boundaries (1.5 hours)

**Objective**: Document import boundary decisions formally

**Create**: `docs/architecture_review/ADR/ADR-005 - Import Boundaries.md`

**Template** (following existing ADR format):

```markdown
# ADR-005: Import Boundary Enforcement

**Status**: Accepted
**Date**: 2025-10-14
**Authors**: WP5 Team
**Supersedes**: None
**Related**: ADR-001 (Ports), ADR-002 (World), ADR-003 (DTOs), ADR-004 (Policy)

---

## Context

During WP1-4 and WP5, we refactored the codebase into a modular architecture with clear separation of concerns. However, without automated enforcement, these boundaries can erode over time as developers add new features.

**Problem**: How do we prevent architectural regression and ensure the modular structure is maintained?

**Key Concerns**:
1. New code might violate established boundaries
2. Gradual coupling between modules degrades architecture
3. Manual code review is error-prone for detecting violations
4. Developers may not be aware of architectural contracts

---

## Decision

We will use **import-linter** to enforce architectural boundaries at the import level, with contracts defined in `.importlinter` and enforced in CI.

**9 Contracts Defined**:

1. **DTO Independence** - DTOs must not import concrete packages
2. **Layered Architecture** - Enforce dto → ports → core → adapters → domain
3. **World/Policy Separation** - World must not import policy
4. **Policy/Telemetry Separation** - Policy must not import telemetry
5. **Config DTO-Only** - Config must only import DTOs
6. **DTO Purity** - DTOs must not import external frameworks
7. **Port Independence** - Ports must not import adapters
8. **Test Isolation** - Production code must not import tests
9. **Snapshot Boundaries** - Snapshots must not import implementations

**Exception Process**:
- Legitimate exceptions documented in `IMPORT_EXCEPTIONS.md`
- Requires rationale, alternatives considered, and resolution plan
- ADR author approval required
- Tracked with `import-exception` GitHub label

---

## Consequences

### Positive

✅ **Architectural Integrity**: Boundaries enforced automatically, preventing erosion
✅ **Fast Feedback**: Violations caught in <5 seconds locally, <1 min in CI
✅ **Clear Contracts**: 9 explicit architectural rules, well-documented
✅ **Granular Control**: Can define forbidden, independence, and layered contracts
✅ **Exception Transparency**: All compromises documented with rationale

### Negative

❌ **Build Failures**: New violations will break CI (by design)
❌ **Exception Overhead**: Legitimate cross-boundary imports require documentation
❌ **False Positives**: May need to tune contracts based on real-world usage
❌ **Learning Curve**: Developers need to understand architectural contracts

### Neutral

⚪ **Grandfathered Violations**: 2-5 existing violations documented as exceptions
⚪ **Maintenance**: `.importlinter` config requires updates as architecture evolves

---

## Alternatives Considered

### Alternative 1: Manual Code Review Only

**Pros**: No tooling overhead, flexible
**Cons**: Error-prone, not scalable, inconsistent enforcement
**Verdict**: ❌ Rejected - Too unreliable for long-term architectural health

### Alternative 2: Dependency Cruiser (TypeScript tool)

**Pros**: More features (circular dependency detection)
**Cons**: Not Python-native, requires Node.js, overkill for our needs
**Verdict**: ❌ Rejected - import-linter is Python-native and sufficient

### Alternative 3: Custom Import Hook

**Pros**: Maximum control and flexibility
**Cons**: High maintenance burden, reinventing the wheel
**Verdict**: ❌ Rejected - import-linter is mature and well-supported

---

## Implementation Plan

**Phase 4.0**: Risk Reduction (4 hours)
- Map current dependencies
- Dry run analysis
- Fix easy violations
- Setup exception registry

**Phase 4.1**: Configuration (4 hours)
- Create production config
- Add 9 contracts
- Test with negative cases

**Phase 4.2**: CI Integration (2 hours)
- Add GitHub Actions workflow
- Update existing lint workflow
- Add pre-commit hook

**Phase 4.3**: Documentation (2 hours)
- This ADR
- Update CLAUDE.md
- Update WP_COMPLIANCE_ASSESSMENT.md

---

## Validation

### Success Metrics

- ✅ 9 contracts enforced in CI
- ✅ <5 exceptions documented
- ✅ CI blocks new violations
- ✅ All 561/562 tests passing
- ✅ Zero mypy errors maintained

### Monitoring

- Track exception count over time (should not grow)
- Monitor CI failure rate on import-linter step
- Review exception registry quarterly

---

## References

- [import-linter documentation](https://import-linter.readthedocs.io/)
- `docs/architecture_review/IMPORT_EXCEPTIONS.md` - Exception registry
- `.importlinter` - Contract configuration
- ADR-001: Port and Factory Registry
- ADR-002: World Modularisation
- ADR-003: DTO Boundary
- ADR-004: Policy Training Strategies

---

**Approved**: 2025-10-14
**Signed off by**: WP5 Team
```

**Deliverables**:
- ✅ `ADR-005 - Import Boundaries.md` - Complete ADR document

**Acceptance Criteria**:
- ✅ Follows existing ADR format
- ✅ Comprehensive context and rationale
- ✅ Alternatives considered documented
- ✅ Implementation plan included

---

### 3.2: Update Project Documentation (0.5 hours)

**Objective**: Update main docs to reflect Phase 4 completion

**Files to Update**:

#### 1. `CLAUDE.md`
```markdown
## Architectural Boundaries

The codebase enforces import boundaries using import-linter with 9 contracts:

1. **DTO Independence** - DTOs don't import concrete packages
2. **Layered Architecture** - dto → ports → core → adapters → domain
3. **World/Policy Separation** - Clean module boundaries
4. ... (list all 9)

**Checking boundaries locally**:
```bash
import-linter --config .importlinter
```

**Exception process**: See `docs/architecture_review/IMPORT_EXCEPTIONS.md`
```

#### 2. `docs/architecture_review/WP_TASKINGS/WP_COMPLIANCE_ASSESSMENT.md`
```markdown
### WP5: Final Hardening & Quality Gates

**Status**: COMPLETE ✅
**Completion**: 100%

#### Phase 4: Boundary Enforcement ✅
- ✅ Import-linter configured (9 contracts)
- ✅ CI integration complete
- ✅ Exception registry established
- ✅ ADR-005 published
```

#### 3. `docs/architecture_review/WP_NOTES/WP5/WP5_PROGRESS_SUMMARY.md`
```markdown
| Phase | Status | Progress |
|-------|--------|----------|
| Phase 4: Boundary Enforcement | ✅ COMPLETE | 100% |
```

**Deliverables**:
- ✅ Updated `CLAUDE.md` with boundary checking instructions
- ✅ Updated `WP_COMPLIANCE_ASSESSMENT.md` showing Phase 4 complete
- ✅ Updated `WP5_PROGRESS_SUMMARY.md` with Phase 4 status

**Acceptance Criteria**:
- ✅ All docs reflect Phase 4 completion
- ✅ Developer guidance provided
- ✅ Links to detailed docs included

---

## Phase Summary & Success Criteria

### Overall Success Criteria

**Must Have** (Blocking):
- ✅ 9 import-linter contracts configured and passing
- ✅ CI blocks on new boundary violations
- ✅ Exception registry established with ≤5 exceptions
- ✅ ADR-005 published
- ✅ All 561/562 tests still passing
- ✅ Zero mypy errors maintained

**Should Have** (Desirable):
- ✅ Pre-commit hook installed
- ✅ Visual dependency graphs generated
- ✅ Import analysis script created
- ✅ Easy violations fixed (5-10 commits)

**Nice to Have** (Optional):
- ⭕ Automated exception tracking dashboard
- ⭕ Quarterly exception review process established

### Quality Metrics

**Code Quality**:
- ✅ `.importlinter` config well-commented
- ✅ `IMPORT_EXCEPTIONS.md` comprehensive
- ✅ `ADR-005` follows ADR template

**Testing**:
- ✅ `test_import_boundaries.py` with 5+ test cases
- ✅ Negative tests validate contracts work
- ✅ CI workflow tested

**Documentation**:
- ✅ Developer guidance in CLAUDE.md
- ✅ Architectural decisions in ADR-005
- ✅ Exception process clearly defined

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation | Status |
|------|------------|--------|------------|--------|
| CI failures surprise team | LOW | MEDIUM | Risk reduction phase maps all violations upfront | ✅ MITIGATED |
| Excessive exceptions needed | LOW | MEDIUM | Quick win fixes reduce count before enforcement | ✅ MITIGATED |
| Contracts too strict | MEDIUM | LOW | Dry run calibrates contracts before enforcement | ✅ MITIGATED |
| Developer friction | MEDIUM | LOW | Clear exception process and developer docs | ✅ MITIGATED |
| False positives | LOW | LOW | Contract testing validates enforcement logic | ✅ MITIGATED |

---

## Rollback Plan

**Trigger Conditions**:
1. CI consistently failing due to contract issues (>50% of PRs blocked)
2. Excessive exceptions needed (>20 documented)
3. Developer productivity significantly impacted

**Rollback Procedure**:

### Step 1: Disable CI Enforcement (15 minutes)
```bash
# Comment out import-linter step in CI
git checkout .github/workflows/import-boundaries.yml
# Comment out the import-linter job

git commit -m "Temporarily disable import-linter CI enforcement"
git push
```

### Step 2: Keep Local Checking Available (Optional)
```bash
# Leave .importlinter config in place
# Developers can still run locally: import-linter
# This allows voluntary checking without CI blocking
```

### Step 3: Assess Issues (1-2 hours)
```markdown
# Create assessment document
- What contracts are failing frequently?
- Are violations legitimate or architectural issues?
- Do contracts need refinement vs removal?
- Is exception process too heavyweight?
```

### Step 4: Refine and Re-enable (1-2 days)
```bash
# Option A: Adjust contracts to be less strict
# Option B: Add more grandfathered exceptions
# Option C: Change enforcement level (warnings vs errors)

# Re-enable after refinement
```

**Time to Rollback**: <30 minutes (disable CI), 1-2 days (fix and re-enable)

---

## Timeline Summary

| Phase | Duration | Effort | Dependencies |
|-------|----------|--------|--------------|
| **Phase 0: Risk Reduction** | 0.5 days | 4 hours | None |
| 0.1: Dependency Baseline | | 1.5 hours | |
| 0.2: Dry Run Analysis | | 1 hour | 0.1 complete |
| 0.3: Quick Win Fixes | | 1 hour | 0.2 complete |
| 0.4: Exception Registry | | 0.5 hours | 0.2, 0.3 complete |
| **Phase 1: Configuration** | 0.5 days | 4 hours | Phase 0 complete |
| 1.1: Production Config | | 1 hour | |
| 1.2: Additional Contracts | | 2 hours | 1.1 complete |
| 1.3: Contract Testing | | 1 hour | 1.2 complete |
| **Phase 2: CI Integration** | 0.25 days | 2 hours | Phase 1 complete |
| 2.1: GitHub Actions | | 1 hour | |
| 2.2: Update Lint Workflow | | 0.5 hours | |
| 2.3: Pre-Commit Hook | | 0.5 hours | |
| **Phase 3: Documentation** | 0.25 days | 2 hours | Phase 2 complete |
| 3.1: ADR-005 | | 1.5 hours | |
| 3.2: Update Project Docs | | 0.5 hours | |
| **TOTAL** | **1.5 days** | **12 hours** | Sequential |

**Parallelization Opportunities**: None (all phases are sequential dependencies)

---

## Deliverables Checklist

### Code & Configuration
- [ ] `.importlinter` - Production config with 9 contracts
- [ ] `scripts/analyze_imports.py` - Import analysis script
- [ ] `tests/test_import_boundaries.py` - Contract validation tests
- [ ] `.github/workflows/import-boundaries.yml` - CI workflow
- [ ] `.pre-commit-config.yaml` - Pre-commit hook (optional)

### Documentation
- [ ] `docs/architecture_review/IMPORT_EXCEPTIONS.md` - Exception registry
- [ ] `docs/architecture_review/ADR/ADR-005 - Import Boundaries.md` - ADR
- [ ] `docs/architecture_review/WP5_PHASE4_dependency_graph.svg` - Visual graph
- [ ] `docs/architecture_review/WP5_PHASE4_package_dependencies.svg` - Package view
- [ ] `docs/architecture_review/WP5_PHASE4_violation_assessment.md` - Assessment
- [ ] Updated `CLAUDE.md` - Developer guidance
- [ ] Updated `WP_COMPLIANCE_ASSESSMENT.md` - Phase 4 status
- [ ] Updated `WP5_PROGRESS_SUMMARY.md` - Progress tracking

### Analysis Files (Baseline)
- [ ] `WP5_PHASE4_dto_violations.txt` - DTO boundary violations
- [ ] `WP5_PHASE4_config_violations.txt` - Config violations
- [ ] `WP5_PHASE4_world_to_policy.txt` - World→Policy violations
- [ ] `WP5_PHASE4_policy_to_telemetry.txt` - Policy→Telemetry violations
- [ ] `WP5_PHASE4_import_matrix.csv` - Package import matrix
- [ ] `WP5_PHASE4_linter_dry_run.txt` - Dry run output

**Total Deliverables**: 19 files (5 code/config, 8 docs, 6 analysis)

---

## Sign-Off

**Phase 4 Status**: READY TO START

**Risk Level**: LOW (after Phase 0 risk reduction)

**Confidence**: HIGH
- Similar patterns successfully used in other projects
- Dry run approach de-risks enforcement
- Clear rollback plan provides safety net

**Recommendation**: **PROCEED** with Phase 0 risk reduction activities

**Next Action**: Begin Phase 0.1 (Import Dependency Baseline)

---

**End of Phase 4 Execution Plan**
