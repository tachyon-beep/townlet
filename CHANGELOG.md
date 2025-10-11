# Changelog

## [Unreleased]
### Added

- Telemetry and policy pipeline now emit DTO-only payloads with structured `summary` metrics; 
  guardrails, parity harness (feature_dim=81, map_shape=(4, 11, 11)), and console docs updated.
- Runtime-checkable protocols for agent, relationship, and employment services (`townlet.world.agents.interfaces`).
- `AffordanceEnvironment` wiring in `world/affordances/` plus service-focused unit tests (`tests/test_agents_services.py`).
- Read-only `WorldRuntimeAdapter` façade (`townlet.world.core.runtime_adapter`) and observation/telemetry adapter smoke tests (`tests/test_observation_builder_parity.py`, `tests/test_telemetry_adapter_smoke.py`).
- Telemetry benchmark utilities and scripts: `scripts/wp_d_benchmark.py`, `scripts/wp_d_benchmark_compare.py`.
- Built-in telemetry metrics: queue peaks, flush durations, send failure counters, and totals surfaced via `latest_transport_status()`.
- Documentation: Phase 7 runbook (docs/architecture_review/wp-d_phase7_runbook.md) and telemetry pipeline guide (docs/guides/telemetry_pipeline.md).
 - Policy backend packages and docs:
   - PyTorch backend utilities under `townlet.policy.backends.pytorch` (PPO ops, BC)
   - Scripted backend alias `townlet.policy.backends.scripted.ScriptedPolicyBackend`
   - Public shims (`townlet.policy.ppo.utils`, `townlet.policy.bc`) keep legacy import paths importable without Torch
   - Guides: `docs/guides/policy_backends.md`, `docs/guides/wp-e_upgrade_guide.md`

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
- Telemetry sink protocol expanded with read-only accessors used by consoles and observers; console handlers hardened to use protocol-safe accessors with stub-friendly fallbacks.
 - Policy selection is config‑driven with scripted as default; selecting `pytorch` falls back to stub when Torch is unavailable. Training CLI prints friendly messages when ML modes are requested without Torch.
