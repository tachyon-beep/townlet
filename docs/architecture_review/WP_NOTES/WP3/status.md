# WP3 Status

**Current state (2025-10-09)**
- Scoping complete: WP3 owns the telemetry sink rework, policy observation flow, and the final simulation loop cleanup.
- Event schema drafted (`event_schema.md`) covering `loop.tick`, `loop.health`, `loop.failure`, `console.result`, and policy/stability payloads.
- `TelemetryEventDispatcher` implemented with bounded queue/rivalry caches and subscriber hooks; Stdout adapter now routes lifecycle events through the dispatcher, and the stub sink logs events via the same path.
- Legacy writer shims removed from `TelemetryPublisher`; the loop emits `loop.tick`/`loop.health`/`loop.failure`/`stability.metrics`/`console.result` events exclusively. HTTP/streaming transports must consume dispatcher events before reactivation.
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
