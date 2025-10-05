# WP-306 – Phase 3 Policy Runtime Decomposition

## Objectives
- Break down `PolicyRuntime` and related training orchestration into focused components to simplify maintenance and testing.
- Isolate behaviour/anneal blending, trajectory/replay data management, and PPO/BC training loops behind clear interfaces.
- Preserve existing CLI/telemetry/contracts while deprecating ad-hoc helpers gradually.

## Phase Breakdown

### Phase 0 – Discovery & Risk Reduction
1. Inventory `PolicyRuntime`, `PolicyTrainer`, replay buffers, and promotion hooks; document responsibilities and dependencies (`tmp/wp306_phase3/policy_runtime.md`).
2. Baseline targeted tests: `tests/test_policy_anneal_blend.py`, `tests/test_policy_models.py`, `tests/test_policy_rivalry_behavior.py`; note results in `tmp/wp306_phase3/baseline_tests.log`.
3. Capture current CLI smoke reference (optional) to compare after refactor.

### Phase 1 – Behaviour & Action Bridge
- Extract behaviour/anneal blending into `policy.behavior_bridge` (decide, option commit, possession handling). (completed)
- Introduce interface consumed by `SimulationLoop`/CLI; add focused unit tests. (completed)

### Phase 2 – Trajectory & Replay Services
- Move `_transitions`, trajectory collection, replay dataset utilities into dedicated service(s). (completed)
- Update PPO/BC code to consume the new services; ensure serialization paths remain compatible. (completed)

### Phase 3 – Policy Training Orchestrator
- Create orchestrator responsible for PPO/BC loops, logging, telem snapshots. (completed — see `src/townlet/policy/training_orchestrator.py`)
- Refactor CLI entrypoints and training scripts to use orchestrator; retain compatibility shims. (completed; CLI now instantiates the orchestrator directly.)

### Phase 4 – Integration & Validation
- Reconcile imports, remove deprecated helper methods from `PolicyRuntime`. (completed)
- Run comprehensive policy suites and CLIs; refresh docs/audit notes. (completed; pytest + Ruff commands logged below, including `tests/test_policy_runtime_surface.py`)

## Deliverables
- New policy modules (behaviour bridge, trajectory service, training orchestrator) with docstrings and type hints.
- Updated `PolicyRuntime` reduced to thin coordination layer.
- Passing targeted tests and baseline parity verified.
- Documentation updates capturing architectural changes.



### Validation notes
- Targeted training suites now run clean (`.venv/bin/python -m pytest tests/test_training_replay.py tests/test_training_anneal.py`); see `tmp/wp306_phase3/post_orchestrator_tests.log` for the latest execution.
- Linting (`.venv/bin/ruff check` on updated modules) passes with no outstanding findings.
