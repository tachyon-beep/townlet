# ADR 0001: Ports and Factory Registry

## Status

Accepted

## Context

The simulation loop currently instantiates concrete classes from `townlet.world`, `townlet.policy`, and `townlet.telemetry`. That tight coupling makes it difficult to stub dependencies, complicates optional installs (e.g., torch), and blocks incremental refactors. Work Package 1 introduces minimal protocol ports and registry-backed factories so the loop depends on behaviour contracts rather than specific implementations.

## Decision

Implement the following shape, mirroring the WP1 requirements:

1. **Minimal ports only.** Create `townlet/ports/` and define the exact protocols below. They represent the sole surface the loop sees. World is exported via `townlet.ports.world.WorldRuntime` (runtime-checkable protocol); policy and telemetry remain under `townlet.core`.

   ```python
   # townlet/ports/world.py
   from typing import Protocol, Iterable, Mapping, Any

   from collections.abc import Iterable, Mapping, Callable
   from typing import Protocol, Any

   class WorldRuntime(Protocol):
       def bind_world(self, world: WorldState) -> None: ...
       def queue_console(self, operations: Iterable[ConsoleCommandEnvelope]) -> None: ...
       def apply_actions(self, actions: Mapping[str, Any]) -> None: ...
       def tick(
           self,
           *,
           tick: int,
           console_operations: Iterable[ConsoleCommandEnvelope] | None = None,
           action_provider: Callable[[WorldState, int], Mapping[str, Any]] | None = None,
           policy_actions: Mapping[str, Any] | None = None,
       ) -> RuntimeStepResult: ...
       def snapshot(
           self,
           *,
           config: Any | None = None,
           telemetry: TelemetrySinkProtocol | None = None,
           stability: Any | None = None,
           promotion: Any | None = None,
           rng_streams: Mapping[str, Any] | None = None,
           identity: Mapping[str, Any] | None = None,
       ) -> SnapshotState: ...
   ```

   ```python
   # townlet/ports/policy.py
   from typing import Protocol, Mapping, Any, Iterable

   class PolicyBackend(Protocol):
       def on_episode_start(self, agent_ids: Iterable[str]) -> None: ...
       def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]: ...
       def on_episode_end(self) -> None: ...
   ```

   ```python
   # townlet/ports/telemetry.py
   from typing import Protocol, Mapping, Any

   class TelemetrySink(Protocol):
       def start(self) -> None: ...
       def stop(self) -> None: ...
       def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None: ...
       def emit_metric(self, name: str, value: float, **tags: Any) -> None: ...
   ```

   *No console buffering, training hooks, transport specifics, or loop instrumentation methods belong on these ports.*

2. **World owns the tick.** `WorldRuntime.tick` accepts the loop tick and optional console/actions inputs. `ConsoleRouter` stages commands via `queue_console`; the loop forwards policy actions via `apply_actions` before invoking `tick`. DTO-only follow-up work (WP3) will replace the `WorldState` callback with prebuilt DTO action batches.

3. **Telemetry lifecycle is explicit.** The loop calls `telemetry.start()` before the first tick and `telemetry.stop()` during shutdown. Every other telemetry concern (console output, batching, back-pressure) lives in adapters.

4. **Adapters form the anti-corruption layer.** Provide thin wrappers in `townlet.adapters.*` that satisfy each port by delegating to the existing world, policy, and telemetry implementations. Any legacy methods stay inside the adapter.

5. **Registry-backed factories compose the runtime.** Implement:

   - `townlet/factories/registry.py` with a `register(kind: str, key: str)` decorator, `REGISTRY: dict[str, dict[str, Callable[..., object]]]`, and `ConfigurationError`.
   - Domain factories:
     * `create_world(cfg) -> WorldRuntime`
     * `create_policy(cfg) -> PolicyBackend`
     * `create_telemetry(cfg) -> TelemetrySink`
   - Register the WP1 canonical providers:
     * World: `"default"`, `"dummy"`
     * Policy: `"scripted"` (default), `"dummy"`
     * Telemetry: `"stdout"` (default), `"stub"`, `"dummy"`

   Unknown keys raise `ConfigurationError(f"Unknown {kind} provider: {key}. Known: {sorted(REGISTRY[kind])}")`.

6. **Composition root imports ports only.** Entry points resolve providers via factories; the simulation loop emits dispatcher events plus a DTO `global_context` payload. High-level structure:

   ```python
   world = create_world(cfg)
   policy = create_policy(cfg)
   telemetry = create_telemetry(cfg)

   telemetry.start()
   agent_ids = list(world.agents())
   policy.on_episode_start(agent_ids)
   for tick in range(1, cfg.runtime.max_ticks + 1):
       envelope = world.observe()
       actions = policy.decide(envelope)
       world.apply_actions(actions)
       result = world.tick(tick=tick)
       telemetry.emit_event("loop.tick", {"tick": tick, "result": result})
   policy.on_episode_end()
   telemetry.stop()
   ```

   The loop never imports concrete adapters or internal modules directly.

7. **Testing surface.** Provide dummy implementations in `townlet/testing/dummies.py` and mark smoke tests that use adapters if they require optional dependencies. This matches WP1’s acceptance criteria.

## Consequences

- Composition becomes configuration-driven; swapping implementations requires registry entries only.
- Tests can execute the loop end-to-end with dummy providers, improving reliability under minimal dependencies.
- Optional tooling (e.g., torch-based policy backends) can be registered out-of-tree without forcing heavy installs on baseline runs.
- Further refactors (breaking up world god-objects, decomposing telemetry) can happen behind adapters without touching the loop contract.

## Migration Notes

- Relocate any extra behaviour (`queue_console`, `flush_transitions`, `active_policy_hash`, etc.) into adapters or specialised backends. Expanding the ports requires a fresh ADR.
- Keep provider keys stable; document additions in both the ADR and the WP1 tasking file.
- When removing legacy factories, ensure configs use the new registry-backed paths and update docs alongside the code.
- As DTO-only telemetry rolls out (WP3 Stage 5/6), keep guard tests (`tests/core/test_no_legacy_observation_usage.py`, `tests/test_telemetry_surface_guard.py`, `tests/test_console_commands.py`, `tests/test_conflict_telemetry.py`, `tests/test_observer_ui_dashboard.py`) green—any reintroduction of legacy observation builders or payloads must be confined to adapters/factories explicitly listed in the whitelist.
- Health/failure telemetry now exposes a structured payload with `transport`, DTO `global_context`, and a `summary` block replacing prior `telemetry_*` aliases. Adapters that ingest historical payloads must convert aliases into the summary before handing data to dashboards; new integrations should rely on the structured fields exclusively.

## Implementation Status

**Status**: COMPLETE (with architectural improvements)
**Completion Date**: 2025-10-13 (WP3.2 WS1)

### Delivered Components

- ✅ Port protocols defined in `townlet/ports/` (world, policy, telemetry)
- ✅ Registry-backed factories in `townlet/factories/`
- ✅ Adapter implementations in `townlet/adapters/`
- ✅ Dummy test implementations in `townlet/testing/`
- ✅ Comprehensive test coverage (14 tests passing):
  - Port surface tests (3 tests)
  - Factory registry tests (7 tests)
  - Dummy loop integration tests (3 tests)
  - Modular smoke tests (1 test)

### Deviations from Original Specification

The implementation evolved beyond the original ADR specification in ways that objectively improve the architecture:

#### 1. WorldRuntime Implementation

**Planned**: WorldContext façade implementing WorldRuntime protocol
**Actual**: WorldRuntime concrete class in `world/runtime.py`, separate from WorldContext

**Rationale**:
- The WorldRuntime façade requires stateful coordination (action staging, buffer management, tick sequencing)
- A concrete class provides this coordination layer more naturally than a pure context object
- WorldContext (in `world/core/context.py`) focuses on system aggregation and observation building

**Assessment**: Objectively better — clearer separation of concerns (runtime orchestration vs. context access)

#### 2. Naming Convention

**Planned**: Different names for protocol and implementation
**Actual**: Same name (WorldRuntime) for both protocol and concrete class

**Rationale**:
- Structural typing (PEP 544) allows this pattern without confusion
- Different namespaces provide natural separation (`ports.world` vs. `world.runtime`)
- The concrete class naturally fulfills the protocol contract
- Cleaner API - consumers import from logical locations

**Assessment**: Acceptable — no confusion in practice due to namespacing. Enhanced with comprehensive docstring explaining the pattern (see `ports/world.py:27-55`).

#### 3. WorldContext Architecture

**Planned**: Single WorldContext implementing WorldRuntime
**Actual**: WorldContext in `world/core/context.py`, separate from WorldRuntime façade

**Rationale**:
- WorldContext aggregates domain systems and provides state access
- WorldRuntime orchestrates tick sequencing and manages external interactions
- Clean separation: context = state access, runtime = orchestration
- WorldContext is used internally by WorldRuntime, not exposed at port boundary

**Assessment**: Objectively better — clearer responsibilities, easier testing, better modularity

#### 4. Obsolete Context Stub Removed

**Planned**: N/A (predates this specification)
**Actual**: Deleted `townlet/world/context.py` stub containing only NotImplementedError

**Rationale**:
- Stub was created as placeholder during WP2 planning
- Full implementation now exists in `world/core/context.py` and `world/runtime.py`
- Stub served no purpose and caused naming confusion

**Assessment**: Objectively better — eliminates dead code and reduces confusion

### Verification

- ✅ All port/factory tests passing (14/14)
- ✅ Type checking clean (`mypy src/townlet/ports/`)
- ✅ No imports of deleted context stub
- ✅ Documentation updated with implementation patterns
- ✅ ADR-002 (World Modularisation) documents actual architecture
- ✅ ADR-003 (DTO Boundary) extends ports with typed DTOs

## Related Documents

- `docs/architecture_review/WP_TASKINGS/WP1.md` — implementation checklist aligned with this ADR.
- `docs/architecture_review/ARCHITECTURE_REVIEW_2.md` — architectural context motivating the port boundary.
- `docs/architecture_review/ADR/ADR-002 - World Modularisation.md` — world package structure and WorldContext implementation.
- `docs/architecture_review/ADR/ADR-003 - DTO Boundary.md` — typed DTO boundaries extending the port protocols.
