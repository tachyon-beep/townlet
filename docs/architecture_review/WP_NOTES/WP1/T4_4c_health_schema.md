# WP1 – T4.4c Health Telemetry Audit & Redesign (2025-10-11)

This document captures the current behaviour of the `loop.health` event, the
surfaces that depend on it, and the proposed DTO-first schema for T4.4c. Use it
as the single source of truth while implementing the refactor.

## 1. Current Event Shape (SimulationLoop `health_payload`)

As of 2025-10-11 the loop emits the structured schema implemented in T4.4c:

```jsonc
{
  "tick": <int>,
  "status": "ok" | "warn" | "error",
  "duration_ms": <float>,
  "failure_count": <int>,
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
  "summary": {
    "duration_ms": <float>,
    "queue_length": <int>,
    "dropped_messages": <int>,
    "last_flush_duration_ms": <float|null>,
    "payloads_flushed_total": <int>,
    "bytes_flushed_total": <int>,
    "auth_enabled": <bool>,
    "worker_alive": <bool>,
    "worker_error": <str|null>,
    "worker_restart_count": <int>,
    "perturbations_pending": <int>,
    "perturbations_active": <int>,
    "employment_exit_queue": <int>
  }
}
```

Historical payloads may still contain the deprecated alias block
(`telemetry_queue`, `perturbations_pending`, …); the telemetry publisher now
converts those aliases into the `summary` structure on ingest.

## 2. Consumer Inventory

| Consumer / Location                                | Usage                                                                                                    |
|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| `TelemetryPublisher._handle_event` (`loop.health`) | Stores payload via `_ingest_health_metrics`; queues history via dispatcher (needs `queue_metrics`).       |
| `TelemetryEventDispatcher._append_queue_history`   | Reads `queue_metrics` (top-level) or `payload["global_context"]["queue_metrics"]` when present.          |
| `townlet_ui/telemetry.py` (`HealthStatus`)         | Expects scalar fields (`telemetry_queue`, `telemetry_dropped`, `perturbations_pending`, `employment_exit_queue`, etc.). |
| `scripts/telemetry_watch.py` + `tests/test_telemetry_watch.py` | Parse structured log lines derived from the same scalars.                                    |
| Logging (`logger.info("tick_health ...")`)         | Emits legacy key/value text consumed by `telemetry_watch` utilities.                                     |
| `tests/test_sim_loop_health.py`                    | Asserts cached health state mirrors scalar keys and snapshot path.                                      |
| `TelemetryEventDispatcher.queue_history`           | Persists queue metrics history for dashboards.                                                           |

No other subsystem uses the event today, but CLI/observer dashboards depend on
the scalar aliases for rendering and threshold checks.

## 3. Identified Gaps / Risks

1. **Legacy world touchpoints:** `employment_exit_queue` is fetched directly
   from `WorldState`, blocking removal of the legacy world reference.
2. **Duplicated transport data:** Scalars repeat information already available
   via `_last_transport_status`.
3. **Missing DTO context:** Queue/employment/perturbation metrics are already
   present in `global_context`, but the health event does not expose or reuse
   that structure.
4. **Inconsistent downstream expectations:** UI/CLI/tests hard-code the scalar
   field names; changing them without a compatibility layer would break tools.

## 4. Proposed DTO-First Schema

Emit a structured payload that mirrors the DTO tick event while retaining
compatibility aliases for one release cycle.

```jsonc
{
  "tick": <int>,
  "status": "ok" | "warn" | "error",
  "duration_ms": <float>,
  "failure_count": <int>,
  "transport": {
    "queue_length": <int>,
    "dropped_messages": <int>,
    "last_flush_duration_ms": <float|null>,
    "worker": {
      "alive": <bool>,
      "error": <str|null>,
      "restart_count": <int>
    },
    "auth_enabled": <bool>,
    "payloads_flushed_total": <int>,
    "bytes_flushed_total": <int>
  },
  "global_context": {
    "queue_metrics": {...},
    "employment_snapshot": {...},
    "perturbations": {...},
    "stability_metrics": {...},
    "...": "reuse from loop.tick global_context"
  },
  "aliases": {
    "telemetry_queue": <int>,
    "telemetry_dropped": <int>,
    "telemetry_flush_ms": <float|null>,
    "telemetry_worker_alive": <bool>,
    "telemetry_worker_error": <str|null>,
    "telemetry_worker_restart_count": <int>,
    "telemetry_console_auth_enabled": <bool>,
    "telemetry_payloads_total": <int>,
    "telemetry_bytes_total": <int>,
    "perturbations_pending": <int>,
    "perturbations_active": <int>,
    "employment_exit_queue": <int>
  }
}
```

Implementation notes:

- `transport` is populated directly from `_last_transport_status`.
- `global_context` is copied from the DTO tick builder to guarantee parity.
- Alias block mirrors existing field names to keep dashboards/CLI/tests stable
  during migration; aliases can be removed once downstream consumers migrate.
- `duration_ms` supersedes `tick_duration_ms`; retain `tick_duration_ms` inside
  `aliases` for compatibility.

## 5. Data Derivation Mapping

| Target Field                                        | Source                                                                        |
|-----------------------------------------------------|-------------------------------------------------------------------------------|
| `duration_ms`                                       | Loop timing (`duration_ms` calculation).                                      |
| `transport.*`                                       | `_build_transport_status` snapshot (already DTO-friendly).                    |
| `global_context.queue_metrics`                      | Existing `_build_tick_global_context` result for current tick.                |
| `global_context.employment_snapshot.exit_queue`     | `employment_snapshot["exit_queue_length"]` exported by `WorldContext`.        |
| `global_context.perturbations`                      | `self.perturbations.export_state()` (already feeding tick event).             |
| Alias `employment_exit_queue`                       | Derived from `global_context.employment_snapshot`.                            |
| Alias `perturbations_*`                              | Derived from `global_context.perturbations`.                                  |
| Alias transport fields                               | Derived from `transport` block.                                               |

This removes direct `self.world.employment` access and keeps all inputs within
the modular DTO exports.

## 6. Downstream Adjustments

1. **TelemetryPublisher / EventDispatcher**  
   - Consume `payload["transport"]` / `payload["global_context"]` first.  
   - Maintain alias fallbacks for existing API methods (e.g., `latest_health_status()`).

2. **UI (`townlet_ui/telemetry.py`) & Dashboard scripts**  
   - Prefer the structured fields; fall back to aliases for backward
     compatibility.

3. **CLI (`scripts/telemetry_watch.py`)**  
   - Update `_parse_health_line` to handle the new JSON structure (or adjust log
     format) while still recognising legacy log lines.

4. **Tests**  
   - Refresh `tests/test_sim_loop_health.py`, `tests/test_telemetry_watch.py`,
     `tests/test_telemetry_surface_guard.py`, dispatcher tests, and DTO smoke
     suites to assert the new structure.

## 7. Compatibility & Migration Plan

1. Emit both structured fields and alias block for one release cycle; mark alias
   fields with TODO to remove after downstream migration.
2. Update documentation (ADR-001 appendix, WP1 README/status) to describe the new
   schema and deprecation timeline.
3. Once UI/CLI/tests drop alias usage, remove the alias block and tighten guard
   tests to forbid legacy keys.

## 8. Implementation Checklist (for subsequent plan)

1. Refactor `SimulationLoop.step` health payload builder to emit the new schema
   (including `global_context`).  
2. Update telemetry dispatcher/publisher to prefer structured fields and keep
   alias warnings.  
3. Refresh UI/CLI helpers and associated tests.  
4. Adjust logging format (`tick_health …`) to reflect new schema while
   maintaining legacy parser compatibility.  
5. Document schema changes and rerun targeted regression suites.

Once the above changes are complete and validated, proceed to T4.4d to align the
failure payload with the same structure.

---

## 9. Detailed Execution Plan (T4.4c)

### Step 1 – Simulation Loop rewrite
1. Introduce `_build_health_payload()` helper in `SimulationLoop` that:
   - Copies the current tick’s `global_context` (reuse `_build_tick_global_context` output).
   - Builds the structured `transport` block from `_build_transport_status`.
   - Derives alias metrics (`telemetry_queue`, `perturbations_pending`, etc.) from the structured sections.
2. Replace the inline `health_payload` construction in `SimulationLoop.step`
   with the helper; remove direct `self.world.employment`/`perturbations` calls.
3. Ensure `global_context` is included in the health payload and cached for the
   dispatcher.
4. Update logging so the `tick_health` line references the new aliases while
   remaining parseable by existing CLI tools.

### Step 2 – Telemetry pipelines
1. `TelemetryPublisher._handle_event` (`loop.health`):
   - Consume the structured payload; store both the structured sections and the
     alias block (`latest_health_status` should expose aliases transparently).
   - Update `_ingest_health_metrics` to store transport/context snapshots for UI access.
2. `TelemetryEventDispatcher._append_queue_history`:
   - Prefer `payload["global_context"]["queue_metrics"]`; fall back to aliases
     with a warning.
3. `HealthMonitor` (if required) should consume the structured payload; confirm
   it still emits metrics based on queue/event counts (may be unchanged).

### Step 3 – UI / CLI / Tests
1. `townlet_ui/telemetry.py`:
   - Parse the new `transport` and `global_context` fields; retain alias fallback.
2. `scripts/telemetry_watch.py` & `tests/test_telemetry_watch.py`:
   - Support the structured payload (either by consuming JSON events or by
     parsing the alias block); ensure legacy log parsing still works.
3. Update unit/integration tests:
   - `tests/test_sim_loop_health.py` (structured payload assertions).
   - `tests/test_telemetry_surface_guard.py` (ensure DTO-only health payload).
   - `tests/telemetry/test_event_dispatcher.py` (queue history from context).
   - Any dashboard/console tests relying on queue metrics.

### Step 4 – Documentation & Regression
1. Update ADR-001 appendix and WP1 status/README to describe the new schema and
   deprecation timeline for aliases.
2. Record the updated regression command in the WP1 status file.
3. Run targeted suite:
   ```
   pytest tests/test_sim_loop_health.py \
          tests/telemetry/test_event_dispatcher.py \
          tests/test_telemetry_surface_guard.py \
          tests/test_console_commands.py \
          tests/test_conflict_telemetry.py \
          tests/test_observer_ui_dashboard.py \
          tests/test_telemetry_watch.py -q
   ```
4. Capture parity notes (queue history, employment metrics) in WP1/WP3 briefs.

### Step 5 – Cleanup & TODOs
1. Leave TODO comment noting alias removal timing (post dashboard/CLI migration).
2. Open follow-up task for T4.4d (failure payload) referencing the structured
   transport/helper once T4.4c lands.

## 10. Execution Notes (2025-10-11)
- Steps 1–4 above are complete: `SimulationLoop` emits the structured payload,
  telemetry publisher/dispatcher/UI/CLI consume it, and the regression bundle
  listed in Step 4 passes.
- Alias fields (`telemetry_*`, `tick_duration_ms`, `perturbations_*`,
  `employment_exit_queue`) remain for compatibility; remove after dashboards and
  CLI migrate to the structured schema.
