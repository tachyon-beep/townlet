# WorldState Refactor Tracking (Phase 0)

## Baseline Assets
- Telemetry snapshot & stream: `audit/baselines/worldstate_phase0/snapshots/`
- Console command baselines:
  - Router commands (`employment_exit review/approve`): `audit/baselines/worldstate_phase0/console/router_results.json`
  - Queued world commands (`force_chat`): `audit/baselines/worldstate_phase0/console/queued_results.json`
- Guardrail test subset: `pytest tests/test_world_* tests/test_console_* tests/test_telemetry_*` (or `tox -e refactor`).
- Added debug timings
  - `world.resolve_affordances` emits `world.resolve_affordances` duration + queue depth when `DEBUG` logging is enabled.
  - `employment.enqueue_exit` logs queue depth deltas for pending exits.

## Module Ownership Map (Target)
- `world/employment.py` → queue state, lateness tracking, exit flows.
- `world/affordances.py` → running affordances, hook dispatch, agent state mutations.
- `world/relationships.py` → relationship/rivalry updates consumed by telemetry & stability.
- `world/console_bridge.py` → console handler registration + admin gating.

## TODO Hotspots To Resolve
- `src/townlet/world/grid.py:1297` — update agent snapshot based on affordance outcomes.
- `src/townlet/world/grid.py:1329` — integrate affordance hooks during resolution.
- Employment queue helpers share mutable state across methods; ensure new module owns `_employment_*` fields.

## Coordination Notes
- Flag any concurrent work touching `src/townlet/world/grid.py` in PR descriptions and link back to this document.
- Prefer staging refactor changes behind short-lived feature branches to keep rebases manageable.
- Capture before/after telemetry snapshots when extracting subsystems to detect behavioural drift early.

_Last updated: Phase 0 completion._

## Phase 1 – Discovery (Baseline Mapping)

### WorldState Responsibility Map

| Segment | Line Range | Primary Methods | Future Owner |
| --- | --- | --- | --- |
| Console ingress & admin handlers | 290–1054 | `apply_console`, `_register_default_console_handlers`, `_console_*` | ConsoleBridge |
| Affordance lifecycle & hooks | 420–2076 | `register_affordance_hook`, `apply_actions`, `resolve_affordances`, `_start_affordance`, `_dispatch_affordance_hooks`, `_apply_affordance_effects`, `affordance_manifest_metadata` | AffordanceRuntime |
| Telemetry/export utilities | 1397–1526, 2022–2026 | `snapshot`, `local_view`, `drain_events`, `agent_context`, `active_reservations`, `_emit_event` | Shared (Telemetry bridge) |
| Relationships & rivalry | 1534–1856 | `_record_queue_conflict`, `rivalry_snapshot`, `relationships_snapshot`, `update_relationship`, `record_chat_success/failure` | RelationshipManager |
| Employment & job lifecycle | 2167–2686 | `_assign_jobs_to_agents`, `_employment_*`, `employment_queue_snapshot`, `employment_request_manual_exit` | EmploymentEngine |
| Economy & nightly upkeep | 2090–2711 | `_apply_need_decay`, `apply_nightly_reset`, `_update_basket_metrics`, `_restock_economy` | Core loop / Economy service |

### Proposed Module Interfaces (Draft)

- **EmploymentEngine**
  - `enqueue_exit(agent_id, tick)`/`remove_from_queue(agent_id)`
  - `queue_snapshot()` returning current pending/metrics
  - `update_for_tick(world_state, tick)` to advance lateness, shift transitions
  - `manual_exit_request(agent_id, tick)` and `defer_exit(agent_id)` helpers

- **AffordanceRuntime**
  - `register(spec)` to ingest affordance definitions
  - `apply_actions(agent_actions, tick)` producing success flags
  - `resolve(tick)` to tick running affordances + emit events/hooks
  - `clear_hooks()/register_hook` surfaces feeding into hook registry

- **RelationshipManager**
  - `record_queue_conflict(...)`, `update_relationship(...)`
  - `snapshot()` returning rivalry + relationship structures for telemetry
  - `decay(tick)` to manage periodic decay (currently `_decay_*` helpers)

- **ConsoleBridge**
  - `register_default_handlers()` and role-aware handler wiring
  - `dispatch(command)` returning `ConsoleCommandResult`
  - `record_result(result)` & idempotency cache management

Each module should receive a lightweight context rather than holding direct references to the entire `WorldState`.

### Shared Context & Utilities

Cross-cutting services identified during the audit:

- **Event emission**: `_emit_event` used by employment and affordance flows.
- **Randomness & RNG streams**: `attach_rng`, `set_rng_state`, `queue_manager` operations.
- **Queue manager access**: reservation sync, fairness metrics.
- **Telemetry hooks**: promotion/stability updates, console result history, n-ary snapshots.
- **Config slices**: employment settings, affordance manifests, economy knobs.

Proposed context object shape (working name `WorldRuntimeContext`):

```python
@dataclass
class WorldRuntimeContext:
    config: SimulationConfig
    queue_manager: QueueManager
    emit_event: Callable[[str, dict[str, object]], None]
    rng: random.Random
    telemetry: TelemetryPublisher  # or a thin interface for metrics updates
    promotion: PromotionManager | None
```

Module APIs should depend on this context plus the agent/object collections they manipulate (`agents`, `objects`, `affordances`). The goal is to keep data ownership explicit while avoiding circular imports when components become standalone modules.

## Phase 2 – Employment Extraction (In Progress)

- Introduced `townlet/world/employment.py` with `EmploymentEngine` owning employment state (context map, exit queue, manual exit set).
- `WorldState` instantiates the engine and delegates queue-oriented helpers (`_employment_enqueue_exit`, `employment_queue_snapshot`, `employment_request_manual_exit`, `employment_defer_exit`). Method signatures remain unchanged.
- The legacy `_employment_*` dictionaries now proxy to the engine to keep behaviour stable pending full extraction of shift logic.
- Baseline telemetry/console artefacts re-captured (`audit/baselines/worldstate_phase0_current/`) differ only by timing variability; guardrail and employment-focused test suites pass.
