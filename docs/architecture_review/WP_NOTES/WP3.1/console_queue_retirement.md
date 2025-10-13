# Console Queue Retirement Plan

**Status**: ✅ COMPLETE (2025-10-13)
**Execution Log**: See `stage6_recovery_log.md` for detailed execution notes

## Background
Console routing is intended to flow through `TelemetryEventDispatcher` events (`console.result`, `console.command`). Stage 6 notes claim the legacy `queue_console_command` path was removed, but the repository still depends on it via the telemetry contract and tests.

## Current State Audit
- `TelemetrySinkProtocol` still defines `queue_console_command` / `export_console_buffer` (`src/townlet/core/interfaces.py:96-102`).
- `TelemetryPublisher` authenticates and buffers console commands internally (`src/townlet/telemetry/publisher.py:333-367`).
- `StubTelemetrySink` maintains its own `_console_buffer` (`src/townlet/telemetry/fallback.py:35-49`).
- Test fixtures enqueue commands by calling `loop.telemetry.queue_console_command(...)` (`tests/test_console_dispatcher.py:47-118`, `tests/orchestration/test_console_health_smokes.py:57-92`).
- Docs and scripts reference the shim (`docs/ops/CONSOLE_ACCESS.md`, `scripts/console_dry_run.py`).

## Implementation Plan

### 1. Protocol & Stub Teardown
1.1 Remove `queue_console_command`/`export_console_buffer` definitions from
    `TelemetrySinkProtocol` (`src/townlet/core/interfaces.py`).
    - Change signature block, keep `drain_console_buffer` for snapshot restore.
    - Acceptance: `rg "queue_console_command" src/townlet/core/interfaces.py`
      returns 0.
1.2 Update `StubTelemetrySink` to drop the buffer and expose
    `_latest_console_events: list[Mapping[str, object]]` plus a
    `latest_console_results` getter.
    - Replace `_console_buffer` usage with event cache.
    - Ensure `drain_console_buffer` pulls from the cache so snapshots still
      clear pending commands.
1.3 Adjust fixtures that consume `TelemetrySinkProtocol` to stop referencing
    queue helpers (`tests/conftest.py`, adapter smoke fixtures).

### 2. TelemetryPublisher Rewrite
2.1 Extract an `_authorise_console_command` helper containing the logic from
    lines 333-357.
    - Return `(ConsoleCommandEnvelope, principal)` on success; raise on auth
      failure.
2.2 Replace `_console_buffer` with `_latest_console_events` seeded as `deque`
    limited to e.g. 50 entries (matches existing history length).
2.3 Rename `queue_console_command` to `submit_console_command` and:
    - Call `_authorise_console_command`.
    - Emit `console.command` immediately via dispatcher.
    - Append sanitised envelope to `_latest_console_events`.
    - Emit `console.result` when dispatcher produces output (ensure we surface
      event in `_latest_console_results`).
2.4 Update `drain_console_buffer` to operate on `_latest_console_events`.
2.5 Update `export_state` and any snapshot importers to use the new cache.

### 3. Telemetry Adapter Wiring
3.1 Add `submit_console_command` method to `StdoutTelemetryAdapter` that proxies
    to publisher.
3.2 Remove properties exposing the publisher for queue access.
3.3 Update dependency injection sites (telemetry factory, demo wiring) to use
    the new method.

### 4. Simulation Loop Integration
4.1 Replace every `loop.telemetry.queue_console_command` call with
    `loop.telemetry.submit_console_command` or equivalent router helper in:
    - `tests/test_console_dispatcher.py` `_queue_command` helper.
    - `tests/orchestration/test_console_health_smokes.py`.
    - `tests/test_console_auth.py`, `tests/test_sim_loop_snapshot.py`,
      `tests/core/test_sim_loop_modular_smoke.py`, and other references reported
      by `rg "queue_console_command"`.
4.2 Ensure `ConsoleRouter` exposes a helper used by tests/scripts so telemetry
    layering is respected.
4.3 Update `scripts/console_dry_run.py` (and any ops scripts) to call the
    router helper instead of accessing telemetry directly.

### 5. Result History Exposure
5.1 Ensure `TelemetryPublisher.latest_console_results()` returns dispatcher
    event history rather than queue state.
5.2 Mirror the API in `StubTelemetrySink` so smoke tests can assert on
    `latest_console_results` for both stub and stdout providers.
5.3 Add regression coverage checking that repeated commands with identical
    `cmd_id` reuse cached results (existing tests should be updated to reflect
    event-based caching).

### 6. Snapshot & Resume Handling
6.1 Remove queue payloads from `SnapshotState` import/export.
6.2 Update `tests/test_sim_loop_snapshot.py` to assert that snapshot restore
    carries over the dispatcher event history.

### 7. Documentation & Migration Notes
7.1 Update `docs/ops/CONSOLE_ACCESS.md`,
    `docs/engineering/CONSOLE_COMMAND_CONTRACT.md`, and any README snippets to
    describe `submit_console_command` and dispatcher routing.
7.2 Draft a short migration note for release comms listing the removed API and
    replacement path.

### 8. Validation Sequence
- `rg "queue_console_command" src tests docs scripts`
- `pytest tests/test_console_router.py tests/test_console_events.py \
         tests/test_console_commands.py tests/orchestration/test_console_health_smokes.py -q`
- `pytest tests/telemetry/test_aggregation.py tests/test_console_auth.py -q`
- Manual run: `python scripts/run_simulation.py --config configs/examples/base.yml`
  then trigger a console command through the router; confirm result emitted.

## Validation Checklist
- [ ] `grep -r "queue_console_command"` returns no hits under `src/` or `tests/`.
- [ ] Console routing suites pass: `pytest tests/test_console_router.py tests/test_console_events.py tests/test_console_commands.py tests/orchestration/test_console_health_smokes.py -q`.
- [ ] Telemetry integration suites pass: `pytest tests/telemetry/ -q`.
- [ ] Manual smoke via `python scripts/run_simulation.py --config configs/examples/base.yml` exercises console commands without failures (document in recovery log).

## Risks & Mitigations
- **Persisted snapshot compatibility:** legacy snapshots may contain queued commands. Mitigate by adding migration logic or documenting a breaking change.
- **External integrations:** dashboards or ops scripts may call the queue method. Prepare a compatibility shim or release notes before removal.
- **Auth bypass regressions:** event routing must still enforce auth; ensure tests cover unauthorized and malformed payloads.

## Dependencies
- Must complete before adapter cleanup (workstream 2) to avoid refactoring properties that still rely on the queue shim.
