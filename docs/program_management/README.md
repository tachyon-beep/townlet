# Townlet Delivery Plan Overview

This suite enumerates the outstanding work required to align the current Townlet implementation with the policies and design intent documented under `docs/`. It provides:

- A consolidated backlog of remediation work packages that map documented contracts to missing or incomplete runtime behaviour.
- A project management plan describing milestones, staffing assumptions, dependencies, and risk controls to deliver these fixes.

Use these artifacts as the authoritative reference for planning and tracking the remediation effort **and** the forward-looking milestones required to deliver every capability described in `docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md` and `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md` (snapshotted here for convenience). The remediation work packages close today's gaps; the extended milestone plan in `PROJECT_PLAN.md` captures the "get to finished" roadmap once remediation completes.

## Work Hierarchy Schema

All planning in this folder follows the same hierarchy:

1. **Milestone** – outcome-oriented checkpoint with explicit exit criteria (e.g., “M4 – Social Foundations”).
2. **Phase** – thematic slice within a milestone that groups related outcomes (e.g., “Phase C1 – Chat Rewards”).
3. **Step** – concrete deliverable chunks that advance a phase (e.g., “Implement trust/familiarity storage”, “Add narration throttle”).
4. **Task** – executable units assigned to people/PRs. Tasks should include acceptance criteria, required tests, and documentation updates.

"Work package" is a generic wrapper that may cover any combination of steps/tasks; the hierarchy above always applies when decomposing work.

## Risk Management Standard

Before work begins on any task or step:

- The task **and every parent level** (step → phase → milestone) must have an up-to-date risk assessment covering medium and high implementation risks.
- Identified risks include mitigation or risk-reduction activities; any mitigation work lands as additional tasks before or alongside the main implementation.
- Risk reviews happen when a parent item changes scope or at least once per milestone. No task starts until its dependency chain documents the risks and the planned reductions.

## Included References

- `PROJECT_PLAN.md` — milestone schedule and design alignment notes.
- `WORK_PACKAGES.md` — remediation backlog mapped to design contracts.
- `MILESTONE_ROADMAP.md` — high-level milestone ladder.
- `PRODUCT_CHARTER.md` — vision, KPIs, and success criteria.
- `DOCUMENTATION_PLAN.md` — documentation deliverables and sequencing.
- `snapshots/` — frozen copies of the architectural and conceptual specifications. See below for usage notes.
- `MASTER_PLAN_PROGRESS.md` — current progress snapshot against the roadmap.

## Snapshot Usage

The `snapshots/` directory holds pinned references of the core design documents used in planning:

- `HIGH_LEVEL_DESIGN.md`
- `CONCEPTUAL_DESIGN.md`
- `ARCHITECTURE_INTERFACES.md`
- `REQUIREMENTS.md`

When preparing a milestone or work package:

1. Read the snapshot to confirm scope and contracts.
2. If the official design document changes, update the snapshot copy in this directory and note the revision in `DOCUMENTATION_PLAN.md` and `IMPLEMENTATION_NOTES`.
3. Ensure cross-references in planning/engineering docs point to the snapshot location so readers always land on the pinned version.
