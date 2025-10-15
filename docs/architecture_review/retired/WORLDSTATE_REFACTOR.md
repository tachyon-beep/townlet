# WorldState Refactor Tracking (Phase 0)

## Phase 3 Update (2025-04-12)

- Introduced runtime-checkable protocols for the agent registry, relationship service, and employment façade (`townlet.world.agents.interfaces`). `WorldContext` now exposes the composed services so downstream layers can depend on the interfaces.
- Extracted `AffordanceEnvironment` under `world/affordances/` and rewired the runtime/service stack to consume the environment instead of raw `WorldState` attributes. Hook payloads now receive both the environment and an optional world reference for backwards compatibility.
- `AgentRegistry`, `RelationshipService`, and affordance context delegation gained focused unit coverage (`tests/test_agents_services.py`). Behaviour/queue/console integration suites were refreshed to rely on public helpers (`relationship_tie`, `get_rivalry_ledger`).
- The demo timeline and rivalry behaviour tests no longer reach into `_relationship_ledgers`/`_rivalry_ledgers`, reducing direct coupling on internal state while preserving existing assertions.

## Phase 4–5 Update (2025-10-18)

- Added `WorldRuntimeAdapter` (`townlet.world.core.runtime_adapter`) to expose read-only accessors for agents, objects, queue metrics, relationships, and embedding allocator state. `SimulationLoop.world_adapter` caches the façade for reuse by policy, telemetry, and snapshot codepaths.
- Observation builders and helper modules now coerce incoming world references through `ensure_world_adapter`, enabling adapter/`WorldState` parity tests (`tests/test_observation_builder_parity.py`).
- Telemetry publisher and snapshot capture lean on the adapter for queue, relationship, and personality metrics, reducing direct `WorldState` coupling while retaining raw access for specialised exports (economy/employment). Adapter smoke tests cover telemetry publishing (`tests/test_telemetry_adapter_smoke.py`).
- Documentation and migration notes updated to reflect the adapter boundary; future subsystem extractions should depend on the façade rather than the concrete grid.
- Nightly upkeep moved into `townlet.world.agents.nightly_reset.NightlyResetService`, which `WorldState` wires during `__post_init__` and `WorldContext` now exposes via `apply_nightly_reset()`. This keeps queue release, need refill, and employment reset logic isolated from the grid orchestrator.
- Employment helpers route through the expanded `townlet.world.agents.employment.EmploymentService`; `WorldRuntimeAdapter` and nightly reset alike depend on the façade for context lookups and shift lifecycle operations.
- Dedicated delegation tests cover nightly reset and employment service calls (`tests/test_world_nightly_reset.py`, `tests/test_world_employment_delegation.py`).
- Economy/utility upkeep now lives in `townlet.world.economy.EconomyService`, trimming basket/price/outage logic out of `WorldState` while keeping public methods intact (`tests/test_world_economy_delegation.py`).
- Perturbation scheduling (`src/townlet/scheduler/perturbations.py`) delegates through `townlet.world.perturbations.PerturbationService`, which reuses the economy façade for price spikes/outages and centralises arranged meet moves (`tests/test_world_perturbation_service.py`).
- Legacy `WorldState` helpers (`set_price_target`, `apply_price_spike`, `apply_arranged_meet`, `utility_snapshot`, etc.) now proxy directly to the new services. Callers are encouraged to resolve `world.economy_service` / `world.perturbation_service` to avoid future deprecation churn.
- Console handlers, telemetry publisher, and perturbation scheduler were updated to consume the facades; downstream extensions should follow the same pattern when introducing new price/outage behaviour.
- Lifecycle orchestration has a dedicated `townlet.world.agents.lifecycle.LifecycleService`; `WorldState` delegates spawn/teleport/remove/kill/respawn, and `WorldContext` exposes the façade for downstream consumers. Console spawn validation and lifecycle-focused tests now rely on the service instead of private grid helpers.

### Migration notes – employment & lifecycle consumers

- Employment-oriented code (telemetry exporters, console manual exits, observation builders) should import from `townlet.world.agents.employment` rather than reaching into `EmploymentRuntime`. The `WorldState` wrappers remain but are strictly delegations.
- Nightly reset and employment shift helpers are available via `WorldContext.nightly_reset_service` / `WorldContext.employment_service`, ensuring adapters and tests can request the façade without touching grid internals.
- Lifecycle mechanics (spawn, teleport, remove, respawn, reservation sync) now live in `townlet.world.agents.lifecycle.LifecycleService`; `WorldState` delegates public helpers to the service and exposes it via `WorldContext.lifecycle_service`. Console handlers, lifecycle manager, and telemetry tests use the façade to avoid private-grid coupling.

## Phase 6 Validation (2025-10-24)

- Executed `pytest -q` (533 passed / 1 skipped) after routing observation and telemetry consumers through the adapter; log archived at `tmp/wp-c/phase4_validation.txt`.
- `ruff check src tests` continues to surface pre-existing style violations in legacy console/config modules; Phase 4 additions now lint clean (see targeted check summary in the same log).
- `mypy src` still fails due to historical typing gaps (≈531 errors). Adapter modules remain type-hint complete; remediation is deferred to WP-D typing follow-up.
- `tox -e docstrings` maintains the callable coverage guard (45.18 %, minimum 40 %).
- Captured a 50-tick smoke run via `python scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 50 --telemetry-path tmp/wp-c/phase6_smoke_telemetry.jsonl`; telemetry diff matches Phase 0 baselines.

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

## Observation Contract Snapshot (2025-10-03)
- Builder outputs use `map`, `features`, `metadata` keys across all variants; policy pipelines (`policy.runner.flush_transitions`) rely on those exact keys.
- `metadata.feature_names` currently exposes 81 entries shared across variants, including critical channels `need_hunger`, `need_hygiene`, `need_energy`, `wallet`, `time_sin`, `time_cos`, and `ctx_reset_flag`.
- Map tensor expectations:
  - **Hybrid**: `(4, 11, 11)` with channels `self`, `agents`, `objects`, `reservations`.
  - **Full**: `(6, 11, 11)` adding `path_dx`, `path_dy` channels.
  - **Compact**: empty spatial tensor (`(0, 0, 0)`), relies solely on the feature vector.
- Social snippet aggregates, landmark slices, and personality overlays are carried via `metadata.social_context`, `metadata.landmark_slices`, and `metadata.feature_names`; tests assert these keys survive refactors.
- Fixture regeneration (`tests/data/observations/baseline_*.npz`) uses `scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 200 --telemetry-path tmp/telemetry_baseline.json` to seed deterministic inputs prior to encoding.
- Observation helper logic now lives in `townlet.world.observations`; `WorldState.local_view()/agent_context()` are thin shims delegating to those modules so downstream systems can consume the same APIs without coupling to private fields.
- Legacy `WorldState.local_view`/`agent_context` shim methods were removed in favour of direct imports from `townlet.world.observations`; downstream callers should migrate to the helper module before Milestone M4.

## RNG & Snapshot Semantics (2025-10-03)
- `WorldState.attach_rng` installs a shared `random.Random` used for nightly resets, hook scheduling, and queue conflict perturbations; `get_rng_state`/`set_rng_state` wrap the underlying `random` state.
- Simulation snapshots serialise RNG via `townlet.utils.encode_rng_state`; reload paths (`snapshots/state.py`) call `decode_rng_state` before reinjecting with `WorldState.set_rng_state`.
- Policy anneal blending, queue perturbations, and scripted actors share the same RNG; restoring the world state must therefore restore RNG before processing queued actions for deterministic replay.
- Regression coverage (`tests/test_utils_rng.py`) now asserts state round-trips on the `WorldState` object, guarding against regressions when the runtime facade assumes ownership of RNG plumbing.

## Integration Test Matrix (M3 Phase 0)
| Focus | Test suite(s) | Purpose | Notes |
| --- | --- | --- | --- |
| World runtime sequencing | `tests/test_world_queue_integration.py`, `tests/test_world_nightly_reset.py` | Validate tick ordering, queue sync, nightly resets | Must run on every runtime facade PR. |
| Observation parity | `tests/test_observation_baselines.py`, `tests/test_world_local_view.py` | Guard map/features tensors and local view contexts | Requires refreshed NPZ fixtures from Phase 0. |
| Telemetry compatibility | `tests/test_telemetry_baselines.py`, `tests/test_telemetry_stream_smoke.py`, `tests/test_observer_ui_dashboard.py` | Ensure telemetry snapshot schema and UI dashboards remain intact | UI smoke relies on `SCREEN=off` pseudo terminal; keep invocation headless. |
| Snapshot import/export | `tests/test_snapshot_manager.py`, `tests/test_snapshot_migrations.py` | Confirm RNG + world payloads survive save/restore | Already executed in Phase 0; rerun before releasing runtime facade. |
| Performance smoke | `scripts/run_simulation.py configs/scenarios/queue_conflict.yaml --ticks 500` | Capture tick throughput reference prior to refactor | Metrics stored in `benchmarks/m3_runtime_baseline.json`. |

## Runtime Facade Rollback Controls (M3 Phase 1)
- **Update (2025-??-??):** The legacy runtime toggle has been removed; `WorldRuntime` is now the sole tick implementation. CLI tools (`scripts/run_simulation.py`, `scripts/observer_ui.py`) no longer expose `--runtime`, and `TOWNLET_LEGACY_RUNTIME` is ignored.
- Telemetry continues to emit a `runtime_variant` field (currently always `"facade"`) for backwards compatibility with dashboards that track historical deployments.
- Regression protocol: run `pytest tests/test_simulation_loop_runtime.py` to ensure the facade initialises correctly and continue executing the integration suites listed above for release candidates.

### Runtime Feature Flag (Retired)
- The previous `TOWNLET_LEGACY_RUNTIME` environment switch and associated CLI overrides were decommissioned as part of Milestone M3 Phase 3 cleanup.
- Docs and automation should no longer reference the legacy path; rollback, if ever required, would be handled via git tags/branches rather than a runtime flag.

### Observation Accessor Refresh (Completed 2025-??-??)
- Observation helpers now consume the read-only `WorldState` accessors (`src/townlet/world/observation.py`), eliminating direct access to private fields.
- `tests/test_world_state_accessors.py` covers the view contracts; observation suites were updated accordingly.
- Baseline NPZ fixtures (`tests/data/observations/baseline_*.npz`) regenerated via `scripts/run_simulation.py` + `ObservationBuilder` after the migration to confirm parity.

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
| Console ingress & admin handlers | 290–1054 | `apply_console`, `_register_default_console_handlers`, `_console_*` | ConsoleService |
| Affordance lifecycle & hooks | 420–2076 | `register_affordance_hook`, `apply_actions`, `resolve_affordances`, `_start_affordance`, `_dispatch_affordance_hooks`, `_apply_affordance_effects`, `affordance_manifest_metadata` | AffordanceCoordinator |
| Telemetry/export utilities | 1397–1526, 2022–2026 | `snapshot`, `local_view`, `drain_events`, `agent_context`, `active_reservations`, `_emit_event` | Shared (Telemetry bridge) |
| Relationships & rivalry | 1534–1856 | `_record_queue_conflict`, `rivalry_snapshot`, `relationships_snapshot`, `update_relationship`, `record_chat_success/failure` | RelationshipManager |
| Employment & job lifecycle | 2167–2686 | `_assign_jobs_to_agents`, `_employment_*`, `employment_queue_snapshot`, `employment_request_manual_exit` | EmploymentCoordinator |
| Economy & nightly upkeep | 2090–2711 | `_apply_need_decay`, `apply_nightly_reset`, `_update_basket_metrics`, `_restock_economy` | Core loop / Economy service |

### Affordance Responsibility Notes (2025-10-03)

- **Resolution loop** — `src/townlet/world/grid.py:1330` owns tick-time processing: queue fairness refresh, stalled reservation ghost-steps, running affordance completion, hook dispatch, event emission, and need decay chaining.
- **Running-set maintenance** — `src/townlet/world/grid.py:2034` seeds `RunningAffordance` entries; cleanup paths live in `src/townlet/world/grid.py:1373`, `src/townlet/world/grid.py:1955`, and `src/townlet/world/grid.py:1974`, with reservation sync via `_sync_reservation` (`src/townlet/world/grid.py:1924`).
- **Hook registry** — registration/proxy lives in `src/townlet/world/grid.py:419`; dispatch context construction and cancellation semantics are in `_dispatch_affordance_hooks` (`src/townlet/world/grid.py:445`).
- **Telemetry writes** — affordance flows feed telemetry indirectly through `_emit_event` (`src/townlet/world/grid.py:1992`) and queue manager metrics consumed by `TelemetryPublisher.publish_tick`. Affordance starts/finishes push `affordance_*` events; precondition failures also enqueue console-visible telemetry via `_pending_events`.
- **Scaffolding** — `src/townlet/world/affordances.py` tracks runtime context, running-state snapshots, hook payload schema, and per-action outcomes ahead of extraction.

### Proposed Module Interfaces (Draft)

- **EmploymentCoordinator**
  - Wraps `EmploymentEngine` in `townlet/world/employment_service.py`, providing queue operations (`enqueue_exit`, `remove_from_queue`, `queue_snapshot`) and delegation hooks (`assign_jobs_to_agents`, `apply_job_state`).
  - Maintains exit counts/metrics while shielding `WorldState` from direct state management.

- **AffordanceCoordinator**
  - Wraps `DefaultAffordanceRuntime` in `townlet/world/affordance_runtime.py`, exposing `start`, `release`, `resolve`, `running_snapshot`, and `remove_agent`.
  - Allows `WorldState` to delegate affordance orchestration without exposing runtime internals, facilitating future extraction.

- **RelationshipManager**
  - `record_queue_conflict(...)`, `update_relationship(...)`
  - `snapshot()` returning rivalry + relationship structures for telemetry
  - `decay(tick)` to manage periodic decay (currently `_decay_*` helpers)

- **ConsoleService**
  - `queue_command` / `apply` façade backed by the legacy bridge
  - Handler registration with role enforcement and idempotency helpers
  - History caching (`cached_result`) and result buffering for telemetry consumers

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
- `WorldState` instantiates the engine and delegates queue-oriented helpers (`employment.enqueue_exit`, `employment_queue_snapshot`, `employment_request_manual_exit`, `employment_defer_exit`). Method signatures remain unchanged.
- The legacy `_employment_*` dictionaries now proxy to the engine to keep behaviour stable pending full extraction of shift logic.
- Baseline telemetry/console artefacts re-captured (`audit/baselines/worldstate_phase0_current/`) differ only by timing variability; guardrail and employment-focused test suites pass.

## Phase 3 – Affordance Runtime Extraction (Active)

- Added `DefaultAffordanceRuntime` (`src/townlet/world/affordances.py`) responsible for affordance lifecycle orchestration (start, release, ghost-step handling, resolution loop, hook dispatch) while retaining existing event telemetry and DEBUG timing probes.
- `WorldState.apply_actions` now delegates `start`/`release`/`blocked` affordance actions to the runtime; agent outcome bookkeeping flows through `AffordanceOutcome` to update `AgentSnapshot` state deterministically.
- `resolve_affordances` and `_handle_blocked` are thin adapters pointing to the runtime, preparing for full module extraction without altering public signatures.
- Running-state snapshots are exposed via `DefaultAffordanceRuntime.running_snapshot()` to ease telemetry/test assertions when the runtime becomes standalone.
- Runtime owns agent cleanup during `WorldState.remove_agent` and `WorldState.running_affordances_snapshot()` forwards the structured view for telemetry consumers.
- `ConsoleService` (`src/townlet/console/service.py`) now wraps the bridge implementation, letting `WorldState` delegate console orchestration without exposing handler state, while maintaining the existing audit/history semantics.
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

## Policy Runtime Surface (Phase 3)

- Behaviour/anneal logic lives in `townlet.policy.behavior_bridge.BehaviorBridge`; the simulation loop interacts through `PolicyRuntime.behavior` APIs.
- Trajectory management is handled by `townlet.policy.trajectory_service.TrajectoryService`, shared between `PolicyRuntime` and `PolicyTrainingOrchestrator`.
- PPO/BC/anneal tooling should use `townlet.policy.training_orchestrator.PolicyTrainingOrchestrator`; the legacy `TrainingHarness` remains as a compatibility alias but is slated for removal once downstream callers migrate.
- Public surfaces now expose `transitions`/`trajectory` properties; direct access to private `_transitions` buffers has been removed. Update tests and integrations accordingly.
