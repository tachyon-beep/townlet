# WP4 Implementation Approach

**Updated**: 2025-10-13
**Status**: Planning

## Overview

This document outlines the phased approach to refactoring `PolicyTrainingOrchestrator` from a 984-line monolith into composable strategy objects.

## Guiding Principles

1. **Incremental extraction** — Extract one strategy at a time, maintain green tests
2. **Services first** — Extract stateless helpers before stateful strategies
3. **Simple to complex** — BC → Anneal → PPO (ascending complexity)
4. **Torch isolation** — Keep orchestrator and services importable without torch
5. **DTO boundaries** — All strategy results use Pydantic DTOs
6. **Backwards compatibility** — CLI behavior unchanged (via compatibility shims)

## Phase Breakdown

### Phase 0: Analysis & Design (2-3 hours)

**Goal**: Understand current code, design target architecture

**Deliverables**:
- ✅ `orchestrator_analysis.md` — Line-by-line breakdown
- `strategy_interface.md` — TrainingStrategy protocol
- `dto_design.md` — Training result DTO schemas
- `torch_isolation.md` — Optional dependency strategy
- `extraction_plan.md` — Step-by-step extraction sequence

**Risks**: None (pure analysis)

**Decision Points**:
- Should strategies be protocols or abstract base classes? → **Protocols** (structural typing, WP1 pattern)
- Where to put anneal baseline state? → **AnnealStrategy** (strategy owns its state)
- How to handle social reward stage mutation? → **TrainingContext** (pass config slice, allow mutation)

### Phase 1: Package Structure & DTOs (2 hours)

**Goal**: Create skeleton structure and DTO definitions

**Tasks**:
1. Create `townlet/policy/training/` package
   ```
   townlet/policy/training/
     __init__.py
     orchestrator.py      # Stub façade
     contexts.py          # TrainingContext, PPOState, AnnealContext
     services.py          # Service stubs
     strategies/
       __init__.py
       base.py            # TrainingStrategy protocol
       bc.py              # Empty BCStrategy
       ppo.py             # Empty PPOStrategy
       anneal.py          # Empty AnnealStrategy
   ```

2. Create `townlet/dto/policy.py`
   ```python
   class BCTrainingResultDTO(BaseModel): ...
   class PPOTrainingResultDTO(BaseModel): ...
   class AnnealStageResultDTO(BaseModel): ...
   class AnnealSummaryDTO(BaseModel): ...
   class TrainingResultDTO(BaseModel): ...  # Union type
   ```

3. Update `townlet/policy/training_orchestrator.py` to import from new location (compatibility shim)

**Acceptance**:
- [ ] Import `townlet.policy.training` succeeds
- [ ] Import `townlet.dto.policy` succeeds
- [ ] Existing tests still import successfully (via shim)

**Risks**: Low (structural only, no behavior changes)

### Phase 2: Service Extraction (3 hours)

**Goal**: Extract stateless/low-state helpers into services

**Tasks**:

#### 2.1: RolloutCaptureService
Extract `capture_rollout()` (lines 147-199)

```python
class RolloutCaptureService:
    def __init__(self, config: SimulationConfig): ...
    def capture(
        self,
        ticks: int,
        auto_seed_agents: bool = False,
        output_dir: Path | None = None,
        prefix: str = "rollout_sample",
        compress: bool = True,
    ) -> RolloutBuffer: ...
```

**Tests**: `tests/policy/training/test_services.py::test_rollout_capture_*`

#### 2.2: ReplayDatasetService
Extract:
- `_summarise_batch()` → `summarise_batch()`
- `_resolve_replay_manifest()` → `resolve_manifest()`
- `build_replay_dataset()` → `build_dataset()`
- `run_replay()`, `run_replay_batch()`, `run_replay_dataset()` → Service methods

```python
class ReplayDatasetService:
    @staticmethod
    def summarise_batch(batch: ReplayBatch, batch_index: int) -> dict[str, float]: ...

    @staticmethod
    def resolve_manifest(manifest: Path | str | None, config: SimulationConfig) -> Path: ...

    @staticmethod
    def build_dataset(config: ReplayDatasetConfig | Path | str | None, sim_config: SimulationConfig) -> ReplayDataset: ...
```

**Tests**: `tests/policy/training/test_services.py::test_replay_*`

#### 2.3: PromotionServiceAdapter
Extract `_record_promotion_evaluation()` (lines 854-896)

```python
class PromotionServiceAdapter:
    def __init__(self, config: SimulationConfig): ...

    def record_evaluation(
        self,
        status: str,
        results: list[dict[str, object]],
    ) -> None: ...

    @property
    def pass_streak(self) -> int: ...

    @property
    def candidate_ready(self) -> bool: ...
```

**Tests**: `tests/policy/training/test_services.py::test_promotion_*`

#### 2.4: TrainingServices Composition
```python
@dataclass
class TrainingServices:
    rollout_capture: RolloutCaptureService
    replay_dataset: ReplayDatasetService
    promotion: PromotionServiceAdapter

    @classmethod
    def from_config(cls, config: SimulationConfig) -> "TrainingServices": ...
```

**Acceptance**:
- [ ] Services extracted and unit tested
- [ ] Orchestrator uses services (temporary delegation)
- [ ] All existing tests pass

**Risks**: Low (stateless helpers, clear boundaries)

### Phase 3: BCStrategy Extraction (2-3 hours)

**Goal**: Extract simplest strategy to establish pattern

**Tasks**:

#### 3.1: Define BCStrategy
Extract `run_bc_training()` (lines 233-273)

```python
class BCStrategy:
    """Behaviour cloning training strategy."""

    name: ClassVar[str] = "bc"
    requires_torch: ClassVar[bool] = True

    def __init__(self, config: SimulationConfig, services: TrainingServices): ...

    def prepare(self, context: TrainingContext) -> None: ...

    def run(
        self,
        manifest: Path | None = None,
        config: BCTrainingParams | None = None,
    ) -> BCTrainingResultDTO: ...
```

#### 3.2: Torch Guard
```python
def run(self, ...) -> BCTrainingResultDTO:
    if not torch_available():
        raise TorchNotAvailableError(
            "PyTorch is required for BC training. Install with: pip install townlet[ml]"
        )
    # ... rest of implementation
```

#### 3.3: Return DTO
```python
return BCTrainingResultDTO(
    mode="bc",
    manifest=str(manifest_path),
    accuracy=float(metrics["accuracy"]),
    loss=float(metrics["loss"]),
    learning_rate=float(metrics.get("learning_rate", 0.0)),
    batch_size=int(metrics.get("batch_size", 0)),
    epochs=int(metrics.get("epochs", 0)),
    duration_sec=float(metrics.get("duration_sec", 0.0)),
)
```

#### 3.4: Update Orchestrator
```python
class PolicyTrainingOrchestrator:
    def __init__(self, config: SimulationConfig, *, services: TrainingServices | None = None):
        self.config = config
        self.services = services or TrainingServices.from_config(config)
        self._bc_strategy = BCStrategy(config, self.services)

    def run_bc_training(self, ...) -> dict[str, float]:
        result = self._bc_strategy.run(...)
        return result.model_dump()  # Compatibility shim
```

**Acceptance**:
- [ ] BCStrategy implements TrainingStrategy protocol
- [ ] Returns BCTrainingResultDTO
- [ ] Orchestrator delegates to strategy
- [ ] Tests pass (using compatibility shim)
- [ ] Torch guard works (skip test if torch missing)

**Risks**: Low (small, self-contained method)

### Phase 4: AnnealStrategy Extraction (3-4 hours)

**Goal**: Extract medium-complexity strategy with state management

**Tasks**:

#### 4.1: Define AnnealContext
```python
@dataclass
class AnnealContext:
    cycle: int
    stage: str
    dataset_label: str
    bc_accuracy: float | None
    bc_threshold: float
    bc_passed: bool
    loss_baseline: float | None
    queue_events_baseline: float | None
    queue_intensity_baseline: float | None
    loss_tolerance: float
    queue_tolerance: float
```

#### 4.2: Define AnnealStrategy
Extract `run_anneal()` (lines 275-367)

```python
class AnnealStrategy:
    """Anneal scheduling strategy coordinating BC/PPO transitions."""

    name: ClassVar[str] = "anneal"
    requires_torch: ClassVar[bool] = True  # Indirect (uses BC/PPO)

    def __init__(
        self,
        config: SimulationConfig,
        services: TrainingServices,
        bc_strategy: BCStrategy,
        ppo_strategy: PPOStrategy,
    ): ...

    def run(
        self,
        dataset_config: ReplayDatasetConfig | None = None,
        in_memory_dataset: InMemoryReplayDataset | None = None,
        log_dir: Path | None = None,
        bc_manifest: Path | None = None,
    ) -> AnnealSummaryDTO: ...

    def evaluate_results(self, stages: list[AnnealStageResultDTO]) -> str: ...
```

#### 4.3: State Management
```python
def __init__(self, ...):
    self._anneal_context: AnnealContext | None = None
    self._baselines: dict[str, dict[str, float]] = {}
    self._anneal_ratio: float | None = None
    self._last_status: str | None = None
```

#### 4.4: Return DTO
```python
return AnnealSummaryDTO(
    stages=[AnnealStageResultDTO(...) for ...],
    status=status,  # PASS/HOLD/FAIL
    dataset_label=dataset_key,
    baselines=self._baselines,
)
```

**Acceptance**:
- [ ] AnnealStrategy implements TrainingStrategy protocol
- [ ] Returns AnnealSummaryDTO
- [ ] Coordinates BC/PPO strategies correctly
- [ ] Baseline tracking preserved
- [ ] Threshold evaluation matches original logic
- [ ] Tests pass

**Risks**: Medium (stateful, coordination logic)

### Phase 5: PPOStrategy Extraction (5-7 hours)

**Goal**: Extract most complex strategy (~470 lines)

**Approach**: Incremental extraction with helper functions

#### 5.1: Define PPOState
```python
@dataclass
class PPOState:
    step: int = 0
    learning_rate: float = 1e-3
    log_stream_offset: int = 0
    cycle_id: int = -1
```

#### 5.2: Extract Helper Functions (internal to PPOStrategy)
- `_ensure_finite()` — NaN/Inf validation
- `_update_advantage_health()` — Advantage std tracking
- `_open_log()` — Log file rotation
- `_select_device()` — CUDA device selection with memory check
- `_build_epoch_summary()` — Metric aggregation

#### 5.3: Define PPOStrategy
Extract `run_ppo()` (lines 369-840)

```python
class PPOStrategy:
    """PPO training strategy."""

    name: ClassVar[str] = "ppo"
    requires_torch: ClassVar[bool] = True

    def __init__(self, config: SimulationConfig, services: TrainingServices):
        self.config = config
        self.services = services
        self.state = PPOState()
        self._anneal_context: AnnealContext | None = None

    def prepare(self, context: TrainingContext) -> None:
        """Set anneal context for current run."""
        self._anneal_context = context.anneal_context

    def run(
        self,
        dataset_config: ReplayDatasetConfig | None = None,
        epochs: int = 1,
        log_path: Path | None = None,
        log_frequency: int = 1,
        max_log_entries: int | None = None,
        in_memory_dataset: InMemoryReplayDataset | None = None,
        device_str: str | None = None,
    ) -> PPOTrainingResultDTO: ...

    def run_rollout_ppo(self, ticks: int, ...) -> PPOTrainingResultDTO: ...
```

#### 5.4: Incremental Extraction Steps
1. Extract device selection → `_select_device()` helper
2. Extract setup (policy/optimizer) → `_setup_training()` helper
3. Extract epoch loop → Keep as main `run()` body
4. Extract mini-batch loop → `_train_mini_batch()` helper (if too large)
5. Extract telemetry aggregation → `_build_epoch_summary()` helper
6. Extract log rotation → `_open_log()` helper

#### 5.5: Return DTO
```python
return PPOTrainingResultDTO(
    epoch=epoch + 1,
    updates=mini_batch_updates,
    transitions=transitions_processed,
    loss_policy=averaged_metrics["policy_loss"],
    loss_value=averaged_metrics["value_loss"],
    loss_entropy=averaged_metrics["entropy"],
    loss_total=averaged_metrics["total_loss"],
    clip_fraction=averaged_metrics["clip_frac"],
    # ... ~30 more fields
)
```

**Acceptance**:
- [ ] PPOStrategy implements TrainingStrategy protocol
- [ ] Returns PPOTrainingResultDTO
- [ ] Device selection works (CUDA with best memory, CPU fallback)
- [ ] Training loop preserves all metrics
- [ ] Anneal context integration works
- [ ] Log rotation works
- [ ] Tests pass (mark slow, skip if torch missing)

**Risks**: High (very complex, large surface area)

**Mitigation**: Break into helper functions, test incrementally

### Phase 6: Orchestrator Façade (2-3 hours)

**Goal**: Create thin composition layer

#### 6.1: New Orchestrator Structure
```python
class PolicyTrainingOrchestrator:
    """Thin façade coordinating training strategies."""

    def __init__(
        self,
        config: SimulationConfig,
        *,
        services: TrainingServices | None = None,
    ):
        self.config = config
        self.services = services or TrainingServices.from_config(config)

        # Strategy instances
        self._bc_strategy = BCStrategy(config, self.services)
        self._ppo_strategy = PPOStrategy(config, self.services)
        self._anneal_strategy = AnnealStrategy(
            config,
            self.services,
            self._bc_strategy,
            self._ppo_strategy,
        )

    def run(self) -> TrainingResultDTO:
        """Entry point based on config.training.source."""
        mode = self.config.training.source
        if mode == "bc":
            return self.run_bc_training()
        if mode == "anneal":
            return self.run_anneal()
        raise NotImplementedError(f"Training mode '{mode}' not supported")

    def run_bc_training(self, ...) -> BCTrainingResultDTO:
        """Run BC training strategy."""
        return self._bc_strategy.run(...)

    def run_ppo(self, ...) -> PPOTrainingResultDTO:
        """Run PPO training strategy."""
        return self._ppo_strategy.run(...)

    def run_anneal(self, ...) -> AnnealSummaryDTO:
        """Run anneal scheduling strategy."""
        return self._anneal_strategy.run(...)

    # Compatibility shims for existing code
    def current_anneal_ratio(self) -> float | None:
        return self._anneal_strategy.anneal_ratio

    # ... other compatibility methods
```

#### 6.2: Compatibility Layer
Keep old method signatures but delegate to strategies:

```python
def run_bc_training(self, ...) -> dict[str, float]:
    """BC training (compatibility shim)."""
    result = self._bc_strategy.run(...)
    return result.model_dump()
```

**Acceptance**:
- [ ] Orchestrator <150 LOC
- [ ] Delegates to strategies cleanly
- [ ] Compatibility shims preserve old API
- [ ] Tests pass

**Risks**: Low (composition only)

### Phase 7: CLI & Test Updates (4-5 hours)

**Goal**: Update scripts and tests to use new structure

#### 7.1: CLI Updates
Update `scripts/run_training.py`:

```python
# Before
orchestrator = PolicyTrainingOrchestrator(config)
result = orchestrator.run_bc_training()  # Returns dict
print(json.dumps(result, indent=2))

# After (DTO-aware)
orchestrator = PolicyTrainingOrchestrator(config)
result = orchestrator.run_bc_training()  # Returns BCTrainingResultDTO
print(result.model_dump_json(indent=2))  # Or keep dict via shim
```

#### 7.2: Test Updates
Migrate tests to use strategies directly:

**Before**:
```python
def test_bc_training(orchestrator):
    result = orchestrator.run_bc_training(manifest=...)
    assert result["accuracy"] > 0.9
```

**After**:
```python
def test_bc_strategy(config, services):
    strategy = BCStrategy(config, services)
    result = strategy.run(manifest=...)
    assert result.accuracy > 0.9
    assert isinstance(result, BCTrainingResultDTO)
```

#### 7.3: Integration Tests
Add smoke tests with stubbed strategies:

```python
def test_orchestrator_with_fake_strategies():
    """Verify orchestrator wiring with fake strategy implementations."""

    class FakeBCStrategy:
        def run(self, **kwargs):
            return BCTrainingResultDTO(
                mode="bc",
                accuracy=0.95,
                loss=0.05,
                # ... minimal fields
            )

    orchestrator = PolicyTrainingOrchestrator(config)
    orchestrator._bc_strategy = FakeBCStrategy()
    result = orchestrator.run_bc_training()
    assert result.accuracy == 0.95
```

**Acceptance**:
- [ ] CLI scripts updated
- [ ] JSON output unchanged (via `.model_dump()`)
- [ ] Tests migrated to new structure
- [ ] New strategy unit tests added
- [ ] Integration smoke tests added
- [ ] All tests pass

**Risks**: Medium (many test files to update)

### Phase 8: Documentation (2 hours)

**Goal**: Author ADR-004 and update architecture docs

#### 8.1: ADR-004
```markdown
# ADR 0004: Policy Training Strategies

## Status
Accepted

## Context
[Explain monolithic orchestrator problem]

## Decision
[Document strategy pattern, DTO boundaries, torch isolation]

## Consequences
[List benefits and trade-offs]
```

#### 8.2: Update Architecture Review
- Update ARCHITECTURE_REVIEW_2.md §6.4 Policy section
- Add training strategy diagram
- Document new package structure

#### 8.3: Update Developer Docs
- Add training strategy guide
- Document torch optional dependency pattern
- Update CLI usage examples

**Acceptance**:
- [ ] ADR-004 authored and merged
- [ ] Architecture review updated
- [ ] Developer docs updated
- [ ] WP4 marked complete in WP_TASKINGS/WP4.md

**Risks**: None (documentation only)

## Decision Log

### Why protocols instead of ABC?
**Decision**: Use `typing.Protocol` with `@runtime_checkable`
**Rationale**: Consistent with WP1 port pattern; structural typing more flexible; no inheritance required

### Where to store anneal baseline state?
**Decision**: Inside `AnnealStrategy`
**Rationale**: Strategy owns its state; baselines are anneal-specific; keeps orchestrator stateless

### How to handle config mutations (social reward stage)?
**Decision**: Pass config slice to strategies, allow mutation via `TrainingContext`
**Rationale**: Matches existing behavior; config is mutable singleton; document side effect

### Should PPO loop be broken into more helpers?
**Decision**: Yes, extract ~5 helpers (device selection, setup, summary building)
**Rationale**: 470 lines too large for single method; helpers improve testability; maintain green tests

### How to maintain backwards compatibility?
**Decision**: Compatibility shims in orchestrator + `.model_dump()` for JSON
**Rationale**: Gradual migration; CLI unchanged; DTOs internally

## Success Metrics

- [ ] `PolicyTrainingOrchestrator` reduced from 984 → <150 LOC (85% reduction)
- [ ] 3 strategies extracted: BC <100 LOC, PPO <200 LOC, Anneal <150 LOC
- [ ] Services extracted: Rollout, Replay, Promotion
- [ ] Import `townlet.policy.training` succeeds without torch
- [ ] All DTOs defined in `townlet/dto/policy.py`
- [ ] All existing tests pass (via shims)
- [ ] New strategy unit tests added
- [ ] `pytest -q`, `ruff`, `mypy` clean
- [ ] ADR-004 complete

## Next Steps

1. ✅ Complete orchestrator analysis
2. Create strategy interface design (→ `strategy_interface.md`)
3. Create DTO schema design (→ `dto_design.md`)
4. Create torch isolation plan (→ `torch_isolation.md`)
5. Create detailed extraction plan (→ `extraction_plan.md`)
6. Begin Phase 1 implementation
