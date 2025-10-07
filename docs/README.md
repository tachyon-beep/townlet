# Townlet Documentation Index

This directory centralises working notes, design artifacts, and operational runbooks for the Townlet project. Use this guide to locate material quickly before adding new documents.

## Directory overview

| Path | Purpose |
| --- | --- |
| `architecture_review/` | Historical architecture deep-dives. The current tree only contains retired plans kept for reference. |
| `audit/` | Compliance checklists and tracer bullet audits. |
| `certificates/` | Certificates required for secure integrations and simulated credentials. |
| `design/` | Product design briefs, interaction flows, and prototype annotations. |
| `engineering/` | Engineering RFCs, implementation notes, and service diagrams. |
| `external/` | Outbound communications and partner-facing collateral. |
| `guides/` | How-to guides for common workflows (e.g., onboarding, operations). |
| `handovers/` | Transition packs for teams handing over ownership. |
| `notebooks/` | Jupyter notebooks exported for reproducibility. |
| `ops/` | Operational runbooks and on-call checklists. |
| `policy/` | Policy engine reference material and governance notes. |
| `product/` | Roadmaps, positioning statements, and product requirement docs. |
| `program_management/` | Cross-team planning artifacts, status reports, and RACI charts. |
| `qa/` | Quality assurance test plans and release sign-off checklists. |
| `remediation/` | Post-incident analyses and mitigation tracking. |
| `research/` | User research findings, survey summaries, and experiment notes. |
| `rollout/` | Deployment plans, launch playbooks, and success metrics. |
| `samples/` | Example payloads, API transcripts, and schema snapshots. |
| `telemetry/` | Observability design notes, signal catalogues, and storage schemas. |
| `testing/` | Testing strategies, rig documentation, and fixture descriptions. |
| `training/` | Enablement material for internal and external audiences. |
| `work_packages/` | Focused initiative plans that bundle discovery, execution, and acceptance criteria. |

## Contributing to docs

1. Pick the directory that matches your audience. If no folder fits, propose one in your PR.
2. Add a short `README.md` alongside dense collections (see `work_packages/` for an example) so others can scan intent quickly.
3. Keep filenames descriptive and use `YYYY-MM-DD` prefixes for chronological logs.
4. Cross-link related documents instead of duplicating content.

Remember to run `ruff format` on Markdown files with code blocks to keep fenced snippets tidy.
