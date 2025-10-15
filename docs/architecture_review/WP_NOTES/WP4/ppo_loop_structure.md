# PPO Training Loop Structure Analysis

**Purpose**: Risk reduction research for PPO extraction
**Lines**: 369-840 (472 lines total)
**Complexity**: Very High

## Structure Overview

The PPO loop has 5 major sections:

1. **Setup & Validation** (Lines 369-465, ~96 lines)
2. **Helper Functions** (Lines 467-516, ~49 lines)
3. **Training Loop** (Lines 517-835, ~318 lines)
4. **Cleanup** (Lines 836-840, ~4 lines)
5. **Return** (Line 840)

## Section 1: Setup & Validation (96 lines)

### 1.1 Torch Guard (Lines 379-380)
```python
if not torch_available():
    raise TorchNotAvailableError(...)
```
**Extract to**: Strategy guard (first line of `PPOStrategy.run()`)

### 1.2 Dataset Resolution (Lines 382-405, ~23 lines)
```python
# Resolve dataset (in_memory vs config)
# Load batches
# Infer network dimensions from batch
# Get baseline metrics
```
**Extract to**: `_resolve_dataset()` helper (~20 lines)

### 1.3 Torch Imports (Lines 407-409)
```python
import torch
from torch.distributions import Categorical
from torch.nn.utils import clip_grad_norm_
```
**Keep**: Inside PPOStrategy (local imports)

### 1.4 Device Selection (Lines 411-453, ~42 lines)
```python
# Config check
# Device string override
# CUDA memory-aware selection
# Device logging
# CUDA optimization flags
```
**Extract to**: `_select_device()` helper (~40 lines)
**Returns**: `tuple[torch.device, str | None]` (device, device_name)

### 1.5 Policy/Optimizer Setup (Lines 454-465, ~11 lines)
```python
# Build policy network
# Move to device
# Create optimizer
# Update state
# Create generator
# Get dataset label
```
**Extract to**: `_setup_training()` helper (~15 lines)
**Returns**: `tuple[Policy, Optimizer, Generator, str]`

## Section 2: Helper Functions (49 lines)

### 2.1 _ensure_finite() (Lines 467-469)
```python
def _ensure_finite(name: str, tensor: torch.Tensor, batch_index: int) -> None:
    if torch.isnan(tensor).any() or torch.isinf(tensor).any():
        raise ValueError(...)
```
**Keep**: As PPOStrategy internal helper

### 2.2 _update_advantage_health() (Lines 471-483)
```python
def _update_advantage_health(
    flat_advantages: torch.Tensor,
    *,
    batch_index: int,
    stats: dict[str, float],
) -> None:
    # Track advantage std
    # Count zero-std batches
```
**Keep**: As PPOStrategy internal helper

### 2.3 Log Setup (Lines 484-516)
```python
# Log frequency/max entries config
# Log file handle/rotation tracking
# Cycle ID management
# Data mode detection
# _open_log() closure
```
**Extract to**: `_setup_logging()` helper (~20 lines)
**Returns**: `LoggingContext` (handle, rotation_index, entries_written, cycle_id, data_mode, offset)

## Section 3: Training Loop (318 lines!)

### 3.1 Epoch Loop Setup (Lines 517-577, ~60 lines)
```python
for epoch in range(epochs):
    epoch_start = time.perf_counter()
    # Initialize metric accumulators
    # Initialize health tracking
```
**Keep**: Main loop structure

### 3.2 Batch Loop (Lines 579-810, ~231 lines!)

#### 3.2.1 Batch Processing (Lines 579-614)
```python
for batch_index, batch in enumerate(batches, start=1):
    # Summarize batch (conflict stats)
    # Load tensors to device
    # Compute GAE advantages
    # Normalize advantages
    # Validate finite
    # Update health tracking
    # Extend buffers
    # Flatten tensors
```
**Potential extract**: `_process_batch()` (~30 lines)
**Returns**: `BatchTensors` (flat_maps, flat_features, flat_actions, flat_advantages, flat_returns, flat_old_log_probs, flat_old_values)

#### 3.2.2 Mini-Batch Loop (Lines 634-810, ~176 lines!!)
```python
    # Calculate mini-batch size
    # Generate permutation
    for start in range(0, total_transitions, mini_batch_size):
        # Index mini-batch
        # Forward pass (policy + value)
        # Compute losses (policy, value, entropy)
        # Backward pass
        # Gradient clipping/tracking
        # Optimizer step
        # Accumulate metrics
        # Track health
```
**Potential extract**: `_train_mini_batches()` (~150 lines)
**Input**: BatchTensors, policy, optimizer, config
**Output**: Metrics dict

### 3.3 Epoch Summary Building (Lines 812-851, ~39 lines)
```python
    # Average metrics
    # Compute entropy stats
    # Compute reward-advantage correlation
    # Update learning rate/step count
    # Build epoch_summary dict (core metrics)
    # Add health tracking
    # Print warnings
```
**Extract to**: `_build_epoch_summary_core()` (~25 lines)

### 3.4 Telemetry Enrichment (Lines 853-951, ~98 lines)

#### 3.4.1 Telemetry v1.1 Fields (Lines 853-894)
```python
    if PPO_TELEMETRY_VERSION >= 1.1:
        epoch_summary.update({
            "epoch_duration_sec": ...,
            "data_mode": ...,
            "cycle_id": ...,
            "batch_entropy_mean": ...,
            # ... 15 more fields
        })
```
**Extract to**: `_add_telemetry_v1_1()` (~20 lines)

#### 3.4.2 Anneal Context Fields (Lines 896-940)
```python
    anneal_context = getattr(self, "_anneal_context", None)
    if PPO_TELEMETRY_VERSION >= 1.2 and anneal_context:
        # Extract anneal context fields
        # Evaluate flags (loss, queue, intensity)
        epoch_summary.update({
            "anneal_cycle": ...,
            "anneal_stage": ...,
            # ... 11 more fields
        })
```
**Extract to**: `_add_anneal_context()` (~30 lines)

#### 3.4.3 Baseline Metrics (Lines 941-948)
```python
    if baseline_metrics:
        epoch_summary["baseline_sample_count"] = ...
        # ... 5 more fields
```
**Extract to**: `_add_baseline_metrics()` (~10 lines)

#### 3.4.4 Conflict Stats (Lines 949-951)
```python
    if conflict_acc:
        for key, value in conflict_acc.items():
            epoch_summary[f"{key}_avg"] = value / len(batches)
```
**Keep**: Inline (3 lines)

### 3.5 Logging (Lines 953-967, ~14 lines)
```python
    print(f"PPO epoch {epoch + 1}:", epoch_summary)
    should_log_epoch = ...
    if should_log_epoch and log_path is not None:
        # Check rotation
        # Write log
        # Increment counter
```
**Keep**: Inline (simple logging logic)

## Section 4: Cleanup (4 lines)
```python
if log_handle is not None:
    log_handle.close()
if PPO_TELEMETRY_VERSION >= 1.1:
    self._ppo_state["log_stream_offset"] = log_stream_offset
return last_summary
```
**Keep**: End of run() method

## Extraction Plan

### Phase 5.1: Extract Setup Helpers (Low Risk)
1. `_select_device()` — Lines 415-453 (~40 lines)
2. `_setup_training()` — Lines 454-465 + network build (~20 lines)
3. `_setup_logging()` — Lines 484-516 (~20 lines)
4. `_resolve_dataset()` — Lines 382-405 (~20 lines)

**Total**: ~100 lines extracted, ~370 lines remaining

### Phase 5.2: Extract Summary Builders (Medium Risk)
1. `_build_epoch_summary_core()` — Lines 812-851 (~25 lines)
2. `_add_telemetry_v1_1()` — Lines 853-894 (~20 lines)
3. `_add_anneal_context()` — Lines 896-940 (~30 lines)
4. `_add_baseline_metrics()` — Lines 941-948 (~10 lines)

**Total**: ~85 lines extracted, ~285 lines remaining

### Phase 5.3: Consider Batch Processing Extract (High Risk)
Option A: Keep batch/mini-batch loops inline (~230 lines)
Option B: Extract `_process_batch()` (~30 lines) + `_train_mini_batches()` (~150 lines)

**Recommendation**: Keep inline initially (too complex, many temp variables)
**Alternative**: Extract only `_process_batch()` preprocessing (~30 lines)

## Final Structure

### PPOStrategy.run() (~200 lines after extraction)
```python
def run(...) -> PPOTrainingResultDTO:
    # 1. Torch guard (2 lines)
    # 2. Resolve dataset (call helper, 5 lines)
    # 3. Imports (3 lines)
    # 4. Select device (call helper, 3 lines)
    # 5. Setup training (call helper, 3 lines)
    # 6. Setup logging (call helper, 5 lines)
    # 7. Epoch loop: ~200 lines
    #    - Batch loop: ~180 lines
    #      - Process batch: ~40 lines
    #      - Mini-batch loop: ~140 lines
    #    - Summary building: call helpers, ~10 lines
    #    - Logging: ~10 lines
    # 8. Cleanup (4 lines)
    # 9. Return DTO (5 lines)
```

### Helper Functions (~180 lines)
- `_select_device()` — 40 lines
- `_setup_training()` — 20 lines
- `_setup_logging()` — 20 lines
- `_resolve_dataset()` — 20 lines
- `_build_epoch_summary_core()` — 25 lines
- `_add_telemetry_v1_1()` — 20 lines
- `_add_anneal_context()` — 30 lines
- `_add_baseline_metrics()` — 10 lines
- `_ensure_finite()` — 3 lines (already exists)
- `_update_advantage_health()` — 13 lines (already exists)

**Total**: ~380 lines (200 in run() + 180 in helpers)

## Key Risks

| Risk | Severity | Mitigation |
|---|---|---|---|
| Helper extraction breaks temp variable scope | High | Pass all needed vars explicitly |
| Mini-batch loop too complex to extract | High | Keep inline, extract only preprocessing |
| Logging state management fragile | Medium | Encapsulate in LoggingContext dataclass |
| Anneal context field extraction errors | Medium | Unit test each helper independently |
| Device selection edge cases | Low | Copy existing logic exactly |

## Success Criteria

- [ ] PPOStrategy.run() <200 LOC
- [ ] Helpers testable independently
- [ ] No logic changes (golden test output unchanged)
- [ ] All existing tests pass
- [ ] Torch imports stay local
- [ ] State management clear (PPOState dataclass)

## Next Steps

1. Create test fixtures capturing current PPO output
2. Extract setup helpers first (lowest risk)
3. Extract summary helpers next (medium risk)
4. Keep batch/mini-batch loops inline (high risk, low benefit)
5. Add unit tests for each helper
6. Verify golden test still passes
