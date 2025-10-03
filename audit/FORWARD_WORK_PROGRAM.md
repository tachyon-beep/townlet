# Forward Work Program – Townlet Tech Demo

Derived from `docs/external/Forward Work Program for Townlet Tech Demo.pdf`, this document re-casts each forward work package with actionable detail, risk highlights, and the primary components we expect to modify.

## FWP-01 Restore Simulation Loop Execution & Smoke Tests *(Completed)*
- **Fix / Change**: CLI now runs `loop.run_for(...)`, closes telemetry, reports tick statistics, and exposes `--stream-telemetry` / `--telemetry-path` flags for output control. Smoke tests cover default, streaming, and file sink cases.
- **Risks**: Verified minimal—default runs stay quiet, telemetry flags tested; no outstanding issues.
- **Affected Components**: `scripts/run_simulation.py`, `tests/test_run_simulation_cli.py`, quickstart docs (`README.md`, `docs/guides/CONSOLE_DRY_RUN.md`).
- **Validation**: `pytest tests/test_run_simulation_cli.py`; manual runs for default, `--stream-telemetry`, and `--telemetry-path` modes.

## FWP-02 Strengthen Core Loop Stability with Tests *(Completed)*
- **Fix / Change**: Added `SimulationLoop.run_for_ticks()` (used by tests and CLI helpers), expanded simulation/training CLI subprocess tests, and documented the helper in the console dry-run guide.
- **Risks**: Minor—CLI tests increase runtime slightly; existing mypy variance warnings remain and should be addressed separately.
- **Affected Components**: `src/townlet/core/sim_loop.py`, `tests/test_sim_loop_structure.py`, `tests/test_training_cli.py`, docs (`docs/guides/CONSOLE_DRY_RUN.md`).
- **Validation**: `pytest tests/test_sim_loop_structure.py tests/test_run_simulation_cli.py tests/test_training_cli.py`; spot-checked CLI flows (`run_simulation`, `run_training --mode replay`); `mypy src/townlet/core/sim_loop.py` still flags pre-existing variance issues (not a regression).

## FWP-03 Complete Observation & Reward Plumbing *(Completed)*
- **Fix / Change**: Compact observations now include normalized local summaries (agent/object/reservation ratios, nearest-agent distance) with metadata in `local_summary`. Reward guardrails verified via new termination-window tests.
- **Risks**: Compact feature vector grew slightly; downstream consumers should rely on metadata (`feature_names`, `local_summary`) rather than positional assumptions.
- **Affected Components**: `src/townlet/observations/builder.py`, `tests/test_observation_builder_compact.py`, `docs/design/OBSERVATION_TENSOR_SPEC.md`, `tests/test_reward_engine.py`.
- **Validation**: `pytest tests/test_observation_builder_compact.py tests/test_observation_builder.py tests/test_reward_engine.py`.

## FWP-04 Optimize Performance for Longer Runs *(Completed)*
- **Fix / Change**: Observation builder now caches agent/object/reservation lookups per tick and reuses them to build map tensors and local summaries in O(radius²). Compact metadata exposes `local_summary` for debugging.
- **Risks**: Cache rebuild happens once per batch; regenerate caches if future workflows mutate agents mid-build. Telemetry stdout still noisy unless muted via CLI flags.
- **Affected Components**: `src/townlet/observations/builder.py`, `tests/test_observation_builder*.py`, `docs/engineering/WORLDSTATE_REFACTOR.md`.
- **Validation**: `pytest tests/test_observation_builder.py tests/test_observation_builder_compact.py tests/test_run_simulation_cli.py tests/test_training_cli.py`; ad-hoc timing showed ~226 → ~395 ticks/sec (10 agents) improvement in quick benchmark.

## FWP-05 Telemetry Reliability & Diff Streaming *(Completed)*
- **Fix / Change**: Telemetry publisher now supports diff-mode streaming (first payload snapshot, subsequent payloads `payload_type = diff` with `changes`/`removed` sections) and exposes worker/queue health metrics. UI clients merge diffs automatically.
- **Risks**: Consumers must respect `payload_type` and apply diffs in order; large sections still emit whole-block changes when content shifts significantly.
- **Affected Components**: `src/townlet/telemetry/publisher.py`, `src/townlet_ui/telemetry.py`, `tests/test_telemetry_stream_smoke.py`, `docs/telemetry/TELEMETRY_CHANGELOG.md`, `src/townlet/config/loader.py`.
- **Validation**: `pytest tests/test_telemetry_stream_smoke.py tests/test_ui_telemetry.py tests/test_telemetry_client.py`; manual `run_simulation.py --stream-telemetry` spot-check; diff payloads verified to reduce repeated sections in file transport logs.

## FWP-06 Finalize Observer Dashboard UI *(Completed)*
- **Fix / Change**: Rich dashboard now paginates agent cards with sociability/alert overlays, surfaces a perturbation status banner, renders all KPI metrics, and exposes CLI pagination controls. Audio playback remains out-of-scope for CLI/Rich UI but documented for future web work.
- **Risks**: Rendering performance acceptable in benchmarks; Rich Live refresh handles real-time updates. Coordinate with web observer initiative for audio accessibility.
- **Affected Components**: `src/townlet_ui/dashboard.py`, `scripts/observer_ui.py`, `tests/test_dashboard_panels.py`, `tests/test_observer_ui_dashboard.py`, docs (`docs/design/DASHBOARD_UI_ENHANCEMENT.md`, `docs/guides/OBSERVER_UI_GUIDE.md`).
- **Validation**: `pytest tests/test_dashboard_panels.py tests/test_observer_ui_dashboard.py tests/test_observer_ui_script.py`; manual `scripts/observer_ui.py --config configs/examples/poc_hybrid.yaml --ticks 10 --refresh 0.5` smoke run.

## FWP-07 Decide on Web GUI vs. Console
- **Fix / Change**: Decide whether to invest in a lightweight web observer, capturing requirements (audio cues, accessibility, remote viewing) and, if proceeding, outline telemetry bridge and deployment plan.
- **Risks**: Parallel UI stacks risk diverging UX and doubling maintenance; web stack introduces auth/sandbox concerns.
- **Affected Components**: Decision record under `docs/program_management/`, potential new `townlet_web/` prototype, ops guide updates if web UI lands.
- **Validation**: Documented decision + spike results; if approved, initial telemetry echo test from browser.

## FWP-08 Demo Scenario Scripting & QA
- **Fix / Change**: Script a narrative-driven demo using `DemoScheduler`, rehearse perturbations/console triggers, and ensure telemetry narrations tell the story.
- **Risks**: Time-sensitive scripts can flake; heavy scheduling might strain stability; demo drift if config changes are untracked.
- **Affected Components**: `src/townlet/demo/timeline.py`, `scripts/demo_run.py`, `configs/scenarios/`, narrative tests (`tests/test_demo_timeline.py`).
- **Validation**: Full demo rehearsal (CLI + UI), verify narration stream, document operator checklist.

## FWP-09 Agent Personalities & Diversity
- **Fix / Change**: Introduce personality profiles affecting needs, rewards, and action bias; expose traits in observations and UI.
- **Risks**: Behaviour variance could destabilize training; balancing traits requires tuning; UI clutter if not well presented.
- **Affected Components**: `src/townlet/agents/models.py`, `src/townlet/policy/behavior.py`, `src/townlet_ui/dashboard.py`, relevant tests (`tests/test_behavior_rivalry.py`, `tests/test_dashboard_panels.py`).
- **Validation**: Behavioural regression tests, telemetry summaries highlighting trait-driven outcomes, updated documentation.

## FWP-10 Personal Agent Inventories & Items
- **Fix / Change**: Add inventory system for agents (e.g., meals/tools), integrate with affordances and telemetry, and display inventory state.
- **Risks**: Data model expansion may impact snapshots; inventory state must serialize cleanly; observer UI must handle new metadata.
- **Affected Components**: `src/townlet/world/grid.py`, `src/townlet/world/affordances.py`, `src/townlet_ui/dashboard.py`, tests (`tests/test_affordance_hooks.py`, `tests/test_observer_payload.py`).
- **Validation**: Unit tests for new affordances, snapshot migration checks, UI verification for inventory icons.

## FWP-11 Richer Social Interactions & Relationships
- **Fix / Change**: Add organic chat/conflict affordances, scripted social vignettes, and richer narrative logging.
- **Risks**: Event spam could overwhelm telemetry; balancing social rewards critical; narrative logging must avoid performance regressions.
- **Affected Components**: `src/townlet/world/relationships.py`, `src/townlet/rewards/engine.py`, `src/townlet/telemetry/narration.py`, social tests (`tests/test_relationship_metrics.py`, `tests/test_telemetry_narration.py`).
- **Validation**: Social event regression tests, narrative playback checks, telemetry diff validation.

## FWP-12 Extended Visualization & Feedback
- **Fix / Change**: Enhance console/global map views, agent highlights, optional audio cues, and ensure new stats (inventory, personality) are visible.
- **Risks**: Visualization updates might desync from telemetry; audio support raises accessibility/config complexity; map rendering must scale.
- **Affected Components**: `src/townlet_ui/dashboard.py`, `src/townlet_ui/telemetry.py`, optional web visualizer, docs (`docs/design/DASHBOARD_UI_ENHANCEMENT.md`).
- **Validation**: UI manual checks, telemetry-client contract tests, documentation walkthrough.

## FWP-13 Polish, Testing, and Tuning
- **Fix / Change**: Execute long-running sims, expand tests for new features, tune rewards/needs to hit KPIs, and refresh documentation.
- **Risks**: Schedule pressure as this work is open-ended; risk of chasing emergent edge cases; documentation drift if not maintained.
- **Affected Components**: Cross-cutting (reward configs, telemetry KPIs, docs in `docs/ops/`, `docs/program_management/`), CI scripts.
- **Validation**: Extended soak tests (`pytest -m slow` where applicable), KPI monitoring, final doc review.
