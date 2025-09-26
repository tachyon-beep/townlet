# Townlet Milestone Roadmap (v0.1)

This roadmap tracks sequencing across Phases A–C. Durations are intentionally unspecified; milestones advance when exit criteria are satisfied.

| Milestone | Theme | Key Deliverables | Dependencies | Exit Criteria |
| --- | --- | --- | --- | --- |
| M0 | Home Sandbox | Core tick loop, needs decay/recovery, affordance loader, observer diff channel skeleton | Baseline configs, reward clamps | Agents sustain hunger/hygiene/energy >0.3 for 1 in-sim day without interventions |
| M1 | Basic Economy | Grocery + cooking affordances, inventory & spoilage flags, wage stipend removal, telemetry for economy | M0 | Agents buy/cook meals; basket sanity check passes; no stock deadlocks over 2 days |
| M2 | Employment Loop | Job scheduling, punctuality window, wage payouts, exit caps, console auth gate | M1 | ≥70% shifts attended on-time; lateness canary wired into stability monitor |
| M2.5 | Conflict Intro | Queue fairness, reservation manager, rivalry placeholder fields, narrative hooks for friction | M2 | Queue deadlocks auto-resolve; rivalry scaffolding emits diagnostics |
| M3 | Relationships Observed | Social snippet in observations, action biasing, stability monitor gating | M2.5 | RL agents incorporate social context without KPI regression >15%; relationships persisted in snapshots |
| C1 | Social Reward Seed | Chat reward taps, narration throttle, console social commands hardened | M3 | Successful chats deliver reward w/out destabilising return variance (>1.5x baseline) |
| C2 | Conflict Avoidance | Add avoidance bonus, refine guardrails, start perturbation dry-run | C1 | Conflict avoidance metrics improve; no starvation spike; promotion gate passes |
| BC | Behaviour Cloning Prep | Capture scripted trajectories, dataset manifest, imitation training harness | C2 | Imitation accuracy ≥90% on held-out scripts; value MSE within tolerance |
| Anneal | Scripted→Learned Mix | Mixed-control scheduler, safety freeze logic, deployment toggle | BC | KPI drop <30% during anneal; rollbacks auto-disable learned head if breached |
| C3 | Relationship Modifiers | Relationship-quality reward modifiers, narration polish, rivalry events | Anneal | Relationship KPIs hit target without exceeding conflict cap; telemetry stable |
| M4 | Perturbation Scheduler | Price spikes, outages, arranged meets, cooldown fairness | C3 | City events fire with logged cooldowns; lifecycle exits suppressed correctly |
| M5 | Personality & Ops Polish | Personality balancing, admin console extensions, release/shadow ops docs | M4 | Release policy promotion loop runs end-to-end with ops handbook ready |

## Cross-Cutting Workstreams

- **Testing & Verification:** Property-based economy checks (M1+), queue fuzz tests (M2.5), chaos suite (M4).
- **Telemetry & Tooling:** Observer schema versioning (M0), KPI dashboards (M2), policy inspector (C-phases), replay capture (M4).
- **Documentation:** Charter & roadmap (Week 1), Architecture Guide (Week 2), Ops Handbook (Week 3), Testing Plan (Week 4), Privacy Policy (Week 5), Contributor alignment (Week 6).

## Sequencing Notes

- Hold perturbations and social rewards behind feature flags until prior KPIs are stable for two consecutive evaluation windows.
- Promotion gates require release/shadow alignment; no observation variant flips without dedicated A/B runs.
- Embedding slot cooldowns and lifecycle exit caps must be enabled prior to C-phases to limit non-stationarity.
