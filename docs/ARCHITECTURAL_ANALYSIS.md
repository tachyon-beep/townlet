# Architectural Analysis: Townlet

## Executive Summary

**Current State**: Townlet is a simulation-first modular monolith centred on a tick-driven core loop that orchestrates world state, policy runtime, telemetry, and stability services. The conceptual architecture is well documented, but the Python implementation is still highly scaffolded, with many subsystems only partially realised and concentrated in a few oversized modules. 【F:README.md†L1-L35】【F:docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md†L5-L68】【F:src/townlet/core/sim_loop.py†L1-L303】

**Key Findings**:
1. Critical packages such as `world`, `telemetry`, and `policy` house extremely large classes and functions (e.g., `WorldState` at ~2.7k LOC and `TrainingHarness.run_ppo` with cyclomatic complexity 75), leading to poor cohesion and high coupling. 【753790†L57-L76】【ce1de6†L5-L10】【F:src/townlet/world/grid.py†L200-L400】【F:src/townlet/policy/runner.py†L881-L1038】
2. Static analysis reveals pervasive typing and lint issues (hundreds of mypy and Ruff violations) and minimal docstring coverage (18%), indicating weak type safety and maintainability controls. 【df034d†L1-L400】【e4e9ca†L1-L120】【78b940†L1-L1】
3. Test collection fails due to missing heavyweight dependencies (PyTorch) and inadequate dependency isolation, preventing even baseline regression coverage. 【bfa4be†L1-L158】

**Priority Recommendations**:
1. Decompose `WorldState`, `TelemetryPublisher`, and `TrainingHarness` into smaller, domain-driven components with explicit interfaces to align implementation with the documented architecture.
2. Introduce stratified module boundaries and dependency inversion (e.g., repository/service layers, transport adapters) to reduce coupling and allow isolated testing.
3. Establish automated quality gates (pre-commit hooks, CI) that run mypy, Ruff, pytest (with dependency stubs), and security scanners to prevent regression of current debt.

**Overall Assessment**: **D+** — Rich architecture vision with detailed docs, but the Python codebase remains a monolithic scaffold exhibiting high complexity, weak typing discipline, and failing tests. Significant refactoring and tooling are required before production readiness.

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architectural Analysis](#2-architectural-analysis)
3. [Quality Assessment](#3-quality-assessment)
4. [Issue Summary](#4-issue-summary)
5. [Recommendations](#5-recommendations)
6. [Prioritised Roadmap](#6-prioritised-roadmap)
7. [Appendices](#7-appendices)

---

## 1. Project Overview

### 1.1 Repository Structure
The repository follows a `src` layout with clear domain-based packages (`agents`, `world`, `policy`, etc.), configuration YAMLs under `configs/`, CLI scripts in `scripts/`, and extensive planning documents under `docs/`. 【F:README.md†L11-L35】

### 1.2 Module Organization
- **Core Loop** (`src/townlet/core/sim_loop.py`): Entry point orchestrating tick progression, delegating to lifecycle, policy, telemetry, stability, and snapshots. 【F:src/townlet/core/sim_loop.py†L50-L303】
- **World** (`src/townlet/world/`): Contains grid state, affordances, queues, employment, and rivalry management. The `WorldState` dataclass owns most mutation paths. 【F:src/townlet/world/grid.py†L200-L400】【F:src/townlet/world/affordances.py†L1-L200】
- **Config** (`src/townlet/config/loader.py`): Pydantic schema describing every feature flag, reward knob, telemetry transport, and snapshot policy. 【F:src/townlet/config/loader.py†L1-L200】【F:src/townlet/config/loader.py†L352-L460】
- **Policy** (`src/townlet/policy/`): Behaviour controllers, PPO training harness, replay/bc utilities; requires PyTorch to function. 【F:src/townlet/policy/runner.py†L592-L879】【F:src/townlet/policy/models.py†L1-L83】
- **Telemetry** (`src/townlet/telemetry/`): Publishes world snapshots and manages transports, console auth, narration throttling. 【F:src/townlet/telemetry/publisher.py†L1-L200】【F:src/townlet/telemetry/transport.py†L1-L118】
- **Tests** (`tests/`): Scenario-focused pytest suites mirroring the package; currently blocked during import by missing PyTorch. 【F:tests/test_sim_loop_structure.py†L1-L23】【bfa4be†L1-L158】

### 1.3 Technology Stack
- Python 3.11+, Pydantic v2 for schema validation, FastAPI & Uvicorn for web surfaces, PettingZoo for RL envs, PyTorch (optional but assumed) for PPO/BC, Prometheus for telemetry. 【F:pyproject.toml†L1-L48】【F:src/townlet/policy/models.py†L1-L83】

### 1.4 Code Statistics
- Total LOC (src/townlet): 20,259 LOC / 17,465 SLOC / 2,286 blanks. 【753790†L57-L76】
- Largest files: `world/grid.py` (2,694 LOC), `telemetry/publisher.py` (2,451 LOC), `world/affordances.py` (646 LOC).
- Cyclomatic complexity hotspots: `WorldState.apply_actions` (E/32), `ObservationBuilder._map_with_summary` (D/27), `TrainingHarness.run_ppo` (F/75). 【753790†L57-L76】【ce1de6†L5-L10】
- Docstring coverage: 18.4% (target 80%). 【78b940†L1-L1】

---

## 2. Architectural Analysis

### 2.1 Current Architecture
The runtime is a layered monolith with a central `SimulationLoop` coordinating subsystems that mostly live within the same process and share world state objects. Configuration-driven behaviour (affordances, perturbations, telemetry) is modelled via Pydantic schemas, aligning with the documented design blueprint. However, implementation boundaries are blurred: massive classes own both orchestration and business logic, and modules often reach across layers (e.g., policy touching world state directly). 【F:docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md†L5-L68】【F:src/townlet/core/sim_loop.py†L50-L303】【F:src/townlet/world/grid.py†L200-L400】【F:src/townlet/policy/runner.py†L881-L1038】

**Strengths**
- Architecture docs provide a clear target state and data flows for each component. 【F:docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md†L5-L68】
- Configuration schema is comprehensive, capturing guardrails, feature flags, and snapshot identity requirements with validation. 【F:src/townlet/config/loader.py†L1-L200】【F:src/townlet/config/loader.py†L600-L760】
- Core loop correctly sequences interactions (console → scheduler → actions → rewards → telemetry) mirroring the design doc. 【F:src/townlet/core/sim_loop.py†L203-L303】

**Weaknesses**
- Implementation concentrates numerous responsibilities in monolithic classes, violating single responsibility and hindering testability (`WorldState`, `TelemetryPublisher`, `TrainingHarness`). 【F:src/townlet/world/grid.py†L200-L400】【F:src/townlet/telemetry/publisher.py†L41-L200】【F:src/townlet/policy/runner.py†L881-L1038】
- Cross-layer knowledge: policy code manipulates world internals, telemetry reaches into employment/rivalry internals, conflating domain and infrastructure concerns. 【F:src/townlet/policy/runner.py†L1003-L1038】【F:src/townlet/telemetry/publisher.py†L190-L220】
- Lack of dependency boundaries prevents swapping implementations (e.g., no separate data access or transport adapters), limiting alignment with the modular blueprint. 【F:src/townlet/world/grid.py†L200-L400】【F:src/townlet/telemetry/transport.py†L1-L118】

### 2.2 Component Breakdown

#### Component: Simulation Core
- **Purpose**: Drive tick lifecycle, coordinate subsystems. 【F:src/townlet/core/sim_loop.py†L50-L303】
- **Dependencies**: Lifecycle, policy, rewards, telemetry, perturbations, stability, world snapshots.
- **Issues**: Tight coupling to concrete classes (no interfaces), uses global RNG seeds without abstraction, results pipeline intimately tied to telemetry publisher.
- **Size**: 300+ LOC but manageable; main complexity arises from dependencies.

#### Component: World Domain
- **Purpose**: Represent grid state, affordances, employment, relationships. 【F:src/townlet/world/grid.py†L200-L400】【F:src/townlet/world/affordances.py†L1-L200】
- **Dependencies**: Config, employment engine, queue manager, telemetry events. Exposes many mutable structures used by other modules.
- **Issues**: `WorldState` handles console integration, hook loading, RNG, employment bridging, rivalry metrics—resulting in a god object. Affordance runtime remains in-world package with TODO to extract.
- **Size**: `grid.py` 2.7k LOC, `affordances.py` 646 LOC.

#### Component: Policy & Training
- **Purpose**: Behaviour controllers, anneal scheduling, PPO/BC training, action selection. 【F:src/townlet/policy/runner.py†L592-L1038】【F:src/townlet/policy/models.py†L1-L83】
- **Dependencies**: PyTorch, Replay datasets, world state for runtime decisions.
- **Issues**: PyTorch optional guard leads to runtime import failures in tests; `TrainingHarness.run_ppo` extremely complex, mixing dataset validation, logging, training loop, and promotion gating; no separation between online runtime and offline training.
- **Size**: Runner file 1.3k LOC.

#### Component: Telemetry & Console
- **Purpose**: Publish observer payloads, manage console commands, transport buffering. 【F:src/townlet/telemetry/publisher.py†L41-L200】
- **Dependencies**: Console auth, transport, world state introspection.
- **Issues**: `TelemetryPublisher` holds vast mutable state, performs auth, diffing, transport control, metrics summarisation, and manual narration in one class; thread management embedded; heavy reliance on global world internals.
- **Size**: 2.4k LOC.

#### Component: Config & Snapshots
- **Purpose**: Schema for simulation/training/telemetry, snapshot state management. 【F:src/townlet/config/loader.py†L1-L200】【F:src/townlet/config/loader.py†L800-L1000】
- **Dependencies**: Pydantic, YAML, modules referenced by migration handlers.
- **Issues**: Schema definitions instantiate complex defaults inline, making the file dense; runtime features (personality, telemetry) validated here rather than at domain boundaries.

### 2.3 Dependency Graph
- **Direction**: Most modules depend on `config`, while `core` depends on almost every subsystem. `world` components depend on `config` and `telemetry` for instrumentation, while `telemetry` references world and policy structures.
- **Observations**: There is no separation between domain (world, agents), application (loop), and infrastructure (telemetry, persistence). Circular import risk mitigated via delayed imports (e.g., in `TrainingHarness.capture_rollout`), indicating existing cyclic pressure. 【F:src/townlet/policy/runner.py†L640-L703】
- **Coupling**: Tight — direct attribute access to other modules' internals (e.g., telemetry reading employment exit queues, policy hooking into world RNG). 【F:src/townlet/core/sim_loop.py†L281-L301】【F:src/townlet/policy/runner.py†L977-L1038】

### 2.4 Patterns & Anti-patterns
- **Patterns**: Configuration via Pydantic models; strategy-like behaviour selection within policy (scripted vs RL). 【F:src/townlet/config/loader.py†L1-L200】【F:src/townlet/policy/runner.py†L640-L739】
- **Anti-patterns**: God objects (`WorldState`, `TelemetryPublisher`); long methods (e.g., `run_ppo`); duplication of queue/employment logic between world and telemetry; optional dependency pitfalls causing runtime failures; limited interface segregation (Protocols used sparingly). 【F:src/townlet/world/grid.py†L200-L400】【F:src/townlet/telemetry/publisher.py†L41-L200】【F:src/townlet/policy/runner.py†L881-L1038】【bfa4be†L1-L158】

---

## 3. Quality Assessment

### 3.1 Code Quality
- **Type Checking**: `mypy` reports extensive errors across packages (missing stubs, incorrect typing, unreachable code), highlighting incomplete type hints and misuse of TypedDicts. 【df034d†L1-L400】
- **Linting**: `ruff` flags 234 issues (import ordering, unused imports, formatting, typing modernisation), reflecting inconsistent style and outdated typing constructs. 【e4e9ca†L1-L120】
- **Complexity**: Radon identifies multiple high-complexity methods (grade E/F). Particularly `TrainingHarness.run_ppo` (F/75) and `WorldState.apply_actions` (E/32), both candidates for refactor. 【ce1de6†L5-L10】
- **Documentation**: Docstring coverage 18.4%, below 80% target, limiting onboarding effectiveness. 【78b940†L1-L1】

### 3.2 Test Quality
- **Execution**: `pytest --cov` aborts during collection due to missing `torch`, meaning effective test coverage is 0% in current environment. 【bfa4be†L1-L158】
- **Test Design**: Existing tests load full simulation configs, indicating integration focus but also heavy dependency on optional ML stack; lack of dependency injection prevents isolation.

### 3.3 Security
- **Static Scan**: Bandit reports 19 issues (mostly low-severity RNG assertions and `pickle` usage for RNG state); one medium severity for pickle deserialisation in RNG utilities. 【66d768†L1-L125】
- **Dependencies**: `pip-audit` flags vulnerabilities in `pip` and `py` packages; remediate via upgrades. 【234a52†L1-L7】
- **Observations**: Telemetry transport lacks robust TLS validation in plaintext mode and uses asserts for socket state. 【F:src/townlet/telemetry/transport.py†L68-L145】【66d768†L1-L125】

### 3.4 Performance
- Heavy reliance on Python dictionaries and large loops in `run_ppo` and `WorldState` methods without profiling instrumentation; nightly resets iterate entire agent set each tick without batching; Telemetry flush thread handles large payloads synchronously. 【F:src/townlet/core/sim_loop.py†L203-L303】【F:src/townlet/policy/runner.py†L1003-L1038】【F:src/townlet/telemetry/publisher.py†L41-L200】

### 3.5 Maintainability
- Oversized modules hamper comprehension; optional dependencies cause brittle imports; TODOs indicate pending extraction (`Affordance runtime scaffolding pending extraction`). 【F:src/townlet/world/affordances.py†L1-L40】
- Inconsistent typing (legacy `typing.List`, `Optional`) flagged by Ruff; cross-module access patterns reduce modularity.

---

## 4. Issue Summary

### 4.1 Critical Issues (P0)
- **Test suite fails to import due to missing PyTorch** — blocks regression testing. 【bfa4be†L1-L158】
- **Medium severity security risk** via `pickle.loads` for RNG state deserialisation without trust boundary. 【66d768†L1-L125】

### 4.2 Major Issues (P1)
- **Monolithic world and telemetry classes** leading to high complexity and coupling. 【F:src/townlet/world/grid.py†L200-L400】【F:src/townlet/telemetry/publisher.py†L41-L200】
- **Training harness complexity** with F-grade cyclomatic complexity and direct PyTorch dependency. 【ce1de6†L5-L10】【F:src/townlet/policy/runner.py†L881-L1038】
- **Extensive mypy/ruff violations** undermining reliability. 【df034d†L1-L400】【e4e9ca†L1-L120】
- **Lack of modular boundaries** prevents mocking/injection for tests and alternative implementations. 【F:src/townlet/core/sim_loop.py†L50-L303】

### 4.3 Minor Issues (P2)
- **Optional TLS enforcement** in telemetry transport reliant on asserts and manual configuration. 【F:src/townlet/telemetry/transport.py†L68-L145】
- **Docstring coverage gaps** reducing knowledge transfer. 【78b940†L1-L1】
- **Legacy typing constructs** (`typing.List`, `Optional`) flagged by Ruff, causing technical debt. 【e4e9ca†L1-L120】

### 4.4 Opportunities (P3)
- **Adopt data-oriented subpackages** (e.g., separate `economy`, `narration`, `queueing` modules) to reflect architecture doc.
- **Introduce plugin interfaces** for policy backends to support alternative ML frameworks.
- **Enhance observability** with structured logs and metrics derived from telemetry state.

---

## 5. Recommendations

### 5.1 Strategic Recommendations

#### Target Architecture
Adopt a layered architecture aligned with the documented modules:
1. **Domain Layer**: `world`, `agents`, `affordances`, `economy` with pure domain logic and state transitions.
2. **Application Layer**: `core` orchestrator, `lifecycle`, `scheduler`, `policy` interfaces operating on domain interfaces.
3. **Infrastructure Layer**: `telemetry`, `console`, `snapshots`, `config`, `web`, each behind adapters (e.g., `TelemetryGateway`, `SnapshotRepository`).
4. **Interface Contracts**: Define protocols/dataclasses for cross-layer communication (e.g., `IWorld`, `TelemetrySink`, `PolicyDecisionEngine`).

#### Migration Path
- **Phase 1**: Extract interfaces and façade classes from existing monoliths without changing behaviour (introduce wrappers around `WorldState`, `TelemetryPublisher`).
- **Phase 2**: Gradually move domain-specific logic (employment, rivalry, console bridging) into dedicated modules; refactor `TrainingHarness` into separate dataset loader, trainer, and evaluation components.
- **Phase 3**: Implement dependency injection (via constructors or simple registries) so `SimulationLoop` depends on abstractions. Add test doubles for each interface.
- **Phase 4**: Harden infrastructure (transport retries, snapshot storage) and align with docs (e.g., dedicated telemetry service).

#### Design Principles
- Enforce **SOLID** (especially SRP and DIP) by giving each subsystem a narrow API.
- Use **dependency injection** to supply optional components (e.g., ML backends, telemetry sinks).
- Move toward a **Clean Architecture** style, ensuring domain code has zero dependency on infrastructure packages.

### 5.2 Tactical Recommendations

#### Recommendation: Split World Domain Responsibilities
**What**: Partition `WorldState` into focused services (`AgentRegistry`, `AffordanceManager`, `EmploymentService`, `RivalryService`).

**Why**:
- Current `WorldState` handles state, console hooks, RNG, employment bridging, rivalry updates, and telemetry interactions in one dataclass, making reasoning and testing difficult. 【F:src/townlet/world/grid.py†L200-L400】

**How**:
1. Introduce lightweight interfaces for key concerns (e.g., `IAffordanceRuntime`, `IEmploymentGateway`).
2. Extract employment-related attributes/methods into a new `townlet.world.employment_service` module that `WorldState` composes.
3. Move console bridge and hook loading logic into infrastructure layer (now provided by `ConsoleService` wrapping the legacy bridge) and inject into world.
4. Provide serialization helpers independent from world to support snapshots/telemetry.

**Effort**: Large (2-3 weeks).

**Risk**: Medium — affects many modules but can be phased by migrating one concern at a time.

**Dependencies**: Requires defined interfaces and tests to assert behaviour.

**Impact**: Improved maintainability, testability, and alignment with architecture doc.

#### Recommendation: Modularise Telemetry Pipeline
**What**: Break `TelemetryPublisher` into composable pipelines (event collector, diff generator, transport worker).

**Why**:
- Single class handles auth, buffer management, narration throttling, metrics; extremely stateful and tightly coupled. 【F:src/townlet/telemetry/publisher.py†L41-L200】

**How**:
1. Create `TelemetryBufferWorker` responsible solely for batching/flushing to transports.
2. Extract data collection into domain-specific reporters (e.g., `QueueMetricsReporter`, `RivalryReporter`) that consume world snapshots via interfaces.
3. Define `TelemetryCommandService` to manage console interactions separately from streaming.
4. Add asynchronous hooks or message queue abstractions to decouple flush thread from simulation thread.

**Effort**: Large (2 weeks).

**Risk**: Medium — touches console integration and tests.

**Impact**: Lower complexity, easier to mock/test, improved resilience.

#### Recommendation: Introduce Policy Backend Abstraction
**What**: Separate policy runtime/training concerns into interface-based backends with optional PyTorch implementation.

**Why**:
- Tests fail when PyTorch missing; training logic is tightly coupled to torch-specific constructs; monolithic `run_ppo` is hard to maintain. 【bfa4be†L1-L158】【F:src/townlet/policy/runner.py†L881-L1038】

**How**:
1. Define `PolicyBackend` protocol exposing `decide`, `train_epoch`, `load_state`.
2. Move torch imports and training utilities into `townlet.policy.backends.torch` so base package remains importable without torch.
3. Split `TrainingHarness` into orchestrator plus backend-specific trainers; isolate dataset validation and logging.
4. Provide stub/mock backend for tests that ensures deterministic behaviour.

**Effort**: Medium (1-2 weeks).

**Risk**: Medium — requires refactoring training CLI and tests.

**Impact**: Restores testability without torch, simplifies adding alternative backends.

#### Recommendation: Establish Quality Gates
**What**: Configure pre-commit/CI to run `mypy`, `ruff`, `pytest -m "not slow"`, `bandit`, `pip-audit`.

**Why**: Current tooling reveals hundreds of violations and vulnerabilities; lacking automation allows regressions. 【df034d†L1-L400】【e4e9ca†L1-L120】【66d768†L1-L125】【234a52†L1-L7】

**How**:
1. Add `.pre-commit-config.yaml` with hooks for formatting, linting, type checking.
2. Update CI to install optional dependencies (torch stub or CPU wheel) or use dependency injection for tests.
3. Track metrics (lint error count, docstring coverage) to enforce thresholds.

**Effort**: Small (2-3 days).

**Risk**: Low.

**Impact**: Immediate improvement in code hygiene and reliability.

#### Recommendation: Harden RNG and Snapshot Security
**What**: Replace `pickle`-based RNG serialization with safe formats and remove asserts for security-critical paths.

**Why**: Bandit flags medium severity for pickle usage; asserts bypass runtime checks in production. 【66d768†L1-L125】【F:src/townlet/utils/rng.py†L1-L40】【F:src/townlet/telemetry/transport.py†L68-L145】

**How**:
1. Encode RNG state as JSON-safe primitives or use `random.getstate()` with base64 plus integrity checks.
2. Replace asserts in telemetry transport with explicit error handling raising `TelemetryTransportError`.
3. Document trust boundaries and add tests covering malicious inputs.

**Effort**: Small (2-3 days).

**Risk**: Low.

**Impact**: Improved security posture and error resilience.

#### Recommendation: Improve Documentation & Observability
**What**: Increase docstring coverage, add architecture guide mirroring docs, and provide instrumentation hooks.

**Why**: Low docstring coverage and reliance on TODOs reduce maintainability; instrumentation lacking for performance evaluation. 【78b940†L1-L1】【F:src/townlet/world/affordances.py†L1-L40】

**How**:
1. Adopt docstring templates for each module, focusing on purpose and invariants.
2. Produce architecture diagrams showing planned vs actual modules.
3. Add optional logging/tracing wrappers around critical paths (e.g., queue manager) for profiling.

**Effort**: Medium (1 week).

**Risk**: Low.

**Impact**: Better onboarding, easier troubleshooting.

### 5.3 Quick Wins
- Add PyTorch extra (CPU-only) to dev requirements or use stub module during tests to restore pytest pass. 【bfa4be†L1-L158】
- Run `ruff --fix` to resolve import ordering and typing modernisation issues quickly. 【e4e9ca†L1-L120】
- Upgrade vulnerable dependencies (`pip`, `py`) and pin via `requirements-dev.txt`. 【234a52†L1-L7】
- Replace `assert` statements in runtime code with explicit exceptions/logs (e.g., telemetry transport). 【F:src/townlet/telemetry/transport.py†L96-L145】【66d768†L1-L125】
- Introduce docstrings for key entry points (`SimulationLoop.step`, `TrainingHarness.run_ppo`) to raise coverage. 【F:src/townlet/core/sim_loop.py†L203-L303】【F:src/townlet/policy/runner.py†L881-L1038】

---

## 6. Prioritised Roadmap

### Phase 0: Immediate (This Week)
- [ ] Provide PyTorch stub or optional dependency gate so pytest imports succeed. 【bfa4be†L1-L158】
- [ ] Patch `pickle` usage and asserts flagged by Bandit. 【66d768†L1-L125】
- [ ] Upgrade vulnerable dependencies (`pip`, `py`). 【234a52†L1-L7】

### Phase 1: Short-term (Next Month)
- [ ] Extract policy backend interface and modularise training harness. 【F:src/townlet/policy/runner.py†L881-L1038】
- [ ] Introduce telemetry pipeline refactor (buffer worker + reporters). 【F:src/townlet/telemetry/publisher.py†L41-L200】
- [ ] Enforce CI gates for linting/type checking/testing. 【df034d†L1-L400】【e4e9ca†L1-L120】

### Phase 2: Medium-term (Next Quarter)
- [ ] Refactor `WorldState` into domain services and reduce cross-layer coupling. 【F:src/townlet/world/grid.py†L200-L400】
- [ ] Align application layer with clean architecture boundaries, introducing interfaces for lifecycle, scheduler, telemetry.
- [ ] Expand documentation and observability instrumentation.

### Phase 3: Long-term (Next Year)
- [ ] Evaluate splitting runtime and training into separate deployable services (simulation vs training shards) per design doc. 【F:docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md†L69-L75】
- [ ] Consider microservice or FFI integration for performance-critical paths (pathfinding, queue simulation).

---

## 7. Appendices

### Appendix A: Detailed Metrics
- **Radon RAW**: LOC totals and file stats. 【753790†L57-L76】
- **Radon CC**: Complexity grades (see `radon_cc.txt`). 【ce1de6†L1-L10】
- **Mypy Report**: Selected errors across modules. 【df034d†L1-L400】
- **Ruff Report**: 234 lint violations. 【e4e9ca†L1-L120】
- **Interrogate**: Docstring coverage 18.4%. 【78b940†L1-L1】
- **Bandit**: 19 findings (medium severity pickle). 【66d768†L1-L125】
- **Pytest**: 43 import errors due to missing torch. 【bfa4be†L1-L158】
- **pip-audit**: 2 vulnerabilities (pip, py). 【234a52†L1-L7】

### Appendix B: Dependency List
Key runtime dependencies from `pyproject.toml` (numpy, pydantic, pettingzoo, fastapi, uvicorn, prometheus-client). 【F:pyproject.toml†L12-L24】

### Appendix C: Configuration Recommendations
- Leverage `pyproject.toml` for tool config; add `tool.ruff.format`, `tool.pytest.ini_options` updates, and new `[tool.coverage]` when coverage restored. 【F:pyproject.toml†L30-L48】

### Appendix D: Glossary
- **Affordance**: Configured interactive action available in the world.
- **Anneal**: Training schedule mixing behaviour cloning and PPO stages.
- **Telemetry**: Streaming observer data for UI/console consumers.
- **Promotion**: Stability evaluation gating policy release.
