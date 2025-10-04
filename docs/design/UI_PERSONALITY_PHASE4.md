# UI & Narration Personality Surfacing – Phase 0 Notes

## Interface Inventory
- **Rich CLI dashboard** (`src/townlet_ui/dashboard.py`): renders agent cards, queue panels, and narration feed. Trait badges will surface here; palette filters already act on agent metadata.
- **CLI command palette / console router** (`src/townlet/console/handlers.py`): supplies telemetry snapshots and narration stream to the CLI. Needs optional personality block handling so existing commands stay backward compatible.
- **Demonstration runner** (`src/townlet/demo/runner.py`): seeds demo state and drives dashboard callbacks. Ensures initial narration/palette status picks up new cues without extra wiring.
- **Web spectator** (`townlet_web/src/components/*`, `townlet_web/src/utils/selectors.ts`, `townlet_web/src/hooks/useTelemetryClient.ts`): React agent cards/sidebars consume telemetry snapshots; selectors must accept optional personality payloads.
- **Narration utilities** (`src/townlet/telemetry/publisher.py`, `townlet_ui/dashboard.py` narration pane, `townlet_web/src/components/NarrationLog.tsx`): limiter categories and rendering logic for new trait-driven messages.

## Baseline Capture Plan
- Record current CLI dashboard run (`python scripts/demo_run.py --ticks 60`) with existing agent cards/narration output. Store summary (agent list, narration count) alongside this document for comparison after changes.
- Capture web UI snapshot via `npm run dev --prefix townlet_web` against the baseline telemetry feed; note agent card DOM classnames for regression tests.
- Preserve current narration logs (`logs/narration_demo.jsonl`, if present) as pre-change reference.

## Compatibility Audit
- CLI components rely on optional telemetry keys; new badge fields must be appended to existing metadata blocks to avoid breaking invariants.
- React selectors type-check telemetry via `telemetryTypes.ts`; extend the interface with optional personality payloads to prevent compile errors while keeping backward compatibility.
- Narration limiter currently tracks categories `relationship_friendship`, `relationship_rivalry`, `social_alert`; new categories should reuse limiter wiring and be toggleable.

## Rollback & Feature Flags
- Personality rendering will be gated by a UI-level toggle (`ui.personality_badges`, to be added) so operators can revert to neutral cards without touching observation flags.
- Trait-driven narrations will share the existing `features.observations.personality_channels` flag plus a dedicated narration toggle (`telemetry.narration.enable_personality` planned) to disable cues independently if volume becomes noisy.
- Document fallback steps in release notes (disable UI toggle, flush caches, reload dashboard).

## Fixture & Test Preparation
- Clone current React component test fixtures (agent card snapshots in `townlet_web/src/__tests__`) before modifying rendering output.
- Duplicate CLI dashboard regression logs used by `tests/test_observer_ui_dashboard.py` so new badges can be asserted without losing the legacy expectation.
- Note lacking automation around narration volume (manual check). Consider adding a log-length assertion once personality cues land.

## Next Steps
1. Phase 4.1 complete — badges/filters live in CLI + web.
2. Phase 4.2 underway — narration cues, limiter tuning, and mute toggles implemented.
3. Continue expanding automated coverage and capture post-change fixtures for regression tracking.

## Phase 4.2 Snapshot
- Added `telemetry.personality_narration` config (thresholds + enable toggle) plus a dedicated
  cooldown for `personality_event` narrations.
- Telemetry publisher now emits trait-aware cues (high extroversion chats, low conflict tolerance)
  gated by config and dedupe/limiter rules.
- CLI dashboard exposes personality narrations with themed styling and a runtime flag via
  `--mute-personality-narration`.
- Web spectator surfaces the same entries with badges and a “Show personality stories” toggle.
- Test suites cover narration emission, limiter behaviour, CLI filtering, and the React toggle flow.

## Flagging Strategy
- Observation tensor personality data is gated by `features.observations.personality_channels`.
- UI surfaces (badges, filters) will respect a separate `features.observations.personality_ui` toggle so operators can hide presentation changes without disabling upstream telemetry.
