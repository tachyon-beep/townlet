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
- [x] Replace legacy console buffer (`_console_results_batch`) with dispatcher
  events; delete `_queue_console_command` and friends in `world/grid.py`. *(2025-10-11)*
- [x] Rebuild affordance hook registration to emit DTO events or operate through
  modular services without direct `WorldState` mutation. *(2025-10-11)* Default
  hooks now use `AffordanceEnvironment` services (queue manager, relationship
  service, dispatcher) and stop mutating `WorldState` internals directly.
- [x] Update console handler tests and hook parity fixtures to validate the
  dispatcher-first flow. *(2025-10-11)* Console results now flow entirely through
  dispatcher events; `TelemetryPublisher` tracks the latest payloads without
  maintaining mirrored batches, and console/telemetry suites cover the new path.

## Batch C — Employment & Affordance State
- [x] Remove `_job_keys`, direct employment runtime caches, and job reward helpers
  from `WorldState`; rely on `EmploymentCoordinator` + DTO events.
   - Current touchpoints:
     - `WorldState._job_keys` seeded from `config.jobs` and forwarded into
       `LifecycleService(job_keys=...)`, `EmploymentRuntime.assign_jobs_to_agents`,
       and the legacy `EmploymentEngine` hot path (`world/employment.py`).
     - `EmploymentEngine.assign_jobs_to_agents` mutates agent inventory and
       references `_job_keys` for round-robin defaults; `EmploymentRuntime`
       still guards on `_job_keys` being non-empty.
     - Lifecycle respawns rely on `_assign_job_if_missing` (fed the tuple of job
       keys) to seed newly spawned agents before handing them to the employment
       service.
     - Legacy `_apply_job_state`/_`_employment_context_*` helpers on
       `WorldState` wrap `employment_system` functions for tests/back-compat.
     - Economy tie-in: wage accrual updates inventory (`wages_earned`) and
       wallet directly via employment hooks; ghost writes still originate from
       the employment service, so removing the world helper requires ensuring
       DTO exports read from service snapshots.
   - **Planned remediation:** keep the job roster inside the employment
     coordinator/service, update lifecycle respawns to call into the coordinator
     for default assignments, and delete the world-level convenience wrappers.
     - Economy linkage: `_update_basket_metrics` / `_restock_economy` remain as
       world fallbacks but already delegate into `EconomyService`; they can be
       retained as thin pass-throughs once the employment hooks stop invoking
       them during `_apply_need_decay`. (Reviewed 2025-10-11 – no further changes needed.)
- [x] Refactor manifest loading to delegate through modular registries instead of
  mutating `WorldState` dicts.
- [x] Add regression tests to ensure queue/employment metrics remain stable.

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
