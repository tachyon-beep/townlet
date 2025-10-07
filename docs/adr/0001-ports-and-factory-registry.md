# ADR 0001: Ports and Factory Registry

## Status

Accepted

## Context

The simulation loop previously depended on concrete implementations from `townlet.world`,
`townlet.policy`, and `townlet.telemetry`. That coupling impeded testing, optional features, and
future refactors. We need a thin port layer and registry-backed factories so composition happens
against behaviour contracts rather than concrete types.

## Decision

Introduce three protocol ports with minimal method sets:

- `WorldRuntime` (`townlet.ports.world`): `reset(seed)`, `tick()`, `agents()`,
  `observe(agent_ids|None)`, `apply_actions(actions)`, `snapshot()`.
- `PolicyBackend` (`townlet.ports.policy`): `on_episode_start(agent_ids)`, `decide(observations) -> actions`,
  `on_episode_end()`.
- `TelemetrySink` (`townlet.ports.telemetry`): `start()`, `stop()`, `emit_event(name, payload|None)`,
  `emit_metric(name, value, **tags)`.

Do not include console UI, training internals, or transport-specific helpers in ports. Place those
behind adapters.

Create adapters in `townlet.adapters.*` that wrap current implementations to satisfy the ports.
Provide registry-backed factories in `townlet.factories.*`:

- `create_world(cfg) -> WorldRuntime`
- `create_policy(cfg) -> PolicyBackend`
- `create_telemetry(cfg) -> TelemetrySink`

Use string keys for providers. Unknown keys raise `ConfigurationError`.

### Registry keys

- World: `default`, `dummy`
- Policy: `scripted` (default), `dummy`
- Telemetry: `stdout` (default), `stub`, `dummy`

### Composition

The composition root imports only ports and factories, resolves providers from config, and injects
them into the loop. The loop calls:

1. `obs = world.observe(agent_ids=None)`
2. `actions = policy.decide(obs)`
3. `world.apply_actions(actions)`
4. `world.tick()`
5. `telemetry.emit_event("tick", world.snapshot())`

## Consequences

- Tests run with `dummy` providers. Optional backends are add-ons, not hard requirements.
- Telemetry and console remain pluggable and do not leak into domain code.

## Example config

```yaml
world:
  provider: default
policy:
  provider: scripted
telemetry:
  provider: stdout
```

## Notes

If legacy call sites need console buffering or training hooks, adapt them in the corresponding
adapter. Do not expand the ports unless the loop itself truly needs the capability.
