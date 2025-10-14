# Phase 0: Risk Reduction Activities

**Purpose**: De-risk Phase 1-3 execution through investigation and validation
**Duration Estimate**: 0.5-1 day
**Priority**: 🔴 CRITICAL (prevents costly mistakes)

---

## Overview

Before executing code changes (Phase 1) or making architectural decisions (Phase 2), we need to validate assumptions and understand the actual implementation. Phase 0 performs **reconnaissance activities** that will inform later phases.

**Principle**: *"Measure twice, cut once"*

---

## Risk Reduction Activities

### RR1: Reward Engine Impact Analysis (Est: 2-3 hours)

**Objective**: Understand current reward system structure and integration points before modifying.

**Activities**:

1. **Map reward engine structure** (30 min)
   - Read `src/townlet/rewards/engine.py` thoroughly
   - Document current return type and structure
   - Identify all methods that return rewards
   - Note any existing DTO usage or preparation

2. **Find all reward consumers** (60 min)
   ```bash
   # Find all imports of reward engine
   grep -r "from townlet.rewards" src/ tests/
   grep -r "import.*rewards" src/ tests/

   # Find all callsites of reward computation
   grep -r "\.compute\(" src/ tests/ | grep -i reward
   grep -r "reward.*breakdown" src/ tests/
   ```
   - Document every module that consumes rewards
   - Identify dict access patterns (e.g., `rewards["alice"]["total"]`)
   - Create callsite inventory for later validation

3. **Analyze reward test coverage** (30 min)
   ```bash
   # Find reward tests
   find tests -name "*reward*" -type f
   grep -r "RewardEngine" tests/
   ```
   - Count existing reward tests
   - Identify integration tests vs unit tests
   - Note any missing coverage areas

4. **Create reward DTO compatibility matrix** (30 min)
   - Document current dict structure vs DTO fields
   - Identify any missing fields in DTO
   - Flag any backward compatibility concerns
   - Estimate test update effort

**Deliverable**: `REWARD_IMPACT_ANALYSIS.md` with:
- Current reward flow diagram
- Callsite inventory (with line numbers)
- Test coverage assessment
- DTO compatibility matrix
- Risk assessment for Phase 1

**Success Criteria**:
- ✅ Complete understanding of reward data flow
- ✅ All consumers identified
- ✅ Test strategy validated
- ✅ No surprises in Phase 1

---

### RR2: Context/Runtime Dependency Analysis (Est: 1-2 hours)

**Objective**: Map the actual relationships between the three Context/Runtime concepts before making consolidation decision.

**Activities**:

1. **Check for imports of skeleton stub** (15 min)
   ```bash
   # Find imports of world/context.py stub
   grep -r "from townlet.world.context import" src/ tests/
   grep -r "from townlet.world import.*Context" src/ tests/
   grep -r "world\.context\." src/ tests/
   ```
   - Verify stub is never imported (as suspected)
   - Document any surprising usage

2. **Map WorldContext usage** (30 min)
   ```bash
   # Find imports of world/core/context.py
   grep -r "from townlet.world.core.context import" src/ tests/
   grep -r "WorldContext" src/ tests/
   ```
   - Document all consumers of `WorldContext`
   - Identify creation patterns
   - Note dependencies

3. **Map WorldRuntime usage** (30 min)
   ```bash
   # Find WorldRuntime usage
   grep -r "from townlet.world.runtime import" src/ tests/
   grep -r "WorldRuntime" src/ tests/
   grep -r "from townlet.ports.world import" src/ tests/
   ```
   - Document adapter usage patterns
   - Identify port protocol vs implementation usage
   - Note test patterns

4. **Create dependency diagram** (30 min)
   - Sketch actual dependencies between concepts
   - Identify delegation patterns
   - Highlight any circular dependencies
   - Document ownership (who creates what)

**Deliverable**: `CONTEXT_RUNTIME_DEPENDENCY_MAP.md` with:
- Import graph (ASCII diagram)
- Usage patterns
- Delegation chains
- Recommended consolidation approach (with evidence)

**Success Criteria**:
- ✅ Clear picture of actual dependencies
- ✅ Evidence-based consolidation decision
- ✅ No risk of breaking hidden dependencies
- ✅ Confident Phase 2 execution

---

### RR3: World Package Structure Validation (Est: 1-2 hours)

**Objective**: Verify actual world package matches claimed structure before documenting in ADR-002.

**Activities**:

1. **Generate actual world package tree** (15 min)
   ```bash
   # Generate clean tree view
   tree src/townlet/world -L 3 -I "__pycache__|*.pyc" > world_structure.txt

   # Count modules per subdirectory
   find src/townlet/world -name "*.py" -not -path "*/__pycache__/*" | \
     xargs dirname | sort | uniq -c
   ```

2. **Verify systems architecture** (30 min)
   - Read `world/systems/` module docstrings
   - Verify each system's purpose matches documentation
   - Check for any legacy or deprecated systems
   - Identify any missing systems from ADR-002

3. **Validate observation architecture** (30 min)
   - Verify `world/observations/` matches WP3.1 delivery
   - Check encoder implementation status
   - Validate service orchestration pattern
   - Confirm no legacy ObservationBuilder usage

4. **Check for orphaned modules** (30 min)
   ```bash
   # Find potential orphans (no imports)
   for file in src/townlet/world/*.py; do
     name=$(basename $file .py)
     count=$(grep -r "from townlet.world import.*$name" src/ tests/ | wc -l)
     if [ $count -eq 0 ]; then
       echo "Potential orphan: $file"
     fi
   done
   ```
   - Identify unused modules
   - Check for TODOs or NotImplementedError stubs
   - Flag candidates for cleanup

**Deliverable**: `WORLD_PACKAGE_VALIDATION.md` with:
- Actual package tree (cleaned)
- Module purpose matrix
- Orphan candidates
- Discrepancies from ADR-002
- Verified architecture diagram

**Success Criteria**:
- ✅ Accurate world package structure documented
- ✅ No surprises when updating ADR-002
- ✅ Orphan modules identified for cleanup
- ✅ Confident Phase 3 execution

---

### RR4: Test Suite Health Check (Est: 30 min)

**Objective**: Establish baseline test health before making changes.

**Activities**:

1. **Run full test suite** (15 min)
   ```bash
   pytest --tb=short --co -q  # Collect tests
   pytest -x --tb=short       # Run with fail-fast
   ```
   - Verify all 816+ tests pass
   - Note any flaky tests
   - Document baseline execution time

2. **Run type checking** (5 min)
   ```bash
   mypy src/townlet/rewards
   mypy src/townlet/world
   mypy src/townlet/dto
   ```
   - Verify clean type checking
   - Note any pre-existing issues

3. **Run linting** (5 min)
   ```bash
   ruff check src/townlet/rewards
   ruff check src/townlet/world
   ruff check src/townlet/dto
   ```
   - Verify clean linting
   - Note any pre-existing issues

4. **Check coverage baseline** (5 min)
   ```bash
   pytest --cov=src/townlet/rewards --cov-report=term
   pytest --cov=src/townlet/world --cov-report=term
   ```
   - Document baseline coverage for affected modules
   - Identify low-coverage areas

**Deliverable**: `BASELINE_TEST_HEALTH.md` with:
- Test count (overall and per-module)
- Baseline execution time
- Pre-existing type/lint issues
- Coverage baselines
- Flaky test list (if any)

**Success Criteria**:
- ✅ Baseline established for comparison
- ✅ Pre-existing issues documented (won't be blamed on WP4.1)
- ✅ Health check passed (ready for changes)

---

### RR5: Reward DTO Compatibility Validation (Est: 1 hour)

**Objective**: Verify that `RewardBreakdown` DTO matches actual reward engine output structure.

**Activities**:

1. **Capture actual reward output** (30 min)
   ```python
   # Create test script to capture reward structure
   from townlet.core.sim_loop import SimulationLoop
   from townlet.config.loader import load_config
   import json

   config = load_config("configs/examples/poc_hybrid.yaml")
   loop = SimulationLoop(config)

   # Run one tick and capture rewards
   loop.step()
   # Capture actual reward structure (will be in sim_loop or accessible via telemetry)
   ```
   - Run minimal simulation to capture reward output
   - Save actual structure to JSON
   - Document all fields and types

2. **Compare with RewardBreakdown DTO** (15 min)
   - Load `townlet/dto/rewards.py`
   - Compare captured structure with DTO fields
   - Identify mismatches:
     - Missing fields in DTO
     - Extra fields in DTO (unused)
     - Type mismatches
   - Note any name discrepancies

3. **Test DTO construction** (15 min)
   ```python
   from townlet.dto.rewards import RewardBreakdown
   import json

   # Try to construct DTO from captured output
   captured = json.load(open("captured_rewards.json"))
   for agent_id, reward_data in captured.items():
       try:
           dto = RewardBreakdown(
               agent_id=agent_id,
               tick=reward_data["tick"],
               total=reward_data["total"],
               # ... map all fields
           )
           print(f"✅ {agent_id}: DTO construction successful")
       except Exception as e:
           print(f"❌ {agent_id}: {e}")
   ```
   - Validate DTO construction works with real data
   - Identify any validation errors
   - Fix DTO if needed before Phase 1

**Deliverable**: `REWARD_DTO_COMPATIBILITY.md` with:
- Captured reward structure (JSON)
- Field mapping table (actual → DTO)
- Compatibility assessment
- Required DTO updates (if any)
- Construction validation results

**Success Criteria**:
- ✅ DTO matches actual reward structure
- ✅ No field mismatches
- ✅ DTO construction validated
- ✅ No DTO updates needed (or updates documented)

---

### RR6: Create Phase 1 Test Strategy (Est: 30 min)

**Objective**: Design test update strategy before touching code.

**Activities**:

1. **Catalog existing reward tests** (15 min)
   - List all test files touching rewards
   - Categorize by test type (unit/integration)
   - Identify hermetic vs end-to-end tests

2. **Design DTO test strategy** (15 min)
   - Plan new DTO-specific tests (validation, serialization)
   - Plan test updates for existing tests
   - Identify tests that need mocking
   - Design integration test for end-to-end DTO flow
   - Estimate test update effort per file

**Deliverable**: `PHASE1_TEST_STRATEGY.md` with:
- Test catalog
- Update strategy per test type
- New test specifications
- Effort estimates
- Test execution order

**Success Criteria**:
- ✅ Clear test update plan
- ✅ No ad-hoc test changes
- ✅ Coverage maintained or improved
- ✅ TDD approach enabled

---

## Phase 0 Execution Order

Execute in this sequence to minimize rework:

1. **RR4** (30 min) — Establish baseline first
2. **RR1** (2-3 hours) — Understand reward system (critical path)
3. **RR5** (1 hour) — Validate DTO compatibility
4. **RR6** (30 min) — Plan test strategy
5. **RR2** (1-2 hours) — Map context/runtime dependencies
6. **RR3** (1-2 hours) — Validate world structure

**Total Time**: 5.5-8 hours (0.5-1 day)

**Parallel Opportunities**:
- RR2 and RR3 can be done in parallel with RR1
- RR4 should be done first (baseline)
- RR5 and RR6 depend on RR1

---

## Phase 0 Deliverables Summary

1. ✅ `REWARD_IMPACT_ANALYSIS.md` — Reward engine structure and consumers
2. ✅ `CONTEXT_RUNTIME_DEPENDENCY_MAP.md` — Architecture dependencies
3. ✅ `WORLD_PACKAGE_VALIDATION.md` — Verified world structure
4. ✅ `BASELINE_TEST_HEALTH.md` — Pre-change test health
5. ✅ `REWARD_DTO_COMPATIBILITY.md` — DTO validation results
6. ✅ `PHASE1_TEST_STRATEGY.md` — Test update plan

All deliverables stored in: `docs/architecture_review/WP_NOTES/WP4.1/`

---

## Risk Reduction Success Metrics

### Before Phase 0 (Current Risk Level)
- 🔴 **HIGH**: Unknown reward consumer count
- 🔴 **HIGH**: Unknown context/runtime dependencies
- 🟡 **MEDIUM**: Unverified world structure
- 🟡 **MEDIUM**: Unknown DTO compatibility

### After Phase 0 (Target Risk Level)
- 🟢 **LOW**: All reward consumers mapped
- 🟢 **LOW**: Clear context/runtime understanding
- 🟢 **LOW**: Verified world structure
- 🟢 **LOW**: DTO compatibility validated

**Risk Reduction**: 2 HIGH + 2 MEDIUM → 4 LOW

---

## Phase 0 → Phase 1 Handoff

**Phase 0 Exit Criteria** (all must pass):
- ✅ All 6 deliverables created
- ✅ Baseline tests passing (816+)
- ✅ No showstoppers identified
- ✅ Reward DTO compatibility validated
- ✅ Test strategy documented
- ✅ Impact radius known

**Phase 1 Entry Confidence**: 🟢 HIGH (from 🟡 MEDIUM)

---

## Optional: Risk Reduction Plus (If Time Permits)

If Phase 0 completes quickly, consider these bonus activities:

### RR7: Create Reward DTO Migration Scaffold (Est: 1 hour)
- Create branch `feature/wp4.1-reward-dtos`
- Scaffold DTO changes (no implementation)
- Create stub tests
- Validate build passes
- **Benefit**: Faster Phase 1 execution

### RR8: Identify Context/Runtime Quick Wins (Est: 30 min)
- Document easy consolidation paths
- Identify any low-hanging fruit (e.g., delete stub)
- Flag any risky consolidations
- **Benefit**: Faster Phase 2 execution

---

## Lessons from WP3.2 Phase 0

WP3.2 had a comprehensive Phase 0 risk assessment (`WP3.2_PHASE0_RISK_ASSESSMENT.md`). Key lessons:

1. ✅ **Risk assessment prevented scope creep** — Identified out-of-scope work early
2. ✅ **Impact analysis reduced surprises** — Test update effort was accurately estimated
3. ✅ **Compatibility validation caught issues** — DTO mismatches found before coding
4. ✅ **Baseline establishment enabled attribution** — Pre-existing issues not blamed on WP

**WP4.1 Phase 0 follows this proven pattern.**

---

**Prepared By**: Claude Code
**Date**: 2025-10-14
**Status**: 🟡 READY FOR EXECUTION
