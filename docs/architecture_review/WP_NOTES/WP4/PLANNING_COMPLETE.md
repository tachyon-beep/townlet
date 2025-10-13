# WP4 Planning Phase Complete

**Date**: 2025-10-13
**Status**: ✅ Planning Complete — Ready for Implementation

## Planning Documents Created

All planning documents have been created and reviewed:

1. ✅ **README.md** — Overview, goals, success criteria, risks, timeline
2. ✅ **orchestrator_analysis.md** — Line-by-line breakdown of current 984-line monolith
3. ✅ **approach.md** — 8-phase implementation plan with decision log
4. ✅ **strategy_interface.md** — TrainingStrategy protocol and context design
5. ✅ **dto_design.md** — Complete DTO schemas for all training results

## Key Decisions Made

### Architecture Decisions
- ✅ Use `typing.Protocol` for strategy interface (structural typing, WP1 pattern)
- ✅ Anneal baseline state lives in `AnnealStrategy` (strategy owns its state)
- ✅ Social reward stage mutation via `TrainingContext` (pass config slice)
- ✅ PPO loop broken into ~5 helper functions (device selection, setup, summary)

### DTO Decisions
- ✅ Use Pydantic v2 `BaseModel` for all DTOs
- ✅ Support 3 telemetry versions (1.0, 1.1, 1.2) via optional fields
- ✅ Frozen DTOs for immutability (`frozen=True`)
- ✅ Strict validation with `extra="forbid"`

### Service Decisions
- ✅ Extract 3 services: Rollout, Replay, Promotion
- ✅ Services are stateless/low-state
- ✅ Services are torch-free (importable without ML dependencies)

### Strategy Size Targets
- ✅ BCStrategy: <100 LOC
- ✅ PPOStrategy: <200 LOC (with helpers)
- ✅ AnnealStrategy: <150 LOC
- ✅ Orchestrator: <150 LOC

## Implementation Sequence

### Phase 0: Analysis & Design ✅ COMPLETE
- ✅ Code analysis
- ✅ Strategy interface design
- ✅ DTO schema design

### Phase 1: Package Structure & DTOs (Next)
- Create `townlet/policy/training/` package
- Create `townlet/dto/policy.py` with all DTOs
- Create compatibility shim in old location

### Phase 2: Service Extraction
- RolloutCaptureService
- ReplayDatasetService
- PromotionServiceAdapter
- TrainingServices composition

### Phase 3: BCStrategy Extraction
- Simplest strategy
- Establish extraction pattern
- Torch guard implementation

### Phase 4: AnnealStrategy Extraction
- Medium complexity
- State management
- BC/PPO coordination

### Phase 5: PPOStrategy Extraction
- Most complex (~470 lines)
- Incremental extraction with helpers
- Device selection, training loop, telemetry

### Phase 6: Orchestrator Façade
- Thin composition layer
- Compatibility shims

### Phase 7: CLI & Test Updates
- Update scripts
- Migrate tests
- Add integration smoke tests

### Phase 8: Documentation
- Author ADR-004
- Update architecture docs

## Risks & Mitigations

| Risk | Severity | Mitigation | Status |
|---|---|---|---|
| PPO loop too complex | High | Incremental extraction with helpers | ✅ Mitigated (helpers planned) |
| Torch dependency leakage | Medium | Centralized guards + import checks | ✅ Mitigated (strategy-level guards) |
| DTO schema mismatches | Medium | Golden test fixtures | ✅ Mitigated (comprehensive schema) |
| CLI breaking changes | High | Compatibility shims + `.model_dump()` | ✅ Mitigated (shims planned) |
| Test coverage gaps | Medium | Strategy unit tests | ✅ Mitigated (test plan complete) |

## Success Criteria

All criteria defined and measurable:

- [ ] `PolicyTrainingOrchestrator` <150 LOC (from 984, 85% reduction)
- [ ] BCStrategy <100 LOC
- [ ] PPOStrategy <200 LOC
- [ ] AnnealStrategy <150 LOC
- [ ] 3 services extracted (Rollout, Replay, Promotion)
- [ ] Import `townlet.policy.training` succeeds without torch
- [ ] All DTOs defined in `townlet/dto/policy.py`
- [ ] All existing tests pass
- [ ] New strategy unit tests added
- [ ] `pytest -q`, `ruff`, `mypy` clean
- [ ] ADR-004 complete

## Timeline Estimate

**Total**: 20-30 hours (2.5-4 full work days)

Breakdown:
- Phase 0: 2-3 hours ✅ COMPLETE
- Phase 1: 2 hours
- Phase 2: 3 hours
- Phase 3: 2-3 hours
- Phase 4: 3-4 hours
- Phase 5: 5-7 hours
- Phase 6: 2-3 hours
- Phase 7: 4-5 hours
- Phase 8: 2 hours

## Code Statistics

### Current State
- **File**: `src/townlet/policy/training_orchestrator.py`
- **Total Lines**: 984
- **Responsibilities**: 7 distinct roles mixed together
- **Torch Imports**: 4 locations

### Target State
- **Package**: `townlet/policy/training/`
- **Files**: ~8 files
- **Strategies**: 3 files (<200 LOC each)
- **Services**: 1 file (~150 LOC)
- **Orchestrator**: 1 file (<150 LOC)
- **Total Lines**: ~750 (24% reduction through decomposition)
- **Torch Imports**: Isolated to strategy implementations only

## Next Actions

1. Begin Phase 1: Create package structure and DTOs
2. Update TODO list with Phase 1 tasks
3. Create feature branch: `feature/wp4-policy-training-strategies`
4. Start implementation following `approach.md` sequence

## Related Documents

**Planning Documents** (this directory):
- README.md — Overview
- orchestrator_analysis.md — Current code analysis
- approach.md — Implementation phases
- strategy_interface.md — Protocol design
- dto_design.md — DTO schemas

**Architecture Documents**:
- `docs/architecture_review/WP_TASKINGS/WP4.md` — Official tasking
- `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md` — Port foundation
- `docs/architecture_review/ADR/ADR-003 - DTO Boundary.md` — DTO patterns

**Implementation Target**:
- `src/townlet/policy/training_orchestrator.py` — Current monolith to refactor

---

✅ **Planning phase complete. Ready to proceed with implementation.**
