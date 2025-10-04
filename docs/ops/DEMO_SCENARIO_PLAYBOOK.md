# Demo Story Arc Scenario Playbook

Reference hashes:
- `configs/scenarios/demo_story_arc.yaml` — `c3ebb8fbfc9bc6ab793aeb3784a6bf1cf044c8b0`
- `configs/scenarios/timelines/demo_story_arc.yaml` — `dafe8f3298f62e1ddeaf0fd40c7907fc3507b2d6`

Use this playbook when rehearsing the narrative demo storyline (`storyline_id = demo_story_arc`).

## 1. Operator Setup
- Activate the virtualenv and ensure editable dependencies are installed:
  ```bash
  source .venv/bin/activate
  pip install -e .[dev]
  ```
- Run the rehearsal helper (adjust `TICKS` or flags as needed):
  ```bash
  scripts/demo_rehearsal.sh --narration-level summary
  ```
- Manual dashboard: launch `python -m townlet_ui.dashboard --config configs/scenarios/demo_story_arc.yaml` in a second terminal when prompted by the script.
- Personality tooling:
  - Use `--personality-filter <profile>` (e.g., `stoic`) when calling
    `scripts/demo_run.py` to spotlight specific archetypes in the agent cards.
  - Pass `--mute-personality-narration` if the audience does not need trait-driven
    narration beats (relationship/conflict narrations still appear).
  - The web spectator mirrors the same controls (“Show personality stories” toggle).
- Capture narration output for regression comparison against `tests/data/demo_story_arc_narrations.json`.

## 2. Stage & Cue Timeline

| Tick (±2) | Beat | Operator Cue | Telemetry Expectations |
| --- | --- | --- | --- |
| 0 | Warm-up | Confirm Rich dashboard panels populated; narrations show warmup message. | `narrations[0].category = demo_story`, relationship friendship narrations for demo agents, employment panel green. |
| 8 | Avery ↔ Kai | Highlight social panel and narrations for forced chat. | `loop.telemetry.latest_narrations()` includes `relationship_friendship` deltas; palette banner cyan when `force_chat` executes. |
| 18 | Avery energy boost | Mention in narration log (optional) and verify agents panel needs adjust. | Agent `avery.needs.energy ≈ 0.68`; reward panel remains neutral. |
| 40 | Blair arrival | Announce new resident; point out agent card for `blair`. | Agent `blair` visible with wallet 2.5; employment panel shows pending cafe shift. |
| 46 | Blair ↔ Avery intro | Call out relationship delta; remind viewers of upcoming disruption. | Narrations include `force_chat` follow-up; friendship scores rise. |
| 60 | Price spike perturbation | Trigger console banner commentary; ensure audience sees perturbation status turn red. | `perturbation_trigger price_spike` queued (`ConsoleCommandExecutor` status green); telemetry perturbation panel lists active spike (magnitude 1.55). |
| 72 | Blair fatigue | Mention energy dip; pivot to employment lateness risk. | Agent `blair.needs.energy ≈ 0.35`; employment lateness stays < threshold. |
| 88 | Kai ↔ Blair encouragement | Narrate recovery arc; point to friendship narrations. | Narrations show `relationship_friendship` for Kai/Blair plus optional `personality_event` highlighting extroversion; conflict panel remains nominal. |
| 110 | Arrange meet | Highlight operator-triggered reconciliation; ensure palette banner green. | `perturbation_trigger arrange_meet` executes; turbulence banner clears within 20 ticks. |
| 126 | Closing social beat | Deliver final narration (scripted in timeline extension if desired) and tee up wrap-up. | Friendship narrations reflect Avery → Blair confidence; employment KPIs cooling. |

## 3. Operator Checklist
1. Start rehearsal via `scripts/demo_rehearsal.sh` (logs go to stdout by default).
2. Verify narration stream matches golden fixture using `pytest tests/test_demo_timeline.py::test_demo_story_arc_narrations_match_golden`.
3. Capture dashboard screenshots: warm-up (tick ~5), price spike (tick ~65), recovery (tick ~115).
4. Record console log snippets for `announce_story` outputs (palette status green, pending count resets).
5. Note any deviations; if config/timeline changes occur, recompute hashes (`git hash-object`) and regenerate `tests/data/demo_story_arc_narrations.json`.

## 4. Troubleshooting
- **Narration missing**: Ensure `--narration-level` not `off`; check palette banner for queue saturation; rerun with larger tick spacing between narration events.
- **Telemetry drift**: Confirm `seed` and timeline hash match above references; rerun rehearsal after cleaning `logs/`.
- **Observer UI lag**: Increase `--refresh` interval or set `--history-window 20` when launching `scripts/demo_run.py` manually.

## 5. Artefact Capture & Reporting
- Store latest rehearsal transcript in `docs/samples/demo_story_arc/` (create if missing) including:
  - `command_log.txt` – CLI output from rehearsal run.
  - `narrations.json` – exported narration stream (tie back to golden fixture).
  - `screenshots/` – PNG captures of dashboard panels for each beat.
- Update the Forward Work Program entry with completion notes (see `audit/FORWARD_WORK_PROGRAM.md`), including the latest config hashes listed in this playbook.
- Share highlight reel (terminal recording or GIF) ahead of stakeholder demos to reinforce cue timing.
