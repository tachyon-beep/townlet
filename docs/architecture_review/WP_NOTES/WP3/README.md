# WP3 — Telemetry & Policy Modernisation

Purpose: capture the design intent, decisions, and progress for Work Package 3. This package delivers the remaining port refactors that unblock WP1 and WP2, with emphasis on an event-driven telemetry sink, observation-first policy orchestration, and the final simulation loop cleanup.

## Context

- WP1 introduced minimal ports/factories and now emits loop state via `ConsoleRouter`, `HealthMonitor`, and telemetry events. Telemetry writer methods have been removed; remaining work is to route console commands without touching `runtime.queue_console`.
- WP2 modularised the world context and systems. Adapters expose transitional handles, but the loop still feeds the scripted backend raw `WorldState` objects. Observation-first policy decisions and DTO streaming depend on WP3.
- WP3 therefore owns the remaining substrate changes required to retire legacy getters, writers, and world references.

## Goals

1. Maintain an event/metric streaming telemetry sink (`emit_event`/`emit_metric`) so composition code never mutates publisher internals.
2. Provide canonical DTOs for policy/telemetry consumers driven by the modular world context (observation-first policy decisions, queue/relationship metrics, rivalry feeds).
3. Finalise the simulation loop migration: world actions via port APIs only, telemetry purely event-driven, policy surface independent of `WorldState`.

## Deliverables

- Event-first telemetry sink (`TelemetrySink.emit_event/emit_metric`) that handles:
  - tick lifecycle (`loop.tick`, `loop.health`, `loop.failure`)
  - console results (`console.result`)
  - policy/health/stability metrics
- Updated adapters (`StdoutTelemetryAdapter`, HTTP sink, stubs) translating the new events to existing transports.
- Policy DTO exporter (observation-first `decide` inputs, metadata events) and removal of `PolicyRuntime` leaks.
- DTO envelope enriched with queue/affordance/relationship context to support DTO-only policy decisions.
- Finalised `SimulationLoop` implementation using only port surfaces.

## Dependencies & Blockers

- **Blocks WP1 Step 8 completion:** loop still calls `record_console_results`, `record_health_metrics`, `record_loop_failure`, and delegates world actions via `runtime.queue_console`. WP3 must ship replacement events/port helpers before WP1 can delete the old path.
- **Blocks WP2 adapter finalisation:** policy still consumes `WorldState` directly; observation-driven DTOs planned in WP3 remove that dependency.
- The telemetry transport refactor must keep stdout/HTTP compatibility so downstream tooling (dashboards, promotion pipeline) continue functioning during rollout.
-
WP1 / WP2 progress trackers should cross-link to the matching WP3 tasks (see `tasks.md`).

## Current Progress

- Event schema drafted (`event_schema.md`) covering `loop.tick`, `loop.health`, `loop.failure`, `console.result`, and policy/stability payloads.
- `TelemetryEventDispatcher` implemented with bounded queue/rivalry caches and subscriber hooks; stdout and stub adapters now route events through the dispatcher.
- Simulation loop emits `loop.tick/health/failure`, `console.result`, and `stability.metrics` events exclusively; legacy writer shims have been removed from the publisher.
- HTTP transport now relays dispatcher events via JSON POST requests; streaming/WebSocket transport remains a placeholder until required by downstream consumers.

## Execution Priorities

1. **Telemetry cleanup** – update any remaining transports (e.g., HTTP) to consume dispatcher events and add guard tests to prevent regression.
2. **Policy DTO rollout** – provide observation DTOs and policy metadata events so WP1/WP2 can drop `WorldState` access.
3. **Loop finalisation** – remove `runtime.queue_console`, ensure all telemetry/policy interactions flow through ports, and close out WP1 Step 8 / WP2 Step 7 with parity tests and docs.

## Open Questions

- Telemetry schema versioning once events replace writer methods—do we bump major or treat as additive?
- Need for backfill/history APIs (queue fairness, rivalry snapshots) when streaming replaces getters.
- Policy observation DTO format for scripted vs. ML backends—single schema or configurable variants?

Keep this document up to date as design decisions land. Refer to `status.md` for current execution state and `implementation_plan.md` for detailed sequencing.
