# OBS-Prep7 Plan – Integrate Context.observe into Simulation Loop

## Current Behaviour
- `SimulationLoop._build_components` constructs `ObservationBuilder` directly and caches it on `self._observation_builder`.
- During each tick (`SimulationLoop.step`), the loop calls `self._observation_builder.build_batch(self.world_adapter, terminated)` and passes the raw dict plus numerous helper snapshots into `build_observation_envelope`.
- The world factory still returns `DefaultWorldAdapter` backed by `LegacyWorldRuntime`; modular `WorldContext` is not wired in yet, so `context.observe` cannot be invoked by default.

## Target State for Prep7
- `SimulationLoop` should obtain the DTO envelope from the world port (`WorldRuntime.observe`/`WorldContext.observe`) instead of rebuilding it manually.
- Helper metrics (queue, employment, economy, running affordances, relationships) should flow from the context/port rather than loop-side collectors.
- Legacy observation builder usage must remain available behind a temporary guard until the factory swap lands.

## Action Items
1. **Seam for DTO envelopes**
   - Add an internal helper `_get_observation_envelope` that checks whether the world port exposes `observe` and an observation service; fall back to legacy builder when not available.
   - Thread in action/reward/metadata inputs required by `WorldContext.observe` so both paths produce equivalent envelopes.
2. **Loop refactor** *(Completed 2025-10-10)*
   - Replaced direct `build_observation_envelope` usage with context-backed DTO envelopes.
   - Removed the redundant helper collectors (`_collect_queue_metrics`, `_collect_queue_affinity_metrics`, `_collect_job_snapshot`, `_collect_economy_snapshot`) now that `WorldContext.export_*` feeds the loop.
3. **Factory bridging**
   - Insert temporary hook in `SimulationLoop._build_components` to install an observation service on legacy world contexts when available (e.g., `if hasattr(self.world, "context")`).
   - Until WP1 Step 7 rewires `create_world`, keep the legacy adapter path intact.
4. **Testing**
   - Extend `tests/core/test_sim_loop_dto_parity.py` to cover the new code path (expect DTO envelope unchanged).
   - Add regression ensuring loops run when context lacks `observe` (legacy fallback).

## Risks / Blockers
- Full completion requires the world factory to return a modular context; currently blocked by outstanding WP1 Step 7 tasks. For now we integrate a guarded path while leaving the fallback active.
- ObservationBuilder lifetime must remain deterministic during transition; ensure we release embedding slots when falling back to legacy path.

Proceed with the guarded implementation in `SimulationLoop`; revisit factory integration once WP1 Step 7 is executed.
