# Observation Module Test Plan (Phase 4)

This placeholder documents the parity checks we will add once the observation
helpers move under `townlet.world.observations` and the runtime adapter lands.

## Parity Suites
- `test_observation_builder_parity.py`: compare feature vectors/map tensors from
  the new `ObservationService` against the Phase 0 baseline captured in
  `tmp/wp-c/phase4_baseline_shapes.json`.
- `test_world_runtime_adapter_views.py`: validate that the adapter exposes the
  same read-only views (agents, objects, queue snapshots, relationship metrics)
  currently provided by `WorldState`; mocks will assert immutability.
- `test_snapshot_precondition_context.py`: ensure JSON-serialisable payloads
  emitted through the adapter match prior expectations in
  `tests/test_world_observation_helpers.py`.

## Fixture Work
- Extend the existing fixture world from `tests/test_observation_builder.py` into
  a shared factory so both legacy and adapter-based tests can reuse the same
  state setup.
- Capture additional telemetry baselines (relationship deltas, queue metrics)
  after the adapter extraction to compare against
  `tmp/wp-c/phase4_baseline_telemetry.jsonl`.
- Add goldens for compact/full variants if Phase 4 alters channel ordering.
