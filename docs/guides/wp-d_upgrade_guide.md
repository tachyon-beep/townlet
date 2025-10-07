# WP-D Upgrade Guide – Telemetry Consumer Migration

This guide outlines the practical steps for migrating telemetry consumers from
concrete `TelemetryPublisher` imports to the protocol-based `TelemetrySinkProtocol`.

## 1. Replace Concrete Imports with Protocols

- Before:
  - `from townlet.telemetry.publisher import TelemetryPublisher`
- After:
  - `from townlet.core.interfaces import TelemetrySinkProtocol`
  - Acquire instances via the loop or factory: `loop.telemetry` or `resolve_telemetry(...)`.

Rationale: decouple consumers from publisher internals and support stub transports.

## 2. Use Factory/Loop Accessors

- Prefer `SimulationLoop(config).telemetry` or `resolve_telemetry(name, **options)` over direct class construction.
- Use `townlet.core.utils.telemetry_provider_name(loop)` for visibility and `is_stub_telemetry(sink)` for capability checks (e.g., to display a warning banner).

## 3. Read-Only Accessors and Defensive Calls

- Use protocol-safe getters for snapshots and metrics: `latest_*` methods are available on the protocol surface.
- For optional features, call through helpers that tolerate missing methods (see the console bridge pattern using `getattr` to supply defaults).

## 4. Console and Snapshot Paths

- Console routers should import the protocol and avoid direct publisher attributes.
- Snapshot save/load should pass `TelemetrySinkProtocol` to persistence helpers; optional telemetry fields are handled behind guards.

## 5. Stub Compatibility

- `StubTelemetrySink` implements the protocol with no-ops and logs a single activation warning.
- Consumers should not break when the stub is active; avoid hard casts to concrete classes and favor `getattr`/protocol guards for optional features.

## 6. Transport and Worker Metrics

- Observe worker status via `latest_transport_status()`; do not traverse the worker manager directly.
- Key fields: `queue_length`, `dropped_messages`, `last_flush_duration_ms`, `queue_length_peak`, `payloads_flushed_total`, `send_failures_total`, `worker_restart_count`.

## 7. Validation Checklist

- [ ] No remaining `TelemetryPublisher` imports in consumer codepaths
- [ ] Type hints reference `TelemetrySinkProtocol`
- [ ] Console/snapshot flows operate with both `stdout` and `stub` telemetry
- [ ] Scripts emit a clear message when stub is active
- [ ] Benchmarks recorded and compared for regressions (see Phase 7 runbook)

