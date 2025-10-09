# WP1 Status

**Current state (2025-10-09)**
- Port protocols, registry framework, and default adapters were completed in the initial WP1 pass; smoke tests for the new factories remain pending because the composition root still uses the legacy registry helpers.
- WP2 Step 6 is now finished: `WorldContext` returns `RuntimeStepResult`, modular systems run via `SystemContext`, and the legacy `WorldState` exposes the helper methods expected by the port layer (`agent_records_view`, `emit_event`, `event_dispatcher`, deterministic RNG seed access). Targeted suites (`pytest tests/world -q`, `pytest tests/test_world_context.py -q`) pass.
- `WorldRuntime.tick` recognises the modular result, so swapping the simulation loop over to `WorldContext` is unblocked.

**Up next (Step 7 / WP1 Step 4 resume)**
- World factory now builds `WorldContext`; dummy/stub providers are updated and `tests/world/test_world_factory.py` covers the path.
- Next steps focus on the simulation loop refactor (Step 8): introduce the factory helpers, wire in `ConsoleRouter`/`HealthMonitor`, and migrate telemetry usage from getter-style pulls to event/metric emissions.
- Work proceeds incrementally per the detailed plan (Phase 1: factory swap, Phase 2: console/monitor integration, Phase 3: telemetry getter removal, Phase 4: cleanup/docs).
- Console routing and health monitoring now initialise inside `SimulationLoop`: console commands are mirrored into the new router (still forwarded to the legacy runtime for execution) and `HealthMonitor` emits baseline queue/event metrics via the telemetry port.
- Telemetry events (`loop.tick`, `loop.health`, `loop.failure`) now flow through the WP3 dispatcher via the stdout adapter; legacy `record_*` calls remain only as shims and will be removed once WP3 Section 3 completes.

**Legacy caller inventory (2025-10-09 snapshot)**
- Policy:
  - `PolicyController` now owns ctx-reset/anneal hooks and per-tick bookkeeping; the loop no longer calls `PolicyRuntime` directly for these operations.
  - `src/townlet/core/sim_loop.py:369` — controller still delegates `decide(world, tick)` straight to the scripted backend with a `WorldState`; migrate to observation-first `policy_port.decide(observations)` once world-driven observations are ready.
  - `src/townlet/core/sim_loop.py:387-393` — controller forwards telemetry metadata from the backend; replace with port-friendly events when policy adapters expose the necessary data.
- Telemetry (loop relies on publisher internals slated for removal):
  - `src/townlet/core/sim_loop.py:214` and `src/townlet/core/sim_loop.py:270` — runtime variant and policy identity setters; emit these as events/metrics through the telemetry port instead of mutating publisher state.
  - `src/townlet/core/sim_loop.py:359-380` — console buffer is still drained from telemetry to preserve legacy behaviour, but the router now emits console events; complete the migration by dropping the getter usage and feeding commands directly into the router entrypoint.
  - `src/townlet/core/sim_loop.py:484` — loop now emits `loop.tick` events via the telemetry port; underlying adapters translate to `publish_tick`, but the composition root no longer calls the legacy API directly.
  - `src/townlet/core/sim_loop.py:502` — queue/embedding/job/employment metrics and rivalry history are derived from the world adapter; remaining telemetry getters have been removed from the loop.
  - `src/townlet/core/sim_loop.py:526` and `src/townlet/core/sim_loop.py:589` — health/failure payloads pull from locally tracked status snapshots; Stdout adapter now forwards `loop.health` / `loop.failure` events into the legacy publisher until the sink exposes streaming equivalents.
- World (loop still holds legacy runtime/world references):
  - `src/townlet/core/sim_loop.py:366` and `src/townlet/core/sim_loop.py:371` — uses `runtime.queue_console` and passes an `action_provider`; after the port swap the loop should enqueue console commands through `ConsoleRouter` and call `world_port.tick()` once actions are applied.
  - `src/townlet/core/sim_loop.py:381-383` and `src/townlet/core/sim_loop.py:392` — mutates agents directly off `WorldState`; migrate to `WorldContext` helpers (or dedicated services) so loop code no longer pokes at internal registries.
  - `src/townlet/core/sim_loop.py:399` — reads `self.config` plus `policy.active_policy_hash()` to construct identity; ultimately the world snapshot + policy adapter should feed this via events without exposing the legacy runtime.
