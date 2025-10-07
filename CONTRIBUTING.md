# Contributing to Townlet

Thank you for your interest in shaping Townlet. This guide summarises how we work, how to set up your environment, and where to focus implementation effort.

## Development Workflow

1. Fork/branch from `main`.
2. Align with the design artefacts in `docs/` and confirm that your change respects the active `config_id`.
3. Keep changes modular and well tested. Touch only the observation variant flagged in `features.observations` unless coordinating an A/B gate.
4. Run the quality gates locally before pushing:
   ```bash
   ruff check src tests
   mypy src
   pytest
   scripts/check_docstrings.py src/townlet --min-module 95 --min-callable 40
   ```
   - If you modify configuration models under `src/townlet/config/`, regenerate the reference docs before committing:
     ```bash
     python scripts/gen_config_reference.py --out docs/guides/CONFIG_REFERENCE.md
     ```
     Include the regenerated `docs/guides/CONFIG_REFERENCE.md` in your PR to keep docs in sync.
5. Open a pull request using the template. Summarise behaviour, risks, and validation evidence.

## Coding Standards

- Refer to `docs/guides/DOCSTRING_GUIDE.md` for docstring tone and formatting.
- Target Python 3.11+ with type annotations and `from __future__ import annotations` in new modules.
- Keep modules small and cohesive. Cross-module interactions should use clearly defined dataclasses or protocols.
- Use feature flags (`features.*`) to guard work-in-progress systems. Do not couple experimental behaviour to ad-hoc conditionals.
- Avoid global singletons. Pass explicit handles (e.g., RNG streams, config slices) to functions and classes.
- Docstrings should describe responsibilities, inputs, outputs, and any stability hooks or guardrails involved.

## Testing Expectations


- Run the telemetry transport and observer smoke suites when touching `src/townlet/telemetry` or `src/townlet_ui/`:
  ```bash
  pytest tests/test_telemetry_client.py tests/test_observer_ui_dashboard.py \
         tests/test_telemetry_stream_smoke.py tests/test_telemetry_transport.py
  ```
- Unit tests for config validation, reward calculations, lifecycle gates.
- Property-based/fuzz tests for queues, scheduler fairness, and economy invariants (see `docs/REQUIREMENTS.md`).
- Golden tests for YAML schemas and telemetry payloads.
- Run the snapshot regression subset when touching persistence or RNG surfaces:
  ```bash
  pytest tests/test_utils_rng.py tests/test_snapshot_manager.py \
         tests/test_snapshot_migrations.py tests/test_sim_loop_snapshot.py
  ```
- Keep test data and fixtures under `tests/fixtures/` if needed.

## Communication

- Use GitHub Discussions for architectural questions.
- Tag design references (e.g., `DESIGN#4.1`) in code comments where behaviour follows a specific spec section.
- Escalate canary or KPI regression risks early.

## Code of Conduct

By participating you agree to abide by the [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
