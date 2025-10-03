# Demo Run Artifact Bundle

Use this directory to store evidence from scripted dashboards runs.

## Capture Steps
1. Launch the demo with logging enabled:
   ```bash
   python scripts/demo_run.py configs/examples/poc_hybrid.yaml \
       --timeline configs/demo/demo_timeline.yml \
       --ticks 240 --history-window 30 \
       > docs/samples/demo_run/command_log.txt
   ```
2. Trigger the `telemetry_snapshot` console command (via palette or REST transport) and save the payload as `telemetry_snapshot.json`.
3. Capture PNG screenshots of the Agents, Social, Perturbations, and Palette panels using Rich capture (`rich.live.Live` record) or terminal tooling. Store as `agents.png`, `social.png`, `perturbations.png`, `palette.png`.
4. Update `manifest.json` with filenames and SHA-256 checksums:
   ```bash
   sha256sum docs/samples/demo_run/*.png docs/samples/demo_run/*.json docs/samples/demo_run/command_log.txt >> docs/samples/demo_run/manifest.json
   ```
5. Cross-check palette shortcuts and QA checklist (`docs/testing/COMMAND_PALETTE_QA.md`) during capture.

## Notes
- Keep only the most recent validated run in this directory to avoid confusion.
- If terminal capture is not possible, note the omission and link to alternative evidence (e.g., asciinema recording).
