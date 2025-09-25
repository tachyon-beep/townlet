# Conflict-Aware Replay DataLoader Work Package

## Objective
Build a reusable replay dataloader that batches observation/telemetry samples—including rivalry signals—so future PPO/BC pipelines can consume conflict-aware inputs and validate behaviour prior to live training.

## Scope
- `townlet.policy.replay`: dataset abstractions, shuffling/iterator interfaces, schema validation.
- Training harness CLI (`scripts/run_training.py`) and eventual PPO hooks consuming the dataloader.
- Documentation and tests covering replay batches, feature schemas, and telemetry alignment.

## Deliverables
1. Dataset abstraction that loads observation NPZ/JSON (and optionally telemetry NDJSON) into memory or streaming iterators with configurable batch size/shuffle/seed.
2. Conflict-aware feature normalization/inspection utilities (e.g., stats logging for rivalry_max and queue_conflict counts).
3. Integration into training harness: `TrainingHarness` exposes iterator factory; CLI accepts dataset manifest.
4. Tests for dataset loading, batching, and conflict metric preservation; docs updated (implementation notes, training guide).

## Plan
### Phase 1 — API & Schema Alignment
- Define `ReplayDatasetConfig` (paths, batch size, shuffle, drop_last) and document expected file formats (observation NPZ + metadata JSON, optional telemetry JSON/NDJSON).
- Extend `ReplaySample` metadata with version info; add schema check for conflict feature presence.

### Phase 2 — Dataset Implementation
- Implement `ReplayDataset` collecting multiple samples, verifying shape compatibility, and exposing `__len__`, `__iter__` returning `ReplayBatch`.
- Add optional streaming loader (generator) that loads sample per iteration to limit memory footprint.

### Phase 3 — Training Harness Hookup
- Update `TrainingHarness` with `build_replay_dataloader(dataset_config)` returning iterator.
- CLI accepts `--replay-manifest` (YAML/JSON list) to drive dataset creation; retains single-sample path for quick checks.
- Log per-batch statistics (mean rivalry, avoid counts) to stdout for early inspection.

### Phase 4 — Validation & Docs
- Pytests: dataset shape/len checks; shuffle determinism with seed; CLI integration smoke using manifest with conflict-high/low samples.
- Documentation updates: `docs/IMPLEMENTATION_NOTES.md`, training guide quickstart, observation spec referencing manifest usage.

## Risks
| Risk | Impact | Mitigation | Risk Reduction Activity |
| --- | --- | --- | --- |
| Schema drift breaks loader | High | Embed feature name validation + version guard; unit tests with samples | Add schema-check unit test covering rivalry features |
| Batch shape mismatch (heterogeneous windows) | Medium | Validate shape before stacking; provide friendly error | Implement loader pre-flight validation + specific error message |
| Memory pressure with large datasets | Medium | Support streaming iterator + `batch_size` limit | Provide streaming path, document memory considerations |
| Telemetry alignment gaps | Medium | Define telemetry schema excerpt with queue_conflict fields; add sample check | Create telemetry schema test verifying event format |
| Shuffle determinism for training | Low | Use seeded RNG; expose `seed` param in config | Unit test verifying deterministic order with fixed seed |

## Risk Reduction Activities
1. Schema Guard Tests — ensure loader asserts presence of `rivalry_max`/`rivalry_avoid_count` and observation variant metadata before batching.
2. Sample Validation Tool — extend `scripts/run_replay.py --validate` to check schema and print warnings.
3. Streaming Prototype — implement generator path and measure memory usage; add documentation on best practices.
4. Telemetry Sample Check — add pytest ensuring conflict telemetry sample matches expected fields (intensity, reason, queue length).

## Success Criteria
- `python scripts/run_training.py ... --replay-manifest docs/samples/replay_manifest.json` iterates through batches, logging conflict stats.
- Tests cover dataset loader, seeded shuffle, CLI integration.
- Docs describe replay dataset workflow and manifest format.
