# Changelog

## [Unreleased]
### Added
- Runtime-checkable protocols for agent, relationship, and employment services (`townlet.world.agents.interfaces`).
- `AffordanceEnvironment` wiring in `world/affordances/` plus service-focused unit tests (`tests/test_agents_services.py`).

### Changed
- `WorldState` now composes services (`AgentRegistry`, `RelationshipService`, `EmploymentService`) and injects them via `WorldContext`.
- Affordance runtime/service consume the new environment, removing direct `WorldState` coupling.
- Behaviour, console, and rivalry tests now use public helpers instead of private world fields.
