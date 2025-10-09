# WP1 — Ports & Factory Registry (Working Notes)

Purpose: capture findings, decisions, and progress while implementing Work Package 1. Update proactively as seams are discovered or addressed.

## TODO / Progress Checklist

- [x] Inventory `SimulationLoop` dependencies (world, policy, telemetry methods used).
- [x] Audit current world implementation entry points (`world/core`, adapters).
- [x] Audit policy runtime / orchestrator interfaces.
- [x] Audit telemetry publisher surface.
- [x] Draft port protocol stubs aligning with ADR-001.
- [x] Outline adapter delegations for default providers.
- [x] Define registry module responsibilities & key names.
- [x] Identify required dummies/testing hooks.
- [x] Plan composition root refactor sequence.
- [x] Note integration tests to add/adjust.

## Findings & Open Questions

### Loop Surface Inventory (2024-XX-XX)
- **Policy backend methods invoked by `SimulationLoop`:** `register_ctx_reset_callback`, `enable_anneal_blend`, `set_anneal_ratio`, `active_policy_hash`, `current_anneal_ratio`, `reset_state`, `decide`, `post_step`, `flush_transitions`, `latest_policy_snapshot`, `possessed_agents`, `consume_option_switch_counts`.  
  - *Implication:* Only `decide` (+ simple lifecycle) belong on the WP1 port. The remaining hooks must move behind policy adapters or be driven via strategy/telemetry services.
- **Telemetry sink usage:** `set_runtime_variant`, `update_policy_identity`, `drain_console_buffer`, `record_console_results`, `publish_tick`, `latest_queue_metrics`, `latest_embedding_metrics`, `latest_job_snapshot`, `latest_events`, `latest_employment_metrics`, `latest_rivalry_events`, `record_stability_metrics`, `latest_transport_status`, `record_health_metrics`, `record_loop_failure`.  
  - *Implication:* Port must stay slim (`start/stop/emit_event/emit_metric`). Console buffering, health reporting, and “latest_*” accessors need to live in adapters or separate telemetry services.
- **World runtime usage:** `queue_console`, `tick` (passing action provider), optional `bind_world_adapter`. Core loop also touches `WorldState` directly (`self.world`).  
  - *Implication:* Port should expose only `observe`, `apply_actions`, `tick`, `snapshot`. Console queueing + adapter binding remain implementation details in default adapter.
- **Direct world state access:** loop iterates `self.world.agents`, etc. Need to decide how much remains outside the port for WP1 (short-term we may keep direct access while world modularisation lands in WP2).

### Implementation Audit Notes (2024-XX-XX)
- **World runtime (`world/runtime.py`):** exposes rich console queueing, staged actions, `tick` returning `RuntimeStepResult`, and `snapshot`. Also supports `bind_world`, `bind_world_adapter`. Good news: port can wrap `tick/apply_actions/observe/snapshot`; adapters will need to bridge console queueing + binding mechanics.
- **World state (`world/grid.py` et al.):** `WorldState` still aggregates everything (console, relationships, etc.). For WP1, adapters should shield the loop from these details while WP2 performs the decomposition.
- **Policy runtime (`policy/runner.py`):** contains many extra hooks (anneal controls, action providers, telemetry snapshots). Port should boil this down to `on_episode_start`, `decide`, `on_episode_end`. Adapters for scripted/Torch/stub will continue exposing hashes, anneal ratios, console wiring internally.
- **Telemetry publisher (`telemetry/publisher.py`):** god-object maintaining queue metrics, console auth, worker threads, `latest_*` queries. Port must *not* expose these; default adapter should translate port calls (`emit_event`, `emit_metric`, `start`, `stop`) into publisher operations and preserve legacy accessors for consoles via composition.
- **Fallback providers:** `policy/fallback.py` and `telemetry/fallback.py` show how stub implementations operate today; useful reference when creating WP1 dummy/test utilities.

### Open Questions
- Where to relocate policy anneal blend + hash reporting so the WP1 port remains minimal?
- Can telemetry `latest_*` queries be satisfied via caching DTOs in the adapter while exposing only generic `emit_*` calls on the port?

### Step 6 recap (handover from WP2)
- `WorldContext` now returns `RuntimeStepResult`, manages modular systems, and exposes the interfaces the WP1 ports expect (`reset`, `apply_actions`, `tick`, `snapshot`).
- Legacy `WorldState` exposes the new helpers (`agent_records_view`, `emit_event`, `event_dispatcher`, `rng_seed`), ensuring the adapter path and the modular pipeline remain compatible.
- Targeted test suites (`pytest tests/world -q`, `pytest tests/test_world_context.py -q`) verify queue/affordance/employment/relationship/economy/perturbation systems as well as the new action pipeline.

### Step 7 plan (WP1 Step 4 resumption)
- **Factory & adapter wiring**
  - Update `townlet.factories.world_factory.create_world` to construct `WorldContext` (and supporting services) directly.
  - Refresh `WorldRuntimeAdapter` so policy/telemetry consumers see the new facade; ensure dummy providers keep working for smoke tests.
- **Simulation loop refactor**
  - Swap `SimulationLoop` over to `create_world/policy/telemetry`; drop `resolve_*` helpers.
  - Introduce the orchestration services promised by external guidance (`ConsoleRouter`, `HealthMonitor`) and route telemetry through events/metrics instead of `latest_*` getters.
  - Ensure policy/telemetry helper functions (`policy_provider_name`, stub detection) read provider metadata via the new factories.
- **Tests**
  - Add loop-level smoke tests that instantiate the new providers (`tests/test_loop_with_dummies.py`, `tests/test_loop_with_adapters_smoke.py`).
  - Implement console/health monitor suites once the services land (`tests/test_console_router.py`, `tests/test_health_monitor.py`).
  - Add a guard test that fails if the loop calls telemetry `latest_*` helpers.
- **Docs**
  - Extend ADR-001 with provider table updates; draft the promised console/monitor ADR.
  - Update this README and WP1 task sheet as milestones close; capture migration instructions for downstream teams.

## References

- `docs/architecture_review/WP_TASKINGS/WP1.md`
- `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md`
- `src/townlet/core/sim_loop.py`
- `src/townlet/world/**`
- `src/townlet/policy/**`
- `src/townlet/telemetry/**`

Update this file as work proceeds (new sections welcome: risk log, test plan, blockers, etc.).

### Composition Findings (2024-XX-XX)
- `core/factory_registry.py` currently holds three global registries (`world`, `policy`, `telemetry`) and registers providers inline. Keys in use: world (`default`, `facade`), policy (`scripted`, `default`, `stub`, `pytorch`), telemetry (`stdout`, `default`, `stub`, `http`). Multiple aliases resolve to the same implementation today.
- Configs (`runtime` section in e.g. `configs/examples/poc_hybrid.yaml`) specify provider names plus optional `options` dict. Migration to WP1 factories must preserve this schema or introduce a clear transition plan.
- Provider resolution happens during `SimulationLoop` construction via `resolve_world/policy/telemetry` with keyword options forwarded wholesale.
- WP1 registry modules will need to re-export the existing fallback behaviour (Torch/httpx guards) and ensure defaults match ADR-001 keys (`default`, `scripted`, `stdout`, with `dummy/stub` variants registered for tests).

### Stub & Test Inventory (2024-XX-XX)
- **Policy:** `townlet.policy.fallback.StubPolicyBackend` satisfies the legacy `PolicyBackendProtocol`, returning wait actions. Tests exercising it:
  - `tests/test_fallbacks.py::test_policy_stub_resolution`
  - `tests/test_policy_orchestrator.py::test_capture_rollout_warns_on_stub_policy`
  - `tests/test_policy_backend_selection.py::test_pytorch_provider_resolves_conditionally`
- **Telemetry:** `townlet.telemetry.fallback.StubTelemetrySink` mirrors telemetry port surface (including console buffers, latest_* accessors). Covered by `tests/test_fallbacks.py::test_telemetry_stub_resolution` and orchestrator stub wiring.
- **World:** no existing dummy/stub world implementation; WP1 must introduce `DummyWorld` to support loop smoke tests.
- **Utility helpers:** `townlet.core.is_stub_policy/is_stub_telemetry` rely on provider names; ensure new registry/factory API preserves these helpers or update tests accordingly.

Implication: new WP1 dummies should integrate cleanly with existing stub tests, or tests must be updated to the new factory paths.

### Tooling & Gate Check (2024-XX-XX)
- `pyproject.toml` already includes `pydantic>=2.11` and dev dependencies (`mypy`, `pytest`, `ruff`). Mypy runs in strict mode across `townlet` by default; expect to satisfy strict typing for new modules or configure targeted overrides.
- Ruff lint targets main sources/tests with rulesets `E,F,I,N,UP,B,A,C4,TID,RUF` and line length 140.
- Pytest default command includes coverage flags; new tests should fit within existing structure (`tests/...`).
- No additional config needed for DTO work—Pydantic is available out of the box.
- Pre-existing overrides ignore mypy missing imports for selected world modules; new ports/factories should not require similar overrides if typed cleanly.

### Step 1 Progress (Ports Created)
- Added `src/townlet/ports/` package with protocols for world, policy, and telemetry per ADR-001.
- Protocols intentionally minimal: world handles reset/tick/agents/observe/apply_actions/snapshot; policy exposes episode hooks + decide; telemetry exposes lifecycle + generic emit calls.
- Adapters will shoulder any additional behaviour (console, anneal, hashes, etc.).

### Adapter & Orchestration Design (aligned with guidance)
- Console commands/results are handled by a new orchestration-level `ConsoleRouter` that translates commands into world actions/queries and emits results via `TelemetrySink.emit_event("console.result", ...)`.
- Stability/health metrics flow through a `HealthMonitor` service that consumes world snapshots/events each tick and emits metrics via telemetry—no more telemetry getters.
- The world adapter owns `ObservationBuilder`; `WorldRuntime.observe()` remains the single observation entrypoint. `world.snapshot()` will include tick-scoped domain events consumed by monitors.
- Telemetry adapters remain pure sinks (`start/stop/emit_event/emit_metric`); any legacy `latest_*` access moves to monitors or policy-side state.
- Tick pipeline: console.run_pending() → world.observe()/policy.decide() → world.apply_actions()/tick() → snapshot (with events) → health_monitor.on_tick(...) → telemetry emits.

### Step 2 Progress (Adapters scaffolding)
- Created `src/townlet/adapters/` package with initial adapters:
  - `DefaultWorldAdapter` wraps legacy `WorldRuntime`, hosts `ObservationBuilder`, emits per-tick events via snapshot.
  - `ScriptedPolicyAdapter` bridges the current scripted policy backend to the minimal port (temporary world-provider dependency; will align with new observation flow during loop refactor).
  - `StdoutTelemetryAdapter` wraps `TelemetryPublisher` as a sink; currently stores emitted events/metrics in publisher state pending new pipeline wiring.
- `ConsoleRouter` and `HealthMonitor` are now instantiated by `SimulationLoop`; console commands drain through the router (while still forwarding to the legacy runtime for now) and the health monitor emits baseline queue/event metrics via the telemetry port.
- Added a transitional `PolicyController` facade so the loop can gradually move off `PolicyRuntime` while the scripted backend continues to supply anneal/metadata hooks.
- Further work: finish migrating telemetry consumers away from publisher getters, move policy-side callbacks into adapters, and remove the remaining legacy world touch points during the ongoing composition refactor.

### Step 3 Progress (Factories)
- Added `townlet.factories` package with shared registry utilities and domain-specific factory helpers (`create_world`, `create_policy`, `create_telemetry`).
- Registered default providers mapping to new adapters; stubs remain available (`policy:stub`, `telemetry:stub`).
- Current implementation still expects legacy runtime instances (world/policy/telemetry); Step 4 will remove the old resolving path and fully adopt the new factories.
- Configuration errors now produce helpful listings of known providers.
- Adapters tweaked after review:
  - `DefaultWorldAdapter.snapshot()` clears cached events post-exposure to avoid double counting.
  - `ScriptedPolicyAdapter` still exposes `attach_world()` for transition (docstring updated to reflect temporary use); upcoming loop refactor will remove the world dependency entirely.
- `StdoutTelemetryAdapter` now forwards `loop.*` events through `TelemetryPublisher`'s event dispatcher (temporary shim); remaining legacy writer calls will disappear once WP3 completes the sink refactor.
- `StubTelemetrySink` emits logging-only events via the same dispatcher, ensuring tests rely solely on `emit_event` / `emit_metric` behaviour.

### External “Fix Pack” Review (2024-XX-XX)
- Reviewed the architect’s drop-in patch suggestions. Intent aligns (true sink telemetry, observation-driven policy, factories constructing dependencies), but concrete diffs don’t apply cleanly:
  - Telemetry patch referenced non-existent publisher APIs and bypassed the worker/aggregator pipeline.
  - Policy adapter patch stubbed scripted behaviour with `noop`, breaking current gameplay paths.
  - Factory patches required modules/constructors not present in the project, defaulting to dummies.
- Decision: retain the strategy while implementing code tailored to Townlet’s runtime in Steps 4+.

### Step 4 Status
- Phase 1 (factory swap) is complete: `SimulationLoop` now resolves world/policy/telemetry via `create_*` helpers while maintaining legacy behaviour behind the adapters.
- Phase 2 has started: the loop routes console traffic through `ConsoleRouter` and feeds `HealthMonitor` snapshots each tick (emitting metrics via the telemetry port) but still mirrors data back into the legacy publisher for parity.
- Phase 3 underway: telemetry getters are no longer pulled from the loop—the tick step computes queue/employment metrics directly and emits a `loop.tick` event through the telemetry port, leaving only the legacy record calls to phase out.
- Remaining work: finish migrating policy callers to the port layer (observation-first decisions) and drop the legacy runtime dependencies once world context + adapters provide all required data.
