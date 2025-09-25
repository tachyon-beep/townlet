# Observation Tensor Specification (Hybrid Variant) — Draft v2025-09-25

## 1. Goals
- Replace placeholder observation payloads with deterministic tensors for the hybrid variant described in `docs/HIGH_LEVEL_DESIGN.md` (§6).
- Enable renderer/UI to consume consistent map/scalar/social features.
- Provide a layout that can be extended in later phases (social snippets, personality) without breaking schema.

## 2. Feature Overview
| Component | Description | Source | Shape |
| --- | --- | --- | --- |
| Local map | Egocentric 11×11 window (centered on agent) with 4 channels: occupancy, object type, agent type, reservations | `WorldState` grid + objects | (4, 11, 11) |
| Target bearings | Normalised vectors + distance to fridge/stove/bed/shower | Precomputed world metadata | (4, 3) (dx, dy, dist per target) |
| Self scalars | Needs (hunger, hygiene, energy), wallet, lateness counter, on_shift flag, time-of-day sin/cos | Agent snapshot + config | (8,) |
| Employment stats | shift_state one-hot (4), attendance ratio, wages_withheld | Agent snapshot | (6,) |
| Embedding slot | Integer slot normalised (slot / max_slots) | Embedding allocator | (1,) |
| Context flags | `ctx_reset_flag`, `episode_step_norm` | Builder state | (2,) |
| Social placeholder | Zero vector reserved for future (length 16) | N/A | (16,) |
| Conflict features | Rivalry max magnitude and avoid-count derived from ledger top-K | `WorldState.rivalry_top` | (2,) |

Total flattened length ≈ 4×11×11 + 8 + 6 + 1 + 2 + 16 + 2 = 531 values.
Reference sample: `docs/samples/observation_hybrid_sample.npz` (with metadata JSON alongside).

## 3. Tensor Layout
- Use `numpy.ndarray` with dtype `float32`.
- Layout: concatenate features into a single vector; maintain map as channels-first (C,H,W) for downstream CNN.
- Provide metadata dict alongside tensor: `{ "map_shape": (4,11,11), "feature_slices": {...} }` to help consumers.

## 4. Config knobs
- `observations.hybrid.local_window`: odd integer (default 11).
- `observations.hybrid.include_targets`: bool.
- Schema added to `SimulationConfig` with validation (odd window, >=3).

## 5. Open Questions
- Do we need occupancy for walls? Proposed to treat unknown as 0.
- Time-of-day derived from tick? Need baseline for sin/cos (e.g., 1440 ticks per day).

Approval Checklist:
- [x] Architecture sign-off (2025-09-25, Project Director)
- [x] Product sign-off (2025-09-25, Project Director)
- [ ] Renderer buy-in (placeholder OK)

Next steps: implement neighborhood helper, config nodes, encoding per plan.

Replay validation command:
```bash
source .venv/bin/activate && python scripts/run_training.py configs/examples/poc_hybrid.yaml --replay-sample docs/samples/observation_hybrid_sample_base.npz --replay-meta docs/samples/observation_hybrid_sample_base.json
```

Sample manifest for batching:
```
cat docs/samples/replay_manifest.json
```
