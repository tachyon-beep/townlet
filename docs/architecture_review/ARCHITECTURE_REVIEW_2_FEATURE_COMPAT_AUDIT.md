# Architecture Review 2 — Feature Flag & Backward Compatibility Audit

*Audit Date: 2025-10-07T11:19:18Z*

This audit surfaces all feature flag entry points and backward-compatibility shims identified in the Townlet codebase, evaluating whether they are still exercised and recommending follow-up actions prior to the branch merge.

## 1. Feature Flag Inventory

| Flag | Definition | Live usages | Findings | Recommendation |
| --- | --- | --- | --- | --- |
| `features.stages.relationships` | `StageFlags.relationships` (`src/townlet/config/flags.py:24`) | Gated chat logic in `policy.behavior._maybe_chat()` (`src/townlet/policy/behavior.py:177`); observation social slots guard (`src/townlet/observations/builder.py:140`). | Actively controls relationship-enabled behaviours; default `OFF` still respected. | Keep. Document expected stage transitions in config README. |
| `features.stages.social_rewards` | `StageFlags.social_rewards` | Applied in reward engine to scale social reward components (`src/townlet/rewards/engine.py:167`) and orchestrator overrides (`src/townlet/policy/training_orchestrator.py:922`). | Flag drives reward curves; default `OFF` may mask expected behaviour if schedule not configured. | Keep but add config validation to ensure stage specified when social rewards config present. |
| `features.systems.lifecycle` | `SystemFlags.lifecycle` default `"on"` | **No runtime references** (codebase search). Lifecycle subsystem is always initialised via `LifecycleManager`. | Dead flag; toggling has no effect -> source of misconfiguration confusion. | Deprecate flag in config schema and remove from docs; consider hard-coding lifecycle `on`.
| `features.systems.observations` | Observation variant toggle | `SimulationConfig.observation_variant` accessor, loader validation (`src/townlet/config/loader.py:299`). | Needed to select hybrid/full/compact. | Keep. |
| `features.training.curiosity` | `TrainingFlags.curiosity` default `phase_A` | **No direct runtime usage**; curiosity behaviour controlled via `TrainingConfig.curiosity` instead. | Redundant/unused toggle; suggests stale design. | Remove flag or wire into curiosity pipeline (`policy.trainers`); update configs accordingly. |
| `features.console.mode` | `ConsoleFlags.mode` default `viewer` | **No runtime usage** (console auth handles modes). | Redundant. | Drop from schema or hook into console initialisation to avoid false expectation. |
| `features.relationship_modifiers` | Boolean | Enables personality-based relationship deltas (`src/townlet/world/agents/relationships_service.py:290`). | Functional; default `False`. | Keep. |
| `features.behavior.personality_profiles` | Boolean | Enables policy bias adjustments (`src/townlet/policy/behavior.py:49`) and telemetry personality snapshot (`src/townlet/telemetry/publisher.py:1005`). | Functional. | Keep; add doc clarifying impact. |
| `features.behavior.reward_multipliers` | Boolean | Enables reward scaling in reward engine (`src/townlet/rewards/engine.py:28`) and world personality rewards (`src/townlet/world/grid.py:321`). | Functional. | Keep. |
| `features.observations.personality_channels` | Boolean | Enables personality channels in observations (`src/townlet/observations/builder.py:59`) & telemetry overlays (`src/townlet/telemetry/publisher.py:1005`). | Functional. | Keep. |
| `features.observations.personality_ui` | Boolean | Checked by dashboard (`townlet_ui/dashboard.py:2015`). | UI-only but active. | Keep; ensure server exposes flag in telemetry metadata. |

### Flag hygiene summary

- **Unused flags:** `systems.lifecycle`, `training.curiosity`, `console.mode`.
- **Partial wiring:** social reward stage lacks validation when schedule defined; consider cross-checking.
- **Documentation gaps:** flag meanings scattered; central README should be updated during doc tidy.

## 2. Backward Compatibility Surfaces

| Component | Location | Behaviour | Status / Risk | Recommendation |
| --- | --- | --- | --- | --- |
| Agent registry dict shim | `src/townlet/world/agents/registry.py:10` | Preserves dict-like access for legacy callers, exposes callbacks for new systems. | Low risk; still used broadly. | Retain until bounded services land; add TODO to remove once APIs stabilise. |
| `WorldState.employment_runtime` & `affordance_service` properties | `src/townlet/world/grid.py:636` | Expose internals for tests/back-compat during extraction. | Medium risk: encourages external coupling. | Mark properties as deprecated; migrate tests to façade or adapters before dropping. |
| Affordance hook registration fallback | `src/townlet/world/grid.py:665` | Uses `hasattr` to route to new service or legacy registry. | Indicates partial migration (dual path). | After affordance service extraction completes, remove legacy branch. Track under affordance decomposition work package. |
| Queue package re-export | `src/townlet/world/queue/__init__.py:1` | Re-exports `QueueManager/QueueConflictTracker` pending package split. | Neutral. | Leave until namespace refactor finishes; add comment referencing tracking issue. |
| Snapshot scalar compatibility | `src/townlet/snapshots/state.py:189` | Accepts legacy scalar relationship encoding. | Medium risk: masks format drift. | Add migration to convert on load and emit warning when scalar encountered; plan deprecation once migrations in place. |
| Telemetry transport `close()` alias | `src/townlet/telemetry/transport.py:30` | Keeps older code/tests working. | Low risk. | Leave; note in docs once new API stable. |
| Telemetry publisher flush poll exposure | `src/townlet/telemetry/publisher.py:175` | Exposes internal interval for legacy tests. | Low; mostly harmless. | Move to explicit `@property` and deprecate comment to clarify usage. |
| Training harness wrapper | `src/townlet/policy/runner.py:453` | Deprecation shim around `PolicyTrainingOrchestrator`. | Medium: warns but still available, can hide missing refactors. | Add TODO to remove after next release; ensure all callers updated. |
| Telemetry UI snapshot wrapper | `townlet_ui/telemetry.py:1075` | Provides old schema to UI consumers. | Unknown usage; risk of stale schema. | Confirm consumer list; plan removal post DTO migration. |
| Web gateway heartbeat arg | `src/townlet/web/gateway.py:50` | Accepts unused parameter for future compat. | Minor; ensure TODO exists so parameter begins being used or removed. |

## 3. Key Gaps & Actions

1. **Retire dead feature flags**: Remove `systems.lifecycle`, `training.curiosity`, and `console.mode` from `FeatureFlags`. Update YAML configs (`configs/examples/poc_hybrid.yaml`) and documentation to reduce configuration noise.
2. **Harden social reward staging**: Add loader validation that raises if social reward stage is `OFF` while social reward weights diverge from defaults; document recommended stage per config.
3. **Deprecate compatibility properties**: Annotate `WorldState.employment_runtime` / `.affordance_service` with `warnings.warn` and migrate tests to new service injection path.
4. **Snapshot scalar warning**: Emit `logger.warning` whenever scalar fallback path engages and schedule migration to drop support once snapshot migrations framework is active.
5. **Telemetry/UI compatibility review**: Inventory consumers of the UI compatibility wrapper and plan DTO transition to avoid double maintenance during telemetry rewrite.
6. **Documentation refresh**: Add consolidated feature-flag matrix to `docs/README.md` (or dedicated page) so toggles aren’t rediscovered ad-hoc during future refactors.

## 4. Removal & Validation Plan

### Dead-flag retirement

1. **Usage verification**
   - Run `rg "features\.systems\.lifecycle"`, `rg "features\.training"`, and `rg "features\.console"` across `src/` and `tests/` to confirm no dynamic uses exist beyond config schema (baseline checks already clean).
   - Add temporary `print`/`logger.debug` in `SimulationConfig.model_validate` during local validation to ensure sample configs don’t supply unexpected values.

2. **Schema update**
   - Remove `LifecycleToggle`, `CuriosityToggle`, and `ConsoleFlags` definitions from `config/flags.py`, along with related exports in `config/__init__.py`.
   - Drop fields from `FeatureFlags` and adjust `SystemFlags` to only expose `observations`.

3. **Config sweep**
   - Update all curated YAML configs under `configs/` to delete the retired flag blocks. Provide defaults for lifecycle/curiosity/console via dedicated domain configs if needed.
   - Add migration note to `docs/README.md` instructing downstream consumers to remove the deprecated keys.

4. **Tests & CI**
   - Run `pytest` with focus on config loaders (`pytest tests/test_config_loader.py`) to catch schema regressions.
   - Execute `python scripts/run_simulation.py --config configs/examples/poc_hybrid.yaml` to ensure runtime initialises without the removed flags.

### Validation of retained flags

1. **Relationship & social rewards**
   - Add unit tests in `tests/test_policy_behavior.py` and `tests/test_rewards.py` toggling `features.stages.relationships/social_rewards` to verify behaviour changes (chat enabling, reward scaling).
   - Introduce assertions in `tests/test_fallbacks.py` ensuring relationship flags still allow stub policies to operate when disabled.

2. **Behavioral/personality toggles**
   - Extend existing policy behaviour tests to confirm `features.behavior.personality_profiles` and `reward_multipliers` alter thresholds/reward bias when set.
   - Add telemetry snapshot assertions verifying personality overlays only render when `features.observations.personality_channels` is `True`.

3. **Observation variant flag**
   - Ensure `SimulationConfig.require_observation_variant` is exercised in `tests/test_observation_builder*.py` for each supported variant.

4. **Documentation & telemetry**
   - Publish a short matrix in `docs/architecture_review/ARCHITECTURE_REVIEW_2_RESPONSE.md` linking each remaining flag to its covered tests.
   - Emit telemetry during `pytest -k "telemetry"` runs to confirm personality UI/telemetry toggles produce expected metadata; add guard tests if missing.

5. **Post-change monitoring**
   - After merging the flag removal, enable a temporary CI job that inspects incoming configs for deprecated keys and fails fast with actionable messages.

## 5. Open Questions

- Who consumes `TrainingFlags.curiosity`? If external tooling relied on it historically, capture that contract before removal.
- Are there remaining legacy callers using `WorldState.register_affordance_hook` without the service? If not, we can delete the fallback path in the next PR.
- Can we track snapshot scalar usage frequency via telemetry to build confidence before deprecation?

---

Prepared for inclusion in the refactor work package backlog. Update this audit as flags are retired or compatibility shims are removed.
