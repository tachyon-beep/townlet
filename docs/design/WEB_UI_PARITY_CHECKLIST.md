# Web UI Parity Checklist

Keep this checklist updated as panels evolve. Each section corresponds to an existing Rich dashboard component.

- [ ] Telemetry header (schema, transport status, warnings)
- [ ] Perturbation status banner (active/pending/cooldown indicators)
- [ ] Economy & utilities panel (with outage colours)
- [ ] Employment queue summary (counts, caps, pending agents)
- [ ] Conflict metrics (cooldown, ghost steps, rivalry events)
- [ ] Anneal / promotion panels (cycle state, pass streak, alerts)
- [ ] Agent cards (needs bars, wallet, attendance, social heartbeat, alerts)
- [x] Agent summary grid (wallet, attendance, shift) *(spectator MVP placeholder)*
- [ ] KPI panel (all metrics + trend arrows)
- [ ] Relationship overlays (top deltas, churn tables, updates)
- [ ] Social panel (status, cards, churn, events)
- [ ] Narrations feed (priority markers)
- [ ] Map overlay (local agent map or equivalent visualization)
- [ ] Command palette & history (operator console only)
- [ ] Legend / operator tips

For each item capture:
- Component owner (FE/BE)
- Acceptance tests (unit + e2e)
- Accessibility requirements (keyboard focus order, screen-reader labels)

### Current Progress (Milestone 1.2)

- Spectator shell includes header status, agent summary grid, and narration feed components backed by telemetry diff logic.
- Telemetry hook unit tests live in `townlet_web/src/hooks/useTelemetryClient.test.ts`.
- Storybook scaffolding available (`npm run storybook`) for iterative parity reviews.

Update this file at the end of each milestone to record parity status.
