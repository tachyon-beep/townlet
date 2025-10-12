# Legacy Cleanup Plan — World/Grid Stack (2025-10-11)

This plan translates the audit findings into bite-sized remediation batches.
Ordering favours low-risk changes first so the test suite stays green while we
chip away at the remaining legacy surfaces.

## Batch A — Observation & Adapter Tightening
1. **Observation context hardening**
   - Remove `_maybe_call` fallbacks in `observations/context.py`; require DTO
     services (adapter) for employment context metrics.
   - Drop `ensure_world_adapter` try/except; fail fast if no adapter is present.
   - Update unit tests (`tests/world/test_observation_dto_factory.py`,
     `tests/test_world_observation_helpers.py`) to inject adapters explicitly.
2. **Local view detangling**
   - Replace raw `adapter.objects`/`objects_by_position_view()` usage in
     `observe.py` with calls to modular services exposed via the adapter.
   - Ensure reservation checks rely on queue services rather than direct
     `_active_reservations` snapshots.
3. **DefaultWorldAdapter slimming**
   - Remove getters exposing raw world internals (`world_state`,
     `queue_manager`, etc.); instead expose DTO snapshots or service facades
     where needed.
   - Patch adapter tests and ports guard (`tests/adapters/test_default_world_adapter.py`,
     `tests/test_ports_surface.py`) to match the lean surface.

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
