# BC/Anneal Promotion Training Plan (Ops & QA)

## Audience
- Operations analysts responsible for dataset stewardship and promotion reviews.
- QA engineers validating anneal runs and telemetry gates.

## Goals
1. Teach the BC/anneal workflow (dataset audit → BC gate → anneal run → promotion decision).
2. Ensure teams can interpret watcher alerts, dashboard anneal panel, and telemetry summaries.
3. Rehearse rollback/freeze decisions when thresholds are breached.

## Session Agenda (90 minutes)
1. **Overview (10 min)** — Slide deck reviewing Phase 5.5 gates, artefacts, and responsibilities.
2. **Dataset Audit Demo (15 min)** — Run `scripts/audit_bc_datasets.py`, interpret findings, remediate missing files.
3. **BC Gate Walkthrough (10 min)** — Execute `TrainingHarness.run_bc_training()` snippet, compare accuracy vs threshold.
4. **Anneal Rehearsal Lab (20 min)** — Participants run `scripts/run_anneal_rehearsal.py --exit-on-failure`, capture `summary.json`, and inspect telemetry summary + watcher outputs.
5. **Dashboard Deep Dive (15 min)** — Navigate the observer UI; identify pass/fail signals on the Anneal panel, conflict panel, and Employment queue.
6. **Incident Simulation (15 min)** — Inject a synthetic drift (e.g., edit summary to flip `anneal_loss_flag`), decide rollback/freeze actions, log follow-up.
7. **Q&A / Next Steps (5 min)** — Capture feedback, assign TODOs (e.g., additional automation requests).

## Pre-Work
- Ensure participants have access to repo + virtualenv with `pip install -e .[dev]`.
- Provide sample artefacts (latest acceptance bundle) and slide deck in shared workspace.

## Materials
- Slide deck (stored under `docs/ops/training/BC_ANNEAL_PROMOTION.pptx` — TODO when ready).
- Hands-on guide referencing `docs/ops/OPS_HANDBOOK.md`, `docs/ops/ANNEAL_PROMOTION_GATES.md`, and new scripts.
- Feedback form (link TBD) to collect follow-up items.

## Follow-Up
- Publish session recording + notes in ops knowledge base.
- Track action items (e.g., additional dashboards, script enhancements) in Trello/Jira board.
- Schedule quarterly refresher or when promotion criteria change.

