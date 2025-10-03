# Observer UI Guide (v0.1)

The observer dashboard provides a console-based view of Townlet’s employment KPIs and agent stats. It is intended as a lightweight operator tool and demo aid until a richer renderer is available.

## Quickstart
1. Activate the virtualenv and install dependencies (`pip install -e .[dev]`).
2. Launch the dashboard:
   ```bash
   scripts/observer_ui.py configs/examples/poc_hybrid.yaml --refresh 0.5 [--focus-agent alice]
   ```
3. You’ll see the following panels:
   - **Telemetry** — schema version and compatibility warning.
   - **Employment** — queue length, exits, caps.
   - **Conflict** — queue cooldowns, ghost steps, rivalry edges.
   - **Anneal Status** — latest BC/anneal gate metrics (accuracy vs threshold, drift flags, dataset).
   - **Policy Inspector** — per-agent selected action, probability, value estimate, and top action distribution.
   - **Relationship Overlay** — top trust ties with recent deltas (trust/fam/rivalry).
   - **KPI Panel** — rolling KPIs (queue intensity, lateness, late help) with colour-coded thresholds.
   - **Narrations** — recent narrated events with priority markers.
   - **Agents** — per-agent wallet, shift state, attendance, wages withheld.
   - **Legend** — usage hints and colour semantics.
   - (Optional) **Local Map** — ASCII map derived from the hybrid observation tensor for the first agent.

Press `Ctrl+C` to exit. Use `--ticks N` to auto-stop after N ticks; `--focus-agent` selects the map focus agent; `--approve/--defer` can trigger employment actions at startup.

For scripted demos, launch `scripts/demo_run.py` with the new `configs/demo/poc_demo.yaml` config, which writes telemetry to `logs/demo_stream.jsonl` so the Rich dashboard stays readable. For example:

```bash
python scripts/demo_run.py configs/demo/poc_demo.yaml --ticks 300 --refresh 0.5
```

Reuse the same config with `scripts/observer_ui.py` when you want a quiet telemetry sink while exploring manually.

When screen-sharing or streaming demos over untrusted networks, switch to
`configs/demo/poc_demo_tls.yaml`. It targets a secure TCP collector with TLS
enabled (`allow_plaintext: false`) so telemetry stays encrypted in transit.


## Schema Compatibility
- The dashboard uses `schema_version` from telemetry snapshots. If a shard reports a newer major version, the client aborts with a `SchemaMismatchError`.
- Minor mismatches emit a warning banner in the header; upgrade the UI when possible.

## Console Operations
- Approve or defer employment exits from the dashboard by issuing commands in a separate terminal (see `scripts/console_dry_run.py` for examples).
- Future versions may add interactive controls; current MVP is read-only.

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
