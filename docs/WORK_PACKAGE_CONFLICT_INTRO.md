# Conflict Intro (M2.5) Work Package

## Objective
Introduce basic conflict dynamics so interactive queues recover from friction, rivalry scaffolding is persisted and observable, and narrative hooks surface conflict beats without destabilising the employment/economy loops.

## Scope
- Queue fairness and reservation orchestration (`src/townlet/world/queue_manager.py`, `src/townlet/world/grid.py`).
- Rivalry state storage/decay on agents and scheduler hooks (`src/townlet/world/grid.py`, `src/townlet/agents`).
- Behavior and planner updates to react to queue fairness + rivalry flags (`src/townlet/policy`, `src/townlet/agents`).
- Narrative & telemetry reporting (`src/townlet/telemetry`, `src/townlet/console`, `src/townlet_ui`).
- Documentation & samples in `docs/` and `docs/samples/`.

## Dependencies
- Observer UI follow-ups (usability capture, perf probe) signed off.
- Employment metrics stable for two evaluation windows.
- Observation tensor fields reserved for rivalry already exposed (hybrid variant).

## Deliverables
1. Fair-queue reservation manager that detects and resolves deadlocks, enforces cooldowns, and emits metrics.
2. Rivalry scaffolding with configurable decay/admission, telemetry exposure, and placeholders for future relationship logic.
3. Behavior fallback rules so scripted/learning agents respect rivalry but fall back to need overrides when scarcity thresholds are hit.
4. Narrative + telemetry events (`conflict_detected`, `queue_recovered`, rivalry diagnostics) wired into console/UI.
5. Updated documentation: work package doc, architecture interfaces, implementation notes, ops handbook, telemetry changelog.
6. Automated tests (unit, property, integration, UI snapshot) and sample payloads containing queue/rivalry data.

## High-Level Tasks
1. **Spec & Design Alignment**
   - Extract conflict specifics from `docs/CONCEPTUAL_DESIGN.md` and requirements section 5.
   - Finalise rivalry attribute schema (caps, decay functions, thresholds) and queue fairness parameters.
   - Document config additions/changes (e.g., `queue_fairness`, rivalry decay config block).
2. **Queue Fairness Enhancements**
   - Extend `QueueManager` for multi-tile queues, stall metrics, and fairness instrumentation.
   - Add reservation snapshots and telemetry wiring.
   - Integrate ghost-step/cooldown behaviour with narrative hooks.
3. **Rivalry State & Persistence**
   - Add rivalry fields to `AgentSnapshot` and persistence layers.
   - Implement rivalry update pipeline (queue conflict increments, decay pass, cap enforcement).
   - Surface rivalry metadata in observations and planner masks.
4. **Behavior & Scheduler Updates**
   - Update scripted behaviour to consider rivalry weights when selecting queue targets.
   - Ensure need overrides bypass rivalry avoidance when critical.
   - Prepare planner hints (e.g., `rival_in_queue`) for RL usage.
5. **Telemetry, Console, UI**
   - Version telemetry schema, extend snapshots and console commands.
   - Update Rich dashboard with queue backlog/rivalry badges, legends, and warnings.
   - Capture new sample payloads and observer UI screenshots/GIFs.
6. **Validation & Documentation**
   - Add deterministic queue fairness tests, rivalry decay unit tests, telemetry serialization checks, and dashboard snapshot tests.
   - Run extended smoke (≥2 days sim) to ensure no regressions.
   - Update docs (`ARCHITECTURE_INTERFACES.md`, `IMPLEMENTATION_NOTES.md`, `OPS_HANDBOOK.md`, `TELEMETRY_CHANGELOG.md`, roadmap/progress trackers).

## Risk Register
| ID | Risk | Prob | Impact | Exposure | Early Indicators | Mitigation | Contingency | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Queue fairness changes stall existing loops or starve agents. | Medium | High | High | Smoke sims show stalled queues; needs drop during queues. | Build deterministic queue fairness tests and run long smokes; gate rollout behind config flag. | Revert fairness changes, restore previous config, capture incident note. | Simulation lead |
| C2 | Rivalry state drifts or explodes, blocking future relationship phases. | Medium | Medium | Medium | Rival counts exceed cap; decay tests fail; telemetry shows runaway rivalry. | Implement decay cap tests; expose diagnostics; include config clamps. | Disable rivalry increments, keep queue fairness only until fixed. | Systems architect |
| C3 | Telemetry/schema churn breaks observer tooling. | Low | High | Medium | Dashboard snapshot tests fail; schema compatibility warnings. | Version schema, provide fixtures, extend serialization tests. | Ship compatibility shim or pin UI to prior schema while patching. | Telemetry lead |
| C4 | Behavior heuristics cause avoidance to starve critical needs. | Medium | Medium | Medium | Agents skip meals/sleep while rivals present; need fallback triggers. | Implement need override thresholds; log override invocations. | Relax avoidance weighting, re-run smokes, document impact. | Policy owner |
| C5 | Performance regression from extra bookkeeping. | Low | Medium | Low | Tick duration increases >5%; profiling hot spots. | Benchmark fairness/rivalry loops; optimise or cache data. | Disable detailed metrics, defer rivalry until optimised. | Performance owner |
| C6 | Narrative spam overwhelms UX. | Low | Medium | Low | Console/UI flooded with conflict events. | Add narration throttle + UX checklist review before enabling. | Reduce event emission frequency, rework messaging. | UX lead |

## Risk Reduction Activities
1. Draft this work-package doc, ensure design artefacts and config tables captured (C1, C2).
2. Build deterministic queue fairness test harness (unit + property) and wire into CI (C1, C5).
3. Prototype rivalry transition fixtures and observation coverage, including decay/threshold tests (C2, C4).
4. Bump telemetry schema version, extend dashboard tests, and add fixture-driven serialization checks (C3).
5. Instrument tick/perf metrics around queue/rivalry updates and compare against baseline (C5).
6. Define narration throttling plus UX review checklist before enabling conflict events (C6).

## Acceptance Criteria
- Queue fairness metrics demonstrate cooldown and ghost-step behaviour in tests and telemetry.
- Rivalry fields persist across ticks, decay toward zero without activity, and are visible in observations/telemetry.
- Behavior heuristics respect rivalry while honouring need overrides; smokes show no starvation spikes.
- Telemetry schema version increments with documented changes and updated fixtures; observer UI handles new fields.
- Performance delta within ±5% of prior tick timing; instrumentation logs included in PR notes.
- Narrative events rate-limited; UX review sign-off recorded.

## Verification Checklist
- [ ] Unit tests for queue fairness edge cases.
- [ ] Property-based tests covering random queue stall scenarios.
- [ ] Rivalry decay/increment unit tests with cap assertions.
- [ ] Telemetry serialization + observer UI snapshot tests.
- [ ] Long-running smoke (≥2 in-sim days) with metrics diff to baseline.
- [ ] Documentation updates merged with cross-links to roadmap and design.
- [ ] UX checklist completed and stored in `docs/`.

## Reporting
- Update `docs/MASTER_PLAN_PROGRESS.md` and `docs/MILESTONE_ROADMAP.md` upon completion.
- Capture telemetry sample in `docs/samples/conflict_intro_snapshot.json` (to be generated).
- Log stakeholder sign-off in `docs/IMPLEMENTATION_NOTES.md`.
