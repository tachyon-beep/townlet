# ADR 0001: Ports and Factory Registry

## Status

Accepted

## Context

The simulation loop currently instantiates concrete classes from `townlet.world`, `townlet.policy`, and `townlet.telemetry`. That tight coupling makes it difficult to stub dependencies, complicates optional installs (e.g., torch), and blocks incremental refactors. Work Package 1 introduces minimal protocol ports and registry-backed factories so the loop depends on behaviour contracts rather than specific implementations.

## Decision

Implement the following shape, mirroring the WP1 requirements:

1. **Minimal ports only.** Create `townlet/ports/` and define the exact protocols below. They represent the sole surface the loop sees.

   ```python
   # townlet/ports/world.py
   from typing import Protocol, Iterable, Mapping, Any

   class WorldRuntime(Protocol):
       def reset(self, seed: int | None = None) -> None: ...
       def tick(self) -> None: ...
       def agents(self) -> Iterable[str]: ...
       def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]: ...
       def apply_actions(self, actions: Mapping[str, Any]) -> None: ...
       def snapshot(self) -> Mapping[str, Any]: ...
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

2. **World owns the tick.** `world.tick()` takes no tick argument; the loop reads the current tick from `world.snapshot()`. Maintain `world.apply_actions()` between `observe` and `tick` so policy decisions remain stateless.

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

6. **Composition root imports ports only.** Entry points resolve providers via factories:

   ```python
   world = create_world(cfg)
   policy = create_policy(cfg)
   telemetry = create_telemetry(cfg)

   telemetry.start()
   agent_ids = list(world.agents())
   policy.on_episode_start(agent_ids)
   for _ in range(cfg.runtime.max_ticks):
       observations = world.observe()
       actions = policy.decide(observations)
       world.apply_actions(actions)
       world.tick()
       telemetry.emit_event("tick", world.snapshot())
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

## Related Documents

- `docs/architecture_review/WP_TASKINGS/WP1.md` — implementation checklist aligned with this ADR.
- `docs/architecture_review/ARCHITECTURE_REVIEW_2.md` — architectural context motivating the port boundary.
