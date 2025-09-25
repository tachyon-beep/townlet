# Conflict-Aware Training Harness Work Package

## Objective
Stand up the initial RL training harness capable of consuming conflict-aware observation features and telemetry, ensuring replay tooling and validation loops exercise rivalry signals before introducing learned policies.

## Scope
- `src/townlet/policy/runner.py` / Replay utilities / future PPO integration stubs.
- Observation + telemetry sample replay (`scripts/run_replay.py`) and replay batch loaders.
- Documentation and validation scripts demonstrating rivalry-aware inputs.

## Deliverables
1. Training harness scaffold that ingests observation tensors (including rivalry features) and logs minibatch stats.
2. Replay pipeline that converts sample NPZ/JSON into training-ready tensors and exposes a configurable batch iterator.
3. Validation checklist + automated tests covering replay loader, batching iterator, and harness integration.
4. Updated documentation (implementation notes, training guide) and sample usage instructions.

## Tasks
1. **Design / API Alignment**
   - Finalise tensor-to-batch API for upcoming PPO integration; document expected shapes (map, feature, metadata) including conflict features.
   - Specify telemetry→dataset ingestion contract (e.g., NDJSON fields for queue conflicts) to ensure replay and live streams align.
2. **Loader Implementation**
   - Extend `townlet.policy.replay` with batching utilities and dataset iterator capable of shuffling/multi-sample stacking.
   - Add conflict feature assertions and optional normalisation hooks for future PPO consumption.
3. **Harness Scaffold Updates**
   - Enhance `TrainingHarness` to expose replay batch runs (`run_replay_batch`) and log summary stats; wire CLI (`scripts/run_training.py`) to accept multiple samples.
   - Integrate with future PPO stub (no-op for now) to verify shapes.
4. **Testing & Docs**
   - Add pytest coverage for loader, batching, and harness CLI path.
   - Update `docs/IMPLEMENTATION_NOTES.md`, `docs/design/OBSERVATION_TENSOR_SPEC.md`, and training workflow guides; log telemetry change entry if schema touched.

## Risks
- **Schema drift**: loader must tolerate future observation additions; guard with metadata version check.
- **Batch mismatch**: inconsistent map/feature shapes across samples break stacking—validate before stacking.
- **Scaling**: replay loader may need streaming capabilities; document limitations.

## Success Criteria
- Running `python scripts/run_training.py configs/examples/poc_hybrid.yaml --replay-sample ...` outputs conflict-aware stats and batch summary without error.
- Tests cover replay loader, batch iterator, and CLI integration.
- Docs highlight replay workflow; change log references new capability.
