# Console Service Relocation Plan — 2025-10-11

Goal: move console service ownership from `WorldState` into the orchestration
layer (`SimulationLoop` + `ConsoleRouter`) so the world no longer maintains its
own buffering or handler lifecycle.

## Execution Steps

- [x] **Extract Console Construction**
   - Stop instantiating `ConsoleService` inside `WorldState.__post_init__`.
   - Add `WorldState.attach_console_service(console)` helper that installs handlers
     and rebuilds `WorldContext`; allow `WorldState.from_config` to skip console
     attachment or accept an injected factory.
   - Ensure `WorldContext` creation happens only after a console service is
     attached.

- [x] **Rewire Factory & Loop** *(2025-10-11)*
   - Update the default world factory to create the console service explicitly,
     call `world.attach_console_service`, and expose the service to the loop via
     `WorldComponents`.
   - Persist a reference to the service in `SimulationLoop` so downstream tests
     and the console router share the same instance.

- [ ] **Remove World-Level Buffers**
   - Drop any remaining `WorldState._console_*` caching utilities now that the
     loop/router owns emission.
   - Update telemetry publisher and stub transports to rely solely on dispatcher
     events (`console.result`) instead of polling world buffers.

- [ ] **Docs & Tests**
   - Refresh WP1/WP3 notes, ADR references, and console contract docs to describe
     the new ownership.
   - Update tests/dummy harnesses to construct and attach console services
     explicitly; rerun console, telemetry, and dashboard suites.

This file tracks progress through the relocation. Steps 1–2 complete; proceed
with buffer removal and documentation refresh.
