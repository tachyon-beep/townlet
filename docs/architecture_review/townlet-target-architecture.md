# Target Architecture: Townlet Simulation Platform

## 1. Architectural Overview
The target architecture keeps the existing simulation loop as the orchestrator while replacing concrete dependencies with clearly defined interfaces. Each subsystem is implemented behind a factory-resolved boundary, allowing the loop to operate on abstractions rather than concrete implementations. This change enables easier swapping of implementations, targeted testing, and progressive modularization.

```
+---------------------+
|  Simulation Loop    |
|  (Orchestrator)     |
+----------+----------+
           | interfaces
           v
+----------+----------+----------------------+---------------------+
| World API| Policy API| Telemetry API        | Ancillary Services  |
+----------+----------+----------------------+---------------------+
| World    | Policy    | Telemetry            | Rewards, Scheduler, |
| Packages | Backends  | Pipelines            | Stability, etc.     |
+----------+----------+----------------------+---------------------+
```

## 2. Layered Core and Interface Contracts

### 2.1 Simulation Loop Layer
- Maintains responsibility for tick orchestration, lifecycle progression, and coordination of subsystems.
- Interacts exclusively through three primary interfaces:
  - `WorldRuntime` protocol (state queries, action application, snapshots).
  - `PolicyBackend` protocol (action selection, training hooks, optional replay buffers).
  - `TelemetrySink` protocol (metric publication, event streaming, narration callbacks).
- Uses factories (e.g., `WorldFactory`, `PolicyFactory`, `TelemetryFactory`) to resolve concrete implementations at startup based on configuration.

### 2.2 Domain Service Layer
- Each interface is implemented by a cohesive package:
  - `world/` decomposed into subpackages (`agents`, `affordances`, `console`, `employment`, `relationships`, `simulation_state`).
  - `policy/` split into strategy-neutral orchestration and backend plug-ins (`scripted`, `pytorch`, future `rl-lib`).
  - `telemetry/` separated into `aggregation`, `transforms`, and `transports` modules.
- Ancillary services (rewards, scheduler, stability) depend on the `WorldRuntime` interface rather than concrete grid types.

### 2.3 Infrastructure Layer
- Configuration loader provides typed descriptors that map to factory names, not modules.
- Optional services (FastAPI admin, snapshot exporters) register themselves with the relevant factory via entry points or plugin hooks.
- Dependency injection occurs during bootstrapping; runtime code receives fully constructed interfaces.

## 3. Decomposed Subsystems

### 3.1 World Packages
- **Simulation Core**: Maintains spatial grid, agent registry, event queue.
- **Agents & Relationships**: Handles employment, rivalry, and interpersonal mechanics.
- **Affordances & Hooks**: Encapsulates interaction logic and environment-driven extensions.
- **Console & Narration**: Manages operator commands, logging, and optional streaming outputs.
- **Observation Builders**: Generate policy-facing observations behind the `WorldRuntime` interface. A read-only `WorldRuntimeAdapter` (exported from `townlet.world.core`) brokers access to shared services (`agents`, `objects`, `queue_manager`, `relationships`) so downstream consumers avoid binding to the monolithic grid.

### 3.2 Policy Backends
- **Backend Interface**: Defines `initialize()`, `select_actions(observation, world_state)`, `record_outcome()`, and `train()` methods.
- **Scripted Backend**: Default lightweight backend requiring no ML dependencies; ideal for deterministic tests.
- **PyTorch Backend**: Provided via `[ml]` optional extra, constructed only when dependency available.
- **External Integrations**: Additional backends (e.g., HTTP microservices) can be registered without altering the loop.

### 3.3 Telemetry Pipelines
- **Aggregation Services**: Domain-focused collectors produce structured events (employment metrics, queue lengths, stability indicators).
- **Transformation Layer**: Normalizes events, applies redaction, and attaches metadata.
- **Transport Adapters**: Implement protocols for stdout, file, WebSocket, or HTTP streaming. Each adapter lives in its own module and can be toggled via configuration. Telemetry collectors consume the same `WorldRuntimeAdapter` façade as policy/observation code, ensuring queue/relationship metrics rely on a stable contract rather than ad-hoc `WorldState` attributes.
- **Lifecycle Management**: Worker pools and threads are managed via context managers with explicit startup/shutdown hooks exposed through the `TelemetrySink` interface.

## 4. Optional Dependency Adapters
- Introduce dedicated extras in `pyproject.toml` (e.g., `[ml]`, `[api]`, `[ui]`).
- Factories check dependency availability and configuration before instantiating optional components.
- Graceful degradation strategy:
  - If a dependency is missing, the factory returns a stub implementation that logs capability gaps and continues execution.
  - Tests assert stub usage where optional dependencies are intentionally absent.
- Configuration documentation includes dependency flags and fallback behaviors.

## 5. Migration Path
1. **Define Protocols**: Introduce `Protocol`/`ABC` interfaces for world, policy, and telemetry subsystems along with registry-style factories.
2. **Adapter Layer**: Wrap existing concrete classes in adapters that satisfy the new interfaces without changing internal logic.
3. **Incremental Extraction**: Move cohesive sections of monolithic modules into dedicated subpackages while keeping public APIs stable.
4. **Simulation Loop Refactor**: Replace direct imports with factory lookups; update tests to rely on stub implementations.
5. **Dependency Gates**: Implement optional dependency checks and extras; update CI to install minimal dependencies by default with targeted jobs covering full extras.
6. **Quality Gate Ratcheting**: Once boundaries stabilize, enforce lint/type/doc requirements on newly modularized packages, gradually expanding coverage to legacy areas.

## 6. Expected Outcomes
- Reduced coupling enables targeted testing, faster iteration, and safer refactors.
- Optional dependency management lowers onboarding friction and ensures baseline CI stability.
- Clear package boundaries allow parallel development across world, policy, and telemetry teams without frequent merge conflicts.
- Improved observability and maintainability through explicit lifecycle management and interface-driven design.
