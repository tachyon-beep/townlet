# Observer Dashboard Usability Notes (2025-09-25)

## Session Summary
- Config: configs/examples/poc_hybrid.yaml (employment loop enabled by default).
- Command: `PYTHONPATH=src python scripts/observer_ui.py configs/examples/poc_hybrid.yaml --ticks 5 --refresh 0.0`
- Captured output (`docs/samples/observer_ui_output.txt`).

## Observations
- Panels are legible and update per tick; ASCII map currently empty due to placeholder geometry.
- Employment panel clearly displays caps and queue (pending none during run).
- Schema warning banner shows “OK” when matching.
- Scrollback-friendly output; recommended to run with slower refresh (>=0.2s) for live review.

## Feedback / Next Steps
- Add legend/banner explaining ASCII map (A = agents).
- Provide optional color highlights for pending queues when backlog grows.
- Consider command-line flag to select focus agent for map view.
- Gather stakeholder feedback after sharing GIF to confirm CLI sufficiency for demos.

## Follow-up
- Map legend and colour cues implemented (red border for backlog, yellow center).
- `--focus-agent` flag allows targeting specific agents.
- Async executor with logging added for future interactive commands.
