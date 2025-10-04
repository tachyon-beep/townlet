# Web UI Roadmap

Townlet’s web experience extends the Rich console with a spectator dashboard and an operator console. This roadmap captures scope, sequencing, and checkpoints so work tracked under FWP-07 remains auditable.

## Goals
- Provide a read-only spectator view suitable for demos and remote observers.
- Deliver an authenticated operator console with command palette parity and telemetry overlays.
- Keep transport schemas, accessibility, and operational runbooks aligned across CLI and web surfaces.

## Milestones

### M0 – Foundations & Risk Reduction (Completed)
- Version telemetry schema for WebSocket transport; ship fixtures in `tests/data/web_telemetry/`.
- Draft security baseline and threat model (`docs/program_management/WEB_UI_SECURITY_BASELINE.md`, `WEB_UI_THREAT_MODEL.md`).
- Publish shared design tokens and parity checklist (`docs/design/web_ui_tokens.json`, `WEB_UI_PARITY_CHECKLIST.md`).
- Stand up CI scaffolding for `townlet_web/` (lint, vitest, Storybook smoke).
- Document rollback/console fallback in `docs/ops/WEB_UI_ROLLBACK_PLAN.md`.

### M1 – Spectator Viewer MVP (Completed)
- Implement FastAPI gateway with snapshot/diff streaming (`src/townlet/web/gateway.py`) and Prometheus metrics.
- Build React/Vite shell that renders tick status, agent summaries, narrations, perturbations, KPIs, and utilities (`townlet_web/src/App.tsx`).
- Add diff-aware telemetry client hook plus vitest coverage (`townlet_web/src/hooks/useTelemetryClient.ts`).
- Containerize gateway + static bundle and publish deployment guide (`docs/ops/WEB_SPECTATOR_DEPLOY.md`).
- Run baseline load tests (k6/Locust) to verify <250 ms p95 updates at demo concurrency.

### M2 – Operator Console Parity (In Progress)
- Secure operator WebSocket with token validation and command dispatch loop (`tests/test_web_operator.py`).
- Mirror console overlays (relationships, social, KPIs, perturbations) using selector utilities with tests (`townlet_web/src/utils/selectors.ts`).
- Ship accessibility upgrades: skip links, ARIA roles, axe smoke tests, optional audio cues (`townlet_web/src/hooks/useAudioCue.ts`).
- Add Playwright flows covering spectator/operator happy paths (`townlet_web/tests/e2e/`).
- Exit criteria: parity checklist satisfied; command dispatch regression suite green; accessibility report stored with decisions.

### M3 – Production Readiness (Planned)
- Capacity: soak tests for 100+ spectator clients; chaos drills for gateway restarts; log retention policy.
- Operations: Helm chart hardening, TLS termination options, CDN tuning, observability dashboards.
- Training: update operator handbook, document feature flags, finalize go/no-go checklist.

## Open Risks & Mitigations
1. **Parity Drift** – Maintain selector unit tests plus snapshot comparisons against the Rich console; run parity audit each release.
2. **Security** – Integrate gateway auth with the chosen IdP; enforce rate limits and CSRF protections per threat model.
3. **Performance** – Monitor message rate and apply adaptive throttling; budget CPU/GPU impact for heavier visualizations.
4. **Accessibility** – Keep axe/Playwright accessibility checks mandatory in CI; coordinate with documentation for keyboard shortcuts and audio toggles.
5. **Operational Complexity** – Capture rollback/incident response drills in runbooks; ensure console fallback remains tested.

## Next Actions
- Finalize operator parity tasks (audio toggles, overlay performance tuning).
- Execute production readiness tasks in M3 with infrastructure stakeholders.
- Track changes via FWP-07 in `audit/FORWARD_WORK_PROGRAM.md` and update this roadmap alongside milestone sign-offs.
