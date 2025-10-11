# WP3 Context Snapshot (2025-10-10)

Use this as reorientation material if the working memory is compacted. It summarises current state, blockers, and the next concrete actions across WP1–WP3.

## Telemetry (WP3 Section 1)

- **Event Schema**: Defined in `event_schema.md` covering `loop.tick`, `loop.health`, `loop.failure`, `console.result`, `policy.metadata`, `stability.metrics`, and `rivalry.events`.
- **Dispatcher**: `TelemetryEventDispatcher` implemented with bounded queue/rivalry caches and subscriber hooks. Registered inside `TelemetryPublisher` (see `_handle_event`).
- **Transports**:
  - `StdoutTelemetryAdapter` and `StubTelemetrySink` emit events through the dispatcher; publisher shims have been removed.
  - HTTP transport now posts dispatcher events; streaming/WebSocket transports remain inactive until downstream consumers need them.
- **Loop Emission**: `SimulationLoop` emits events exclusively for console results, stability metrics, loop health/failure, and loop tick; it no longer calls `record_*` directly.
- **Next steps**: Expand transport coverage to streaming/WebSocket once required and keep parity checks running while the DTO rollout proceeds.

## Policy DTOs (WP3 Section 2)

- Current status: `PolicyController` still delegates to `PolicyRuntime.decide(world, tick)` but all decisions consume DTO envelopes; fallback logging remains for missing data during migration.
- DTO schema models scaffolded at `src/townlet/world/dto/observation.py` (re-exported via `townlet.world.dto`); converter helper `build_observation_envelope`, fixture smoke tests, and a loop parity harness (`tests/core/test_sim_loop_dto_parity.py`) exist. `SimulationLoop` caches/emits the envelope while policy/world detachment remains, and the envelope carries queue rosters, running affordances, and relationship metrics for DTO adapters.
- Scripted behaviour now consumes the DTO-backed queue/affordance/relationship views (`DTOWorldView`) and guardrail mutations emit `policy.guardrail.request` events; legacy fallbacks remain for envelopes absent during migration. Unit coverage lives in `tests/policy/test_dto_world_view.py` and `tests/world/test_guardrail_events.py`.
- `WorldContext.tick` routes combined actions through `affordances.process_actions`
  (extracted from `WorldState.apply_actions`), eliminating the extra legacy bridge while keeping
  behaviour parity. DTO queue snapshots normalise to agent identifiers to keep guardrails compatible,
  `queues.step` captures ghost-step conflicts, and `advance_running_affordances` handles
  completion/hand-over events via the runtime service.
- Scripted behaviour now consumes DTO-backed agent snapshots/iterators provided by `DTOWorldView`;
  guard tests (`tests/policy/test_scripted_behavior_dto.py`) cover pending-intent promotion, chat
  selection, and rivalry avoidance without touching legacy world state.
- `TrajectoryService.flush_transitions` accepts DTO envelopes (with anneal context preserved) and the
  training orchestrator consumes DTO-backed trajectory frames (`tests/policy/test_trajectory_service_dto.py`,
  `tests/policy/test_training_orchestrator_capture.py`).
- Scripted parity smokes (`tests/test_behavior_personality_bias.py`) now pass; reward/ML parity
  remains outstanding for DTO-only validation.
- Todo:
  - Define observation DTOs from `WorldContext`/observation builder.
  - DTO-driven policy events (`policy.metadata` / `policy.possession` / `policy.anneal.update`) stream from `SimulationLoop`; finish migrating ML adapters to the DTO pathway before retiring remaining legacy hooks.
  - DTO ML smoke harness (`tests/policy/test_dto_ml_smoke.py`) keeps torch-based parity between DTO and legacy feature tensors; integrate into automated ML workflows next.
  - Adjust training/orchestrator code to the new DTO flow and record updated parity baselines.

## Simulation Loop Cleanup (WP3 Section 3)

- Console commands now flow through `ConsoleRouter.enqueue`, which forwards them to the world runtime and records telemetry; if the router is absent the loop drops buffered commands with a warning. `SimulationLoop.step` no longer calls `runtime.queue_console` and the new smoke (`tests/core/test_sim_loop_modular_smoke.py`) covers DTO envelopes plus console telemetry.
- World factory + adapter always operate on `WorldContext.observe`; the legacy ObservationBuilder fallback is gone from the loop, and `DefaultWorldAdapter.observe` simply proxies the context with fresh unit coverage in `tests/adapters/test_default_world_adapter.py`. Remaining work is to migrate adapter-side observation helpers/tests to the DTO-native path (T2.4) and keep ML parity in sync.
- Plan: finish ML parity work, complete failure/snapshot refactors, add the promised health-monitor smokes, and mark WP1 Step 8 / WP2 Step 7 complete.

## Cross-Package Dependencies

- **WP1** waits on WP3 for: observation-first policy decisions (ML parity) and failure/snapshot refactors.
- **WP2** waits on WP3 for: observation DTO schema (done) and removal of legacy adapter shims; once DTO-only ML parity lands we can drop the ObservationBuilder/queue-console compatibility paths.
- **WP3 telemetry cleanup** now focuses on transport parity and guard tests before WP1/WP2 closure.
- Transitional bridge removal (legacy apply/resolves) is tracked under WP3B once modular systems are fully operational.

## Immediate Next Steps

1. **Telemetry**: Complete T4.2b by routing console result emissions entirely through the dispatcher (`TelemetryPublisher.emit_event`) and removing any lingering direct writer calls.
2. **Loop Smokes**: Implement T4.5a integration tests (`tests/core/test_sim_loop_modular_smoke.py`) exercising default providers plus console routing.
3. **Adapter Coverage**: Expand adapter tests (T2.4) to cover the DTO-only observe path and guard against regression.
4. **Docs**: Update ADR-001 / console docs once telemetry + loop cleanup completes; sync WP1/WP2 briefs with the latest DTO-only architecture.

Keep this snapshot updated if major structural decisions change.
