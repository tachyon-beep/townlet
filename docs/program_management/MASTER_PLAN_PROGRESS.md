# Project Progress Tracker (2025-10-06)

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

- **WP-06 – Telemetry Publishing Hardening (Completed 2025-10-04):** transport abstraction (stdout/file/tcp) with buffered delivery + retry status, console/observer telemetry exposes transport health, smoke command + docs updated, regression suites cover transport buffer/backpressure/failure cases.
- **WP-07 – Conflict & Rivalry Systems (Completed 2025-10-05):** queue fairness counters, rivalry decay/avoidance, telemetry snapshots (queue history + rivalry events), scenario baselines, console runbook, and regression suites shipped.
- **Milestone M5 – Behaviour Cloning & Anneal (Completed 2025-10-06):** dataset capture, BC/anneal harness, release bundle archived at `artifacts/m5/release_bundle/`.
## In-Flight Work Packages
1. **Observer UI Integration** (`docs/work_packages/WORK_PACKAGE_OBSERVER_UI.md`)
   - Owner: DevEx/UX
   - Status: In progress — Phases 6A–6H verified on 2025-10-06 (observer UI & policy inspector). Audio toggle pending design; remaining tasks: implement toggle + documentation once approved.
   - Next: schedule audio-toggle implementation (Phase 6E) and UI usability capture work.
2. **PPO Telemetry Monitoring** (`docs/work_packages/WORK_PACKAGE_PPO_PHASES_2_4.md` follow-up)
   - Owner: RL/Training
   - Status: Operational (soak harness artefacts archived; monitoring handed to ops).
   - Next: schedule periodic soak runs, wire results into ops review cadence.

## Upcoming Milestones (see `PROJECT_PLAN.md` for detail)
- **M4 – Social Foundations** (Completed 2025-09-30)
- **M5 – Behaviour Cloning & Anneal** (Completed 2025-10-06)
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
