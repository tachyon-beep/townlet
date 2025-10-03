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

### Current Progress (Milestone 2.3)

- Spectator/operator UI now includes skip-link navigation, audio cue toggle, and narration-focused audio alerts.
- Panels implemented: header, perturbations, economy, employment, conflict, KPIs, agent grid, narration feed, relationship overlays, social feed, legend.
- Unit tests: telemetry hook (`useTelemetryClient.test.ts`), selectors (`selectors.test.ts`), audio cue hook (`useAudioCue.test.ts`).
- Storybook stories cover panels (`DashboardPanels.stories.tsx`) for visual regression and accessibility checks.

Update this file at the end of each milestone to record parity status.
