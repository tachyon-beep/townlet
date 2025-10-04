# Observation & Telemetry – Phase 3 Risk Readiness

## Observation Tensor Consumers
- `src/townlet/core/sim_loop.py`: drives `ObservationBuilder.build_batch` every tick before handing tensors to the active policy runtime.
- `src/townlet/policy/runner.py` and PPO helpers (`src/townlet/policy/ppo/*`): expect consistent feature vectors for neural policies and replay export.
- `src/townlet/policy/scripted.py` / `scripts/profile_observations.py`: scripted capture paths store observation tensors for BC manifests.
- Snapshot tooling (`src/townlet/snapshots/state.py`) and regression tests (`tests/test_observations_*`) ingest the builder output when verifying round-trips.

## Telemetry Readers
- `src/townlet_ui/dashboard.py` and related CLI palette components rely on `TelemetryPublisher.export_state()` fields for live dashboards.
- Web spectator (`townlet_web/src/hooks/useTelemetryClient.ts`, `townlet_web/src/utils/selectors.ts`, `townlet_web/src/utils/telemetryTypes.ts`) parses JSON snapshots for UI state.
- Automation/tests (`tests/test_console_commands.py`, `tests/test_observer_ui_dashboard.py`, `tests/test_web_telemetry`) assert schema stability.
- Snapshot loader (`src/townlet/snapshots/state.py`) depends on telemetry payloads when restoring recorder sessions.
- Telemetry payload now exposes a `personalities` section and personality-driven narration events when the observation flag is enabled; downstream decoders must treat this block as optional.

## Baseline Captures
- Observation tensor shape snapshot (demo_story_arc, 3 seeded agents, feature length 81) stored at `tests/data/baselines/observation_tensor_baseline.json`.
- Personality-enabled observation snapshot (flag on, feature length 84 with trait channel) stored at `tests/data/baselines/observation_tensor_personality_enabled.json`.
- Telemetry KPI baseline (10 ticks, queue/employment KPIs zeroed, embedding metrics captured) stored at `tests/data/baselines/telemetry_snapshot_baseline.json`.

## Decoder Audit Notes
- Policy stack only inspects contiguous feature vectors; additional channels must append safely without reordering existing indices. PPO replay writers read raw vectors but ignore metadata maps; ensure new metadata stays optional.
- Scripted BC capture writes tensors by length, so tests must be updated when feature_length changes.
- UI telemetry layers ignore unknown keys thanks to TypeScript intersection types; ensure new personality blocks land under optional properties and document defaults.
- Snapshot importers deserialize telemetry via `dict.get`, so extra fields are tolerated, but downstream processors require explicit handling if traits become mandatory.

## Rollback Controls
- Behaviour-only traits continue to gate through `features.behavior.personality_profiles`.
- Needs/reward scaling already controlled via `features.behavior.reward_multipliers`.
- Observation tensor change will ship behind a new `features.observations.personality_channels` flag (to be added in Phase 3 implementation) so operators can revert to legacy tensors without disabling other personality features.
- Telemetry personality exposure will piggyback on the same flag; documentation updates will highlight the toggle and expected schema deltas.

## Fixture Preparation
- Golden narration fixture previously cloned to `tests/data/baselines/demo_story_arc_narrations_baseline.json` for regression checks.
- Observation and telemetry baselines above provide pre-change references for shape/KPI assertions.
- No schema migrations required yet; if new telemetry blocks become mandatory, a versioned schema key will be added alongside the rollout flag.

## Next Steps (Phases 3.1–3.2)
1. Gate personality observation channel behind the new feature flag and append trait metadata to observation payloads.
2. Update observation/BC tests and regenerate fixtures to include the additional channel.
3. Publish personality profile data in telemetry snapshots and extend client decoders/tests to cover the new fields.
