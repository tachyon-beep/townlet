# Web UI Rollback Plan

This runbook outlines how to fall back to the Rich console dashboard if the web observer experiences issues during a demo.

## Preconditions
- Operators retain SSH access to the demo host.
- `scripts/observer_ui.py` remains functional with the same config used by the web client.
- Telemetry gateway runs behind a feature flag (`WEB_OBSERVER_ENABLED`).

## Rollback Steps
1. **Disable Web Gateway**
   - Set `WEB_OBSERVER_ENABLED=0` (environment flag) and redeploy gateway.
   - Confirm WebSocket endpoint returns 503 within 1 minute.
2. **Notify Operators**
   - Announce fallback in ops channel; provide console command to launch Rich dashboard locally:  `python scripts/observer_ui.py --config <demo-config> --refresh 0.5 --ticks 0`.
3. **Switch Telemetry Links**
   - Update runbook sheet and demo handout to reference Rich dashboard instructions.
4. **Collect Diagnostics**
   - Capture gateway logs, browser console output, and relevant telemetry metrics for post-mortem.

## Recovery
- After investigating, re-enable the feature flag in staging and run smoke tests (Milestone 1 pipeline) before toggling back in production/demo environments.

Keep this document synced with the rollout checklist (FWP-07 Milestone 3).
