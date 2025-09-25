# Observer UI Product Decisions (2025-09-25)

## Goals
- Provide an immediate operator/demonstration interface for employment KPIs and observation snapshots.
- Keep abstraction layers flexible enough to evolve toward richer 2D/3D visualisations (e.g., voxel-style renderer) without discarding current work.

## Current Environment
- Telemetry payloads now include employment metrics and hybrid observation tensors (map + features).
- Rich/Textual dashboard prototype exists; CLI entry point already shipping.
- No front-end asset pipeline yet; renderer roadmap still exploratory.

## Front-End Options Evaluated
| Option | Pros | Cons | Path to 3D |
| --- | --- | --- | --- |
| **Remain CLI-only (Rich/Textual)** | Zero additional deps, fast iteration, easy to script, good for ops | Limited visual fidelity; no rich interactions | Acts as control surface/data feed; can co-exist with 3D client |
| **Streamlit/Plotly Web UI** | Quick to stand up charts, map heatmaps; no heavy front-end build | Less control over UX, still limited for real-time map | Can export same telemetry to separate 3D client later |
| **Custom Web (FastAPI + React/Svelte)** | Full control, better for future 3D portal integration | Higher maintenance, build tooling required now | Could share APIs with voxel client later |
| **Direct 3D prototype (e.g., Panda3D, Godot)** | Moves toward voxel vision quickly | High upfront cost; observation tensor not enough data yet | Would anchor technology choice early, reduces flexibility |

## Decision
- **Primary UI**: Keep Rich/Textual console dashboard as Tier-1 operator tool. Extend with features (alerts, map legends, override commands) but avoid heavy dependencies.
- **Artifact Strategy**: Treat CLI output + telemetry client as authoritative data services. Expose a clean Python API that a future graphical/3D client can reuse.
- **3D Path Compatibility**: Document observation tensor schema and employment API; abstain from decisions that would require rewriting data feeds.
- **Stretch Goal**: After conflict intro (M2.5), revisit a lightweight web viewer (FastAPI + a minimal front-end) if demo requirements demand richer visuals. This web layer should consume the same `townlet_ui.telemetry` client to ensure parity.

## Implementation Implications
1. Enhance existing CLI dashboard (alerts, concurrency) but keep it non-blocking—makes porting to other UI stacks easier.
2. Expose telemetry client as package entry point (`townlet_ui`) for reuse; document API guarantees (versioning, field names).
3. When world geometry is ready, extend `WorldState.local_view` to include object positions and queue nodes; UI can then gradually upgrade from ASCII map to more detailed rendering.
4. Prepare data adapters (e.g., convert map tensor → JSON/canvas) for future web or 3D layers.

## Residual Questions
- Confirm with Product/Marketing whether Rich CLI suffices for upcoming demos (collect feedback during usability dry run).
- Investigate integration with future voxel renderer (likely separate process subscribing to telemetry stream).
- Determine whether to package UI as optional extra (e.g., `pip install townlet[ui]`).

## Next Actions
- Add colour-coded backlog indicators and ASCII legend per UX feedback.
- Log console command errors; surface warnings in dashboard header for ops.
- Consider caching observation tensors to minimise redundant builder calls.
- Implement dashboard improvements (alerts, concurrency) — already scheduled in current work package.
- Schedule usability dry run session, capture feedback (store attachments/notes), and document in implementation notes.
- Add roadmap reminder to reassess web/3D UI after conflict intro milestone.
