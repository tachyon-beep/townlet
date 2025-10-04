# Agent Personalities – Phase 0 Notes

## Baseline Behaviour Snapshots (2025-10-24)
- `configs/examples/poc_hybrid.yaml` (no seeded agents): avg reward ≈ 0 over 10 ticks; agent count 0.
- `configs/scenarios/demo_story_arc.yaml` with `seed_demo_state` (150 ticks): avg reward ≈ -0.462 per tick; 3 seeded agents (sample `demo_1#1` needs: hunger ≈ 0.17, hygiene ≈ 0.30, energy ≈ 0.24).
- These values provide a regression baseline once personality deltas are introduced.

## Telemetry & UI Consumers Impacted
- `townlet_ui` Rich dashboard (`src/townlet_ui/dashboard.py`, `src/townlet_ui/telemetry.py`).
- Web spectator/operator client (`townlet_web/src/utils/selectors.ts`, UI panels, audio hooks).
- CLI tools/tests relying on telemetry snapshots (`tests/test_console_commands.py`, `tests/test_observer_ui_dashboard.py`, `tests/test_web_telemetry` fixtures).
- Golden narration fixture (`tests/data/demo_story_arc_narrations.json`) and rehearsal docs (`docs/ops/DEMO_SCENARIO_PLAYBOOK.md`).

## Feature Flag / Rollback Strategy
- Introduce `features.behavior.personality_profiles` toggle (default `false`).
- Config loader: reject unknown profiles when flag disabled; stage new schema behind optional config entry.
- Telemetry/observation exports gated behind the same flag to preserve backward compatibility.
- Document toggle usage in release notes and playbook to allow quick rollback if traits destabilise training/demos.
