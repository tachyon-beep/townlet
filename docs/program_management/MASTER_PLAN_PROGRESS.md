# Project Progress Tracker (2025-10-03)

Status companion to `PROJECT_PLAN.md`; use this to record actual delivery progress against the milestone roadmap.

## Completed Work Packages
- Employment Loop Hardening (R1–R7 mitigated; default config enabled).
- Observation Tensor Upgrade (hybrid tensors implemented; samples published).
- Telemetry Consumer Tooling (schema versioning, validator, dashboard MVP).
- Replay DataLoader & PPO Phase 1 (conflict-aware batching, torch scaffolding).
- Rollout Capture Foundations (PolicyRuntime metrics logging, capture CLI, scenario groundwork).
- PPO Integration Phase 2 (rollout ingestion, PPO training loop, telemetry schema/tests, drift analytics tooling).
- PPO Integration Phase 3 (telemetry_version 1.1 schema, streaming cycle IDs, validator/watch/summary tooling, CI harness validation).
  - Ops checklist: `docs/ops/ROLLOUT_PPO_CHECKLIST.md`
- PPO Integration Phase 4 (rollout capture→PPO bridge, queue-conflict telemetry, mixed-mode ops workflow, CI artefact uploads, soak harness drift analysis).
  - 2025-09-29 update: social telemetry metrics surfaced end-to-end (watcher/summary/ops docs); scenario soaks captured for queue_conflict, employment_punctuality, rivalry_decay, kitchen_breakfast, observation_baseline.
- **Milestone M4 – Social Foundations (Completed 2025-09-30):** relationship persistence, social observation snippet, Phase C1 rewards, narration throttle, CI/ops governance.
- **WP-04 – Stability & Console Safeguards (Completed 2025-10-02):** stability monitor guardrails, perturbation scheduler, admin-gated console commands, telemetry/docs/tests updated.
- **WP-05 – Snapshot & Config Identity (Completed 2025-10-03):** SnapshotConfig + migration registry, RNG/state identity, console diagnostics, autosave guardrails, regression coverage.

## In-Flight Work Packages
1. **Observer UI Integration** (`docs/work_packages/WORK_PACKAGE_OBSERVER_UI.md`)
   - Owner: DevEx/UX
   - Status: In progress (telemetry client + dashboard shipped; narration panel delivered).
   - Next: usability capture, legend toggles, concurrency executor polish, documentation refresh.
2. **Conflict Intro (M2.5)** (`docs/work_packages/WORK_PACKAGE_CONFLICT_INTRO.md`)
   - Owner: Systems/Gameplay
   - Status: In progress (queue fairness + rivalry scaffolding underway).
   - Next: ghost-step telemetry, rivalry decay tuning, ops troubleshooting guide.
3. **PPO Telemetry Monitoring** (`docs/work_packages/WORK_PACKAGE_PPO_PHASES_2_4.md` follow-up)
   - Owner: RL/Training
   - Status: Operational (soak harness artefacts archived; monitoring handed to ops).
   - Next: schedule periodic soak runs, wire results into ops review cadence.

4. **M5 Behaviour Cloning Phase 5.4** (`docs/program_management/M5_BEHAVIOUR_CLONING_EXECUTION.md`)
   - Owner: RL/Training
   - Status: Completed (BC dataset catalogued, acceptance smoke logged under `artifacts/m5/acceptance/`, ops & CI guardrails landed).
   - Next: proceed to Phase 5.5 planning (anneal promotion governance).

5. **WP-06 Telemetry Publishing Hardening** (`docs/program_management/MILESTONE_ROADMAP.md`)
   - Owner: Platform/Observer UI
   - Status: Queued — begins next sprint after telemetry lint clean-up; planning workshop scheduled to scope transport wiring and KPI aggregation.
   - Next: lock transport decision, refresh telemetry contract tests, draft ops rollback plan.

## Upcoming Milestones (see `PROJECT_PLAN.md` for detail)
- **M4 – Social Foundations** (Completed 2025-09-30)
- **M5 – Behaviour Cloning & Anneal**: trajectory capture, BC harness, mixed scripted→learned control with rollback guard.
- **M6 – Observer Experience & Policy Inspector**: dashboard overlays, policy inspector, audio toggles, KPI panels.
- **M7 – Promotion & Release Governance**: automated promotion gate, golden rollouts, rollback drills.
- **M8 – Perturbations & Narrative Events**: scheduler fairness buckets, lifecycle vignettes, perturbation telemetry.
- **M9 – Personality & Ops Polish**: personality balancing, admin console extensions, privacy/ethics controls.

## Open Risks
- UI toolkit decision for Observer UI (Rich/Textual vs web) may delay UX polish.
- Observation map fidelity requires geometry enhancements; solution TBD.
- CI runtime may exceed thresholds once Phase 4.5 suites land; monitor after merging expanded tests and split workloads if >20 min.
- Stakeholder go/no-go could surface unmet acceptance criteria late; assemble artefacts and dry-run review ahead of the meeting.
- Behaviour cloning data quality risks (M5) – need representative scripted coverage before training.

## Upcoming Decision Points
1. Observer UI toolkit sign-off (Rich/Textual vs web).
2. Conflict telemetry metric prioritisation vs UI polish trade-offs.
3. Phase 4.5 go/no-go stakeholder review (target early Oct; artefact bundle + checklist).
4. Definition of BC dataset scope and anneal schedule (ties to M5).
