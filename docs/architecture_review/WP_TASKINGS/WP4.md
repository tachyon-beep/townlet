## Prompt: *Implement Work Package 4 — Policy Training Strategies (Townlet)*

**Role:** You are an autonomous coding agent contributing to **Townlet**. Implement **WP4**: refactor the monolithic `PolicyTrainingOrchestrator` into composable strategy objects (BC, PPO, Anneal) that cooperate via typed DTOs and honour optional Torch dependencies. This work builds on WP1 (ports/factories), WP2 (modular world façade), and WP3 (DTO boundary). Keep CLI behaviour equivalent while dramatically improving testability and modularity.

> **Read first (in repo):**
>
> * `docs/architecture_review/ARCHITECTURE_REVIEW_2.md` (§6.4 Policy & tests)
> * `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md`
> * `docs/architecture_review/ADR/ADR-002 - World Modularisation.md`
> * `docs/architecture_review/WP_TASKINGS/WP1.md` / `WP2.md` / `WP3.md`
> * `src/townlet/policy/training_orchestrator.py`, `policy/replay.py`, `policy/rollout.py`
> * Tests in `tests/test_policy_orchestrator.py` and `tests/test_policy_backend_selection.py`

**High-level goal:** Extract a **policy training package** with small, single-responsibility components:

* `PolicyTrainingOrchestrator` becomes a thin façade that selects strategies, provides shared services (trajectory capture, replay dataset helpers), and enforces stub-friendly guards.
* Training logic for **behaviour cloning, PPO, and anneal scheduling** lives in dedicated strategy classes conforming to a common interface.
* All strategies consume DTOs introduced in WP3 (e.g., `ObservationBatchDTO`, `RewardBreakdownDTO`, `TelemetryEventDTO`) to stay consistent with the refactored loop.
* Optional Torch dependencies are isolated so installing without `ml` extras still permits replay/analysis workflows and tests.

---

### Deliverables (Definition of Done)

1. **New Package Layout (`townlet/policy/training/`)**

   Create the following structure (adjust names to actual responsibilities discovered during extraction):

   ```
   townlet/policy/training/
     __init__.py
     orchestrator.py       # thin façade replacing old PolicyTrainingOrchestrator
     contexts.py           # dataclasses for shared config/runtime state
     services.py           # helpers: rollout capture, replay dataset loading, promotion eval
     strategies/
       __init__.py
       base.py             # Strategy protocol / abstract class
       bc.py               # Behaviour cloning strategy
       ppo.py              # PPO strategy (Torch-only)
       anneal.py           # Anneal manager orchestrating BC/PPO cycles
     telemetry.py          # Training telemetry helpers (optional)
   ```

   * Delete or shrink `src/townlet/policy/training_orchestrator.py` to a compatibility shim that re-exports the new façade.
   * Update imports across the codebase (CLI, tests) to use `townlet.policy.training.orchestrator.PolicyTrainingOrchestrator`.

2. **Strategy Interface**

   * Define `TrainingStrategy` protocol/ABC with methods like:

     ```python
     class TrainingStrategy(Protocol):
         name: ClassVar[str]
         requires_torch: ClassVar[bool] = False

         def prepare(self, context: TrainingContext) -> None: ...
         def run(self, context: TrainingContext) -> TrainingResult: ...
     ```

   * `TrainingContext` encapsulates DTO-based dependencies:
     * Simulation config / runtime overrides.
     * Rollout capture service (wraps `SimulationLoop` using DTOs from WP3).
     * Replay dataset accessors.
     * Promotion manager / anneal trackers.
   * `TrainingResult` typed DTO (Pydantic or dataclass) capturing metrics, flags, duration, etc.

3. **Strategy Implementations**

   * **BCStrategy**
     * Loads manifests via service helpers.
     * Wraps `BCTrainer` interactions; raises `TorchNotAvailableError` gracefully when torch missing.
     * Returns typed metrics (`BCTrainingResultDTO`) with accuracy/loss, manifest path, duration.
   * **PPOStrategy**
     * Encapsulates PPO training loops, gradient steps, logging rotation.
     * Depends on Torch; mark `requires_torch = True` and short-circuit with precise error when unavailable.
     * Emits structured stats (`PPOTrainingResultDTO`) instead of ad-hoc dicts.
     * Exposes hooks for anneal manager to evaluate thresholds (queue intensity, loss flags).
   * **AnnealStrategy**
     * Coordinates a schedule of `BCStrategy`/`PPOStrategy` executions using DTO results.
     * Maintains baselines in context, updates promotion metrics, and surfaces final status.
     * CLI entry point `run_anneal` delegates entirely to this strategy.

4. **Orchestrator Façade**

   * New `PolicyTrainingOrchestrator` composes services + strategies:

     ```python
     class PolicyTrainingOrchestrator:
         def __init__(self, config: SimulationConfig, *, services: TrainingServices | None = None) -> None: ...
         def run(self) -> TrainingResult: ...
         def run_bc_training(...), run_ppo(...), run_anneal(...), capture_rollout(...), run_replay_dataset(...)
     ```

   * Methods delegate to strategy instances and return DTOs.
   * Torch gating occurs at strategy boundaries; orchestrator remains importable without Torch.
   * Provide compatibility helpers that turn DTO results into the legacy dicts used by current CLI scripts (until those scripts are updated).

5. **Shared Services**

   * Introduce `RolloutCaptureService` wrapping `SimulationLoop` from WP1/2/3 — ensures DTO-based interaction.
   * `ReplayDatasetService` handles manifest resolution, dataset building, sample summaries (currently `_resolve_replay_manifest`, `_summarise_batch`, etc.).
   * `PromotionServiceAdapter` encapsulates promotion evaluation logic.
   * Ensure services are pure-Python, torch-free; strategies inject dependencies at runtime.

6. **DTO Alignment (WP3 dependency)**

   * Define DTOs under `townlet/dto/policy.py` (or extend WP3 modules) for:
     * `BCTrainingResult`, `PPOTrainingResult`, `AnnealStageResult`, `AnnealSummary`.
     * `RolloutFrameDTO` (if not already defined) for capture buffers.
   * Replace dict returns in strategies/orchestrator/tests with these DTOs; provide `.model_dump()` for legacy JSON output.
   * Ensure `TrajectoryService` exposure (`transitions`, `trajectory`) uses DTO aliases where applicable.

7. **Torch Optionality & Environment Guards**

   * Centralise `torch_available()` checks in strategy registration; orchestrator should list available strategies at runtime.
   * Provide stub strategy shims when Torch missing (`PPOStrategy` raises immediately with actionable message).
   * Update tests to assert `pytest.importorskip("torch")` gating around Torch-only behaviours.

8. **CLI / Script Updates**

   * Update `scripts/run_training.py` and any other entry points to consume DTO `TrainingResult` objects (format/print via helper).
   * Ensure CLI flags (`--mode anneal`, etc.) map cleanly to strategy names.
   * Reflect new return shapes (DTOs) in CLI output; maintain backwards-compatible JSON logs using `.model_dump()`.

9. **Tests**

   * Unit coverage:
     * `tests/policy/strategies/test_bc_strategy.py`
     * `tests/policy/strategies/test_anneal_strategy.py`
     * `tests/policy/strategies/test_ppo_strategy.py` (mark `@pytest.mark.slow` and skip when Torch unavailable).
     * `tests/policy/training/test_services.py` for manifest resolution, rollout capture warnings.
   * Update existing tests to import new orchestrator path and expect DTOs:
     * Ensure stub warning test still verifies the log message & empty result.
   * Add integration smoke: run anneal schedule with stubbed strategies (inject fake strategy implementations) to confirm orchestrator wiring.

10. **Docs & ADR**

* Author `docs/architecture_review/ADR/ADR-004 - Policy Training Strategies.md` describing:
  * Strategy interface, context objects, optional-dependency policy.
  * DTO alignment with WP3.
  * Promotion manager integration.
* Update developer docs / architecture review tables referencing policy trainer refactor.

11. **Sanity Checklist**

- Old `PolicyTrainingOrchestrator` module reduced to shim or deleted; all behaviour lives in `townlet/policy/training/`.
- Strategies <200 LOC each; orchestrator <150 LOC.
- Importing training modules without Torch succeeds for replay-only workflows.
- CLI + tests use DTO results; no dict-shaped payloads leak across module seams.
- `pytest -q`, `ruff check`, `mypy` (with `townlet/policy/training` in “strict” mode if feasible) pass.
- ADR-004 merged; dependency docs updated.

---

### Method & Cut Plan (Do This In Order)

1. **Round up Responsibilities**
   * Annotate the existing orchestrator methods by concern (BC, PPO, anneal, replay, rollout, promotion).
   * Capture sample outputs/metrics (using fixtures) to inform DTO schemas.

2. **Draft ADR-004 + DTO Models**
   * Outline strategy interface, DTO fields, optional dependency policy.
   * Land DTO definitions in `townlet/dto/policy.py` alongside WP3 work.

3. **Introduce Training Package Skeleton**
   * Create `townlet/policy/training/` modules with empty strategies + context classes.
   * Wire import paths and compatibility shim.

4. **Extract Shared Services**
   * Move `_resolve_replay_manifest`, `_summarise_batch`, rollout capture logic into `services.py`.
   * Ensure services consume DTOs from WP3 (observations, telemetry) where applicable.

5. **Port BC Strategy**
   * Move behaviour-cloning logic into `strategies/bc.py`.
   * Return `BCTrainingResultDTO`; adjust tests.

6. **Port PPO Strategy**
   * Extract PPO loop (including logging, advantage health) into `strategies/ppo.py`.
   * Keep Torch-dependent imports local.
   * Provide deterministic seed injection via context for tests.

7. **Port Anneal Strategy**
   * Implement schedule execution orchestrating BC/PPO results with tolerance checks.
   * Update promotion manager interactions via service.

8. **Refactor Orchestrator Façade**
   * New orchestrator composes strategies/services; API parity with old methods.
   * Provide simple dependency injection for tests (e.g., pass fake strategies).

9. **Update CLI + Snapshots**
   * Adjust `scripts/run_training.py`, any notebooks or docs referencing old structure.
   * Ensure snapshot manager (if it touches training) reacts appropriately.

10. **Testing & Validation**
    * Run unit tests for services/strategies/orchestrator.
    * Run integration smoke (with Torch available if possible).
    * Verify stub environment paths (Torch absent) raise clear `TorchNotAvailableError`.

11. **Docs & Polish**
    * Finalise ADR-004, update README/architecture notes, cross-link WP1–WP4.
    * Ensure WP1–WP3 docs mention dependency on DTOs/policy strategies where relevant.

---

**Ready to implement once WP1–WP3 are in review or merged.**
