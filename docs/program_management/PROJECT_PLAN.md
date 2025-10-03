# Townlet Delivery Project Plan

## Objectives

- Close policy gaps identified in the latest repository audit, ensuring strict dependency handling, fail-fast behaviour, and guardrails across affordances, observations, and rewards.
- Deliver the remaining systems promised in the conceptual and high-level designs without introducing partial degradations.
- Establish a trackable programme with clear owners, milestones, and risk controls until Townlet meets its documented contracts.

## Governance & Roles

- **Delivery Lead (Engineering Manager):** Owns schedule, unblockers, and weekly status reporting.
- **Simulation Strike Team:** 2 engineers focused on world/affordance and reward subsystems.
- **Observability Squad:** 1 engineer + 1 UX partner covering telemetry, console, and stability workflows.
- **Quality Owner:** 1 SDET responsible for regression automation and policy compliance tests.
- **Doc Steward:** 0.5 FTE technical writer ensuring documentation updates ship with each work package.

## Milestones

| Milestone | Target Week | Exit Criteria | Primary Work Packages |
|-----------|-------------|---------------|-----------------------|
| M1 – Runtime Safety | Week 2 | Affordance manifests validated; observation variants gated; reward guardrails enforced with tests. | WP-01, WP-02, WP-03 |
| M2 – Operational Guardrails | Week 4 | Stability monitor thresholds active; console ops validated; telemetry publisher upgraded with schema versioning. | WP-04, WP-06 |
| M3 – Continuity & Conflict Systems | Week 6 | Snapshot persistence functional; conflict/rivalry events flow into observations/rewards; observer UI smoke tests pass. (Status: on track; rivalry system delivered 2025-10-05.) | WP-05, WP-07 |

## Future Milestones (Beyond Remediation)

These milestones map the remaining functionality promised in `docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md` and `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md`. They follow immediately after the remediation backlog so this directory stays the single source of truth for "finished" Townlet scope.

| Milestone | Target Window* | Scope Highlights | Exit Criteria |
|-----------|----------------|------------------|---------------|
| M4 – Social Foundations | Week 8 | Implement trust/familiarity storage, social observation snippets, and chat reward taps (Phase C1); add narration throttling and event dedupe. | Relationships persist per design, observer UI shows top ties, chat rewards reflected in telemetry; narration spam guard verified. |
| M5 – Behaviour Cloning & Anneal | Week 10 | Capture scripted trajectories, stand up BC training harness, and introduce the mixed scripted→learned anneal scheduler. | BC accuracy ≥90% on held-out data, anneal runs with rollback guard, mixed-control tests green. |
| M6 – Observer Experience & Policy Inspector | Week 12 | Deliver policy inspector panels, relationship overlay, audio toggles, KPI dashboard, and anneal promotion indicators. | Viewer session exercises overlays/inspector without schema mismatches; ops handbook updated with UI workflows; anneal panel reflects latest gate state. |
| M7 – Promotion & Release Governance | Week 14 | Complete stability monitor automation, golden rollout replay suite, BC/anneal audit cadence, release/shadow promotion tooling, and rollback procedures. | Promotion gate enforces KPIs over consecutive windows; rollback drill documented/tested; dataset audit + anneal rehearsal automation in CI. |
| M8 – Perturbations & Narrative Events | Week 16 | Implement perturbation scheduler (price spikes, outages, arranged meets) with fairness buckets and narrated vignettes; hook into lifecycle UI. | Events fire with cooldowns, UI vignettes render arrival/exit, telemetry captures perturbation metadata. |
| M9 – Personality & Ops Polish | Week 18 | Finalise personality balancing, admin console extensions, streaming privacy mode, and ethics guardrails. | KPI targets hit with personalities enabled, console commands documented/tested, privacy toggle in place. |

*Target windows assume the remediation milestones complete on schedule; adjust during sprint planning.

## Design Alignment

- **M1–M3** close the runtime and operational gaps documented in `docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md` and related requirements.
- **M4** traces to the social relationship and narration features in `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md` §§5–12 and the UI hooks in `docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md` (Telemetry & UI Gateway).
- **M5** covers the behaviour-cloning and scripted→learned handoff described in `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md` §9.
- **M6** delivers the observer experience, policy inspector, and KPI dashboards called out in `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md` §12 and `docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md` (Telemetry/UI modules).
- **M7** aligns with the promotion governance and stability monitor expectations in `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md` §9 and `docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md` (Stability Monitor & Promotion).
- **M8** implements perturbations, narrative events, and lifecycle vignettes from `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md` §§11–12.
- **M9** completes personality polish, console extensions, and privacy/ethics controls described across the design documents’ later phases.

The current codebase already fulfils the PPO Phase 2–4 hardening and telemetry bridge (refer to `docs/rollout/ROLLOUT_PHASE4_ACCEPTANCE.md`). The milestone stack above captures the remaining functionality required to meet the full design specification.


## Iteration Structure

- **Cadence:** Two-week sprints with mid-sprint demos of guarded features (feature flags off in production until DoD met).
- **Backlog Grooming:** Delivery Lead + squads refine WP tasks every Monday; blockers escalated same day.
- **Quality Gates:** No work package closes without (a) unit/integration coverage for happy/sad paths, (b) documentation updates, (c) telemetry assertions when relevant. Telemetry surfaces must ship with the transport+observer smoke command (`pytest tests/test_telemetry_client.py tests/test_observer_ui_dashboard.py tests/test_telemetry_stream_smoke.py tests/test_telemetry_transport.py`).

## Dependency Management

- Align schema validation for affordances with the Doc Steward to publish manifest requirements before implementation freezes.
- Coordinate with Observer UI roadmap so telemetry schema changes ship alongside updated UI snapshots.
- Ensure snapshot storage decisions (WP-05) reuse existing infrastructure from prior PPO phases to avoid new platform work.

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hidden edge cases in legacy YAML manifests | Medium | High | Build dry-run CLI that validates all manifests before rollout; add CI gate. |
| Observation encoder complexity slips schedule | Medium | Medium | Stage delivery: gate unsupported variants first, then implement encoders with golden tensor fixtures. |
| Telemetry transport dependency delays WP-06 | Low | High | Preselect supported transport (e.g., stdout + file sink) as interim solution; fail fast if env vars missing. |
| Snapshot persistence introduces regressions | Medium | High | Maintain deterministic replay tests and the snapshot regression subset (`pytest tests/test_utils_rng.py tests/test_snapshot_manager.py tests/test_snapshot_migrations.py tests/test_sim_loop_snapshot.py`) before enabling in production. |

## Communication Plan

- **Status Reports:** Weekly email + dashboard updates summarising progress against milestones and open risks.
- **Stakeholder Reviews:** End-of-milestone demos with Ops and Product to sign off acceptance criteria.
- **Incident Handling:** Any blocker extending >2 days triggers an escalation meeting with the Delivery Lead and affected squad.

## Acceptance & Exit Criteria

- All work packages WP-01 through WP-07 are delivered, tested, and documented.
- CI pipeline includes linting, type checks, manifest validation CLI, and remediation regression suites.
- Documentation plan updated to reflect the new baseline, and legacy TODOs in code are either resolved or tracked with an owner and due date.
