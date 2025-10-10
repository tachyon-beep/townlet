# WP3B – Legacy Bridge Trace (Demo Story Arc, ticks 0–10)

This note captures the behaviours that still rely on the legacy world helpers after the DTO
refactor. The trace was generated from the demo story arc scenario (`configs/scenarios/demo_story_arc.yaml`)
with the personality features disabled (default scripted controller). The raw data lives at
`data/demo_trace_tick0-10.json` and records per-tick actions, emitted events, queue state, and
post-tick need levels.

## Observed Call Flow (WorldContext.tick)

1. **Respawn & Console Processing**
   - `lifecycle.process_respawns` → `WorldState.apply_console` → `WorldState.consume_console_results`.
2. **Perturbations**
   - `perturbations.tick` (unchanged from legacy flow).
3. **Action Application (Transitional Bridge)**
   - Modular path: `_coerce_actions` → `townlet.world.actions.apply_actions`.
     - Emits `action.move`/`action.invalid` events but only handles `move`/`noop`.
   - Legacy bridge: `WorldState.apply_actions` replays the full pipeline
     (`queue_system.request_access`, `affordance_system.start/release`, chat guards, etc.).
4. **System Steps**
   - `SystemContext` constructed with dispatcher + RNG stream.
   - `queues.step` is still a no-op; queue mutations occur during the legacy bridge.
   - `affordances.step` currently delegates to `WorldState.resolve_affordances` (legacy runtime).
   - `employment`, `relationships`, `economy`, `perturbations` steps run but rely on internal
     services seeded during bridge execution.
5. **Nightly Reset / Lifecycle**
   - `NightlyResetService.apply` (when `tick % ticks_per_day == 0`).
   - `lifecycle.evaluate` and `lifecycle.termination_reasons`.
6. **Event Drain**
   - `WorldState.drain_events` returns a mix of DTO-generated `action.*` events and the legacy
     mutations; duplicate `action.invalid` entries in the trace highlight the dual pathways.

## Key Findings

- **Queue state**: After 10 ticks the queue manager still reports empty active/queued slots, but the
  trace shows `action.invalid` events for each `wait` intent because the modular action pipeline
  does not implement `wait`. The behaviour guard rails rely on the legacy bridge to ignore these
  failures.
- **Needs decay**: Hunger/hygiene/energy dropped from the seeded values (e.g. demo_1 hunger
  `0.45 → 0.40`), confirming `_apply_need_decay` executes via
  `AffordanceRuntimeService.resolve → ctx.apply_need_decay`.
- **Relationship ledger**: Trust/familiarity values remain populated via the legacy chat events; no
  rivalry is introduced in the first 10 ticks.
- **Duplicate events**: Each tick records duplicate `chat_success` and `action.invalid` events
  because both the modular dispatcher and the legacy bridge emit them. This is safe short-term but
  will inflate telemetry until the bridge is removed.

## Next Actions (feeds WP3B plan)

1. **Queues**: Populate `townlet.world.systems.queues.step` with reservation/rotation/blocked logic,
   then stop calling `WorldState.apply_actions` for queue mutations. *(Ghost-step handling now
   resides in `queues.step`; promotion/handover logic still needs to migrate.)*
2. **Affordances**: Route modular actions through `AffordanceRuntimeService` directly and delete the
   `state.resolve_affordances` fallback.
3. **Need decay**: Expose `ctx.apply_need_decay` as a dedicated system (or keep it inside the
   affordance step once modularised).
4. **Instrumentation**: Once the bridge is gone, reproduce this trace and ensure no duplicate
   `action.*` events remain.

## Stage 3A – Direct `WorldState` reads (2025-10-10)

Audit of the remaining policy code paths that still reach into the raw `WorldState`
instead of the DTO façade. These references are now tracked so we can close them out during WP3B/WP3C.

- `src/townlet/policy/behavior.py` (`decide_agent`, guardrail helpers) – guardrail logic inspects
  `world.agents` snapshots and queue/relationship helpers. DTO equivalents live in `DTOWorldView`
  but the scripted behaviours still fall back to `world` for trust/rivalry details.
- `src/townlet/policy/behavior.py` (`_rivals_in_queue`, chat guard) – reads `world.queue_manager`
  and `world.relationship_tie` when DTO queue data is missing. Tagged for removal once DTO queue
  helpers are exercised in Stage 3B.
- `src/townlet/policy/scripted.py` – scripted capture adapters still enumerate `world.agents` to
  emit wait actions and update snapshots; DTO-backed scripted fixtures will replace these during the
  Stage 3B parity sweep.
- `src/townlet/policy/scenario_utils.py` – scenario seeding utilities populate `loop.world.agents`
  directly; intentional for fixtures, but noted so runtime logic does not depend on it.

All other `WorldState` accesses inside the policy runtime now pass through `DTOWorldView` courtesy of
the Stage 3A wiring. This list should shrink as we execute the Stage 3B plan.
