# Extraction Strategy & Test Plan

**Purpose**: Final risk reduction document for WP4 implementation
**Status**: Complete
**Updated**: 2025-10-13

## Overview

This document synthesizes findings from the three risk reduction research documents (`ppo_loop_structure.md`, `torch_dependency_map.md`, `dto_validation.md`) into a concrete extraction strategy with test plans for each phase.

## Related Documents

- `orchestrator_analysis.md` — Line-by-line breakdown of 984-line monolith
- `approach.md` — 8-phase implementation plan
- `strategy_interface.md` — TrainingStrategy protocol design
- `dto_design.md` — Complete DTO schemas
- `ppo_loop_structure.md` — PPO loop extraction plan
- `torch_dependency_map.md` — Torch isolation strategy
- `dto_validation.md` — DTO completeness validation
- `PLANNING_COMPLETE.md` — Readiness summary

## Extraction Boundaries

### File-Level Boundaries

```
Current (1 file):
  training_orchestrator.py (984 lines)

Target (8+ files):
  townlet/policy/training/
    __init__.py
    orchestrator.py           # Façade (<150 LOC)
    contexts.py               # TrainingContext, AnnealContext, PPOState
    strategies/
      __init__.py
      base.py                 # TrainingStrategy protocol
      bc.py                   # BCStrategy (<100 LOC)
      ppo.py                  # PPOStrategy (~200 LOC)
      anneal.py               # AnnealStrategy (<150 LOC)
    services/
      __init__.py
      replay.py               # ReplayDatasetService
      rollout.py              # RolloutCaptureService
      promotion.py            # PromotionServiceAdapter
  townlet/dto/
    policy.py                 # All training DTOs
```

---

### Method-Level Boundaries

#### From Orchestrator → Services (Torch-Free)

| Current Method | Lines | Target Service | New Method |
|----------------|-------|----------------|------------|
| `run_replay()` | 119-125 | `ReplayDatasetService` | `summarize_sample()` |
| `run_replay_batch()` | 127-132 | `ReplayDatasetService` | `summarize_batch()` |
| `run_replay_dataset()` | 134-145 | `ReplayDatasetService` | `summarize_dataset()` |
| `build_replay_dataset()` | 958-964 | `ReplayDatasetService` | `build_dataset()` |
| `capture_rollout()` | 147-199 | `RolloutCaptureService` | `capture()` |
| `run_rollout_ppo()` | 201-231 | `RolloutCaptureService` | Helper (delegates to PPO) |
| `_record_promotion_evaluation()` | 858-895 | `PromotionServiceAdapter` | `record_evaluation()` |
| `_resolve_replay_manifest()` | 934-956 | `ReplayDatasetService` | `resolve_manifest()` |

#### From Orchestrator → BCStrategy (Torch-Dependent)

| Current Method | Lines | Target Strategy | New Method |
|----------------|-------|-----------------|------------|
| `run_bc_training()` | 237-273 | `BCStrategy` | `run()` |
| `_load_bc_dataset()` | 233-235 | `BCStrategy` | Internal helper |

#### From Orchestrator → PPOStrategy (Torch-Dependent)

| Current Method | Lines | Target Strategy | New Method | Notes |
|----------------|-------|-----------------|------------|-------|
| `run_ppo()` | 369-840 | `PPOStrategy` | `run()` | Main training loop |
| `_ppo_ops()` | 72-84 | `PPOStrategy` | `_ppo_ops()` | Lazy torch import helper |
| `build_policy_network()` | 966-981 | `PPOStrategy` | `_build_network()` | Part of setup |
| `_summarise_batch()` | 924-932 | `PPOStrategy` | `_summarize_batch()` | Conflict stats |

**PPO Helper Functions** (extracted from run_ppo):
- `_select_device()` — Lines 415-453 (~40 LOC)
- `_setup_training()` — Lines 454-465 (~20 LOC)
- `_setup_logging()` — Lines 484-516 (~20 LOC)
- `_resolve_dataset()` — Lines 382-405 (~20 LOC)
- `_build_epoch_summary_core()` — Lines 705-733 (~30 LOC)
- `_add_telemetry_v1_1()` — Lines 739-762 (~25 LOC)
- `_add_anneal_context()` — Lines 764-808 (~45 LOC)
- `_add_baseline_metrics()` — Lines 809-817 (~10 LOC)

#### From Orchestrator → AnnealStrategy (Torch-Dependent)

| Current Method | Lines | Target Strategy | New Method |
|----------------|-------|-----------------|------------|
| `run_anneal()` | 275-367 | `AnnealStrategy` | `run()` |
| `evaluate_anneal_results()` | 842-852 | `AnnealStrategy` | `evaluate_results()` |
| `current_anneal_ratio()` | 109-110 | `AnnealStrategy` | Property accessor |
| `set_anneal_ratio()` | 112-117 | `AnnealStrategy` | Property setter |
| `last_anneal_status` | 855-856 | `AnnealStrategy` | Property accessor |
| `_select_social_reward_stage()` | 897-914 | `AnnealStrategy` | `_select_reward_stage()` |
| `_apply_social_reward_stage()` | 916-922 | `TrainingContext` | Via context mutation |

---

## Extraction Sequence

### Phase 1: Package Structure & DTOs (~2 hours)

**Goals**:
- Create package structure
- Implement all DTOs
- No code movement yet (preparation only)

**Tasks**:
1. Create `townlet/policy/training/` package with empty `__init__.py`
2. Create `townlet/dto/policy.py` with all DTOs:
   - `TrainingResultBase`
   - `BCTrainingResultDTO`
   - `PPOTrainingResultDTO`
   - `AnnealStageResultDTO`
   - `AnnealSummaryDTO`
3. Create `townlet/policy/training/contexts.py`:
   - `TrainingContext`
   - `AnnealContext`
   - `PPOState`
4. Add unit tests for DTOs (`tests/dto/test_policy_dtos.py`)
5. Add compatibility import shim in old location (if needed)

**Success Criteria**:
- [ ] All DTOs pass validation with sample data
- [ ] `pytest tests/dto/test_policy_dtos.py` passes
- [ ] `mypy townlet/dto/policy.py` clean
- [ ] No existing code broken (DTOs not used yet)

**Test Plan**:
```python
# tests/dto/test_policy_dtos.py

def test_bc_result_dto_validation():
    """Verify BCTrainingResultDTO validates correctly."""
    dto = BCTrainingResultDTO(
        mode="bc",
        manifest="/path/to/manifest.json",
        accuracy=0.93,
        loss=0.15,
        learning_rate=1e-3,
        batch_size=32,
        epochs=10,
    )
    assert dto.accuracy == 0.93
    assert dto.schema_version == "1.0.0"

def test_ppo_result_dto_optional_fields():
    """Verify PPOTrainingResultDTO handles optional fields."""
    minimal = PPOTrainingResultDTO(
        epoch=1.0, updates=10.0, transitions=100.0,
        loss_policy=0.1, loss_value=0.2, loss_entropy=0.01, loss_total=0.29,
        clip_fraction=0.1, adv_mean=0.0, adv_std=1.0,
        grad_norm=1.0, kl_divergence=0.01, lr=1e-3, steps=100.0,
    )
    assert minimal.epoch_duration_sec is None  # Optional v1.1 field

def test_anneal_summary_dto_wraps_stages():
    """Verify AnnealSummaryDTO structure."""
    stages = [
        AnnealStageResultDTO(cycle=0, mode="bc", accuracy=0.93, passed=True),
        AnnealStageResultDTO(cycle=0, mode="ppo", loss_total=0.12),
    ]
    summary = AnnealSummaryDTO(
        stages=stages, status="PASS", dataset_label="rollout_001", baselines={}
    )
    assert len(summary.stages) == 2
    assert summary.status == "PASS"
```

---

### Phase 2: Service Extraction (~3 hours)

**Goals**:
- Extract torch-free services
- Services testable independently
- Orchestrator still works (delegates to services)

**Tasks**:
1. Create `townlet/policy/training/services/replay.py`:
   - `ReplayDatasetService` class
   - Methods: `summarize_sample()`, `summarize_batch()`, `summarize_dataset()`, `build_dataset()`, `resolve_manifest()`
2. Create `townlet/policy/training/services/rollout.py`:
   - `RolloutCaptureService` class
   - Methods: `capture()`, `build_dataset_from_buffer()`
3. Create `townlet/policy/training/services/promotion.py`:
   - `PromotionServiceAdapter` class (wraps `PromotionManager`)
   - Methods: `record_evaluation()`, `update_metrics()`, `set_candidate_metadata()`
4. Create `townlet/policy/training/services/__init__.py`:
   - `TrainingServices` composition class
   - Factory method: `TrainingServices.from_config()`
5. Update orchestrator to delegate to services
6. Add unit tests for each service

**Success Criteria**:
- [ ] All 3 services importable without torch
- [ ] `import townlet.policy.training.services` works without torch installed
- [ ] Orchestrator delegates to services (all existing tests pass)
- [ ] Service unit tests pass independently
- [ ] `pytest tests/policy/training/services/` passes

**Test Plan**:
```python
# tests/policy/training/services/test_replay_service.py

def test_replay_service_import_without_torch(monkeypatch):
    """Verify service imports without torch."""
    monkeypatch.setattr("townlet.policy.models.torch_available", lambda: False)
    from townlet.policy.training.services import ReplayDatasetService
    # Should not raise

def test_replay_service_summarize_batch():
    """Verify batch summarization."""
    service = ReplayDatasetService(config)
    batch = create_test_batch()  # Fixture
    summary = service.summarize_batch(batch, batch_index=1)
    assert "batch_size" in summary
    assert "feature_dim" in summary

def test_rollout_service_capture():
    """Verify rollout capture."""
    service = RolloutCaptureService(config)
    buffer = service.capture(ticks=10, auto_seed_agents=True)
    assert buffer.tick_count == 10
    assert len(buffer.frames) > 0
```

---

### Phase 3: BCStrategy Extraction (~2-3 hours)

**Goals**:
- Extract simplest strategy first
- Establish extraction pattern
- Verify torch guard works

**Tasks**:
1. Create `townlet/policy/training/strategies/base.py`:
   - `TrainingStrategy` protocol
2. Create `townlet/policy/training/strategies/bc.py`:
   - `BCStrategy` class implementing protocol
   - Move `run_bc_training()` → `BCStrategy.run()`
   - Move `_load_bc_dataset()` → `BCStrategy._load_dataset()`
   - Return `BCTrainingResultDTO` instead of dict
   - Add duration timer
3. Update orchestrator to delegate to `BCStrategy`
4. Add compatibility shim: `run_bc_training()` calls `BCStrategy.run().model_dump()`
5. Add unit tests for BCStrategy

**Success Criteria**:
- [ ] `BCStrategy` importable without torch (guard at run() entry)
- [ ] `BCStrategy.run()` returns `BCTrainingResultDTO`
- [ ] Orchestrator `run_bc_training()` still returns dict (compatibility)
- [ ] All existing BC tests pass
- [ ] New BCStrategy unit tests pass

**Test Plan**:
```python
# tests/policy/training/strategies/test_bc_strategy.py

def test_bc_strategy_requires_torch(monkeypatch):
    """Verify BCStrategy fails gracefully without torch."""
    monkeypatch.setattr("townlet.policy.models.torch_available", lambda: False)
    strategy = BCStrategy(config, services)
    with pytest.raises(TorchNotAvailableError, match="PyTorch is required"):
        strategy.run(manifest=Path("test_manifest.json"))

def test_bc_strategy_returns_dto():
    """Verify BCStrategy returns typed DTO."""
    strategy = BCStrategy(config, services)
    result = strategy.run(manifest=Path("test_manifest.json"))
    assert isinstance(result, BCTrainingResultDTO)
    assert result.mode == "bc"
    assert 0.0 <= result.accuracy <= 1.0

def test_bc_strategy_tracks_duration():
    """Verify duration is tracked."""
    strategy = BCStrategy(config, services)
    result = strategy.run(manifest=Path("test_manifest.json"))
    assert result.duration_sec is not None
    assert result.duration_sec > 0.0
```

---

### Phase 4: AnnealStrategy Extraction (~3-4 hours)

**Goals**:
- Extract medium-complexity strategy
- Coordinate BC/PPO sub-strategies
- Return enhanced DTO (not just stage list)

**Tasks**:
1. Create `townlet/policy/training/strategies/anneal.py`:
   - `AnnealStrategy` class
   - Move `run_anneal()` → `AnnealStrategy.run()`
   - Move `evaluate_anneal_results()` → `AnnealStrategy.evaluate_results()`
   - Move anneal ratio/status properties
   - Return `AnnealSummaryDTO` instead of list
2. Update orchestrator to delegate to `AnnealStrategy`
3. Add compatibility shim for CLI
4. Add unit tests

**Success Criteria**:
- [ ] `AnnealStrategy` coordinates BC/PPO strategies
- [ ] Returns `AnnealSummaryDTO` with status, baselines, promotion metadata
- [ ] Orchestrator shim provides list compatibility
- [ ] All existing anneal tests pass
- [ ] New AnnealStrategy unit tests pass

**Test Plan**:
```python
# tests/policy/training/strategies/test_anneal_strategy.py

def test_anneal_strategy_delegates_to_sub_strategies():
    """Verify anneal coordinates BC and PPO."""
    bc_strategy = mock.Mock(spec=BCStrategy)
    ppo_strategy = mock.Mock(spec=PPOStrategy)
    strategy = AnnealStrategy(config, services, bc_strategy, ppo_strategy)

    bc_strategy.run.return_value = BCTrainingResultDTO(...)
    ppo_strategy.run.return_value = PPOTrainingResultDTO(...)

    result = strategy.run(dataset_config=config)
    assert isinstance(result, AnnealSummaryDTO)
    assert len(result.stages) == 2
    bc_strategy.run.assert_called_once()
    ppo_strategy.run.assert_called_once()

def test_anneal_strategy_evaluates_status():
    """Verify anneal evaluates PASS/HOLD/FAIL."""
    strategy = AnnealStrategy(config, services, bc_strategy, ppo_strategy)
    result = strategy.run(dataset_config=config)
    assert result.status in ("PASS", "HOLD", "FAIL")

def test_anneal_strategy_tracks_baselines():
    """Verify baselines are tracked across runs."""
    strategy = AnnealStrategy(config, services, bc_strategy, ppo_strategy)
    result1 = strategy.run(dataset_config=config)
    result2 = strategy.run(dataset_config=config)
    assert "rollout_001" in result2.baselines
```

---

### Phase 5: PPOStrategy Extraction (~5-7 hours)

**Goals**:
- Extract most complex strategy
- Incremental helper extraction
- Maintain green tests throughout

**Tasks** (Incremental):

#### 5.1: Extract Setup Helpers (~2 hours)
1. Create `PPOStrategy` class skeleton in `strategies/ppo.py`
2. Move `run_ppo()` → `PPOStrategy.run()` (no refactoring yet)
3. Extract 4 setup helpers from inside `run()`:
   - `_resolve_dataset()` — Lines 382-405
   - `_select_device()` — Lines 415-453
   - `_setup_training()` — Lines 454-465 (includes build_policy_network)
   - `_setup_logging()` — Lines 484-516
4. Call helpers from `run()` main body
5. Run tests after each extraction

**Success Criteria**:
- [ ] `PPOStrategy.run()` reduced from 472 to ~370 lines
- [ ] All existing PPO tests pass
- [ ] Helpers are private methods (`_` prefix)

#### 5.2: Extract Summary Builders (~2 hours)
1. Extract 4 summary builders from inside `run()`:
   - `_build_epoch_summary_core()` — Lines 705-733
   - `_add_telemetry_v1_1()` — Lines 739-762
   - `_add_anneal_context()` — Lines 764-808
   - `_add_baseline_metrics()` — Lines 809-817
2. Call builders to construct `epoch_summary`
3. Return `PPOTrainingResultDTO(**epoch_summary)` instead of dict
4. Run tests after each extraction

**Success Criteria**:
- [ ] `PPOStrategy.run()` reduced to ~285 lines
- [ ] Returns `PPOTrainingResultDTO` instead of dict
- [ ] All tests pass

#### 5.3: Final Integration (~1-2 hours)
1. Add `run_rollout_ppo()` convenience method
2. Add torch guard at `run()` entry
3. Add local torch imports (lines 407-409)
4. Move `_ppo_ops()` helper
5. Move `_summarize_batch()` helper
6. Update orchestrator to delegate to `PPOStrategy`
7. Add compatibility shim
8. Add unit tests

**Success Criteria**:
- [ ] `PPOStrategy.run()` at ~200 LOC (including helpers)
- [ ] Torch guard at entry, local imports after guard
- [ ] All existing PPO tests pass
- [ ] New PPOStrategy unit tests pass

**Test Plan**:
```python
# tests/policy/training/strategies/test_ppo_strategy.py

def test_ppo_strategy_requires_torch(monkeypatch):
    """Verify PPOStrategy fails gracefully without torch."""
    monkeypatch.setattr("townlet.policy.models.torch_available", lambda: False)
    strategy = PPOStrategy(config, services)
    with pytest.raises(TorchNotAvailableError, match="PyTorch is required"):
        strategy.run(dataset_config=config, epochs=1)

def test_ppo_strategy_returns_dto():
    """Verify PPOStrategy returns typed DTO."""
    strategy = PPOStrategy(config, services)
    result = strategy.run(dataset_config=config, epochs=1)
    assert isinstance(result, PPOTrainingResultDTO)
    assert result.epoch == 1.0
    assert result.telemetry_version >= 1.0

def test_ppo_strategy_device_selection():
    """Verify device selection logic."""
    strategy = PPOStrategy(config, services)
    result = strategy.run(dataset_config=config, device_str="cpu")
    # Verify CPU was used (can check via telemetry or logs)

def test_ppo_strategy_with_anneal_context():
    """Verify anneal context fields are populated."""
    strategy = PPOStrategy(config, services)
    context = TrainingContext(
        config=config,
        services=services,
        anneal_context=AnnealContext(...),
    )
    strategy.prepare(context)
    result = strategy.run(dataset_config=config, epochs=1)
    assert result.anneal_cycle is not None
    assert result.anneal_loss_flag is not None
```

---

### Phase 6: Orchestrator Façade (~2-3 hours)

**Goals**:
- Thin composition layer
- Compatibility shims for CLI
- Property accessors for state

**Tasks**:
1. Refactor `PolicyTrainingOrchestrator` in `orchestrator.py`:
   - Keep `__init__` (instantiates strategies and services)
   - Replace method bodies with strategy delegation
   - Add compatibility shims: `dict` → DTO → `dict` (via `.model_dump()`)
2. Keep property accessors:
   - `transitions`, `trajectory` → `_trajectory_service`
   - `current_anneal_ratio()`, `last_anneal_status` → `_anneal_strategy`
   - `promotion` → `_services.promotion`
3. Keep `run()` entry point (delegates to strategies based on config)
4. Add typed variants for new callers:
   - `run_bc_training_typed() -> BCTrainingResultDTO`
   - `run_ppo_typed() -> PPOTrainingResultDTO`
   - `run_anneal_typed() -> AnnealSummaryDTO`
5. Update imports in `__init__.py`

**Success Criteria**:
- [ ] `PolicyTrainingOrchestrator` <150 LOC
- [ ] All existing tests pass (compatibility shims work)
- [ ] New typed methods available for type-safe callers
- [ ] `pytest tests/policy/test_training_orchestrator.py` passes

**Test Plan**:
```python
# tests/policy/test_training_orchestrator.py

def test_orchestrator_bc_compatibility():
    """Verify orchestrator returns dict for BC (CLI compatibility)."""
    orch = PolicyTrainingOrchestrator(config)
    result = orch.run_bc_training(manifest=Path("test_manifest.json"))
    assert isinstance(result, dict)
    assert "accuracy" in result
    assert "mode" in result

def test_orchestrator_bc_typed():
    """Verify orchestrator typed method returns DTO."""
    orch = PolicyTrainingOrchestrator(config)
    result = orch.run_bc_training_typed(manifest=Path("test_manifest.json"))
    assert isinstance(result, BCTrainingResultDTO)

def test_orchestrator_delegates_to_strategies():
    """Verify orchestrator delegates to strategies."""
    orch = PolicyTrainingOrchestrator(config)
    # Mock strategies to verify delegation
    orch._bc_strategy = mock.Mock()
    orch._bc_strategy.run.return_value = BCTrainingResultDTO(...)
    orch.run_bc_training(manifest=Path("test.json"))
    orch._bc_strategy.run.assert_called_once()
```

---

### Phase 7: CLI & Test Updates (~4-5 hours)

**Goals**:
- Update training scripts to use new structure
- Migrate or update integration tests
- Add smoke tests

**Tasks**:
1. Update `scripts/run_training.py`:
   - Import from new package
   - Use orchestrator (no changes needed if compatibility shims work)
2. Update `scripts/run_bc_training.py`, `scripts/run_ppo_training.py`:
   - Use orchestrator facade
3. Migrate integration tests:
   - Update imports
   - Verify compatibility shims
4. Add smoke tests:
   - `test_training_package_import_without_torch()`
   - `test_strategy_protocol_compliance()`
   - `test_end_to_end_bc_training()`
   - `test_end_to_end_ppo_training()`
   - `test_end_to_end_anneal()`
5. Update `tests/test_policy_training_integration.py`

**Success Criteria**:
- [ ] All CLI scripts work unchanged
- [ ] All integration tests pass
- [ ] Smoke tests verify torch isolation
- [ ] `pytest tests/` passes (full test suite)

**Test Plan**:
```python
# tests/integration/test_training_smoke.py

def test_training_package_import_without_torch(monkeypatch):
    """Verify package can be imported without torch."""
    monkeypatch.setattr("townlet.policy.models.torch_available", lambda: False)
    from townlet.policy.training import TrainingServices
    from townlet.policy.training.services import ReplayDatasetService
    # Should not raise

def test_strategy_protocol_compliance():
    """Verify all strategies implement protocol."""
    from townlet.policy.training.strategies import BCStrategy, PPOStrategy, AnnealStrategy
    from townlet.policy.training.strategies.base import TrainingStrategy
    assert isinstance(BCStrategy(config, services), TrainingStrategy)
    assert isinstance(PPOStrategy(config, services), TrainingStrategy)
    assert isinstance(AnnealStrategy(config, services, bc, ppo), TrainingStrategy)

def test_end_to_end_bc_training():
    """Smoke test for BC training."""
    orch = PolicyTrainingOrchestrator(config)
    result = orch.run_bc_training(manifest=test_manifest)
    assert isinstance(result, dict)
    assert result["accuracy"] > 0.0

def test_end_to_end_ppo_training():
    """Smoke test for PPO training."""
    orch = PolicyTrainingOrchestrator(config)
    result = orch.run_ppo(dataset_config=test_config, epochs=1)
    assert isinstance(result, dict)
    assert result["epoch"] == 1.0
```

---

### Phase 8: Documentation (~2 hours)

**Goals**:
- Author ADR-004
- Update architecture docs
- Update CLAUDE.md

**Tasks**:
1. Create `docs/architecture_review/ADR/ADR-004 - Training Strategy Pattern.md`:
   - Context, Decision, Consequences
   - Implementation details
   - Torch isolation strategy
2. Update `docs/architecture_review/ARCHITECTURE_REVIEW_2.md`:
   - Add WP4 summary
   - Update module map
3. Update `CLAUDE.md`:
   - Update policy training section
   - Document new package structure
   - Update import examples
4. Archive WP4 planning docs in `docs/architecture_review/WP_NOTES/WP4/`

**Success Criteria**:
- [ ] ADR-004 complete and reviewed
- [ ] Architecture docs updated
- [ ] CLAUDE.md reflects new structure
- [ ] Planning docs archived

---

## Test Coverage Strategy

### Unit Test Coverage Targets

| Module | Target Coverage | Critical Paths |
|--------|-----------------|----------------|
| `townlet/dto/policy.py` | >95% | Field validation, optional fields |
| `services/replay.py` | >90% | Batch summarization, manifest resolution |
| `services/rollout.py` | >85% | Rollout capture, buffer building |
| `services/promotion.py` | >80% | Evaluation recording, metadata |
| `strategies/bc.py` | >85% | Torch guard, dataset loading, DTO return |
| `strategies/ppo.py` | >80% | Torch guard, device selection, helper delegation |
| `strategies/anneal.py` | >85% | Stage coordination, status evaluation |
| `orchestrator.py` | >90% | Strategy delegation, compatibility shims |

### Integration Test Coverage

- [ ] Full BC training run (manifest → DTO)
- [ ] Full PPO training run (dataset → DTO)
- [ ] Full anneal run (schedule → summary DTO)
- [ ] Rollout + PPO (capture → train)
- [ ] BC → PPO anneal sequence
- [ ] Promotion evaluation flow

### Torch Isolation Tests

- [ ] Import services without torch
- [ ] Import strategies without torch (no error until run)
- [ ] Strategy torch guards trigger correctly
- [ ] Local torch imports work after guards

---

## Risk Management

### High-Risk Extractions

| Extraction | Risk Level | Mitigation |
|------------|------------|------------|
| PPO mini-batch loop | **High** | Keep inline, extract only preprocessing |
| Anneal return type change | **High** | Compatibility shims in orchestrator |
| Torch import leakage | **Medium** | Import tests + code review |
| DTO validation breaks legacy logs | **Medium** | Use lenient parsing in tests |

### Mitigation Strategies

1. **Incremental extraction**: Never move more than one method at a time
2. **Run tests after each move**: Catch regressions immediately
3. **Keep helpers inline initially**: Extract only when stable
4. **Use compatibility shims**: CLI doesn't need to change
5. **Golden test fixtures**: Capture current output before changes

---

## Rollback Strategy

If any phase fails:

1. **Revert last commit**: `git revert HEAD`
2. **Run test suite**: Verify revert restored green state
3. **Analyze failure**: Review logs, test output, type errors
4. **Adjust approach**: Modify extraction plan or defer risky section
5. **Retry with smaller scope**: Extract smaller piece if needed

---

## Success Metrics

### Quantitative

- [ ] `PolicyTrainingOrchestrator`: 984 → <150 LOC (85% reduction)
- [ ] `BCStrategy`: <100 LOC
- [ ] `PPOStrategy`: <200 LOC (with helpers)
- [ ] `AnnealStrategy`: <150 LOC
- [ ] Total LOC: ~750 (24% reduction from decomposition)
- [ ] Test coverage: >85% on all modules
- [ ] No test regressions: All existing tests pass

### Qualitative

- [ ] Torch isolation works (import without torch succeeds for services)
- [ ] DTOs provide type safety (mypy clean)
- [ ] Strategies are independently testable (mock dependencies)
- [ ] CLI unchanged (compatibility shims work)
- [ ] Code is more maintainable (smaller, focused modules)

---

## Timeline

| Phase | Estimated Time | Critical Path |
|-------|----------------|---------------|
| Phase 0: Planning | 3 hours | ✅ Complete |
| Phase 1: DTOs | 2 hours | Low risk |
| Phase 2: Services | 3 hours | Medium risk |
| Phase 3: BCStrategy | 2-3 hours | Low risk |
| Phase 4: AnnealStrategy | 3-4 hours | Medium risk |
| Phase 5: PPOStrategy | 5-7 hours | **High risk** (critical path) |
| Phase 6: Orchestrator | 2-3 hours | Medium risk |
| Phase 7: CLI/Tests | 4-5 hours | Medium risk |
| Phase 8: Docs | 2 hours | Low risk |
| **Total** | **23-30 hours** | **3-4 work days** |

---

## Next Actions

1. ✅ Complete Phase 0 (this document)
2. ⏳ Begin Phase 1: Create package structure and implement DTOs
3. ⏳ Proceed sequentially through phases 2-8
4. ⏳ Run full test suite after each phase
5. ⏳ Commit after each green phase (atomic commits)
6. ⏳ Update PLANNING_COMPLETE.md when done

---

## Conclusion

**Phase 0 Complete** — All risk reduction research documents created:
- ✅ `orchestrator_analysis.md` — Monolith breakdown
- ✅ `ppo_loop_structure.md` — PPO extraction plan
- ✅ `torch_dependency_map.md` — Torch isolation strategy
- ✅ `dto_validation.md` — DTO completeness validation
- ✅ `extraction_strategy.md` — This document (final synthesis)

**Readiness**: 🟢 **Ready to proceed with Phase 1 implementation**

**Confidence Level**: High
- Current code already follows torch isolation best practices
- DTO schemas validated against all outputs
- Extraction boundaries clearly defined
- Test strategy covers all risk areas
- Incremental approach minimizes regression risk

**Key Success Factors**:
1. Incremental extraction (one method at a time)
2. Run tests after every change
3. Keep PPO batch loop inline (too complex to extract)
4. Use compatibility shims for CLI (zero breaking changes)
5. Extract helpers only after main body is stable
