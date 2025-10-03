# Demo Playbook — Scripted Observer Run

## 1. Prerequisites
- Python environment with Townlet dev dependencies installed (`pip install -e .[dev]`).
- Baseline config: `configs/examples/poc_hybrid.yaml` or a scenario override with relationships enabled.
- Optional timeline file (defaults to `configs/demo/demo_timeline.yml`).
- Optional perturbation plan (`configs/perturbations/*`).
- QA checklist reference: `docs/testing/COMMAND_PALETTE_QA.md`.

## 2. Quick Start
```bash
python scripts/demo_run.py configs/examples/poc_hybrid.yaml \
    --timeline configs/demo/demo_timeline.yml \
    --perturbation-plan configs/perturbations/poc_plan.yml \
    --ticks 240 \
    --refresh 1.0 \
    --history-window 30
```
- `--relationships` forces relationship stage `≥ A` when using trimmed configs.
- `--no-palette` hides the command palette for minimal runs.
- `--history-window 0` disables sparklines if terminals struggle with refresh.

The script seeds agents, jobs, and relationships, warms telemetry buffers, then executes the timeline via `DemoScheduler` while the Rich dashboard renders.

## 3. Expected Visuals
- **Agents panel**: Needs/wallet/rivalry sparklines populated within the first refresh; new `guest_1` card appears by tick 5.
- **Social section**: Top friends/rivals and churn metrics populated from the seeded relationship ledger.
- **Perturbation banner**: `price_spike` trigger at tick 20 moves from pending → active with remaining ticks.
- **Command palette**: Pending count should spike briefly when scripted commands enqueue; status banner reports each dispatch (green) or queue warning (yellow).

## 4. Timeline & Config Editing
- Modify `configs/demo/demo_timeline.yml` to adjust tick offsets or add additional actions (`set_need`, `spawn_agent`, `force_chat`, console commands).
- Perturbation plans can preload longer sequences via `loop.perturbations.load_plan()`; reference `configs/perturbations/` for templates.

## 5. Troubleshooting
- **Queue saturation warnings**: The palette banner flips yellow; consider bumping `max_pending` via `ConsoleCommandExecutor` or spacing timeline ticks.
- **Telemetry lag**: Increase `--refresh` interval, disable palette (`--no-palette`), or reduce `--history-window` for shorter buffers.
- **Empty sparklines**: Confirm `history_window > 0` and relationships stage is enabled; rerun with `--relationships` flag.
- **Missing Social data**: Ensure QA checklist steps for relationship stage and telemetry history are followed.

## 6. Artifact Capture
Capture evidence for demo readiness under `docs/samples/demo_run/`:
1. Run the demo with terminal capture:
   ```bash
   python scripts/demo_run.py configs/examples/poc_hybrid.yaml \
       --timeline configs/demo/demo_timeline.yml \
       --ticks 240 --history-window 30 \
       > docs/samples/demo_run/command_log.txt
   ```
2. Export telemetry snapshot using the console palette (`telemetry_snapshot`) or `townlet.snapshots.SnapshotManager` and save as `docs/samples/demo_run/telemetry_snapshot.json`.
3. Use `rich` capture (e.g., `python -m rich.console --record`) or terminal screenshot tooling to store PNGs of key panels (`agents.png`, `social.png`, `palette.png`).
4. Update `docs/samples/demo_run/manifest.json` with filenames and SHA-256 checksums (`sha256sum <file>`).

See `docs/samples/demo_run/README.md` for detailed capture workflow.

## 7. Latest Validation Run (2025-10-24)
- Command log: `docs/samples/demo_run/command_log.txt` (40 ticks @ 0.1s refresh).
- Average tick duration: ~0.11s (2.3s for 20 ticks after warmup).
- Scheduled commands executed: 3/3 (spawn_agent, force_chat, perturbation_trigger).
- Telemetry snapshot: `docs/samples/demo_run/telemetry_snapshot.json` seeded after 20 ticks.
- Outstanding artifacts: capture PNG screenshots for agents/social/perturbations/palette panels before stakeholder review.
