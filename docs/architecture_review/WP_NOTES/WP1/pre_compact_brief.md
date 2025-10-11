# WP1 Pre-Compact Brief — 2025-10-10

## Current Focus
- WP1 remediation continues; world factory and adapter operate solely on `WorldContext`, with adapter coverage added in `tests/adapters/test_default_world_adapter.py` to lock in `reset`/`tick`/`observe` semantics.
- SimulationLoop routes console events exclusively through the telemetry dispatcher (T4.2b) and the modular smoke (`tests/core/test_sim_loop_modular_smoke.py`) verifies DTO envelopes plus console telemetry on default providers.

## Outstanding Work
- T5.x: add dummy world/policy/telemetry providers plus loop/console/health-monitor smokes.
- T4.4/T4.4a: failure handling and snapshot refactors remain; update ADR-001 and console/monitor ADR once the remaining loop cleanup lands.
- Documentation updates (ADR-001, console/monitor ADR, status) after the adapter/loop cleanup finalises.

## Dependences / Notes
- Context wiring currently depends on the factory ensuring `observation_service` is configured; adapter.observe now proxies DTO envelopes directly from the context and adapter tests guard the behaviour.
- Telemetry/policy DTO work (WP3) remains active—keep schema alignment in mind while removing residual legacy helpers.

## Helpful Paths
- Factory tests: `tests/factories/test_world_factory.py`
- World context tests: `tests/test_world_context.py`, `tests/world/test_world_context_observe.py`
- Simulation loop parity: `tests/core/test_sim_loop_dto_parity.py`
- Modular smoke: `tests/core/test_sim_loop_modular_smoke.py`

Use this as reorientation after compaction.
