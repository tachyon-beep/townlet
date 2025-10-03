# Command Palette QA Checklist

## Environment Prep
- [ ] Launch `run_dashboard` against `configs/examples/poc_hybrid.yaml` with relationships stage enabled (ensures social telemetry).
- [ ] Ensure `ui.history.enabled=true` in observer config to surface sparkline buffers.

## Keyboard & Focus
- [ ] `Ctrl+P` opens the palette overlay and initial focus lands on the search prompt.
- [ ] `Tab` cycles search → filter chips → history panel without skipping interactive elements.
- [ ] `Esc` dismisses the palette and returns focus to the dashboard scrollback.

## Command Execution
- [ ] Selecting `queue_inspect` with `Enter` dispatches instantly; pending banner increments then returns to 0 within 2 refreshes.
- [ ] Attempting an admin command in viewer mode surfaces the yellow warning banner (`Queue saturated` or `forbidden`).
- [ ] `Ctrl+L` toggles the result log panel while the palette is open (no layout jitter).

## Accessibility & Contrast
- [ ] Palette border contrasts against dimmed dashboard background (WCAG AA equivalent when tested in 120×40 terminal).
- [ ] Status banners use consistent colour semantics (`green=success`, `yellow=warning`).
- [ ] Sparklines remain legible on dark and light terminal themes.

## Performance & Latency
- [ ] Holding palette open for 30s does not increase tick latency beyond ±10% of baseline.
- [ ] Queue saturation at 32 pending commands triggers warning without freezing render loop.

## Telemetry History Verification
- [ ] Needs/wallet/rivalry sparklines update within two ticks when metrics change.
- [ ] Disabling history buffers (`ui.history.enabled=false`) falls back to `n/a` placeholders without errors.

## Regression Sweep
- [ ] `pytest tests/test_console_commands.py tests/test_ui_telemetry.py tests/test_dashboard_panels.py` passes locally.
- [ ] Manual smoke of `render_snapshot(..., palette=PaletteState(visible=True))` shows overlay appended after telemetry panel.
