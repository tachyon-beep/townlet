# Quick Wins

Sorted by estimated impact-to-effort ratio; all packages require <1 day of focused work.

1. **WP-301 – Harden Console Auth Defaults**
   - **Impact**: Critical security gap closes immediately for all deployments.
   - **Effort**: S (simple guard + configuration update).
   - **ROI Rationale**: Prevents unauthenticated admin access with minimal code changes and adds automated regression coverage.

2. **WP-303 – Guard Telemetry Flush Worker Failures**
   - **Impact**: Restores observability when the flush thread crashes; prevents silent data loss.
   - **Effort**: S (wrap loop, set health flag, add unit test).
   - **ROI Rationale**: A handful of structured logs and health checks dramatically reduce MTTR for telemetry outages.

3. **WP-310 – Persist Affordance Outcome Metadata**
   - **Impact**: Medium — richer telemetry unlocks faster debugging of player actions and affordance tuning.
   - **Effort**: S (extend snapshot schema + tests).
   - **ROI Rationale**: Provides immediate insight for designers with minimal schema and UI touches.

