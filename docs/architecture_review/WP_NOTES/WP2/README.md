# WP2 — World Modularisation Notes

This workspace tracks analysis, plans, and progress for Work Package 2 (modularising the world subsystem behind the WP1 ports).

## Scope Overview
- Decompose the monolithic `world/grid.py` + friends into a cohesive `townlet.world` package aligned with ADR-002.
- Introduce `WorldContext` implementing the `WorldRuntime` port, backed by explicit modules for state, agents, actions, systems, events, and RNG.
- Emit domain events instead of direct telemetry calls; prepare orchestration services (console router, health monitor) to consume those events.
- Update factories and the simulation loop to depend on the new context (resuming WP1 Step 4 once the world package is in place).

## Current Status
- WP1 scaffold (ports/adapters/factories) complete; composition refactor deferred to WP2.
- Planning phase underway (see `tasks.md`, `implementation_plan.md`).

Use this folder to capture findings, risks, test coverage, and design decisions as WP2 progresses.
