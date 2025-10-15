# Command Palette & Interaction Enhancements — Discovery Notes

## 1. Objectives & Constraints
- **Goal**: Add a Rich-based command palette for quick operator actions (spawn, need tweaks, forced chats, toggles) plus sparkline telemetry/history.
- **Dashboard cadence**: `render_snapshot` executes once per refresh (default every 0.8–1.0s). Any palette overlay must fit inside this cadence without blocking the simulation loop.
- **Terminal envelope**: Current layouts assume ~120×40 terminals. Social and agent card grids already consume full width, so the palette must either overlay temporarily (modal) or occupy a collapsible sidebar.
- **Input mode**: Dashboard currently uses non-blocking key polling; palette should activate via a single shortcut (provisional `ctrl+p`) and close with `esc`. Palette interactions must preserve keyboard-only workflows and avoid disrupting screen readers.

## 2. Existing Console Command Inventory
Source: `create_console_router` in `src/townlet/console/handlers.py` (schema 0.9.x). Commands are split by execution mode.

### 2.1 Viewer-safe command matrix
| Command | Mode | Required params | Palette UX | Failure / validation notes |
| --- | --- | --- | --- | --- |
| `telemetry_snapshot` | viewer | none | Informational – no form | Already validated; bubble schema warning if present |
| `conflict_status` | viewer | none | Display only | Consider filter chip for queues once telemetry adds support |
| `queue_inspect` | viewer | `object_id` (str) | Autocomplete from known objects | Return empty-state banner if queue empty; highlight `not_found` errors |
| `rivalry_dump` | viewer | none | Warn about large payload | Palette should request confirmation when rivalry count > 50 |
| `employment_status` | viewer | none | Display only | No additional validation |
| `employment_exit` | viewer | optional `agent_id` | Optional agent selector | Maintain `_forbidden` message when admin path requested |
| `health_status` | viewer | none | Display only | None |
| `affordance_status` | viewer | none | Paginated view | Palette must truncate payload for display (>5k chars) |
| `promotion_status` | viewer | none | Display only | None |
| `relationship_summary` | viewer | none | Inline table | Ensure palette handles empty summary gracefully |
| `social_events` | viewer | optional `limit` (int) | Slider 1–20 (default 8) | Validate integer, clamp 1–100 |
| `perturbation_queue` | viewer | none | Display only | None |
| `snapshot_inspect` | viewer | `path` (str) | File picker prompt | Long-running / IO heavy – palette shows busy state |
| `snapshot_validate` | viewer | `path`, optional `strict` | File picker + checkbox | Warn if blocking >2 s; show migration outcome |
| `arrange_meet` | viewer | payload block | JSON editor using form template | Enforce agent existence + spec validation as today |

### 2.2 Admin-only matrix
| Command | Mode | Required params | Palette UX | Safety rails |
| --- | --- | --- | --- | --- |
| `relationship_detail` | admin | `agent_id` | Agent selector (restricted) | Hide command when not in admin mode |
| `possess` / `kill` | admin | `agent_id` | Confirmation dialog | Double-confirm (type agent id) before dispatch |
| `toggle_mortality` | admin | none | Simple toggle | Display resulting state |
| `set_exit_cap` | admin | `cap` (int) | Numeric input with min/max | Validate ≥0 and ≤ queue limit |
| `set_spawn_delay` | admin | `ticks` (int) | Numeric input | Clamp to 0–1440 |
| `perturbation_trigger` | admin | spec, optional duration/targets | Form template (spec dropdown, magnitude slider) | Validate spec against scheduler allowlist; show reason on failure |
| `perturbation_cancel` | admin | `event_id` | Dropdown of active IDs | Display `cancelled=False` gracefully |
| `snapshot_migrate` | admin | `path`, optional `output` | File picker | Blocking; show progress indicator |
| `promote_policy` / `rollback_policy` / `policy_swap` | admin | varies | Dedicated panel with metadata preview | Require file existence + display promotion snapshot |

### 2.3 Palette backlog (new commands required)
- **Spawn agent** → New lifecycle handler returning success/error payload; ensure spawn templates respect config capacity.
- **Set need** → Controlled mutation handler with bounded adjustments and audit log entry.
- **Force chat** → Hook scheduler/behaviour runtime to enqueue scripted chat with validation around cooldowns.
- **Perturbation filters** → Enhance `perturbation_queue` with filter kwargs so palette can show targeted subsets.

Fixtures for these backlog items live under `tests/data/palette_commands.json` (added in this phase) to keep schema examples next to automated dry-run checks.

### 2.4 Executor & validation observations
- `ConsoleCommandExecutor` already exposes `submit_payload`, which instantiates `PaletteCommandRequest` and returns the normalised `ConsoleCommand`. The palette can call this in “dry-run” mode to show the exact payload that will be dispatched before enqueueing it.
- The executor now supports optional pending limits (`max_pending`) and a non-enqueue inspection path (`submit_payload(..., enqueue=False)`). Palette should surface queue saturation errors (`CommandQueueFullError`) as a red banner and encourage operators to wait.
- Handlers expect positional arguments first (`command.args`) and then keyword overrides; palette forms should pre-normalise both so handlers keep receiving the shapes tested in `tests/test_console_commands.py`.
- Error responses typically include `{ "error": <code>, "message": <reason> }`; palette UI should surface both fields and preserve any attached metadata (`cmd_id`, `issuer`) so automation can correlate outcomes.

### 2.5 Fixture catalogue
- `tests/data/palette_commands.json` captures representative viewer/admin submissions plus backlog prototypes for spawn / set_need / force_chat. These power dry-run tests and UI previews.
- `tests/data/palette_command_errors.json` contains invalid payloads with expected error envelopes (usage violations, permission denials). Tests should load these fixtures to assert handler parity and ensure palette validation mirrors server behaviour.

## 3. Palette Interaction Model (Draft)
- **Activation**: `ctrl+p` toggles palette overlay. Secondary shortcuts (e.g. `:`) remain available for future features.
- **Navigation**: Fuzzy search input with up/down to select, `enter` to confirm. On selection, prompt for arguments using on-the-fly forms (e.g. agent dropdown populated from `snapshot.agents`).
- **Async dispatch**: Palette enqueues `ConsoleCommand` objects through `ConsoleCommandExecutor.submit`. Need to surface command UUID so results can be matched for inline feedback.
- **Result presentation**: Non-blocking status banner at top of overlay showing `success|error`, trimmed JSON payload, and optional link to open full object in side panel.
- **Accessibility**: Provide textual hints (`[Esc] close`, `[Tab] cycle fields`). Ensure palette is skippable when no TTY support (`--no-palette` flag).

### 3.1 Wireframe sketch (Rich modal)
```
+────────────────────────────────────────────────────────────────────────────+
| Palette ▸ ctrl+p                        [Esc] close   [Tab] next field      |
|────────────────────────────────────────────────────────────────────────────|
| › queue_inspect                     mode: viewer                          |
|   social_events                     limit ▸ 10                             |
|   employment_status                                                         |
|                                                                            |
|   Filters: [viewer] [admin] [custom]                                        |
|────────────────────────────────────────────────────────────────────────────|
| Command preview                                                             |
|   {"name": "queue_inspect", "args": ["coffee_shop_1"], "kwargs": {}}       |
|                                                                            |
| Result history                                                             |
|   ✓ social_events (tick 1204, 14 ms)                                        |
|   ⚠ queue_inspect — error: usage (missing object_id)                        |
+────────────────────────────────────────────────────────────────────────────+
```
- Search input sits at the top; arrow keys cycle suggestions, `ctrl+f` toggles filter chips.
- Command preview mirrors the dry-run payload returned by `submit_payload(..., enqueue=False)`.
- Result history shows last 5 outcomes with status glyphs; clicking enter on an error reopens the command pre-filled.
- Palette occupies 70% of terminal width, overlaying existing dashboard panels while dimming the background.

## 4. Async Routing Guardrails
- `ConsoleCommandExecutor` maintains a single background thread and unbounded queue. Palette must:
  - Guard against queue blow-up by bounding pending submissions (proposed cap 32, with warning banner).
  - Ensure thread-safe shutdown when dashboard exits (call `executor.shutdown()`).
  - Support command de-dup (optionally filter repeated identical commands within 5 ticks).
- Palette should record submission timestamps to measure round-trip latency for Phase 3 QA.
- Consider adding a non-blocking `peek_results()` helper so overlay can poll for command outcomes without blocking the render loop.

## 5. Telemetry Sparkline Buffer Prototype
To support per-agent sparklines, we propose extending telemetry payloads with optional history buckets while keeping existing clients functional.

### 5.1 Publisher additions (future)
```python
# TelemetryPublisher (future sketch)
self._history_buffers = {
    "needs": deque(maxlen=HISTORY_WINDOW),
    "wallet": deque(maxlen=HISTORY_WINDOW),
    "rivalry": deque(maxlen=HISTORY_WINDOW),
}
```
Each tick pushes `(tick, agent_id, metric_name, value)` entries.

### 5.2 Client schema proposal
`TelemetryClient.parse_snapshot` would accept an optional `history` section:
```json
{
  "history": {
    "needs": {"alice": [0.65, 0.64, ...]},
    "wallet": {"alice": [1.4, 1.35, ...]},
    "rivalry": {"alice|bob": [0.2, 0.25, ...]}
  }
}
```
- Keys remain optional; if absent, existing behaviour is unchanged.
- Buffer lengths default to 30 samples (~30s at default cadence) and are truncatable per config.
- Dashboard-level configuration flag `ui.history.enabled` toggles sparkline rendering to avoid performance regressions on low-powered TTYs.
- Backward compatibility: legacy clients that ignore the `history` key continue to function because new fields live under an optional top-level namespace with plain dict/list payloads.
- Client retention is configurable via `TelemetryClient(history_window=...)`; the dashboard passes through the window to trim sequences before rendering sparklines.
- Palette status banners communicate state via colour coding (`green` success, `yellow` warning, `cyan` preview) so accessibility guidance can map to ops runbooks.

## 6. Next Steps
1. Socialise this spec with ops & gameplay teams for command coverage sign-off.
2. Define concrete schema changes (`TelemetrySnapshot` dataclasses + version bump strategy).
3. Prototype palette overlay skeleton (Phase 1) using Rich Prompt + keyboard hooks.
4. Flesh out new console commands (spawn, set_need, force_chat) ahead of implementation phase.

## 7. Ops Review Log
- **2024-06-29** — Ops feedback captured: prefer `ctrl+p` primary shortcut, `alt+p` fallback for terminals where ctrl sequences are reserved. Requested queue saturation banner at ≥32 pending items and explicit confirmation when dispatching admin-only commands.
- **2024-06-29** — Gameplay ops confirmed sparkline buffers should default off for live demos; require `ui.history.enabled` flag documented for quick toggling.
