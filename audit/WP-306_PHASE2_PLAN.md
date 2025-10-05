# WP-306 – Phase 2 Employment & Affordance Separation

## Objectives
- Decouple `WorldState` from employment queue/shift orchestration and the affordance runtime plumbing.
- Deliver focused coordinator modules with clear APIs for employment lifecycle and affordance hooks/runtime state.
- Preserve existing observation, telemetry, and console behaviour during the migration.

## Phase 2 Workflow

### Phase 0 – Risk Reduction & Baselines
1. **Employment Lifecycle Inventory** *(Step 1)*
   - Trace entry points: `WorldState._apply_need_decay`, nightly reset, respawn helpers, console commands, and simulation loop interactions.
   - Map coordinator methods used (`assign_jobs_to_agents`, `apply_job_state`, queue APIs) and note shared state (ctx caches, exit counters).
   - Capture notes in `tmp/wp306_phase2/employment_lifecycle.md` plus dependency graph for follow-up.
2. **Affordance Runtime Inventory**
   - Catalog hook registry usage, reservation helpers, and `AffordanceCoordinator` touch points.
   - Snapshot instrumentation options (`runtime_cfg.instrumentation`, `options`) and baseline hook allowlist.
   - Store notes in `tmp/wp306_phase2/affordance_runtime.md`.
3. **Baseline Test/Telemetry Sweep**
   - Run focused tests: `tests/test_affordance_hooks.py`, `tests/test_world_queue_integration.py`, `tests/test_world_runtime_facade.py`.
   - Record outputs in `tmp/wp306_phase2/baseline_tests.log`.

### Phase 1 – Employment Runtime Extraction
- Introduce `townlet.world.employment_runtime` module encapsulating employment queue/context helpers. (completed)
- Refactor `WorldState` to delegate through the new runtime (`world.employment_runtime`), providing shims for existing properties.
- Update tests consuming employment helpers to use the new facade; ensure console handlers continue to function. (completed)

### Phase 2 – Affordance Runtime Separation
- Move hook registry, reservation sync, and runtime instrumentation handling into `townlet.world.affordance_runtime_service`.
- Expose a `WorldAffordanceRuntime` facade used by console commands, observation builders, and policy guardrails.
- Ensure spatial index + reservation syncing behave identically; expand unit coverage if necessary.

### Phase 3 – Integration & Cleanup
- Update `SimulationLoop` and telemetry exports to consume new runtime/employment facades.
- Remove deprecated shim methods from `WorldState` once tests are green.
- Refresh docs (`docs/engineering/WORLDSTATE_REFACTOR.md`) and audit files to reflect the new structure.

## Deliverables
- New runtime modules with docstrings and type hints.
- Updated `WorldState` exposing `employment_runtime` / `affordance_runtime` accessors and deprecation shims.
- Passing baseline test suites and lint checks.
- Updated documentation & audit notes for WP-306 Phase 2.


### Phase 2 – Affordance Runtime Separation (Next Up)
- Extract affordance hook/queue orchestration into `townlet.world.affordance_runtime_service`. (completed)
- Provide facade exposing hook registry operations, reservation sync, instrumentation, and runtime access for observation/console. (completed)
- Update `WorldState` to delegate to the new service while keeping compatibility wrappers for `running_affordances_snapshot`, `active_reservations`, etc. (completed)
- Run affordance-related suites (`tests/test_affordance_hooks.py`, `tests/test_world_queue_integration.py`, observation builders) after extraction. (completed)
