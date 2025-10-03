# Lifecycle Flow Mapping (Current State)

## 1. Spawn & Initialisation
- **Config bootstrap**: `WorldState.__post_init__` (`src/townlet/world/grid.py:228`) loads objects/affordances and initial agents if provided in config.
- **Console spawn**: `spawn` command routes to `_console_spawn_agent` which creates `AgentSnapshot`, initialises needs, wallet, assigns job via `_sync_agent_spawn` (`grid.py:672`).
- **Home routing**: Each agent snapshot records `home_position`; spawn and respawn paths populate it so nightly resets can return agents home (`grid.py:709`).
- **Employment context**: `_sync_agent_spawn` hydrates `_employment_state` with defaults (lateness counters, wages, attendance) and allocates embedding slots.
- **Current behaviour**: `LifecycleManager` now schedules respawns using the configurable
  `lifecycle.respawn_delay_ticks`. Agents removed by lifecycle evaluation are reintroduced after
  the delay with default needs, a fresh agent identifier (tracked via `origin_agent_id`), and reset employment state.

## 2. Employment Queue & Shift Cycle
- **Queue manager**: `QueueManager` tracks object reservations and request access (stay in queue until granted) (`grid.py` interactions around apply_actions/resolve_affordances).
- **Fairness tuning**: rotation/ghost-step metrics driven by `queue_fairness.*`; see `docs/ops/QUEUE_FAIRNESS_TUNING.md` for parameter rationale.
- **Employment loop**: `_employment_*` helpers drive shift states (idle, prepare, active) and update context each tick (`grid.py:2057-2400`).
- **Manual exits**: lifecycle queues exits via `_employment_enqueue_exit`; console `employment_exit` adds to `_employment_manual_exits` (admin approval).
- **LifecycleManager ties**: `_evaluate_employment` enforces exit caps/review windows and emits `employment_exit_processed` events (`lifecycle/manager.py:40-114`).
- **Current behaviour**: Terminated agents are removed from the world map, queues, and ledgers;
  respawn tickets are queued for later re-entry.

## 3. Affordance Execution
- **Queue → affordance start**: `apply_actions` handles `request`, `start`, `release`; `_start_affordance` checks reservation, preconditions, runs hooks, schedules effects (`grid.py:1020-1859`).
- **Effects**: `_apply_affordance_effects` modifies needs/wallet based on spec; hooks (default + plugin) handle stock, social outputs (`grid.py:1734`, `world/hooks/default.py`).
- **Rivalry telemetry**: conflict snapshots reflect `world.register_rivalry_conflict` events and drive stability alerts (see `tests/test_conflict_scenarios.py`).
- **Running affordances** resolved each tick in `resolve_affordances` (decrement duration, apply effects, release queues).
- **Gaps**: TODO to update agent snapshot post actions; limited effect coverage (manifests incomplete for social/energy).

## 4. Needs Decay & Reward Loop
- **Needs decay**: `_apply_need_decay` (grid) reduces needs per tick; interplay with reward engine (lack context? confirm). Rewards computed after lifecycle evaluation (`rewards/engine.py`).
- **Reward guardrails**: handles punishments, wages, social bonuses, clipping; uses employment context for punctuality/wage data.
- **Gaps**: Some documented reward taps still missing (e.g., social for meals? watchers?). Need cross-check design.

## 5. Lifecycle Evaluation & Termination
- **LifecycleManager.evaluate** runs each tick, calling `_evaluate_employment` and checking hunger threshold for mortality; returns `terminated` map (`lifecycle/manager.py:23-57`).
- **Downstream usage**: SimulationLoop passes `terminated` to rewards, policy, and stability monitor (`core/sim_loop.py:177-219`). After post-step metrics, `LifecycleManager.finalize` removes agents and queues respawns.
- **Events**: Employment exits emit events; agent removal emits `agent_removed` and respawns trigger `agent_respawn`.
- **Remaining gaps**:
  - Respawns still reuse existing agent IDs; consider unique identity refresh per conceptual design.
  - No dedicated death telemetry audit beyond the removal event.
  - TODOs referenced in design (health resets, shelter return) remain open.

## 6. Stability & Promotion Interaction
- **StabilityMonitor.track** consumes rewards/metrics; counts alerts, updates promotion window states.
- **Promotion**: Snapshot includes pass streak, required passes; PromotionManager (core loop) still manual. Automation arriving in LR3.

## Key Gaps Identified
1. **Affordance side-effects**: TODO to update agent snapshots post-actions; limited coverage of social/economic effects. Option commitment window missing.
2. **Reward/needs alignment**: reward taps in design (punctuality, social) partially implemented; need validation.
3. **Telemetry & events**: No explicit death/removal telemetry; promotion automation still manual.

## Next Steps (per LR1.1 plan)
- Design agent removal & respawn flow, aligned with config.
- Decide on whether terminated agents respawn automatically or require console action.
- Extend LifecycleManager to emit removal events and coordinate with WorldState to despawn.
- Implement telemetry updates (death events, respawn logs).
