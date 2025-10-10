# WP1 Status

**Current state (2025-10-10)**
- Port protocols, registry wiring, and adapter surfaces remain stable; Step 7 factory work is complete (`create_world` now returns `WorldContext`, dummy/stub providers and registry metadata are in sync, and `WorldRuntimeAdapter` bridges both modular and legacy paths for remaining callers).
- WP2 Step 6/7 continue to supply modular tick orchestration; the simulation loop already instantiates `ConsoleRouter` and `HealthMonitor`, emits telemetry via the WP3 dispatcher, and defers console execution through the router while keeping legacy fallbacks available.
- WP3B (modular systems) is complete and WP3C is deep in Stage 3: policy runtime/controller, scripted behaviours, trajectory service, and replay tooling all consume DTO envelopes. Recent work added DTO-rich metadata to rollout frames and manifests (`*_dto.json`) so training/replay consumers can transition away from the legacy observation blobs.
- Stage 5/6 safeguards are now active: `tests/core/test_no_legacy_observation_usage.py` locks ObservationBuilder/legacy payload usage out of runtime code, and the telemetry surface guard verifies dispatcher payloads ship DTO envelopes plus cached metadata snapshots each tick.
- Outstanding WP3C items (training adapters, DTO-only ML parity, Stage 6 documentation/world-adapter cleanup) remain the blockers for Step 8; until those land the loop must keep `runtime.queue_console` and legacy world handles for policy/training.

**Focus areas (Step 8 execution once unblocked)**
- Finish the simulation loop refactor by removing `runtime.queue_console`, enforcing DTO-only policy decisions, and delegating world mutations through the modular context. Telemetry surface work is largely done; remaining effort is tied to the policy/world detach.
- Add the pending loop/console/health-monitor smoke tests plus factory/port regression coverage. The telemetry guard suite and DTO parity harness are already in place; console and router tests remain on the to-do list.
- Document the composition-root changes in ADR-001, draft the console/router ADR, and refresh the WP1 README once Step 8 completes.

**Legacy caller inventory (updated 2025-10-10)**
- Policy:
  - `PolicyController` owns ctx-reset/anneal hooks; decision path still hands the legacy `WorldState` into scripted backends. Switch to DTO-only requests once WP3C Stage 3D/Stage 5 land.
  - Training orchestrator now streams DTO frames, but replay exports keep the legacy translator until downstream consumers ingest the new JSON artefacts.
- Telemetry:
  - Loop identity (`runtime.variant`, `policy_info`) still mutated directly; convert these to dispatcher events post-WP3C.
  - Console history is still sourced from telemetry for parity; once DTO-only command routing is validated, drop the getter usage.
- World:
  - Console queueing (`runtime.queue_console`) and direct `WorldState` mutations (pending intent/agent state writes) remain. Replace with `ConsoleRouter` queues and `WorldContext` helpers when DTO guardrails are in place.
  - Provider metadata is correct, but the default loop retains `self.world` for legacy observers; plan to cull after WP3 Stage 5 removes the observation dict.

Keep this file in sync with WP2/WP3 dependencies as Step 8 progresses.
