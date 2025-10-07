# Architectural Analysis: Townlet

## Executive Summary

**Current State**: Townlet implements an ambitious small-town life simulation with a comprehensive simulation loop that coordinates world state, policy orchestration, rewards, telemetry, and stability subsystems, closely following the published high-level design.

**Key Findings**:
1. Several core modules are monolithic (e.g., `world/grid.py` at 2,535 LOC, `policy/runner.py` at 1,493 LOC, `telemetry/publisher.py` at 2,190 LOC), creating tightly coupled god objects that span multiple concerns and hinder evolution.
2. Quality gates are far from green: Ruff reports 180 lint violations, mypy flags 474 typing errors, and docstring coverage is only 29.9%, indicating significant maintainability debt.
3. The default environment cannot execute the test suite because optional dependencies such as `torch` and `httpx` are not managed, causing 50 collection errors during pytest.

**Priority Recommendations**:
1. Modularize the world, policy, and telemetry layers into smaller bounded contexts to align code structure with the documented architecture and reduce coupling.
2. Introduce explicit optional dependency management and adapter interfaces so simulators and tests degrade gracefully when heavy ML stacks (e.g., PyTorch) or web tooling are absent.
3. Establish enforceable tooling gates (ruff, mypy, interrogate, pytest subsets) within CI to drive remediation of the 180+ lint, 470+ type, and doc coverage gaps incrementally.

**Overall Assessment**: **C** — The architecture is thoughtfully envisioned and partially realized, but the current implementation suffers from large monolithic modules, fragile dependency management, and failing quality checks that collectively threaten maintainability and velocity.

## Table of Contents

1. Project Overview  
2. Architectural Analysis  
3. Quality Assessment  
4. Issue Summary  
5. Recommendations  
6. Prioritized Roadmap  
7. Appendices  
8. Checks Run

---

## 1. Project Overview

### 1.1 Repository Structure
The repository follows the documented structure, with runtime code under `src/townlet/`, configuration examples under `configs/`, scripts for simulation/training entry points, extensive documentation in `docs/`, and mirrored pytest suites in `tests/`. A separate `townlet_web` directory hosts the React-based operator UI.

### 1.2 Module Organization
Key Python packages include agents, config, core, lifecycle, observations, policy, rewards, scheduler, stability, telemetry, and world, reflecting the layered design described in the high-level architecture snapshot.

### 1.3 Technology Stack
- Python 3.11+ with Pydantic, NumPy, PettingZoo, Typer, FastAPI, and Rich for runtime features; pytest, mypy, and ruff are the primary dev tools.
- Front-end uses React 18 with Vite, Storybook, Vitest, and Playwright tooling.

### 1.4 Code Statistics
- Total LOC: 20,866 (SLOC: 17,882); average cyclomatic complexity A (4.02).
- Docstring coverage: 29.9% (below 80% threshold).
- Test status: pytest aborts with 50 collection errors due to missing `torch` and `httpx`.

---

## 2. Architectural Analysis

### 2.1 Current Architecture
The `SimulationLoop` orchestrates world construction, lifecycle evaluation, perturbations, observation building, policy execution, rewards, telemetry, stability, and promotion management each tick, mirroring the documented flow. Data passes through `WorldRuntime`, which sequences console input, perturbations, affordances, lifecycle checks, and event emission.

**Strengths**: Clear separation of orchestration vs. subsystem implementation; robust snapshot support; telemetry integration matches operator needs.  
**Weaknesses**: Many subsystems are single mega-modules with implicit shared state, leading to tight coupling and limited replaceability (e.g., policy runner assumes PyTorch availability).

### 2.2 Component Breakdown

#### Component: Core Simulation Loop
- **Purpose**: Bind configuration to runtime components, manage ticks, snapshots, and telemetry emission.
- **Dependencies**: Imports 10+ subsystems directly (world, policy, rewards, scheduler, telemetry, stability, snapshots), creating a dense dependency fan-in.
- **Issues**: Minimal abstraction boundaries; testing requires full stack due to direct instantiation.
- **Size**: ~360 LOC.

#### Component: World Engine (`world/grid.py`)
- **Purpose**: Houses agent state, affordances, console, queue management, employment, rivalry, hooks, telemetry bridges, RNG state, and observation helpers.
- **Dependencies**: Agents, config, console, observations, telemetry, scheduler, employment, preconditions, rivalry; also environment variables for hooks.
- **Issues**: 2,535 LOC single file; violates single responsibility by handling simulation state, I/O (console logging), dynamic module loading, and telemetry coordination. Hard to mock or swap subsystems.
- **Size**: 2,535 LOC (largest module).

#### Component: Policy Runner
- **Purpose**: Bridges scripted behavior, PPO/BC training, annealing, replay datasets, and option commit logic.
- **Dependencies**: Behavior controllers, BC/PPO tooling, NumPy, promotion manager, world snapshot.
- **Issues**: Assumes PyTorch availability via `townlet.policy.ppo.utils` (importing `torch`) and does not guard optional ML backends, breaking tests without GPU dependencies.
- **Size**: 1,493 LOC.

#### Component: Telemetry Publisher
- **Purpose**: Aggregates metrics, enforces console auth, manages transport workers, and publishes observer payloads, including rate-limited narration and diff streaming.
- **Dependencies**: Console auth, transport layer, narration, personality registry, world snapshots.
- **Issues**: 2,190 LOC with manual threading, buffer management, and extensive state; mixing auth, event processing, metrics, and transport logic impedes testing and alternative backends.

#### Component: Configuration Loader
- **Purpose**: Pydantic schema for all config surfaces (features, rewards, perturbations, telemetry, snapshot guardrails, training), with custom validators and normalization logic.
- **Issues**: 1,092 LOC module; numerous cross-imports (agents, snapshots) and runtime operations (module loading) blur boundaries between schema and behavior.

#### Component: Lifecycle & Scheduler
- **Purpose**: Manage agent respawns, employment exits, and bounded random events.
- **Notes**: Relatively focused but depend on full world state APIs.

#### Component: Front-end (`townlet_web`)
- **Purpose**: React operator UI with Storybook and Playwright; currently a separate build system with minimal runtime dependencies (React only).
- **Issues**: Unknown integration state; separate `node_modules` adds maintenance overhead.

### 2.3 Dependency Analysis
- The simulation loop directly instantiates all major subsystems, causing upward dependencies on heavy modules and limiting inversion possibilities.
- World state, telemetry, and policy share rich data structures with little interface segregation, implying tight coupling; e.g., telemetry consumes world’s internal structures directly.
- Optional features rely on environment variables and direct module imports (hook modules), risking runtime surprises.
- No evidence of circular imports detected, but cross-layer references (config -> snapshots, policy -> world) produce a web that is hard to untangle.

### 2.4 Patterns & Anti-patterns
- **Patterns**: Use of dataclasses for immutable value objects (agents, scheduler events); Pydantic models for configuration; provider methods for RNG seeds; CLI entry points follow Typer/argparse patterns.
- **Anti-patterns**: God objects (world, telemetry, policy), duplicate responsibilities (config loader performing runtime registration), and implicit global state (module-level registries for snapshots and personalities). Lack of plugin interfaces or dependency injection increases risk when expanding features.

### 2.5 Data Flow
- **Sources**: YAML configs, console commands, RNG streams, optional replay datasets.
- **Transformations**: World runtime applies actions, resolves affordances, and updates needs before lifecycle and rewards compute outputs.
- **Sinks**: Telemetry transport (stdout/file/TCP), snapshots, training buffers, UI subscribers.
- Data flow matches the design doc but lacks explicit interfaces, leading to deep knowledge of internal structures across layers.

---

## 3. Quality Assessment

### 3.1 Code Quality
- **Static Metrics**: LOC 20,866; average cyclomatic complexity A (4.02).
- **Linting**: Ruff reports 180 errors (89 fixable), including modern syntax suggestions (PEP 604 unions) and other issues.
- **Typing**: Mypy finds 474 errors across 35 files, notably missing stubs for UI modules and numerous incompatible types in dashboards.
- **Documentation**: Docstring coverage at 29.9% vs. 80% target; little inline documentation outside config models.

### 3.2 Test Quality
- The pytest suite fails to collect because `torch` (policy) and `httpx` (FastAPI test clients) are absent, indicating tests assume heavier optional dependencies than the default extras install.
- Tests are numerous and organized (dozens of files), but their usefulness is blocked by dependency issues.

### 3.3 Security
- Bandit reports 18 low and 1 medium severity findings (details not shown in quiet output), requiring review to ensure no true positives.
- `pip-audit` shows no known vulnerabilities for the declared package metadata.

### 3.4 Documentation
- README provides overview and commands, but architectural documentation exists in `docs` while code lacks inline explanations; docstring deficit is notable.

---

## 4. Issue Summary

### 4.1 Critical Issues (P0)
- **Unmanaged Optional Dependencies**: Policy runner imports PyTorch unconditionally, causing runtime/test failure without GPU packages; FastAPI tests require `httpx` not installed by default.

### 4.2 Major Issues (P1)
- **Monolithic Modules**: World, policy, telemetry, and config modules exceed 1k LOC each, combining multiple responsibilities and impeding maintainability.
- **Broken Quality Gates**: Ruff (180 errors), mypy (474 errors), and doc coverage (29.9%) highlight systemic code quality debt.
- **Tight Coupling & Lack of Abstractions**: Simulation loop imports concrete implementations directly, preventing modular substitution or testing in isolation.
- **Telemetry Threading Risk**: Manual thread management without lifecycle hooks or context managers raises stability concerns under heavy load.

### 4.3 Minor Issues (P2)
- **Config Loader Coupling**: Schema module handles runtime registration and YAML loading, mixing I/O and validation concerns.
- **Environment-driven Hook Loading**: Reliance on environment variables for affordance hooks without safety wrappers may cause hard-to-debug runtime behavior.
- **Front-end Isolation**: Separate `node_modules` increases maintenance overhead; integration strategy unclear.

### 4.4 Opportunities (P3)
- **Interface-driven Design**: Introduce explicit interfaces for telemetry transports, policy backends, and world subsystems for easier experimentation.
- **Incremental Observability Enhancements**: Telemetry already tracks numerous metrics; modularizing pipelines would facilitate alternative sinks (e.g., metrics services).
- **Adopt modern Python features**: Many lint warnings suggest migrating to PEP 604 unions and dataclass improvements.

---

## 5. Recommendations

### 5.1 Strategic Recommendations

#### Target Architecture
- **Layered Core**: Keep `SimulationLoop` as orchestrator but have it depend on abstract interfaces (world, policy, telemetry) registered via factories, enabling test stubs and alternative implementations.
- **Decomposed Subsystems**: Split world/telemetry/policy modules into focused packages (e.g., world agents, affordances, console, employment) to align with domain boundaries outlined in the design doc.
- **Optional Dependency Adapters**: Provide shims (e.g., policy backend interface) that gracefully degrade when torch or HTTP clients are absent, allowing CI to run minimal suites.

**Migration Path**:
1. Introduce protocol/ABC interfaces and factories for major subsystems.
2. Extract submodules incrementally, moving code without behavior changes.
3. Update simulation loop and tests to consume interfaces.
4. Address dependency gating and quality gates once modularization reduces blast radius.

### 5.2 Tactical Recommendations

#### Recommendation: Modularize World Engine
**What**: Split `world/grid.py` into subpackages (`agents`, `objects`, `console`, `employment`, `relationships`, `hooks`) with clear APIs.  
**Why**: 2,535 LOC file blends multiple concerns, making changes risky and tests heavy.

**How**:
1. Identify cohesive domains (agent snapshot, affordance runtime, console, relationships).
2. Move dataclasses and helper functions into new modules under `world/`.
3. Provide a `WorldContext` interface exposing only necessary operations to policy/telemetry.
4. Update imports incrementally and ensure tests target new modules.  
**Effort**: Large (2–3 weeks).  
**Risk**: Medium (refactors widely used APIs).  
**Dependencies**: Establish interface tests first (SimulationLoop + telemetry).  
**Impact**: Improved maintainability, clearer test seams, easier onboarding.

#### Recommendation: Introduce Policy Backend Interface & Optional Dependencies
**What**: Abstract policy execution behind an interface and gate PyTorch-dependent code behind optional extras.  
**Why**: Current runner hard-imports `torch`, breaking environments without ML stack and blocking tests.

**How**:
1. Define `PolicyBackend` protocol with methods for action selection and training.
2. Provide a default scripted backend (no torch) and a PyTorch backend behind an extra `[ml]`.
3. Update config loader to map `policy_backend` identifiers to implementations.
4. Adjust tests to skip ML scenarios when backend unavailable.  
**Effort**: Medium (5–7 days).  
**Risk**: Medium (touches core decision loop).  
**Dependencies**: Modularization of policy runner internals helps.  
**Impact**: Restores testability, enables lighter deployments, clarifies dependency graph.

#### Recommendation: Refactor Telemetry Pipeline into Service Layers
**What**: Separate telemetry responsibilities into transport manager, metric aggregators, and console auth handler.  
**Why**: `telemetry/publisher.py` mixes threading, auth, metric aggregation, and event formatting in 2,190 LOC, complicating reliability improvements.

**How**:
1. Extract `TelemetryTransportWorker` class handling threading & buffers.
2. Move metric aggregation into domain-specific services (queues, relationships, employment).
3. Create telemetry API interface consumed by simulation loop.
4. Implement lifecycle hooks for clean shutdown (context managers).  
**Effort**: Large (2 weeks).  
**Risk**: Medium-high (requires careful testing).  
**Dependencies**: World modularization to reduce direct state coupling.  
**Impact**: Better stability, easier alternative transports, improved observability.

#### Recommendation: Decompose Config Loader
**What**: Move each domain’s schema into dedicated modules (e.g., `config/rewards.py`) and keep loader focused on I/O and assembly.  
**Why**: The current 1,092 LOC module mixes validation, runtime registration, and dynamic imports, leading to complex dependencies.

**How**:
1. Create submodules for rewards, telemetry, snapshots, perturbations.
2. Use Pydantic’s `model_config` to reference shared validators.
3. Keep `load_config` in `loader.py` and assemble top-level `SimulationConfig`.  
**Effort**: Medium (1 week).  
**Risk**: Medium (needs thorough regression tests).  
**Dependencies**: Establish baseline tests for config parsing.  
**Impact**: Reduced import churn, clearer responsibilities, easier future schema changes.

#### Recommendation: Enforce Quality Gates in CI
**What**: Integrate `ruff`, `mypy`, `interrogate`, and a dependency-managed pytest subset into CI with baselines.  
**Why**: Current metrics reveal large numbers of lint and type issues plus missing docs; lack of enforcement allows regression.

**How**:
1. Configure CI to run tools on touched modules.
2. Introduce baseline suppression (e.g., using Ruff `--exit-zero` initially) and ratchet down.
3. Add docstring coverage gating with targeted exceptions.
4. Provide developer documentation on running these locally.  
**Effort**: Small-Medium (2–4 days).  
**Risk**: Low (tooling).  
**Dependencies**: None.  
**Impact**: Progressive code quality improvement, fewer regressions.

### 5.3 Quick Wins
- Add extras in `pyproject.toml` (e.g., `[ml]` including `torch`, `[api]` including `httpx`) and guard imports to unblock tests.
- Apply automatic Ruff fixes for syntax updates (`X | Y` unions) to reduce lint backlog quickly.
- Document optional dependencies and how to run partial test suites (README + docs).
- Use Pydantic model docstrings or `Field(description=...)` to boost doc coverage in schema-heavy modules.

---

## 6. Prioritized Roadmap

### Phase 0: Immediate (This Week)
- [ ] Define optional dependency extras and guard ML imports (unblock pytest).  
- [ ] Configure CI to run ruff/mypy/interrogate with non-blocking baselines.

### Phase 1: Short-term (Next Month)
- [ ] Modularize world engine into subpackages and update telemetry/policy to use narrower interfaces.  
- [ ] Extract telemetry transport worker and metric services.  
- [ ] Begin resolving highest-priority ruff/mypy findings per module.

### Phase 2: Medium-term (Next Quarter)
- [ ] Introduce policy backend abstraction and optional PyTorch integration.  
- [ ] Decompose config loader into domain modules.  
- [ ] Achieve docstring coverage ≥60% and reduce lint/type errors by 50%.

### Phase 3: Long-term (Next Year)
- [ ] Complete telemetry refactor and support alternative sinks (e.g., Prometheus).  
- [ ] Explore moving performance-sensitive paths (pathfinding) behind stable interfaces as hinted in design docs.
- [ ] Integrate front-end pipeline with back-end services via modular API boundaries.

---

## 7. Appendices

### Appendix A: Detailed Metrics
- LOC & complexity: `radon raw`, `radon cc` outputs.
- Lint: `ruff check src/townlet` (180 errors).
- Types: `mypy src/townlet` (474 errors).
- Docstrings: `interrogate -c pyproject.toml src/townlet` (29.9%).
- Security: `bandit -r src/townlet` summary.
- Dependencies: `pip-audit -P townlet -V 0.1.0` (clean).

### Appendix B: Dependency List
- Python project dependencies and extras as declared in `pyproject.toml`.
- Front-end dependencies from `townlet_web/package.json`.

### Appendix C: Configuration Recommendations
- Use modular config schema modules for readability and reusability (see Recommendation 4).
- Document optional extras and default config entry points in README.

### Appendix D: Glossary
- **Affordance**: Interactable object behavior defined by YAML manifest.
- **Perturbation**: Bounded random events (price spike, blackout).
- **Promotion Manager**: Evaluates stability metrics for policy promotion.

---

## Checks Run

* ✅ `radon raw src/townlet`
* ✅ `radon cc -s -a src/townlet`
* ⚠️ `ruff check src/townlet` (reported 180 issues)
* ⚠️ `mypy src/townlet` (reported 474 errors)
* ✅ `bandit -r src/townlet -q`
* ✅ `pip-audit -P townlet -V 0.1.0`
* ⚠️ `interrogate -c pyproject.toml src/townlet` (29.9% coverage)
* ⚠️ `pytest -q` (failed: missing torch/httpx)

No code changes were made; analysis only.
