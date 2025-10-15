# WP3B – Modular Systems Reattachment

Purpose: Replace the temporary legacy bridges left in place after the DTO refactor with fully modular
system steps so the world can operate through `WorldContext` without calling back into legacy
helpers.

## Objectives

1. Deliver queue/affordance/employment system steps that replicate the behaviour currently covered
   by `WorldState.apply_actions` and `WorldState.resolve_affordances`. **(Completed 2025-10-09)**
2. Remove the transitional bridge inside `WorldContext.tick` while keeping scripted parity
   (`tests/test_behavior_personality_bias.py`) and DTO parity smokes green. **(Completed 2025-10-09)**
3. Provide focused regression tests to lock in system sequencing and ensure nightly decay, job
   updates, and economy metrics still advance. **(Completed 2025-10-09)**

## Work Breakdown

### A. System Inventory & Gap Analysis
- Catalogue the methods exercised by `WorldState.apply_actions`, `resolve_affordances`, and
  `_apply_need_decay` during the demo parity run (queue reservations, running affordances, need
  decay, job state, relationship decay, basket metrics).
- Identify which behaviours already exist in the placeholder system modules (`queues`, `affordances`,
  `employment`, `economy`) and note missing helpers.
- Risk reduction: capture a short parity trace (actions, queue states, needs) with the legacy bridge
  active for later comparison.

### B. Implement Queue/Affordance Steps *(Completed)*
- `townlet.world.systems.queues.step` now synchronises reservations, handles ghost-step conflicts,
  and delegates handover/promotion logic via `handle_handover`; unit coverage added in
  `tests/world/test_systems_queues.py`.
- `advance_running_affordances` and `employment.step` call the queue helper, removing reliance on
  legacy `WorldState.resolve_affordances`. `townlet.world.systems.affordances.step` now delegates
  exclusively to the runtime service.
- Targeted tests for the runtime service/fallback paths live in
  `tests/world/test_systems_affordances.py`.

### C. Employment & Economy Integration *(Completed)*
- `employment.step` invokes `assign_jobs_to_agents()` + `apply_job_state()` each tick with guarded
  legacy fallback; `_apply_need_decay` only calls back into employment when the modular service is
  absent. Tests: `tests/world/test_systems_employment.py`.
- `economy.step` updates basket metrics (falling back to `_update_basket_metrics` when necessary) and
  leaves restocking logic inside the service; tests: `tests/world/test_systems_economy.py`.
- `relationships.step` now handles decay per tick, allowing `_apply_need_decay` to avoid calling the
  legacy helper when the modular service is configured; tests: `tests/world/test_systems_relationships.py`.

### D. Remove Transitional Bridge *(Completed)*
- `townlet.world.systems.affordances.step` no longer calls `state.resolve_affordances`; modular
  systems now own the entire action→runtime→handover pipeline.
- `WorldState._apply_need_decay` only invokes employment/economy fallbacks when the modular services
  are missing, preventing double-application of wages or basket metrics.
- Parity guard suites (`pytest tests/world -q`, DTO parity, behaviour smokes) run clean post-change.

## Detailed Execution Plan (Archive)

*The following sections capture the original action plan for historical context; all items have been
executed and validated.*

### B1. Queue Promotion & Affinity Logic
- Extract the promotion handover path from `WorldState.resolve_affordances` (promotion to next agent,
  rivalry/affinity adjustments) into `_process_queue_conflicts` or a dedicated helper under
  `townlet.world.systems.queues`.
- Ensure queue release/requeue mirrors legacy semantics for success/failure cases; update the queue
  manager so promotion honours affinity bias.
- Tests:
  - Extend `tests/world/test_systems_queues.py` with a promotion regression (queue length > 1,
    verify promoted agent, rivalry event payload).
  - Add guard case covering affinity preference toggles.
- Risks & mitigations: capture legacy trace before/after; add debug logging behind test flag if
  parity drifts.

### B2. Affordance Runtime Detachment
- Port the remaining `state.resolve_affordances` behaviour into
  `townlet.world.affordances.service.AffordanceService` so the system step no longer needs the
  legacy method:
  - Ensure action ingestion uses `process_actions`.
  - Move cooldown/need decay sequencing into service helpers (currently split between runtime +
    state method).
  - Confirm guardrail events fire via the dispatcher after completion.
- Drop the temporary call to `state.resolve_affordances` inside
  `townlet.world.systems.affordances.step`.
- Tests: add targeted unit test for `advance_running_affordances` to cover success/failure paths and
  guardrail event emission; keep DTO parity harness green.
- Risks: employment/economy hooks still rely on the legacy call — blocked until C1 lands; validate
  with integration smoke once new steps wired.

### C1. Employment System Migration
- Capture the current behaviour of `WorldState._apply_job_state()` (legacy) by running a short
  scripted scenario and noting wage deltas / on-shift flags; record in `WP3B_trace_notes.md` for
  parity checks.
- Implement `employment.step` so it:
  - Retrieves `state._employment_service`; if present, call `assign_jobs_to_agents()` when new
    agents appear and `apply_job_state()` every tick.
  - Falls back to `state._apply_job_state()` when the modular service is missing (keeps legacy tests
    alive).
  - Handles manual-exit queue flushes by delegating to `employment_service.runtime` helpers when the
    queue length changes (expose metrics to telemetry in C2).
- Remove the `_apply_job_state()` invocation from `WorldState._apply_need_decay()` to avoid
  double-applying wages once the modular step is active; retain a guarded fallback (call only when
  the system step is unavailable).
- Tests:
  - Add `tests/world/test_systems_employment.py` with stubs asserting that `step` invokes the service
    once per tick and honours the legacy fallback path.
  - Extend DTO parity smoke to verify wage accumulation matches the legacy run after the refactor.
- Risks & mitigations:
  - Wage double-counting while both paths run → remove the legacy call in the same patch and add a
    regression that tracks `wages_earned`.
  - Missing employment service on older fixtures → keep the legacy fallback + provide a warning log
    so we can spot misconfigured contexts.

### C2. Economy System Migration
- Snapshot legacy behaviour by recording basket costs and stove stock deltas over a 300-tick run;
  store the trace for parity when the modular step lands.
- Implement `economy.step` so it:
  - Pulls `state._economy_service`; if present, invoke `update_basket_metrics()` every tick (which
    internally handles restocking) and optionally logs a debug guard when the service is missing.
  - Falls back to `state._update_basket_metrics()` to keep legacy worlds functional.
- Keep the system ordering (after employment, before relationships/economy consumers) so basket
  metrics are ready before telemetry/perturbations inspect them.
- Tests:
  - Add `tests/world/test_systems_economy.py` verifying both the service path and legacy fallback,
    including restock triggering by stubbing `tick_supplier`.
  - Extend DTO parity/telemetry guard to ensure `basket_cost` continues matching the legacy trace.
- Risks: double restock if both paths run (mitigated by removing the legacy call alongside the new
  step); ensure mocks supply `tick` so restock cadence stays deterministic.

### C3. Perturbation / Need Decay Alignment
- Verify `_apply_need_decay` side-effects now occur via modular services; if not, lift them into the
  appropriate system (likely employment/economy) and confirm nightly reset handles residuals.
- Update docs to record sequencing order.
- Tests: extend `tests/world/test_world_context.py` nightly tick case to check need decay.

### D1. Remove Legacy Bridge
- Once C1–C3 pass parity, delete the fallback `state.resolve_affordances` call and any unused helper
  methods in `WorldState`.
- Update `WorldContext.tick` to rely solely on modular steps; remove related TODOs.
- Run full targeted suite: `pytest tests/world -q`, `pytest tests/core/test_sim_loop_dto_parity.py`,
  behaviour parity, and DTO harness.
- Document final state in WP3 README/status and notify WP1/WP2 owners that the blocker is lifted.

## Exit Criteria

- `WorldContext.tick` no longer calls legacy `WorldState.apply_actions`/`resolve_affordances`.
- Queue/affordance/employment system modules contain the required logic with unit coverage.
- Parity tests (`tests/test_behavior_personality_bias.py`, DTO harness, guardrail events) remain
  green.
- Docs/tasks reference the completed bridge removal and highlight any outstanding cleanups.
