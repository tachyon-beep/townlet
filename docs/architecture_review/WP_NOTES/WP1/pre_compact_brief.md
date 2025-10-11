# WP1 Pre-Compact Brief — 2025-10-10

## Current Focus
- WP1 remediation continues; world factory and adapter now operate solely on `WorldContext`, with the legacy `runtime=` pathway removed and tests updated to enforce the new contract.
- SimulationLoop now resolves world/lifecycle/telemetry components exclusively through the factories (with override hooks for tests) and consumes DTO envelopes directly from `WorldContext.observe` (legacy observation-builder fallback removed).

## Outstanding Work
- T5.x: add dummy world/policy/telemetry providers plus loop/console/health-monitor smokes.
- Simulation loop cleanup: remove direct `runtime.queue_console` usage, lean exclusively on ports, and backfill integration smokes.
- Documentation updates (ADR-001, console/monitor ADR, status) after the adapter/loop cleanup finalises.

## Dependences / Notes
- Context wiring currently depends on the factory ensuring `observation_service` is configured; adapter.observe now proxies DTO envelopes directly from the context.
- Telemetry/policy DTO work (WP3) remains active—keep schema alignment in mind while removing residual legacy helpers.

## Helpful Paths
- Factory tests: `tests/factories/test_world_factory.py`
- World context tests: `tests/test_world_context.py`, `tests/world/test_world_context_observe.py`
- Simulation loop parity: `tests/core/test_sim_loop_dto_parity.py`

Use this as reorientation after compaction.
