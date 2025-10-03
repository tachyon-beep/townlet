# Command Palette Shortcuts & Usage

- `Ctrl+P` — open/close palette overlay (fallback `Alt+P` documented for terminals that intercept Ctrl combos).
- `Tab` / `Shift+Tab` — cycle input fields and filter chips inside the palette.
- `Up` / `Down` — navigate command suggestions; suggestions auto-filter by mode (viewer/admin).
- `Enter` — confirm selection; palette will prompt for required params before dispatching.
- `Ctrl+L` — toggle command result log panel within the overlay.
- `Ctrl+F` — focus filter chip row to include/exclude admin or custom commands quickly.
- `Esc` — cancel current interaction, close overlay, and return focus to dashboard timeline.

Notes:
- The palette uses dry-run payload previews; operators can inspect the command JSON before sending.
- Admin-only commands prompt for confirmation and show the active mode in the header.
- Queue saturation banner appears when 32+ pending commands are detected; commands can still be queued but will warn about potential delays.
- Telemetry history buffers drive sparklines: set `ui.history.enabled=true` in observer config (or adjust `TelemetryClient(history_window=...)`) to control retention. When disabled, the dashboard falls back to `n/a` placeholders.
- Palette status banners follow consistent colour semantics (`green=success`, `yellow=warning`, `cyan=preview`).
