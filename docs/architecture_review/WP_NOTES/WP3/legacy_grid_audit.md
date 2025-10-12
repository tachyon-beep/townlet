# Legacy Surface Audit — World/Grid & Observations (2025-10-11)

## Scope
The sweep covers the remaining legacy pathways that still bypass the modular
services introduced in WP1‒WP3:

- `src/townlet/world/grid.py`
- `src/townlet/world/hooks/default.py` and `townlet/world/hooks/__init__.py`
- `src/townlet/world/observations/context.py` and helper shims
- `src/townlet/world/observe.py` (adapter entry points)
- `src/townlet/adapters/world_default.py`
- `src/townlet/telemetry/publisher.py` (legacy ingestion guards)

The goal is to catalogue the exact legacy behaviours that must be removed or
refactored so the runtime depends exclusively on modular `WorldContext`
systems, DTO observation envelopes, and dispatcher-driven telemetry.

## Findings

### 1. `world/grid.py`
- The file still defines the monolithic `WorldState` dataclass with embedded
  registries, reservation tracking, RNG caches, employment runtime wiring, and
  console history. Many helpers (`_apply_need_decay`, `_apply_affordance_effects`,
  `_recent_meal_participants`, `_job_keys`, `_pending_events`) duplicate logic now
  owned by modular systems (`world.systems.*`).  
  ↳ See lines ~85–540, ~880–1330.
  - **Update 2025-10-11:** Job roster is now owned by the employment engine;
    `_job_keys` has been removed from `WorldState`, lifecycle respawns call into
    the employment service for assignments, and DTO inventories initialise wage
    counters via the service facade.
  - **Update 2025-10-11:** Legacy employment helpers (`_apply_job_state`,
    `_employment_context_*`, shift helper wrappers) were removed; the modular
    step falls back to the coordinator directly when services are absent, and
    observation builders consume context data via `EmploymentService`.
- Console plumbing persists (`ConsoleService`, `_queue_console_command`),
  despite the simulation loop now routing console inputs through the
  dispatcher.  
  ↳ Lines ~160–320, ~1380–1500.
- Employment fallback code (`assign_jobs_to_agents`, `_employment_runtime`,
  `apply_job_rewards`) still mutates agents directly instead of relying on
  `EmploymentCoordinator` and DTO events.  
  ↳ Lines ~360–520, ~1010–1130.
- Event emission helpers still maintain a legacy `_pending_events` cache and
  write combined payloads (`{"event": event, **payload}`) intended for the old
  telemetry surface.  
  ↳ Lines ~1210–1340.
- Affordance manifest loading rewrites `objects`, `affordances`, and
  `store_stock` inside `WorldState`; modular systems already expose register
  primitives.  
  ↳ Lines ~1340–1395.
  - **Update 2025-10-11:** Manifest loader now resets the object registry via
    `_reset_object_registry` and routes stock updates through
    `register_object(..., stock=...)`, keeping `store_stock` and spatial indices
    in sync with the lifecycle service.

### 2. `world/hooks/default.py`
- **Resolved 2025-10-11:** Built-in hooks consume `HookPayload.environment`
  services (queue manager, relationship service, emitter) rather than mutating
  `WorldState` directly. Store stock and meal participant caches now flow
  through the environment, and events are emitted via the dispatcher.
- Hook registry still requires `world.register_affordance_hook`, keeping the
  import-time registration contract in place for third-party modules.

### 3. Observation helpers
- **Resolved 2025-10-11:** `observations/context.py` now requires a
  DTO-capable adapter (no `_maybe_call` fallback); tests patch DTO context when
  necessary.  
  ↳ Lines ~12–55.
- **Resolved 2025-10-11:** `observe.py.local_view` consumes immutable snapshots
  (`adapter.objects_snapshot()`) and reservation sets, eliminating direct access
  to mutable world structures. Snapshot export follows the same path.  
  ↳ Lines ~20–120.
- Remaining: tighten DTO-only enforcement by removing `ensure_world_adapter`
  compatibility with raw `WorldState` once WP3B hook migration completes.

### 4. Adapters
- `adapters/world_default.py` still exposes `world_state`, `queue_manager`, and
  other internal surfaces rather than forwarding to discrete services.  
  ↳ Lines ~40–210.
- Console helpers on the adapter still surface the internal console bridge
  rather than a dispatcher-friendly façade.

### 5. Telemetry Publisher
- `_ingest_health_metrics` and `_ingest_failure_snapshot` accept legacy alias
  fields (`worker_alive`, `tick_duration_ms`, `aliases`) and coerce them into
  the structured schema.  
  ↳ Lines ~780–880.
- Console history flushing previously relied on `_console_results_history`; the
  publisher now derives results from dispatcher events, but history retention
  still needs validation once transports migrate fully.
- `emit_event` paths allow bare dict payloads lacking DTO `global_context`
  without surfacing errors.

## Risks
- Legacy mutations bypass the modular systems, making it difficult to guarantee
  deterministic DTO observations and telemetry parity.
- Console and employment fallbacks undermine WP3’s goal of an event-only loop.
- Observation helpers mask missing DTO data, inviting regressions if the legacy
  surfaces are removed abruptly.
- Telemetry compatibility logic reintroduces schema drift and makes it harder
  to reason about transport payloads.

## Recommendations
1. **World grid extraction:** Split `WorldState` into thin façades that delegate
   to modular services (`QueueManager`, `AffordanceRuntimeService`, etc.) and
   delete the internal caches in favour of runtime adapters. This likely
   requires a staged removal plan (TBD “WP4” or WP3 follow-up).
2. **Hook redesign:** Replace the hook module with dispatcher-first handlers or
   precondition callbacks that operate on DTO snapshots, eliminating direct
   mutation of `WorldState`.
3. **Observation cleanup:** Promote adapter-only access (fail loudly when no
   adapter) and move employment context helpers into modular services.
4. **Adapter tightening:** Reduce `DefaultWorldAdapter` to the port contract
   defined in WP1 (reset/tick/observe/export APIs) and remove accessors that
   expose internal registries.
5. **Telemetry hardening:** Drop alias coercion once downstream dashboards are
   confirmed DTO-only; add guard tests to prevent reintroduction.

Document prepared to guide the upcoming remediation passes.
