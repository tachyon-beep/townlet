# Observation Tensor Specification — v2025-10-23

Townlet exposes three observation variants (`hybrid`, `full`, `compact`). Each
variant includes a shared scalar feature bundle and then adds variant-specific
spatial detail. This document lists the feature layout, map semantics, and how
to regenerate golden fixtures for regressions.

## 1. Shared Scalar Feature Bundle

All variants emit the following scalars in the order shown:

- Needs: `need_hunger`, `need_hygiene`, `need_energy`
- Economy: `wallet`
- Employment: `lateness_counter`, `on_shift`, `attendance_ratio`, `wages_withheld`
- Time embedding: `time_sin`, `time_cos` (tick-based with
  `observations.hybrid.time_ticks_per_day`, default 1440)
- Shift state one-hot: `shift_pre`, `shift_on_time`, `shift_late`, `shift_absent`, `shift_post`
- Embedding allocator: `embedding_slot_norm`
- Lifecycle flags: `ctx_reset_flag`, `episode_progress`
- Rivalry metrics: `rivalry_max`, `rivalry_avoid_count`
- Last-action metadata: `last_action_id_hash` (blake2s/float32), `last_action_success`,
  `last_action_duration`
- Environment flags: `reservation_active`, `in_queue`
- Path hint logits: `path_hint_north`, `path_hint_south`, `path_hint_east`, `path_hint_west`
- Landmark bearings/distances (optional): for each of `fridge`, `stove`, `bed`, `shower`
  we append `<name>_dx`, `<name>_dy`, `<name>_dist`
- Personality traits (optional): when `features.observations.personality_channels`
  is enabled the builder appends `personality_extroversion`,
  `personality_forgiveness`, and `personality_ambition` to expose the live trait
  vector. Metadata also carries the resolved profile name plus configured
  multipliers for quick inspection.
- Social snippet: `social_slot{n}_d{m}` entries plus aggregates when
  `include_aggregates` is enabled. Each slot packs the hashed agent embedding
  followed by trust, familiarity, and rivalry scores derived from the relationship
  ledger. When relationship data are disabled the builder falls back to rivalry
  edges (for avoidance context) and flags the snippet as empty in metadata.
  Aggregates compute mean/max trust and rivalry across populated slots.

Episode progress derives from `agent_snapshot.episode_tick` divided by
`time_ticks_per_day` (wraps each day). Last-action fields are updated whenever the
world processes actions (request/move/start/release/blocked).

## 2. Hybrid Variant

| Component | Description | Source | Shape |
| --- | --- | --- | --- |
| Local map | Egocentric 11×11 window with 4 channels: `self`, `agents`, `objects`, `reservations` | `townlet.world.observation.local_view()` | (4, 11, 11) |
| Scalars | Shared bundle (§1) | Observation builder | ~70 (`+3` when personality channels enabled) |
| Social snippet | Optional top friends/rivals embeddings | Relationships ledger | configurable |

Reference sample: `docs/samples/observation_hybrid_sample.npz` (metadata JSON alongside).

## 3. Full Variant

| Component | Description | Source | Shape |
| --- | --- | --- | --- |
| Local map | Egocentric 11×11 window with 6 channels: `self`, `agents`, `objects`, `reservations`, `path_dx`, `path_dy` | `townlet.world.observation.local_view()` | (6, 11, 11) |
| Scalars | Shared bundle (§1) | Observation builder | ~74 (`+3` when personality channels enabled) |
| Social snippet | Optional | Relationships ledger | configurable |

`path_dx/path_dy` encode normalized directional vectors per tile based on relative offsets.
`metadata['map_channels']` lists channel order; `metadata['landmark_slices']` records
(start, stop) indices for each landmark triple.

## 4. Compact Variant

| Component | Description | Source | Shape |
| --- | --- | --- | --- |
| Feature vector | Shared bundle (§1) plus local summary scalars (`neighbor_agent_ratio`, `neighbor_object_ratio`, `reserved_tile_ratio`, `nearest_agent_distance`) | Observation builder | ~84 (`+3` when personality channels enabled) |
| Map tensor | Not used (placeholder zeros) | — | (0, 0, 0) |

Compact omits the spatial map entirely. Instead, the builder encodes a coarse
summary of the local egocentric window: counts and ratios for neighboring
agents/objects/reservations and the normalized distance to the nearest other
agent. These values populate the new scalar features and appear in
`metadata['local_summary']` for downstream inspection. Consumers should branch
when `metadata['map_shape'] == (0, 0, 0)` and rely on the summary bundle rather
than expecting spatial grids.

## 5. Social Snippet Behaviour

Social slots may be included with any variant provided relationships stage ≥ `A`. Each
slot contributes `embed_dim + 3` floats (embedding + trust/familiarity/rivalry) plus
optional aggregates when `include_aggregates` is true. Disable `top_friends`/`top_rivals`
for compact/full fixtures when social context is unnecessary. The builder now backfills
friendship/rivalry data from the live relationship ledger every tick, ensuring compact
variants expose the same context operators see in telemetry.

Metadata emitted alongside each observation now includes a `social_context` block:

```json
"social_context": {
  "configured_slots": 4,
  "slot_dim": 11,
  "filled_slots": 2,
  "relation_source": "relationships",
  "aggregates": ["social_trust_mean", "social_trust_max", "social_rivalry_mean", "social_rivalry_max"],
  "has_data": true
}
```

`relation_source` reports whether the data originated from the relationship ledger,
the rivalry fallback, or if no data were found (`"empty"`). Consumers should prefer
metadata rather than hard-coded indices when interpreting social values.

## 6. Configuration Knobs

- `features.systems.observations`: `hybrid` (default), `full`, or `compact`
- `features.observations.personality_channels`: gate the personality trait channel
  and metadata bundle (defaults to `false` for backward compatibility)
- `observations.hybrid.local_window`: odd integer ≥3 (hybrid/full map size)
- `observations.hybrid.include_targets`: whether to append landmark bearings/distances
- Social snippet controls: `observations.social_snippet.*`

## 7. Regenerating Golden Fixtures

```bash
# Hybrid sample regeneration
source .venv/bin/activate
python scripts/run_training.py \
  configs/examples/poc_hybrid.yaml \
  --replay-sample docs/samples/observation_hybrid_sample_base.npz \
  --replay-meta docs/samples/observation_hybrid_sample_base.json

# Full variant smoke
python - <<'PY'
from pathlib import Path
from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop

config = load_config(Path("configs/examples/poc_hybrid.yaml"))
config.features.systems.observations = "full"
loop = SimulationLoop(config)
obs = loop.observations.build_batch(loop.world, terminated={})
print("full map channels:", obs[next(iter(obs))]["metadata"]["map_channels"])
PY

# Compact variant smoke
python - <<'PY'
from pathlib import Path
from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop

config = load_config(Path("configs/examples/poc_hybrid.yaml"))
config.features.systems.observations = "compact"
loop = SimulationLoop(config)
obs = loop.observations.build_batch(loop.world, terminated={})
sample = next(iter(obs.values()))
print("compact features shape:", sample["features"].shape)
print("first feature names:", sample["metadata"]["feature_names"][:10])
PY
```

## 8. Approval Notes

- Architecture sign-off: 2025-09-30 (Project Director)
- Product sign-off: 2025-09-30 (Project Director)
- Renderer integration: ensure UI handles empty map tensor for compact variant before release

Future improvement: replace Manhattan-based path hints with real navigation hints from
the pathing system once available.
