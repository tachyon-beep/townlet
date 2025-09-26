# Townlet Milestone Roadmap (v1.1)

# Milestone Roadmap (Aligned with `PROJECT_PLAN.md`)

This roadmap tracks the sequencing across remediation and forward-looking Townlet milestones. See `PROJECT_PLAN.md` for detailed scopes, owners, and risk controls.

| Milestone | Theme | Key Deliverables | Dependencies | Exit Criteria |
| --- | --- | --- | --- | --- |
| M1 | Runtime Safety | Affordance manifest validation, observation variant gating, reward guardrails. | Existing simulator foundation. | Invalid manifests fail fast; observation variants contractually defined; reward guardrails enforced with tests. |
| M2 | Operational Guardrails | Stability monitor thresholds, console safeguards, telemetry publisher hardening. | M1 | Console operations validated, telemetry stream versioned, stability alerts actionable. |
| M3 | Continuity & Conflict Systems | Snapshot persistence, conflict/rivalry telemetry, observer UI smoke test. | M2 | Snapshots round-trip deterministically; conflict events influence telemetry; UI smoke passes. |
| M4 | Social Foundations | Relationship storage, social observation snippets, chat rewards (C1), narration throttling. | M3 | Relationships persisted per design; observer UI surfaces ties; narration guard verified. |
| M5 | Behaviour Cloning & Anneal | Scripted trajectory capture, BC training harness, mixed control scheduler with rollback guard. | M4 | BC accuracy ≥90%; anneal runs with rollback guard and tests. |
| M6 | Observer Experience & Policy Inspector | Dashboard overlays, policy inspector, audio toggles, KPI panels. | M5 | Viewer exercises overlays and inspector without schema mismatches; ops handbook updated. |
| M7 | Promotion & Release Governance | Automated promotion gate, golden rollouts, rollback/ops drills. | M6 | Promotion gate enforces KPIs, rollback drills documented and tested. |
| M8 | Perturbations & Narrative Events | Perturbation scheduler, fairness buckets, lifecycle vignettes, perturbation telemetry. | M7 | Events fire with cooldowns, vignettes render, telemetry captures perturbation metadata. |
| M9 | Personality & Ops Polish | Personality balancing, admin console extensions, privacy/ethics controls. | M8 | KPI targets met with personalities enabled; console/ethics controls documented and tested. |

## Cross-Cutting Workstreams

- **Testing & Verification:** Property-based checks (M1+), queue fuzz tests (M4), BC/anneal regression suite (M5), chaos suite (M8).
- **Telemetry & Tooling:** Schema versioning (M2), KPI dashboards (M6), policy inspector (M6), soak harness (operational ongoing).
- **Documentation:** Charter & roadmap (current), Architecture Guide, Ops Handbook, Testing Plan, Privacy Policy, Contributor Guide (refer to `DOCUMENTATION_PLAN.md`).

## Sequencing Notes

- Hold social rewards and perturbations behind feature flags until prior milestones record two consecutive green evaluation windows.
- Promotion gates require release/shadow alignment; observation variant or reward changes ship only with golden rollout sign-off.
- Embedding slot cooldowns and lifecycle exit caps remain mandatory before social phases to limit non-stationarity.
