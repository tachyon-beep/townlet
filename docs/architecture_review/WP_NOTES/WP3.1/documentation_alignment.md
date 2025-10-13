# Documentation & Verification Alignment Plan

## Background
WP3 status files and ops guides claim Stage 6 is complete, yet the repository still contains the legacy shims. We need to update documentation only after the code matches the target state and run the promised verification suite (pytest, ruff, mypy, docstring coverage).

## Current State Audit
- `docs/architecture_review/WP_NOTES/WP3/status.md` marks Stage 6 complete with inaccurate statements about console queue removal and observation builder retirement.
- `docs/ops/CONSOLE_ACCESS.md`, `docs/engineering/CONSOLE_COMMAND_CONTRACT.md`, and related guides still describe the queue-based API.
- `docs/design/OBSERVATION_TELEMETRY_PHASE3.md` references `ObservationBuilder` behaviour.
- No recovery log exists for the Stage 6 verification sweep.

## Implementation Plan

### 1. Communication Prep
1.1 Draft internal summary (`WP3.1/communication_draft.md`) outlining:
    - Gap between reported Stage 6 status and repo reality.
    - Planned remediation timeline.
    - Expected API changes (console submission, observation builder removal).
1.2 Circulate draft to WP1/WP2 leads for sign-off before code lands.

### 2. Documentation Updates *(execute after code merges)*
2.1 Update `WP3/status.md` with an explicit “Stage 6 Recovery” section listing:
    - Actual completion date.
    - Summary of removals (queue, adapter shims, builder).
    - Verification commands with PASS indicators.
2.2 Amend `legacy_grid_cleanup_plan.md` to record Batch E execution details.
2.3 Rewrite console guides:
    - `docs/ops/CONSOLE_ACCESS.md`: replace queue-focused workflow with
      dispatcher submission example (code snippet + auth notes).
    - `docs/engineering/CONSOLE_COMMAND_CONTRACT.md`: update contract tables.
2.4 Update observation docs (`docs/design/OBSERVATION_TELEMETRY_PHASE3.md`,
    `docs/testing/QA_CHECKLIST.md`) to remove builder references and describe DTO
    envelope usage.
2.5 Append release/migration notes to existing changelog or create
    `docs/releases/WP3_stage6_recovery.md` summarising externally-visible
    changes.

### 3. Verification Sweep & Logging
3.1 After all code changes merge, run:
    - `pytest --cov=src/townlet --cov-report=term-missing`.
    - `pytest tests/test_console_router.py tests/core/test_sim_loop_dto_parity.py -q`
      (spot checks recorded separately).
    - `ruff check src tests`.
    - `ruff format --check src tests` (ensure formatting consistent).
    - `mypy src`.
    - `python scripts/check_docstrings.py src/townlet --min-module 95 --min-callable 40`.
3.2 Capture stdout/stderr for each command and summarise in
    `WP3.1/stage6_recovery_log.md` (include timestamp, exit code, key metrics).

### 4. Status File Updates
4.1 Once verification passes, update WP1/WP2 status docs to acknowledge Stage 6
    completion and unblock dependencies.
4.2 Link the recovery log and release notes for traceability.
4.3 Update `regression_plan.json` if thresholds/commands changed.

### 5. Post-Mortem & Prevention
5.1 Write a brief post-mortem section in the recovery log covering:
    - Root cause analysis.
    - Detection gaps.
    - Process changes (e.g. gating documentation updates on CI evidence).
5.2 Share the summary with leadership/QA via the chosen channel (Slack/email).

### 6. Validation Sequence
- All documentation PRs reviewed by respective module owners.
- Recovery log populated with command outputs and sign-off checklist.
- `rg "queue_console_command" docs`, `rg "ObservationBuilder" docs` return 0.
- Communication draft approved by WP1/WP2 leads prior to publication.

## Validation Checklist
- [ ] All documentation changes reviewed by module owners (console, telemetry, observations).
- [ ] Verification commands recorded with timestamps and PASS results.
- [ ] No references remain to the removed APIs (`rg "queue_console_command" docs/`, `rg "ObservationBuilder" docs/`).
- [ ] Recovery log filed and linked from `README.md`.

## Risks & Mitigations
- **Documentation drift:** ensure doc updates are gated on code reviews; coordinate merges carefully.
- **Command failures:** capture any failing outputs in the recovery log and track follow-up tasks.
- **Stakeholder visibility:** provide regular updates via WP status channels to rebuild confidence after the miss.

## Dependencies
- Runs after console, adapter, and observation builder workstreams complete and land on `main`.
