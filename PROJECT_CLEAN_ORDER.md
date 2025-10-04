# Project Clean Order

This prioritised backlog is derived from a repository-wide `ruff check` on the current main branch.
Counts reflect outstanding lint diagnostics per file and highlight the dominant rule breaches to
help target modernisation and quality wins.

| Priority | File | Ruff findings | Observations & opportunities |
| --- | --- | --- | --- |
| 1 | `src/townlet/config/loader.py` | 38 issues &mdash; UP037×21, UP031×6, N805×5 | Central config loader still uses legacy typing syntax and camelCase arguments; fixing it should ripple type safety and doc clarity across the project. |
| 2 | `src/townlet/world/grid.py` | 38 issues &mdash; C416×7, UP038×7, B904×7 | Core world grid logic mixes comprehension anti-patterns and outdated isinstance checks; refactor to clarify error propagation and modern typing. |
| 3 | `scripts/telemetry_watch.py` | 35 issues &mdash; E501×31, RUF001×2 | CLI watch utility breaches line-length and string-style rules; opportunity to adopt pathlib and rich logging. |
| 4 | `src/townlet/observations/builder.py` | 33 issues &mdash; UP037×31 | Observation builder still quotes annotations; converting to modern generics unlocks strict typing downstream. |
| 5 | `scripts/telemetry_summary.py` | 26 issues &mdash; E501×22 | Summary CLI long lines and outdated patterns; refactor for readability and reuse of telemetry parsing. |
| 6 | `src/townlet/snapshots/state.py` | 20 issues &mdash; UP045×10 | Snapshot models mix Optional typing helpers; aligning with 3.12 syntax and dataclass usage improves maintainability. |
| 7 | `src/townlet/policy/runner.py` | 18 issues &mdash; UP038×8 | Policy runner still relies on legacy type checks and import ordering; modernising clarifies runtime composition. |
| 8 | `scripts/manage_phase_c.py` | 16 issues &mdash; UP006×12 | Phase-C management script imports typing aliases and uses long lines; clean-up will reduce CLI debt. |
| 9 | `src/townlet/policy/replay.py` | 16 issues &mdash; UP045×12 | Replay module needs Optional rewrite and type clarity to stabilise training pipelines. |
| 10 | `scripts/capture_scripted.py` | 13 issues &mdash; UP006×8 | Scripted capture CLI has legacy typing and long strings; a refactor will standardise CLI ergonomics. |

The remaining files carry progressively fewer diagnostics and can follow once the highest-impact
modules are professionalised.
