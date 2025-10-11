# WP1 Ground Truth Remediation – Executable Task Breakdown

Each section expands the issues from `ground_truth_issues.md` into concrete tasks (T#). Use these to track work as we close out WP1.

## 1. Legacy world factory path still active
- **T1.1** Implement `WorldContext.from_config` (or equivalent builder) that wires `WorldState`, lifecycle, perturbations, modular systems, and returns an object satisfying `WorldRuntime`. *(Completed 2025-10-09.)*
- **T1.2** Update `_build_default_world` so it constructs and returns the modular `WorldContext`; remove all `LegacyWorldRuntime`/`ObservationBuilder` references. *(Completed 2025-10-10 — factory now rejects `runtime=` and always wraps the context; see tests/factories/test_world_factory.py).*
- **T1.3** Delete the fallback kwargs (`lifecycle`, `perturbations`, etc.) once the modular context owns that configuration; adjust callers accordingly. *(Completed 2025-10-11 — factory constructs services internally; loop/tests updated, legacy kwargs now raise `TypeError`.)*
- **T1.4** Add factory unit tests verifying `create_world` returns the modular runtime and emits DTO observations/events. *(Completed 2025-10-11 — integration tests now assert DTO observation envelopes and event payloads.)*
- **T1.5** Add regression test ensuring legacy inputs trigger clear errors (provider key, missing config). *(Completed 2025-10-11 — invalid provider now raises `ConfigurationError`; missing config still raises `TypeError`.)*
- **T1.5** Add regression test ensuring legacy inputs trigger clear errors (provider key, missing config). *(Pending.)*

## 2. DefaultWorldAdapter is a legacy bridge
- **T2.1** Replace `DefaultWorldAdapter` implementation with a wrapper around the modular `WorldContext` and DTO helpers. *(Completed 2025-10-10 — adapter now depends solely on `WorldContext`.)*
- **T2.2** Remove `.world_state` and any direct `LegacyWorldRuntime` dependencies; expose only the `WorldRuntime` port. *(Completed 2025-10-10 — property removed, legacy runtime branch deleted.)*
- **T2.3** Ensure observation building is handled by DTO pipeline; drop `ObservationBuilder` usage. *(Completed 2025-10-10 — adapter.observe now proxies `WorldContext.observe` and no longer references the legacy builder.)*
- **T2.4** Add adapter tests covering `reset`, `tick`, `observe`, `apply_actions`, `snapshot` behaviour. *(Completed 2025-10-10 — see `tests/adapters/test_default_world_adapter.py` for the new unit coverage.)*

## 3. WorldContext is unimplemented
- **T3.1** Port tick orchestration into `WorldContext` (`reset`, `tick`, `agents`, `observe`, `apply_actions`, `snapshot`).
- **T3.2** Integrate modular systems/services and deterministic RNG streams; ensure events populate `snapshot()`.
- **T3.3** Provide unit/system tests comparing modular tick behaviour with legacy parity fixtures.
- **T3.4** Update `WorldContext` exports/documentation to reflect the implementation.

## 4. SimulationLoop remains tied to legacy runtime
- **T4.1a** Introduce seam in `_build_components` that accepts pre-built world/policy/telemetry objects (for test injection). *(Completed 2025-10-10 — see `override_world_components`/`override_policy_components`/`override_telemetry_components` helpers.)*
- **T4.1b** Remove direct `WorldState` construction, instead call `create_world` and pull context/adapter details via the port; update tests depending on `loop.world` attribute. *(Completed 2025-10-10 — loop now derives world/lifecycle/perturbations from `create_world` and uses adapter context for state access.)*
- **T4.1c** Replace `_observation_builder` usage with DTO envelope caching; ensure reward engine consumes the DTO data. *(Completed 2025-10-10 — legacy observation builder fallback removed; DTO envelopes supplied exclusively by `WorldContext.observe`.)*
- **T4.2** Remove direct `runtime.queue_console` usage; pipe console input through `ConsoleRouter.enqueue`/`run_pending`. *(ConsoleRouter now forwards commands; remaining telemetry cleanup tracked under T4.2b.)*
- **T4.3** *(Completed 2025-10-10)* Ensure policy decisions operate on cached DTO envelopes; drop observation dict/collector caches (loop now pulls queue/employment/job metrics directly from `WorldContext.export_*`).
- **T4.4** Refresh loop tick flow to emit telemetry via ports only (no legacy writer calls). *(See detailed T4.x breakdown below — T4.4a complete; T4.4b audit exposes aggregator/UI/CLI migrations still outstanding.)*
- **T4.5** Add loop smoke tests for modular providers and DTO parity.

## 5. Missing dummy providers and promised tests
- **T5.1** Create `src/townlet/testing/` with dummy world/policy/telemetry implementations satisfying the ports. *(Completed 2025-10-11 — see `townlet.testing` package for dummy world/policy/telemetry classes.)*
- **T5.2** Register dummy providers in the factories under documented keys. *(Completed 2025-10-11 — `create_world/policy/telemetry(provider="dummy")` now returns the testing stubs.)*
- **T5.3** Write `tests/test_ports_surface.py` validating method presence/forbidden symbols on ports/adapters. *(Completed 2025-10-11 — port contracts now covered by dedicated tests.)*
- **T5.4** Add `tests/test_loop_with_dummies.py` (fast smoke) driving the loop through dummy providers. *(Completed 2025-10-11 — helper + smokes landed.)*
  - Implemented `tests/helpers/dummy_loop.py`, which constructs a `SimulationLoop`
    via the override seams and injects lightweight doubles for world/context,
    lifecycle, perturbations, rewards, stability, promotion, and policy. The helper
    reuses `TelemetryPublisher` while swapping in `DummyTelemetrySink` so console
    routing, health monitoring, and DTO pipelines exercise the real orchestration
    path.
  - Added `tests/core/test_sim_loop_with_dummies.py` covering two tick increments,
    DTO envelope integrity, console routing (`console.result` events), and
    `loop.health` telemetry on the dummy providers.
  - Regression command recorded under WP1 status: `pytest tests/test_ports_surface.py tests/core/test_sim_loop_with_dummies.py -q`.
- **T5.5** Implement console router & health monitor smokes as per WP1 plan. *(Completed 2025-10-11 — see orchestration smokes.)*
  - Added `tests/orchestration/test_console_health_smokes.py` using the dummy loop harness to
    verify console routing end-to-end (snapshot + unknown command) and health monitor metric
    emission. Harness now exposes the live `ConsoleRouter`/`HealthMonitor` instances through
    `DummyLoopHarness` for assertions.
  - Regression command: `pytest tests/test_ports_surface.py tests/core/test_sim_loop_with_dummies.py tests/orchestration/test_console_health_smokes.py -q`.

## 6. Port boundaries still leak legacy types
- **T6.1** Revise `WorldRuntime` port signatures to remove `WorldState`/console coupling; document DTO expectation.
  - **T6.1a – Usage inventory** *(Completed 2025-10-11)*: Logged port consumers, required methods, and coupling hotspots (see Ground Truth Issues §6 note). Key dependencies: loop + console router depend on `queue_console`; `tick` still passes `WorldState`; runtime binding hooks used during world reset; tests enforce current signature.
  - **T6.1b – Port schema proposal (In progress)**: Define the target DTO-first contract eliminating `WorldState` arguments and console coupling.
    - Proposed surface:
      * `tick(*, tick: int, actions: Mapping[str, object], events: Iterable[dict[str, object]] | None = None) -> RuntimeStepResult` — loop supplies already normalised action payloads and optional external events (e.g., console outcomes) rather than a callback.
      * `stage_actions(actions)` becomes optional; loop can call `apply_actions` prior to `tick` for staged inputs (kept for backwards compatibility but slated for removal).
      * Console routing moves entirely into `ConsoleRouter`, which will call a new `world_context.process_console(envelope)` instead of invoking `WorldRuntime.queue_console`. The port drops `queue_console` altogether.
      * Snapshot method keeps the same shape but documents DTO expectations (world implementations should embed DTO-friendly data so telemetry/policy exporters stay aligned).
      * Add explicit `agents()` + `agent_view()` helpers returning DTO snapshot proxies so scripted behaviours have a read-only path without direct `WorldState` access.
    - Migration notes: introduce transitional methods (`queue_console` calling `process_console`) marked deprecated; update `DefaultWorldAdapter`, dummy runtime, and tests to satisfy the new signature before enforcing removal.
  - **T6.1c – Transitional adapter plan** *(Completed 2025-10-11)*:
    - Step 1: introduce interface aliases (`WorldRuntimeVNext`) exporting the new DTO-first methods while keeping legacy names deprecated. `DefaultWorldAdapter` implements both for a deprecation window by adapting the DTO inputs back into current world-context calls.
    - Step 2: update factories and the loop to consume the new interface: `SimulationLoop` prepares an action batch via the controller and calls `runtime.tick_dto(tick, actions, console_events)`; console router streams results directly to telemetry and optionally passes commands to the world via `context.process_console`. Legacy `queue_console` stays available but emits a deprecation warning and delegates to the router hook.
    - Step 3: migrate test doubles (`DummyWorldRuntime`, `_LoopDummyWorldRuntime`, `tests/test_core_protocols.py` stubs) to the new methods and remove direct `WorldState` dependencies. Provide helper wrappers so existing tests can still instantiate the runtime without DTO knowledge during the transition.
    - Step 4: once adapters/tests align, delete the legacy methods and collapse the alias back into `WorldRuntime`. Document timeline in ADR-001 and mark the deprecation removal milestone in WP1 status.
  - **T6.1d – Documentation update (Pending)**: Once the new interface is ready, refresh ADR-001, CORE_PROTOCOLS.md, and WP1/WP3 status docs to describe the DTO-first contract, console-router ownership, and deprecation timeline for legacy methods. Include migration guidance for downstream providers/dummies.
- **T6.2** Update adapters and loop to match the refined signatures; remove dependency on `core.interfaces` legacy protocols. *(Completed 2025-10-11 — loop/factories now type against `townlet.ports.world.WorldRuntime`.)*
  - Simulation loop, factory registry, and helper harnesses import the port directly; `core.interfaces.WorldRuntimeProtocol` is now a deprecated alias for backwards compatibility.
  - Added `runtime_checkable` to the port protocol so provider factories can continue validating instances structurally.
  - Updated regression tests (`tests/test_factory_registry.py`, `tests/test_core_protocols.py`) to assert against the port contract and check the telemetry/world overrides via the actual ports.
- **T6.3** Provide guard tests ensuring the loop imports only `townlet.ports.*` interfaces. *(Completed 2025-10-11 — see `tests/core/test_world_port_imports.py`)*.
  - Added a static guard that fails if any core/factory/orchestration/testing/telemetry file imports `WorldRuntimeProtocol` from `townlet.core.interfaces`.
  - Regression command: `pytest tests/core/test_world_port_imports.py -q`.
- **T6.4** Deprecate/remove unused members from `core.interfaces` once the loop migrates.

## High-Complexity Task Breakdown

### T1.1 / T3.x – Implement modular WorldContext
- **T1.1a** Extract current tick orchestration flow from `LegacyWorldRuntime.tick` into a design doc snippet mapping each phase (apply actions, systems, snapshot).
- **T1.1b** Stub `WorldContext` methods with TODOs and wire constructor dependencies (state, services, dispatcher) without behaviour yet.
- **T1.1c** Implement `WorldContext.reset` using `WorldState.from_config` and deterministic RNG setup; add unit test covering seed reproducibility.
- **T1.1d** Implement `apply_actions` + `tick` using modular services; include event buffering + RuntimeStepResult construction.
- **T1.1e** Implement `agents`/`observe` returning DTO envelopes via the existing DTO factory; unit test per-agent output and terminated flag handling.
- **T1.1f** Implement `snapshot` returning world/global DTO-friendly payloads; add regression test comparing against legacy snapshot for baseline config.
- **T1.1g** Run parity harness (`tests/core/test_sim_loop_dto_parity.py`) against new context and capture any deltas for follow-up fixes.
- **T3.x Parity (2025-10-11)** Added targeted parity checks (`tests/world/test_world_context_parity.py`) ensuring `WorldContext` queue/economy/relationship exports mirror the underlying world services.

### T4.x – Refactor SimulationLoop onto modular ports
- **T4.1a** Introduce seam in `_build_components` that accepts pre-built world/policy/telemetry objects (for test injection) to aid migration.
- **T4.1b** Remove direct `WorldState` construction, instead call `create_world` and pull context/adapter details via the port; update tests depending on `loop.world` attribute.
- **T4.1c** Replace `_observation_builder` usage with DTO envelope caching; ensure reward engine consumes the DTO data.
- **T4.2a** Move console queueing into `ConsoleRouter.enqueue` during input ingestion; delete `runtime.queue_console` calls.
- **T4.2b** Update telemetry emission to rely solely on port methods (`emit_event/emit_metric`), removing legacy writer fallbacks. *(Completed 2025-10-10 — console results now emit via dispatcher events with router-aware payloads; regression covered by `tests/test_console_events.py`.)*
- **T4.3** *(Completed 2025-10-10)* Ensure policy decisions operate on cached DTO envelopes; drop observation dict/collector caches (loop now pulls queue/employment/job metrics directly from `WorldContext.export_*`).
- **T4.4** Refresh loop tick/health/failure telemetry so payloads flow entirely through the telemetry port (no raw publisher/world references).
  - **T4.4a** *(Completed 2025-10-10)* Expose `transport_status()` on the telemetry port and update the loop to prefer it over publisher helpers.
  - **T4.4b** *(Completed 2025-10-11)*:
    - **T4.4b-A – Publisher ingestion cleanup** *(Completed 2025-10-10)*  
      DTO `global_context` now seeds queue/relationship/job/economy/employment/utilities snapshots; `_capture_affordance_runtime` consumes DTO running/reservation payloads and emits single-shot warnings when fields are missing. Regression coverage lives in `tests/test_telemetry_surface_guard.py`.
    - **T4.4b-B – Aggregator/builders** *(Completed 2025-10-10)*  
      `TelemetryAggregator.collect_tick` takes `global_context`, `StreamPayloadBuilder` prefers DTO data when explicit kwargs are absent, and aggregation tests validate the DTO-only path.
    - **T4.4b-C – Consumer migration** *(Completed 2025-10-10)*  
      Console, CLI, observer dashboard, and conflict telemetry consumers now rely on dispatcher DTO `global_context` payloads; `tests/helpers/telemetry.build_global_context` seeds DTO fixtures for console/telemetry suites, and regression tests (`tests/test_console_commands.py`, `tests/test_conflict_telemetry.py`, `tests/test_observer_ui_dashboard.py`) cover the DTO path.
    - **T4.4b-D – Documentation & regression** *(Completed 2025-10-11)*
      - ADR-001, WP1 status/pre-brief, and parity notes now describe the DTO-first telemetry path and reference the regression bundle (`pytest tests/telemetry/test_aggregation.py tests/test_telemetry_surface_guard.py tests/test_console_commands.py tests/test_conflict_telemetry.py tests/test_observer_ui_dashboard.py -q`).
  - **T4.4c** Rebuild `loop.health` payloads using the new transport snapshot + context exports; adjust `HealthMonitor`, publisher caches, CLI/console helpers, and automated tests. *(Completed 2025-10-11 — structured payload + alias fallback implemented; see `T4_4c_health_schema.md` for schema notes.)*
  - **T4.4d** Align `loop.failure` payloads with the health schema (transport block, snapshot path, error info) and ensure failure handling emits via the telemetry port only; update tests/CLI consumers. *(Completed 2025-10-11 — structured failure payload + regression bundle; see `T4_4d_failure_schema.md`.)*
- **T4.5a** Add new smoke test `tests/core/test_sim_loop_modular_smoke.py` covering two ticks with default providers, asserting DTO envelope + telemetry events. *(Completed 2025-10-10 — smoke verifies DTO envelopes and console telemetry on default providers.)*

### T6.x – Tighten port boundaries
- **T6.1a** Draft revised `WorldRuntime` protocol without `WorldState` references; circulate with WP2 owner for sign-off.
- **T6.1b** Update adapters (`world_default`, dummy world) to satisfy new signatures; ensure type check passes.
- **T6.2a** Update `SimulationLoop` to import only `townlet.ports.world.WorldRuntime`; remove use of `core.interfaces.WorldRuntimeProtocol`.
- **T6.3a** Add guard test `tests/core/test_loop_port_imports.py` ensuring the loop cannot import legacy protocols.
- **T6.4a** Deprecate unused members in `core/interfaces.py` and document removal timeline; follow up with final deletion once callers migrate.

## Additional subdivision for complex tasks

### WorldContext implementation (supersedes T1.1a–T1.1g)
- **WC-A** Capture an action/system/snapshot sequence diagram from `LegacyWorldRuntime.tick` and note required dependencies (no code changes yet).
- **WC-B** Implement `WorldContext.__init__`/`reset` wiring state, RNG builders, dispatcher stubs; write seed determinism test.
- **WC-C** Implement `WorldContext.apply_actions` (queue actions, basic validation) with unit test using stub state/service.
- **WC-D** Implement `WorldContext.tick` orchestrating action processing → systems → event buffer, returning a provisional `RuntimeStepResult` (without DTO dependency yet); add unit test with mocked systems verifying call order.
- **WC-E** Integrate DTO observation builder: update `WorldContext.observe` to call `build_observation_envelope`; unit-test per-agent payload and terminated flag handling.
- **WC-F** Implement `WorldContext.snapshot` to emit tick, events, and DTO/global metrics; unit-test shape and event clearing.
- **WC-G** Run parity harness against the new context and capture delta report; open follow-up tasks for any discrepancies.

### SimulationLoop migration (supersedes T4.1a–T4.5a)
- **SL-A** Introduce constructor seams (dependency injection hooks) for world/policy/telemetry to ease staged migration; add tests ensuring defaults still work. *(Completed 2025-10-10 — `SimulationLoop` now exposes override hooks for all component bundles.)*
- **SL-B** Replace direct `WorldState` creation with `create_world` call; adjust loop attributes and tests that relied on `self.world` being the legacy object. *(Completed 2025-10-10 — loop builds world components via `create_world`, enforcing context-backed adapters.)*
- **SL-C** Swap policy setup to use `create_policy` output directly, ensuring controller binding works; add regression test for pending intent handling. *(Completed 2025-10-10 — policy components come from factory, controller wiring validated by DTO parity tests.)*
- **SL-D** Swap telemetry setup to use `create_telemetry`, removing direct `TelemetryPublisher` mutation; verify telemetry events via existing tests. *(Completed 2025-10-10 — telemetry components now resolved via factory.)*
- **SL-E** Remove `_observation_builder` cache; update reward engine and policy decision path to consume the DTO envelope; add unit test ensuring policy sees matching agent IDs. *(Completed 2025-10-10 — loop consumes DTO envelopes through `WorldContext.observe`, legacy builder removed.)*
- **SL-F** Route console commands via `ConsoleRouter` exclusively and delete `runtime.queue_console`; extend console smoke test to assert router usage. *(Completed 2025-10-10 — loop drops buffered commands if the router is absent and no longer calls `runtime.queue_console`; smoke test covers router-based telemetry.)*
- **SL-G** Update failure/snapshot handling to pull data from modular runtime (`runtime.snapshot`), adjusting `SnapshotManager` tests as needed. *(Completed 2025-10-10 — loop delegates to runtime snapshot, SnapshotManager tests updated, and console router normalises SnapshotState payloads.)*
- **SL-H** Add new smoke `tests/core/test_sim_loop_modular_smoke.py` running two ticks and asserting DTO envelope + telemetry events (stdout adapter stub). *(Completed 2025-10-10.)*

### Port boundary tightening (supersedes T6.x)
- **PB-A** Draft revised `WorldRuntime` protocol without `WorldState`/console references and circulate for sign-off; no code changes yet. *(Completed 2025-10-11 — see `PB_port_contract.md` for the agreed surface.)*
- **PB-B** Introduce transitional methods on adapters (e.g., `queue_console_router`) to support new protocol while keeping tests passing. *(Completed 2025-10-11 — console routing now flows entirely through `ConsoleRouter`; adapters/dummies no longer expose `queue_console`.)*
- **PB-C** Update `DefaultWorldAdapter` and dummy world to satisfy the revised protocol; unit test behaviour. *(Completed 2025-10-11 — adapter/dummy runtime refitted, port surface tests (`tests/test_ports_surface.py`) and loop smokes updated.)*
- **PB-D** Update `SimulationLoop` to import and use only `townlet.ports.world.WorldRuntime`; remove `core.interfaces.WorldRuntimeProtocol` usage.
- **PB-E** Add guard test ensuring loop modules don’t import `core.interfaces`; enforce via CI.
- **PB-F** Deprecate unused members in `core/interfaces.py`; schedule follow-up removal once call sites are gone.

---
## Progress Log (2025-10-10)
- Completed **WC-A** – legacy tick flow documented (`WC_A_tick_flow.md`).
- Completed **WC-B** – added deterministic reset regression test (`tests/test_world_context.py::test_world_context_reset_deterministic`).
- Completed **WC-C** – tightened `WorldContext.apply_actions` with validation and added regression test `test_world_context_apply_actions_validation`.
- WC-D plan: validate `WorldContext.tick` orchestrates actions + systems via tests covering (1) pending vs prepared action merge/clear, (2) nightly reset invocation on cadence, ensuring returned `RuntimeStepResult` matches expectations. No structural code changes anticipated; focus on regression coverage.
- Completed **WC-D** – added regression tests `test_world_context_tick_merges_pending_and_prepared` and `test_world_context_tick_triggers_nightly_reset` to cover tick orchestration behaviour.

### WC-E – Observation envelope support (planned work)
- **OBS-Prep1** Inventory `build_observation_envelope` inputs and map each field to a world/context source (queues, employment, policy metadata, etc.); capture the mapping in a short table under `docs/architecture_review/WP_NOTES/WP1`.
- **OBS-Prep2** Design a lightweight observation service interface (`WorldObservationService`) responsible for assembling raw observation batches and agent contexts; document API and dependencies.
- **OBS-Prep3** Thread the observation service through `WorldState` → `WorldContext` construction (update `WorldState.__post_init__` and context factory wiring) without changing behaviour.
- **OBS-Prep4** Implement data collection helpers inside `WorldContext.tick` (or dedicated methods) that surface queue metrics, running affordances, relationship snapshots, employment/economy snapshots, and anneal context so the DTO builder no longer depends on the simulation loop.
- **OBS-Prep5** Add `WorldContext.observe` implementation calling `build_observation_envelope` using the data gathered above; ensure the method accepts optional agent IDs and returns DTO envelopes.
- **OBS-Prep6** Write unit/integration tests covering: (a) per-agent DTO fields (needs, wallet, queue state, pending intent), (b) terminated flag propagation, (c) global context snapshots. Use fixture worlds to ensure determinism.
- **OBS-Prep7** Update `SimulationLoop` to consume the new `WorldContext.observe` method instead of rebuilding envelopes manually; adjust policy/telemetry emission code accordingly and run DTO parity harness to confirm no regressions.
- Completed **OBS-Prep3** – threaded optional observation service through `WorldState` and `WorldContext` construction (no behavioural changes).
- Completed **OBS-Prep4** – added context-level snapshot helper methods (`export_queue_metrics`, `export_relationship_snapshot`, etc.) for DTO assembly.
- Completed **OBS-Prep5** – implemented `WorldContext.observe` returning DTO envelopes, added helper exports (job snapshot, mapping conversion), and regression tests (`tests/world/test_world_context_observe.py`).
- Completed **OBS-Prep6** – expanded observation tests covering per-agent DTO fields, agent filters, and global snapshot data (`tests/world/test_world_context_observe.py`).
- Completed **OBS-Prep7** – simulation loop now attempts to consume `WorldContext.observe` (with fallback to legacy builder), observation service injected during component build, DTO parity tests refreshed.
- Completed **T1.1** – `create_world` now builds modular `WorldContext` adapters (with observation service), updated `DefaultWorldAdapter` to handle both legacy and modular paths, and added factory regression tests (`tests/factories/test_world_factory.py`).
