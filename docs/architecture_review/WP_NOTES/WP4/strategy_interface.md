# Training Strategy Interface Design

**Updated**: 2025-10-13
**Status**: Design

## Overview

This document defines the `TrainingStrategy` protocol and associated context/result types for WP4 policy training strategies.

## Design Principles

1. **Protocol-based** — Use `typing.Protocol` for structural typing (consistent with WP1)
2. **Minimal interface** — Only methods needed by orchestrator
3. **Context injection** — Pass dependencies via `TrainingContext` rather than constructor
4. **DTO results** — All strategies return Pydantic DTOs
5. **Optional torch** — Torch dependency declared via class var

## Strategy Protocol

```python
from typing import ClassVar, Protocol, runtime_checkable

@runtime_checkable
class TrainingStrategy(Protocol):
    """Protocol defining the interface for training strategies.

    Strategies implement specific training approaches (BC, PPO, Anneal) and
    coordinate with the orchestrator via a common interface. Strategies may
    require optional dependencies (e.g., PyTorch) declared via class variables.

    Example:
        class BCStrategy:
            name: ClassVar[str] = "bc"
            requires_torch: ClassVar[bool] = True

            def prepare(self, context: TrainingContext) -> None:
                # Setup before training
                pass

            def run(self, **kwargs) -> BCTrainingResultDTO:
                # Execute training
                return BCTrainingResultDTO(...)
    """

    # Class-level metadata
    name: ClassVar[str]
    """Strategy identifier (e.g., 'bc', 'ppo', 'anneal')."""

    requires_torch: ClassVar[bool]
    """Whether this strategy requires PyTorch to be installed."""

    def prepare(self, context: TrainingContext) -> None:
        """Prepare strategy for execution.

        Called before run() to inject runtime dependencies and context.
        Strategies should store any needed context for the upcoming run.

        Args:
            context: Runtime context with config, services, and metadata.
        """
        ...

    def run(self, **kwargs) -> TrainingResultDTO:
        """Execute the training strategy.

        Args:
            **kwargs: Strategy-specific parameters (manifest, epochs, etc.).

        Returns:
            TrainingResultDTO: Typed result containing metrics and metadata.

        Raises:
            TorchNotAvailableError: If requires_torch=True and torch missing.
            ValueError: If required parameters missing or invalid.
        """
        ...
```

## Training Context

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from townlet.config import SimulationConfig
from townlet.policy.training.services import TrainingServices

@dataclass
class TrainingContext:
    """Shared context passed to strategies before execution.

    Provides access to configuration, services, and optional runtime metadata
    like anneal context or promotion state.

    Example:
        context = TrainingContext(
            config=config,
            services=services,
            anneal_context=AnnealContext(...),
        )
        strategy.prepare(context)
        result = strategy.run(...)
    """

    config: SimulationConfig
    """Simulation configuration (mutable)."""

    services: TrainingServices
    """Shared service instances (rollout, replay, promotion)."""

    anneal_context: AnnealContext | None = None
    """Current anneal stage context (PPO strategies only)."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional runtime metadata (extensible)."""

    @classmethod
    def from_config(cls, config: SimulationConfig) -> "TrainingContext":
        """Create context from configuration.

        Args:
            config: Simulation configuration.

        Returns:
            TrainingContext with services initialized.
        """
        return cls(
            config=config,
            services=TrainingServices.from_config(config),
        )
```

## Anneal Context

```python
from dataclasses import dataclass

@dataclass
class AnnealContext:
    """Context for PPO training within anneal schedules.

    Contains baseline metrics and thresholds for evaluating whether PPO
    training has degraded performance relative to BC warm-start.

    Example:
        context = AnnealContext(
            cycle=1,
            stage="ppo",
            dataset_label="rollout_001",
            bc_accuracy=0.93,
            bc_threshold=0.90,
            bc_passed=True,
            loss_baseline=0.15,
            queue_events_baseline=12.0,
            queue_intensity_baseline=45.0,
            loss_tolerance=0.10,
            queue_tolerance=0.15,
        )
        # PPO strategy uses this to emit anneal_* telemetry fields
    """

    cycle: int
    """Anneal cycle number (0-indexed)."""

    stage: str
    """Stage identifier ('bc' or 'ppo')."""

    dataset_label: str
    """Dataset identifier for baseline tracking."""

    bc_accuracy: float | None
    """Accuracy from most recent BC training (if applicable)."""

    bc_threshold: float
    """Minimum BC accuracy required to proceed (e.g., 0.90)."""

    bc_passed: bool
    """Whether BC stage met accuracy threshold."""

    loss_baseline: float | None
    """Baseline total loss from previous PPO stage."""

    queue_events_baseline: float | None
    """Baseline queue conflict event count."""

    queue_intensity_baseline: float | None
    """Baseline queue conflict intensity sum."""

    loss_tolerance: float
    """Relative loss change threshold (e.g., 0.10 = 10%)."""

    queue_tolerance: float
    """Relative queue metric change threshold (e.g., 0.15 = 15%)."""

    def evaluate_ppo_flags(
        self,
        loss_total: float,
        queue_events: float,
        queue_intensity: float,
    ) -> tuple[bool, bool, bool]:
        """Evaluate PPO metrics against baselines.

        Args:
            loss_total: Current PPO total loss.
            queue_events: Current queue conflict event count.
            queue_intensity: Current queue conflict intensity sum.

        Returns:
            Tuple of (loss_flag, queue_flag, intensity_flag).
            True indicates metric exceeded tolerance.
        """
        loss_flag = False
        if self.loss_baseline is not None and self.loss_baseline > 0:
            relative_change = abs(loss_total - self.loss_baseline) / abs(self.loss_baseline)
            loss_flag = relative_change > self.loss_tolerance

        queue_flag = False
        if self.queue_events_baseline is not None and self.queue_events_baseline > 0:
            queue_flag = queue_events < (1.0 - self.queue_tolerance) * self.queue_events_baseline

        intensity_flag = False
        if self.queue_intensity_baseline is not None and self.queue_intensity_baseline > 0:
            intensity_flag = queue_intensity < (1.0 - self.queue_tolerance) * self.queue_intensity_baseline

        return (loss_flag, queue_flag, intensity_flag)
```

## PPO State

```python
from dataclasses import dataclass

@dataclass
class PPOState:
    """Persistent state for PPO training across runs.

    Tracks step count, learning rate, log stream offset, and cycle ID to
    maintain continuity across multiple PPO runs.

    Example:
        state = PPOState()
        # After first run
        state.step = 10000
        state.learning_rate = 1e-3
        state.cycle_id = 0
        # After second run
        state.step = 20000
        state.cycle_id = 1
    """

    step: int = 0
    """Total transitions processed across all PPO runs."""

    learning_rate: float = 1e-3
    """Current optimizer learning rate."""

    log_stream_offset: int = 0
    """Log entry counter for stream continuity."""

    cycle_id: int = -1
    """Current cycle ID (increments on rollout-based training)."""
```

## Strategy Implementations

### BCStrategy Signature

```python
class BCStrategy:
    """Behaviour cloning training strategy."""

    name: ClassVar[str] = "bc"
    requires_torch: ClassVar[bool] = True

    def __init__(self, config: SimulationConfig, services: TrainingServices):
        self.config = config
        self.services = services

    def prepare(self, context: TrainingContext) -> None:
        """No-op for BC (stateless)."""
        pass

    def run(
        self,
        manifest: Path | None = None,
        config: BCTrainingParams | None = None,
    ) -> BCTrainingResultDTO:
        """Run BC training.

        Args:
            manifest: Path to BC manifest JSON (optional, uses config default).
            config: BC training parameters (optional, uses config defaults).

        Returns:
            BCTrainingResultDTO with accuracy, loss, and metadata.

        Raises:
            TorchNotAvailableError: If PyTorch not installed.
            ValueError: If manifest not found or dataset empty.
        """
        ...
```

### PPOStrategy Signature

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
        """Store anneal context for this run."""
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
    ) -> PPOTrainingResultDTO:
        """Run PPO training.

        Args:
            dataset_config: Replay dataset config (mutually exclusive with in_memory_dataset).
            epochs: Number of training epochs.
            log_path: Path for JSONL training log.
            log_frequency: Log every N epochs.
            max_log_entries: Rotate log after N entries.
            in_memory_dataset: In-memory replay dataset (mutually exclusive with dataset_config).
            device_str: Torch device override (e.g., 'cuda:1', 'cpu').

        Returns:
            PPOTrainingResultDTO with losses, metrics, and telemetry.

        Raises:
            TorchNotAvailableError: If PyTorch not installed.
            ValueError: If dataset empty or invalid.
        """
        ...

    def run_rollout_ppo(
        self,
        ticks: int,
        batch_size: int = 1,
        epochs: int = 1,
        **kwargs,
    ) -> PPOTrainingResultDTO:
        """Capture rollout and run PPO training.

        Convenience method combining rollout capture and PPO training.

        Args:
            ticks: Number of simulation ticks to run.
            batch_size: Replay batch size.
            epochs: Number of training epochs.
            **kwargs: Additional arguments passed to run().

        Returns:
            PPOTrainingResultDTO from training.
        """
        ...
```

### AnnealStrategy Signature

```python
class AnnealStrategy:
    """Anneal scheduling strategy."""

    name: ClassVar[str] = "anneal"
    requires_torch: ClassVar[bool] = True  # Indirect via BC/PPO

    def __init__(
        self,
        config: SimulationConfig,
        services: TrainingServices,
        bc_strategy: BCStrategy,
        ppo_strategy: PPOStrategy,
    ):
        self.config = config
        self.services = services
        self.bc_strategy = bc_strategy
        self.ppo_strategy = ppo_strategy
        self._baselines: dict[str, dict[str, float]] = {}
        self._last_status: str | None = None

    def prepare(self, context: TrainingContext) -> None:
        """No-op for anneal (coordinates sub-strategies)."""
        pass

    def run(
        self,
        dataset_config: ReplayDatasetConfig | None = None,
        in_memory_dataset: InMemoryReplayDataset | None = None,
        log_dir: Path | None = None,
        bc_manifest: Path | None = None,
    ) -> AnnealSummaryDTO:
        """Run anneal schedule.

        Executes sequence of BC/PPO stages defined in config.training.anneal_schedule.
        Tracks baselines and evaluates thresholds at each stage.

        Args:
            dataset_config: Replay dataset for PPO stages.
            in_memory_dataset: In-memory dataset for PPO stages.
            log_dir: Directory for anneal results JSON.
            bc_manifest: Manifest for BC stages.

        Returns:
            AnnealSummaryDTO with stage results and final status.

        Raises:
            ValueError: If schedule empty or dataset missing for PPO stages.
        """
        ...

    def evaluate_results(self, stages: list[AnnealStageResultDTO]) -> str:
        """Evaluate anneal results to determine PASS/HOLD/FAIL status.

        Args:
            stages: List of stage results.

        Returns:
            Status string: "PASS", "HOLD", or "FAIL".
        """
        ...

    @property
    def anneal_ratio(self) -> float | None:
        """Current BC weight for mixed training."""
        ...

    @property
    def last_status(self) -> str | None:
        """Status from most recent anneal run."""
        ...
```

## Usage Examples

### Basic BC Training

```python
config = SimulationConfig(...)
services = TrainingServices.from_config(config)
strategy = BCStrategy(config, services)

context = TrainingContext(config=config, services=services)
strategy.prepare(context)

result = strategy.run(manifest=Path("data/bc_manifest.json"))
print(f"BC Accuracy: {result.accuracy:.2%}")
```

### PPO with Anneal Context

```python
# Setup
config = SimulationConfig(...)
services = TrainingServices.from_config(config)
strategy = PPOStrategy(config, services)

# Create anneal context
anneal_ctx = AnnealContext(
    cycle=1,
    stage="ppo",
    dataset_label="rollout_001",
    bc_accuracy=0.93,
    bc_threshold=0.90,
    bc_passed=True,
    loss_baseline=0.15,
    queue_events_baseline=12.0,
    queue_intensity_baseline=45.0,
    loss_tolerance=0.10,
    queue_tolerance=0.15,
)

# Inject context
context = TrainingContext(config=config, services=services, anneal_context=anneal_ctx)
strategy.prepare(context)

# Run PPO
result = strategy.run(
    dataset_config=ReplayDatasetConfig(...),
    epochs=5,
)

# Check flags
loss_flag = result.anneal_loss_flag
queue_flag = result.anneal_queue_flag
print(f"Loss flag: {loss_flag}, Queue flag: {queue_flag}")
```

### Orchestrator Integration

```python
class PolicyTrainingOrchestrator:
    def __init__(self, config: SimulationConfig, *, services: TrainingServices | None = None):
        self.config = config
        self.services = services or TrainingServices.from_config(config)

        # Initialize strategies
        self._bc_strategy = BCStrategy(config, self.services)
        self._ppo_strategy = PPOStrategy(config, self.services)
        self._anneal_strategy = AnnealStrategy(
            config,
            self.services,
            self._bc_strategy,
            self._ppo_strategy,
        )

    def run_bc_training(self, **kwargs) -> BCTrainingResultDTO:
        """Run BC training."""
        context = TrainingContext(config=self.config, services=self.services)
        self._bc_strategy.prepare(context)
        return self._bc_strategy.run(**kwargs)

    def run_ppo(self, *, anneal_context: AnnealContext | None = None, **kwargs) -> PPOTrainingResultDTO:
        """Run PPO training."""
        context = TrainingContext(
            config=self.config,
            services=self.services,
            anneal_context=anneal_context,
        )
        self._ppo_strategy.prepare(context)
        return self._ppo_strategy.run(**kwargs)
```

## Type Checking

All protocols and dataclasses should be type-checkable with mypy:

```bash
mypy src/townlet/policy/training --strict
```

Key patterns:
- Use `ClassVar` for class-level metadata
- Use `@runtime_checkable` for protocol
- Use `@dataclass` for context objects
- Return concrete DTO types from `run()` methods

## Next Steps

1. Implement `TrainingStrategy` protocol in `strategies/base.py`
2. Implement context dataclasses in `contexts.py`
3. Design DTOs (→ `dto_design.md`)
4. Implement concrete strategies following this interface
