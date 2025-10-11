# WP1 – T4.4d Loop Failure Telemetry Redesign (2025-10-11)

This note captures the current state of `loop.failure` payloads, the dependent
surfaces, and the plan for migrating them to the DTO-first schema introduced by
T4.4c. Follow this as the implementation checklist for T4.4d.

## 1. Current Payload (post-refactor)

`SimulationLoop._build_failure_payload` now mirrors the DTO-first health schema:

```jsonc
{
  "tick": <int>,
  "status": "error",
  "duration_ms": <float>,
  "failure_count": <int>,
  "error": "<ExceptionName>: <message>",
  "snapshot_path": "<path>|null",
  "transport": {
    "provider": <str|null>,
    "queue_length": <int>,
    "dropped_messages": <int>,
    "last_flush_duration_ms": <float|null>,
    "payloads_flushed_total": <int>,
    "bytes_flushed_total": <int>,
    "auth_enabled": <bool>,
    "worker": {
      "alive": <bool>,
      "error": <str|null>,
      "restart_count": <int>
    }
  },
  "global_context": { ... },
  "health": { ... },             // optional copy of last loop.health payload
  "summary": {
    "duration_ms": <float>,
    "queue_length": <int>,
    "dropped_messages": <int>
  }
}
```

Legacy payloads containing `tick_duration_ms` / `telemetry_queue` /
`telemetry_dropped` are still accepted; the publisher synthesises the `summary`
block from those aliases when necessary.

## 2. Consumer Inventory

| Surface / File                                         | Usage                                                                                          |
|--------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `TelemetryPublisher._ingest_loop_failure`              | Passes payload to aggregator and stores `_latest_health_status` via `_store_loop_failure`.     |
| `TelemetryAggregator.record_loop_failure`              | Wraps payload into a `TelemetryEvent(kind="health")`; expects scalar keys.                     |
| `TelemetryEventDispatcher` (`loop.failure`)            | Caches payload via `_latest_failure = dict(payload)`.                                          |
| CLI runner (`scripts/run_simulation.py`)               | Prints payload (newline separated) when the simulation aborts.                                 |
| Tests (`tests/test_sim_loop_health.py`, etc.)          | Assert `latest_health_status()` contains snapshot path/error fields.                           |
| Telemetry worker/internal metrics tests                | Feed dummy payloads into publisher to exercise buffering/metrics (`tests/test_telemetry_worker_health.py`, `tests/test_telemetry_internal_metrics.py`). |
| UI/dashboard (indirect)                                | Currently inspect `TelemetryPublisher.latest_health_status()` rather than failure payload.     |

## 3. Desired DTO-First Schema

Match the event schema in `WP3/event_schema.md` while retaining aliases during
the transition:

```jsonc
{
  "tick": <int>,
  "status": "error",
  "duration_ms": <float>,
  "failure_count": <int>,
  "error": "<ExceptionName>: <message>",
  "snapshot_path": "<path>|null",
  "transport": {
    "provider": "port",
    "queue_length": <int>,
    "dropped_messages": <int>,
    "last_flush_duration_ms": <float|null>,
    "payloads_flushed_total": <int>,
    "bytes_flushed_total": <int>,
    "auth_enabled": <bool>,
    "worker": {
      "alive": <bool>,
      "error": "<str|null>",
      "restart_count": <int>
    }
  },
  "global_context": { ... },          // reuse last known DTO context when available
  "health": { ... }                   // optional structured copy of last loop.health payload
}
```

Notes:
- When a failure occurs before a new DTO context is built, fall back to the last
  available observation envelope/global context (if present).
- The `health` section can reuse the most recent structured health payload (from
  `_build_health_payload`) if one exists.
- Legacy alias keys have been removed; downstream consumers should rely on the
  structured transport/summary data.

## 4. Implementation Plan

### Step 1 – Simulation Loop helper
1. Introduce `_build_failure_payload()` in `SimulationLoop` that:
   - Accepts `tick`, `duration_ms`, `error_message`, `snapshot_path`, and the
     transport snapshot.
   - Reuses `_build_transport_status` output and cached `self._last_health_payload`
     (set by `_build_health_payload`) to populate `transport` / `health`.
   - Pulls the last known DTO global context from
     `self._policy_observation_envelope.global_context` or cached tick context,
     falling back to `{}` when unavailable.
   - Computes alias fields (`telemetry_queue`, `telemetry_dropped`, `tick_duration_ms`)
     for backwards compatibility.
2. Replace the inline payload in `_handle_step_failure` with the helper.
3. Update the failure log message to continue reporting alias fields (so existing
   CLI parsers work) while including a pointer to the structured transport context.

### Step 2 – Telemetry pipeline updates
1. `TelemetryPublisher._store_loop_failure`:
   - Store the structured payload (`transport`, `global_context`, `health`, `aliases`).
   - Maintain compatibility for consumers expecting `telemetry_queue` / `telemetry_dropped`.
   - Ensure the failure log uses the alias fields to avoid breaking existing log parsers.
2. `TelemetryAggregator.record_loop_failure`:
   - No change to event type; ensure tests cover the structured payload (payload is
     passed through unchanged).
3. `TelemetryEventDispatcher`:
   - Continue caching the entire payload; add guards if consumers rely on aliases.

### Step 3 – UI / CLI / Tests
1. Update `scripts/run_simulation.py` to pretty-print the new structured payload
   while retaining legacy output (use alias values for the summary line).
2. Refresh tests:
   - `tests/test_sim_loop_health.py`: assert failure payload contains `transport`,
     `aliases`, and preserves snapshot/error information.
   - `tests/test_run_simulation_cli.py`: adjust mocks for the new structure.
   - `tests/test_telemetry_worker_health.py`,
     `tests/test_telemetry_internal_metrics.py`: provide structured payloads in assertions.
   - Add/extend tests ensuring the alias fields match the structured data (similar to
     the health test additions).

### Step 4 – Documentation & Regression
1. Update T4.4 task tracker (`ground_truth_executable_tasks.md`), pre-brief, and
   status docs to mark T4.4d complete once implemented.
2. Refresh ADR-001 / telemetry documentation to describe the new failure schema.
3. Run regression subset (health/failure/CLI/telemetry tests):
   ```
   pytest tests/test_sim_loop_health.py \
          tests/test_run_simulation_cli.py \
          tests/telemetry/test_event_dispatcher.py \
          tests/test_telemetry_worker_health.py \
          tests/test_telemetry_internal_metrics.py \
          tests/test_console_commands.py \
          tests/test_conflict_telemetry.py -q
   ```
4. Perform a T4.4 stocktake: confirm tick/health/failure/console flows are DTO-first
   and document any remaining alias deprecation tasks.

### Step 5 – Follow-up / TODOs
1. Leave TODO comments noting the planned removal of the alias block once dashboards
   and CLI migrate.
2. Schedule documentation updates (ADR-001 appendix, operator guide) to reflect the
   structured failure payload.
3. Ensure WP1/WP3 briefs capture the alias removal plan so the work is tracked after
   T4.4d.

---

## Execution Notes (2025-10-11)
- `_build_failure_payload` now mirrors the health schema (structured transport,
  cached global context, optional health snapshot, alias block). `SimulationLoop`
  calls the helper during failure handling, ensuring transport/context data remain
  DTO-first even when failures occur mid-tick.
- Telemetry publisher merges alias values into `_latest_health_status` for
  compatibility and logs queue/dropped counts alongside the error. Worker/CLI
  tests now provide structured payloads.
- Targeted regression bundle (`pytest tests/test_sim_loop_health.py tests/test_run_simulation_cli.py tests/telemetry/test_event_dispatcher.py tests/test_telemetry_worker_health.py tests/test_telemetry_internal_metrics.py tests/test_console_commands.py tests/test_conflict_telemetry.py -q`)
  passes. Alias removal is deferred until dashboards/CLI migrate.
