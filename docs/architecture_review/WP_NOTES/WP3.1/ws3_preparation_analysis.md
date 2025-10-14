# WS3 ObservationBuilder Retirement - Preparation Analysis

**Date**: 2025-10-13
**Status**: Ready for execution
**Risk Level**: MEDIUM - requires careful migration with parity testing

---

## Executive Summary

ObservationBuilder (1059 LOC) needs to be retired as part of WP3 Stage 6. The class is **currently still in active use** through `WorldObservationService` which wraps it. The DTO observation path exists and is being tested, but ObservationBuilder has not yet been fully replaced.

### Current Architecture Flow

```
WorldContext.observe()
    → observation_service.build_batch()  # WorldObservationService
        → ObservationBuilder.build_batch()  # LEGACY - 1059 lines
    → build_observation_envelope()  # Wraps legacy output in DTO
```

The DTO envelope is built **around** legacy observations, not instead of them.

---

## Reference Inventory (40 references across 15 files)

### 1. Core Implementation (2 files)
- `src/townlet/observations/builder.py` - **1059 lines** - The class itself
- `src/townlet/observations/__init__.py` - Factory export

### 2. Runtime Usage (3 files)
- `src/townlet/world/observations/service.py:21` - **WorldObservationService wraps ObservationBuilder**
- `src/townlet/world/grid.py` - Legacy world state reference (likely in comments/docstrings)
- `src/townlet/config/observations.py:49` - Config docstring reference

### 3. Test Files (9 files)
#### Direct builder tests:
- `tests/test_observation_builder.py` - 7 test functions
  - `test_observation_builder_hybrid_map_and_features`
  - `test_observation_ctx_reset_releases_slot`
  - `test_observation_rivalry_features_reflect_conflict`
  - `test_observation_queue_and_reservation_flags`
  - `test_observation_respawn_resets_features`
  - `test_ctx_reset_flag_on_teleport_and_possession`
  - `test_personality_channels_append_when_enabled`

- `tests/test_observation_builder_full.py` - Full variant tests
- `tests/test_observation_builder_compact.py` - Compact variant tests
- `tests/test_observation_builder_parity.py` - Parity checks
- `tests/test_observations_social_snippet.py` - Social feature tests

#### Parity/integration tests using builder:
- `tests/policy/test_dto_ml_smoke.py:42` - **DTO vs legacy parity check**
- `tests/test_telemetry_adapter_smoke.py:32` - Telemetry smoke test
- `tests/test_observation_baselines.py:33` - Baseline capture
- `tests/test_embedding_allocator.py:69` - Embedding tests
- `tests/test_training_replay.py:208,268` - Replay buffer tests

### 4. Tooling (1 file)
- `scripts/profile_observation_tensor.py:25,28` - Performance profiling

### 5. Guard Test (1 file)
- `tests/core/test_no_legacy_observation_usage.py:57-58` - **Whitelist check**

---

## Key Findings

### 1. **WorldObservationService is NOT DTO-native**
The service at `src/townlet/world/observations/service.py` still uses ObservationBuilder internally:

```python
class WorldObservationService(ObservationServiceProtocol):
    def __init__(self, *, config: SimulationConfig) -> None:
        self._builder = observations.create_observation_builder(config=config)

    def build_batch(self, world, terminated):
        return self._builder.build_batch(world, terminated)
```

This means **all observations currently flow through ObservationBuilder**, even when they're subsequently wrapped in DTOs.

### 2. **DTO Envelope Factory Wraps Legacy Output**
`src/townlet/world/dto/factory.py:build_observation_envelope()` accepts the **output of ObservationBuilder** and converts it to DTO format:

```python
def build_observation_envelope(
    *,
    observations: Mapping[str, Mapping[str, Any]],  # <-- Legacy builder output
    ...
) -> ObservationEnvelope:
    for agent_id in agent_ids:
        payload = observations.get(agent_id, {})
        map_tensor = _coerce_ndarray(payload.get("map"))
        features = _coerce_ndarray(payload.get("features"))
        metadata = _to_builtin(payload.get("metadata", {}))
```

### 3. **Parity Tests Validate DTO Against Legacy**
`tests/policy/test_dto_ml_smoke.py` **compares** DTO features against legacy ObservationBuilder output:

```python
observation_builder = ObservationBuilder(config=config)
for _ in range(5):
    envelope = loop.step().envelope  # DTO
    legacy_batch = observation_builder.build_batch(adapter, {})  # Legacy
    # Compare them
    np.testing.assert_allclose(dto_features, legacy_features, atol=1e-6)
```

This confirms DTO observations are built from legacy observations, not independently.

### 4. **Feature Coverage Analysis**
ObservationBuilder provides:
- **Map tensors**: 3 variants (full, hybrid, compact) with channel encoding
- **Feature vectors**: 40+ features including needs, wallet, time, shift state, landmarks, rivalry, queues, personality
- **Social snippets**: Top friends/rivals with embeddings
- **Metadata**: Variant info, channel names, feature names, social context

The DTO schema (`src/townlet/world/dto/observation.py`) includes:
- `AgentObservationDTO`: map, features, metadata, needs, wallet, job, personality, queue_state
- All fields populated from legacy builder output

**Gap Analysis**: DTO schema appears complete, but construction logic is in factory, not service.

---

## Migration Path Analysis

### Option A: Rewrite WorldObservationService (RECOMMENDED)
**Complexity**: HIGH
**Risk**: MEDIUM
**Impact**: Complete replacement

Reimplement `WorldObservationService.build_batch()` to construct observation data **directly** without ObservationBuilder:

```python
class WorldObservationService(ObservationServiceProtocol):
    def build_batch(self, world, terminated):
        # Build map tensors directly from world adapter
        # Build feature vectors directly from agent snapshots
        # Return dict matching current builder output format
```

**Pros**:
- Clean break from legacy
- Performance opportunity (remove intermediate dict step)
- Aligns with DTO-first architecture

**Cons**:
- Must replicate 1059 lines of encoding logic
- High risk of subtle feature calculation bugs
- Extensive parity testing required

### Option B: Keep WorldObservationService as Compatibility Layer (INTERIM)
**Complexity**: LOW
**Risk**: LOW
**Impact**: Moves ObservationBuilder into observations package as private

Move ObservationBuilder to `src/townlet/world/observations/_legacy_builder.py`:
- Rename to `_LegacyObservationBuilder`
- Keep WorldObservationService wrapper
- Update guard test whitelist
- Plan for eventual replacement in WP4

**Pros**:
- Minimal immediate risk
- Preserves all existing parity
- Isolates legacy code clearly

**Cons**:
- Doesn't truly retire ObservationBuilder
- Defers architectural debt
- Still have 1059 lines of legacy code

### Option C: Build DTO Observations Directly in WorldContext (IDEAL)
**Complexity**: VERY HIGH
**Risk**: HIGH
**Impact**: Major architectural shift

Eliminate observation service layer entirely:
- WorldContext.observe() builds DTO envelope directly
- Extract feature calculation into pure functions
- Use helper modules for map/social/landmark encoding

**Pros**:
- True DTO-first architecture
- Potential performance gains
- Cleaner separation of concerns

**Cons**:
- Requires rewriting all encoding logic
- Large changeset, high merge conflict risk
- Would need new comprehensive test suite

---

## Critical Dependencies & Blockers

### 1. Test Migration Strategy
All 9 test files using ObservationBuilder need migration:
- **Builder-specific tests** → Convert to DTO envelope tests
- **Parity tests** → Update to compare DTO fields directly
- **Integration tests** → Use DTO envelopes instead of builder

### 2. Training/Replay Compatibility
`tests/test_training_replay.py` uses ObservationBuilder for replay buffers:
```python
builder = ObservationBuilder(config)
observations = builder.build_batch(...)
# Store observations in replay buffer
```

**Blocker**: Replay buffer format may depend on builder output structure.
**Resolution Required**: Verify DTO envelope compatibility with replay storage.

### 3. Profiling Script
`scripts/profile_observation_tensor.py` profiles ObservationBuilder performance:
- Used for benchmarking observation encoding
- May be referenced in performance monitoring

**Resolution**: Update script to profile DTO envelope construction, or mark deprecated.

### 4. Guard Test Whitelist
`tests/core/test_no_legacy_observation_usage.py` has whitelist:
```python
WHITELIST_PATHS = {
    (SRC_ROOT / "core" / "sim_loop.py").resolve(),
    (SRC_ROOT / "config" / "observations.py").resolve(),
}
```

Currently **no** source files in whitelist use ObservationBuilder (only config docstring).
After migration, ensure no new violations.

---

## Risk Assessment

### HIGH RISK
1. **Feature parity regression**: Missing or incorrect feature calculation in new implementation
2. **Observation variant handling**: Compact/hybrid/full variants have different encoding logic
3. **Social snippet calculation**: Complex embedding and aggregation logic
4. **Replay buffer compatibility**: Stored observations may depend on exact format

### MEDIUM RISK
1. **Performance regression**: DTO construction may be slower than legacy
2. **Test coverage gaps**: New implementation may miss edge cases
3. **Embedding allocator integration**: ctx_reset_flag and slot management
4. **Personality channel toggles**: Feature flag interactions

### LOW RISK
1. **Guard test violations**: Easy to detect and fix
2. **Import errors**: Will fail immediately in tests
3. **Type checking**: Mypy will catch protocol violations

---

## Recommended Execution Plan

### Phase 1: Analysis & Preparation (CURRENT)
- ✅ Complete reference inventory
- ✅ Analyze current DTO construction flow
- ✅ Identify all test dependencies
- ✅ Document migration options

### Phase 2: Choose Migration Strategy
**Recommendation**: Option A (Rewrite WorldObservationService)

**Rationale**:
- WP3 Stage 6 goal is **complete** ObservationBuilder retirement
- Option B defers the problem
- Option C is too risky for current timeline
- Option A balances risk and architectural goals

### Phase 3: Implementation Steps
1. **Create new observation encoding module** (`src/townlet/world/observations/encoders.py`)
   - Extract map encoding logic (full/hybrid/compact variants)
   - Extract feature vector encoding (40+ features)
   - Extract social snippet encoding
   - Pure functions taking world adapter and config

2. **Rewrite WorldObservationService**
   - Use encoder functions to build observation dicts
   - Match exact output format of current ObservationBuilder
   - Preserve all variant handling

3. **Parallel parity testing**
   - Run both old and new side-by-side
   - Assert exact numerical equality
   - Test all variants and edge cases

4. **Migrate tests incrementally**
   - Convert builder tests to encoder tests
   - Update parity tests to use new service
   - Ensure 100% test pass rate before deletion

5. **Delete ObservationBuilder**
   - Remove `src/townlet/observations/builder.py`
   - Update `__init__.py`
   - Verify guard test passes

6. **Update tooling**
   - Migrate profiling script to DTO path
   - Update any documentation references

### Phase 4: Validation
- Full pytest suite (no skips)
- Parity harness (`test_sim_loop_dto_parity.py`)
- ML smoke test (`test_dto_ml_smoke.py`)
- Performance benchmark comparison
- Manual simulation smoke test

---

## Open Questions

1. **Q**: Are there external tools/scripts depending on ObservationBuilder output format?
   **A**: Need to check `scripts/` directory and any external integrations

2. **Q**: Does replay buffer storage format depend on exact builder dict structure?
   **A**: Check `tests/test_training_replay.py` and `RolloutBuffer` implementation

3. **Q**: Are observation baselines (`test_observation_baselines.py`) stored files that will break?
   **A**: Check if baselines are committed or generated on-the-fly

4. **Q**: Can we extract and unit test encoding functions before integrating?
   **A**: Yes - recommended to build encoders as pure functions first

5. **Q**: What's the performance baseline for ObservationBuilder.build_batch()?
   **A**: Run `scripts/profile_observation_tensor.py` before migration

---

## Success Criteria

### Must Have
- ✅ Zero references to `ObservationBuilder` in `src/` (except guard test)
- ✅ All tests passing with new implementation
- ✅ DTO parity tests passing (numerical equality)
- ✅ ML smoke test passing (identical model outputs)
- ✅ Guard test passing (`test_no_legacy_observation_usage`)

### Should Have
- ✅ Performance neutral or improved (within 10%)
- ✅ Test coverage ≥ 95% on new encoding modules
- ✅ Documentation updated (architecture diagrams, ADRs)
- ✅ Profiling script updated or marked deprecated

### Nice to Have
- Performance improvement >10%
- Reduced DTO envelope construction overhead
- Clearer separation of encoding concerns

---

## Next Steps

1. **Decision Point**: Choose migration strategy (recommend Option A)
2. **Spike**: Extract one encoder function (e.g., map encoding) and validate approach
3. **Build**: Implement full encoder module with parity tests
4. **Migrate**: Update WorldObservationService to use encoders
5. **Test**: Run full validation suite
6. **Delete**: Remove ObservationBuilder and update guard tests
7. **Document**: Update WP3 status and ADRs

---

## Appendix: File Modification Checklist

### Files to Modify
- [ ] `src/townlet/world/observations/service.py` - Rewrite build_batch()
- [ ] `src/townlet/observations/__init__.py` - Remove ObservationBuilder export
- [ ] `tests/test_observation_builder*.py` (4 files) - Convert to DTO tests
- [ ] `tests/test_observations_social_snippet.py` - Update to DTO
- [ ] `tests/test_embedding_allocator.py` - Update to DTO
- [ ] `tests/test_training_replay.py` - Update to DTO
- [ ] `tests/test_telemetry_adapter_smoke.py` - Update to DTO
- [ ] `tests/test_observation_baselines.py` - Update to DTO
- [ ] `tests/policy/test_dto_ml_smoke.py` - Remove legacy comparison
- [ ] `scripts/profile_observation_tensor.py` - Update or deprecate
- [ ] `src/townlet/config/observations.py` - Update docstring
- [ ] `tests/core/test_no_legacy_observation_usage.py` - Verify passes

### Files to Create
- [ ] `src/townlet/world/observations/encoders/map.py` - Map tensor encoding
- [ ] `src/townlet/world/observations/encoders/features.py` - Feature vector encoding
- [ ] `src/townlet/world/observations/encoders/social.py` - Social snippet encoding
- [ ] `tests/world/observations/test_encoders.py` - Encoder unit tests

### Files to Delete
- [ ] `src/townlet/observations/builder.py` - **1059 lines to remove**

---

**Estimated Effort**: 2-3 days (assuming no major blockers)
**Estimated Risk**: MEDIUM (high complexity, good test coverage mitigates)
**Blocking**: None (WS1 and WS2 complete)
