# PolicyTrainingOrchestrator Analysis

**File**: `src/townlet/policy/training_orchestrator.py`
**Total Lines**: 984
**Status**: Monolithic, needs decomposition

## High-Level Responsibilities

The current orchestrator performs 7 distinct roles:

1. **BC Training** — Behaviour cloning from expert demonstrations
2. **PPO Training** — Proximal Policy Optimization from replay/rollout data
3. **Anneal Scheduling** — Coordinated BC→PPO transition with guardrails
4. **Rollout Capture** — Run simulation and collect trajectory frames
5. **Replay Dataset** — Load/build datasets from saved trajectories
6. **Promotion Evaluation** — A/B testing and candidate promotion tracking
7. **Utility Services** — Batch summarization, manifest resolution, social reward stage selection

## Line-by-Line Breakdown

### Initialization & Configuration (Lines 1-70)

```python
class PolicyTrainingOrchestrator:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self._trajectory_service = TrajectoryService()
        self._ppo_state = {"step": 0, "learning_rate": 1e-3}
        self._capture_loop = None
        self._apply_social_reward_stage(-1)
        self._anneal_context: dict[str, object] | None = None
        self._anneal_baselines: dict[str, dict[str, float]] = {}
        self._anneal_ratio: float | None = None
        self.promotion = PromotionManager(config=config, log_path=None)
        self._promotion_eval_counter = 0
        self._promotion_pass_streak = 0
        self._last_anneal_status: str | None = None
```

**State Tracked**:
- Trajectory service (transitions/frames)
- PPO training state (step counter, learning rate)
- Anneal context and baselines
- Promotion manager and counters

**Extract to**: `TrainingContext` dataclass + individual strategies

### Core Entry Points (Lines 98-133)

| Method | Lines | Purpose | Strategy Target |
|---|---|---|---|
| `run()` | 98-107 | Dispatch to BC/Anneal | Orchestrator |
| `current_anneal_ratio()` | 109-110 | Get anneal BC weight | AnnealStrategy |
| `set_anneal_ratio()` | 112-117 | Set anneal BC weight | AnnealStrategy |
| `run_replay()` | 119-125 | Single sample stats | Service helper |
| `run_replay_batch()` | 127-132 | Batch replay stats | Service helper |
| `run_replay_dataset()` | 134-145 | Dataset iteration | Service helper |

**Extract to**: Orchestrator façade + `ReplayDatasetService`

### Rollout Capture (Lines 147-199)

```python
def capture_rollout(
    self,
    ticks: int,
    auto_seed_agents: bool = False,
    output_dir: Path | None = None,
    prefix: str = "rollout_sample",
    compress: bool = True,
) -> RolloutBuffer:
```

**Responsibility**: Run simulation loop, collect trajectory frames, save to disk

**Dependencies**:
- SimulationLoop (WP1/WP2)
- PolicyRuntime (for trajectory collection)
- RolloutBuffer (data structure)

**Torch Dependency**: NO (but depends on policy which may use torch)

**Extract to**: `RolloutCaptureService`

**Key Logic**:
- Validation (ticks > 0, agents present)
- Stub policy detection + warning
- Step loop with frame collection
- Optional disk persistence

### PPO Rollout Wrapper (Lines 201-231)

```python
def run_rollout_ppo(
    self,
    ticks: int,
    batch_size: int = 1,
    auto_seed_agents: bool = False,
    output_dir: Path | None = None,
    prefix: str = "rollout_sample",
    compress: bool = True,
    epochs: int = 1,
    log_path: Path | None = None,
    log_frequency: int = 1,
    max_log_entries: int | None = None,
) -> dict[str, float]:
```

**Responsibility**: Capture rollout → build dataset → run PPO

**Extract to**: PPOStrategy (internal helper)

### BC Training (Lines 233-273)

```python
def run_bc_training(
    self,
    *,
    manifest: Path | None = None,
    config: BCTrainingParams | None = None,
) -> dict[str, float]:
```

**Current Logic** (~40 lines):
1. Check torch availability
2. Resolve manifest path
3. Load BC dataset
4. Create BCTrainer with config
5. Run `trainer.fit()`
6. Return metrics dict

**Torch Dependency**: YES (BCTrainer requires torch)

**Extract to**: `BCStrategy`

**DTO Target**: `BCTrainingResultDTO`

**Return Shape**:
```python
{
    "mode": "bc",
    "manifest": str,
    "accuracy": float,
    "loss": float,
    "learning_rate": float,
    "batch_size": int,
    "epochs": int,
    # ... from BCTrainer.fit()
}
```

### Anneal Scheduling (Lines 275-367)

```python
def run_anneal(
    self,
    *,
    dataset_config: ReplayDatasetConfig | None = None,
    in_memory_dataset: InMemoryReplayDataset | None = None,
    log_dir: Path | None = None,
    bc_manifest: Path | None = None,
) -> list[dict[str, object]]:
```

**Current Logic** (~90 lines):
1. Load schedule from config
2. Resolve replay dataset
3. Initialize baselines dict
4. For each stage in schedule:
   - If BC: run training, check accuracy threshold
   - If PPO: run training with anneal context, update baselines
   - Break on BC failure
5. Evaluate results (PASS/HOLD/FAIL)
6. Record promotion evaluation
7. Save results JSON

**Torch Dependency**: Indirect (calls BC/PPO strategies)

**Extract to**: `AnnealStrategy`

**DTO Target**: `AnnealStageResultDTO`, `AnnealSummaryDTO`

**Key State**:
- `_anneal_context`: Current stage context
- `_anneal_baselines`: Loss/queue metrics per dataset
- `_anneal_ratio`: BC weight for mixed training

**Complexity**: Medium (coordination logic, baseline tracking, threshold checks)

### PPO Training Loop (Lines 369-840)

**WARNING**: This is the largest and most complex method (~470 lines!)

```python
def run_ppo(
    self,
    dataset_config: ReplayDatasetConfig | None = None,
    epochs: int = 1,
    log_path: Path | None = None,
    log_frequency: int = 1,
    max_log_entries: int | None = None,
    in_memory_dataset: InMemoryReplayDataset | None = None,
    device_str: str | None = None,
) -> dict[str, float]:
```

**Major Sections**:

#### 1. Setup (Lines 369-465)
- Torch availability check
- Dataset resolution (in-memory vs config)
- Policy network dimensions inference
- Device selection (CUDA with best free memory, fallback CPU)
- Policy network initialization
- Optimizer setup
- Logging setup

#### 2. Helper Functions (Lines 467-516)
- `_ensure_finite()` — NaN/Inf checks
- `_update_advantage_health()` — Advantage std tracking
- `_open_log()` — Log file rotation

#### 3. Training Loop (Lines 517-835)
```python
for epoch in range(epochs):
    epoch_start = time.perf_counter()
    metrics = {...}  # Initialize accumulators
    health_tracking = {...}  # Advantage/clip monitoring

    for batch_index, batch in enumerate(batches):
        # 1. Load tensors to device
        # 2. Compute GAE advantages
        # 3. Normalize advantages
        # 4. Mini-batch training
        for start in range(0, total_transitions, mini_batch_size):
            # Forward pass
            # Compute losses (policy, value, entropy)
            # Backward pass + optimizer step
            # Track metrics

    # 5. Compute epoch averages
    # 6. Add telemetry fields (v1.1, v1.2)
    # 7. Add anneal context if present
    # 8. Add baseline metrics
    # 9. Add conflict stats
    # 10. Log epoch summary
```

**Torch Dependency**: YES (heavy torch usage throughout)

**DTO Target**: `PPOTrainingResultDTO`

**Complexity**: Very High
- Device management
- GAE computation
- Mini-batch shuffling
- Gradient clipping
- Health tracking (advantage std, clip fractions)
- Multiple telemetry versions (1.0, 1.1, 1.2)
- Anneal context integration
- Log rotation

**Return Shape**:
```python
{
    "epoch": float,
    "updates": float,
    "transitions": float,
    "loss_policy": float,
    "loss_value": float,
    "loss_entropy": float,
    "loss_total": float,
    "clip_fraction": float,
    "adv_mean": float,
    "adv_std": float,
    "grad_norm": float,
    "kl_divergence": float,
    "telemetry_version": float,
    "lr": float,
    "steps": float,
    # ... +20 more fields for v1.1/1.2
}
```

### Anneal Evaluation (Lines 842-852)

```python
def evaluate_anneal_results(self, results: list[dict[str, object]]) -> str:
```

**Logic** (~10 lines):
- Scan results for BC failures → "FAIL"
- Scan results for PPO flags (loss/queue/intensity) → "HOLD"
- Otherwise → "PASS"

**Extract to**: `AnnealStrategy` (internal helper)

### Promotion Recording (Lines 854-896)

```python
def _record_promotion_evaluation(
    self,
    *,
    status: str,
    results: list[dict[str, object]],
) -> None:
```

**Logic** (~40 lines):
- Increment eval counter
- Update pass streak
- Check candidate ready status
- Update promotion manager
- Set candidate metadata

**Extract to**: `PromotionServiceAdapter`

### Social Reward Stage Selection (Lines 897-923)

```python
def _select_social_reward_stage(self, cycle_id: int) -> str | None:
def _apply_social_reward_stage(self, cycle_id: int) -> None:
```

**Logic** (~25 lines):
- Check config override
- Scan schedule for applicable stage
- Apply stage to config features

**Extract to**: `TrainingContext` or orchestrator (config mutation)

**Note**: Side effect on `self.config` — needs careful handling

### Utility Helpers (Lines 924-982)

```python
def _summarise_batch(self, batch: ReplayBatch, batch_index: int) -> dict[str, float]:
    # Extract conflict stats from batch

def _resolve_replay_manifest(self, manifest: Path | str | None) -> Path:
    # Search for manifest in multiple locations

def build_replay_dataset(self, config: ReplayDatasetConfig | Path | str | None = None) -> ReplayDataset:
    # Construct replay dataset from config/manifest

def build_policy_network(
    self,
    feature_dim: int,
    map_shape: tuple[int, int, int],
    action_dim: int,
    hidden_dim: int | None = None,
) -> ConflictAwarePolicyNetwork:
    # Build policy network with specified architecture
```

**Extract to**: `ReplayDatasetService` + orchestrator utilities

## Torch Dependency Map

| Component | Torch Required | Import Location | Fallback |
|---|---|---|---|
| `run_bc_training()` | YES | BCTrainer import | Raise TorchNotAvailableError |
| `run_ppo()` | YES | torch, optimizer, distributions | Raise TorchNotAvailableError |
| `_ppo_ops()` | YES | ppo_utils (lazy import) | Raise TorchNotAvailableError |
| `build_policy_network()` | YES | ConflictAwarePolicyNetwork | Raise TorchNotAvailableError |
| `capture_rollout()` | NO | — | Works without torch |
| `run_replay_*()` | NO | — | Works without torch |
| Promotion/anneal eval | NO | — | Works without torch |

**Strategy**: Isolate torch imports inside strategy implementations; orchestrator and services remain torch-free.

## Extraction Priorities

### Phase 1: Low-Hanging Fruit (Services)
1. ✅ `_summarise_batch()` → `ReplayDatasetService`
2. ✅ `_resolve_replay_manifest()` → `ReplayDatasetService`
3. ✅ `build_replay_dataset()` → `ReplayDatasetService`
4. ✅ `capture_rollout()` → `RolloutCaptureService`
5. ✅ `_record_promotion_evaluation()` → `PromotionServiceAdapter`

### Phase 2: Simple Strategy (BC)
1. ✅ `run_bc_training()` → `BCStrategy`
2. ✅ `_load_bc_dataset()` → BCStrategy internal helper

### Phase 3: Medium Strategy (Anneal)
1. ✅ `run_anneal()` → `AnnealStrategy`
2. ✅ `evaluate_anneal_results()` → AnnealStrategy internal helper
3. ✅ `_anneal_context`, `_anneal_baselines`, `_anneal_ratio` → AnnealStrategy state

### Phase 4: Complex Strategy (PPO)
1. ✅ `run_ppo()` → `PPOStrategy` (~470 lines)
2. ✅ `run_rollout_ppo()` → PPOStrategy convenience method
3. ✅ `_ppo_ops()` → PPOStrategy internal lazy import
4. ✅ `_ppo_state` → PPOStrategy state

### Phase 5: Orchestrator Façade
1. ✅ `run()` dispatch
2. ✅ Strategy factory/selection
3. ✅ Shared services composition
4. ✅ `build_policy_network()` delegation

## State Management

### Current State (all in `__init__`)
```python
self.config: SimulationConfig
self._trajectory_service: TrajectoryService
self._ppo_state: dict[str, Any]
self._anneal_context: dict[str, object] | None
self._anneal_baselines: dict[str, dict[str, float]]
self._anneal_ratio: float | None
self.promotion: PromotionManager
self._promotion_eval_counter: int
self._promotion_pass_streak: int
self._last_anneal_status: str | None
```

### Target State Distribution

**Orchestrator**:
```python
self.config: SimulationConfig
self.services: TrainingServices
```

**TrainingServices**:
```python
self.rollout_capture: RolloutCaptureService
self.replay_dataset: ReplayDatasetService
self.promotion: PromotionServiceAdapter
```

**BCStrategy**:
```python
# Stateless (uses context)
```

**PPOStrategy**:
```python
self.ppo_state: PPOState  # step, learning_rate, log_offset
```

**AnnealStrategy**:
```python
self.anneal_context: AnnealContext | None
self.baselines: dict[str, dict[str, float]]
self.anneal_ratio: float | None
self.last_status: str | None
```

**PromotionServiceAdapter**:
```python
self.manager: PromotionManager
self.eval_counter: int
self.pass_streak: int
```

## Testing Surface

### Current Tests
- `tests/test_policy_orchestrator.py` — Main orchestrator tests
- `tests/test_policy_backend_selection.py` — Provider selection tests
- Integration tests using orchestrator

### Target Tests
- `tests/policy/training/test_orchestrator.py` — Façade composition tests
- `tests/policy/training/strategies/test_bc_strategy.py` — BC unit tests
- `tests/policy/training/strategies/test_ppo_strategy.py` — PPO unit tests (slow, torch)
- `tests/policy/training/strategies/test_anneal_strategy.py` — Anneal unit tests
- `tests/policy/training/test_services.py` — Service helpers
- `tests/policy/training/test_torch_guards.py` — Optional dependency checks

## Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| PPO loop too complex to extract | High | Incremental extraction with internal helpers |
| State management bugs | Medium | Comprehensive unit tests per strategy |
| Torch import leakage | Medium | Centralized torch guards + import checks |
| Breaking CLI changes | High | Compatibility shims + `.model_dump()` |
| Anneal baseline persistence | Medium | Document baseline dict structure |
| Log rotation logic fragile | Low | Extract to helper, test independently |

## Next Steps

1. Design `TrainingStrategy` protocol (→ `strategy_interface.md`)
2. Design training result DTOs (→ `dto_design.md`)
3. Create extraction sequencing plan (→ `extraction_plan.md`)
4. Document torch isolation approach (→ `torch_isolation.md`)
