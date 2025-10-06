# Changelog

## [Unreleased]
### Added
- Runtime-checkable protocols for agent, relationship, and employment services (`townlet.world.agents.interfaces`).
- `AffordanceEnvironment` wiring in `world/affordances/` plus service-focused unit tests (`tests/test_agents_services.py`).
- Read-only `WorldRuntimeAdapter` façade (`townlet.world.core.runtime_adapter`) and observation/telemetry adapter smoke tests (`tests/test_observation_builder_parity.py`, `tests/test_telemetry_adapter_smoke.py`).

### Changed
- `WorldState` now composes services (`AgentRegistry`, `RelationshipService`, `EmploymentService`) and injects them via `WorldContext`.
- Affordance runtime/service consume the new environment, removing direct `WorldState` coupling.
- Behaviour, console, and rivalry tests now use public helpers instead of private world fields.
- Telemetry publisher and snapshot capture route through `ensure_world_adapter`, reducing direct `WorldState` access for queue/relationship metrics.
- Observation builder and helpers accept adapters, ensuring policy/telemetry consumers share the same contract.
- Nightly reset logic moved into `townlet.world.agents.nightly_reset.NightlyResetService` and exposed through `WorldContext.apply_nightly_reset()`; employment helpers now delegate via the expanded `townlet.world.agents.employment.EmploymentService`.
- Economy and perturbation logic extracted to `townlet.world.economy.EconomyService` and `townlet.world.perturbations.PerturbationService`; world and scheduler now delegate price spikes, outages, and arranged meets through these façades.
- Re-export modules (`townlet.world.__init__`, `townlet.world.affordances.*`, console/queue shims) have sorted imports/`__all__` definitions and trimmed `# noqa` flags so `ruff check src/townlet/world` runs clean; console handlers now preserve exception context when validating spawn payloads.
- Phase 5 Step 4 telemetry/observation baselines re-run (`tmp/wp-c/phase5_validation_telemetry.jsonl`) match the prior capture for overlapping ticks, confirming the new services leave runtime outputs unchanged.
- Spawn/teleport/remove/respawn logic now lives in `townlet.world.agents.lifecycle.LifecycleService`; `WorldState`/`WorldContext` expose the service, and console/lifecycle/telemetry suites rely on the façade instead of private helpers. New unit coverage (`tests/test_world_lifecycle_service.py`) exercises the lifecycle surface.
- Phase 6 validation logged at `tmp/wp-c/phase4_validation.txt`; 50-tick smoke telemetry captured in `tmp/wp-c/phase6_smoke_telemetry.jsonl`.
