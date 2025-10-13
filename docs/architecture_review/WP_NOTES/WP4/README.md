# WP4: Policy Training Strategies — Planning Notes

**Status**: Planning
**Start Date**: 2025-10-13
**Dependencies**: WP1 (Ports & Factories) ✅, WP2 (World Modularisation) ✅, WP3 (DTO Boundary) ✅

## Overview

Work Package 4 refactors the monolithic `PolicyTrainingOrchestrator` (984 lines) into composable strategy objects that honor optional Torch dependencies and consume typed DTOs from WP3.

## Goals

1. **Extract training strategies** — BC, PPO, Anneal into separate strategy classes (<200 LOC each)
2. **Create orchestrator façade** — Thin composition layer (<150 LOC)
3. **Isolate shared services** — Rollout capture, replay datasets, promotion eval
4. **DTO alignment** — Training results use Pydantic DTOs
5. **Optional dependencies** — Torch can be absent for replay/analysis workflows
6. **Maintain CLI compatibility** — Existing scripts continue to work

## Key Metrics

- **Current**: 1 file, 984 lines, mixed responsibilities
- **Target**: ~8 files, strategies <200 LOC, façade <150 LOC
- **Code reduction**: ~40% through extraction and decomposition

## Documents in this Directory

- **README.md** (this file) — Overview and navigation
- **orchestrator_analysis.md** — Current code analysis and responsibility mapping
- **extraction_plan.md** — Detailed extraction strategy and sequencing
- **approach.md** — Implementation phases and decision log
- **strategy_interface.md** — Strategy protocol design
- **dto_design.md** — Training result DTO schemas
- **torch_isolation.md** — Optional dependency handling strategy
- **testing_strategy.md** — Test migration and coverage plan

## Current State Analysis

### PolicyTrainingOrchestrator Breakdown

| Responsibility | Lines | Complexity | Torch Dep |
|---|---|---|---|
| PPO training loop | ~470 | High | Yes |
| Anneal scheduling | ~90 | Medium | Via BC/PPO |
| BC training | ~40 | Low | Yes |
| Rollout capture | ~50 | Low | No |
| Replay datasets | ~30 | Low | No |
| Promotion eval | ~40 | Low | No |
| Utilities/helpers | ~260 | Low-Med | Mixed |

### Dependencies

```
PolicyTrainingOrchestrator
├── WP1 Ports (SimulationLoop via factory) ✅
├── WP2 World (via SimulationLoop) ✅
├── WP3 DTOs (will consume for telemetry/obs) ✅
├── BCTrainer (torch-dependent)
├── PolicyRuntime (torch-dependent)
├── ReplayDataset (torch-free)
├── RolloutBuffer (torch-free)
├── PromotionManager (torch-free)
└── TrajectoryService (torch-free)
```

## Success Criteria

- [ ] `PolicyTrainingOrchestrator` <150 LOC (façade only)
- [ ] BCStrategy <100 LOC
- [ ] PPOStrategy <200 LOC
- [ ] AnnealStrategy <150 LOC
- [ ] All strategies implement `TrainingStrategy` protocol
- [ ] Import `townlet.policy.training` succeeds without Torch
- [ ] CLI maintains backwards compatibility (JSON output unchanged)
- [ ] All existing tests pass with new structure
- [ ] `pytest -q`, `ruff`, `mypy` clean
- [ ] ADR-004 authored and merged

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| PPO loop too complex to extract | High | Incremental extraction with helper functions |
| Torch dependency leakage | Medium | Centralized torch guards + import-time checks |
| DTO schema mismatches | Medium | Golden test fixtures + schema validation |
| CLI breaking changes | High | Compatibility shims + `.model_dump()` |
| Test coverage gaps | Medium | Strategy unit tests + integration smoke tests |

## Timeline Estimate

**Total: 20-30 hours** (2.5-4 full work days)

### Phase Breakdown

- **Phase 1: Analysis & Design** (2-3 hours)
  - Code analysis
  - Strategy interface design
  - DTO schema design

- **Phase 2: Skeleton & Services** (3-4 hours)
  - Package structure
  - Shared services extraction
  - DTO definitions

- **Phase 3: BCStrategy** (2-3 hours)
  - Simplest strategy, establish pattern

- **Phase 4: AnnealStrategy** (3-4 hours)
  - Medium complexity, baseline tracking

- **Phase 5: PPOStrategy** (5-7 hours)
  - Most complex, large loop extraction

- **Phase 6: Orchestrator Façade** (2-3 hours)
  - Thin composition layer

- **Phase 7: Tests & CLI** (4-5 hours)
  - Test migration
  - CLI updates

- **Phase 8: Documentation** (2 hours)
  - ADR-004
  - Update architecture docs

## Next Steps

1. ✅ Create WP4 planning directory
2. Analyze current orchestrator (→ `orchestrator_analysis.md`)
3. Design strategy interface (→ `strategy_interface.md`)
4. Design training DTOs (→ `dto_design.md`)
5. Create extraction plan (→ `extraction_plan.md`)
6. Document torch isolation approach (→ `torch_isolation.md`)
7. Begin implementation

## Related Documents

- `docs/architecture_review/WP_TASKINGS/WP4.md` — Official tasking document
- `src/townlet/policy/training_orchestrator.py` — Current monolith (984 lines)
- `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md` — Port foundation
- `docs/architecture_review/ADR/ADR-003 - DTO Boundary.md` — DTO patterns to follow
