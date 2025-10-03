# Dashboard UI Enhancement Notes (Draft)

## 1. Current Layout Inventory
- **Render cadence**: `dashboard.render_snapshot` runs once per loop iteration from the Rich console driver (`refresh_interval` default 1.0s). Snapshot data pulled via `TelemetryClient.from_console`; map panel rendered afterwards using fresh observations.
- **Telemetry Header**: schema/tick/transport health plus optional tick-duration metrics.
- **Economy & Utilities**: economy settings table, utilities status, active price spikes (panel border flips green/yellow/red based on outages/spikes).
- **Employment Queue**: pending exits, counts, cap/limit, review window (panel border turns red when backlog present).
- **Conflict Suite**: queue deltas (recent history), rivalry events, stability alerts; coloured magenta when conflict metrics >0.
- **Anneal & Policy Panels**: anneal status, policy inspector, promotion gate (rendered via `_build_anneal_panel` / `_build_policy_inspector_panel`).
- **Relationship Overlay**: top ties with deltas (`_build_relationship_overlay_panel`).
- **KPI Panel**: running metrics (queue intensity, lateness, late help).
- **Narrations**: throttled event log (utility/shower/sleep/queue categories only).
- **Social Panel**: status summary, per-agent cards (top friends/rivals), churn aggregates, social event feed (chat/avoidance).
- **Relationship Churn/Updates**: churn totals by owner/reason and recent delta table.
- **Agents Table**: wallet, shift state, attendance ratio, wages withheld, lateness.
- **Local Map**: egocentric map for focus agent (default first agent).
- **Legend**: textual legend reminding operators of panel semantics.

## 2. Ops Feedback & Must-Have Metrics
- **Needs & Wallet**: Ops handbook highlights monitoring agent well-being and finances alongside employment KPIs.
- **Rivalry/Conflict Signals**: Queue fairness deltas, rivalry events, and avoidance behaviour central to conflict response.
- **Job Status**: Attendance ratio, shift state, backlog flags feed into employment playbooks.
- **Perturbations**: Health snapshot exposes pending/active counts; ops expect prominent alerting during demo runs.
- **Social Stories**: Recent docs emphasise friendship/rivalry narrations and social event feeds for demo visibility.

## 3. Proposed Enhancements (Wireframe Overview)
- **Per-Agent Card Grid**
  - Placement: directly after header (two columns on standard terminal width, degrade to single column on narrow screens).
  - Scroll behaviour: vertical pager when agent count exceeds available height; keyboard toggle to focus on specific agent.
- **Perturbation Banner**
  - Sits above conflict panel; concise summary of active event id, timer, severity colour; secondary line for pending queue.
  - Banner collapses when no perturbations; optional key to expand for detail.

### 3.1 Card Content
- Needs spark bars (hunger/hygiene/energy) with threshold colouring.
- Shift block (state, on_shift flag, attendance %, lateness counter).
- Wallet & wages withheld summary.
- Rivalry snapshot (top rival & intensity, avoidance flag if above threshold).
- Social heartbeat (last chat partner/result, friendship delta arrow).
- Optional icons for alerts (employment exit pending, perturbation impact, being on cooldown).

### 3.2 Perturbation Highlight Rules
- **Active**: red border, countdown timer (ticks remaining) with event type (e.g., `price_spike: market (T-120)`).
- **Pending**: yellow/gold accent, queued start tick, ability to cycle through multiple pending events.
- **Cooldown**: muted teal, display cooldown spec remaining vs agent cooldowns.
- Include fallback text `No perturbations scheduled` when empty.

## 4. Risks & Open Questions
- Rich layout constraints: need to confirm card grid fits within typical 120×40 terminal without horizontal clipping.
- Performance: increased per-tick rendering (sparklines, multiple panels) may require batching or reduced refresh interval.
- Data volume: per-agent telemetry may become heavy for >12 agents; consider pagination or filter.
- Accessibility: ensure colour choices meet contrast requirements; consider text alternatives for banner icons.
- Future integration: command palette (Milestone M2) may share screen real estate—plan for toggleable overlay.

