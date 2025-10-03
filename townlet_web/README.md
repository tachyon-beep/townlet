# Townlet Web Viewer

Milestone 1 (Phase 1.2) scaffold for the spectator dashboard.

## Scripts

```bash
npm install
npm run dev           # Start Vite dev server
npm run test          # Run Vitest unit tests
npm run storybook     # Launch Storybook for component review
npm run playwright:test # Run Playwright end-to-end suite
```

## Structure

- `src/hooks/useTelemetryClient.ts` — WebSocket diff-merging hook shared by app/tests.
- `src/components/` — Presentational components for header, agent grid, overlays, narration feed.
- `src/theme/tokens.ts` — Shared design tokens in sync with docs/design/web_ui_tokens.json.
- `.storybook/` — Storybook configuration for rapid UI review.
- `vite.config.ts` / `vitest.setup.ts` — Tooling for build + tests.
- `playwright.config.ts` / `tests/e2e/` — End-to-end smoke tests against the mock gateway.

### Testing Fixtures

The hook tests exercise the diff merge helper; integration with the real gateway happens in Milestone 1.3 once the transport service is deployed.

## Next Steps

- Wire the hook to the new FastAPI gateway once deployed (`ws://.../ws/telemetry`).
- Flesh out agent detail panels and KPI charts per parity checklist.
- Add accessibility checks (axe) and expand Storybook stories covering empty/error states.
