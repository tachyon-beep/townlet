# Project Progress Tracker (2025-09-26)

## Completed Work Packages
- Employment Loop Hardening (R1–R7 mitigated; default config enabled).
- Observation Tensor Upgrade (hybrid tensors implemented; samples published).
- Telemetry Consumer Tooling (schema versioning, validator, dashboard MVP).
- Replay DataLoader & PPO Phase 1 (conflict-aware batching, torch scaffolding).
- Rollout Capture Foundations (PolicyRuntime metrics logging, capture CLI, scenario groundwork).

## Upcoming Work Packages
1. **Observer UI Integration** (`docs/WORK_PACKAGE_OBSERVER_UI.md`)
   - Owner: DevEx/UX
   - Status: In progress (telemetry client + dashboard shipped).
   - Next: usability capture, legend tweaks, concurrency executor polish, review feedback backlog.
2. **Conflict Intro (M2.5)**
   - Owner: Systems/Gameplay
   - Status: In progress (queue fairness + rivalry scaffolding underway).
   - Next: risk reduction activities, telemetry/tests per work package.
3. **PPO Integration Phase 2** (`docs/WORK_PACKAGE_PPO_INTEGRATION.md`)
   - Owner: RL/Training
   - Status: In progress (loss/optimizer + rollout capture landed).
   - Next: integrate scripted scenarios, regress on captured datasets, finalize telemetry export.
4. **Renderer/Geometry Enhancements**
   - Dependent on observer UI feedback; adds real object coordinates to `WorldState.local_view`.

## Open Risks
- UI toolkit decisions (Observer UI work package).
- Geometry fidelity for observation map (renderer roadmap).
- PPO performance tuning once torch models active (loss/optimizer integration).

## Next Decision Points
1. Observer UI MVP toolkit sign-off (Rich/Textual vs web).
2. Conflict Intro telemetry/metrics prioritisation vs UI polish.
3. PPO Phase 2 scope approval (loss/optimizer implementation).
## Remaining Milestones
- **M2.5 Conflict Intro**
  - Phases: Queue fairness polish → Rivalry events → Telemetry validation
  - Tasks: reservation manager upgrades, rivalry decay tuning, conflict logging
  - Steps: implement ghost-step telemetry, add rivalry unit tests, document ops playbook
- **M3 Relationships Observed**
  - Phases: Social observation encode → Behaviour biasing → Telemetry gating
  - Tasks: embed social tuples, scripted behaviour updates, stability monitoring
  - Steps: update observation builder, add behaviour heuristics, log social KPIs
- **C1 Social Reward Seed**
  - Phases: Reward taps → Narration → Console hardening
  - Tasks: implement chat rewards, rate-limit narration, extend console commands
  - Steps: add reward config, create narration templates, update ops handbook
- **C2 Conflict Avoidance**
  - Phases: Avoidance bonus → Guardrail refinement → Perturbation dry-run
  - Tasks: add reward modifiers, tighten guardrails, run dry-run tests
  - Steps: configure avoidance weights, update tests, log metrics
- **BC Behaviour Cloning Prep**
  - Phases: Trajectory capture → Dataset manifest → Training harness
  - Tasks: record scripted trajectories, build manifests, implement BC pipeline
  - Steps: sample capture CLI, schema validation, BC training script
- **Anneal Scripted→Learned Mix**
  - Phases: Mixed-control scheduler → Safety freeze → Deployment toggle
  - Tasks: design scheduler, implement safety freeze, add deployment controls
  - Steps: scheduler config, freeze tests, ops procedures
- **M4+ (Perturbations, Personality)**
  - Phases: Event scheduler → Personality tuning → Ops polish
  - Tasks/Steps: follow roadmap for price spikes, persona balancing, release docs
