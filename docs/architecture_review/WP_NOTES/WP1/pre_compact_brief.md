# WP1 Pre-Compact Brief — 2025-10-10

## Current Focus
- WP1 remediation continues; world factory and adapter now operate solely on `WorldContext`, with the legacy `runtime=` pathway removed and tests updated to enforce the new contract.
- Observation pipeline (WC-E) remains stable: the simulation loop consumes `WorldContext.observe` DTO envelopes with a guarded fallback while we finish the remaining loop refactors.

## Outstanding Work
- T2.3+: retire the observation-builder fallback once loop/policy paths prove DTO-only stability; this will allow us to drop the builder from the adapter entirely.
- T5.x: add dummy world/policy/telemetry providers plus loop/console/health-monitor smokes.
- Simulation loop cleanup: remove direct `runtime.queue_console` usage, lean exclusively on ports, and backfill integration smokes.
- Documentation updates (ADR-001, console/monitor ADR, status) after the adapter/loop cleanup finalises.

## Dependences / Notes
- Loop still seeds the observation service on the context; we can remove that bootstrap once factory wiring guarantees an injected service.
- Telemetry/policy DTO work (WP3) remains active—keep schema alignment in mind while removing residual legacy helpers.

## Helpful Paths
- Factory tests: `tests/factories/test_world_factory.py`
- World context tests: `tests/test_world_context.py`, `tests/world/test_world_context_observe.py`
- Simulation loop parity: `tests/core/test_sim_loop_dto_parity.py`

Use this as reorientation after compaction.
