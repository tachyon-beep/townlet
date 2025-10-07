# Consolidated ADR 0001: Ports and Factory Registry

## Status

Accepted

## Context

The simulation loop imported concrete classes from `townlet.world`, `townlet.policy` and `townlet.telemetry`. That blocked stubbing, complicated testing, and made optional features feel mandatory. WP1 introduces ports (protocol interfaces) and registry-backed factories so the loop depends on behaviour, not implementation.

## Decision

Define three minimal ports in `townlet.ports.*`. Keep them focused on what the loop actually calls. Do not include console UI, training internals or transport specifics in the ports. Those live behind adapters.

| Port            | Module                    | Purpose                                      | Minimal methods                                                                                                                                      |                                                                                                          |                                                                                                                     |
| --------------- | ------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `WorldRuntime`  | `townlet.ports.world`     | Advance and query world state.               | `reset(seed: int                                                                                                                                     | None) -> None`,`tick() -> None`,`agents() -> Iterable[AgentId]`,`observe(agent_ids: Iterable[AgentId] | None) -> Mapping[str, Any]`,`apply_actions(actions: Mapping[str, Any]) -> None`,`snapshot() -> Mapping[str, Any]` |
| `PolicyBackend` | `townlet.ports.policy`    | Decide actions for agents.                   | `on_episode_start(agent_ids: Iterable[AgentId]) -> None`, `decide(observations: Mapping[str, Any]) -> Mapping[str, Any]`, `on_episode_end() -> None` |                                                                                                          |                                                                                                                     |
| `TelemetrySink` | `townlet.ports.telemetry` | Emit events and metrics. Lifecycle optional. | `start() -> None`, `stop() -> None`, `emit_event(name: str, payload: Mapping[str, Any]                                                               | None = None) -> None`,`emit_metric(name: str, value: float, **tags: Any) -> None`                       |                                                                                                                     |

Anything like `queue_console`, `drain_console_buffer`, `register_ctx_reset_callback`, `flush_transitions`, `active_policy_hash`, `publish_tick`, or `record_loop_failure` is intentionally not part of these ports. Put those behind adapters or backend-specific utilities.

Adapters in `townlet.adapters.*` wrap current implementations to satisfy the ports without changing their internals:

* `WorldContextAdapter` implements `WorldRuntime` by delegating to today’s world engine.
* `ScriptedPolicyAdapter` implements `PolicyBackend` with the current non-torch logic.
* `TelemetryAdapter` implements `TelemetrySink` and translates domain events into whatever publisher you have now. Console I/O belongs here or in a CLI layer, not in world.

Factories and registry live in `townlet.factories.*`:

* `create_world(cfg) -> WorldRuntime`
* `create_policy(cfg) -> PolicyBackend`
* `create_telemetry(cfg) -> TelemetrySink`

A simple string keyed registry maps provider names to constructors. Unknown keys raise `ConfigurationError`.

### Registry keys

| Domain    | Keys (initial)                                      |
| --------- | --------------------------------------------------- |
| world     | `default`, `dummy`                                  |
| policy    | `scripted` (default), `pytorch` (optional), `dummy` |
| telemetry | `stdout` (default), `stub`, `file`, `dummy`         |

These names are examples. Keep them stable in docs and config.

### Composition

The composition root resolves the three ports via factories and passes only ports into the loop. The loop imports `townlet.ports.*` and factory helpers only. No concrete imports.

### Example configuration

```yaml
runtime:
  world: { provider: default }
  policy: { provider: scripted }
  telemetry: { provider: stdout }
```

## Consequences

* Tests can run the loop with `dummy` providers.
* Optional features like torch are truly optional. If the pytorch backend is not installed, the factory can refuse with a clear error or fall back to `scripted`.
* WP2 can modularise world internals safely because the loop does not reach in via console queues or publisher helpers.

## Migration notes for existing code

* If the current world or telemetry exposes console buffers, keep that in the adapter layer. The world port must not mention console.
* Training utilities like transition buffers, hashes, annealing, etc. should live inside the pytorch policy backend or its helpers, not in the policy port.

---

## Quick fix-up checklist for your two ADR variants

The two ADRs are close, but both pulled today’s surface area into the ports. To align them with the consolidated ADR:

1. Remove console and training methods from ports:

   * Drop `bind_world`, `queue_console`, `drain_console_buffer`, `register_ctx_reset_callback`, `flush_transitions`, `active_policy_hash`, `publish_tick`, `record_loop_failure`, `record_stability_metrics`.
   * If call sites exist, rehome them into the relevant adapter and expose a simple `emit_event` from the loop instead.

2. Adjust world tick contract:

   * Prefer `world.tick()` with no tick argument. The world should own its tick counter. If the loop needs the count, read it from `world.snapshot()`.

3. Keep `apply_actions` on world, and keep policy pure:

   * Loop: `obs = world.observe(ids)` then `actions = policy.decide(obs)` then `world.apply_actions(actions)` then `world.tick()` then `telemetry.emit_event(...)`.

4. Telemetry API:

   * Use `start` and `stop` rather than `close`. Keep `emit_event` and `emit_metric`. If you really want a single “publish tick” call, implement it inside the telemetry adapter and have the loop call that, but do not add it to the port unless absolutely necessary.

5. Registry keys:

   * Collapse to `default/scripted/stdout` plus `dummy` and keep a single place documenting them. Avoid duplicate names like `default` and `facade` for the same thing.

6. Factories:

   * Ensure unknown keys raise `ConfigurationError` with a helpful message and known keys in the error string.

7. Tests:

   * One smoke test that runs two ticks with dummies only.
   * One factory test per domain for key selection and error paths.

---

## Paste-ready ADR to commit

Replace `docs/adr/0001-ports-and-factories.md` with this content so there is a single source of truth. Keep the file name stable.

````markdown
# ADR 0001: Ports and Factory Registry

## Status

Accepted

## Context

The simulation loop previously depended on concrete implementations from `townlet.world`, `townlet.policy`, and `townlet.telemetry`. That coupling impeded testing, optional features, and future refactors. We need a thin port layer and registry-backed factories so composition happens against behaviour contracts rather than concrete types.

## Decision

Introduce three protocol ports with minimal method sets:

- `WorldRuntime` (`townlet.ports.world`): `reset(seed)`, `tick()`, `agents()`, `observe(agent_ids|None)`, `apply_actions(actions)`, `snapshot()`.
- `PolicyBackend` (`townlet.ports.policy`): `on_episode_start(agent_ids)`, `decide(observations) -> actions`, `on_episode_end()`.
- `TelemetrySink` (`townlet.ports.telemetry`): `start()`, `stop()`, `emit_event(name, payload|None)`, `emit_metric(name, value, **tags)`.

Do not include console UI, training internals, or transport-specific helpers in ports. Place those behind adapters.

Create adapters in `townlet.adapters.*` that wrap current implementations to satisfy the ports. Provide registry-backed factories in `townlet.factories.*`:

- `create_world(cfg) -> WorldRuntime`
- `create_policy(cfg) -> PolicyBackend`
- `create_telemetry(cfg) -> TelemetrySink`

Use string keys for providers. Unknown keys raise `ConfigurationError`.

### Registry keys

- World: `default`, `dummy`
- Policy: `scripted` (default), `pytorch` (optional), `dummy`
- Telemetry: `stdout` (default), `stub`, `file`, `dummy`

### Composition

The composition root imports only ports and factories, resolves providers from config, and injects them into the loop. The loop calls:

1. `obs = world.observe(agent_ids=None)`
2. `actions = policy.decide(obs)`
3. `world.apply_actions(actions)`
4. `world.tick()`
5. `telemetry.emit_event("tick", world.snapshot())` or finer-grained events as needed

## Consequences

- Tests run with `dummy` providers. Optional backends like pytorch are add-ons, not hard requirements.
- WP2 can safely modularise world internals behind `WorldRuntime`.
- Telemetry and console remain pluggable and do not leak into domain code.

## Example config

```yaml
runtime:
  world: { provider: default }
  policy: { provider: scripted }
  telemetry: { provider: stdout }
````

## Notes

If legacy call sites need console buffering or training hooks, adapt them in the corresponding adapter. Do not expand the ports unless the loop itself truly needs the capability.
