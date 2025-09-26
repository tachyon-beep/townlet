# Townlet Documentation Plan

_Last updated: 2025-09-24_

## Overview

This plan defines the documentation suite required to deliver Townlet from proof of concept through Phases A–C, and the order in which artefacts will be produced. It aligns with the conceptual, high-level, and requirements design documents already in `docs/`.

## Target Document Set

- **Product Charter** — states the Townlet vision, target KPIs, success metrics, and key guardrails; provides executive alignment (ties to `CONCEPTUAL_DESIGN.md`).
- **Milestone Roadmap** — milestone-by-milestone scope (M0–M4), feature flag posture, and KPI expectations; the source of record for sprint planning and reporting.
- **Architecture & Interfaces Guide** — authoritative reference for module responsibilities, PettingZoo contracts, telemetry schema, snapshot layout, and config identity rules (extends `HIGH_LEVEL_DESIGN.md`).
- **Operations Handbook** — runbooks for standing up training shards, release vs shadow policy promotion, console administration, monitoring dashboards, alert thresholds, and rollback policy.
- **RL Experiment Playbook** — experiment templates, reward tuning levers, BC→anneal procedures, KPI evaluation suites, and logging conventions for reproducibility.
- **Testing & Verification Plan** — mapping of unit/integration/property/chaos tests to requirement sections; includes acceptance criteria, tooling, and regression gates.
- **Data & Privacy Policy** — telemetry retention rules, privacy-mode behaviour, redaction requirements, and compliance notes for streamer mode and public logs.
- **Contributor Guide (expanded)** — keep `CONTRIBUTING.md` as the workflow/process source of truth while `AGENTS.md` covers day-to-day repo usage; extend both with branching policy, CI gates, issue triage workflow, and cross-links.

## Delivery Sequence

| Week | Focus | Deliverables | Dependencies |
| ---- | ----- | ------------ | ------------ |
| 1 | Kick-off & vision | Product Charter (draft), Milestone Roadmap (skeleton) | Requires alignment with existing design docs |
| 2 | Architecture alignment | Architecture & Interfaces Guide (draft), Roadmap dates finalised | Charter + roadmap skeleton |
| 3 | Ops readiness | Operations Handbook (draft), RL Experiment Playbook outline | Architecture draft for interfaces |
| 4 | Quality strategy | Testing & Verification Plan (draft), Experiment Playbook v1 | Roadmap + architecture inputs |
| 5 | Privacy & compliance | Data & Privacy Policy (draft) | Architecture (telemetry), Ops (logging) |
| 6 | Contributor enablement | Contributor Guide expansion, doc cross-link review, publish v1 bundle | All prior drafts |

## Review Cadence

- Weekly doc review sync (60 min) with engineering, PM, RL, ops, and QA leads.
- Async sign-off comments in PRs; final approval requires leads for impacted domains.
- Version each document with semantic tags (e.g., `v1.0.0`) upon sign-off; log deltas in a shared changelog.

## Ownership & Next Steps

- **Program Manager** owns the Product Charter and Milestone Roadmap.
- **Architecture Lead** owns Architecture & Interfaces Guide and supports downstream documents.
- **Operations Lead** owns Operations Handbook; **RL Lead** owns Experiment Playbook.
- **QA Lead** owns Testing & Verification Plan.
- **Security/Privacy Officer** owns Data & Privacy Policy.
- **Developer Experience Lead** owns Contributor Guide expansion, coordinating updates between `CONTRIBUTING.md` and `AGENTS.md` so instructions stay consistent.

Immediate action: schedule the Week 1 kick-off with all owners, spin up shared skeletons (Docs/Notion/Git markdown), and register doc tracking issues in GitHub referencing this plan.
