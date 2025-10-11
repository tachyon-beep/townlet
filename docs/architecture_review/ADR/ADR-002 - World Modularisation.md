# ADR 0002: World Modularisation

## Status

Accepted

## Context

Townlet's world logic currently lives inside a single god-module (`world/grid.py`) that mixes grid
state, agent bookkeeping, action handling, per-tick systems, telemetry hooks, and randomness.
WP1 created the `WorldRuntime` port so the simulation loop can depend on behaviour contracts. The
port now lives in `townlet.ports.world`; the legacy `WorldRuntimeProtocol` alias in
`townlet.core.interfaces` has been removed.
acting as a deprecated alias during migration), but the concrete world implementation still exposes
sprawling concerns that are hard to test and evolve.
the concrete world implementation still exposes sprawling concerns that are hard to test and evolve.

We need a modular world package that keeps domain responsibilities isolated, emits domain events for
observers such as telemetry, and drives all mutation through a deterministic tick pipeline.

## Decision

- Create `townlet/world/` as the home for world runtime code. The minimum layout is:

  ```
  townlet/world/
    __init__.py
    context.py           # structural WorldRuntime façade
    state.py             # authoritative world state containers
    actions.py           # action schema, validation, apply pipeline
    observe.py           # read-only observation builders
    agents.py            # agent registry and lifecycle helpers
    spatial.py           # grid utilities, neighbourhood lookups
    systems/             # per-tick domain systems (employment, economy, etc.)
      __init__.py
      ...
    events.py            # domain events + dispatcher
    rng.py               # deterministic random helpers
    errors.py            # world-specific exceptions
  ```

- `context.WorldContext` composes these collaborators and provides the methods required by
  `WorldRuntime` (`reset`, `tick`, `agents`, `observe`, `apply_actions`, `snapshot`). Structural
  typing is sufficient; subclassing the protocol is optional.

- The tick pipeline follows a strict order:

  1. Intake actions via `actions.apply(state, actions_map, rng)` (validation + side effects).
  2. Run registered systems (`systems.default_pipeline()` yields callables).
  3. Capture emitted domain events (synchronous dispatch stored on the context).
  4. Increment the tick counter and expose snapshots via `snapshot()`.

- Determinism requirements:

  * `rng.make(seed: int | None)` returns a reproducible RNG.
  * `WorldContext.reset(seed)` creates a fresh state and RNG; identical seeds yield identical
    tick sequences in tests.

- Domain code must not import telemetry, CLI, HTTP, or policy modules. Any non-domain behaviour is
  delegated to adapters layered on top of `WorldRuntime`.

- Provide dummy/test helpers in `townlet/testing/dummies.py` so loop-level tests can exercise the
  modular world without heavy dependencies.

- Register `WorldContext` as the default provider in the world factory (`create_world`). Legacy
  world modules are retired once references are migrated.

## Module Map

```
WorldContext (context.py)
├── WorldState (state.py)
├── RNG (rng.py)
├── Action pipeline (actions.py)
│   └── emits Events (events.py)
├── Systems pipeline (systems/__init__.py)
│   └── individual systems (systems/*.py)
├── Agent registry (agents.py)
├── Spatial utilities (spatial.py)
└── Observations (observe.py)
    └── consumes state/agents/spatial
```

## Consequences

- Smaller modules allow targeted unit tests (spatial math, action validation, system behaviour).
- Telemetry and policy code integrate via ports instead of reaching inside the world.
- Event-driven design enables future features (analytics, back-pressure) without modifying world
  internals.
- Refactors can happen per module (e.g., replacing the spatial grid) without destabilising the tick
  loop contract.
- Old imports must be updated to `townlet.world.context.WorldContext` or the factory; documentation
  and configs need matching updates.

## Implementation Notes

- Provide a fixture (or builder) that constructs a tiny deterministic world for tests.
- Maintain a canonical list of registered systems in `systems/__init__.py` to avoid import cycles.
- When serialising snapshots, stick to JSON-safe structures until WP3 introduces DTOs.

## Related Documents

- `docs/architecture_review/WP_TASKINGS/WP1.md`
- `docs/architecture_review/WP_TASKINGS/WP2.md`
