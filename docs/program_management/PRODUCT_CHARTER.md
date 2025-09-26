# Townlet Product Charter (v1.1)

## Vision
Deliver an always-on small-town simulation where 6–10 reinforcement-learning agents grow from scripted primitives into emergent daily routines, delighting viewers while proving the viability of configurable, observable DRL sandboxes for social storytelling.

## Objectives
- Prove the Townlet simulation loop can sustain needs, jobs, and light social dynamics without collapse through Milestone M3, then extend into the social/perturbation roadmap captured in `PROJECT_PLAN.md`.
- Demonstrate PettingZoo-based training + evaluation that promotes stable policies via release/shadow separation, with soak-tested drift analytics and promotion guardrails.
- Showcase console-driven live operations so humans can perturb the world safely during demos and streams, including observer dashboards, narration, and policy inspector tooling.

## Success Metrics (KPIs)
- Self-sufficiency ≥70% of agents with all needs >0.3 maintained for 24h simulated time.
- Job tenure mean ≥3 in-sim days with lateness <15% during Milestones M2–M3.
- Relationship formation: ≥60% of agents hold at least one |trust| or |rivalry| tie >0.3 by Phase C.
- Runtime throughput ≥4k env-steps/sec on 8×8 agents in headless training with hybrid observations.

## Scope (Phases A–C)
- **Phase A (M0–M2)**: scripted primitives, needs loop, wage economy, console + observer API stubs. ✅ Simulation, economy, and employment loops are implemented.
- **Phase B (M3)**: relationships surfaced in observations, action biasing, perturbation scheduler gated off. 🔜 Planned in `PROJECT_PLAN.md` milestones M4–M6.
- **Phase C (C1–C3/M4+)**: social rewards, conflict hooks, narration overlays, perturbation scheduler, behaviour-cloned primitives with anneal. 🔜 Captured in milestones M4–M9 with phased delivery.

## Non-Goals
- No 3D renderer or large (>10 agents) towns in the demo window.
- No full-production security hardening; console auth is scoped to bearer tokens and audit logs.
- No live monetisation loops; economy stays closed.

## Guardrails & Constraints
- Config changes require `config_id` bump and promotion gate; variant swaps must pass A/B evaluation.
- Reward clips, death/exit guard, and exit caps enforced to protect PPO stability.
- Embedding slots observe a two-day cooldown before reuse; log reuse when pool pressure forces recycling.

## Stakeholders & Ownership
- Product: Program Manager (charter keeper).
- Architecture: Technical Lead (AI agent) + Architecture Lead human sponsor.
- Ops: Operations and RL leads co-own release/shadow, telemetry, and runbooks.
- Developer Experience: maintains CONTRIBUTING.md and AGENTS.md alignment.
- Security/Privacy: owns telemetry redaction and data retention policy drafts.

## Status Snapshot (2025-09-29)
- **Delivered**: Employment loop hardening, observation tensor upgrade, telemetry consumer tooling, replay/PPO Phase 1, rollout capture foundations, PPO Phases 2–4 hardening with soak harness.
- **In Progress**: Observer UI integration, conflict intro hardening, long-run telemetry monitoring (ops owned).
- **Planned**: Social foundations, BC/anneal, observer experience, promotion governance, perturbations, and personality polish per milestones M4–M9.

## Immediate Next Steps
1. Keep `PROJECT_PLAN.md` and `WORK_PACKAGES.md` in sync with charter objectives; review milestones at each sprint planning session.
2. Ensure every new milestone/phase carries risk assessments per the risk standard in `README.md`.
3. Maintain KPI dashboards and soak harness outputs so charter success metrics are continuously monitored.
