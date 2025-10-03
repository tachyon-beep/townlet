# WorldState Refactor Tracking (Phase 0)

## Baseline Assets
- Telemetry snapshot & stream: `audit/baselines/worldstate_phase0/snapshots/`
- Console command baselines:
  - Router commands (`employment_exit review/approve`): `audit/baselines/worldstate_phase0/console/router_results.json`
  - Queued world commands (`force_chat`): `audit/baselines/worldstate_phase0/console/queued_results.json`
- Phase 3 affordance baseline (poc_hybrid):
  - Stream (120 ticks, seeded agents, queued chat success): `audit/baselines/worldstate_phase3/snapshots/telemetry_stream.jsonl`
  - Snapshot payload: `audit/baselines/worldstate_phase3/snapshots/telemetry_snapshot.json`
  - Console traces: `audit/baselines/worldstate_phase3/console/{router_results.json,queued_results.json}`
- Phase 4 affordance baseline (post-runtime extraction):
  - Stream/snapshot/console: `audit/baselines/worldstate_phase4/{snapshots,console}/`
  - World snapshot for structural diffs: `audit/baselines/worldstate_phase4/world_snapshot.json`
- Guardrail test subset: `pytest tests/test_world_* tests/test_console_* tests/test_telemetry_*` (or `tox -e refactor`).
- Guardrail status (2025-10-03):
  - `pytest tests/test_affordance_* tests/test_world_*` ✅
  - `tox -e refactor` ✅ (allowlisted external `pytest`, explicit world/console/telemetry file list).
- Added debug timings
  - `world.resolve_affordances` now logs start/end envelopes with queue deltas when `DEBUG` logging is enabled.
  - `_dispatch_affordance_hooks` records per-hook and per-handler duration to surface drift once AffordanceRuntime lands.
  - `employment.enqueue_exit` logs queue depth deltas for pending exits.

## Module Ownership Map (Target)
- `world/employment.py` → queue state, lateness tracking, exit flows.
- `world/affordances.py` → running affordances, hook dispatch, agent state mutations.
- `world/relationships.py` → relationship/rivalry updates consumed by telemetry & stability.
- `world/console_bridge.py` → console handler registration + admin gating.

## TODO Hotspots To Resolve
- ✅ `src/townlet/world/grid.py:1297` — agent snapshot outcomes now flow through `apply_affordance_outcome` (see `src/townlet/world/affordances.py`).
- ✅ `src/townlet/world/grid.py:1329` — hook dispatch now builds structured payloads via `build_hook_payload`.
- Employment queue helpers share mutable state across methods; ensure new module owns `_employment_*` fields.

## Coordination Notes
- Flag any concurrent work touching `src/townlet/world/grid.py` in PR descriptions and link back to this document.
- Prefer staging refactor changes behind short-lived feature branches to keep rebases manageable.
- Capture before/after telemetry snapshots when extracting subsystems to detect behavioural drift early.
- Temporary DEBUG instrumentation has landed in `resolve_affordances`/`_dispatch_affordance_hooks`; coordinate before altering those code paths so timing probes remain consistent through Phase 3.
- October 2025 update: Observation builders now construct per-tick caches (agent/object/reservation lookup) so `local_view` scopes run in O(radius²) instead of O(n_agents). Compact variant metadata carries `local_summary` totals for downstream debug tooling.

_Last updated: Phase 0 instrumentation refresh (2025-10-03)._

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

### Affordance Responsibility Notes (2025-10-03)

- **Resolution loop** — `src/townlet/world/grid.py:1330` owns tick-time processing: queue fairness refresh, stalled reservation ghost-steps, running affordance completion, hook dispatch, event emission, and need decay chaining.
- **Running-set maintenance** — `src/townlet/world/grid.py:2034` seeds `RunningAffordance` entries; cleanup paths live in `src/townlet/world/grid.py:1373`, `src/townlet/world/grid.py:1955`, and `src/townlet/world/grid.py:1974`, with reservation sync via `_sync_reservation` (`src/townlet/world/grid.py:1924`).
- **Hook registry** — registration/proxy lives in `src/townlet/world/grid.py:419`; dispatch context construction and cancellation semantics are in `_dispatch_affordance_hooks` (`src/townlet/world/grid.py:445`).
- **Telemetry writes** — affordance flows feed telemetry indirectly through `_emit_event` (`src/townlet/world/grid.py:1992`) and queue manager metrics consumed by `TelemetryPublisher.publish_tick`. Affordance starts/finishes push `affordance_*` events; precondition failures also enqueue console-visible telemetry via `_pending_events`.
- **Scaffolding** — `src/townlet/world/affordances.py` tracks runtime context, running-state snapshots, hook payload schema, and per-action outcomes ahead of extraction.

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

### AffordanceRuntime API Draft

Target module: `src/townlet/world/affordances.py`

```python
@dataclass(slots=True)
class AffordanceRuntimeConfig:
    rng: random.Random
    queue_manager: QueueManager
    emit_event: Callable[[str, dict[str, object]], None]
    register_hook: Callable[[str, Callable[[dict[str, object]], None]], None]
    telemetry: TelemetryPublisher  # narrow to the metrics we touch during Phase 3


@dataclass(slots=True)
class RunningAffordanceState:
    agent_id: str
    object_id: str
    affordance_id: str
    duration_remaining: int
    effects: dict[str, float]


class AffordanceRuntime(Protocol):
    def bind(self, *, world_state: "WorldState", config: AffordanceRuntimeConfig) -> None: ...
    def apply_actions(self, actions: Mapping[str, dict[str, object]], *, tick: int) -> None: ...
    def resolve(self, *, tick: int) -> None: ...
    def running_snapshot(self) -> dict[str, RunningAffordanceState]: ...
    def clear(self) -> None: ...
```

Key expectations:
- `bind` wires shared collections (`agents`, `objects`, `affordances`) and shared services (queue manager, event emitter). Keeps runtime pure-ish by avoiding direct constructor coupling to `WorldState`.
- `apply_actions` consumes the per-agent affordance directives currently handled inside `WorldState.apply_actions`; it should return success/failure for action completion (feed into agent snapshots and policy feedback).
- `resolve` executes what `WorldState.resolve_affordances` does today: ticking `QueueManager`, finishing running affordances, dispatching hooks, emitting telemetry-ready events, syncing reservations.
- `running_snapshot` surfaces deterministic state for telemetry/tests without leaking internal dict references.
- `clear` resets runtime for snapshot restore / world reset flows.

### Data Contracts

Hook payloads today are loosely shaped via `_dispatch_affordance_hooks` (`src/townlet/world/grid.py:445`). Explicit types help downstream:

```python
class HookStage(Enum):
    BEFORE = "before"
    AFTER = "after"
    FAIL = "fail"


class HookPayload(TypedDict, total=False):
    stage: Literal["before", "after", "fail"]
    hook: str
    tick: int
    agent_id: str
    object_id: str
    affordance_id: str
    effects: dict[str, float]
    reason: str
    condition: str
    context: dict[str, object]


class AgentAffordanceSnapshot(TypedDict):
    agent_id: str
    needs: dict[str, float]
    wallet: float
    inventory: dict[str, int]
    on_shift: bool
    job_id: str | None
```

`HookPayload` variants align with current call sites: `before` passes base metadata, `after` optionally includes `effects`, and `fail` attaches `reason`/`condition`/`context`. The runtime extraction should normalise these payloads before invoking hook handlers and telemetry.

### Hook Semantics Inventory

| Hook | Stage(s) | Required context keys | Side-effects today | Reference |
| --- | --- | --- | --- | --- |
| `on_attempt_shower` | `before` | `world`, `agent_id`, `object_id`, `spec` | Cancels when shower offline, increments `showers_started`, mutates store stock | `src/townlet/world/hooks/default.py:31` |
| `on_finish_shower` | `after` | `world`, `agent_id`, `object_id` | Increments `showers_taken`, emits `shower_complete` | `src/townlet/world/hooks/default.py:61` |
| `on_no_power` | `fail` (via `_abort_affordance`) | `world`, `object_id` | Sets `power_on=0`, emits `shower_power_outage` | `src/townlet/world/hooks/default.py:80` |
| `on_attempt_eat` | `before` | `world`, `agent_id`, `object_id`, `spec` | Validates meal stock & wallet, decrements stock, charges agent, tracks participants | `src/townlet/world/hooks/default.py:96` |
| `on_finish_eat` | `after` | `world`, `agent_id`, `object_id` | Applies relationship deltas, emits `shared_meal` | `src/townlet/world/hooks/default.py:136` |
| `on_attempt_cook` | `before` | `world`, `agent_id`, `object_id`, `spec` | Charges ingredients cost, ensures stock, may cancel with `reason` | `src/townlet/world/hooks/default.py:165` |
| `on_finish_cook` | `after` | `world`, `agent_id`, `object_id` | Increments cooked meals & store stock | `src/townlet/world/hooks/default.py:193` |
| `on_cook_fail` | `fail` | `world`, `object_id` | Normalises raw ingredients stock on failure | `src/townlet/world/hooks/default.py:207` |
| `on_attempt_sleep` | `before` | `world`, `agent_id`, `object_id`, `spec` | Manages sleep slot capacity, cancels when unavailable, tracks attempts | `src/townlet/world/hooks/default.py:217` |
| `on_finish_sleep` | `after` | `world`, `agent_id`, `object_id` | Restores sleep slots, increments `sleep_sessions`, emits `sleep_complete` | `src/townlet/world/hooks/default.py:239` |

Test coverage expectations:
- `tests/test_affordance_hooks.py:16` asserts `before`/`after` hooks fire once per affordance lifecycle.
- `tests/test_affordance_hooks.py:40` verifies `fail` hooks receive `reason` context and do not double-fire on duplicate releases.
- `tests/test_affordance_hooks.py:68` ensures precondition failures enqueue `affordance_precondition_fail` events and respect hook-driven cancellations.

These invariants should carry forward into the runtime extraction; introduce regression tests for hook payload schema once the TypedDicts land.

## Phase 2 – Employment Extraction (In Progress)

- Introduced `townlet/world/employment.py` with `EmploymentEngine` owning employment state (context map, exit queue, manual exit set).
- `WorldState` instantiates the engine and delegates queue-oriented helpers (`_employment_enqueue_exit`, `employment_queue_snapshot`, `employment_request_manual_exit`, `employment_defer_exit`). Method signatures remain unchanged.
- The legacy `_employment_*` dictionaries now proxy to the engine to keep behaviour stable pending full extraction of shift logic.
- Baseline telemetry/console artefacts re-captured (`audit/baselines/worldstate_phase0_current/`) differ only by timing variability; guardrail and employment-focused test suites pass.

## Phase 3 – Affordance Runtime Extraction (Active)

- Added `DefaultAffordanceRuntime` (`src/townlet/world/affordances.py`) responsible for affordance lifecycle orchestration (start, release, ghost-step handling, resolution loop, hook dispatch) while retaining existing event telemetry and DEBUG timing probes.
- `WorldState.apply_actions` now delegates `start`/`release`/`blocked` affordance actions to the runtime; agent outcome bookkeeping flows through `AffordanceOutcome` to update `AgentSnapshot` state deterministically.
- `resolve_affordances` and `_handle_blocked` are thin adapters pointing to the runtime, preparing for full module extraction without altering public signatures.
- Running-state snapshots are exposed via `DefaultAffordanceRuntime.running_snapshot()` to ease telemetry/test assertions when the runtime becomes standalone.
- Runtime owns agent cleanup during `WorldState.remove_agent` and `WorldState.running_affordances_snapshot()` forwards the structured view for telemetry consumers.
- `ConsoleBridge` (`src/townlet/world/console_bridge.py`) now encapsulates handler registration/history, letting `WorldState` delegate console orchestration instead of storing handler state.
- Queue conflict/rivalry bookkeeping lives inside `QueueConflictTracker` (`src/townlet/world/queue_conflict.py`), keeping rivalry/chat event handling separate from core world state.
- `SimulationLoop` accepts an optional `affordance_runtime_factory`, enabling tests to inject custom runtimes while the default factory still produces `DefaultAffordanceRuntime` instances.

## Phase 4 – Verification Snapshot (2025-10-03)

- **Unit tests**: `tests/test_affordance_hooks.py` extended to cover runtime start/release, snapshot structure, agent removal cleanup, and capped `_affordance_outcomes` metadata trail (8 tests total).
- **Guardrails**: `pytest tests/test_affordance_hooks.py` + `tox -e refactor` pass on the refactored runtime.
- **Telemetry parity**: 120-tick capture under `configs/examples/poc_hybrid.yaml` matches `audit/baselines/worldstate_phase3` stream byte-for-byte; snapshot diff limited to `health.tick_duration_ms` (expected runtime variance). Console artefacts only differ in command ids used for this run.
- **Instrumentation sanity**: DEBUG logging still emits `world.resolve_affordances.start/end` entries and per-hook timings when `townlet.world.grid` logging is set to DEBUG.
- **Fail-fast guards**: `DefaultAffordanceRuntime` now asserts object/spec presence during `start` and `release`, ensuring missing affordances surface immediately in pre-production.

## Phase 5 – Documentation & Handover Checklist

- **Developer guidance**: `docs/design/AFFORDANCE_RUNTIME.md` captures runtime responsibilities, extension points (hooks, outcomes, snapshots), and expectations for future extractions.
- **Runtime surfaces**: `WorldState.affordance_runtime` and `WorldState.running_affordances_snapshot()` documented for telemetry/testing consumers; `tests/test_affordance_hooks.py` exercises the public-facing helpers.
- **Follow-up backlog**:
  - Evaluate snapshot export integration once persistence shifts to the runtime (tracked in `TODO-AFF-001`).
  - Decide on permanent home for DEBUG timing probes before production rollout (`TODO-AFF-002`).
  - Consider making `DefaultAffordanceRuntime` injectable for specialised scenarios/tests (`TODO-AFF-003`).
- **Handoff**: Update PR/issue templates to mention new runtime entry points and remind collaborators to coordinate when touching `world/affordances.py` or `WorldState.affordance_runtime`.
