# Stage 5 Cleanup Audit — 2025-10-11

Stage 5 of WP3C retired the final legacy-observation shims so DTO payloads are
the single source of truth for policy, telemetry, console, and replay flows.
This snapshot records the post-cleanup ground truth and the minimal shims that
remain for other programmes.

## Highlights

- **Adapters & factories** – `DefaultWorldAdapter.observe()` now returns the DTO
  `ObservationEnvelope`, and dummy runtimes mirror the same contract. The
  legacy world factory registry has been removed; `resolve_world` delegates to
  `townlet.factories.world_factory.create_world`.
- **Observation helpers** – the deprecated `townlet.world.observation` shim was
  deleted. All runtime code imports helper functions directly from
  `townlet.world.observations.{cache,context,views}`; documentation has been
  updated to match.
- **Telemetry & console** – simulation loop emits DTO-first payloads, the
  console router queues commands without touching `runtime.queue_console`, and
  downstream consumers read metrics from `global_context`. Legacy alias fields
  have been removed from loop health/failure payloads. Guard suites covering
  these paths continue to pass:
  `pytest tests/test_console_events.py tests/test_telemetry_surface_guard.py \
          tests/orchestration/test_console_health_smokes.py -q`.
- **Replay/export** – trajectory frames are DTO-enriched and
  `frames_to_replay_sample` converts them into replay tensors without touching
  legacy observation batches. Capture tooling (`scripts/capture_rollout.py`,
  `scripts/capture_scripted.py`) relies on these DTO frames.

## Verification bundle

```
pytest \
  tests/adapters/test_default_world_adapter.py \
  tests/factories/test_world_factory.py \
  tests/test_ports_surface.py \
  tests/policy/test_trajectory_service_dto.py::test_frames_to_replay_sample_preserves_dto_metadata \
  -q
```

## Remaining shims (tracked outside Stage 5)

| Location | Purpose | Notes |
| --- | --- | --- |
| `src/townlet/policy/bc.py` | Optional BC helper shim when Torch is absent | Intentional; owned by ML tooling programme. |

No other legacy observation dependencies remain; DTO envelopes and the derived
trajectory frames are the authoritative data path.
