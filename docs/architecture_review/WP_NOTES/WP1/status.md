# WP1 Status

**Current state (2025-10-10)**
- Port protocols and registry scaffolding remain in place, and `WorldContext` now supports DTO observation envelopes. The default world factory rejects the legacy `runtime=` shortcut and always returns a context-backed adapter; `DefaultWorldAdapter` is context-only (legacy `.world_state`/runtime handles removed) with dedicated tests in `tests/adapters/test_default_world_adapter.py`.
- `SimulationLoop` resolves world/policy/telemetry components exclusively through the factories (with injectable overrides for tests), consumes DTO envelopes directly from `WorldContext.observe`, and now routes console telemetry via dispatcher events (T4.2b). The modular smoke in `tests/core/test_sim_loop_modular_smoke.py` covers DTO envelopes plus console routing on default providers.
- Console routing always flows through `ConsoleRouter`, with buffered commands dropped (and logged) if the router is unavailable; telemetry ingestion happens through `console.result` events, and legacy `record_console_results` shims stay unused. Snapshot commands now return structured results derived from `SnapshotState`.
- WC3 (telemetry/policy DTO work) unlocked the observation pipeline and telemetry guards (`tests/core/test_no_legacy_observation_usage.py`, `tests/test_telemetry_surface_guard.py`). Outstanding WP3C items (training adapters, DTO-only parity sweeps) still block the final removal of remaining legacy world handles.

- Execute T4.4/T4.4a to refresh loop failure handling and snapshot wiring once DTO parity work lands. *(Console/loop snapshot path already uses runtime snapshots; remaining cleanup focuses on failure telemetry wiring.)*
- Deliver T5.x dummy world/policy/telemetry providers and associated loop/console/health-monitor smokes.
- Update documentation (ADR-001, console/monitor ADR, WP1 README/status) after the adapter/loop cleanup converges.

**Legacy caller inventory (updated 2025-10-10)**
- Policy:
  - `PolicyController` owns ctx-reset/anneal hooks; decision path still hands the legacy `WorldState` into scripted backends. Switch to DTO-only requests once WP3C Stage 3D/Stage 5 land.
  - Training orchestrator now streams DTO frames, but replay exports keep the legacy translator until downstream consumers ingest the new JSON artefacts.
- Telemetry:
  - Loop identity (`runtime.variant`, `policy_info`) still mutated directly; convert these to dispatcher events post-WP3C.
  - Console history is still sourced from telemetry for parity; once DTO-only command routing is validated, drop the getter usage.
- World:
- Direct `WorldState` mutations (pending intent/agent state writes) remain; replace them with `ConsoleRouter` queues and `WorldContext` helpers once DTO guardrails are in place.
  - Provider metadata is correct, but the default loop retains `self.world` for legacy observers; plan to cull after WP3 Stage 5 removes the observation dict.

Keep this file in sync with WP2/WP3 dependencies as Step 8 progresses.
