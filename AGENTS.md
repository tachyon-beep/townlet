# Repository Guidelines

## Project Structure & Module Organization
Townlet uses a src-layout Python package. Core code lives in `src/townlet/`, split into domain-focused modules such as `core/` for the tick loop, `policy/` for PettingZoo integration, and `world/` for grid primitives. Configuration entry points sit in `configs/` (e.g., `configs/examples/`, `configs/affordances/`, `configs/perturbations/`). Automation scripts for running the simulator or training loops are in `scripts/`. Reference documentation and design context are under `docs/`. Tests reside in `tests/`, mirroring the package layout; add new suites beside the feature you touch.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — Set up an isolated environment.
- `pip install -e .[dev]` — Install runtime and contributor dependencies with editable source.
- `python scripts/run_simulation.py --config configs/examples/base.yml` — Run the scaffolded sim loop against a canonical config.
- `python scripts/run_training.py --config configs/examples/base.yml` — Exercise the training harness and integration stubs.
- `pytest` — Execute the test suite; narrow scope with `pytest tests/test_config_loader.py` while iterating.
- `ruff check src tests` and `mypy src` — Lint/format and type-check before pushing.

## Coding Style & Naming Conventions
Write Python with 4-space indentation and respect the 100-character soft limit enforced by Ruff. Modules and functions use `snake_case`; classes use `PascalCase`; constants stay UPPER_SNAKE. Prefer type-hinted dataclasses or Pydantic models for structured state. Run `ruff format` to auto-sort imports and normalise whitespace. Keep TODOs in the existing `# TODO(@townlet): context` format to aid tracking.

## Testing Guidelines
Target pytest for all coverage. Name files `test_<feature>.py` and functions `test_<behavior>`. Add regression cases for config parsing, lifecycle transitions, and scheduler logic whenever those modules change. Exercise both success and failure paths; mark long-running sims with `@pytest.mark.slow` so they can be excluded locally (`pytest -m "not slow"`).

## Commit & Pull Request Guidelines
Follow Conventional Commit prefixes (`feat`, `fix`, `docs`, etc.) as seen in history. Keep commits focused and include a body describing intent and validation. PRs should link relevant issues, summarise behaviour changes, list commands run, and attach telemetry snapshots or logs when touching runtime surfaces. Ensure CI passes and request review before merge.

## Configuration & Safety Tips
Treat `configs/examples/` as read-only references; add experimental variants under a new subdirectory with a short README. Document major config or architecture shifts in `docs/` (e.g., `HIGH_LEVEL_DESIGN.md`) so other agents can trace rationale. Never commit secrets—use environment variables or local `.env` files consumed by Typer CLI options.
