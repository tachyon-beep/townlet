# Behaviour Cloning Trajectory Capture Schema (Draft)

## Overview
Behaviour cloning trajectories reuse the replay sample structure (NPZ + JSON metadata) with additional
labels to support dataset curation. Each capture writes:

- `*.npz` — arrays (`map`, `features`, `actions`, `old_log_probs`, `value_preds`, `rewards`, `dones`)
- `*.json` — metadata (feature names, action lookup, quality metrics, tags)

## NPZ Structure
- `map`: `(T, H, W, C)` float32
- `features`: `(T, F)` float32 (includes conflict features: `rivalry_max`, `rivalry_avoid_count`)
- `actions`: `(T,)` int64
- `old_log_probs`: `(T,)` float32 (optional; set to zero if unavailable)
- `value_preds`: `(T+1,)` float32 (final entry duplicates last prediction)
- `rewards`: `(T,)` float32 (per-step reward)
- `dones`: `(T,)` bool

## Metadata Fields (JSON)
- `agent_id`: source agent identifier
- `trajectory_id`: unique capture identifier
- `feature_names`: ordered list of feature names (must include `rivalry_max`, `rivalry_avoid_count`)
- `action_lookup`: mapping serialized like replay samples
- `timesteps`: integer T
- `value_pred_steps`: integer V (T+1)
- `action_dim`: integer |actions| (max action ID + 1)
- `tags`: list of strings (scenario, scripted policy variant)
- `quality_metrics`: mapping (`coverage`, `reward_sum`, etc.)
- `capture_summary`: optional free-text notes

## Example
```json
{
  "agent_id": "queue_script",
  "trajectory_id": "queue_conflict_bc_0001",
  "feature_names": [...],
  "action_lookup": {"{\"kind\": \"wait\"}": 0, "{\"kind\": \"request\", ...}": 1},
  "timesteps": 120,
  "value_pred_steps": 121,
  "action_dim": 4,
  "tags": ["queue_conflict", "scripted_v1"],
  "quality_metrics": {"coverage": 0.92, "reward_sum": 4.5},
  "capture_summary": "Ghost-step scenario with polite handover branch"
}
```

## Quality Metrics (to populate during curation)
- `timesteps`: number of steps in the trajectory.
- `reward_sum`: cumulative reward across the trajectory.
- `mean_reward`: average reward per step (derived).
- `done_count`: number of terminal steps.
- `coverage`: fraction of scripted behaviours exercised (scenario-specific; optional until defined).
- `constraint_violations`: counts per constraint (scenario-specific; optional).
- Scenario metrics (e.g., average queue wait, punctuality score, rivalry window coverage) to be added per scripted policy.

## Validation
- `tests/test_bc_capture_prototype.py` ensures schema round-trip compatibility
- Future work: lint/CI check to confirm feature names + required fields before dataset ingestion
