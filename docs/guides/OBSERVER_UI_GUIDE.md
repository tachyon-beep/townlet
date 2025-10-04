# Observer UI Guide (v0.1)

The observer dashboard provides a console-based view of Townlet’s employment KPIs and agent stats. It is intended as a lightweight operator tool and demo aid until a richer renderer is available.

## Quickstart
1. Activate the virtualenv and install dependencies (`pip install -e .[dev]`).
2. Launch the dashboard:
   ```bash
   scripts/observer_ui.py configs/examples/poc_hybrid.yaml --refresh 0.5 [--focus-agent alice]
   ```
   - For the narrative demo storyline, pair this with the rehearsal helper:
     ```bash
     scripts/demo_rehearsal.sh --narration-level summary --no-palette
     ```
     The helper uses `scripts/demo_run.py --scenario demo_story_arc`, ensuring the observer view and command palette remain in sync with the playbook (`docs/ops/DEMO_SCENARIO_PLAYBOOK.md`).
3. You’ll see the following panels:
   - **Telemetry** — schema version and compatibility warning.
   - **Employment** — queue length, exits, caps.
   - **Conflict** — queue cooldowns, ghost steps, rivalry edges.
   - **Perturbation Status** — banner summarising active and pending system events before the detailed tables.
   - **Anneal Status** — latest BC/anneal gate metrics (accuracy vs threshold, drift flags, dataset).
   - **Policy Inspector** — per-agent selected action, probability, value estimate, and top action distribution.
   - **Relationship Overlay** — top trust ties with recent deltas (trust/fam/rivalry).
   - **KPI Panel** — rolling KPIs (queue intensity, lateness, late help) with colour-coded thresholds.
- **Narrations** — recent narrated events with priority markers.
- **Agents** — paginated per-agent cards with needs sparklines, social heartbeat, rivalry trend, alerts (exit pending, cooldowns).
- **Personality badges** — when `features.observations.personality_ui` is enabled, agent cards include colour-coded profile chips, trait summaries, and behaviour bias hints. Use `--personality-filter <profile>` to pre-filter the panel or palette commands (`filter:profile:<name>`, `filter:trait:ext>=0.5`) to focus on archetypes mid-demo.
- **Legend** — usage hints and colour semantics.
- (Optional) **Local Map** — ASCII map derived from the hybrid observation tensor for the first agent.

Press `Ctrl+C` to exit. Use `--ticks N` to auto-stop after N ticks; `--focus-agent` selects the map focus agent; `--approve/--defer` can trigger employment actions at startup. New pagination controls include `--agent-page-size` (default 6), `--agent-rotate-interval` (ticks between auto-rotation, 0 disables), and `--disable-agent-autorotate` to keep the current page static while presenting.

For scripted demos, prefer `scripts/demo_run.py --scenario demo_story_arc` (or another storyline) so config and timeline hashes stay aligned with the narrative assets. Example:

```bash
python scripts/demo_run.py --scenario demo_story_arc --ticks 150 --narration-level summary \\
  --personality-filter socialite --mute-personality-narration
```

Telemetry is emitted to stdout by default. If you need a quiet sink while inspecting the observer UI interactively, run `scripts/observer_ui.py` with the same config and include `--history-window 0` to trim sparklines.

When screen-sharing or streaming demos over untrusted networks, switch to
`configs/demo/poc_demo_tls.yaml`. It targets a secure TCP collector with TLS
enabled (plaintext overrides are disabled) so telemetry stays encrypted in transit.


## Schema Compatibility
- The dashboard uses `schema_version` from telemetry snapshots. If a shard reports a newer major version, the client aborts with a `SchemaMismatchError`.
- Minor mismatches emit a warning banner in the header; upgrade the UI when possible.

## Console Operations
- Approve or defer employment exits from the dashboard by issuing commands in a separate terminal (see `scripts/console_dry_run.py` for examples).
- Future versions may add interactive controls; current MVP is read-only.
- Audio cues remain out of scope for the Rich console; sound design will land with the web observer UI where accessibility affordances are richer.

### Web Spectator Notes
- The web spectator mirrors CLI features: personality badges/filters on agent cards, narration log with a **Show personality stories** toggle, and audio cues (if enabled).
- Launch locally with `npm run dev --prefix townlet_web`; Storybook smoke tests (`npm run storybook:smoke --prefix townlet_web`) ensure components render with new data contracts.

## Anneal Panel Reference
- **BC Accuracy / Threshold** — derived from the latest anneal run (telemetry version ≥1.2). The panel turns red if BC gate failed and yellow if drift flags trip.
- **Drift Flags** — summarise watcher alerts: `loss` (loss_total moved beyond tolerance), `queue` (events dipped below tolerance), `intensity` (intensity sum dipped). Values come from `anneal_*` fields in the PPO telemetry log.
- **Dataset** — name of the manifest or rollout buffer feeding the anneal run.
- To inspect the underlying log, run `python scripts/telemetry_summary.py <log> --format markdown`.

## Tests & Tooling
- `tests/test_observer_ui_dashboard.py` validates rendering helpers.
- `tests/test_observer_ui_script.py` ensures the CLI entry point runs to completion.
- Sample telemetry payloads live in `docs/samples/`; regenerate if schema changes.

## Roadmap
- Integrate richer map/object visualisation once `WorldState` exposes geometry.
- Add web/GUI layer (see `docs/work_packages/WORK_PACKAGE_OBSERVER_UI.md` stretch goals).
- Hook into the renderer roadmap for combined observation + employment views.
