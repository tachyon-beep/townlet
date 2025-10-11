# Stage 5 Cleanup Audit — 2025-10-11

## Context
Stage 5 of WP3C is meant to finish the legacy-observation retirement by
eliminating the remaining shims that keep the adapters/factories tied to the
old `ObservationBuilder` path, and by ensuring DTO-only payloads flow through
policy + telemetry. This audit re-checks the current code so we can plan the
cleanup with accurate ground truth.

Command history (for traceability):

```
rg "ObservationBuilder" -n
rg "queue_console" -n
sed -n '1,200p' src/townlet/adapters/world_default.py
sed -n '1,200p' src/townlet/factories/world_factory.py
sed -n '139,220p' src/townlet/world/core/context.py
```

## Findings

### F1 — DefaultWorldAdapter still owns ObservationBuilder
- `src/townlet/adapters/world_default.py` instantiates an `ObservationBuilder`
  when `observation_builder` is not passed, caches it on `_obs_builder`, feeds
  it to the context, and `observe()` still delegates to
  `builder.build_batch(...)`.  
- The adapter also keeps `_queued_console` and `_pending_actions`, mirroring
  legacy runtime behaviour.
- Tests: `tests/adapters/test_default_world_adapter.py` construct stub builders
  and assert behaviour through the cached builder.

### F2 — Factory wires builders into adapters
- `src/townlet/factories/world_factory.py::_build_default_world` accepts an
  `observation_builder` kwarg and always instantiates `ObservationBuilder`
  (unless a caller provides one).  
- The factory has to hand the builder to `DefaultWorldAdapter`, which keeps the
  legacy dependency alive.

### F3 — WorldContext.observe still assumes an ObservationService
- `WorldContext.observe()` requires `self.observation_service` and calls
  `.build_batch(adapter, terminated_map)` before wrapping the DTO envelope.
  Today the adapter injects the builder into the context to satisfy this.  
- Until we move the observation assembly inside the context (or provide a DTO
  observation service that does not rely on `ObservationBuilder`), we cannot
  remove the shim in F1/F2.

### F4 — Console queue shim persists
- `DefaultWorldAdapter.queue_console()` and the dummy runtime both buffer console
  commands, even though `ConsoleRouter.enqueue()` already maintains its own
  queue and Stage 4 moved command routing through events.  
- `ConsoleRouter.enqueue()` still attempts to call `world.queue_console(...)`;
  this becomes a no-op if we delete the method, but we need to coordinate the
  removal to avoid breaking existing tests (`tests/test_console_router.py`,
  dummy harness).

### F5 — Documentation out of sync
- `docs/architecture_review/WP_NOTES/WP3/pre_compact_brief.md` and
  `status.md` state that adapter shims are gone, but the code above shows they
  still exist. We must refresh the docs once the cleanup lands.

## Cleanup Plan (Stage 5 Remaining Work)

### S5.A — Move observation service ownership into WorldContext
1. Introduce a DTO-ready observation service (wrapper around the existing
   `ObservationBuilder` initially) that lives inside the context and exposes the
   existing `ObservationServiceProtocol`.  
2. Update `WorldContext` construction to require/populate the service; adapters
   no longer create or cache builders.  
3. Adjust `WorldContext.observe()` to call the local service and drop the
   adapter hand-off.
4. Tests: refresh `tests/adapters/test_default_world_adapter.py`,
   `tests/world/test_world_context_observe.py`, and DTO parity tests to ensure
   they fetch envelopes from the context without touching `_obs_builder`.

### S5.B — Refactor DefaultWorldAdapter
1. Remove `observation_builder` parameter and `_obs_builder` cache.  
2. Route `observe()` directly through `self._context.observe(...)`, forwarding
   optional action/termination data when required.  
3. Delete `_queued_console` and `_pending_actions` storage in favour of relying
   on `WorldContext.apply_actions` and the console router to deliver commands.
4. Ensure `tick()` takes the prepared actions/console ops that the loop already
   supplies; align unit tests with the new behaviour.

### S5.C — Factory cleanup
1. Drop the `observation_builder` kwarg from `_build_default_world`; rely on the
   context-provided service.  
2. Validate lifecycle/perturbation wiring still works and update existing guard
   tests (`tests/factories/test_world_factory.py`) to assert no builder is
   constructed.

### S5.D — Console port follow-up
1. Update `ConsoleRouter.enqueue()` to avoid calling `world.queue_console`
   (log/debug until the port method is removed).  
2. Remove `queue_console` from `DefaultWorldAdapter` and dummy runtime once the
   router no longer depends on it.  
3. Adjust port surfaces/tests (`tests/test_ports_surface.py`,
   `tests/core/test_sim_loop_with_dummies.py`, console smokes) accordingly.

### S5.E — Documentation & Regression
1. Refresh WP1/WP2/WP3 briefs, status, and task trackers to reflect the true
   post-cleanup state.  
2. Update ADR-001 / DTO migration notes once adapters are DTO-only.  
3. Regression bundle: rerun DTO parity, modular smoke, console + telemetry
   suites, and policy/trajectory tests.

## Open Questions / Risks
- We still rely on `ObservationBuilder` to produce map/features. The initial
  refactor (S5.A) can wrap it, but we should schedule a follow-up to replace the
  builder with modular components once DTO pipelines stabilise.
- Removing `queue_console` affects external integrations that may call the port
  directly; confirm no out-of-tree users remain before deleting the method.

Use this audit as the starting point for the Stage 5 cleanup implementation.

---

## Progress Log

- **2025-10-11 — S5.B completed:** `DefaultWorldAdapter` no longer owns an
  `ObservationBuilder`; it delegates observations to `WorldContext.observe`,
  stages policy actions via the context, and converts DTO agents back to the
  legacy mapping for callers. Adapter unit tests were updated accordingly.
- **2025-10-11 — S5.C completed:** Factory wiring no longer accepts
  `observation_builder`; it relies on the context-provided service, and tests
  now guard that passing the legacy kwarg raises a `TypeError`.
- **2025-10-11 — S5.D completed:** Console routing no longer calls
  `runtime.queue_console`; `SimulationLoop` passes authorised envelopes directly
  into the runtime, adapters/runtimes treat `queue_console` as a no-op shim, and
  smoke/port tests updated to reflect the event-only flow.
- **2025-10-11 — S5.E completed:** Ran targeted DTO/console/telemetry regression
  bundles (`pytest tests/telemetry/test_aggregation.py tests/test_telemetry_surface_guard.py tests/test_console_events.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py tests/orchestration/test_console_health_smokes.py tests/test_console_router.py tests/core/test_sim_loop_modular_smoke.py tests/core/test_sim_loop_with_dummies.py -q`
  and `pytest tests/policy/test_dto_ml_smoke.py tests/world/test_world_context_parity.py tests/core/test_sim_loop_dto_parity.py -q`) and refreshed WP3 status/pre-brief to
  record the Stage 5 finish. Full-suite (`pytest`), `mypy`, and `ruff` runs are earmarked for Stage 6.
- **2025-10-11 — S6.A guard sweep:** Removed the remaining `ObservationBuilder` imports from
  `townlet.world` by renaming the wrapper to `WorldObservationService` and routing builder
  construction through `townlet.observations.create_observation_builder`. Guard tests now pass
  (`pytest tests/core/test_no_legacy_observation_usage.py tests/test_telemetry_surface_guard.py -q`).
- **2025-10-11 — S6.B parity rerun:** DTO parity harness, world-context parity, and ML smoke tests
  passed (`pytest tests/core/test_sim_loop_dto_parity.py tests/policy/test_dto_ml_smoke.py tests/world/test_world_context_parity.py -q`), reaffirming schema v0.2.0 parity (feature_dim=81, map_shape=(4, 11, 11)).
