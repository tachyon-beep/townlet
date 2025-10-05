# WP-307 Docstring Coverage RFC

## Context

WP-307 raises docstring coverage and introduces guardrails so exported APIs stay discoverable. The codebase currently lacks a consistent policy for executable examples or doctests. This note records the expectations for reviewers and build tooling before we make sweeping edits.

## Proposal

1. **Docstring Coverage Tooling**
   - Adopt the lightweight AST-based coverage script (see `tmp/wp307/baseline_docstring_coverage.txt`) for fast local feedback; it produces machine-readable outputs (`modules_without_docs.csv`, `missing_callables.json`).
   - Leverage the upstream `interrogate` CLI (configured via `[tool.interrogate]` in `pyproject.toml`) alongside the script and expose both through `tox -e docstrings` for reproducible checks. Current guardrails: module coverage ≥95%, callable coverage ≥40%, interrogate `fail-under` set to 40%. The local checker ignores private (`_name`) callables to mirror interrogate defaults.

2. **Doctest Policy**
   - Treat docstrings as narrative documentation only; do not execute doctests in CI until the simulation APIs stabilise. Examples should be illustrative snippets rather than full workflows.
   - When executable samples are required (e.g., configuration loading), add pytest-based documentation tests under `tests/docs/` instead of doctests. Link the test file in the docstring using `See also: tests/docs/test_config_examples.py` to preserve traceability.

3. **Change Review Expectations**
   - Pull requests that add new modules or public callables must include docstrings that follow `docs/guides/DOCSTRING_GUIDE.md`.
   - Reviewers may accept legacy modules without docstrings until we raise the threshold, but new touchpoints should not regress coverage.

## Open Questions

- Should policy backends expose autodoc-compatible API docs once Phase 3 completes?
- Do we require locale-specific examples for user-facing CLI docstrings?

## Next Steps

- Circulate this RFC to the platform and telemetry leads for sign-off.
- Create a follow-up issue to track integration of the coverage script into `tox` and CI.
- Document the agreed defaults in the contributor guide after the first enforcement PR lands.

* 2025-10-06: WP-308 deferred until post-architecture stabilization.
