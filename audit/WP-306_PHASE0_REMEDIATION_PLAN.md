# WP-306 – World/Policy Decomposition Remediation Plan

## Phase 0 Findings (Discovery & Risk Reduction)

### Responsibility Inventory

- **`WorldState` (src/townlet/world/grid.py)`** currently blends:
  - Console bridge lifecycle (`ConsoleService` wiring, command registration, audit history, handler dispatch).
  - Employment orchestration (`EmploymentCoordinator`, queue exit resets, job schedule bootstrap and tick-time enforcement).
  - Affordance runtime plumbing (manifest loading, hook registry, reservation tracking, runtime instrumentation, queue conflict tracking).
  - Relationship/perturbation bookkeeping (relationship ledgers, rivalry churn, recent meal tracking, policy guardrails, stability snapshots).
  - Economy/state mutation (store stock, utilities, price spikes, need decay, RNG seeding, snapshot migrations).
  - Telemetry-facing views (spatial index rebuilds, accessor helpers consumed by observation/policy layers).

- **`PolicyRuntime` (src/townlet/policy/runner.py)** interleaves:
  - Behavior selection and anneal blending (behavior controller, option commit tracking, relationship guardrails).
  - PPO/BC training primitives (trajectory buffers, advantage computation, gradient statistics, network lifecycle).
  - Action/action-id bookkeeping (json encoding, lookup maps, telemetry snapshots).
  - Replay/rollout orchestration (dataset loaders, CLI entry points, PettingZoo bridges).
  - Promotion/telemetry hooks (promotion manager, health telemetry, CLI messaging).

### Coupling & Dependency Highlights

- `WorldState` exposes ~40 console/affordance/employment helpers that are imported directly by tests and runtime (`SimulationLoop`, console CLI, telemetry exporter). Strong coupling to `ConsoleService`, `EmploymentCoordinator`, `AffordanceCoordinator`, and queue/relationship subsystems.
- `PolicyRuntime` depends on `WorldState` internals (e.g., accessing agent snapshots, commitment metadata) and maintains overlapping interface for CLI & training harness; duplicate `set_anneal_ratio` definitions confirm drift between "runtime" and "trainer" code paths.
- Observation builders consume `WorldState` accessors; extraction must preserve `world.observation` interface to avoid regressions in existing tests/data fixtures.
- Console/telemetry already extracted to separate packages (`ConsoleService`, telemetry publisher) but `WorldState` still instantiates and coordinates them directly, complicating reuse.

### Baseline Evidence

- Targeted tests (baseline safety net):
  - `pytest tests/test_world_state_accessors.py tests/test_world_local_view.py tests/test_policy_anneal_blend.py` → **13 passed** (`tmp/wp306_phase0_baseline.log`).
- Lint probe (`ruff check src tests`) surfaces actionable debt in policy runner & related modules (unused methods, percent-format strings). Resolve alongside refactor to keep touch-points clean.
- TLS/telemetry suites remain green from WP-302 (no additional action needed for WP-306, but rerun focused suites after module extraction).

### Primary Risks Identified

1. **Interface drift** – External callers rely on `WorldState` methods (console handlers, employment hooks). Risk: missing methods or behavioural changes break runtime/tests.
   - *Mitigation*: introduce facade interfaces (`world.console`, `world.employment`, etc.) that forward to new modules; deprecate old attributes gradually with shim warnings.
2. **Observation regression** – Accessors back observation/telemetry fixtures; extraction could alter data shape/perf.
   - *Mitigation*: maintain accessor contract tests (`tests/test_world_state_accessors.py`, observation suites) at each phase; capture golden snapshots before major moves.
3. **Training pipeline interruption** – `PolicyRuntime` handles anneal/trajectory buffers for PPO/BC; splitting into services could break CLI/training flows.
   - *Mitigation*: craft explicit interfaces (`PolicyActionBridge`, `TrainingOrchestrator`) with integration tests (`tests/test_policy_anneal_blend.py`, CLI smoke) before removing legacy paths.
4. **Concurrency/worker state** – Flush threads and queue locks run through `WorldState`; moving employment/affordance managers must preserve locking semantics.
   - *Mitigation*: document current locking expectations; add stress/unit tests for employment queue and affordance runtime before and after migration.

## Implementation Roadmap (Phases, Steps, Tasks)

### Milestone 1 – Console & Telemetry Separation

- **Phase 0 Risk Reduction**
  1. Record console handler inventory and command schemas (export from `_register_default_console_handlers`).
  2. Capture console audit sample (run `scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 50`, archive `logs/console/commands.jsonl`).
  3. Add regression snapshot for `latest_transport_status()` to ensure metrics persist.
- **Phase 1 Console Bridge Extraction**
  1. Introduce `townlet.world.console_bridge` module encapsulating command registration + audit writes.
  2. Replace `_console` direct usage with bridge facade; migrate tests to new module.
  3. Update dependency injection in `SimulationLoop` and CLI to use bridge wrapper; run `tests/test_world_runtime_facade.py`, console/auth suits.
- **Phase 2 Telemetry Hook Simplification**
  1. Move telemetry-related helpers (queue conflict snapshots, runtime variant tagging) into dedicated service.
  2. Provide `WorldTelemetryView` data class consumed by publisher; adjust observation builder/test fixtures.
  3. Execute telemetry suites + targeted smoke run; update docs to describe new entry point.

### Milestone 2 – Employment & Affordance Modularisation

- **Phase 0 Risk Reduction**
  1. Document employment tick lifecycle (current calls to `employment.evaluate`, exit queue management).
  2. Capture affordance runtime instrumentation options + hook list; export config to `tmp/wp306_phase1_affordance.json` for reference.
  3. Run employment/affordance tests (`tests/test_affordance_hooks.py`, `tests/test_world_queue_integration.py`).
- **Phase 1 Employment Extraction**
  1. Create `townlet.world.employment_runtime` exposing scheduler, exit queue, metrics.
  2. Refactor `WorldState` to delegate job operations to new module; ensure `world.employment` API stays compatible via wrapper.
  3. Update employment tests + docs; ensure queue telemetry unaffected.
- **Phase 2 Affordance Runtime Separation**
  1. Encapsulate hook registry/reservation tracking in `AffordanceRuntimeContext`-derived module.
  2. Move event emission & need decay helpers to new runtime package; leave thin forwarding helpers in `WorldState` for migration period.
  3. Re-run affordance/perturbation suites and observation builders.

### Milestone 3 – Policy Runtime Decomposition

- **Phase 0 Risk Reduction**
  1. Snapshot current PPO/BC configuration defaults; store in `docs/audit/WP306_policy_baseline.md`.
  2. Run policy-centric tests (`tests/test_policy_anneal_blend.py`, `tests/test_policy_models.py`).
  3. Capture training CLI smoke run (dry-run with `scripts/run_training.py --config configs/examples/poc_hybrid.yaml --mode replay --ticks 10`).
- **Phase 1 Behavior & Action Bridge**
  1. Extract behavior/anneal blending to `policy.behavior_bridge` with clear interfaces.
  2. Ensure possession & option commit logic remains intact; add targeted unit tests.
- **Phase 2 Trajectory & Replay Services**
  1. Move trajectory collection, replay dataset loaders to dedicated service modules.
  2. Update CLI/training harness to consume new services; replace duplicate `set_anneal_ratio` with shared mixin to resolve lint issue.
- **Phase 3 Training Orchestrator**
  1. Introduce `PolicyTrainer` orchestrator managing PPO/BC loops, metrics, logging.
  2. Shift CLI entrypoints to orchestrator; keep adapters for backward compatibility (deprecation warnings).
- **Phase 4 Integration**
  1. Run full policy test suite + smoke training run.
  2. Update docs (`docs/engineering/WORLDSTATE_REFACTOR.md`, new module guides) and audit logs.

### Milestone 4 – Integration & Cleanup

- **Phase 0 Risk Reduction**
  1. Capture end-to-end benchmarks (ticks/sec, PPO epoch duration) prior to merge.
  2. Ensure observation fixtures updated (NPZ/golden data) and telemetry baselines exist.
- **Phase 1 Interface Harmonisation**
  1. Remove transitional shims, formalise new APIs in `__all__` exports.
  2. Update `tests/` to align with new module layout; search for deprecated attribute usage.
- **Phase 2 Rollout & Documentation**
  1. Refresh `GRID_REFACTOR_PLAN.md` and `audit/WORK_PACKAGES.md` with closure notes.
  2. Publish migration guide summarising API changes and upgrade steps for integrators.

## Phase 0 Exit Criteria

- Responsibility/dependency inventory documented (this file).
- Baseline tests logged to `tmp/wp306_phase0_baseline.log` for regression comparison.
- High-risk areas and mitigations identified for upcoming phases.
- Detailed milestone/phase plan (above) ready for execution with embedded risk-reduction checkpoints.

