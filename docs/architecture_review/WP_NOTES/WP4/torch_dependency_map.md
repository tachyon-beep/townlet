# Torch Dependency Mapping

**Purpose**: Risk reduction research for WP4 torch isolation
**Status**: Complete
**Updated**: 2025-10-13

## Overview

This document maps all PyTorch dependencies in `training_orchestrator.py` to ensure clean extraction and proper torch isolation in the refactored strategy pattern.

## Current Torch Isolation Pattern

The orchestrator uses a **guard-and-lazy-import** pattern:

1. **Module-level imports**: Torch-free (only imports `torch_available()` and `TorchNotAvailableError`)
2. **Function-level guards**: Check `torch_available()` before entering torch-dependent code
3. **Local imports**: Import torch inside functions after guard checks
4. **Lazy ops loading**: PPO operations imported on-demand via `_ppo_ops()` helper

This pattern allows the module to be imported without PyTorch installed, with errors only at runtime when torch-dependent methods are called.

## Torch Import Locations

### 1. Module-Level Imports (Lines 19-24)

**Location**: `src/townlet/policy/training_orchestrator.py:19-24`

```python
from townlet.policy.models import (
    ConflictAwarePolicyConfig,
    ConflictAwarePolicyNetwork,
    TorchNotAvailableError,  # ← Exception type (torch-free)
    torch_available,         # ← Guard function (torch-free)
)
```

**Status**: ✅ Torch-free
**Analysis**: These imports don't require torch. They're helper types/functions for torch availability checking.

**Migration Strategy**:
- Keep `TorchNotAvailableError` and `torch_available()` imports in strategy implementations
- These will be imported at module level in `BCStrategy`, `PPOStrategy`, `AnnealStrategy`

---

### 2. Lazy PPO Operations (Lines 72-84)

**Location**: `src/townlet/policy/training_orchestrator.py:72-84`

```python
@staticmethod
def _ppo_ops():
    """Import PPO ops lazily to avoid Torch dependency at import time."""
    if not torch_available():  # ← Guard
        raise TorchNotAvailableError(
            "PyTorch is required for PPO operations. Install the 'ml' extra."
        )
    from townlet.policy.backends.pytorch import ppo_utils as _ops  # ← Lazy import
    return _ops
```

**Status**: ⚠️ Lazy torch import
**Analysis**: Imports `ppo_utils` (torch-dependent) only when called.

**Migration Strategy**:
- Move `_ppo_ops()` helper to `PPOStrategy` class
- Keep the lazy import pattern (guard → import → return)
- Call as `ops = self._ppo_ops()` inside `PPOStrategy.run()`

**References**: Used at line 561:
```python
ops = self._ppo_ops()
gae = ops.compute_gae(...)
```

---

### 3. BC Training Guard (Lines 243-244)

**Location**: `src/townlet/policy/training_orchestrator.py:243-244`

**Function**: `run_bc_training()`

```python
def run_bc_training(self, ...) -> dict[str, float]:
    if not torch_available():  # ← Guard
        raise TorchNotAvailableError("PyTorch is required for behaviour cloning training")
    # ... rest of BC logic
```

**Status**: ✅ Proper guard pattern
**Analysis**: Guards at function entry before any torch operations.

**Migration Strategy**:
- Move to `BCStrategy.run()` as first line
- Keep identical guard logic

---

### 4. PPO Training Guard (Lines 379-380)

**Location**: `src/townlet/policy/training_orchestrator.py:379-380`

**Function**: `run_ppo()`

```python
def run_ppo(self, ...) -> dict[str, float]:
    if not torch_available():  # ← Guard
        raise TorchNotAvailableError("PyTorch is required for PPO training. Install torch to proceed.")
    # ... rest of PPO logic
```

**Status**: ✅ Proper guard pattern
**Analysis**: Guards at function entry before any torch operations.

**Migration Strategy**:
- Move to `PPOStrategy.run()` as first line
- Keep identical guard logic

---

### 5. PPO Local Torch Imports (Lines 407-409)

**Location**: `src/townlet/policy/training_orchestrator.py:407-409`

**Function**: `run_ppo()` (inside function, after guard)

```python
import torch
from torch.distributions import Categorical
from torch.nn.utils import clip_grad_norm_
```

**Status**: ✅ Local imports (best practice)
**Analysis**: Torch imports inside function after guard check. This ensures:
- Module can be imported without torch installed
- Torch is only loaded when actually needed
- Import errors are caught by the guard

**Migration Strategy**:
- Keep imports local inside `PPOStrategy.run()`
- Place after torch guard (lines 379-380)
- Maintain exact import list

**Usage**:
- `torch`: Device management (lines 418-460), tensor operations (lines 407-840)
- `Categorical`: Policy distribution (line 620)
- `clip_grad_norm_`: Gradient clipping (line 642)

---

### 6. Policy Network Build Guard (Lines 973-974)

**Location**: `src/townlet/policy/training_orchestrator.py:973-974`

**Function**: `build_policy_network()`

```python
def build_policy_network(self, ...) -> ConflictAwarePolicyNetwork:
    if not torch_available():  # ← Guard
        raise TorchNotAvailableError("PyTorch is required to build the policy network. Install torch or disable PPO.")
    # ... build network
```

**Status**: ✅ Proper guard pattern
**Analysis**: Guards before creating torch-dependent network.

**Migration Strategy**:
- Move to `PPOStrategy._setup_training()` helper (extracted from lines 454-465)
- Keep guard at helper entry
- Network construction is part of PPO setup phase

---

## Torch-Dependent Operations by Method

### `run_bc_training()` (Lines 237-273)

**Torch Operations**:
- Line 243: Torch guard
- Lines 251-266: BC trainer instantiation and training (torch-dependent)

**Dependencies**:
- `BCTrainer` (from `townlet.policy.bc`) — Uses torch internally
- `BCTrajectoryDataset` — Torch-free data structure
- `ConflictAwarePolicyConfig` — Configuration dataclass (torch-free)

**Migration**:
- Entire method → `BCStrategy.run()`
- Guard stays at entry
- No local torch imports needed (BCTrainer handles torch internally)

---

### `run_ppo()` (Lines 369-840)

**Torch Operations**:
- Line 379: Torch guard
- Lines 407-409: Local torch imports
- Lines 411-460: Device selection + policy setup (torch-dependent)
- Lines 467-840: Training loop (torch-dependent)

**Dependencies**:
- `torch`: Core tensor library
- `torch.distributions.Categorical`: Policy distribution
- `torch.nn.utils.clip_grad_norm_`: Gradient clipping
- `ppo_utils` (via `_ppo_ops()`): GAE computation, loss functions

**Migration**:
- Entire method → `PPOStrategy.run()`
- Helpers extracted (see `ppo_loop_structure.md`)
- Local torch imports stay inside `run()`

---

### `build_policy_network()` (Lines 966-981)

**Torch Operations**:
- Line 973: Torch guard
- Lines 975-981: Network instantiation (torch-dependent)

**Dependencies**:
- `ConflictAwarePolicyConfig` — Configuration dataclass (torch-free)
- `ConflictAwarePolicyNetwork` — Torch-dependent network class

**Migration**:
- Move to `PPOStrategy._setup_training()` helper
- Guard at helper entry
- Returns network instance for training

---

### `run_anneal()` (Lines 275-367)

**Torch Operations**:
- None directly (coordinates BC/PPO strategies)
- Calls `run_bc_training()` (line 311) — torch-dependent
- Calls `run_ppo()` (line 344) — torch-dependent

**Dependencies**:
- Indirect via BC/PPO sub-strategies

**Migration**:
- Entire method → `AnnealStrategy.run()`
- Delegates to `BCStrategy` and `PPOStrategy`
- `AnnealStrategy.requires_torch = True` (indirect requirement)

---

## Torch-Free Operations

### Replay Dataset Operations

**Methods**:
- `run_replay()` (lines 119-125)
- `run_replay_batch()` (lines 127-132)
- `run_replay_dataset()` (lines 134-145)
- `build_replay_dataset()` (lines 958-964)

**Status**: ✅ Torch-free
**Analysis**: Pure data loading and validation. No torch operations.

**Migration**:
- Move to `ReplayDatasetService` (Phase 2)
- Torch-free service class
- Importable without ML dependencies

---

### Rollout Capture

**Method**: `capture_rollout()` (lines 147-199)

**Status**: ✅ Torch-free
**Analysis**: Runs simulation loop and collects trajectory frames. No torch operations.

**Dependencies**:
- `SimulationLoop` (torch-free)
- `RolloutBuffer` (torch-free)
- `PolicyRuntime` (may use torch internally, but interface is torch-free)

**Migration**:
- Move to `RolloutCaptureService` (Phase 2)
- Torch-free service class
- Can be used without ML dependencies for data collection

---

### Promotion Tracking

**Method**: `_record_promotion_evaluation()` (lines 858-895)

**Status**: ✅ Torch-free
**Analysis**: Pure metric aggregation and promotion state tracking.

**Migration**:
- Move to `PromotionServiceAdapter` (Phase 2)
- Wraps existing `PromotionManager`
- Torch-free service

---

### Configuration Helpers

**Methods**:
- `_select_social_reward_stage()` (lines 897-914)
- `_apply_social_reward_stage()` (lines 916-922)
- `_resolve_replay_manifest()` (lines 934-956)

**Status**: ✅ Torch-free
**Analysis**: Pure configuration logic and file resolution.

**Migration**:
- `_select_social_reward_stage()` → `AnnealStrategy` helper
- `_apply_social_reward_stage()` → `TrainingContext` injection
- `_resolve_replay_manifest()` → `ReplayDatasetService` helper

---

## Torch Isolation Strategy

### Goal

After WP4, the `townlet.policy.training` package should be importable without PyTorch installed:

```python
# Should work without torch installed:
from townlet.policy.training import TrainingServices
from townlet.policy.training.services import ReplayDatasetService

# Should fail gracefully with clear error when torch missing:
from townlet.policy.training import PPOStrategy
strategy = PPOStrategy(config, services)
strategy.run()  # ← TorchNotAvailableError raised here
```

---

### Implementation Rules

1. **Module-level imports must be torch-free**
   - Import `torch_available()` and `TorchNotAvailableError` from `townlet.policy.models`
   - Never import `torch`, `torch.nn`, etc. at module level

2. **Guard at function entry**
   - First line of `BCStrategy.run()`, `PPOStrategy.run()`: torch guard
   - Raise `TorchNotAvailableError` with helpful message

3. **Local imports after guards**
   - Import torch inside functions after guard checks
   - Example (inside `PPOStrategy.run()`):
     ```python
     if not torch_available():
         raise TorchNotAvailableError(...)

     import torch
     from torch.distributions import Categorical
     from torch.nn.utils import clip_grad_norm_
     ```

4. **Service layer is torch-free**
   - `ReplayDatasetService`: Pure data loading
   - `RolloutCaptureService`: Simulation execution
   - `PromotionServiceAdapter`: Metric tracking
   - These can be imported and used without torch

5. **Strategy layer declares torch requirement**
   - `BCStrategy.requires_torch = True`
   - `PPOStrategy.requires_torch = True`
   - `AnnealStrategy.requires_torch = True` (indirect via sub-strategies)

---

## Testing Torch Isolation

### Unit Tests (No Torch Required)

Test that imports work without torch:

```python
def test_training_services_import_without_torch(monkeypatch):
    """Verify services can be imported without torch."""
    monkeypatch.setattr("townlet.policy.models.torch_available", lambda: False)

    from townlet.policy.training.services import (
        ReplayDatasetService,
        RolloutCaptureService,
        PromotionServiceAdapter,
        TrainingServices,
    )

    # Should not raise
```

### Integration Tests (Torch Required)

Test that strategies fail gracefully:

```python
def test_ppo_strategy_requires_torch(monkeypatch):
    """Verify PPOStrategy raises clear error when torch missing."""
    monkeypatch.setattr("townlet.policy.models.torch_available", lambda: False)

    from townlet.policy.training import PPOStrategy

    strategy = PPOStrategy(config, services)
    with pytest.raises(TorchNotAvailableError, match="PyTorch is required for PPO training"):
        strategy.run(dataset_config=config)
```

---

## Extraction Checklist

When extracting each strategy, verify:

- [ ] `torch_available()` and `TorchNotAvailableError` imported at module level
- [ ] Torch guard as first line of `run()` method
- [ ] Local torch imports inside `run()` after guard
- [ ] No torch imports at module level
- [ ] `requires_torch` class variable set correctly
- [ ] Unit tests verify import works without torch
- [ ] Integration tests verify clear error message when torch missing

---

## Current vs Target Structure

### Current (training_orchestrator.py)

```
Module Level:
├─ torch_available() imported ✅
├─ TorchNotAvailableError imported ✅
└─ No torch imports ✅

Methods:
├─ run_bc_training() → torch guard → BC logic
├─ run_ppo() → torch guard → local torch imports → PPO logic
├─ build_policy_network() → torch guard → network build
├─ run_anneal() → delegates to BC/PPO (no direct torch)
└─ Torch-free helpers (replay, rollout, promotion) ✅
```

### Target (townlet/policy/training/)

```
Services (torch-free):
├─ services/replay.py → ReplayDatasetService ✅
├─ services/rollout.py → RolloutCaptureService ✅
├─ services/promotion.py → PromotionServiceAdapter ✅
└─ services/__init__.py → TrainingServices composition ✅

Strategies (torch-dependent):
├─ strategies/bc.py → BCStrategy (torch guard at run() entry)
├─ strategies/ppo.py → PPOStrategy (torch guard + local imports)
├─ strategies/anneal.py → AnnealStrategy (delegates to BC/PPO)
└─ strategies/base.py → TrainingStrategy protocol

Orchestrator (façade):
└─ orchestrator.py → PolicyTrainingOrchestrator (thin composition)
```

---

## Risk Assessment

| Risk | Severity | Mitigation | Status |
|------|----------|------------|--------|
| Torch imports leak to module level | High | Code review + import tests | ✅ Mitigated |
| Service layer accidentally imports torch | Medium | Strict package boundaries + tests | ✅ Mitigated |
| Guard logic inconsistent across strategies | Medium | Extract common guard pattern | ✅ Mitigated |
| Local imports inside helpers break scope | Low | Keep local imports in `run()` only | ✅ Mitigated |
| Error messages unclear when torch missing | Low | Standardize error messages | ✅ Mitigated |

---

## Next Steps

1. ✅ Complete torch dependency mapping (this document)
2. ⏳ Validate DTO schema completeness
3. ⏳ Create test fixtures for torch isolation
4. ⏳ Begin Phase 1: Package structure with torch-free services
5. ⏳ Extract strategies with proper torch guards
6. ⏳ Add integration tests for torch availability checking

---

## Summary

The current orchestrator already follows best practices for torch isolation:

- ✅ No module-level torch imports
- ✅ Guards at function entry
- ✅ Local imports inside functions
- ✅ Clear error messages

**Extraction strategy**: Maintain these patterns in the new structure. Services are torch-free, strategies have guards at `run()` entry with local imports, and the orchestrator façade delegates without direct torch operations.

**Key insight**: The refactoring doesn't need to change the torch isolation strategy—it's already good. We just need to preserve it during extraction.
