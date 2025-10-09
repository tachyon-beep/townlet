# WP2 — World Modularisation Notes

This workspace tracks analysis, plans, and progress for Work Package 2 (modularising the world subsystem behind the WP1 ports).

## Scope Overview
- Decompose the monolithic `world/grid.py` + friends into a cohesive `townlet.world` package aligned with ADR-002.
- Introduce `WorldContext` implementing the `WorldRuntime` port, backed by explicit modules for state, agents, actions, systems, events, and RNG.
- Emit domain events instead of direct telemetry calls; prepare orchestration services (console router, health monitor) to consume those events.
- Update factories and the simulation loop to depend on the new context (resuming WP1 Step 4 once the world package is in place).

## Current Status
- WP1 scaffold (ports/adapters/factories) complete; composition refactor deferred to WP2.
- Planning (Steps 0–1) complete; package skeleton established (Step 2).
- Step 3 complete: stateless helpers extracted (spatial index, observation views) and the domain event dispatcher implemented with unit coverage.
- Step 4 complete: the enriched agent registry/world state ship with RNG seeding, ctx-reset signalling, event buffering, and agent metadata views backed by unit tests.
- Step 5 complete: the action schema/validation pipeline is in place (`move`/`noop` implemented for now) and emits structured events that feed the modular context + dispatcher.
- Step 6 complete: the modular systems execute inside `WorldContext.tick` (queues, affordances, employment, relationships, economy, perturbations), RNG streams are managed centrally, and the legacy world state now exposes the port-friendly surface (`agent_records_view`, `emit_event`, `event_dispatcher`, `rng_seed`) so new tests and the legacy runtime agree.

Use this folder to capture findings, risks, test coverage, and design decisions as WP2 progresses.
