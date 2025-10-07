# WP-C Phase 3 — Agents & Affordances Decomposition

## Interfaces to Extract

- **AgentRegistry**: owns `AgentSnapshot` lifecycle (spawn, remove, iteration) and surfaces a `MutableMapping` compatible API for existing call sites. Responsibilities include spatial index registration hooks, basket metric updates, and context-reset triggers.
- **RelationshipService**: wraps relationship/rivalry ledgers and churn accumulator, exposing mutations (`update_relationship`, `register_conflict`) plus snapshot import/export helpers without leaking `_relationship_ledgers` internals.
- **EmploymentService**: composes `EmploymentCoordinator` and `EmploymentRuntime`, offering a single entry point for console handlers and lifecycle integrations (queueing exits, manual approvals, daily resets).
- **AffordanceEnvironment**: aggregates cross-cutting dependencies (queue manager, relationship service, agent registry, event emitter) supplied to the affordance runtime package instead of direct `WorldState` access.

## Mutable Surface Catalogue

| Concern | Current touchpoints | Notes |
| --- | --- | --- |
| Agent snapshots | `WorldState.agents`, `_sync_agent_spawn`, `AgentRegistry.add/discard`, observation builder, telemetry snapshots | Mutations must trigger spatial index updates and ctx-reset events. Registry exposes lifecycle callbacks for these side-effects. |
| Employment hooks | `EmploymentService.assign_jobs_to_agents`, `apply_job_state`, console `employment_exit` handlers, nightly reset | Coordinator emits telemetry events, runtime tracks queue metrics; facade keeps both pieces aligned. |
| Relationship/rivalry ledgers | Console force_chat/set_rel, queue conflict tracker, telemetry churn metrics, behaviour personality bias tests | Service owns decay cadence and eviction hooks. Pinned ties prevent console overrides from being decayed immediately. |
| Affordance runtime | `AffordanceRuntimeService.start/release/handle_blocked`, hook registry, manifest loader | Environment should hand the runtime only the dependencies it truly needs (queue manager, objects, reservations, emitters). |

## Protocol Summary

The following runtime-checkable protocols live in `townlet.world.agents.interfaces`:

- `AgentRegistryProtocol`: `MutableMapping[str, AgentSnapshot]` with `add`, `discard`, lifecycle callbacks, and a `values_map()` helper for serialization.
- `RelationshipServiceProtocol`: exposes tie/rivalry snapshots, mutation helpers (`update_relationship`, `set_relationship`, `apply_rivalry_conflict`), decay/remove behaviours, and ledger accessors used during tests and migrations.
- `EmploymentServiceProtocol`: wraps manual exit/defer workflows, daily counters, queue snapshots, and job-state helpers consumed by console handlers and nightly reset logic.

These protocols are intended to back the public contract for `WorldContext`, console bridges, and future training APIs.

## Entry Points & Consumers

- **Simulation loop** (`src/townlet/core/sim_loop.py`): relies on `WorldState` façade for registry iteration, relationship snapshots, employment updates, and affordance resolution.
- **Telemetry** (`snapshots/state.py`, relationship metrics publisher): imports registry/service data for snapshot serialization.
- **Console bridge** (`world/console/handlers.py`): uses employment service and relationship service to apply admin commands, now via the protocols above.
- **Queue/behaviour logic** (`world/queue/conflict.py`, `tests/test_behavior_personality_bias.py`): interacts with rivalry metrics and queue manager outcomes, expecting service-level accessors.
- **Training orchestrator & demos** (`townlet/policy/training_orchestrator.py`, `townlet/demo/runner.py`): consume registry/service data when building policy contexts or scripted events.

## Dependency Impacts

- `SimulationLoop` continues to interact through `WorldState` façade; new services are injected during `WorldState.__post_init__` and re-exported via `WorldContext`.
- Console handlers and queue/conflict trackers depend on `RelationshipService` for tie lookups and trust adjustments rather than mutating dictionaries directly.
- Snapshot/restore paths reference the service accessors (`relationships.snapshot_payload()`, `relationships.load_snapshot(...)`) ensuring payload compatibility is preserved.
- Affordance runtime service accepts injected hooks for queue interactions and event emission, enabling future extraction into dedicated modules.

## Validation Checklist

1. Regression suites covering behaviour, relationships, queues, and affordances remain green.
2. Snapshot round-trips (`tests/test_snapshots_state.py`) confirm no schema drift.
3. Console dispatcher exercises (`tests/test_console_dispatcher.py`) continue to function via new service interfaces.
4. Documentation updated to describe service boundaries and migration strategy.
