# Townlet Architecture Migration Work Packages

## Overview
This roadmap decomposes the transition from the current Townlet implementation to the target modular architecture into bounded work packages. Each package defines its objective, primary activities, dependencies, expected duration, and success criteria. The sequence assumes iterative delivery, allowing earlier milestones to unblock later refactors while keeping the simulation usable.

## Work Package 0: Enable Reliable Tooling Baseline
- **Objective**: Restore a dependable developer experience so subsequent refactors can run linting, typing, and targeted tests without heavy optional dependencies.
- **Key Activities**:
  - Introduce optional dependency extras for ML (`[ml]`) and API tooling (`[api]`); guard PyTorch and HTTP imports.
  - Document minimal install paths and add CI jobs for ruff, mypy, interrogate, and smoke pytest targets.
  - Establish skip markers for scenarios requiring unavailable backends.
- **Dependencies**: None (kick-off package).
- **Estimated Duration**: 3–5 engineering days.
- **Exit Criteria**: CI reliably executes agreed tooling gates with green status when optional stacks are absent.

## Work Package 1: Define Core Interfaces and Factories
- **Objective**: Introduce abstraction boundaries so the simulation loop depends on protocols rather than concrete world, policy, and telemetry implementations.
- **Key Activities**:
  - Draft `WorldRuntime`, `PolicyBackend`, and `TelemetryService` protocols describing required interactions.
  - Implement factory functions or registries resolving concrete implementations from configuration.
  - Update simulation loop wiring and smoke tests to consume the new interfaces.
- **Dependencies**: Completion of Work Package 0 to ensure tests and linting function.
- **Estimated Duration**: 1 week.
- **Exit Criteria**: Simulation loop imports only protocol types; integration tests use factories to swap stubbed implementations.

## Work Package 2: Modularize World Subsystem
- **Objective**: Decompose `world/grid.py` into cohesive subpackages aligned with domain concepts while preserving behavior.
- **Key Activities**:
  - Identify logical clusters (agents, affordances, console, employment, relationships, hooks) and move code into dedicated modules.
  - Establish a `WorldContext` façade exposing stable methods consumed by policy, telemetry, and scheduler layers.
  - Add unit tests around migrated modules plus regression tests for representative ticks.
- **Current Status (2025-04-12)**:
  - `world/agents/` now houses the agent registry, employment façade, and relationship service protocols; `WorldState` delegates lifecycle hooks through these services.
  - Affordance runtime/service split into `world/affordances/` with an injected `AffordanceEnvironment`, removing direct `WorldState` coupling.
  - Console/queue suites and new service-focused unit tests (`tests/test_agents_services.py`) guard the refactored boundaries.
- **2025-10-24 Update**:
  - Nightly resets moved into `townlet.world.agents.nightly_reset.NightlyResetService`; `WorldContext.apply_nightly_reset()` provides a façade entry point and tests assert delegation (`tests/test_world_nightly_reset.py`).
  - Employment helpers now route through the expanded `townlet.world.agents.employment.EmploymentService`, and the runtime adapter uses the façade for context lookups (`tests/test_world_employment_delegation.py`).
  - Economy and utility upkeep extracted to `townlet.world.economy.EconomyService`; `WorldState` and `PerturbationService` delegate price spikes and outages through the façade (`tests/test_world_economy_delegation.py`).
  - Perturbation scheduling now relies on `townlet.world.perturbations.PerturbationService`, removing remaining price/outage logic from `world/grid.py` (`tests/test_world_perturbation_service.py`).
  - Phase 5 Step 4 validation captured telemetry and observation baselines post-extraction (telemetry identical for the first five ticks; longer run deltas are limited to additional zeroed ticks). `world/grid.py` now sits at 1 799 LOC (down ~180 from Phase 4), with lifecycle/spawn helpers earmarked as the next extraction slice.
- **Dependencies**: Work Package 1 interfaces to ensure consumers rely on abstractions, reducing coupling risk.
- **Estimated Duration**: 2–3 weeks with staged merges.
- **Exit Criteria**: `world/grid.py` shrinks to orchestration glue (<500 LOC) and all imports reference new submodules.

## Work Package 3: Refactor Telemetry Pipeline
- **Objective**: Separate telemetry concerns into composable services and ensure clean startup/shutdown semantics.
- **Key Activities**:
  - Extract transport worker, metric aggregation, and console authentication into distinct modules implementing `TelemetryService`.
  - Introduce lifecycle management (context managers or async tasks) for background workers.
  - Provide adapters for stdout/file sinks plus placeholders for future observability targets.
- **Dependencies**: Work Package 1 (interfaces) and Work Package 2 (world façade) to prevent tight coupling on internal structures.
- **Estimated Duration**: 2 weeks.
- **Exit Criteria**: Telemetry module coverage increases with isolated unit tests, and simulation loop interacts with a single service entry point.

## Work Package 4: Abstract Policy Backends
- **Objective**: Support multiple policy execution strategies through a unified backend interface that gracefully degrades when ML dependencies are missing.
- **Key Activities**:
  - Implement scripted baseline and PyTorch backends fulfilling `PolicyBackend` protocol.
  - Move training-specific utilities (replay buffers, annealing logic) into backend-specific modules.
  - Update configuration schemas to select backend implementations and add validation.
- **Dependencies**: Work Package 1 (protocol), Work Package 0 (optional dependency management).
- **Estimated Duration**: 1–2 weeks.
- **Exit Criteria**: Policies can be swapped via configuration; pytest skips ML tests when `[ml]` extras are absent without failing collection.

## Work Package 5: Decompose Configuration Loader
- **Objective**: Align configuration schemas with subsystem boundaries for maintainability and clearer dependency flow.
- **Key Activities**:
  - Split the monolithic loader into modules per domain (rewards, telemetry, snapshots, perturbations).
  - Centralize I/O responsibilities in a light `loader.py` orchestrating Pydantic models.
  - Enhance schema documentation via `Field` descriptions and generated reference docs.
- **Dependencies**: Work Packages 2–4 to ensure configuration modules map cleanly to refactored subsystems.
- **Estimated Duration**: 1 week.
- **Exit Criteria**: Config package imports are acyclic; documentation reflects new module structure and docstring coverage surpasses 60%.

## Work Package 6: Quality and Observability Ratchet
- **Objective**: Solidify the refactored architecture with continuous quality improvements and expanded telemetry options.
- **Key Activities**:
  - Incrementally eliminate remaining ruff and mypy suppressions introduced during earlier packages.
  - Extend telemetry adapters (e.g., Prometheus, WebSocket) using the modular service design.
  - Publish updated developer guides covering new architecture, interfaces, and testing patterns.
- **Dependencies**: Completion of Work Packages 0–5.
- **Estimated Duration**: Ongoing (plan for 1 quarter with incremental milestones).
- **Exit Criteria**: Codebase meets agreed lint/type/doc thresholds, and at least one additional telemetry backend operates in production-like tests.
