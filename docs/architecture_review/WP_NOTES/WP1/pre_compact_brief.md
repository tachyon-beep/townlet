# WP1 Pre-Compact Brief — 2025-10-10

## Current Focus
- WP1 remediation continues; world factory and adapter operate solely on `WorldContext`, with adapter coverage added in `tests/adapters/test_default_world_adapter.py` to lock in `reset`/`tick`/`observe` semantics.
- SimulationLoop routes console events exclusively through the telemetry dispatcher (T4.2b); queue/employment/job snapshots now come straight from `WorldContext.export_*`, and the `loop.tick` payload exposes a DTO-first `global_context` block (T4.4b) while the modular smoke (`tests/core/test_sim_loop_modular_smoke.py`) verifies DTO envelopes plus console telemetry on default providers.

## Strategic Guidance
The broader intent is to finish the port-first composition root so the simulation loop, factories, and telemetry stack behave as a thin orchestration shell. Every remaining task should move us toward deterministic, DTO-native ports: no legacy `WorldState` reach-ins, deterministic RNG management owned by the context, and console/telemetry flows expressed purely as events. Keep the end goal in mind—when WP1 closes, downstream packages must be able to plug into world/policy/telemetry ports without encountering legacy shims or hidden state.

## Outstanding Work
- T5.x: add dummy world/policy/telemetry providers plus loop/console/health-monitor smokes.
- T4.4: finish the remaining telemetry/failure cleanup (ports-only failure emission + doc refresh) after the context export refactor. *(loop.tick port work done; health/failure still pending)*
- Documentation & parity: expand DTO parity harness/tests for the context (T3.x), refresh ADRs, and capture the strategic changes in WP1/WP2/WP3 briefs once the remaining tasks converge.

## Dependences / Notes
- Context wiring currently depends on the factory ensuring `observation_service` is configured; adapter.observe now proxies DTO envelopes directly from the context and adapter tests guard the behaviour.
- Telemetry/policy DTO work (WP3) remains active—keep schema alignment in mind while removing residual legacy helpers, especially around RNG determinism and policy snapshot events.

## Helpful Paths
- Factory tests: `tests/factories/test_world_factory.py`
- World context tests: `tests/test_world_context.py`, `tests/world/test_world_context_observe.py`
- Simulation loop parity: `tests/core/test_sim_loop_dto_parity.py`
- Modular smoke: `tests/core/test_sim_loop_modular_smoke.py`

Use this as reorientation after compaction.
