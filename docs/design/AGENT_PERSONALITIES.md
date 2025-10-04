# Agent Personalities – Implementation Notes (2025-11-07)

This document summarises the end-to-end enablement of personality profiles in Townlet.
Phase-by-phase planning lives in `docs/design/AGENT_PERSONALITIES_PLAN.md`; the notes
below reflect the final implementation state after Milestone 4.

## 1. Data Model & Configuration

- Personality profiles (`src/townlet/agents/models.py`) define trait vectors and bias
  multipliers for behaviour, needs decay, and reward scaling.
- Profiles are assigned deterministically via
  `SimulationConfig.resolve_personality_profile()` using seed + agent id.
- Feature flags:
  - `features.behavior.personality_profiles` – enables behaviour/needs overrides.
  - `features.behavior.reward_multipliers` – gates reward scaling separately.
  - `features.observations.personality_channels` – adds trait channels to observation
    tensors + telemetry metadata.
  - `features.observations.personality_ui` – controls whether UI surfaces render
    badges/filters (CLI already respected this; web dashboard now checks the same flag).
- Telemetry configuration adds a dedicated
  `telemetry.personality_narration` section for thresholds and enablement (see
  `configs/examples/poc_hybrid.yaml`).

## 2. Behaviour & Reward Integration

- Scripted behaviour (`src/townlet/policy/behavior.py`) applies bias multipliers
  for queue patience, chat inclination, and conflict avoidance when profiles are enabled.
- Reward engine (`src/townlet/rewards/engine.py`) scales needs and episodic
  rewards according to profile multipliers when `reward_multipliers` is on.
- Tests: `tests/test_behavior_rivalry.py`, `tests/test_relationship_personality_modifiers.py`,
  `tests/test_reward_engine.py` exercise the bias paths and personality scaling.

## 3. Observation & Telemetry

- Observation builder extends hybrid tensors with three personality channels and
  metadata enumerating profile/traits per agent when the feature flag is active.
- Telemetry publisher (`src/townlet/telemetry/publisher.py`) snapshots the
  per-agent profile/trait map (`personalities` block) and exposes it to both UI clients.
- UI telemetry client (`src/townlet_ui/telemetry.py`, `townlet_web/src/utils/telemetryTypes.ts`)
  parses the new block into structured entries.

## 4. UI Surfaces

- **Rich dashboard** (`src/townlet_ui/dashboard.py`):
  - Agent cards show colour-coded profile badges, trait summaries, and behaviour bias hints.
  - Command palette offers quick filters (`filter:profile:<name>`, `filter:trait:ext>=0.5`).
  - CLI flag `--personality-filter` pre-filters agent cards; `--mute-personality-narration`
    hides trait-driven narration entries at runtime.
- **Web spectator** (`townlet_web/src/App.tsx`):
  - Agent grid mirrors CLI badges and trait summaries with tooltips.
  - Profile/trait filter controls with accessible labels.
  - Narration log highlights personality events and includes a “Show personality stories” toggle.

## 5. Narration Pipeline

- Telemetry publisher emits `personality_event` narrations for:
  - High-extroversion chats above `chat_extroversion_threshold` & `chat_quality_threshold`.
  - Low conflict tolerance avoidance events below `conflict_tolerance_threshold`.
- Rate limiter configured with a dedicated `category_cooldown` (default 45 ticks) to
  keep narration volume bounded.
- Tests: `tests/test_telemetry_narration.py::test_personality_narration_*`,
  CLI panel coverage in `tests/test_dashboard_panels.py::test_render_snapshot_filters_personality_narrations_when_muted`,
  and web toggle behaviour in `townlet_web/src/__tests__/App.test.tsx`.

## 6. Rollback & Operational Controls

- Disable behaviour impact: set `features.behavior.personality_profiles = false`
  (disables both bias + needs scaling) and `features.behavior.reward_multipliers = false`.
- Hide UI presentation only: set `features.observations.personality_ui = false` or pass
  `--mute-personality-narration` / uncheck “Show personality stories” in web UI.
- Observation/telemetry fallback: set `features.observations.personality_channels = false`
  to drop additional tensor channels + metadata for legacy clients.

## 7. Documentation & Playbooks

- Operator workflow updates: see `docs/ops/DEMO_SCENARIO_PLAYBOOK.md` for CLI flag usage
  and `docs/guides/OBSERVER_UI_GUIDE.md` for badge/filter toggles.
- Forward Work Program entry FWP-09 records completion, config hashes, and validation steps.

## 8. Validation Summary

- Automated: full `pytest` suite (452 tests) and `townlet_web` vitest suite (16 tests).
- Manual: `python scripts/demo_run.py --scenario demo_story_arc --ticks 60 --personality-filter stoic`
  and `--mute-personality-narration` smoke runs; Storybook smoke test ensures React
  components compile with the new props.

## 9. Key Config Hashes

- `configs/examples/poc_hybrid.yaml` – `8f7c94db0183e2d88a8f689968dca51a5decf251`
- `configs/demo/poc_demo.yaml` – `58431c8e61d4efd34420859b2c22ca9d13557ef9`
- `configs/demo/poc_demo_tls.yaml` – `0214debcffcd0064708454f970dd0627aad928ce`

## 10. Follow-Up Work (if needed)

- Consider per-trait narration categories if future storytelling needs more
  granular filtering (e.g., differentiate extroversion vs conflict tolerance events).
- Monitor training stability with personality biases enabled for extended runs;
  update baselines if KPIs drift.
- Capture updated screenshots/logs for ops handbook once milestone sign-off is complete.
