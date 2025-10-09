# Telemetry Pipeline Guide

This guide describes the refactored telemetry pipeline (WP‑D), including layering, protocols, configuration, and operational tips.

## Architecture Overview

- Aggregation: builds structured payloads from world/runtime artefacts.
- Transform: applies normalization, redaction, and schema validation.
 - Transport: buffers and flushes events (stdout, file, tcp; websocket stubbed; prometheus textfile available).
- Worker: background flush manager with backpressure and retries.

Interfaces are defined in `src/townlet/core/interfaces.py` (TelemetrySinkProtocol). The default sink is `TelemetryPublisher` (`src/townlet/telemetry/publisher.py`). A stub sink (`src/townlet/telemetry/fallback.py`) provides no‑op behavior when transports are unavailable.

## Configuring Telemetry

Example excerpt:

```yaml
telemetry:
  transport:
    type: stdout   # stdout | file | tcp | http | websocket (stub) | prometheus (textfile)
    file_path: logs/telemetry.jsonl  # for file transport
    endpoint: localhost:9090         # for tcp transport
    enable_tls: true                 # tcp only
    send_timeout_seconds: 1.0
    worker_poll_seconds: 0.5
    buffer:
      max_batch_size: 32
      max_buffer_bytes: 256000
      flush_interval_ticks: 1
    worker:
      backpressure: drop_oldest  # drop_oldest | block | fan_out
      block_timeout_seconds: 0.5
      restart_limit: 3
  # Example: to POST events to an external collector, set type=http and provide endpoint=http(s) URL.
  transforms:
    pipeline:
      - snapshot_normalizer
      - redact_fields: {fields: [policy_identity], kinds: [snapshot, diff]}
      - ensure_fields: {required_fields_by_kind: {snapshot: [schema_version, tick]}}
      # - schema_validator: {schemas: {snapshot: path/to/schema.json}}
```

## Protocol Surface (common read‑only accessors)

- `emit_event("loop.tick", payload)` – main emission entrypoint (tick lifecycle).
- `emit_event("loop.health", payload)` / `emit_event("loop.failure", payload)` – health & failure reporting.
- `emit_event("console.result", payload)` – console ingress/egress (results include metadata + payload).
- Read‑only getters used by dashboards and scripts:
  - state snapshots (`latest_*`): economy, utilities, relationships, employment, conflicts, social events, narrations, policy snapshot/identity, affordances, reward breakdown, stability, health.
  - transport: `latest_transport_status()` (queue length, dropped, flushms, peaks, restarts, failures, totals, flags).

The console router uses protocol‑safe accessors and defensive `getattr` guards so both real and stub sinks are supported.

## Observability & Metrics

Worker/population metrics are exposed via `latest_transport_status()`:

- `queue_length`, `queue_length_peak`
- `dropped_messages`
- `last_flush_duration_ms`, `last_batch_count`, `last_flush_payload_bytes`
- `payloads_flushed_total`, `bytes_flushed_total`
- `consecutive_send_failures`, `send_failures_total`
- `worker_restart_count`, `worker_alive`, `worker_error`

Loop health logs include these counters per tick (`tick_health ...`).

## Benchmarking

Use the provided scripts to record and compare benchmarks (see docs/architecture_review/wp-d_phase7_runbook.md). Captured metrics include `avg_tick_seconds` and key transport counters; sweep mode helps tune batch/flush/poll settings.

## Stub Behavior

`StubTelemetrySink` implements the protocol with safe defaults; no streaming occurs. Scripts and consoles surface a warning banner when stub mode is active.

## Prometheus Textfile Transport

Set `telemetry.transport.type: prometheus` and provide `telemetry.transport.file_path` to write counters suitable for node_exporter's textfile collector:

```
telemetry:
  transport:
    type: prometheus
    file_path: /var/lib/node_exporter/textfile_collector/townlet_telemetry.prom
```

The transport writes `townlet_telemetry_messages_total` and `townlet_telemetry_bytes_total` atomically on each batch.
