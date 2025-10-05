# Docstring Guide

This addendum captures the conventions we follow when documenting the Townlet runtime. Use it to keep docstrings consistent while we drive WP-307.

## Scope

Apply these rules to all modules under `src/townlet/` and their mirrored tests. Runtime code that is re-exported for policy, telemetry, or UI consumers must have docstrings that describe the stability contract surface.

## Module Docstrings

- Start every module with a one-line summary that states the primary responsibility (e.g. `"""Telemetry transport adapters."""`).
- Mention key collaborators or configuration touchpoints in a brief second line if needed (e.g. `Depends on TelemetryTransportConfig`). Avoid duplicating implementation detail.
- Reference design docs using the `DESIGN#` notation when behaviour is governed by a spec section.

## Class Docstrings

- The first sentence explains the role of the type and the lifecycle boundaries it manages.
- Document invariants or hooks that callers must respect (e.g. required callbacks, RNG ownership).
- For dataclasses, note any derived fields that are calculated outside `__init__` to avoid surprises.

## Function and Method Docstrings

- Provide a short imperative summary: "Compute policy logits" instead of "This function computes".
- List important parameters using the `Args:` section only when the signature is non-trivial. Example:

  ```markdown
  Args:
      world: Active `WorldState` snapshot.
      tick: Current simulation tick for telemetry alignment.
  ```

- Describe the return value in a `Returns:` block when it is not obvious from the type annotation.
- Call out side effects (mutating inputs, emitting telemetry, scheduling async work) in a `Side Effects:` or `Raises:` block.

## Formatting

- Keep docstrings within 100 characters per line.
- Use reStructuredText field lists (`:param name:`) only when the function needs to integrate with Sphinx. Default to Google-style sections for readability.
- Avoid mentioning argument types (the annotations already express them) unless emphasising units or value ranges.

## Examples

When examples are helpful, prefer minimal snippets that show the public interface. Do not include long CLI transcripts. For doctests, ensure `pyproject.toml` opts out of execution until we have a stable doctest gate.

## Testing Hooks

If a docstring documents behaviour guarded by a feature flag, mention the associated pytest marker so reviewers know which suites to run.

## Updating Documentation

After adding docstrings for a module with an external consumer, update the relevant `docs/` reference (for example, telemetry transport updates feed `docs/ops/TELEMETRY_TLS_SETUP.md`).

## Review Checklist

Before sending your change:

- Run `tox -e docstrings` (or `scripts/check_docstrings.py` directly) to ensure module coverage ≥90% and callable coverage ≥40%.

- Private helper functions (names starting with `_`) are ignored by the coverage checker; focus docstrings on exported APIs.
- Ensure new docstrings match the tone above and link design references where applicable.
- Add follow-up TODOs sparingly—prefer filing an issue when a docstring reveals missing behaviour clarification.
