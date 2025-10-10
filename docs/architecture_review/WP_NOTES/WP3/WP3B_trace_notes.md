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

Initial audit of the policy layer highlighted the last pockets of legacy world access.
Stage 3B executes the remediation plan summarised below.

## Stage 3B Summary (2025-10-10)

- `DTOWorldView` now materialises per-agent snapshots (needs, job, personality, pending intent) and
  exposes iterator helpers plus queue affinity metrics. Legacy fallbacks log once when invoked.
- `ScriptedBehavior` routes all decision logic (`decide`, `_satisfy_needs`, `_maybe_chat`,
  `_avoid_rivals`, `_rivals_in_queue`, `should_avoid`) through the DTO façade; tests guard the
  DTO-only path (`tests/policy/test_scripted_behavior_dto.py`).
- `BehaviorBridge.decide_agent` requires a DTO view; policy runtime already guarantees this after Stage 3A.
  TODO marker remains on `_find_object_of_type` until DTOs export object rosters (Stage 5).
- Remaining legacy reads: scripted CLI adapters (`policy/scripted.py`) and scenario seed helpers still
  touch `loop.world.agents` by design; they will migrate once DTO-capable capture tooling lands.
