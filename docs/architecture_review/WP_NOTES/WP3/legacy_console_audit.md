# Legacy Console Audit — Batch B (2025-10-11)

This note captures the remaining console-specific legacy surfaces prior to
Batch B remediation. The aim is to remove world-level buffering so console
traffic flows exclusively through dispatcher events and the orchestration
router.

## Runtime/Data Flow Overview

```
SimulationLoop.tick()
    └─ runtime.tick(...)
         └─ WorldState.apply_console(...)
              └─ ConsoleService.apply → ConsoleBridge.apply → returns [ConsoleCommandResult]
         (results embedded in RuntimeStepResult.console_results)

SimulationLoop
    ├─ routes console_results to ConsoleRouter (if available)
    └─ falls back to TelemetryPublisher._store_console_results (stub path)

TelemetryPublisher
    ├─ derives `latest_console_results()` from dispatcher emissions (no legacy
        `_console_results_batch/_history` caches)
    ├─ appends console results to the audit log for parity
    └─ emits `console.result` events via dispatcher subscribers
```

### Key Mutating APIs
- `WorldState.apply_console(operations)` forwards to `ConsoleService.apply` and
  returns the generated `ConsoleCommandResult` entries.
- `_record_console_result` exists for direct hook usage but is largely unused.
- `ConsoleService` wraps `ConsoleBridge`, which still manages history/buffer
  limits and cached lookups (`cached_result`, `consume_results` etc.).

### Orchestration Touch Points
- `WorldContext.tick` now captures `console_results = list(state.apply_console(console_operations))`
  before executing systems. The results are embedded in the `RuntimeStepResult`
  returned to the simulation loop.
- `SimulationLoop._run_console_router` (path inside `tick`) pushes console
  results through the dispatcher router; if the router is absent the loop sends
  results to the telemetry publisher so legacy transports can persist them.
- `TelemetryPublisher` still caches batches/history for CLI/dashboard parity.

## Outstanding Legacy Behaviour
1. **WorldState Buffering**
   - `apply_console` still delegates to `ConsoleService`, but results are now
     returned directly to the caller (no more `consume_console_results`). The
     `_console` service remains embedded in `WorldState`, so the next step is to
     lift it out of the state object entirely.
   - Console manifest metadata lives inside the world snapshot export via the
     telemetry publisher, not the dispatcher.

2. **ConsoleService / ConsoleBridge**
   - Bridge maintains a history deque and buffer limit; the loop bypasses it
     when routing directly through the dispatcher.
   - Handler registration still operates on the bridge.

3. **Telemetry Snapshot Glue**
   - Publisher still retains a bounded history deque for CLI snapshots; confirm
     downstream tools consume dispatcher events before trimming further.

4. **Tests/Docs**
   - Numerous tests (`tests/test_console_commands.py`,
     `tests/test_console_router.py`, `tests/test_telemetry_stub_compat.py`)
     still assert on legacy buffer semantics (presence of history, tick rollover).

## Next Steps (Batch B Execution)
1. **Buffer Removal Plan**
   - Move the console service out of `WorldState` (runtime/router own it) so the
     state object stops storing mutable console buffers.
   - Ensure `WorldContext.tick`/`WorldRuntime.tick` eventually stop returning
     `console_results` lists once downstream callers rely purely on dispatcher
     events.
2. **ConsoleRouter Integration**
   - Guarantee all console command pathways enqueue operations via the router,
     so runtime tick receives operations that already carry context metadata.
   - Update stub telemetry to consume dispatcher console events rather than the
     cached batch.
3. **Telemetry Simplification**
   - Verify CLI/dashboard consumers rely on dispatcher events and adjust the
     remaining history buffers accordingly.
   - Refresh tests/docs to match the event-only flow.

This audit documents the legacy surfaces so Batch B can safely remove them.
