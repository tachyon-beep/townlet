# WC-A – Legacy Tick Flow Inventory (2025-10-10)

Source: `src/townlet/world/runtime.py::WorldRuntime.tick` (see repo snapshot).

## Preliminaries
- Inputs per tick: `tick`, optional `console_operations`, optional `action_provider`, optional `policy_actions`.
- Internal state: `_queued_console` (buffered commands), `_pending_actions` (staged actions when no modular context), `_ticks_per_day` (nightly reset cadence), references to `LifecycleManager`, `PerturbationScheduler`, and either legacy `WorldState` or modular `context`.

## Legacy (no `world.context`)
1. **Prepare console queue**
   - Start with `console_operations` if provided, otherwise drain `_queued_console` into `queued_ops`.
   - Clear `_queued_console` after draining.

2. **Prepare actions**
   - If `policy_actions` provided → clone into `prepared_actions`.
   - Else if `action_provider` supplied → call `action_provider(world, tick)` and clone.
   - Else → empty dict.
   - If `prepared_actions` empty and `_pending_actions` is populated → copy `_pending_actions` and clear the cache.

3. **Tick pipeline**
   - `world.tick = tick` (stamp tick).
   - `lifecycle.process_respawns(world, tick)` (spawn new agents).
   - `world.apply_console(queued_ops)` (execute queued commands).
   - `console_results = list(world.consume_console_results())` (capture command output).
   - `perturbations.tick(world, current_tick=tick)` (apply scheduler).
   - `world.apply_actions(prepared_actions)` (stage policy actions).
   - `world.resolve_affordances(current_tick=tick)` (resolve affordance state including queue handovers).
   - If `_ticks_per_day > 0` and `tick % _ticks_per_day == 0` → `world.apply_nightly_reset()`.
   - `terminated = dict(lifecycle.evaluate(world, tick))` (capture per-agent termination flags).
   - `termination_reasons = dict(lifecycle.termination_reasons())` (reason codes).
   - `events = list(world.drain_events())` (collect per-tick domain events).

4. **Result assembly**
   - Return `RuntimeStepResult` with `console_results`, `events`, `actions` (copy of `prepared_actions`), `terminated`, `termination_reasons`.

## Modular path (`world.context` exists)
1. Same console/action preparation as above.
2. Instead of direct pipeline, call `context.tick(...)` with:
   - `tick`, `console_operations=queued_ops`, `prepared_actions`, `lifecycle`, `perturbations`, `ticks_per_day`.
3. Expect `context.tick` to return either `RuntimeStepResult` or a mapping that can initialise one.
4. No legacy steps executed when context handles the tick; event/action/termination data comes from the context.

## Auxiliary methods influencing tick
- `queue_console` → buffers commands into `_queued_console` for next tick.
- `apply_actions` → when modular context exists calls `context.apply_actions`; else populates `_pending_actions` for legacy pipeline.
- `snapshot` → delegates directly to `world.snapshot()`.

## Required dependencies for modular implementation
- `WorldContext` must provide `apply_actions`, `tick`, `observe`/snapshot support, produce `RuntimeStepResult`, and manage:
  - Console command execution
  - Policy action staging
  - Lifecycle evaluation & termination reasons
  - Perturbation scheduler integration
  - Nightly reset scheduling via `ticks_per_day`
  - Event buffering for telemetry/policy usage.

Use this flow as the baseline when implementing `WorldContext` in WC-B onwards.
