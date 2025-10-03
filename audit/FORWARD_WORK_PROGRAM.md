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

## FWP-07 Decide on Web GUI vs. Console *(In Progress – Web UI Chosen)*
- **Fix / Change**: Proceed with a two-tier web experience: (1) a lightweight read-only spectator UI for demos and remote viewing, and (2) a richer operator console mirroring/augmenting the Rich dashboard (command palette, palette queue, perturbation controls). Establish a shared telemetry bridge (WebSocket + diff snapshots) and UI design tokens to keep parity with the console.
- **Risks**: Dual UI surfaces must stay in sync; authentication/authorization for operator view required; browser rendering load must not exceed telemetry cadence; need to budget for accessibility (audio cues, high-contrast mode) to avoid regressions.
- **Affected Components**: New `townlet_web/` package (React/Vite or similar), telemetry gateway service (FastAPI/FastAPI WebSocket), deployment scripts under `scripts/` or `infra/`, docs updates (`docs/design/WEB_UI_ROADMAP.md`, operator handbook), potential adjustments to `townlet_ui/telemetry.py` for JSON schemas.
- **Validation**: Spike deliverables—telemetry echo in browser and parity checklist vs. Rich dashboard; end-to-end smoke test capturing command dispatch from operator UI; load test of spectator client at demo scale; documentation of rollout plan and fallback (console) procedure.

### Execution Plan

| Milestone | Phase | Goal | Key Deliverables |
|-----------|-------|------|------------------|
| **M0 – Risk Reduction & Foundations** | Phase 0.1 Telemetry Contract | Lock down JSON schema for web transport | Versioned schema doc, unit tests, diff replay fixtures |
| | Phase 0.2 Security & Ops | Baseline auth decision, threat model | Auth requirement brief, OWASP checklist, ops runbook outline |
| | Phase 0.3 UX Alignment | Shared design tokens & layout skeletons | Figma/MD components, console parity checklist |
| **M1 – Spectator Web Viewer MVP** | Phase 1.1 Transport Gateway | WebSocket bridge serving snapshots/diffs | FastAPI service, integration tests |
| | Phase 1.2 Frontend Shell | Static viewer (tick header, agent KPIs, narration feed) | React/Vite project, Storybook stories |
| | Phase 1.3 Demo Hardening | Deployable container + CDN caching | Dockerfile, Terraform/Helm stub, latency metrics |
| **M2 – Operator Console Parity** | Phase 2.1 Command Dispatch | Secure palette queue, command status feed | Web UI command panel, e2e dispatch tests |
| | Phase 2.2 Perturbation & Overlay Panels | Interactive overlays mirroring Rich dashboard | Components + snapshot tests |
| | Phase 2.3 Accessibility & Audio | Screen-reader labels, audio cues | WCAG checklist, audio toggle docs |
| **M3 – Production Readiness** | Phase 3.1 Load & Chaos | Multi-client soak, failover drills | k6 report, chaos test logs |
| | Phase 3.2 Rollout & Training | Ops handbook, feature flags | Updated operator guide, go/no-go checklist |

#### Milestone 0 Tasks (Risk Reduction)
- [x] Establish telemetry schema contract (diff payload examples, versioning strategy, backward-compat tests).
- [x] Author security baseline: auth provider selection (e.g., Auth0 / OAuth proxy), session handling, CSRF plan.
- [x] Draft threat model & mitigations (XSS, WS hijacking, replay, DoS) with mitigation tickets.
- [x] Produce shared design tokens (colours, typography, spacing) and UI parity matrix vs. Rich dashboard panels.
- [x] Build mocked telemetry fixtures for web prototyping (JSON replay, WebSocket simulator).
- [x] Spin up CI scaffold for `townlet_web` (lint, unit, smoke jobs) using placeholder app to validate pipeline.
- [x] Document rollback/fallback plan to Rich console if web stack unavailable.

#### Risk Mitigation Strategy
1. **Parity Drift** – Maintain automated parity tests comparing web snapshots to Rich dashboard render expectations; enforce shared schema via typed client. (Milestone 0: schema contract + design tokens)
2. **Security/Access Control** – Integrate auth at gateway before feature work; apply least-privilege scopes for operator actions. (Milestone 0: security baseline, threat model)
3. **Performance/Lag** – Benchmark WebSocket throughput early, introduce adaptive throttling & caching. (Milestone 0: mocked telemetry fixtures for load testing)
4. **Accessibility** – Bake accessibility requirements into tokens/components before UI build to avoid retrofits. (Milestone 0: design tokens & parity matrix)
5. **Operational Complexity** – Prepare deployment templates and rollback plan before MVP launch. (Milestone 0: CI scaffold, rollback doc)

### Milestone 1 Detailed Plan – Spectator Web Viewer MVP

**Phase 1.1 – Transport Gateway**
- Tasks
  - [x] Draft API contract for `/ws/telemetry` (handshake params, heartbeat cadence).
  - [x] Implement FastAPI-based gateway translating internal pub/sub queue to WebSocket (snapshot + diff streaming).
  - [x] Add tick monotonicity & auth stubs (spectator mode: optional token, operator mode: rejected).
  - [x] Write integration test harness replaying fixtures from `tests/data/web_telemetry` and asserting client merge parity.
  - [x] Instrument gateway with Prometheus metrics (connected clients, messages/sec).
- Dependencies: Milestone 0 schema fixtures, existing telemetry publisher.
- Exit Criteria: Gateway runs locally via `uvicorn`, passes integration tests, emits metrics; documented in `docs/design/WEB_TELEMETRY_SCHEMA.md` appendix.

- **Phase 1.2 – Frontend Shell**
  - [x] Scaffold React/Vite app (TypeScript) using tokens from `docs/design/web_ui_tokens.json`.
  - [x] Implement telemetry client hook applying diff merges (unit tests with Vitest fixtures).
  - [x] Build core read-only components: header status bar, agent summary grid, narration feed (KPI/perturbation TBD).
  - [x] Set up Storybook configuration to capture component snapshots.
  - [x] Add accessibility smoke tests (axe-core) for key screens.
- Dependencies: tokens, parity checklist, gateway contract (mocked if gateway not ready).
- Exit Criteria: `npm run build` produces static bundle; Storybook stories for each component; CI runs lint/test/build.

**Phase 1.3 – Demo Hardening**
- Tasks
  - [x] Containerize gateway + static frontend (Dockerfile + docker-compose sample).
  - [x] Create Helm stub for demo deployment with config toggles (spectator URL, rate limits).
  - [x] Add CDN caching headers for spectator assets; ensure no caching of auth endpoints.
  - [x] Run k6 (or Locust) load test simulating 50 concurrent spectators, collect latency metrics.
  - [x] Document deployment/runbook in `docs/ops/WEB_SPECTATOR_DEPLOY.md`.
- Dependencies: Gateway & frontend phases complete; ops baseline from Milestone 0.
- Exit Criteria: Container images build in CI; load test report meets <250 ms p95 update latency; deployment guide published.

### Milestone 2 Detailed Plan – Operator Console Parity

| Phase | Goal | Tasks | Exit Criteria |
|-------|------|-------|---------------|
| **2.1 Command Dispatch** | Bring operator command palette online via secure WebSocket | 1. Implement authenticated operator channel (JWT/opaque token) and gateway auth middleware. 2. Mirror command queue status/history feed in spectator UI (read-only mode). 3. Build command palette UI with preview/execute toggles, tie into parity checklist. 4. Add sandbox SimulationLoop integration tests dispatching commands end-to-end. | Command dispatch succeeds via web UI against test loop; web and console command logs match; auth required for operator mode. |
| **2.2 Perturbation & Overlay Panels** | Achieve visual parity for overlays (relationships, social, KPIs, perturbations) | 1. Implement observer panels using parity checklist items (relationships, overlays, KPI trends, perturbation banner). 2. Add storybook snapshots + unit tests for each panel. 3. Integrate telemetry hook selectors for performance. 4. Update docs with parity matrix status. | Storybook covers all panels; unit tests snapshot output; parity checklist items under FWP-07 marked complete. |
| **2.3 Accessibility & Audio** | Ensure operator UI is accessible and supports alert audio cues | 1. Keyboard navigation + focus order audit across operator screens. 2. Add ARIA labels/live regions for telemetry updates. 3. Implement opt-in audio cues consistent with console docs (muted by default). 4. Run axe/Storybook accessibility checks; capture results. | WCAG smoke tests pass; audio toggle documented; accessibility report stored in ops docs. |

**Dependencies:** Milestone 1 spectator stack, telemetry gateway auth stubs, parity checklist.

**Exit Criteria:** Operator UI meets parity checklist, end-to-end command dispatch suite passes, accessibility audit documented.

**Progress:**
- ✅ Phase 2.1 Command Dispatch – operator WebSocket auth, command palette UI hooks, status mirroring, and dispatch tests delivered (`tests/test_web_operator.py`).
- ✅ Phase 2.2 Perturbation & Overlay Panels – spectator overlays (perturbations, economy/employment, conflict, KPIs, relationships, social, legend) implemented with selectors, vitest coverage (`townlet_web/src/utils/selectors.test.ts`), and Storybook stories.
- ✅ Phase 2.3 Accessibility & Audio – Added skip-link navigation, ARIA-friendly structure, optional audio cues for high-priority narrations, axe smoke test via Storybook, unit tests for audio hook (`townlet_web/src/hooks/useAudioCue.test.ts`), and Playwright e2e smoke tests for spectator/operator flows (`townlet_web/tests/e2e`).

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
