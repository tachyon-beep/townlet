# ADR 0004: Policy Training Strategies

## Status

Accepted

## Context

The simulation's policy training infrastructure was previously implemented as a monolithic 984-line `PolicyTrainingOrchestrator` class that mixed multiple responsibilities: behaviour cloning (BC), Proximal Policy Optimization (PPO), anneal scheduling, rollout capture, replay dataset management, and promotion evaluation. This coupling made the code difficult to test, prevented torch-free imports for replay-only workflows, and complicated feature development.

Work Package 4 refactors this monolith into composable strategy objects following the strategy pattern established in WP1 (Ports & Factory Registry), consuming typed DTOs from WP3 (DTO Boundary), and interacting with the modular world package from WP2.

## Decision

Implement a **strategy-based training architecture** with the following components:

### 1. Strategy Pattern with Protocol Interface

Define a minimal `TrainingStrategy` protocol using structural typing (PEP 544):

```python
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.policy.training.contexts import TrainingContext
    # Result types imported conditionally to avoid circular imports

class TrainingStrategy(Protocol):
    """Strategy protocol for policy training algorithms."""

    def run(self, context: TrainingContext, **kwargs) -> Any:
        """Execute training strategy.

        Args:
            context: Training context with config and services.
            **kwargs: Strategy-specific parameters.

        Returns:
            Typed DTO result (BCTrainingResultDTO, PPOTrainingResultDTO, etc.)
        """
        ...
```

### 2. Three Core Strategies

#### BCStrategy (Behaviour Cloning)
- **Responsibility**: Train policy via supervised learning from expert demonstrations
- **Size**: 131 lines
- **Torch Dependency**: Yes (raises `TorchNotAvailableError` when unavailable)
- **Returns**: `BCTrainingResultDTO` with accuracy, loss, manifest path, duration

#### PPOStrategy (Proximal Policy Optimization)
- **Responsibility**: Train policy via reinforcement learning using PPO algorithm
- **Size**: 709 lines (largest strategy, includes device selection, GAE computation, mini-batch training)
- **Torch Dependency**: Yes (with torch availability checks)
- **Returns**: `PPOTrainingResultDTO` with losses, metrics, anneal flags

#### AnnealStrategy (Scheduled Training Orchestration)
- **Responsibility**: Coordinate BC and PPO stages according to configured schedule, evaluate guardrails
- **Size**: 358 lines
- **Torch Dependency**: Indirect (delegates to BC/PPO strategies)
- **Returns**: `AnnealSummaryDTO` with stage results, status, promotion metrics

### 3. Shared Services Layer

Extract torch-free services for reuse across strategies:

```python
class TrainingServices:
    """Composition of training support services."""

    replay: ReplayDatasetService      # Manifest resolution, dataset building (210 lines)
    rollout: RolloutCaptureService    # Simulation loop capture (145 lines)
    promotion: PromotionServiceAdapter # Promotion tracking (152 lines)

    @classmethod
    def from_config(cls, config: SimulationConfig) -> TrainingServices: ...
```

**Design Principles**:
- Services are **stateless** or **low-state** (e.g., promotion service wraps `PromotionManager`)
- Services are **torch-free** — importable without ML dependencies
- Services provide focused responsibilities (SRP)

### 4. Training Context

Encapsulate strategy dependencies in a context object:

```python
@dataclass
class TrainingContext:
    """Context object encapsulating strategy dependencies."""

    config: SimulationConfig
    services: TrainingServices
    anneal_context: AnnealContext | None = None  # For anneal-aware PPO stages

    @classmethod
    def from_config(cls, config: SimulationConfig) -> TrainingContext: ...
```

**`AnnealContext`** provides anneal-specific state for PPO stages:
- BC accuracy and threshold for promotion decisions
- Loss and queue conflict baselines for guardrail evaluation
- Tolerance thresholds for regression detection

### 5. Orchestrator Façade

New `TrainingOrchestrator` becomes a thin façade (170 lines, 83% reduction from 984):

```python
class TrainingOrchestrator:
    """Training orchestrator façade."""

    def __init__(self, config: SimulationConfig) -> None: ...

    def run_bc(self, *, manifest: Path | None = None) -> BCTrainingResultDTO: ...
    def run_ppo(self, *, dataset_config: ..., epochs: int = 1, ...) -> PPOTrainingResultDTO: ...
    def run_anneal(self, *, dataset_config: ..., log_dir: Path | None = None, ...) -> AnnealSummaryDTO: ...
    def run(self) -> None: ...  # CLI entry point based on config.training.source
```

**Methods** delegate to strategy instances and return typed DTOs. Context is lazily initialized on first access.

### 6. DTO-Based Results

All strategies return Pydantic v2 DTOs defined in `townlet/dto/policy.py`:

#### BCTrainingResultDTO (720 lines total file, ~60 lines per DTO)
```python
class BCTrainingResultDTO(BaseModel):
    """BC training result with accuracy and metrics."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    accuracy: float
    loss: float
    manifest: str
    duration_sec: float
```

#### PPOTrainingResultDTO
```python
class PPOTrainingResultDTO(BaseModel):
    """PPO training result with losses and metrics."""
    # Includes epoch-level metrics, conflict stats, anneal flags
    loss_total: float
    loss_policy: float
    loss_value: float
    queue_conflict_events: int | None
    anneal_loss_flag: bool
    anneal_queue_flag: bool
    anneal_intensity_flag: bool
    duration_sec: float
    # + 40+ additional fields for comprehensive telemetry
```

#### AnnealSummaryDTO
```python
class AnnealSummaryDTO(BaseModel):
    """Anneal schedule execution summary."""
    stages: list[AnnealStageResultDTO]  # Per-stage results
    status: str  # PASS/FAIL/HOLD
    dataset_label: str
    baselines: dict[str, dict[str, float]]
    promotion_pass_streak: int
    promotion_candidate_ready: bool
    duration_sec: float
```

**Benefits**:
- Type safety via Pydantic validation
- Immutability via `frozen=True`
- JSON serialization via `.model_dump()`
- Schema versioning support

### 7. Torch Optionality

Torch dependency isolation ensures torch-free imports:

```python
# Lazy torch imports in strategy implementations
def run(self, context: TrainingContext) -> PPOTrainingResultDTO:
    if not torch_available():
        raise TorchNotAvailableError(
            "PyTorch required for PPO training. Install: pip install -e .[ml]"
        )

    import torch  # Import only after availability check
    # ... training logic
```

**Import Structure**:
- `townlet.policy.training` package is importable without torch
- Strategies import torch **inside methods** after availability checks
- Services are entirely torch-free
- TYPE_CHECKING guards prevent import-time torch dependencies

### 8. Backward Compatibility

During transition period:

```python
# In townlet/policy/training/__init__.py
PolicyTrainingOrchestrator = TrainingOrchestrator  # Alias for compatibility

__all__ = [
    "TrainingOrchestrator",
    "PolicyTrainingOrchestrator",  # Deprecated, use TrainingOrchestrator
    ...
]
```

Old monolithic orchestrator at `src/townlet/policy/training_orchestrator.py` remains functional. Full migration planned for future work package.

## Consequences

### Positive

1. **Modularity**: Each strategy is a focused, single-responsibility component (<710 LOC vs. 984 monolithic)
2. **Testability**: Strategies can be unit-tested in isolation with mock contexts
3. **Optional Dependencies**: Torch can be absent for replay/analysis workflows (22 tests pass without torch)
4. **Type Safety**: Pydantic DTOs provide validation and documentation
5. **Maintainability**: Clear separation of concerns simplifies feature development
6. **Reusability**: Services are shared across strategies, reducing duplication

### Trade-offs

1. **Multiple Files**: 8 new files vs. 1 monolith (acceptable for better organization)
2. **Context Object**: Adds indirection layer (necessary for dependency injection)
3. **Coexistence**: Two orchestrator implementations during transition (temporary, enables gradual migration)
4. **Mypy Complexity**: PPO strategy torch typing required targeted mypy override (pragmatic given torch's complex type stubs)

### Risks Mitigated

- **PPO Complexity** (High): Managed via helper methods and incremental extraction
- **Torch Leakage** (Medium): Resolved via centralized guards and lazy imports
- **CLI Breaking** (High): Prevented via backward compatibility alias
- **Test Coverage** (Medium): 22 new strategy/service tests added

## Implementation Status

**Status**: COMPLETE
**Completion Date**: 2025-10-13 (WP4 Phases 0-8)

### Delivered Components

- ✅ Strategy protocol defined in `townlet/policy/training/strategies/base.py`
- ✅ Three strategies implemented: BCStrategy (131 lines), PPOStrategy (709 lines), AnnealStrategy (358 lines)
- ✅ Three services extracted: ReplayDatasetService, RolloutCaptureService, PromotionServiceAdapter (507 lines total)
- ✅ Training context dataclasses in `townlet/policy/training/contexts.py` (195 lines)
- ✅ Orchestrator façade in `townlet/policy/training/orchestrator.py` (170 lines)
- ✅ Policy DTOs in `townlet/dto/policy.py` (720 lines, ~104 lines actual DTO code)
- ✅ Backward compatibility alias maintained
- ✅ Comprehensive test coverage:
  - 7 BCStrategy unit tests
  - 15 service unit tests
  - All 806 existing tests passing
  - 85% code coverage maintained

### Architecture Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Files | 1 | 8 | +700% (better organization) |
| Largest File | 984 LOC | 720 LOC (DTOs) | -27% |
| Orchestrator | 984 LOC | 170 LOC | -83% |
| Torch-Free Import | ❌ | ✅ | Achieved |
| Strategy LOC | - | 131/709/358 | Focused modules |
| Services LOC | - | 210/145/152 | Reusable components |

### Code Quality

- ✅ All tests passing (806 passed, 1 skipped)
- ✅ Type checking clean (`mypy src/townlet/policy/training/`)
- ✅ Linting clean (`ruff check src/townlet/policy/training/`)
- ✅ 85% code coverage maintained
- ✅ Torch optionality verified (import succeeds without torch)

### Deviations from Original Specification

None. Implementation follows WP4 tasking document specifications. The only pragmatic adjustment was adding a mypy override for PPO strategy torch typing (documented in `pyproject.toml:83-85`), which is acceptable given PyTorch's complex type system.

## Migration Notes

- **CLI Scripts**: Continue using existing imports (`from townlet.policy.training_orchestrator import PolicyTrainingOrchestrator`). These imports work via the old monolithic file which remains functional.
- **New Code**: Use `from townlet.policy.training import TrainingOrchestrator` for new implementations.
- **Full Migration**: Future WP will update CLI scripts and deprecate/remove old orchestrator file.
- **Tests**: New tests in `tests/policy/training/` use new imports. Legacy tests in `tests/test_policy_orchestrator.py` continue using old imports.
- **Torch-Free Workflows**: Import `townlet.policy.training.services` without torch for replay dataset analysis.

## Related Documents

- `docs/architecture_review/WP_TASKINGS/WP4.md` — Official work package tasking
- `docs/architecture_review/WP_NOTES/WP4/` — Planning documents and analysis
  - `README.md` — Overview, goals, success criteria
  - `orchestrator_analysis.md` — 984-line monolith breakdown
  - `approach.md` — 8-phase implementation plan
  - `strategy_interface.md` — Protocol design
  - `dto_design.md` — Complete DTO schemas
- `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md` — Port foundation (WP1)
- `docs/architecture_review/ADR/ADR-002 - World Modularisation.md` — World package structure (WP2)
- `docs/architecture_review/ADR/ADR-003 - DTO Boundary.md` — DTO patterns and validation (WP3)
- `docs/architecture_review/ARCHITECTURE_REVIEW_2.md` — §6.4 Policy & tests architectural context

## Future Work

- **CLI Migration**: Update `scripts/run_training.py`, `run_anneal_rehearsal.py`, `run_mixed_soak.py` to use new import paths
- **Orchestrator Deprecation**: Remove or archive old `src/townlet/policy/training_orchestrator.py` after CLI migration
- **Test Consolidation**: Migrate old orchestrator tests (`tests/test_policy_orchestrator.py`) to use new strategies
- **Strategy Registry**: Consider adding registry-backed strategy selection (following WP1 factory pattern)
- **Integration Tests**: Add end-to-end anneal integration tests with real strategies (currently using functional old orchestrator tests)
