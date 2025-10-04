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
- **Step 0.1: Behavioural Inventory**
  - Catalogue console command flows (queue ingestion, handler dispatch, history caching, error propagation) and log invariants.
  - Map telemetry consumers relying on `latest_console_results` / history for baselining.
- **Step 0.2: Test Reinforcement**
  - Expand unit tests covering `ConsoleBridge.apply()` edge cases (unknown command, admin enforcement, handler exception paths, cached results).
  - Add regression asserting console command metadata snapshot remains stable.
- **Step 0.3: Logging & Snapshot Baseline**
  - Capture log expectations (warning/error signals) for admin escalation and handler failures.
  - Record console result snapshots for canonical command sequences to support diffing post-refactor.

- **Step 0.1: Behavioural Guardrails**
  - Strengthen console dispatcher tests (admin gating, idempotency, error propagation) and ensure telemetry snapshots include console history/assertions.

### Phase 1: API Segmentation

- **Step 1.1: Consumer Inventory & Touchpoints**
  - Enumerated console consumers and expectations:
    - `SimulationLoop.step` — drains `TelemetryPublisher` queue and pushes results back to telemetry (`drain_console_buffer`, `record_console_results`).
    - `TelemetryPublisher.queue_console_command` — enforces auth, normalises payloads, buffers commands for world intake.
    - `WorldState.apply_console` / `ConsoleBridge.apply` — validates envelopes, enforces mode/cmd_id, dispatches handlers, records audit history.
    - `create_console_router` (console handlers) — registers domain-specific handlers, relies on bridge for history/caching.
    - UI/CLI surfaces (`scripts/observer_ui.py`, `townlet_ui.dashboard`, tests) — consume telemetry snapshots (`console_results`, `console_commands`).
    - Test suites (`tests/test_console_*`, new `tests/test_console_bridge_unit.py`) — assert behaviour of bridge, auth, dispatcher.
  - Dependency matrix (command flow): enqueue (TelemetryPublisher) → drain (SimulationLoop/WorldState) → dispatch (ConsoleBridge/handlers) → telemetry snapshot (`console_results`, history, audit) → UI clients.
- **Step 1.2: Interface Definition**
  - Proposed `ConsoleService` protocol (Python typing notation):
    ```python
    class ConsoleService(Protocol):
        def queue_command(self, payload: Mapping[str, Any]) -> None: ...
        def drain(self) -> list[ConsoleCommandEnvelope]: ...
        def submit(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult: ...
        def register_handler(
            self,
            name: str,
            handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult],
            *,
            mode: Literal["viewer", "admin"] = "viewer",
            require_cmd_id: bool = False,
        ) -> None: ...
        def history(self, cmd_id: str) -> ConsoleCommandResult | None: ...
        def clear(self) -> None: ...
    ```
  - `ConsoleBridge` retains history buffer, handler registry, and audit dispatch; service facade will expose queue/drain methods to world/telemetry callers.
- **Step 1.3: Envelope & Result Contracts**
  - Updated `docs/engineering/CONSOLE_COMMAND_CONTRACT.md` to reinforce required fields (mode semantics, issuer propagation, error codes) and noted telemetry alignment.
  - Confirmed `TelemetryPublisher.export_state()` exposes `console_results` consistent with response schema; no discrepancies found.
- **Step 1.4: Shim Strategy Plan**
  - Plan to introduce `townlet.console.service` as façade; `WorldState` methods (`queue_console_command`, `apply_console`, etc.) will delegate via thin wrappers during migration.
  - Temporary shims: `WorldState` retains `_console` but exposes new service attribute; telemetry and router creation import service module to avoid circular dependency.
  - Feature flag deemed unnecessary; migration will be staged via adapters and exhaustive tests.
- **Step 1.5: Exit Criteria & Checklist**
  - Validation on extraction: rerun full test suite, diff console result baselines (`tests/data/baselines/console_results_employment_review.json`), ensure new service satisfies protocol, and verify logs for auth/admin flows.
  - Owners: Console API – *A. Rivera*; Telemetry integration – *S. Iqbal*; Review cadence aligned with weekly grid-refactor sync.

### Phase 2: Implementation Extraction
- **Step 2.1: Service Module Scaffolding**
  - Create `townlet/console/service.py` (or similar) housing the `ConsoleService` implementation; move handler registration, history, and apply logic behind the protocol while re-exporting existing functionality.
  - Maintain backwards compatibility by importing the new service inside `WorldState` and exposing the same public methods.
- **Step 2.2: WorldState Delegation Layer**
  - Replace direct `_console` method calls in `WorldState` with thin delegations to the new service, ensuring signatures (`apply_console`, `consume_console_results`, etc.) remain unchanged.
  - Provide temporary compatibility shims (e.g., properties exposing the service instance) for external callers.
- **Step 2.3: Telemetry & Loop Integration**
  - Update `SimulationLoop`, `TelemetryPublisher`, and router construction to use the service abstraction; adjust imports to avoid cycles.
  - Refresh tests and baselines (console/telemetry snapshots) to ensure behaviour is unchanged.
- **Step 2.4: Logging & Audit Preservation**
  - Confirm log messages (`console_admin_request_blocked`, handler failures) still fire under the new wiring and maintain audit history/back-fill.
- **Step 2.5: Validation & Rollback Hooks**
  - Execute full test suite, diff recorded baselines, and prepare rollback instructions if unexpected regressions appear.

### Phase 3: Cleanup & Validation

- **Step 3.1: Shim Removal & Code Cleanup**
  - Eliminate temporary compatibility layers in `WorldState` (legacy properties, direct bridge access) once consumers exclusively use `ConsoleService`.
  - Ensure no modules import the old bridge directly (grep for `ConsoleBridge` outside service module) and tidy unused imports or helpers.
- **Step 3.2: Documentation Updates**
  - Refresh architecture docs (`docs/engineering/WORLDSTATE_REFACTOR.md`, console contract, roadmap) to describe the new service abstraction.
  - Update developer-facing guides (e.g., README snippets, console command docs) to mention the service module and new import paths.
- **Step 3.3: Validation & Snapshot Diff**
  - Re-run full pytest suite; diff console/telemetry baselines to confirm no behavioural drift.
  - Inspect logs for key warnings/errors (`console_admin_request_blocked`, handler failure logs) to verify signals remain.
- **Step 3.4: Rollback & Monitoring Notes**
  - Rollback plan: reintroduce the previous `ConsoleBridge` instantiation in `WorldState` (commit `HEAD~1`), remove `ConsoleService` import, and rerun the console regression suite before redeploying.
  - Monitoring: watch for `console_admin_request_blocked` warnings and handler failure logs in staging; compare `console_results` telemetry against baselines for the first few deployments.

## Milestone M2 – Affordance Runtime & Employment Separation

### Phase 0: Risk Reduction — **Completed**

- **Step 0.1: Benchmark & Profiling Baseline** *(done)*
  - Benchmarks captured in `benchmarks/m2_affordance_employment_baseline.json` for 10/30/60-agent loads.
  - Telemetry baselines stored at `tests/data/baselines/m2_affordance_heavy.json` and `m2_employment_queue_heavy.json`.
- **Step 0.2: State & Dependency Inventory** *(done)*
  - Inventory recorded in Appendix B (affordance/employment state) and Appendix F (migration playbook).
- **Step 0.3: Test Coverage Augmentation** *(done)*
  - Existing suites (`tests/test_affordance_telemetry.py`, `tests/test_employment_queue_invariants.py`) verified to cover metadata and queue behaviours; no additional cases needed at this stage.
- **Step 0.4: Migration Playbook** *(done)*
  - Drafted in Appendix F with staged rollout and owners.

### Phase 1: Affordance Runtime Extraction
- **Step 1.1: Interface Definition & Context**
  - Finalise the `AffordanceCoordinator` protocol (start, release, resolve, snapshot) and specify its required context (queue manager, emit_event, hook registry, telemetry sink, reservation sync).
- **Step 1.2: Module Extraction**
  - Move runtime logic into `townlet/world/affordance_runtime.py`, ensuring hook dispatch, running-affordance tracking, and metadata capture live outside `WorldState`.
- **Step 1.3: Integration & Testing**
  - Update `WorldState` to delegate to the coordinator, adjust hook registration, and refresh tests/baselines (including `m2_affordance_heavy.json` diffs) to confirm no behavioural drift.
- **Step 1.4: Rollback Plan**
  - Document fallback instructions (switch back to legacy methods) before moving on to employment extraction.
- **Status**: Coordinator extracted (`src/townlet/world/affordance_runtime.py`), `WorldState` delegates via `AffordanceCoordinator`, and full test suite/regression baselines pass.

### Phase 2: Employment & Queue Management
- **Step 2.1: Service Boundary Definition**
  - Finalise the employment service interface (`enqueue_exit`, `defer_exit`, `manual_exit`, `queue_snapshot`, `tick_update`) and document context dependencies (queue manager, emit_event, telemetry registry).
- **Step 2.2: Implementation Split**
  - Extract employment logic into a dedicated coordinator module, ensuring queue state, timestamps, and manual exits live outside `WorldState` while maintaining telemetry metrics.
- **Step 2.3: Queue Conflict & Telemetry Wiring**
  - Decouple queue-conflict tracking and telemetry hooks from `WorldState`, inject dependencies via the new service, and adjust console/telemetry consumers accordingly.
- **Step 2.4: Rollback Plan**
  - Record rollback instructions (restore legacy methods/state) prior to integration.
- **Status**: Employment coordinator added (`src/townlet/world/employment_service.py`), `WorldState` delegation updated, tests passing; queue conflict wiring unchanged pending Phase 3.

### Phase 3: Integration & Regression
- **Step 3.0: Readiness & Risk Check**
  - Review Phase 1/2 pull requests, TODO markers, and ensure pending shims are logged with owners.
  - Confirm rollback points exist (git tags or feature branches) for both coordinators and record in release notes.
  - Sync telemetry baseline fixtures and snapshot scripts to latest schema to avoid false alarms.
- **Step 3.1: World Runtime Integration Sweep**
  - Run focused integration suites (`pytest tests/test_world_queue_integration.py tests/test_world_local_view.py tests/test_telemetry_baselines.py`).
  - Execute an end-to-end simulation (`python scripts/run_simulation.py configs/examples/poc_hybrid.yaml`) capturing telemetry diffs for console, affordance, and employment flows.
  - Inspect logs for ordering issues (reservation sync, employment exits) and file follow-up tasks.
- **Step 3.2: Telemetry & UI Verification**
  - Compare telemetry exports against baselines (`m2_affordance_heavy.json`, `m2_employment_queue_heavy.json`) and update fixtures if behaviour is unchanged.
  - Smoke test observer UI (`python scripts/observer_ui.py configs/examples/poc_hybrid.yaml`) to confirm command history, queue metrics, and affordance panels render correctly.
  - Update documentation only if schemas or user-visible output changed; otherwise note stability.
- **Step 3.3: Performance & Load Checks**
  - Run heavy scenarios (`python scripts/run_simulation.py configs/scenarios/queue_conflict.yaml`) and capture tick duration metrics.
  - Compare against pre-refactor benchmarks (±5 % tolerance); investigate regressions with profiling if needed.
- **Step 3.4: Regression Hardening**
  - Close identified coverage gaps with additional integration/property tests targeting new service boundaries.
  - Ensure `ruff check src tests`, `ruff format`, and `mypy src` pass; resolve warnings introduced during migration.
  - Verify employment/affordance coordinators expose deterministic snapshot APIs for future testability.
- **Step 3.5: Sign-off & Transition**
  - Produce milestone closure note summarising outcomes, risks, and follow-up backlog.
  - Update `GRID_REFACTOR_PLAN.md` status trackers, appendices, and rollout notes to reflect completion.
  - Prepare handoff to Milestone M3 (observation/runtime simplification) with any outstanding dependencies.

## Milestone M3 – Observation & World Runtime Simplification

### Status Snapshot
- Phase 0 (Risk Reduction) – **Completed** (fixtures regenerated, RNG docs/tests, integration matrix & baselines captured).
- Phase 1 (Runtime Core Extraction) – **Completed** (WorldRuntime facade shipped with flag, telemetry/runtime wiring, CLI + test coverage).
- Phase 2 (Observation Helper Relocation) – **Completed** (helpers extracted to `world/observation.py`, builder refactored, telemetry/policy parity confirmed).
- Phase 3 (Final Cleanup) – Planned.

### Phase 0: Risk Reduction

- **Step 0.1: Observation Contract Audit**
  - Task: Enumerate all observation exporters (`observations/builder.py`, policy adapters) and document expected tensors/keys per variant.
  - Task: Regenerate golden fixtures (`tests/data/observations/baseline_*.npz`, `tests/data/baselines/telemetry_snapshot_baseline.json`) via `python scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 200 --telemetry-path tmp/telemetry_baseline.json`.
  - Task: Add contract assertions to `tests/test_observation_baselines.py` ensuring new fixtures align with documented schemas (shape, dtype, key ordering).
- **Step 0.2: RNG & State Handling**
  - Task: Trace RNG entry points (`townlet/utils/rng.py`, `WorldState.get_rng_state/set_rng_state`) and summarise sequencing expectations in `docs/engineering/WORLDSTATE_REFACTOR.md`.
  - Task: Add regression coverage in `tests/test_utils_rng.py` for state export/import parity and nightly reset flows.
  - Task: Validate snapshot import/export by running `pytest tests/test_snapshot_manager.py tests/test_snapshot_migrations.py` and logging any dependencies on runtime order.
- **Step 0.3: Integration Test Matrix & Tooling**
  - Task: Build a dependency matrix of integration suites (world, telemetry, UI) and create a test checklist in `docs/engineering/WORLDSTATE_REFACTOR.md` appendix.
  - Task: Establish lint/type clean-up goals—track Ruff/Mypy failures relevant to `townlet/world`/`observations` in `PROJECT_CLEAN_ORDER.md` with owners and target phases.
  - Task: Design runtime feature flag (`TOWNLET_LEGACY_RUNTIME=1`) with acceptance criteria, including CLI/environment wiring and documentation for toggling during validation.
- **Step 0.4: Baseline Telemetry & Performance Capture**
  - Task: Execute reference simulations (`python scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 500`, `python scripts/run_simulation.py configs/scenarios/queue_conflict.yaml --ticks 500`) and archive telemetry/perf metrics in `benchmarks/m3_runtime_baseline.json`.
  - Task: Capture observer dashboard snapshot (`python scripts/observer_ui.py configs/examples/poc_hybrid.yaml --ticks 5 --refresh 0.1`) and record expected panels/state for comparison post-refactor.
  - Task: Document success criteria (tick throughput ±5 %, telemetry schema unchanged) in the plan to inform Phase 1/2 validation gates.
  - Status: Baseline metrics recorded at ~2.94k (poc_hybrid) and ~3.06k (queue_conflict) ticks/sec; reference telemetry snapshot stored in `tmp/observer_snapshot.txt`. Acceptance threshold logged as ±5 % throughput variance with unchanged `schema_version`.

### Phase 1: Runtime Core Extraction

- **Step 1.1: Create `WorldRuntime` Facade**
  - Task 1.1.1: Draft runtime interface (`class WorldRuntime`) covering lifecycle hooks (`bind_world`, `queue_console`, `apply_actions`, `tick`, `snapshot`).
  - Task 1.1.2: Implement façade in `src/townlet/world/runtime.py`, delegating to existing WorldState internals behind a feature flag.
  - Task 1.1.3: Add unit tests (`tests/test_world_runtime_facade.py`) ensuring the facade invokes WorldState methods in correct order and propagates exceptions.
  - **Status**: Completed (facade landed, unit suite added, integrated into `townlet/world/__init__.py`).
- **Step 1.2: Slim `WorldState`**
  - Task 1.2.1: Introduce thin delegations inside `WorldState` that forward to `WorldRuntime` when active, retaining legacy paths behind `TOWNLET_LEGACY_RUNTIME`.
  - Task 1.2.2: Move tick sequencing helpers (`process_respawns`, `apply_affordances`, `resolve_affordances`, `apply_nightly_reset`) into the runtime module while preserving public signatures.
  - Task 1.2.3: Update policy (`SimulationLoop`), telemetry, and console orchestrators to call the runtime entry points instead of direct WorldState methods.
  - **Status**: Completed (SimulationLoop delegates through facade with env flag + telemetry variant wiring; legacy path guarded).
- **Step 1.3: Compatibility & Rollback Shims**
  - Task 1.3.1: Wire `TOWNLET_LEGACY_RUNTIME` env handling into `SimulationLoop` initialiser and CLI entry points.
  - Task 1.3.2: Emit telemetry field (`runtime_variant`) describing active runtime for diffability.
  - Task 1.3.3: Document rollback instructions in `docs/engineering/WORLDSTATE_REFACTOR.md` and ensure tests cover both flag modes (parametrise key integration suites).
  - **Status**: Completed (runtime CLI switch shipped, telemetry carries variant, docs + tests updated).

### Phase 2: Observation Helper Relocation

- **Step 2.1: Move Observation Helpers**
  - Task 2.1.1: Extract local view builders, reservation cache helpers, and snapshot utilities from `WorldState` into a new `townlet/world/observations.py` (or existing observation module) while maintaining import compatibility via shims.
  - Task 2.1.2: Update `WorldState` to call relocated helpers; provide feature flag or temporary proxy to allow fallback if regressions surface.
  - Task 2.1.3: Add targeted unit tests for the new helper module (`tests/test_world_observation_helpers.py`) covering map generation, reservation overlays, and agent context outputs.
- **Step 2.2: Update Observation Builder & Tests**
  - Task 2.2.1: Refactor `ObservationBuilder` to consume the new helper APIs instead of reaching into `WorldState` internals.
  - Task 2.2.2: Refresh observation fixtures (`tests/data/observations/baseline_*.npz`) and expand contract assertions for relocated helper outputs.
  - Task 2.2.3: Ensure policy runners and replay loaders continue to work with the new metadata (update `tests/test_simulation_loop_runtime.py` parametrisation if required).
- **Step 2.3: Telemetry & Policy Integration**
  - Task 2.3.1: Adjust telemetry publishers and stability monitors to reference relocated observation utilities; validate snapshot parity against frozen fixtures.
  - Task 2.3.2: Update documentation for observation variants (`docs/engineering/WORLDSTATE_REFACTOR.md`, observation README) with new module boundaries and call flows.
  - Task 2.3.3: Run cross-runtime regression suites (legacy vs facade) ensuring observation outputs remain deterministic; backfill additional tests if discrepancies arise.

### Phase 3: Final Cleanup

### Phase 2: Observation Helper Relocation

- **Step 2.1: Move Observation Helpers**
  - Transfer local view builders and context helpers to observation modules, leaving `WorldState` as a data provider.
- **Step 2.2: Update Observation Builder & Tests**
  - Ensure observation builder interacts with the new provider interface.
- **Step 2.3: Telemetry & Policy Integration**
  - Adjust telemetry publishers and policy adapters to consume relocated helpers and validate snapshot parity against frozen fixtures.
  - Refresh documentation for observation variants to reflect new module boundaries.

### Phase 3: Final Cleanup

- **Step 3.1: Dead Code Removal**
  - Task 3.1.1: Catalogue `WorldState` methods/attributes now unused (legacy queue helpers, direct observation caches) and remove or deprecate behind feature flag.
  - Task 3.1.2: Update type hints/invariants for remaining `WorldState` APIs to reflect facade/observation modules; ensure mypy clean for `townlet/world`.
  - Task 3.1.3: Delete temporary compatibility shims once integration tests confirm no downstream usage.
- **Step 3.2: Documentation & Validation**
  - Task 3.2.1: Refresh architecture diagrams plus narrative sections in `docs/engineering/WORLDSTATE_REFACTOR.md` to capture final module boundaries and runtime flow.
  - Task 3.2.2: Regenerate telemetry/observation baselines post-cleanup (facade + legacy modes) and archive diffs.
  - Task 3.2.3: Run `pytest` (full suite), long-form simulation smoke (`scripts/run_simulation.py ... --ticks 5000`), and observer dashboard spot-check; record results in plan appendix.
- **Step 3.3: Tooling Debt Burn-down**
  - Task 3.3.1: Drive `ruff check src/townlet/world src/townlet/observations` to zero findings; align import ordering/annotation modernisation.
  - Task 3.3.2: Ensure `mypy src/townlet/world src/townlet/observations` passes without ignores; lift legacy `type: ignore`s where feasible.
  - Task 3.3.3: Decide fate of `TOWNLET_LEGACY_RUNTIME` flag (✅ completed – legacy runtime removed; facade is sole path).

## Milestone M4 – Hardening & Adoption

### Status Snapshot
- Phase 0 (Risk Reduction) – Pending.
- Phase 1 (Rollout & Monitoring) – Pending.
- Phase 2 (Backlog & Follow-ups) – Pending.
- Phase 3 (Post-mortem) – Pending.

### Phase 0: Risk Reduction

- **Step 0.1: Ops & Tooling Review**
  - Task 0.1.1: Inventory CI workflows, Docker images, and packaging scripts for old import paths; update to use `townlet.world.observation` and runtime facade.
  - Task 0.1.2: Verify training/automation notebooks for deprecated APIs; file follow-up issues or supply migration snippets.
  - Task 0.1.3: Validate telemetry ingestion pipeline (dashboards, alerting) against new `runtime_variant` field and document any consumer updates.
- **Step 0.2: Release Readiness Audit**
  - Task 0.2.1: Confirm lint/type suites run clean on main branch or capture remaining debt with owners/dates.
  - Task 0.2.2: Establish regression runbook (facade vs legacy mode) to execute before merges during rollout.

### Phase 1: Rollout & Monitoring

- **Step 1.1: Merge Strategy**
  - Task 1.1.1: Define staging branches/feature flags for incremental adoption (e.g., enable facade in canary envs first).
  - Task 1.1.2: Schedule stakeholder sign-off (UI, telemetry, training) before toggling default runtime.
- **Step 1.2: Monitoring Hooks**
  - Task 1.2.1: Add structured logs/metrics for runtime-switch decisions (`runtime_variant`, queue metrics) to detect regressions.
  - Task 1.2.2: Establish dashboards/alerts for tick duration, console error rates, telemetry drop counts during rollout window.

### Phase 2: Backlog & Follow-ups

- **Step 2.1: Issue Sweep**
  - Task 2.1.1: Review open PRs/issues referencing legacy helpers; update or close with guidance.
  - Task 2.1.2: Coordinate with documentation/help teams to publish migration notes for external contributors.
- **Step 2.2: Debt Burn-down**
  - Task 2.2.1: Drive remaining `townlet.world` Ruff/mypy findings to zero.
  - Task 2.2.2: Decide timeline for removing `TOWNLET_LEGACY_RUNTIME`; capture rollback plan if retained longer term. (✅ completed – toggle removed)

### Phase 3: Post-mortem

- **Step 3.1: Lessons Learned**
  - Task 3.1.1: Run a retrospective covering risk mitigations, tooling gaps, and stakeholder feedback.
  - Task 3.1.2: Capture metrics (perf deltas, incident counts) to inform future refactors.
- **Step 3.2: Cleanup Tasks**
  - Task 3.2.1: Remove rollout-specific logging/feature flags once stable.
  - Task 3.2.2: Archive design notes, update Confluence/README references, and close the GRID_REFACTOR plan with final status.

## Cross-Cutting Risk Reduction Highlights

- Feature flags to toggle between old/new implementations during rollout if needed.
- Incremental refactors per milestone to limit blast radius.
- Continuous snapshot diffing (telemetry, console, observation outputs) to catch behavioural changes early.
- Joint code reviews between console, affordance, and employment owners for cross-cutting impacts.
- Communication plan for downstream consumers (training scripts, UI) to adjust to API changes.

## Appendix A – Coverage & Baseline Notes

- Expanded console authentication and dispatcher suites to cover admin warning logs, cached results across multiple ticks, and handler error propagation (`tests/test_console_auth.py`, `tests/test_console_dispatcher.py`).
- Added dedicated `ConsoleBridge` unit coverage for unknown commands, admin enforcement, handler errors, cmd_id caching, and history limits (`tests/test_console_bridge_unit.py`).
- Added employment queue invariants and observation/telemetry baseline tests to guard snapshots before refactor (`tests/test_employment_queue_invariants.py`, `tests/test_observation_baselines.py`, `tests/test_telemetry_baselines.py`).
- Captured deterministic observation tensors (`tests/data/observations/baseline_*.npz`) and telemetry snapshots (`tests/data/baselines/*`) for regression diffing.
- Stored console result baseline for employment review flow in `tests/data/baselines/console_results_employment_review.json` to support command routing diffs.
- Test suite executed via `.venv` with PATH prefixed to include `.venv/bin` so subprocess invocations resolve to the editable package.
- Milestone M2 pre-work: added heavy-load telemetry snapshots (`tests/data/baselines/m2_affordance_heavy.json`, `tests/data/baselines/m2_employment_queue_heavy.json`) and micro-benchmarks (`benchmarks/m2_affordance_employment_baseline.json`).

## Appendix B – WorldState Responsibility Map

- **Console Bridge**: `apply_console`, `consume_console_results`, `register_console_handler`, `_record_console_result`, `_console` state.
- **Affordance Runtime**: `_start_affordance`, `_dispatch_affordance_hooks`, `resolve_affordances`, `_handle_blocked`, runtime/queue glue.
- **Employment & Queueing**: `_employment_enqueue_exit`, `employment_queue_snapshot`, `employment_defer_exit`, `employment_request_manual_exit`, `_get_employment_context`.
- **Observations & Local Views**: `local_view`, `agent_context`, `running_affordances_snapshot`, `request_ctx_reset`, observation caches.
- **Lifecycle & Misc**: RNG state (`get_rng_state`, `set_rng_state`), respawn/terminated bookkeeping, `_pending_events` emission, nightly reset helpers.
- **External Touch Points**: `SimulationLoop.step` orchestrates console → policy → affordance ordering; `TelemetryPublisher` consumes queue/affordance snapshots; observation builders query local views; console handlers read employment metrics.

### Affordance & Employment State Inventory (M2 Phase 0)
- Affordance runtime mutates `_running_affordances`, `_active_reservations`, `_pending_events`, and relies on `queue_manager` plus hook registry.
- Employment engine keeps `_employment_state`, `_employment_exit_queue`, `_employment_manual_exits`, `_employment_exit_queue_timestamps`, and surfaces metrics through `employment_queue_snapshot`.
- Telemetry integration currently fetches runtime snapshots via `WorldState.running_affordances_snapshot()` and queue metrics via `WorldState.employment_queue_snapshot()`; both will need new service interfaces.

## Appendix F – Milestone M2 Migration Playbook (Draft)
- **Step 1**: Extract affordance runtime into coordinator module while keeping employment logic untouched. Gate via feature branch and verify against `m2_affordance_heavy` baseline.
- **Step 2**: Migrate employment engine and queue/conflict tracking to dedicated service, validating against `m2_employment_queue_heavy` baseline.
- **Step 3**: Update observation/telemetry consumers and rerun comprehensive benchmarks; prepare rollback instructions (revert service wiring) for each phase.
- Owners: Affordance runtime – *J. Chen*; Employment – *M. Patel*; Telemetry integration – *S. Iqbal*; Benchmark maintenance – *A. Rivera*.

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

## Milestone M1 – Console Bridge Extraction Status
- Phase 0 (Risk Reduction) – **Completed** (tests, baselines, coverage inventory)
- Phase 1 (API Segmentation) – **Completed** (consumer inventory, protocol sketch)
- Phase 2 (Implementation Extraction) – **Completed** (service facade, delegation, test suite)
- Phase 3 (Cleanup & Validation) – **Completed** (docs refreshed, shims removed, full suite rerun, rollback noted)

## Milestone M2 – Affordance Runtime & Employment Separation Status
- Phase 0 (Risk Reduction) – **Completed** (benchmarks, telemetry baselines, migration playbook)
- Phase 1 (Affordance Runtime Extraction) – **Completed** (coordinator module, delegation, tests)
- Phase 2 (Employment & Queue Management) – **Completed** (employment coordinator, delegation, tests)
- Phase 3 (Integration & Regression) – **Completed** (integration tests/runtime sweeps, telemetry/UI verification, performance runs, lint/type audit)

### Milestone M2 Closure Notes
- Executed focused pytest suites (`tests/test_world_queue_integration.py`, `tests/test_world_local_view.py`, `tests/test_telemetry_baselines.py`) and 50-tick sim smoke (`scripts/run_simulation.py configs/examples/poc_hybrid.yaml`) with no regressions beyond expected console auth notices.
- Observer dashboard smoke (`scripts/observer_ui.py configs/examples/poc_hybrid.yaml --ticks 5`) rendered affordance/employment panels correctly; telemetry baselines remained unchanged.
- Queue-conflict load scenario (`scripts/run_simulation.py configs/scenarios/queue_conflict.yaml --ticks 200`) sustained ~3.8k ticks/sec; telemetry buffer warnings persist when running without a consumer—recorded as known behaviour, no new risk.
- `ruff check`, `ruff format --check`, and `mypy src` report long-standing repository violations; captured results for backlog triage (no regressions introduced by M2 work).
- Ready to proceed to Milestone M3; no additional shims or rollback blockers identified.
