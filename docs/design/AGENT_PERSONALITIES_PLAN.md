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
- Introduce `features.behavior.reward_multipliers` toggle to disable needs/reward scaling independently.
- Config loader: reject unknown profiles when flag disabled; stage new schema behind optional config entry.
- Telemetry/observation exports gated behind the same flag to preserve backward compatibility.
- Document toggle usage in release notes and playbook to allow quick rollback if traits destabilise training/demos.

## Behaviour & Rewards Integration Prep (2025-10-28)
- Baseline snapshot captured via `seed_demo_state` + 150 ticks: avg needs ≈ hunger 0.22, hygiene 0.332, energy 0.276; mean per-tick reward ≈ -0.153974 (`tests/data/baselines/demo_story_arc_personality_baseline.json`).
- Behaviour touch-points audited: scripted controller (`src/townlet/policy/behavior.py`), policy runner queue handling (`src/townlet/policy/runner.py`), BC dataset/policy adapters (`src/townlet/policy/bc.py`, `src/townlet/policy/scripted.py`), demo/console spawn paths (`src/townlet/demo/runner.py`, `src/townlet/world/grid.py`).
- Telemetry consumers checked: Rich dashboard (`src/townlet_ui/dashboard.py`) and web UI selectors (`townlet_web/src/utils/selectors.ts`) rely on needs/reward scalars only; no schema additions planned, so downstream compatibility risk is low.
- Rollback levers: new `features.behavior.personality_profiles` flag will gate behaviour/reward multipliers; reward engine will honour the flag so ops can disable traits without reverting configs.
- Fixtures cloned for regression tolerance: golden narration snapshot copied to `tests/data/baselines/demo_story_arc_narrations_baseline.json`; KPI baselines captured in `tests/data/baselines/demo_story_arc_personality_baseline.json` (flag off) and `tests/data/baselines/demo_story_arc_personality_feature_on.json` (flag on) for delta-aware tests.
