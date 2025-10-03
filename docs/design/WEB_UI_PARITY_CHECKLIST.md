# Web UI Parity Checklist

Keep this checklist updated as panels evolve. Each section corresponds to an existing Rich dashboard component.

- [ ] Telemetry header (schema, transport status, warnings)
- [x] Perturbation status banner (active/pending/cooldown indicators)
- [x] Economy & utilities panel (with outage colours)
- [x] Employment queue summary (counts, caps, pending agents)
- [x] Conflict metrics (cooldown, ghost steps, rivalry events)
- [ ] Anneal / promotion panels (cycle state, pass streak, alerts)
- [ ] Agent cards (needs bars, wallet, attendance, social heartbeat, alerts)
- [x] Agent summary grid (wallet, attendance, shift) *(spectator MVP placeholder)*
- [x] KPI panel (all metrics + trend arrows)
- [x] Relationship overlays (top deltas, churn tables, updates)
- [x] Social panel (status, cards, churn, events)
- [ ] Narrations feed (priority markers)
- [ ] Map overlay (local agent map or equivalent visualization)
- [ ] Command palette & history (operator console only)
- [x] Command palette & history (web operator mode) *(Phase 2.1 MVP: dispatch + status)*
- [x] Legend / operator tips

For each item capture:
- Component owner (FE/BE)
- Acceptance tests (unit + e2e)
- Accessibility requirements (keyboard focus order, screen-reader labels)

### Current Progress (Milestone 2.2)

- Spectator shell includes header status, agent summary grid, narration feed, perturbation banner, economy/employment panels, conflict metrics, KPI cards, relationship overlays, social feed, and legend.
- Telemetry hook and selector unit tests live in `townlet_web/src/hooks/useTelemetryClient.test.ts` and `townlet_web/src/utils/selectors.test.ts`.
- Storybook stories cover all spectator/overlay panels (`townlet_web/src/components/DashboardPanels.stories.tsx`).

Update this file at the end of each milestone to record parity status.
