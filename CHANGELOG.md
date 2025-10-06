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
- Phase 6 validation logged at `tmp/wp-c/phase4_validation.txt`; 50-tick smoke telemetry captured in `tmp/wp-c/phase6_smoke_telemetry.jsonl`.
