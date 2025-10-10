# WP3 Status

**Current state (2025-10-09)**
- Scoping complete: WP3 owns the telemetry sink rework, policy observation flow, and the final simulation loop cleanup.
- Event schema drafted (`event_schema.md`) covering `loop.tick`, `loop.health`, `loop.failure`, `console.result`, and policy/stability payloads.
- `TelemetryEventDispatcher` implemented with bounded queue/rivalry caches and subscriber hooks; Stdout adapter now routes lifecycle events through the dispatcher, and the stub sink logs events via the same path.
- Legacy writer shims removed from `TelemetryPublisher`; the loop emits `loop.tick`/`loop.health`/`loop.failure`/`stability.metrics`/`console.result` events exclusively. HTTP/streaming transports must consume dispatcher events before reactivation.
- HTTP transport now posts dispatcher events via simple JSON POSTs; streaming/WebSocket transport remains a TODO once external consumers require it.
- Telemetry guard tests cover the event-only surface and dispatcher smoke path, preventing regressions while DTO work proceeds.
- DTO Step 1 complete: `dto_observation_inventory.md` documents an attribute→consumer map, and `dto_example_tick.json` provides a baseline envelope for schema validation (with planned `dto_schema_version` + Pydantic checks).
- DTO schema surface scaffolded at `src/townlet/world/dto/observation.py` (exported via `townlet.world.dto`) with `DTO_SCHEMA_VERSION = 0.1.0`; converter helper `build_observation_envelope`, fixture-backed smoke tests (`tests/world/test_observation_dto_factory.py`), and a loop-level parity harness (`tests/core/test_sim_loop_dto_parity.py`) now exist—`SimulationLoop` caches/forwards envelopes while we complete world detachment.
- DTO envelope now includes queue rosters, running affordances, and relationship metrics (`src/townlet/world/dto/observation.py`, `src/townlet/world/dto/factory.py`, `src/townlet/core/sim_loop.py`), with tests/fixtures updated accordingly.
- Scripted behaviour path consumes DTO-backed queue/affordance/relationship views via `DTOWorldView`, and guardrail mutations emit `policy.guardrail.request` events with `WorldState` dispatching the resulting chat/block effects (tests: `tests/policy/test_dto_world_view.py`, `tests/world/test_guardrail_events.py`).
- Modular world tick now processes combined actions via `affordances.process_actions`, eliminating
  the extra `WorldState.apply_actions` bridge while keeping parity; DTO queue snapshots normalise
  entries so guardrails receive agent strings (tracked for further cleanup in WP3B). `queues.step`
  now handles ghost-step queue conflicts, ensuring rivalry events continue to emit without the
  legacy loop, and `advance_running_affordances` drives affordance completion/hand-over via the
  runtime service.
- Behaviour parity smokes (`tests/test_behavior_personality_bias.py`) are green again; DTO parity
  harness still needs reward/ML coverage.
- New work packages:
  - **WP3B – Modular Systems Reattachment**: finish queue/affordance/employment steps then drop the
    bridge.
  - **WP3C – DTO Parity Expansion & ML Validation**: enhance parity harness, run ML smoke, retire
    legacy observation payloads.
- WP1 telemetry blockers cleared; remaining dependency is routing console commands without `runtime.queue_console`. WP2 still requires observation-first DTOs.
- WP2 adapters still expose `legacy_runtime` handles so policy consumers can pull `WorldState`; observation-first DTOs from WP3 will remove that dependency.

**Dependencies**
- Unblocks WP1 Step 8 (removal of legacy telemetry writers and `runtime.queue_console` usage).
- Unblocks WP2 Step 7 (policy/world adapters still exposing legacy handles until observation-first DTOs are available).

**Upcoming Milestones**
1. Telemetry event API & sink refactor.
2. Policy observation/controller update (port-driven decisions, metadata streaming).
3. Loop finalisation & documentation sweep (complete WP1/WP2 blockers).

Update this file as WP3 tasks progress.
