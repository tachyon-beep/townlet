# Legacy Cleanup Plan — World/Grid Stack (2025-10-11)

This plan translates the audit findings into bite-sized remediation batches.
Ordering favours low-risk changes first so the test suite stays green while we
chip away at the remaining legacy surfaces.

## Batch A — Observation & Adapter Tightening
1. **Observation context hardening** ✅ (2025-10-11)
   - `_maybe_call` fallbacks deleted; DTO adapters required for employment
     metrics. Tests updated to inject adapters explicitly and reward-engine
     fixture now relies on DTO monkeypatching.
2. **Local view detangling** ✅ (2025-10-11)
   - `observe.py` now consumes `adapter.objects_snapshot()` and cached reservation
     sets; snapshots/state export path updated accordingly. Local cache helpers
     and DTO builders rely solely on adapter services.
3. **DefaultWorldAdapter slimming** ✅ (2025-10-11)
   - `agents()` returns an immutable tuple sourced from `WorldContext.agents_view`
     and adapters no longer expose mutable world registries via `objects`.
     Follow-up: continue trimming transitional helpers once hook/console
     refactors land.

## Batch B — Console & Hook Modernisation
1. Replace legacy console buffer (`_console_results_batch`) with dispatcher
   events; delete `_queue_console_command` and friends in `world/grid.py`.
2. Rebuild affordance hook registration to emit DTO events or operate through
   modular services without direct `WorldState` mutation.
3. Update console handler tests and hook parity fixtures to validate the
   dispatcher-first flow.

## Batch C — Employment & Affordance State
1. Remove `_job_keys`, direct employment runtime caches, and job reward helpers
   from `WorldState`; rely on `EmploymentCoordinator` + DTO events.
2. Refactor manifest loading to delegate through modular registries instead of
   mutating `WorldState` dicts.
3. Add regression tests to ensure queue/employment metrics remain stable.

## Batch D — Telemetry & Event Hardening
1. Delete alias ingestion fallbacks in `TelemetryPublisher` and related
   transports once the above batches land.
2. Strengthen guard tests (`tests/test_telemetry_surface_guard.py`,
   `tests/telemetry/test_event_dispatcher.py`) to fail if legacy keys reappear.

## Execution Notes
- Each batch should land with focused commits plus regression commands recorded
  in `stage5_cleanup_audit.md`.
- Batches can be scheduled independently; Batch A is unblocked now and should
  unblock additional adapter/test cleanups downstream.
