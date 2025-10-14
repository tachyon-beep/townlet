# DTO Schema Validation

**Purpose**: Risk reduction research for WP4 DTO implementation
**Status**: Complete
**Updated**: 2025-10-13

## Overview

This document validates that the designed DTO schemas (from `dto_design.md`) comprehensively cover all fields emitted by the current `training_orchestrator.py` implementation.

## Validation Methodology

For each training method (`run_bc_training`, `run_ppo`, `run_anneal`):
1. Identify all fields in the current dict output
2. Cross-reference with designed DTO schema
3. Flag any missing fields or mismatches
4. Document architectural improvements in DTO design

## BC Training Output Validation

### Current Implementation

**Location**: `training_orchestrator.py:237-273`

**Output Structure** (lines 267-272):
```python
metrics = trainer.fit(dataset)  # Returns dict from BCTrainer
metrics.update({
    "mode": "bc",
    "manifest": str(manifest_path),
})
return metrics  # → dict[str, float]
```

**Fields from `BCTrainer.fit()`**:
- `accuracy`: Training accuracy (0.0-1.0)
- `loss`: Final training loss
- `learning_rate`: Learning rate used
- `batch_size`: Batch size used
- `epochs`: Number of epochs completed
- `val_accuracy`: Validation accuracy (optional)
- `val_loss`: Validation loss (optional)
- `weight_decay`: Weight decay used (optional)
- `device`: Torch device string (optional)

**Fields added by orchestrator**:
- `mode`: "bc"
- `manifest`: Path to manifest JSON

### DTO Schema Coverage

**DTO**: `BCTrainingResultDTO` (dto_design.md:46-129)

| Field | Required | In Current Output | Status |
|-------|----------|-------------------|--------|
| `mode` | ✅ | ✅ | Match |
| `manifest` | ✅ | ✅ | Match |
| `accuracy` | ✅ | ✅ | Match |
| `loss` | ✅ | ✅ | Match |
| `learning_rate` | ✅ | ✅ | Match |
| `batch_size` | ✅ | ✅ | Match |
| `epochs` | ✅ | ✅ | Match |
| `val_accuracy` | Optional | Optional | Match |
| `val_loss` | Optional | Optional | Match |
| `weight_decay` | Optional | Optional | Match |
| `device` | Optional | Optional | Match |
| `duration_sec` | Optional (base) | ❌ Not emitted | **Gap** |
| `schema_version` | Optional (base) | ❌ Not emitted | **Gap** |

### Gaps and Solutions

**Gap 1**: `duration_sec` not currently tracked
- **Solution**: Add timer in `BCStrategy.run()` (lines ~519-742 pattern from PPO)
- **Risk**: Low (simple timer addition)

**Gap 2**: `schema_version` not emitted
- **Solution**: DTO default value handles this (`default="1.0.0"`)
- **Risk**: None (Pydantic auto-populates)

### Verdict

✅ **DTO schema is complete** — All current fields covered, with 2 optional fields added for completeness.

---

## PPO Training Output Validation

### Current Implementation

**Location**: `training_orchestrator.py:369-840`

**Output Structure**: Built incrementally across multiple sections

#### Core Metrics (Lines 705-721)

```python
epoch_summary = {
    "epoch": float(epoch + 1),
    "updates": float(mini_batch_updates),
    "transitions": float(transitions_processed),
    "loss_policy": averaged_metrics["policy_loss"],
    "loss_value": averaged_metrics["value_loss"],
    "loss_entropy": averaged_metrics["entropy"],
    "loss_total": averaged_metrics["total_loss"],
    "clip_fraction": averaged_metrics["clip_frac"],
    "adv_mean": averaged_metrics["adv_mean"],
    "adv_std": averaged_metrics["adv_std"],
    "grad_norm": averaged_metrics["grad_norm"],
    "kl_divergence": averaged_metrics["kl_divergence"],
    "telemetry_version": float(PPO_TELEMETRY_VERSION),
    "lr": lr,
    "steps": float(self._ppo_state["step"]),
}
```

#### Health Tracking (Lines 726-732)

```python
epoch_summary.update({
    "adv_zero_std_batches": float(health_tracking["adv_zero_std_batches"]),
    "adv_min_std": float(min_adv_std),
    "clip_triggered_minibatches": float(health_tracking["clip_triggered_minibatches"]),
    "clip_fraction_max": float(health_tracking["max_clip_fraction"]),
})
```

#### Telemetry v1.1 Fields (Lines 740-762)

```python
if PPO_TELEMETRY_VERSION >= 1.1:
    epoch_summary.update({
        "epoch_duration_sec": float(time.perf_counter() - epoch_start),
        "data_mode": data_mode,
        "cycle_id": float(cycle_id),
        "batch_entropy_mean": float(epoch_entropy_mean),
        "batch_entropy_std": float(epoch_entropy_std),
        "grad_norm_max": float(grad_norm_max),
        "kl_divergence_max": float(kl_max),
        "reward_advantage_corr": float(reward_adv_corr),
        "rollout_ticks": float(rollout_ticks),
        "log_stream_offset": float(log_stream_offset + 1),
        "queue_conflict_events": float(getattr(dataset, "queue_conflict_count", 0)),
        "queue_conflict_intensity_sum": float(getattr(dataset, "queue_conflict_intensity_sum", 0.0)),
        "shared_meal_events": float(getattr(dataset, "shared_meal_count", 0)),
        "late_help_events": float(getattr(dataset, "late_help_count", 0)),
        "shift_takeover_events": float(getattr(dataset, "shift_takeover_count", 0)),
        "chat_success_events": float(getattr(dataset, "chat_success_count", 0)),
        "chat_failure_events": float(getattr(dataset, "chat_failure_count", 0)),
        "chat_quality_mean": float(getattr(dataset, "chat_quality_mean", 0.0)),
    })
```

#### Telemetry v1.2 Anneal Context (Lines 789-808)

```python
if PPO_TELEMETRY_VERSION >= 1.2 and anneal_context:
    epoch_summary.update({
        "anneal_cycle": float(anneal_context.get("cycle", -1.0)),
        "anneal_stage": str(anneal_context.get("stage", "")),
        "anneal_dataset": str(anneal_context.get("dataset_label", "")),
        "anneal_bc_accuracy": float_or_none(bc_accuracy_value),
        "anneal_bc_threshold": float_or_none(bc_threshold_value),
        "anneal_bc_passed": bool(anneal_context.get("bc_passed", True)),
        "anneal_loss_baseline": float_or_none(loss_baseline),
        "anneal_queue_baseline": float_or_none(queue_baseline),
        "anneal_intensity_baseline": float_or_none(intensity_baseline),
        "anneal_loss_flag": bool(loss_flag),
        "anneal_queue_flag": bool(queue_flag),
        "anneal_intensity_flag": bool(intensity_flag),
    })
```

#### Baseline Metrics (Lines 809-817)

```python
if baseline_metrics:
    epoch_summary["baseline_sample_count"] = float(baseline_metrics.get("sample_count", 0.0))
    epoch_summary["baseline_reward_mean"] = float(baseline_metrics.get("reward_mean", 0.0))
    epoch_summary["baseline_reward_sum"] = float(baseline_metrics.get("reward_sum", 0.0))
    if "reward_sum_mean" in baseline_metrics:
        epoch_summary["baseline_reward_sum_mean"] = float(baseline_metrics.get("reward_sum_mean", 0.0))
    if "log_prob_mean" in baseline_metrics:
        epoch_summary["baseline_log_prob_mean"] = float(baseline_metrics.get("log_prob_mean", 0.0))
```

#### Conflict Stats (Lines 817-819)

```python
if conflict_acc:
    for key, value in conflict_acc.items():
        epoch_summary[f"{key}_avg"] = value / len(batches)
```

**Note**: Conflict stats have dynamic keys like `"conflict.queue_conflict_events_avg"`, `"conflict.shared_meal_count_avg"`, etc.

### DTO Schema Coverage

**DTO**: `PPOTrainingResultDTO` (dto_design.md:131-458)

| Field Category | Field Count | All Covered? | Notes |
|----------------|-------------|--------------|-------|
| Core metrics (v1.0) | 12 | ✅ Yes | epoch, updates, transitions, losses, clip, adv, grad, kl, lr, steps |
| Health tracking | 4 | ✅ Yes | adv_zero_std_batches, adv_min_std, clip_triggered_minibatches, clip_fraction_max |
| Extended (v1.1) | 18 | ✅ Yes | epoch_duration_sec, data_mode, cycle_id, entropies, grad/kl max, corr, rollout_ticks, log_offset, social events |
| Anneal (v1.2) | 12 | ✅ Yes | anneal_cycle, stage, dataset, bc_accuracy/threshold/passed, baselines, flags |
| Baseline metrics | 5 | ✅ Yes | sample_count, reward_mean/sum/sum_mean, log_prob_mean |
| Conflict stats | Dynamic | ⚠️ Special | See note below |

#### Conflict Stats Handling

**Current**: Dynamic keys added to dict with `"conflict.*_avg"` prefix

**DTO Design** (line 454-458):
```python
# Conflict stats (averaged across batches)
# Note: These are added dynamically by _summarise_batch()
# We don't enumerate all possible conflict.* fields here;
# they're stored in a dict and flattened during serialization
```

**Solution**: Use Pydantic's `model_extra` or custom serializer to handle dynamic conflict fields.

**Implementation Strategy**:
```python
class PPOTrainingResultDTO(TrainingResultBase):
    # ... all typed fields

    model_config = ConfigDict(extra="allow")  # Allow dynamic conflict.* fields

    def model_post_init(self, __context):
        """Validate that extra fields follow conflict.* naming."""
        for key in self.__dict__:
            if key not in self.model_fields:
                if not key.startswith("conflict."):
                    raise ValueError(f"Unknown field: {key}")
```

### Gaps and Solutions

**Gap 1**: `schema_version` not emitted
- **Solution**: DTO default value handles this
- **Risk**: None

**Gap 2**: Dynamic conflict stats handling
- **Solution**: Use `extra="allow"` with validation in `model_post_init`
- **Risk**: Low (well-established Pydantic pattern)

### Verdict

✅ **DTO schema is complete** — All current fields covered, including telemetry v1.0/1.1/1.2 variants.

---

## Anneal Output Validation

### Current Implementation

**Location**: `training_orchestrator.py:275-367`

**Output Structure**: `list[dict[str, object]]` where each dict is a stage result

#### BC Stage Result (Lines 313-326)

```python
stage_result: dict[str, object] = {
    "cycle": float(stage.cycle),
    "mode": "bc",
    "accuracy": accuracy,
    "loss": float(metrics.get("loss", 0.0)),
    "threshold": bc_threshold,
    "passed": accuracy >= bc_threshold,
    "bc_weight": float(stage.bc_weight),
}
if not stage_result["passed"]:
    stage_result["rolled_back"] = True
```

#### PPO Stage Result (Lines 354-359)

```python
summary_result = {
    "cycle": float(stage.cycle),
    "mode": "ppo",
    **summary,  # ← All PPO fields merged in
}
```

#### Final Return (Line 367)

```python
return results  # → list[dict[str, object]]
```

**Additional Context**:
- Status computed via `evaluate_anneal_results()` (line 364)
- Baselines tracked in `self._anneal_baselines` dict (line 306)
- Dataset label extracted from config (lines 299-304)
- Promotion tracking via `_record_promotion_evaluation()` (line 366)

### DTO Schema Coverage

**DTO**: `AnnealSummaryDTO` (dto_design.md:582-626)

| Field | In Current Output | Status | Notes |
|-------|-------------------|--------|-------|
| `stages` | ✅ (via `results` list) | Match | Each stage is dict with mode-specific fields |
| `status` | ✅ (computed, not returned) | **Gap** | Computed at line 364 but not included in return |
| `dataset_label` | ✅ (local var, not returned) | **Gap** | Extracted at line 299 but not included in return |
| `baselines` | ✅ (in `self._anneal_baselines`) | **Gap** | Tracked internally but not returned |
| `promotion_pass_streak` | ✅ (in `self._promotion_pass_streak`) | **Gap** | Tracked internally but not returned |
| `promotion_candidate_ready` | ⚠️ (derivable) | **Gap** | Can be derived from pass_streak vs required |

**DTO**: `AnnealStageResultDTO` (dto_design.md:460-580)

BC stage fields: ✅ All covered
PPO stage fields: ✅ All covered (via `**summary` spread)

### Architectural Gap Analysis

The current implementation returns `list[dict[str, object]]`, which is **incomplete** compared to the designed `AnnealSummaryDTO` structure.

**Current**:
```python
def run_anneal(...) -> list[dict[str, object]]:
    # ... process stages
    return results  # Just the stage list
```

**Designed**:
```python
def run_anneal(...) -> AnnealSummaryDTO:
    # ... process stages
    return AnnealSummaryDTO(
        stages=[AnnealStageResultDTO(**stage) for stage in results],
        status=self.evaluate_anneal_results(results),
        dataset_label=dataset_label,
        baselines=self._anneal_baselines.copy(),
        promotion_pass_streak=self._promotion_pass_streak,
        promotion_candidate_ready=self._promotion_pass_streak >= required_passes,
    )
```

### Gaps and Solutions

**Gap 1**: Status not included in return value
- **Current**: Computed at line 364, stored in `self._last_anneal_status`
- **Solution**: Include in DTO via `status=self.evaluate_anneal_results(results)`
- **Risk**: None (already computed)

**Gap 2**: Dataset label not returned
- **Current**: Local variable `dataset_label` at line 299
- **Solution**: Include in DTO via `dataset_label=dataset_label`
- **Risk**: None (already available)

**Gap 3**: Baselines not returned
- **Current**: Stored in `self._anneal_baselines` dict
- **Solution**: Include in DTO via `baselines=self._anneal_baselines.copy()`
- **Risk**: None (already tracked)

**Gap 4**: Promotion metrics not returned
- **Current**: Stored in `self._promotion_pass_streak` and computed from config
- **Solution**: Include in DTO
- **Risk**: None (already tracked)

### Verdict

⚠️ **DTO schema is more complete than current output** — This is a **design improvement**. The DTO wraps stage results with metadata that's currently computed but not returned.

**Migration Impact**: When extracting `AnnealStrategy`, we'll change the return type from `list[dict[str, object]]` to `AnnealSummaryDTO`, which is a **breaking change** for the orchestrator façade.

**Mitigation**:
1. Keep orchestrator façade method signature as `list[dict[str, object]]` (for CLI compatibility)
2. Add new method `run_anneal_typed(...) -> AnnealSummaryDTO` for type-safe callers
3. Shim: `def run_anneal(...) -> list[dict]: return self.run_anneal_typed(...).model_dump()["stages"]`

---

## Summary Table

| Training Method | Current Output | DTO Schema | Completeness | Notes |
|-----------------|----------------|------------|--------------|-------|
| `run_bc_training` | `dict[str, float]` | `BCTrainingResultDTO` | ✅ Complete | 2 optional fields added (duration, schema_version) |
| `run_ppo` | `dict[str, float]` | `PPOTrainingResultDTO` | ✅ Complete | Handles v1.0/1.1/1.2 telemetry variants, dynamic conflict fields |
| `run_anneal` | `list[dict[str, object]]` | `AnnealSummaryDTO` | ⚠️ **Enhanced** | DTO wraps stage list with status, baselines, promotion metadata |

---

## Implementation Checklist

When implementing DTOs in Phase 1, verify:

### BCTrainingResultDTO
- [ ] All required fields present in trainer output
- [ ] Add `duration_sec` timer to `BCStrategy.run()`
- [ ] `schema_version` defaults to "1.0.0" in DTO
- [ ] `.model_dump()` produces dict compatible with current CLI

### PPOTrainingResultDTO
- [ ] All core/health/v1.1/v1.2/baseline fields covered
- [ ] Dynamic conflict fields handled via `model_config = ConfigDict(extra="allow")`
- [ ] Validation ensures conflict fields follow naming convention
- [ ] Optional fields use `| None` with `default=None`

### AnnealSummaryDTO
- [ ] Wrap stage results in `AnnealStageResultDTO` instances
- [ ] Include `status` from `evaluate_anneal_results()`
- [ ] Include `dataset_label` from dataset resolution
- [ ] Include `baselines` copy from `_anneal_baselines`
- [ ] Include `promotion_pass_streak` and `promotion_candidate_ready`
- [ ] Orchestrator façade provides compatibility shim for CLI

---

## Testing Strategy

### Unit Tests

```python
def test_bc_result_dto_from_current_output():
    """Verify DTO accepts current trainer output."""
    current_output = {
        "mode": "bc",
        "manifest": "/path/to/manifest.json",
        "accuracy": 0.93,
        "loss": 0.15,
        "learning_rate": 1e-3,
        "batch_size": 32,
        "epochs": 10,
    }
    dto = BCTrainingResultDTO(**current_output)
    assert dto.accuracy == 0.93
    assert dto.loss == 0.15

def test_ppo_result_dto_with_v1_2_telemetry():
    """Verify DTO handles all telemetry versions."""
    # Test with full v1.2 output
    ppo_output = {
        "epoch": 5.0,
        "updates": 1000.0,
        # ... all v1.0/1.1/1.2 fields
        "anneal_loss_flag": False,
    }
    dto = PPOTrainingResultDTO(**ppo_output)
    assert dto.telemetry_version == 1.2

def test_anneal_summary_dto_wraps_stages():
    """Verify DTO wraps stage list correctly."""
    stages = [
        {"cycle": 0, "mode": "bc", "accuracy": 0.93, "passed": True},
        {"cycle": 0, "mode": "ppo", "loss_total": 0.12},
    ]
    dto = AnnealSummaryDTO(
        stages=[AnnealStageResultDTO(**s) for s in stages],
        status="PASS",
        dataset_label="rollout_001",
        baselines={},
    )
    assert len(dto.stages) == 2
    assert dto.status == "PASS"
```

### Golden Tests

Create fixtures in `tests/fixtures/dto/`:
- `bc_result_v1.json` — Sample BC output
- `ppo_result_v1_0.json` — Minimal PPO (telemetry v1.0)
- `ppo_result_v1_1.json` — Extended PPO (telemetry v1.1)
- `ppo_result_v1_2.json` — Full PPO with anneal context (v1.2)
- `anneal_summary.json` — Complete anneal run

Load and validate:
```python
def test_golden_bc_result():
    data = json.loads(Path("tests/fixtures/dto/bc_result_v1.json").read_text())
    dto = BCTrainingResultDTO(**data)
    assert dto.accuracy > 0.9
```

---

## Risk Assessment

| Risk | Severity | Mitigation | Status |
|------|----------|------------|--------|
| DTO schema missing fields | Medium | This validation document | ✅ Complete |
| Dynamic conflict fields break validation | Medium | Use `extra="allow"` + post-init validation | ✅ Mitigated |
| Anneal return type change breaks CLI | High | Compatibility shim in orchestrator | ✅ Mitigated |
| Duration tracking adds overhead | Low | Negligible (one perf_counter call) | ✅ Mitigated |
| DTO validation rejects valid legacy logs | Medium | Use lenient parsing in tests | ✅ Mitigated |

---

## Conclusion

✅ **DTO schemas are comprehensive and validated** against current outputs.

**Key Findings**:
1. BC and PPO DTOs cover all current fields
2. Anneal DTO is more complete than current output (design improvement)
3. Two minor additions needed: BC duration tracking, dynamic conflict field handling
4. Compatibility shims required for anneal return type change

**Next Steps**:
1. Implement DTOs in `townlet/dto/policy.py`
2. Add unit tests with current output samples
3. Add golden test fixtures
4. Update strategies to return DTOs
5. Add orchestrator façade compatibility shims
6. Verify CLI still works with `.model_dump()`
