# Repository Guidelines

## Project Structure & Module Organization
Townlet keeps runtime code in `src/townlet/`, split into focused modules: `core/` for the tick loop, `policy/` for PettingZoo agents, and `world/` for grid primitives. Configuration entry points sit under `configs/` with curated examples in `configs/examples/` and experimentation branches in dedicated subfolders. Automation lives in `scripts/`, while design references stay in `docs/`. Mirror this layout in `tests/` when adding coverage so each module has a matching test suite.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — create and enter the project virtualenv.
- `pip install -e .[dev]` — install the package plus contributor tooling in editable mode.
- `python scripts/run_simulation.py --config configs/examples/base.yml` — run the baseline simulation loop.
- `python scripts/run_training.py --config configs/examples/base.yml` — exercise the training harness end-to-end.
- `pytest` — execute the full test suite; narrow scope with `pytest tests/test_<module>.py` while iterating.
- `ruff check src tests` and `mypy src` — lint, format, and type-check before sharing work.

## Coding Style & Naming Conventions
Use 4-space indentation, keep lines under 100 characters, and prefer descriptive snake_case for modules, functions, and variables. Classes use PascalCase and constants stay in UPPER_SNAKE. Run `ruff format` to normalise imports and whitespace, and address `ruff check` hints before committing. Add type hints and dataclasses where structure clarifies intent.

## Testing Guidelines
Pytest powers the suite; add files as `tests/test_<feature>.py` with functions named `test_<behavior>`. Cover success and failure paths, especially around config parsing and lifecycle transitions. Mark simulations that run longer than a few seconds with `@pytest.mark.slow` so they can be skipped via `pytest -m "not slow"`. Keep fixtures close to their consumers under the relevant test module.

## Commit & Pull Request Guidelines
Follow Conventional Commit prefixes (e.g., `feat`, `fix`, `docs`) and include a concise body describing intent and validation. PRs should link issues, outline behavioral changes, and note validation commands or logs. Ensure CI-relevant checks (`pytest`, `ruff`, `mypy`) pass before requesting review, and surface telemetry or screenshots when touching runtime surfaces.

## Configuration & Safety Tips
Treat `configs/examples/` as read-only references; place experimental variants in a new directory with a short README explaining intent. Never commit secrets—use environment variables or a local `.env` consumed by Typer CLI options. Document significant configuration or architecture shifts in `docs/` so future contributors understand rationale.
