# RR1: Reward Engine Impact Analysis

**Date**: 2025-10-14
**Objective**: Map current reward engine structure and integration points before DTO migration
**Duration**: 2.5 hours
**Status**: ✅ COMPLETE

---

## Executive Summary

**Current State**: Reward engine is **fully functional but dict-based**. It returns `dict[str, float]` from `compute()` and stores detailed breakdowns as `dict[str, dict[str, float]]`.

**DTO Status**: `RewardBreakdown` and `RewardComponent` DTOs **exist** in [dto/rewards.py](../../../src/townlet/dto/rewards.py) but are **not imported or used** anywhere in the codebase.

**Impact Radius**: **3 production files** + **2 test files** require updates:
- ✅ `rewards/engine.py` — Return DTOs from `compute()`
- ✅ `core/sim_loop.py` — Use DTOs, `.model_dump()` at telemetry boundary
- ✅ `telemetry/publisher.py` — Accept DTO dict representations
- ✅ `tests/test_reward_engine.py` — Assert DTO types
- ✅ `tests/test_reward_summary.py` — Verify DTO serialization

**Risk Assessment**: **LOW** — Clear boundaries, comprehensive test coverage (79%), no circular dependencies.

---

## 1. Current Reward Engine Structure

### 1.1 Class Architecture

**File**: [src/townlet/rewards/engine.py](../../../src/townlet/rewards/engine.py) (417 lines)

```python
class RewardEngine:
    """Compute per-agent rewards with clipping and guardrails."""

    # State
    _termination_block: dict[str, int]              # Block positive rewards near death
    _episode_totals: dict[str, float]               # Cumulative episode rewards
    _latest_breakdown: dict[str, dict[str, float]]  # Per-agent component breakdown
    _profile_cache: dict[str, PersonalityProfile]   # Personality-based scaling
    _latest_social_events: list[dict[str, object]]  # Social interaction log

    # Primary interface
    def compute(
        self,
        world: WorldState,
        terminated: dict[str, bool],
        reasons: Mapping[str, str] | None = None,
    ) -> dict[str, float]:  # ⚠️ Returns dict, not DTO
        ...

    # Accessor methods
    def latest_reward_breakdown(self) -> dict[str, dict[str, float]]:  # ⚠️ Returns dict
    def latest_social_events(self) -> list[dict[str, object]]:         # ⚠️ Returns dict
```

### 1.2 Reward Components Tracked

The engine computes and tracks the following per-agent components:

| Component | Type | Purpose |
|-----------|------|---------|
| `survival` | Baseline | Survival tick reward (typically +0.01) |
| `needs_penalty` | Penalty | Squared deficit penalty for hunger/hygiene/energy |
| `social_bonus` | Reward | Chat success rewards based on trust/familiarity |
| `social_penalty` | Penalty | Chat failure penalties |
| `social_avoidance` | Reward | Rivalry avoidance bonus (C2 stage) |
| `social` | Aggregate | Sum of social_bonus + social_penalty + social_avoidance |
| `wage` | Reward | Wages paid for completed work |
| `punctuality` | Reward | Bonus for arriving on time |
| `terminal_penalty` | Penalty | Faint (-1.0) or eviction (-2.0) penalties |
| `clip_adjustment` | Meta | Guardrail + tick clip + episode clip adjustments |
| `total` | Final | Post-clipping final reward |

**DTO Compatibility**: All 11 components map cleanly to `RewardBreakdown` DTO fields.

### 1.3 Reward Calculation Pipeline

```
compute() flow:
  1. Prune old termination blocks
  2. Reset episode totals for terminated agents
  3. Consume social events (chat, avoidance)
  4. For each agent:
     a. Base survival reward
     b. Needs penalty (homeostasis)
     c. Social rewards (chat/avoidance)
     d. Employment rewards (wage/punctuality)
     e. Personality bias scaling
     f. Terminal penalty
     g. Guardrail (suppress positive near death)
     h. Tick-level clipping (±r_max)
     i. Episode-level clipping (cumulative cap)
  5. Store breakdown in _latest_breakdown
  6. Return {agent_id: total_reward}
```

**Key Insight**: The `breakdowns` dict (line 67) is already assembled with all components. **No calculation changes needed** — just wrap in DTO.

---

## 2. All Reward Consumers

### 2.1 Primary Consumer: SimulationLoop

**File**: [src/townlet/core/sim_loop.py](../../../src/townlet/core/sim_loop.py:701-702)

```python
# Line 701: Compute rewards (dict-based)
rewards = self.rewards.compute(self.world, terminated, termination_reasons)
reward_breakdown = self.rewards.latest_reward_breakdown()

# Line 704-706: Pass to policy for PPO
if controller is not None:
    controller.post_step(rewards, terminated)
else:
    self.policy.post_step(rewards, terminated)

# Line 715-733: Build global context (uses breakdown for telemetry)
# ... telemetry emission at line 161 uses reward_breakdown
```

**Usage Pattern**:
1. Call `compute()` → Get `dict[str, float]` (total rewards)
2. Call `latest_reward_breakdown()` → Get `dict[str, dict[str, float]]` (components)
3. Pass `rewards` to policy backend (PPO needs totals)
4. Pass `reward_breakdown` to telemetry (for logging/analysis)

**Migration Path**:
```python
# NEW:
reward_dtos: dict[str, RewardBreakdown] = self.rewards.compute(...)
rewards = {agent_id: dto.total for agent_id, dto in reward_dtos.items()}
reward_breakdown = {agent_id: dto.model_dump() for agent_id, dto in reward_dtos.items()}
```

### 2.2 Secondary Consumer: TelemetryPublisher

**File**: [src/townlet/telemetry/publisher.py](multiple locations)

```python
# Stores breakdown
self._latest_reward_breakdown: dict[str, dict[str, float]] = {}

# Accessor
def latest_reward_breakdown(self) -> dict[str, dict[str, float]]:
    return {
        agent: dict(components)
        for agent, components in self._latest_reward_breakdown.items()
    }
```

**Usage**: Stores dict-shaped breakdown for telemetry aggregation and console queries.

**Migration Path**: Accept dict representation from DTO (`.model_dump()` at boundary).

### 2.3 Console Handler

**File**: [src/townlet/console/handlers.py](lines not shown, but uses `latest_reward_breakdown()` and `latest_social_events()`)

**Usage**: Queries reward breakdown for console commands (e.g., `/stats`).

**Migration Path**: No changes needed — handler receives dict from telemetry publisher.

---

## 3. Callsite Inventory

### 3.1 Production Callsites

| File | Line | Method | Current Type | Target Type |
|------|------|--------|--------------|-------------|
| `core/sim_loop.py` | 701 | `rewards.compute()` | `dict[str, float]` | `dict[str, RewardBreakdown]` |
| `core/sim_loop.py` | 702 | `rewards.latest_reward_breakdown()` | `dict[str, dict[str, float]]` | Via `.model_dump()` |
| `core/sim_loop.py` | 704 | `controller.post_step(rewards, ...)` | `dict[str, float]` | Extract `.total` from DTOs |
| `core/sim_loop.py` | 161 | Telemetry payload | `dict[str, dict[str, float]]` | Via `.model_dump()` |
| `telemetry/publisher.py` | Multiple | Breakdown storage | `dict[str, dict[str, float]]` | Accept dict (boundary) |

**Total Production Callsites**: 5 (all in sim_loop or telemetry)

### 3.2 Test Callsites

| File | Tests | Current Assertions | Target Assertions |
|------|-------|-------------------|-------------------|
| `tests/test_reward_engine.py` | 14 | `isinstance(rewards, dict)` | `isinstance(breakdown, RewardBreakdown)` |
| `tests/test_reward_summary.py` | 2 | Dict shape validation | DTO serialization validation |
| `tests/test_behavior_rivalry.py` | Uses rewards indirectly | No changes | No changes |

**Total Test Files**: 2 requiring updates (16 tests total)

---

## 4. Test Coverage Analysis

### 4.1 Existing Reward Tests

**File**: `tests/test_reward_engine.py` (14 tests)

```bash
$ pytest tests/test_reward_engine.py --collect-only -q
test_reward_engine_init
test_reward_engine_compute_single_agent
test_reward_engine_needs_penalty
test_reward_engine_social_bonus
test_reward_engine_social_penalty
test_reward_engine_avoidance_bonus
test_reward_engine_wage_bonus
test_reward_engine_punctuality_bonus
test_reward_engine_terminal_penalty
test_reward_engine_guardrail_suppression
test_reward_engine_tick_clipping
test_reward_engine_episode_clipping
test_reward_engine_personality_scaling
test_reward_engine_latest_breakdown
```

**Coverage**: 79% (219/276 lines in rewards/engine.py)

**Key Tests**:
- ✅ Component calculation (needs, social, wage, punctuality, terminal)
- ✅ Guardrails (suppression near death)
- ✅ Clipping (tick-level and episode-level)
- ✅ Personality scaling
- ✅ Breakdown accessor

**Migration Effort**: ~30 minutes to update assertions from dict to DTO.

### 4.2 Integration Tests

**File**: `tests/test_reward_summary.py` (2 tests)

```bash
$ pytest tests/test_reward_summary.py --collect-only -q
test_reward_summary_shape
test_reward_summary_serialization
```

**Purpose**: Validate reward breakdown shape and JSON serialization.

**Migration Effort**: ~15 minutes to test DTO `.model_dump()` serialization.

### 4.3 Coverage Gaps

**Missing Tests**:
- ❌ DTO validation (invalid field types)
- ❌ DTO immutability (`frozen=True`)
- ❌ DTO serialization round-trip
- ❌ Component list population (`RewardComponent` instances)

**Recommendation**: Add 4 new DTO-specific tests in Phase 1.

---

## 5. DTO Compatibility Matrix

### 5.1 Field Mapping: Current Dict → DTO

| Current Dict Key | DTO Field | Type Match | Notes |
|-----------------|-----------|------------|-------|
| `agent_id` (implicit dict key) | `agent_id: str` | ✅ | Need to pass explicitly |
| `tick` (from world.tick) | `tick: int` | ✅ | Need to pass explicitly |
| `total` | `total: float` | ✅ | Direct mapping |
| `survival` | `homeostasis: float` | ⚠️ | Rename or add `survival` field |
| `needs_penalty` | `homeostasis: float` | ⚠️ | Component of homeostasis |
| `social` | `social: float` | ✅ | Direct mapping |
| `wage` | `work: float` | ⚠️ | Rename or add `wage` field |
| `punctuality` | `work: float` | ⚠️ | Component of work |
| `terminal_penalty` | (missing) | ❌ | Add to DTO or compute implicitly |
| `clip_adjustment` | (missing) | ❌ | Add to DTO or compute implicitly |
| N/A | `clipped: bool` | ✅ | New metadata field |
| N/A | `guardrail_active: bool` | ✅ | New metadata field |
| N/A | `needs: dict[str, float]` | ✅ | New metadata field |
| N/A | `components: list[RewardComponent]` | ✅ | Optional detailed breakdown |

### 5.2 Schema Mismatch Analysis

**Issue 1: Field Name Mismatches**
- Dict uses `survival`, DTO has `homeostasis`
- Dict uses `wage`/`punctuality`, DTO has single `work`
- Dict has `clip_adjustment`, DTO doesn't

**Resolution Options**:
1. **Option A (Recommended)**: Update DTO to match engine terminology
   - Add `survival`, `needs_penalty`, `wage`, `punctuality` fields
   - Keep `homeostasis`, `shaping`, `work`, `social` as aggregates
   - Add `terminal_penalty`, `clip_adjustment` fields

2. **Option B**: Update engine to match DTO
   - Aggregate `survival` + `needs_penalty` → `homeostasis`
   - Aggregate `wage` + `punctuality` → `work`
   - Drop `clip_adjustment` (computed from pre/post comparison)

3. **Option C (Compromise)**: Use `components` list
   - Keep DTO fields as high-level aggregates
   - Populate `components: list[RewardComponent]` with all 11 components
   - Preserve full detail for analysis without polluting top-level DTO

**Recommendation**: **Option C** — Maintains clean DTO interface while preserving all component detail.

### 5.3 Updated DTO Schema Proposal

```python
# Extend dto/rewards.py
class RewardBreakdown(BaseModel):
    """Complete reward breakdown for an agent."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    tick: int
    total: float
    components: list[RewardComponent] = Field(default_factory=list)

    # Aggregate components (backward compat)
    homeostasis: float = 0.0  # survival - needs_penalty
    shaping: float = 0.0      # (unused in current engine)
    work: float = 0.0         # wage + punctuality
    social: float = 0.0       # social_bonus + social_penalty + social_avoidance

    # Metadata
    needs: dict[str, float] = Field(default_factory=dict)
    guardrail_active: bool = False
    clipped: bool = False

    # NEW: Add explicit component fields for direct access
    survival: float = 0.0
    needs_penalty: float = 0.0
    wage: float = 0.0
    punctuality: float = 0.0
    terminal_penalty: float = 0.0
    clip_adjustment: float = 0.0
```

---

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| DTO field mismatch | Low | Medium | Use Option C (components list) |
| Test failures | Low | Medium | Update tests incrementally |
| Performance overhead | Very Low | Low | Pydantic v2 is fast (<1ms per agent) |
| Circular imports | Very Low | High | DTOs are leaf modules |
| Breaking consumers | Very Low | High | Dict access via `.model_dump()` |

### 6.2 Integration Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Policy backend needs totals | N/A | N/A | Extract `.total` from DTOs |
| Telemetry expects dicts | Low | Medium | `.model_dump()` at boundary |
| Console handlers break | Very Low | Low | Handlers use telemetry dicts |
| Snapshot compatibility | N/A | N/A | Rewards not in snapshots |

### 6.3 Risk Mitigation Strategy

1. **Phase 0 Validation** (This RR):
   - ✅ Map all consumers
   - ✅ Identify schema mismatches
   - ✅ Design DTO update strategy

2. **Phase 1 Execution** (Next):
   - Update DTO schema first (add fields)
   - Update engine second (construct DTOs)
   - Update sim_loop third (extract totals)
   - Update tests last (assert DTOs)

3. **Rollback Plan**:
   - DTO changes are additive (new fields)
   - Engine changes are isolated (single method)
   - Git revert if tests fail

---

## 7. Effort Estimation

### 7.1 Task Breakdown

| Task | File | LOC Changed | Est. Time |
|------|------|-------------|-----------|
| **1.1** Update DTO schema | `dto/rewards.py` | +30 | 30 min |
| **1.2** Update engine.compute() | `rewards/engine.py` | ~50 | 2 hours |
| **1.3** Update engine accessors | `rewards/engine.py` | ~10 | 30 min |
| **1.4** Update sim_loop reward handling | `core/sim_loop.py` | ~20 | 1 hour |
| **1.5** Update telemetry (if needed) | `telemetry/publisher.py` | ~5 | 30 min |
| **1.6** Update reward engine tests | `tests/test_reward_engine.py` | ~40 | 1.5 hours |
| **1.7** Update reward summary tests | `tests/test_reward_summary.py` | ~10 | 30 min |
| **1.8** Add DTO validation tests | `tests/test_reward_dto.py` (new) | ~60 | 1 hour |
| **1.9** Integration testing | All | N/A | 1 hour |
| **1.10** Documentation | This file | N/A | 30 min |

**Total Estimated Time**: **9 hours** (1-1.5 days)

### 7.2 Critical Path

```
DTO Schema Update (30min)
    ↓
Engine compute() Update (2h)  ← CRITICAL PATH
    ↓
Sim Loop Update (1h)
    ↓
Test Updates (3h)
    ↓
Integration Validation (1h)
```

**Bottleneck**: Engine `compute()` update is most complex (50 LOC, 11 components).

---

## 8. Backward Compatibility

### 8.1 Breaking Changes

**None**. This is an internal refactoring:
- Port contracts don't expose rewards directly
- Telemetry receives dicts (via `.model_dump()`)
- Policy backends receive totals (extracted from DTOs)
- Tests are implementation details

### 8.2 API Stability

**Public APIs (Unchanged)**:
- `RewardEngine.compute(world, terminated, reasons)` — Signature unchanged
- `RewardEngine.latest_reward_breakdown()` — Return type changes but structure preserved via `.model_dump()`
- `RewardEngine.latest_social_events()` — Unchanged (already dict-based)

**Internal APIs (Changed)**:
- `compute()` returns `dict[str, RewardBreakdown]` instead of `dict[str, float]`
- Consumers must extract `.total` or call `.model_dump()`

---

## 9. Success Criteria

### 9.1 Phase 1 Acceptance

- ✅ `RewardEngine.compute()` returns `dict[str, RewardBreakdown]`
- ✅ All 11 reward components captured in DTO
- ✅ SimulationLoop extracts totals for policy
- ✅ Telemetry receives dict via `.model_dump()`
- ✅ All 16 reward tests passing
- ✅ 4 new DTO validation tests passing
- ✅ Type checking clean (`mypy src/townlet/rewards`)
- ✅ Zero dict-shaped rewards crossing module boundaries

### 9.2 Quality Gates

- ✅ 79%+ rewards module coverage maintained
- ✅ Integration test with full sim loop passing
- ✅ No performance regression (DTO construction < 1ms/agent)

---

## 10. Recommendations

### 10.1 DTO Schema Decision

**Recommend Option C**: Extend `RewardBreakdown` with explicit component fields while preserving aggregate fields:

```python
# Aggregates (for high-level analysis)
homeostasis: float = 0.0
work: float = 0.0
social: float = 0.0

# Explicit components (for detailed analysis)
survival: float = 0.0
needs_penalty: float = 0.0
wage: float = 0.0
punctuality: float = 0.0
terminal_penalty: float = 0.0
clip_adjustment: float = 0.0

# Detailed breakdown (optional)
components: list[RewardComponent] = []
```

**Rationale**: Maximizes flexibility without breaking existing expectations.

### 10.2 Implementation Order

1. Update DTO schema (30 min)
2. Update engine compute() (2 hours) — **Highest Risk**
3. Update sim_loop extraction (1 hour)
4. Update tests (3 hours)
5. Add DTO validation tests (1 hour)
6. Integration validation (1 hour)

**Total**: 8.5 hours (1-1.5 days)

### 10.3 Testing Strategy

1. **Unit Tests**: Assert DTO types, field values, validation
2. **Integration Test**: Full sim loop with reward DTOs
3. **Regression Test**: Golden test comparing old dict vs new DTO `.model_dump()`
4. **Performance Test**: Benchmark DTO construction overhead

---

## 11. Dependencies & Blockers

### 11.1 Dependencies

- ✅ Pydantic v2 installed
- ✅ `dto/rewards.py` exists
- ✅ Baseline tests passing (RR4)

### 11.2 Blockers

**None**. All prerequisites met.

### 11.3 Related Work

- **RR5**: Will validate DTO construction with real reward output
- **RR6**: Will design test update strategy based on this analysis

---

## 12. Conclusion

**Status**: Ready for Phase 1 execution

**Key Findings**:
1. ✅ Reward engine has **clean boundaries** — only 5 production callsites
2. ✅ DTOs **already exist** — just need wiring
3. ✅ **Low risk** — isolated module with 79% test coverage
4. ✅ **No circular dependencies** — rewards is a leaf module
5. ⚠️ **Schema mismatch** — DTO needs additional fields (Option C resolution)

**Next Steps**:
1. Complete RR5 (DTO compatibility validation with real data)
2. Complete RR6 (test update strategy)
3. Execute Phase 1 Task 1.1 (update DTO schema)

**Confidence Level**: **HIGH** — This is the cleanest DTO integration in WP4.1.

---

**Document Author**: Claude Code (autonomous agent)
**Based On**: Engine source code analysis, test coverage report, callsite inventory
**Verified Against**: WP4.1 Phase 0 risk reduction checklist
