# Grid Refactor Implementation Plan

## Milestone M0 – Foundations & Risk Reduction

### Phase 0: Stabilisation & Discovery

- **Step 0.1: Test Coverage & Snapshot Baseline**
  - Audit existing tests touching `WorldState` pathways (console, affordances, employment, observations).
  - Add missing regression tests for console handler authorisation, queue manager invariants, affordance outcomes, observation snapshots.
  - Capture telemetry/console snapshot fixtures for before/after diffing.
- **Step 0.2: Architecture & Inventory**
  - Produce design note summarising proposed module boundaries (`world/runtime.py`, `world/console_bridge.py`, `world/employment.py`, etc.) and their public interfaces.
  - Catalogue shared state and side effects (reservations, pending events, queue conflicts, RNG usage), noting invariants and ordering requirements.
  - Map all call sites into a dependency graph to identify cycles and high-risk touchpoints.
- **Step 0.3: Tooling & Workflow Prep**
  - Update lint/type configurations to recognise future module layout.
  - Set up long-lived feature branch naming and review cadence.
  - Identify “code owners” for console, affordance, and employment domains to keep reviews consistent.

## Milestone M1 – Console Bridge Extraction

### Phase 0: Risk Reduction

- **Step 0.1: Behavioural Guardrails**
  - Strengthen console dispatcher tests (admin gating, idempotency, error propagation) and ensure telemetry snapshots include console history/assertions.

### Phase 1: API Segmentation

- **Step 1.1: Interface Definition**
  - Define a lightweight `ConsoleService` protocol capturing the minimal methods `SimulationLoop` and other consumers rely on.
- **Step 1.2: Data Contracts**
  - Document console payload shapes (envelopes, results) to ensure stability during migration.

### Phase 2: Implementation Extraction

- **Step 2.1: Module Creation**
  - Move console bridge logic from `WorldState` into a new module (e.g., `world/console_bridge.py`), keeping behaviour behind shim methods.
- **Step 2.2: Wiring & Shims**
  - Update `WorldState` to delegate to the new console module while preserving public methods (`apply_console`, `consume_console_results`).
- **Step 2.3: Telemetry/Loop Integration**
  - Adjust `SimulationLoop` and telemetry components to use the new console interface, ensuring tests and snapshots still pass.

### Phase 3: Cleanup & Validation

- **Step 3.1: Remove Deprecated Paths**
  - Delete temporary shims once consumers migrate.
- **Step 3.2: Docs & Validation**
  - Update design note and inline documentation to reflect the new console architecture.
  - Run full test suite; compare pre/post snapshots.

## Milestone M2 – Affordance Runtime & Employment Separation

### Phase 0: Risk Reduction

- **Step 0.1: Performance & Regression Benchmarks**
  - Capture micro-benchmarks around affordance resolution and employment queue operations.
- **Step 0.2: Migration Plan**
  - Identify shared state between affordance runtime and employment components; plan sequencing to avoid breaking changes.

### Phase 1: Affordance Runtime Extraction

- **Step 1.1: Interface Sketch**
  - Define an `AffordanceCoordinator` interface covering runtime binding, action application, and resolution.
- **Step 1.2: Module Split**
  - Move affordance helpers to a dedicated module (`world/affordance_runtime.py`), wiring dependencies via explicit context objects.
- **Step 1.3: Hook & Telemetry Alignment**
  - Ensure hooks, telemetry payloads, and console commands access affordance data via the new module.

### Phase 2: Employment & Queue Management

- **Step 2.1: Extract Employment Engine**
  - Relocate employment-specific logic into `world/employment.py`, keeping state transitions explicit.
- **Step 2.2: Queue Manager Decoupling**
  - Separate queue-conflict recording from `WorldState`, exposing it through injected dependencies.

### Phase 3: Integration & Regression

- **Step 3.1: Update Observation/Telemetry Consumers**
  - Adjust observation builder, telemetry publisher, and console handlers to reference new employment/queue interfaces.
- **Step 3.2: Benchmarks & Tests**
  - Re-run benchmarks; update documentation with observed impacts.

## Milestone M3 – Observation & World Runtime Simplification

### Phase 0: Risk Reduction

- **Step 0.1: Observation Contract Audit**
  - Freeze observation schemas (hybrid/full/compact) and capture golden fixtures.
- **Step 0.2: RNG & State Handling**
  - Document RNG usage and world snapshot semantics to avoid behavioural drift.

### Phase 1: Runtime Core Extraction

- **Step 1.1: Create `WorldRuntime` Facade**
  - Introduce a runtime orchestrator responsible for tick sequencing (`process_respawns`, `apply_actions`, `resolve_affordances`, etc.).
- **Step 1.2: Slim `WorldState`**
  - Reduce `WorldState` responsibilities to pure data/manipulation (agents, objects, reservations).

### Phase 2: Observation Helper Relocation

- **Step 2.1: Move Observation Helpers**
  - Transfer local view builders and context helpers to observation modules, leaving `WorldState` as a data provider.
- **Step 2.2: Update Observation Builder & Tests**
  - Ensure observation builder interacts with the new provider interface.

### Phase 3: Final Cleanup

- **Step 3.1: Dead Code Removal**
  - Remove unused fields/methods from `WorldState`, verifying type hints and invariants.
- **Step 3.2: Documentation & Validation**
  - Update `docs/engineering/WORLDSTATE_REFACTOR.md` and diagrams.
  - Execute full test suite, reproduce telemetry snapshots, run long-duration sim smoke.

## Milestone M4 – Hardening & Adoption

### Phase 0: Risk Reduction

- **Step 0.1: Ops & Tooling Review**
  - Check CI/build scripts for assumptions about old module layout; update as needed.

### Phase 1: Rollout & Monitoring

- **Step 1.1: Merge Strategy**
  - Coordinate incremental merges, ensuring each step is release-ready.
- **Step 1.2: Monitoring Hooks**
  - Add temporary logging/metrics where behaviour might change to monitor post-merge.

### Phase 2: Backlog & Follow-ups

- **Step 2.1: Issue Sweep**
  - Audit open tickets/PRs for conflicts with new structure; provide guidance or rebases.

### Phase 3: Post-mortem

- **Step 3.1: Lessons Learned**
  - Document successes, challenges, and future opportunities.
- **Step 3.2: Cleanup Tasks**
  - Remove temporary monitoring, mark work packages closed, archive design notes.

## Cross-Cutting Risk Reduction Highlights

- Feature flags to toggle between old/new implementations during rollout if needed.
- Incremental refactors per milestone to limit blast radius.
- Continuous snapshot diffing (telemetry, console, observation outputs) to catch behavioural changes early.
- Joint code reviews between console, affordance, and employment owners for cross-cutting impacts.
- Communication plan for downstream consumers (training scripts, UI) to adjust to API changes.

## Appendix A – Coverage & Baseline Notes

- Expanded console authentication and dispatcher suites to cover admin warning logs, cached results across multiple ticks, and handler error propagation (`tests/test_console_auth.py`, `tests/test_console_dispatcher.py`).
- Added employment queue invariants and observation/telemetry baseline tests to guard snapshots before refactor (`tests/test_employment_queue_invariants.py`, `tests/test_observation_baselines.py`, `tests/test_telemetry_baselines.py`).
- Captured deterministic observation tensors (`tests/data/observations/baseline_*.npz`) and telemetry snapshots (`tests/data/baselines/*`) for regression diffing.
- Test suite executed via `.venv` with PATH prefixed to include `.venv/bin` so subprocess invocations resolve to the editable package.

## Appendix B – WorldState Responsibility Map

- **Console Bridge**: `apply_console`, `consume_console_results`, `register_console_handler`, `_record_console_result`, `_console` state.
- **Affordance Runtime**: `_start_affordance`, `_dispatch_affordance_hooks`, `resolve_affordances`, `_handle_blocked`, runtime/queue glue.
- **Employment & Queueing**: `_employment_enqueue_exit`, `employment_queue_snapshot`, `employment_defer_exit`, `employment_request_manual_exit`, `_get_employment_context`.
- **Observations & Local Views**: `local_view`, `agent_context`, `running_affordances_snapshot`, `request_ctx_reset`, observation caches.
- **Lifecycle & Misc**: RNG state (`get_rng_state`, `set_rng_state`), respawn/terminated bookkeeping, `_pending_events` emission, nightly reset helpers.
- **External Touch Points**: `SimulationLoop.step` orchestrates console → policy → affordance ordering; `TelemetryPublisher` consumes queue/affordance snapshots; observation builders query local views; console handlers read employment metrics.

## Appendix C – Shared State & Ordering Assumptions

- `_active_reservations` and `queue_manager` must stay synchronised via `_sync_reservation`; console operations are applied **before** policy actions each tick.
- `_pending_events` batches world events; telemetry expects `world.drain_events()` immediately after `resolve_affordances` to emit hook outcomes.
- RNG state and tick progression occur in `SimulationLoop.step` prior to nightly resets; observation builders assume `episode_tick` already advanced.
- Employment counters (`_employment_exits_today`, queue timestamps) live inside `EmploymentEngine`; telemetry pulls fresh snapshots after each publish.
- Observation helpers rely on `_objects_by_position` and agent dictionaries remaining consistent during per-tick mutation.

## Appendix D – Proposed Interface Sketches

- `ConsoleService`: `queue(payload)`, `consume_results()`, `history(cmd_id)`, `register(name, handler, mode="viewer")` backed by a dedicated console module.
- `AffordanceCoordinator`: `start(agent, object, affordance, tick)`, `release(agent, object, success, reason, tick)`, `resolve(tick)`, `snapshot()`; context injected with queue manager, hook dispatch, telemetry emitters.
- `EmploymentCoordinator`: `enqueue_exit(agent, tick)`, `defer_exit(agent)`, `manual_exit(agent, tick)`, `snapshot()`, `export_state()`, `import_state()` with structured events.
- `WorldRuntime`: orchestrates tick sequencing (`process_respawns`, `apply_console`, `apply_actions`, `resolve_affordances`, `record_telemetry`) leaving `WorldState` as a data container.

## Appendix E – Workflow & Ownership Preparation

- **Lint/Type Config**: No immediate changes to `pyproject.toml`; prepared to add module-specific overrides once new packages land.
- **Branch Naming**: Adopt `feature/grid-refactor-m{milestone}-{focus}` (e.g., `feature/grid-refactor-m1-console`) for staged delivery; documented in contributing notes.
- **Code Owners**: Console – *A. Rivera*; Affordances – *J. Chen*; Employment – *M. Patel*; Runtime/Loop – *S. Iqbal*. Weekly review rota established.
- **Communication Plan**: Create `#townlet-grid-refactor` channel; publish weekly status including baseline diffs, outstanding risks, and upcoming merges.
