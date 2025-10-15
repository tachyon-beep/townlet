# Web Telemetry Schema

This document captures the payload contract exposed to the upcoming web observer. The transport mirrors the existing Rich console snapshots while adding a stable wrapper that supports streamed diffs.

## Top-Level Envelope

Every message sent over the telemetry gateway is a JSON object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | `string` | Semantic version of the telemetry schema (e.g. `"0.9.7"`). Matches the underlying simulation shard. |
| `tick` | `integer` | Simulation tick associated with the snapshot/diff. Optional for bootstrap messages. |
| `payload_type` | `"snapshot" \| "diff"` | `snapshot` for the first full payload, `diff` for incremental updates. Missing value defaults to `snapshot`. |
| `changes` | `object` | (`diff` only) Partial updates applied on top of the last snapshot. Absent for full snapshots. |
| `removed` | `array[string]` | (`diff` only) Top-level keys removed since the previous payload. |
| `transport` | `object` | Connection health (see below). Required for `snapshot`, optional in diffs unless a field changes. |
| `health` | `object \| null` | Simulation runtime health metrics (queue backlog, tick duration…). |
| `employment`, `conflict`, `relationships`, … | `object` | Same sections produced by `townlet_ui.telemetry.TelemetrySnapshot`. All snapshot sections remain available to the web client. |

### Transport Health

```
transport = {
  "connected": true,
  "dropped_messages": 0,
  "last_error": null,
  "last_success_tick": 120,
  "last_failure_tick": null,
  "queue_length": 0,
  "last_flush_duration_ms": 0.78
}
```

### Health Metrics

```
health = {
  "tick": 120,
  "status": "ok",
  "duration_ms": 4.1,
  "failure_count": 0,
  "transport": {
    "queue_length": 0,
    "dropped_messages": 0,
    "last_flush_duration_ms": 0.78,
    "payloads_flushed_total": 42,
    "bytes_flushed_total": 8192,
    "auth_enabled": false,
    "worker": {"alive": true, "error": null, "restart_count": 0}
  },
  "global_context": {
    "queue_metrics": {...},
    "employment_snapshot": {...},
    "perturbations": {...}
  },
  "summary": {
    "queue_length": 0,
    "dropped_messages": 0,
    "last_flush_duration_ms": 0.78,
    "payloads_flushed_total": 42,
    "bytes_flushed_total": 8192,
    "auth_enabled": false,
    "worker_alive": true,
    "worker_error": null,
    "worker_restart_count": 0,
    "perturbations_pending": 0,
    "perturbations_active": 0,
    "employment_exit_queue": 0
  },
  "raw": {...}
}
```

## Diff Semantics

1. The first message for a subscriber **must** be a full `snapshot`.
2. Subsequent `diff` messages include only mutated top-level keys inside `changes`.
3. Web clients maintain local state by deep-merging `changes` into the previous snapshot and removing any keys listed in `removed`.
4. Consumers should treat unknown fields as forward-compatible extensions.

See `tests/data/web_telemetry/snapshot.json` and `tests/data/web_telemetry/diff.json` for canonical payload examples.

## Validation Tests

`tests/test_web_telemetry_schema.py` parses the snapshot and diff fixtures with the existing `TelemetryClient` to ensure:

- all required fields are present,
- diff application restores an equivalent snapshot,
- the schema wrapper behaves as expected.

Consumers integrating the web observer should depend on this schema and fixtures to keep parity with the Rich dashboard.

## Gateway Reference

The FastAPI gateway lives in `src/townlet/web/gateway.py` and exposes:

- `GET /metrics` – Prometheus metrics covering connection counts and message totals.
- `GET /health` – Simple readiness probe for orchestration.
- `WS /ws/telemetry` – Streams an initial `snapshot` followed by `diff` payloads. The gateway drops out-of-order ticks and keeps payloads JSON-compatible for the web client.
- `WS /ws/operator` – Authenticated operator channel (requires `token` query param). Accepts `{"type":"command", "payload":{...}}` messages and emits `status` snapshots (command history + queue info) plus `command_ack` responses.

Unit tests in `tests/test_web_gateway.py` cover snapshot/diff delivery, stale tick handling, and metrics exposure.
