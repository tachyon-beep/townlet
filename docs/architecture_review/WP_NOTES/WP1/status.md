# WP1 Status

**Current state (2025-10-10)**
- Port protocols and registry scaffolding remain in place, and `WorldContext` now supports DTO observation envelopes. The default world factory now rejects the `runtime=` shortcut and always returns a context-backed adapter; `DefaultWorldAdapter` is context-only (legacy `.world_state`/runtime handles removed) while still exposing the port surface expected by the loop.
- `SimulationLoop` has a guarded integration with `WorldContext.observe`: when the context exposes an observation service, the loop consumes its DTO envelope; otherwise it falls back to the legacy builder. Console routing and health monitoring continue to operate alongside the legacy queue-console path.
- WC3 (telemetry/policy DTO work) unlocked the observation pipeline and telemetry guards (`tests/core/test_no_legacy_observation_usage.py`, `tests/test_telemetry_surface_guard.py`). Outstanding WP3C items (training adapters, DTO-only parity sweeps) still block the final removal of legacy world handles.

**Focus areas (next remediation steps)**
- Finish **T2.3/T4.x**: drop the observation-builder fallback once DTO-only parity is stable, then continue the simulation loop cleanup (remove `runtime.queue_console`, rely solely on ports) and add the missing loop/console smokes.
- Execute T5.x to introduce dummy world/policy/telemetry providers and associated surface tests.
- Update documentation (ADR-001, console/monitor ADR, WP1 README/status) after adapter/loop cleanup converges.

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
