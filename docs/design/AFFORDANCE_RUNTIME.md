# Affordance Runtime Overview

## Context

`DefaultAffordanceRuntime` is the bridge between `WorldState` and affordance execution. The runtime centralises the logic that previously lived in `WorldState` so future refactors can further modularise affordances without breaking public APIs.

## Key Entry Points

- `WorldState.affordance_runtime` — returns the runtime bound to the current world instance.
- `WorldState.running_affordances_snapshot()` — exposes `RunningAffordanceState` structures for telemetry/tests.
- `DefaultAffordanceRuntime.start(agent_id, object_id, affordance_id, tick)` — handles precondition checks, hook dispatch, reservation updates, and event emission.
- `DefaultAffordanceRuntime.release(agent_id, object_id, success, reason, requested_affordance_id, tick)` — applies effects, dispatches hooks, and handles queue release semantics.
- `DefaultAffordanceRuntime.handle_blocked(object_id, tick)` — performs ghost-step handling and hook dispatch when queues stall.
- `DefaultAffordanceRuntime.remove_agent(agent_id)` — clears running affordances when an agent leaves the world.
- `DefaultAffordanceRuntime.running_snapshot()` — serialisable view (object → `RunningAffordanceState`).

## Developer Guidance

### Starting or Extending Hooks

- Register hooks with `WorldState.register_affordance_hook(name, handler)`.
- Handlers receive a `HookPayload`-compatible dict (`stage`, `hook`, `agent_id`, `object_id`, `affordance_id`, etc.).
- Use `context.get("cancel")` within `before` hooks to abort an affordance start.
- Avoid mutating the world outside provided context keys; prefer `world.affordance_runtime` utilities when modifying running affordances.

### Recording Outcomes

- The runtime funnels outcomes through `AffordanceOutcome`; `apply_affordance_outcome` keeps agent snapshots consistent with capped metadata history (`_affordance_outcomes`, max 10 entries).
- When adding new affordance actions, ensure outcome metadata contains serialisable content (primitives) for future telemetry exposure.

### Telemetry & Snapshots

- `running_affordances_snapshot()` is the supported way to surface running state; avoid reaching into `_running_affordances` directly.
- Telemetry parity must be validated against `audit/baselines/worldstate_phase3` after changes affecting runtime scheduling or hook side-effects.

### Testing Expectations

- `tests/test_affordance_hooks.py` covers hook firing order, runtime start/release, agent cleanup, and outcome logging bounds.
- New behaviours should arrive with targeted unit tests alongside guardrail runs (`tox -e refactor`).

## Open Questions / TODOs

- **TODO-AFF-001**: Integrate snapshot persistence with the runtime to eliminate direct `_running_affordances` exports.
- **TODO-AFF-002**: Decide whether DEBUG timing probes stay long-term or move behind a config flag.
- **TODO-AFF-003**: Explore dependency-injectable runtime to support bespoke testing or alternative affordance schedulers.

Please coordinate updates via `docs/engineering/WORLDSTATE_REFACTOR.md` to keep the refactor status in sync.
