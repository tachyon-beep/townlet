# WP3 Context Snapshot (2025-10-09)

Use this as reorientation material if the working memory is compacted. It summarises current state, blockers, and the next concrete actions across WP1–WP3.

## Telemetry (WP3 Section 1)

- **Event Schema**: Defined in `event_schema.md` covering `loop.tick`, `loop.health`, `loop.failure`, `console.result`, `policy.metadata`, `stability.metrics`, and `rivalry.events`.
- **Dispatcher**: `TelemetryEventDispatcher` implemented with bounded queue/rivalry caches and subscriber hooks. Registered inside `TelemetryPublisher` (see `_handle_event`).
- **Transports**:
  - `StdoutTelemetryAdapter` and `StubTelemetrySink` emit events through the dispatcher; publisher shims have been removed.
  - HTTP transport now posts dispatcher events; streaming/WebSocket transports remain inactive until downstream consumers need them.
- **Loop Emission**: `SimulationLoop` now emits events exclusively for console results, stability metrics, loop health/failure, and loop tick; it no longer calls `record_*` directly.
- **Next steps**: Add guard tests preventing reintroduction of writer APIs and update dormant transports (HTTP/streaming) to consume dispatcher events.

## Policy DTOs (WP3 Section 2)

- Current status: `PolicyController` facade exists but still delegates to `PolicyRuntime.decide(world, tick)`.
- Todo:
  - Define observation DTOs from `WorldContext`/observation builder.
  - Update policy adapters (scripted + ML) to consume DTO batches and emit `policy.metadata` / `policy.possession` / `policy.anneal.update` events via telemetry.
  - Adjust training/orchestrator code to the new DTO flow.

## Simulation Loop Cleanup (WP3 Section 3)

- Remaining direct legacy usage:
  - `runtime.queue_console` still invoked by the loop (console commands forwarded to legacy runtime). Need router-driven apply path.
  - Loop still mutates `WorldState` (`world.agents`) directly; needs `WorldContext` helpers/DTOs after WP2/WP3 DTO work.
- Plan: once policy DTOs are in place and telemetry events are fully streamed, remove `runtime.queue_console`, drop `legacy_runtime` handles, and mark WP1 Step 8 / WP2 Step 7 complete.

## Cross-Package Dependencies

- **WP1** waits on WP3 for: observation-first policy decisions and removal of `runtime.queue_console`.
- **WP2** waits on WP3 for: observation DTO schema so adapters expose DTOs instead of raw `WorldState`.
- **WP3 telemetry cleanup** now focuses on transport parity and guard tests before WP1/WP2 closure.

Keep this snapshot updated if major structural decisions change.
