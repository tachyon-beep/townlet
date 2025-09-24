# Townlet

Townlet is a small-town life simulation that explores emergent behaviour in a population of reinforcement-learning agents. The proof of concept targets 6–10 agents living in a 48×48 grid world with scripted primitives, hierarchical options, and configurable observation variants. This repository contains the core simulation, training harness, telemetry surfaces, and operational tooling described in `docs/CONCEPTUAL_DESIGN.md`, `docs/HIGH_LEVEL_DESIGN.md`, and `docs/REQUIREMENTS.md`.

## Status

- ✅ Design documents captured in `docs/`
- 🚧 Simulation, training, and UI modules scaffolded with interfaces and TODO markers
- ⏳ Implementation work tracked via GitHub issues and milestones

## Repository Layout

```
.
├── configs/               # Canonical YAML configuration entry points (features, rewards, affordances, perturbations)
├── docs/                  # Product, design, and planning documentation
├── scripts/               # CLI entry points for running the sim, training, and tooling
├── src/townlet/           # Python package implementing the simulator and services
│   ├── agents/            # Agent state, personalities, relationships
│   ├── console/           # Admin/viewer console adapters and auth
│   ├── config/            # Config schema, loaders, feature flag validation
│   ├── core/              # Main tick loop orchestration
│   ├── lifecycle/         # Exit conditions, spawn logic, population caps
│   ├── observations/      # Observation builders per variant, masks, embeddings
│   ├── policy/            # PettingZoo env wrapper, scripted controllers, PPO integration hooks
│   ├── rewards/           # Reward engine and normalisation scaffolding
│   ├── scheduler/         # Perturbation scheduler, fairness buckets, time dilation
│   ├── snapshots/         # Save/load primitives and config identity enforcement
│   ├── stability/         # Guardrails, canary monitors, release promotion
│   ├── telemetry/         # Pub/sub observer API, KPI emitters, schema definitions
│   └── world/             # Grid representation, affordances, economy, queues
├── tests/                 # Pytest suites exercising config loading and module integrity
├── .github/               # CI, issue templates, pull request guide
└── pyproject.toml         # Tooling configuration (ruff, mypy, pytest, build metadata)
```

## Quickstart

1. Install dependencies (Python 3.11+ recommended):
   ```bash
   pip install -e .[dev]
   ```
2. Run the placeholder smoke test:
   ```bash
   pytest
   ```
3. Explore config examples in `configs/examples/` and align `config_id` before running simulations.

Implementation TODOs are captured with `# TODO(@townlet)` markers inside the package. Each module outlines its responsibilities, inputs, and integration points with the rest of the system.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for development workflow, coding standards, and testing expectations.
