# Module Documentation

## `scripts/audit_bc_datasets.py`

**Purpose**: Audit behaviour cloning datasets for checksum and metadata freshness.
**Lines of code**: 161
**Dependencies**: stdlib=__future__, argparse, datetime, hashlib, json, pathlib, typing; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_versions(path: Path) -> Mapping[str, Mapping[str, object]]` — No docstring provided.
- `audit_dataset(name: str, payload: Mapping[str, object]) -> dict[str, object]` — No docstring provided.
- `audit_catalog(versions_path: Path) -> dict[str, object]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `DEFAULT_VERSIONS_PATH = Path('data/bc_datasets/versions.json')`
- `REQUIRED_VERSION_KEYS = {'manifest', 'checksums', 'captures_dir'}`

### Data Flow
- Inputs: name, path, payload, versions_path
- Processing: Orchestrated via classes None and functions audit_catalog, audit_dataset, load_versions, main, parse_args.
- Outputs: Mapping[str, Mapping[str, object]], None, argparse.Namespace, dict[str, object]
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Functions without docstrings: audit_catalog, audit_dataset, load_versions, main, parse_args.

## `scripts/bc_metrics_summary.py`

**Purpose**: Summarise behaviour cloning evaluation metrics.
**Lines of code**: 52
**Dependencies**: stdlib=__future__, argparse, json, pathlib; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_metrics(path: Path) -> list[dict[str, float]]` — No docstring provided.
- `summarise(metrics: list[dict[str, float]]) -> dict[str, float]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: metrics, path
- Processing: Orchestrated via classes None and functions load_metrics, main, parse_args, summarise.
- Outputs: None, argparse.Namespace, dict[str, float], list[dict[str, float]]
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Functions without docstrings: load_metrics, main, parse_args, summarise.

## `scripts/benchmark_tick.py`

**Purpose**: Simple benchmark to estimate average tick duration.
**Lines of code**: 38
**Dependencies**: stdlib=__future__, argparse, pathlib, time; external=None; internal=townlet.config, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.core.sim_loop

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `benchmark(config_path: Path, ticks: int, enforce: bool) -> float` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: config_path, enforce, ticks
- Processing: Orchestrated via classes None and functions benchmark, main, parse_args.
- Outputs: None, argparse.Namespace, float
- Downstream modules: townlet.config, townlet.core.sim_loop

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop

### Code Quality Notes
- Functions without docstrings: benchmark, main, parse_args.

## `scripts/capture_rollout.py`

**Purpose**: CLI to capture Townlet rollout trajectories into replay samples.
**Lines of code**: 140
**Dependencies**: stdlib=__future__, argparse, datetime, json, pathlib, typing; external=numpy; internal=townlet.config.loader, townlet.core.sim_loop, townlet.policy.metrics, townlet.policy.replay, townlet.policy.scenario_utils
**Related modules**: townlet.config.loader, townlet.core.sim_loop, townlet.policy.metrics, townlet.policy.replay, townlet.policy.scenario_utils

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions main, parse_args.
- Outputs: None, argparse.Namespace
- Downstream modules: townlet.config.loader, townlet.core.sim_loop, townlet.policy.metrics, townlet.policy.replay, townlet.policy.scenario_utils

### Integration Points
- External libraries: numpy
- Internal packages: townlet.config.loader, townlet.core.sim_loop, townlet.policy.metrics, townlet.policy.replay, townlet.policy.scenario_utils

### Code Quality Notes
- Functions without docstrings: main, parse_args.

## `scripts/capture_rollout_suite.py`

**Purpose**: Run rollout capture across a suite of configs.
**Lines of code**: 112
**Dependencies**: stdlib=__future__, argparse, pathlib, typing; external=subprocess, sys; internal=townlet.config.loader
**Related modules**: townlet.config.loader

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `run_capture(config: Path, ticks: int, output: Path, auto_seed: bool, agent_filter: str | None, compress: bool, retries: int) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_filter, auto_seed, compress, config, output, retries, ticks
- Processing: Orchestrated via classes None and functions main, parse_args, run_capture.
- Outputs: None, argparse.Namespace
- Downstream modules: townlet.config.loader

### Integration Points
- External libraries: subprocess, sys
- Internal packages: townlet.config.loader

### Code Quality Notes
- Functions without docstrings: main, parse_args, run_capture.

## `scripts/capture_scripted.py`

**Purpose**: Capture scripted trajectories for behaviour cloning datasets.
**Lines of code**: 131
**Dependencies**: stdlib=__future__, argparse, collections, json, pathlib, typing; external=numpy; internal=townlet.config, townlet.core.sim_loop, townlet.policy.replay, townlet.policy.scenario_utils, townlet.policy.scripted
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.policy.replay, townlet.policy.scenario_utils, townlet.policy.scripted

### Classes
- None

### Functions
- `parse_args(argv: List[str] | None = None) -> argparse.Namespace` — No docstring provided.
- `_build_frame(adapter: ScriptedPolicyAdapter, agent_id: str, observation: Dict[str, np.ndarray], reward: float, terminated: bool, trajectory_id: str) -> Dict[str, object]` — No docstring provided.
- `main(argv: List[str] | None = None) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: adapter, agent_id, argv, observation, reward, terminated, trajectory_id
- Processing: Orchestrated via classes None and functions _build_frame, main, parse_args.
- Outputs: Dict[str, object], None, argparse.Namespace
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.policy.replay, townlet.policy.scenario_utils, townlet.policy.scripted

### Integration Points
- External libraries: numpy
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.policy.replay, townlet.policy.scenario_utils, townlet.policy.scripted

### Code Quality Notes
- Functions without docstrings: _build_frame, main, parse_args.

## `scripts/console_dry_run.py`

**Purpose**: Employment console dry-run harness.
**Lines of code**: 126
**Dependencies**: stdlib=__future__, pathlib; external=tempfile; internal=townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.state, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.state, townlet.world.grid

### Classes
- None

### Functions
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions main.
- Outputs: None
- Downstream modules: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.state, townlet.world.grid

### Integration Points
- External libraries: tempfile
- Internal packages: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.state, townlet.world.grid

### Code Quality Notes
- Functions without docstrings: main.

## `scripts/curate_trajectories.py`

**Purpose**: Filter and summarise behaviour-cloning trajectories.
**Lines of code**: 104
**Dependencies**: stdlib=__future__, argparse, dataclasses, json, pathlib, typing; external=numpy; internal=townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- `EvaluationResult` — defined at line 17; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - sample_path: Path (public)
    - meta_path: Path (public)
    - metrics: Mapping[str, float] (public)
    - accepted: bool (public)
  - Methods: None declared

### Functions
- `parse_args(argv: List[str] | None = None) -> argparse.Namespace` — No docstring provided.
- `_pair_files(directory: Path) -> Iterable[tuple[Path, Path]]` — No docstring provided.
- `evaluate_sample(npz_path: Path, json_path: Path) -> EvaluationResult` — No docstring provided.
- `curate(result: EvaluationResult, *, min_timesteps: int, min_reward: float | None) -> EvaluationResult` — No docstring provided.
- `write_manifest(results: Iterable[EvaluationResult], output: Path) -> None` — No docstring provided.
- `summarise(results: Iterable[EvaluationResult]) -> Mapping[str, float]` — No docstring provided.
- `main(argv: List[str] | None = None) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: argv, directory, json_path, min_reward, min_timesteps, npz_path, output, result, results
- Processing: Orchestrated via classes EvaluationResult and functions _pair_files, curate, evaluate_sample, main, parse_args, summarise, write_manifest.
- Outputs: EvaluationResult, Iterable[tuple[Path, Path]], Mapping[str, float], None, argparse.Namespace
- Downstream modules: townlet.policy.replay

### Integration Points
- External libraries: numpy
- Internal packages: townlet.policy.replay

### Code Quality Notes
- Functions without docstrings: _pair_files, curate, evaluate_sample, main, parse_args, summarise, write_manifest.
- Uses dataclasses for structured state.

## `scripts/manage_phase_c.py`

**Purpose**: Helper script to toggle Phase C social reward stages in configs.
**Lines of code**: 164
**Dependencies**: stdlib=__future__, argparse, pathlib, typing; external=yaml; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_config(path: Path) -> Dict[str, Any]` — No docstring provided.
- `ensure_nested(mapping: Dict[str, Any], keys: List[str]) -> Dict[str, Any]` — No docstring provided.
- `write_config(data: Dict[str, Any], *, output: Path | None, in_place: bool, source: Path) -> None` — No docstring provided.
- `handle_set_stage(args: argparse.Namespace) -> None` — No docstring provided.
- `parse_schedule_entries(entries: List[str]) -> List[Dict[str, Any]]` — No docstring provided.
- `handle_schedule(args: argparse.Namespace) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `VALID_STAGES = {'OFF', 'C1', 'C2', 'C3'}`

### Data Flow
- Inputs: args, data, entries, in_place, keys, mapping, output, path, source
- Processing: Orchestrated via classes None and functions ensure_nested, handle_schedule, handle_set_stage, load_config, main, parse_args, parse_schedule_entries, write_config.
- Outputs: Dict[str, Any], List[Dict[str, Any]], None, argparse.Namespace
- Downstream modules: None

### Integration Points
- External libraries: yaml

### Code Quality Notes
- Functions without docstrings: ensure_nested, handle_schedule, handle_set_stage, load_config, main, parse_args, parse_schedule_entries, write_config.

## `scripts/merge_rollout_metrics.py`

**Purpose**: Merge captured rollout metrics into the golden stats JSON.
**Lines of code**: 132
**Dependencies**: stdlib=__future__, argparse, json, pathlib; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `_load_metrics_from_dir(scenario_dir: Path) -> dict[str, dict[str, float]] | None` — No docstring provided.
- `_collect_input_metrics(root: Path, allow_template: bool) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `DEFAULT_GOLDEN_PATH = Path('docs/samples/rollout_scenario_stats.json')`
- `METRICS_FILENAME = 'rollout_sample_metrics.json'`

### Data Flow
- Inputs: allow_template, root, scenario_dir
- Processing: Orchestrated via classes None and functions _collect_input_metrics, _load_metrics_from_dir, main, parse_args.
- Outputs: None, argparse.Namespace, dict[str, dict[str, dict[str, float]]], dict[str, dict[str, float]] | None
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Functions without docstrings: _collect_input_metrics, _load_metrics_from_dir, main, parse_args.

## `scripts/observer_ui.py`

**Purpose**: Launch the Townlet observer dashboard against a local simulation.
**Lines of code**: 62
**Dependencies**: stdlib=__future__, argparse, pathlib; external=None; internal=townlet.config, townlet.core.sim_loop, townlet_ui.dashboard
**Related modules**: townlet.config, townlet.core.sim_loop, townlet_ui.dashboard

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions main, parse_args.
- Outputs: None, argparse.Namespace
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet_ui.dashboard

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop, townlet_ui.dashboard

### Code Quality Notes
- Functions without docstrings: main, parse_args.

## `scripts/ppo_telemetry_plot.py`

**Purpose**: Quick-look plotting utility for PPO telemetry JSONL logs.
**Lines of code**: 101
**Dependencies**: stdlib=__future__, argparse, json, pathlib, typing; external=matplotlib.pyplot; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_entries(log_path: Path) -> list[dict[str, Any]]` — No docstring provided.
- `summarise(entries: list[dict[str, Any]]) -> None` — No docstring provided.
- `plot(entries: list[dict[str, Any]], show: bool, output: Path | None) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: entries, log_path, output, show
- Processing: Orchestrated via classes None and functions load_entries, main, parse_args, plot, summarise.
- Outputs: None, argparse.Namespace, list[dict[str, Any]]
- Downstream modules: None

### Integration Points
- External libraries: matplotlib.pyplot

### Code Quality Notes
- Functions without docstrings: load_entries, main, parse_args, plot, summarise.

## `scripts/profile_observation_tensor.py`

**Purpose**: Profile observation tensor dimensions for a given config.
**Lines of code**: 86
**Dependencies**: stdlib=__future__, argparse, json, pathlib, statistics; external=numpy; internal=townlet.config, townlet.observations.builder, townlet.world
**Related modules**: townlet.config, townlet.observations.builder, townlet.world

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `bootstrap_world(config_path: Path, agent_count: int) -> tuple[WorldState, ObservationBuilder]` — No docstring provided.
- `profile(world: WorldState, builder: ObservationBuilder, ticks: int) -> dict[str, object]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_count, builder, config_path, ticks, world
- Processing: Orchestrated via classes None and functions bootstrap_world, main, parse_args, profile.
- Outputs: None, argparse.Namespace, dict[str, object], tuple[WorldState, ObservationBuilder]
- Downstream modules: townlet.config, townlet.observations.builder, townlet.world

### Integration Points
- External libraries: numpy
- Internal packages: townlet.config, townlet.observations.builder, townlet.world

### Code Quality Notes
- Functions without docstrings: bootstrap_world, main, parse_args, profile.

## `scripts/promotion_drill.py`

**Purpose**: Run a scripted promotion/rollback drill and capture artefacts.
**Lines of code**: 107
**Dependencies**: stdlib=__future__, argparse, json, pathlib, typing; external=None; internal=townlet.config, townlet.console.handlers, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Classes
- None

### Functions
- `_ensure_candidate_ready(loop: SimulationLoop) -> None` — No docstring provided.
- `run_drill(config_path: Path, output_dir: Path, checkpoint: Path) -> dict[str, Any]` — No docstring provided.
- `main(argv: list[str] | None = None) -> int` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: argv, checkpoint, config_path, loop, output_dir
- Processing: Orchestrated via classes None and functions _ensure_candidate_ready, main, run_drill.
- Outputs: None, dict[str, Any], int
- Downstream modules: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Code Quality Notes
- Functions without docstrings: _ensure_candidate_ready, main, run_drill.

## `scripts/promotion_evaluate.py`

**Purpose**: Evaluate promotion readiness from anneal results payloads.
**Lines of code**: 190
**Dependencies**: stdlib=__future__, argparse, json, pathlib, typing; external=sys; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args(argv: list[str] | None = None) -> argparse.Namespace` — No docstring provided.
- `_load_payload(path: Path | None) -> Dict[str, Any]` — No docstring provided.
- `_derive_status(results: List[Dict[str, Any]]) -> str` — No docstring provided.
- `_collect_reasons(results: List[Dict[str, Any]]) -> List[str]` — No docstring provided.
- `evaluate(payload: Dict[str, Any]) -> Dict[str, Any]` — No docstring provided.
- `_print_human(summary: Dict[str, Any]) -> None` — No docstring provided.
- `main(argv: list[str] | None = None) -> int` — No docstring provided.

### Constants and Configuration
- `DEFAULT_INPUT_PATH = Path('artifacts/m7/anneal_results.json')`

### Data Flow
- Inputs: argv, path, payload, results, summary
- Processing: Orchestrated via classes None and functions _collect_reasons, _derive_status, _load_payload, _print_human, evaluate, main, parse_args.
- Outputs: Dict[str, Any], List[str], None, argparse.Namespace, int, str
- Downstream modules: None

### Integration Points
- External libraries: sys

### Code Quality Notes
- Functions without docstrings: _collect_reasons, _derive_status, _load_payload, _print_human, evaluate, main, parse_args.

## `scripts/reward_summary.py`

**Purpose**: Summarise reward breakdown telemetry for operations teams.
**Lines of code**: 323
**Dependencies**: stdlib=__future__, argparse, collections, dataclasses, json, pathlib, typing; external=sys; internal=None
**Related modules**: None

### Classes
- `ComponentStats` — defined at line 16; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - count: int = 0 (public)
    - total: float = 0.0 (public)
    - minimum: float = float('inf') (public)
    - maximum: float = float('-inf') (public)
  - Methods:
    - `update(self, value: float) -> None` — No docstring provided.
    - `mean(self) -> float` — No docstring provided.
    - `as_dict(self) -> dict[str, float | int]` — No docstring provided.
- `RewardAggregator` — defined at line 46
  - Docstring: Aggregate reward breakdowns from telemetry payloads.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `add_payload(self, payload: Mapping[str, object], source: str) -> None` — No docstring provided.
    - `summary(self) -> dict[str, object]` — No docstring provided.

### Functions
- `_is_number(value: object) -> bool` — No docstring provided.
- `iter_payloads(path: Path) -> Iterator[tuple[Mapping[str, object], str]]` — No docstring provided.
- `collect_statistics(paths: Sequence[Path]) -> RewardAggregator` — No docstring provided.
- `render_text(summary: Mapping[str, object], *, top: int, agent_filters: set[str] | None) -> str` — No docstring provided.
- `render_markdown(summary: Mapping[str, object], *, top: int, agent_filters: set[str] | None) -> str` — No docstring provided.
- `render_json(summary: Mapping[str, object]) -> str` — No docstring provided.
- `parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace` — No docstring provided.
- `main(argv: Sequence[str] | None = None) -> int` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_filters, argv, path, paths, payload, source, summary, top, value
- Processing: Orchestrated via classes ComponentStats, RewardAggregator and functions _is_number, collect_statistics, iter_payloads, main, parse_args, render_json, render_markdown, render_text.
- Outputs: Iterator[tuple[Mapping[str, object], str]], None, RewardAggregator, argparse.Namespace, bool, dict[str, float | int], dict[str, object], float, int, str
- Downstream modules: None

### Integration Points
- External libraries: sys

### Code Quality Notes
- Functions without docstrings: _is_number, collect_statistics, iter_payloads, main, parse_args, render_json, render_markdown, render_text.
- Methods without docstrings: ComponentStats.as_dict, ComponentStats.mean, ComponentStats.update, RewardAggregator.add_payload, RewardAggregator.summary.
- Uses dataclasses for structured state.

## `scripts/run_anneal_rehearsal.py`

**Purpose**: Run BC + anneal rehearsal using production manifests and capture artefacts.
**Lines of code**: 111
**Dependencies**: stdlib=__future__, argparse, json, pathlib, typing; external=importlib.util, sys; internal=scripts, townlet.config, townlet.policy.replay, townlet.policy.runner
**Related modules**: scripts, townlet.config, townlet.policy.replay, townlet.policy.runner

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `run_rehearsal(config_path: Path, manifest_path: Path, log_dir: Path) -> Dict[str, object]` — No docstring provided.
- `evaluate_summary(summary: Dict[str, object]) -> Dict[str, object]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `DEFAULT_CONFIG = Path('artifacts/m5/acceptance/config_idle_v1.yaml')`
- `DEFAULT_MANIFEST = Path('data/bc_datasets/manifests/idle_v1.json')`
- `DEFAULT_LOG_DIR = Path('artifacts/m5/acceptance/logs')`

### Data Flow
- Inputs: config_path, log_dir, manifest_path, summary
- Processing: Orchestrated via classes None and functions evaluate_summary, main, parse_args, run_rehearsal.
- Outputs: Dict[str, object], None, argparse.Namespace
- Downstream modules: scripts, townlet.config, townlet.policy.replay, townlet.policy.runner

### Integration Points
- External libraries: importlib.util, sys
- Internal packages: scripts, townlet.config, townlet.policy.replay, townlet.policy.runner

### Code Quality Notes
- Functions without docstrings: evaluate_summary, main, parse_args, run_rehearsal.

## `scripts/run_employment_smoke.py`

**Purpose**: Employment loop smoke test runner for R2 mitigation.
**Lines of code**: 81
**Dependencies**: stdlib=__future__, argparse, json, pathlib, typing; external=None; internal=townlet.config, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.core.sim_loop

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `run_smoke(config_path: Path, ticks: int, enforce: bool) -> Dict[str, Any]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: config_path, enforce, ticks
- Processing: Orchestrated via classes None and functions main, parse_args, run_smoke.
- Outputs: Dict[str, Any], None, argparse.Namespace
- Downstream modules: townlet.config, townlet.core.sim_loop

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop

### Code Quality Notes
- Functions without docstrings: main, parse_args, run_smoke.

## `scripts/run_mixed_soak.py`

**Purpose**: Run alternating replay/rollout PPO cycles for soak testing.
**Lines of code**: 110
**Dependencies**: stdlib=__future__, argparse, pathlib; external=sys; internal=townlet.config.loader, townlet.policy.replay, townlet.policy.runner
**Related modules**: townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `ROOT = Path(__file__).resolve().parents[1]`
- `SRC = ROOT / 'src'`

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions main, parse_args.
- Outputs: None, argparse.Namespace
- Downstream modules: townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Integration Points
- External libraries: sys
- Internal packages: townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Code Quality Notes
- Functions without docstrings: main, parse_args.

## `scripts/run_replay.py`

**Purpose**: Utility to replay observation/telemetry samples for analysis or tutorials.
**Lines of code**: 84
**Dependencies**: stdlib=__future__, argparse, json, pathlib, typing; external=numpy; internal=townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `render_observation(sample: Dict[str, Any]) -> None` — No docstring provided.
- `inspect_telemetry(path: Path) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: path, sample
- Processing: Orchestrated via classes None and functions inspect_telemetry, main, parse_args, render_observation.
- Outputs: None, argparse.Namespace
- Downstream modules: townlet.policy.replay

### Integration Points
- External libraries: numpy
- Internal packages: townlet.policy.replay

### Code Quality Notes
- Functions without docstrings: inspect_telemetry, main, parse_args, render_observation.

## `scripts/run_simulation.py`

**Purpose**: Run a headless Townlet simulation loop for debugging.
**Lines of code**: 31
**Dependencies**: stdlib=__future__, argparse, pathlib; external=None; internal=townlet.config.loader, townlet.core.sim_loop
**Related modules**: townlet.config.loader, townlet.core.sim_loop

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions main, parse_args.
- Outputs: None, argparse.Namespace
- Downstream modules: townlet.config.loader, townlet.core.sim_loop

### Integration Points
- External libraries: None
- Internal packages: townlet.config.loader, townlet.core.sim_loop

### Code Quality Notes
- Functions without docstrings: main, parse_args.

## `scripts/run_training.py`

**Purpose**: CLI entry point for training Townlet policies.
**Lines of code**: 466
**Dependencies**: stdlib=__future__, argparse, json, pathlib; external=None; internal=townlet.config, townlet.config.loader, townlet.policy.replay, townlet.policy.runner
**Related modules**: townlet.config, townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `_collect_ppo_overrides(args: argparse.Namespace) -> dict[str, object]` — No docstring provided.
- `_apply_ppo_overrides(config, overrides: dict[str, object]) -> None` — No docstring provided.
- `_build_dataset_config_from_args(args: argparse.Namespace, default_manifest: Path | None) -> ReplayDatasetConfig | None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: args, config, default_manifest, overrides
- Processing: Orchestrated via classes None and functions _apply_ppo_overrides, _build_dataset_config_from_args, _collect_ppo_overrides, main, parse_args.
- Outputs: None, ReplayDatasetConfig | None, argparse.Namespace, dict[str, object]
- Downstream modules: townlet.config, townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Code Quality Notes
- Functions without docstrings: _apply_ppo_overrides, _build_dataset_config_from_args, _collect_ppo_overrides, main, parse_args.

## `scripts/telemetry_check.py`

**Purpose**: Validate Townlet telemetry payloads against known schema versions.
**Lines of code**: 84
**Dependencies**: stdlib=__future__, argparse, json, pathlib, typing; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_payload(path: Path) -> Dict[str, Any]` — No docstring provided.
- `validate(payload: Dict[str, Any], schema_version: str) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `SUPPORTED_SCHEMAS = {'0.2.0': {'employment_keys': {'pending', 'pending_count', 'exits_today', 'daily_exit_cap', 'queue_limit', 'review_window'}, 'job_required_keys': {'job_id', 'on_shift', 'wallet', 'shift_state', 'attendance_ratio', 'late_ticks_today', 'wages_withheld'}}}`

### Data Flow
- Inputs: path, payload, schema_version
- Processing: Orchestrated via classes None and functions load_payload, main, parse_args, validate.
- Outputs: Dict[str, Any], None, argparse.Namespace
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Functions without docstrings: load_payload, main, parse_args, validate.

## `scripts/telemetry_summary.py`

**Purpose**: Produce summaries for PPO telemetry logs.
**Lines of code**: 338
**Dependencies**: stdlib=__future__, argparse, json, pathlib, typing; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_records(path: Path) -> list[dict[str, object]]` — No docstring provided.
- `load_baseline(path: Path | None) -> dict[str, float] | None` — No docstring provided.
- `summarise(records: Sequence[dict[str, object]], baseline: dict[str, float] | None) -> dict[str, object]` — No docstring provided.
- `_format_optional_float(value: object, precision: int = 3) -> str` — No docstring provided.
- `render_text(summary: dict[str, object]) -> str` — No docstring provided.
- `render_markdown(summary: dict[str, object]) -> str` — No docstring provided.
- `render(summary: dict[str, object], fmt: str) -> str` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: baseline, fmt, path, precision, records, summary, value
- Processing: Orchestrated via classes None and functions _format_optional_float, load_baseline, load_records, main, parse_args, render, render_markdown, render_text, summarise.
- Outputs: None, argparse.Namespace, dict[str, float] | None, dict[str, object], list[dict[str, object]], str
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Functions without docstrings: _format_optional_float, load_baseline, load_records, main, parse_args, render, render_markdown, render_text, summarise.

## `scripts/telemetry_watch.py`

**Purpose**: Tail PPO telemetry logs and alert on metric thresholds.
**Lines of code**: 381
**Dependencies**: stdlib=__future__, argparse, json, pathlib, time, typing; external=sys; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `build_parser() -> argparse.ArgumentParser` — No docstring provided.
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `parse_args_from_list(argv: list[str]) -> argparse.Namespace` — No docstring provided.
- `stream_records(path: Path, follow: bool, interval: float) -> Iterator[dict[str, float]]` — No docstring provided.
- `check_thresholds(record: dict[str, object], args: argparse.Namespace) -> None` — No docstring provided.
- `main(args: list[str] | None = None) -> None` — No docstring provided.

### Constants and Configuration
- `REQUIRED_KEYS = {'epoch', 'loss_total', 'kl_divergence', 'grad_norm', 'batch_entropy_mean', 'reward_advantage_corr', 'log_stream_offset', 'data_mode', 'queue_conflict_events', 'queue_conflict_intensity_sum', 'shared_meal_events', 'late_help_events', 'shift_takeover_events', 'chat_success_events', 'chat_failure_events', 'chat_quality_mean'}`
- `OPTIONAL_NUMERIC_KEYS = {'anneal_cycle', 'anneal_bc_accuracy', 'anneal_bc_threshold', 'anneal_loss_baseline', 'anneal_queue_baseline', 'anneal_intensity_baseline'}`
- `OPTIONAL_BOOL_KEYS = {'anneal_bc_passed', 'anneal_loss_flag', 'anneal_queue_flag', 'anneal_intensity_flag'}`
- `OPTIONAL_TEXT_KEYS = {'anneal_stage', 'anneal_dataset'}`
- `OPTIONAL_EVENT_KEYS = {'utility_outage_events', 'shower_complete_events', 'sleep_complete_events'}`

### Data Flow
- Inputs: args, argv, follow, interval, path, record
- Processing: Orchestrated via classes None and functions build_parser, check_thresholds, main, parse_args, parse_args_from_list, stream_records.
- Outputs: Iterator[dict[str, float]], None, argparse.ArgumentParser, argparse.Namespace
- Downstream modules: None

### Integration Points
- External libraries: sys

### Code Quality Notes
- Functions without docstrings: build_parser, check_thresholds, main, parse_args, parse_args_from_list, stream_records.

## `scripts/validate_affordances.py`

**Purpose**: Validate affordance manifest files for schema compliance.
**Lines of code**: 126
**Dependencies**: stdlib=__future__, argparse, pathlib, typing; external=sys; internal=townlet.config.affordance_manifest, townlet.world.preconditions
**Related modules**: townlet.config.affordance_manifest, townlet.world.preconditions

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `discover_manifests(inputs: Iterable[str]) -> List[Path]` — No docstring provided.
- `validate_manifest(path: Path) -> AffordanceManifest` — No docstring provided.
- `main() -> int` — No docstring provided.

### Constants and Configuration
- `DEFAULT_SEARCH_ROOT = Path('configs/affordances')`

### Data Flow
- Inputs: inputs, path
- Processing: Orchestrated via classes None and functions discover_manifests, main, parse_args, validate_manifest.
- Outputs: AffordanceManifest, List[Path], argparse.Namespace, int
- Downstream modules: townlet.config.affordance_manifest, townlet.world.preconditions

### Integration Points
- External libraries: sys
- Internal packages: townlet.config.affordance_manifest, townlet.world.preconditions

### Code Quality Notes
- Functions without docstrings: discover_manifests, main, parse_args, validate_manifest.

## `scripts/validate_ppo_telemetry.py`

**Purpose**: Validate PPO telemetry NDJSON logs and report baseline drift.
**Lines of code**: 248
**Dependencies**: stdlib=__future__, argparse, json, math, pathlib, typing; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `_ensure_numeric(key: str, value: object) -> None` — No docstring provided.
- `_load_records(path: Path) -> List[dict[str, object]]` — No docstring provided.
- `_validate_record(record: dict[str, object], source: Path) -> None` — No docstring provided.
- `_load_baseline(path: Path | None) -> dict[str, float] | None` — No docstring provided.
- `_relative_delta(delta: float, base_value: float) -> float | None` — No docstring provided.
- `_report_drift(records: list[dict[str, object]], baseline: dict[str, float], threshold: float | None, include_relative: bool) -> None` — No docstring provided.
- `validate_logs(paths: Iterable[Path], baseline_path: Path | None, drift_threshold: float | None, include_relative: bool) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `BASE_REQUIRED_KEYS = {'epoch', 'updates', 'transitions', 'loss_policy', 'loss_value', 'loss_entropy', 'loss_total', 'clip_fraction', 'clip_fraction_max', 'clip_triggered_minibatches', 'adv_mean', 'adv_std', 'adv_zero_std_batches', 'adv_min_std', 'grad_norm', 'kl_divergence', 'telemetry_version', 'lr', 'steps'}`
- `CONFLICT_KEYS = {'conflict.rivalry_max_mean_avg', 'conflict.rivalry_max_max_avg', 'conflict.rivalry_avoid_count_mean_avg', 'conflict.rivalry_avoid_count_max_avg'}`
- `BASELINE_KEYS = {'baseline_sample_count', 'baseline_reward_mean', 'baseline_reward_sum', 'baseline_reward_sum_mean'}`
- `REQUIRED_V1_1_NUMERIC_KEYS = {'epoch_duration_sec', 'cycle_id', 'batch_entropy_mean', 'batch_entropy_std', 'grad_norm_max', 'kl_divergence_max', 'reward_advantage_corr', 'rollout_ticks', 'log_stream_offset', 'queue_conflict_events', 'queue_conflict_intensity_sum'}`
- `REQUIRED_V1_1_STRING_KEYS = {'data_mode'}`

### Data Flow
- Inputs: base_value, baseline, baseline_path, delta, drift_threshold, include_relative, key, path, paths, record, records, source, threshold, value
- Processing: Orchestrated via classes None and functions _ensure_numeric, _load_baseline, _load_records, _relative_delta, _report_drift, _validate_record, main, parse_args, validate_logs.
- Outputs: List[dict[str, object]], None, argparse.Namespace, dict[str, float] | None, float | None
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Functions without docstrings: _ensure_numeric, _load_baseline, _load_records, _relative_delta, _report_drift, _validate_record, main, parse_args, validate_logs.

## `src/townlet/__init__.py`

**Purpose**: Townlet simulation package.
**Lines of code**: 9
**Dependencies**: stdlib=__future__; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/agents/__init__.py`

**Purpose**: Agent state models.
**Lines of code**: 19
**Dependencies**: stdlib=__future__; external=None; internal=townlet.agents.models, townlet.agents.relationship_modifiers
**Related modules**: townlet.agents.models, townlet.agents.relationship_modifiers

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.agents.models, townlet.agents.relationship_modifiers

### Integration Points
- External libraries: None
- Internal packages: townlet.agents.models, townlet.agents.relationship_modifiers

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/agents/models.py`

**Purpose**: Agent-related dataclasses and helpers.
**Lines of code**: 31
**Dependencies**: stdlib=__future__, dataclasses; external=None; internal=None
**Related modules**: None

### Classes
- `Personality` — defined at line 9; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - extroversion: float (public)
    - forgiveness: float (public)
    - ambition: float (public)
  - Methods: None declared
- `RelationshipEdge` — defined at line 16; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - other_id: str (public)
    - trust: float (public)
    - familiarity: float (public)
    - rivalry: float (public)
  - Methods: None declared
- `AgentState` — defined at line 24; decorators: dataclass
  - Docstring: Canonical agent state used across modules.
  - Attributes:
    - agent_id: str (public)
    - needs: dict[str, float] (public)
    - wallet: float (public)
    - personality: Personality (public)
    - relationships: list[RelationshipEdge] = field(default_factory=list) (public)
  - Methods: None declared

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes AgentState, Personality, RelationshipEdge and functions None.
- Outputs: None
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Uses dataclasses for structured state.

## `src/townlet/agents/relationship_modifiers.py`

**Purpose**: Relationship delta adjustment helpers respecting personality flags.
**Lines of code**: 102
**Dependencies**: stdlib=__future__, dataclasses, typing; external=None; internal=townlet.agents.models
**Related modules**: townlet.agents.models

### Classes
- `RelationshipDelta` — defined at line 23; decorators: dataclass(frozen=True)
  - Docstring: Represents trust/familiarity/rivalry deltas for a single event.
  - Attributes:
    - trust: float = 0.0 (public)
    - familiarity: float = 0.0 (public)
    - rivalry: float = 0.0 (public)
  - Methods: None declared

### Functions
- `apply_personality_modifiers(*, delta: RelationshipDelta, personality: Personality, event: RelationshipEvent, enabled: bool) -> RelationshipDelta` — Adjust ``delta`` based on personality traits when enabled.
- `_apply_forgiveness(value: float, forgiveness: float) -> float` — No docstring provided.
- `_apply_extroversion(value: float, extroversion: float) -> float` — No docstring provided.
- `_apply_ambition(value: float, ambition: float) -> float` — No docstring provided.
- `_clamp(value: float, low: float, high: float) -> float` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: ambition, delta, enabled, event, extroversion, forgiveness, high, low, personality, value
- Processing: Orchestrated via classes RelationshipDelta and functions _apply_ambition, _apply_extroversion, _apply_forgiveness, _clamp, apply_personality_modifiers.
- Outputs: RelationshipDelta, float
- Downstream modules: townlet.agents.models

### Integration Points
- External libraries: None
- Internal packages: townlet.agents.models

### Code Quality Notes
- Functions without docstrings: _apply_ambition, _apply_extroversion, _apply_forgiveness, _clamp.
- Uses dataclasses for structured state.

## `src/townlet/config/__init__.py`

**Purpose**: Config utilities for Townlet.
**Lines of code**: 97
**Dependencies**: stdlib=__future__; external=None; internal=townlet.config.loader
**Related modules**: townlet.config.loader

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.config.loader

### Integration Points
- External libraries: None
- Internal packages: townlet.config.loader

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/config/affordance_manifest.py`

**Purpose**: Utilities for validating affordance manifest files.
**Lines of code**: 316
**Dependencies**: stdlib=__future__, collections.abc, dataclasses, hashlib, logging, pathlib; external=yaml; internal=None
**Related modules**: None

### Classes
- `ManifestObject` — defined at line 17; decorators: dataclass(frozen=True)
  - Docstring: Represents an interactive object entry from the manifest.
  - Attributes:
    - object_id: str (public)
    - object_type: str (public)
    - stock: dict[str, int] (public)
    - position: tuple[int, int] | None (public)
  - Methods: None declared
- `ManifestAffordance` — defined at line 27; decorators: dataclass(frozen=True)
  - Docstring: Represents an affordance definition with preconditions and hooks.
  - Attributes:
    - affordance_id: str (public)
    - object_type: str (public)
    - duration: int (public)
    - effects: dict[str, float] (public)
    - preconditions: list[str] (public)
    - hooks: dict[str, list[str]] (public)
  - Methods: None declared
- `AffordanceManifest` — defined at line 39; decorators: dataclass(frozen=True)
  - Docstring: Normalised manifest contents and checksum metadata.
  - Attributes:
    - path: Path (public)
    - checksum: str (public)
    - objects: list[ManifestObject] (public)
    - affordances: list[ManifestAffordance] (public)
  - Methods:
    - `object_count(self) -> int` — No docstring provided.
    - `affordance_count(self) -> int` — No docstring provided.
- `AffordanceManifestError` (inherits ValueError) — defined at line 56
  - Docstring: Raised when an affordance manifest fails validation.
  - Methods: None declared

### Functions
- `load_affordance_manifest(path: Path) -> AffordanceManifest` — Load and validate an affordance manifest, returning structured entries.
- `_parse_object_entry(entry: Mapping[str, object], path: Path, index: int) -> ManifestObject` — No docstring provided.
- `_parse_affordance_entry(entry: Mapping[str, object], path: Path, index: int) -> ManifestAffordance` — No docstring provided.
- `_parse_position(value: object, *, path: Path, index: int, entry_id: str) -> tuple[int, int] | None` — No docstring provided.
- `_parse_string_list(value: object, *, field: str, path: Path, index: int, entry_id: str) -> list[str]` — No docstring provided.
- `_require_string(entry: Mapping[str, object], field: str, path: Path, index: int) -> str` — No docstring provided.
- `_ensure_unique(entry_id: str, seen: set[str], path: Path, index: int) -> None` — No docstring provided.

### Constants and Configuration
- `_ALLOWED_HOOK_KEYS = {'before', 'after', 'fail'}`

### Data Flow
- Inputs: entry, entry_id, field, index, path, seen, value
- Processing: Orchestrated via classes AffordanceManifest, AffordanceManifestError, ManifestAffordance, ManifestObject and functions _ensure_unique, _parse_affordance_entry, _parse_object_entry, _parse_position, _parse_string_list, _require_string, load_affordance_manifest.
- Outputs: AffordanceManifest, ManifestAffordance, ManifestObject, None, int, list[str], str, tuple[int, int] | None
- Downstream modules: None

### Integration Points
- External libraries: yaml

### Code Quality Notes
- Functions without docstrings: _ensure_unique, _parse_affordance_entry, _parse_object_entry, _parse_position, _parse_string_list, _require_string.
- Methods without docstrings: AffordanceManifest.affordance_count, AffordanceManifest.object_count.
- Uses dataclasses for structured state.
- Logging statements present; ensure log levels are appropriate.

## `src/townlet/config/loader.py`

**Purpose**: Configuration loader and validation layer.
**Lines of code**: 793
**Dependencies**: stdlib=__future__, collections.abc, enum, pathlib, typing; external=importlib, pydantic, re, yaml; internal=townlet.snapshots
**Related modules**: townlet.snapshots

### Classes
- `StageFlags` (inherits BaseModel) — defined at line 30
  - Docstring: No class docstring provided.
  - Attributes:
    - relationships: RelationshipStage = 'OFF' (public)
    - social_rewards: SocialRewardStage = 'OFF' (public)
  - Methods: None declared
- `SystemFlags` (inherits BaseModel) — defined at line 35
  - Docstring: No class docstring provided.
  - Attributes:
    - lifecycle: LifecycleToggle = 'on' (public)
    - observations: ObservationVariant = 'hybrid' (public)
  - Methods: None declared
- `TrainingFlags` (inherits BaseModel) — defined at line 40
  - Docstring: No class docstring provided.
  - Attributes:
    - curiosity: CuriosityToggle = 'phase_A' (public)
  - Methods: None declared
- `PolicyRuntimeConfig` (inherits BaseModel) — defined at line 44
  - Docstring: No class docstring provided.
  - Attributes:
    - option_commit_ticks: int = Field(15, ge=0, le=100000) (public)
  - Methods: None declared
- `ConsoleFlags` (inherits BaseModel) — defined at line 48
  - Docstring: No class docstring provided.
  - Attributes:
    - mode: ConsoleMode = 'viewer' (public)
  - Methods: None declared
- `FeatureFlags` (inherits BaseModel) — defined at line 52
  - Docstring: No class docstring provided.
  - Attributes:
    - stages: StageFlags (public)
    - systems: SystemFlags (public)
    - training: TrainingFlags (public)
    - console: ConsoleFlags (public)
    - relationship_modifiers: bool = False (public)
  - Methods: None declared
- `NeedsWeights` (inherits BaseModel) — defined at line 60
  - Docstring: No class docstring provided.
  - Attributes:
    - hunger: float = Field(1.0, ge=0.5, le=2.0) (public)
    - hygiene: float = Field(0.6, ge=0.2, le=1.0) (public)
    - energy: float = Field(0.8, ge=0.4, le=1.5) (public)
  - Methods: None declared
- `SocialRewardWeights` (inherits BaseModel) — defined at line 66
  - Docstring: No class docstring provided.
  - Attributes:
    - C1_chat_base: float = Field(0.01, ge=0.0, le=0.05) (public)
    - C1_coeff_trust: float = Field(0.3, ge=0.0, le=1.0) (public)
    - C1_coeff_fam: float = Field(0.2, ge=0.0, le=1.0) (public)
    - C2_avoid_conflict: float = Field(0.005, ge=0.0, le=0.02) (public)
  - Methods: None declared
- `RewardClips` (inherits BaseModel) — defined at line 73
  - Docstring: No class docstring provided.
  - Attributes:
    - clip_per_tick: float = Field(0.2, ge=0.01, le=1.0) (public)
    - clip_per_episode: float = Field(50, ge=1, le=200) (public)
    - no_positive_within_death_ticks: int = Field(10, ge=0, le=200) (public)
  - Methods: None declared
- `RewardsConfig` (inherits BaseModel) — defined at line 79
  - Docstring: No class docstring provided.
  - Attributes:
    - needs_weights: NeedsWeights (public)
    - decay_rates: dict[str, float] = Field(default_factory=lambda: {'hunger': 0.01, 'hygiene': 0.005, 'energy': 0.008}) (public)
    - punctuality_bonus: float = Field(0.05, ge=0.0, le=0.1) (public)
    - wage_rate: float = Field(0.01, ge=0.0, le=0.05) (public)
    - survival_tick: float = Field(0.002, ge=0.0, le=0.01) (public)
    - faint_penalty: float = Field(-1.0, ge=-5.0, le=0.0) (public)
    - eviction_penalty: float = Field(-2.0, ge=-5.0, le=0.0) (public)
    - social: SocialRewardWeights = SocialRewardWeights() (public)
    - clip: RewardClips = RewardClips() (public)
  - Methods:
    - `_sanity_check_punctuality(self) -> 'RewardsConfig'` — No docstring provided.
- `ShapingConfig` (inherits BaseModel) — defined at line 105
  - Docstring: No class docstring provided.
  - Attributes:
    - use_potential: bool = True (public)
  - Methods: None declared
- `CuriosityConfig` (inherits BaseModel) — defined at line 109
  - Docstring: No class docstring provided.
  - Attributes:
    - phase_A_weight: float = Field(0.02, ge=0.0, le=0.1) (public)
    - decay_by_milestone: Literal['M2', 'never'] = 'M2' (public)
  - Methods: None declared
- `QueueFairnessConfig` (inherits BaseModel) — defined at line 114
  - Docstring: Queue fairness tuning parameters (see REQUIREMENTS#5).
  - Attributes:
    - cooldown_ticks: int = Field(60, ge=0, le=600) (public)
    - ghost_step_after: int = Field(3, ge=0, le=100) (public)
    - age_priority_weight: float = Field(0.1, ge=0.0, le=1.0) (public)
  - Methods: None declared
- `RivalryConfig` (inherits BaseModel) — defined at line 122
  - Docstring: Conflict/rivalry tuning knobs (see REQUIREMENTS#5).
  - Attributes:
    - increment_per_conflict: float = Field(0.15, ge=0.0, le=1.0) (public)
    - decay_per_tick: float = Field(0.005, ge=0.0, le=1.0) (public)
    - min_value: float = Field(0.0, ge=0.0, le=1.0) (public)
    - max_value: float = Field(1.0, ge=0.0, le=1.0) (public)
    - avoid_threshold: float = Field(0.7, ge=0.0, le=1.0) (public)
    - eviction_threshold: float = Field(0.05, ge=0.0, le=1.0) (public)
    - max_edges: int = Field(6, ge=1, le=32) (public)
    - ghost_step_boost: float = Field(1.5, ge=0.0, le=5.0) (public)
    - handover_boost: float = Field(0.4, ge=0.0, le=5.0) (public)
    - queue_length_boost: float = Field(0.25, ge=0.0, le=2.0) (public)
  - Methods:
    - `_validate_ranges(self) -> 'RivalryConfig'` — No docstring provided.
- `ConflictConfig` (inherits BaseModel) — defined at line 147
  - Docstring: No class docstring provided.
  - Attributes:
    - rivalry: RivalryConfig = RivalryConfig() (public)
  - Methods: None declared
- `PPOConfig` (inherits BaseModel) — defined at line 151
  - Docstring: Config for PPO training hyperparameters.
  - Attributes:
    - learning_rate: float = Field(0.0003, gt=0.0) (public)
    - clip_param: float = Field(0.2, ge=0.0, le=1.0) (public)
    - value_loss_coef: float = Field(0.5, ge=0.0) (public)
    - entropy_coef: float = Field(0.01, ge=0.0) (public)
    - num_epochs: int = Field(4, ge=1, le=64) (public)
    - mini_batch_size: int = Field(32, ge=1) (public)
    - gae_lambda: float = Field(0.95, ge=0.0, le=1.0) (public)
    - gamma: float = Field(0.99, ge=0.0, le=1.0) (public)
    - max_grad_norm: float = Field(0.5, ge=0.0) (public)
    - value_clip: float = Field(0.2, ge=0.0, le=1.0) (public)
    - advantage_normalization: bool = True (public)
    - num_mini_batches: int = Field(4, ge=1, le=1024) (public)
  - Methods: None declared
- `EmbeddingAllocatorConfig` (inherits BaseModel) — defined at line 168
  - Docstring: Embedding slot reuse guardrails (see REQUIREMENTS#3).
  - Attributes:
    - cooldown_ticks: int = Field(2000, ge=0, le=10000) (public)
    - reuse_warning_threshold: float = Field(0.05, ge=0.0, le=0.5) (public)
    - log_forced_reuse: bool = True (public)
    - max_slots: int = Field(64, ge=1, le=256) (public)
  - Methods: None declared
- `HybridObservationConfig` (inherits BaseModel) — defined at line 177
  - Docstring: No class docstring provided.
  - Attributes:
    - local_window: int = Field(11, ge=3) (public)
    - include_targets: bool = False (public)
    - time_ticks_per_day: int = Field(1440, ge=1) (public)
  - Methods:
    - `_validate_window(self) -> 'HybridObservationConfig'` — No docstring provided.
- `SocialSnippetConfig` (inherits BaseModel) — defined at line 189
  - Docstring: No class docstring provided.
  - Attributes:
    - top_friends: int = Field(2, ge=0, le=8) (public)
    - top_rivals: int = Field(2, ge=0, le=8) (public)
    - embed_dim: int = Field(8, ge=1, le=32) (public)
    - include_aggregates: bool = True (public)
  - Methods:
    - `_validate_totals(self) -> 'SocialSnippetConfig'` — No docstring provided.
- `ObservationsConfig` (inherits BaseModel) — defined at line 204
  - Docstring: No class docstring provided.
  - Attributes:
    - hybrid: HybridObservationConfig = HybridObservationConfig() (public)
    - social_snippet: SocialSnippetConfig = SocialSnippetConfig() (public)
  - Methods: None declared
- `StarvationCanaryConfig` (inherits BaseModel) — defined at line 209
  - Docstring: No class docstring provided.
  - Attributes:
    - window_ticks: int = Field(1000, ge=1, le=100000) (public)
    - max_incidents: int = Field(0, ge=0, le=10000) (public)
    - hunger_threshold: float = Field(0.05, ge=0.0, le=1.0) (public)
    - min_duration_ticks: int = Field(30, ge=1, le=10000) (public)
  - Methods: None declared
- `RewardVarianceCanaryConfig` (inherits BaseModel) — defined at line 216
  - Docstring: No class docstring provided.
  - Attributes:
    - window_ticks: int = Field(1000, ge=1, le=100000) (public)
    - max_variance: float = Field(0.25, ge=0.0) (public)
    - min_samples: int = Field(20, ge=1, le=100000) (public)
  - Methods: None declared
- `OptionThrashCanaryConfig` (inherits BaseModel) — defined at line 222
  - Docstring: No class docstring provided.
  - Attributes:
    - window_ticks: int = Field(600, ge=1, le=100000) (public)
    - max_switch_rate: float = Field(0.25, ge=0.0, le=10.0) (public)
    - min_samples: int = Field(10, ge=1, le=100000) (public)
  - Methods: None declared
- `PromotionGateConfig` (inherits BaseModel) — defined at line 228
  - Docstring: No class docstring provided.
  - Attributes:
    - required_passes: int = Field(2, ge=1, le=10) (public)
    - window_ticks: int = Field(1000, ge=1, le=100000) (public)
    - allowed_alerts: tuple[str, ...] = () (public)
    - model_config = ConfigDict(extra='forbid') (public)
  - Methods:
    - `_coerce_allowed(cls, value: object) -> object` — No docstring provided.
    - `_normalise(self) -> 'PromotionGateConfig'` — No docstring provided.
- `LifecycleConfig` (inherits BaseModel) — defined at line 251
  - Docstring: No class docstring provided.
  - Attributes:
    - respawn_delay_ticks: int = Field(0, ge=0, le=100000) (public)
  - Methods: None declared
- `StabilityConfig` (inherits BaseModel) — defined at line 255
  - Docstring: No class docstring provided.
  - Attributes:
    - affordance_fail_threshold: int = Field(5, ge=0, le=100) (public)
    - lateness_threshold: int = Field(3, ge=0, le=100) (public)
    - starvation: StarvationCanaryConfig = StarvationCanaryConfig() (public)
    - reward_variance: RewardVarianceCanaryConfig = RewardVarianceCanaryConfig() (public)
    - option_thrash: OptionThrashCanaryConfig = OptionThrashCanaryConfig() (public)
    - promotion: PromotionGateConfig = PromotionGateConfig() (public)
  - Methods:
    - `as_dict(self) -> dict[str, object]` — No docstring provided.
- `IntRange` (inherits BaseModel) — defined at line 274
  - Docstring: No class docstring provided.
  - Attributes:
    - min: int = Field(ge=0) (public)
    - max: int = Field(ge=0) (public)
    - model_config = ConfigDict(extra='forbid') (public)
  - Methods:
    - `_coerce(cls, value: object) -> dict[str, int]` — No docstring provided.
    - `_validate_bounds(self) -> 'IntRange'` — No docstring provided.
- `FloatRange` (inherits BaseModel) — defined at line 303
  - Docstring: No class docstring provided.
  - Attributes:
    - min: float (public)
    - max: float (public)
    - model_config = ConfigDict(extra='forbid') (public)
  - Methods:
    - `_coerce(cls, value: object) -> dict[str, float]` — No docstring provided.
    - `_validate_bounds(self) -> 'FloatRange'` — No docstring provided.
- `PerturbationKind` (inherits str, Enum) — defined at line 332
  - Docstring: No class docstring provided.
  - Attributes:
    - PRICE_SPIKE = 'price_spike' (public)
    - BLACKOUT = 'blackout' (public)
    - OUTAGE = 'outage' (public)
    - ARRANGED_MEET = 'arranged_meet' (public)
  - Methods: None declared
- `BasePerturbationEventConfig` (inherits BaseModel) — defined at line 339
  - Docstring: No class docstring provided.
  - Attributes:
    - kind: PerturbationKind (public)
    - probability_per_day: float = Field(0.0, ge=0.0, alias='prob_per_day') (public)
    - cooldown_ticks: int = Field(0, ge=0) (public)
    - duration: IntRange = Field(default_factory=lambda: IntRange(min=0, max=0)) (public)
    - model_config = ConfigDict(extra='forbid', populate_by_name=True) (public)
  - Methods:
    - `_normalise_duration(cls, values: dict[str, object]) -> dict[str, object]` — No docstring provided.
- `PriceSpikeEventConfig` (inherits BasePerturbationEventConfig) — defined at line 354
  - Docstring: No class docstring provided.
  - Attributes:
    - kind: Literal[PerturbationKind.PRICE_SPIKE] = PerturbationKind.PRICE_SPIKE (public)
    - magnitude: FloatRange = Field(default_factory=lambda: FloatRange(min=1.0, max=1.0)) (public)
    - targets: list[str] = Field(default_factory=list) (public)
  - Methods:
    - `_normalise_magnitude(cls, values: dict[str, object]) -> dict[str, object]` — No docstring provided.
- `BlackoutEventConfig` (inherits BasePerturbationEventConfig) — defined at line 366
  - Docstring: No class docstring provided.
  - Attributes:
    - kind: Literal[PerturbationKind.BLACKOUT] = PerturbationKind.BLACKOUT (public)
    - utility: Literal['power'] = 'power' (public)
  - Methods: None declared
- `OutageEventConfig` (inherits BasePerturbationEventConfig) — defined at line 371
  - Docstring: No class docstring provided.
  - Attributes:
    - kind: Literal[PerturbationKind.OUTAGE] = PerturbationKind.OUTAGE (public)
    - utility: Literal['water'] = 'water' (public)
  - Methods: None declared
- `ArrangedMeetEventConfig` (inherits BasePerturbationEventConfig) — defined at line 376
  - Docstring: No class docstring provided.
  - Attributes:
    - kind: Literal[PerturbationKind.ARRANGED_MEET] = PerturbationKind.ARRANGED_MEET (public)
    - target: str = Field(default='top_rivals') (public)
    - location: str = Field(default='cafe') (public)
    - max_participants: int = Field(2, ge=2) (public)
  - Methods: None declared
- `PerturbationSchedulerConfig` (inherits BaseModel) — defined at line 389
  - Docstring: No class docstring provided.
  - Attributes:
    - max_concurrent_events: int = Field(1, ge=1) (public)
    - global_cooldown_ticks: int = Field(0, ge=0) (public)
    - per_agent_cooldown_ticks: int = Field(0, ge=0) (public)
    - grace_window_ticks: int = Field(60, ge=0) (public)
    - window_ticks: int = Field(1440, ge=1) (public)
    - max_events_per_window: int = Field(1, ge=0) (public)
    - events: dict[str, PerturbationEventConfig] = Field(default_factory=dict) (public)
    - model_config = ConfigDict(extra='allow', populate_by_name=True) (public)
  - Methods:
    - `event_list(self) -> list[PerturbationEventConfig]` — No docstring provided.
- `AffordanceConfig` (inherits BaseModel) — defined at line 405
  - Docstring: No class docstring provided.
  - Attributes:
    - affordances_file: str = Field('configs/affordances/core.yaml') (public)
  - Methods: None declared
- `EmploymentConfig` (inherits BaseModel) — defined at line 409
  - Docstring: No class docstring provided.
  - Attributes:
    - grace_ticks: int = Field(5, ge=0, le=120) (public)
    - absent_cutoff: int = Field(30, ge=0, le=600) (public)
    - absence_slack: int = Field(20, ge=0, le=600) (public)
    - late_tick_penalty: float = Field(0.005, ge=0.0, le=1.0) (public)
    - absence_penalty: float = Field(0.2, ge=0.0, le=5.0) (public)
    - max_absent_shifts: int = Field(3, ge=0, le=20) (public)
    - attendance_window: int = Field(3, ge=1, le=14) (public)
    - daily_exit_cap: int = Field(2, ge=0, le=50) (public)
    - exit_queue_limit: int = Field(8, ge=0, le=100) (public)
    - exit_review_window: int = Field(1440, ge=1, le=100000) (public)
    - enforce_job_loop: bool = False (public)
  - Methods: None declared
- `BehaviorConfig` (inherits BaseModel) — defined at line 423
  - Docstring: No class docstring provided.
  - Attributes:
    - hunger_threshold: float = Field(0.4, ge=0.0, le=1.0) (public)
    - hygiene_threshold: float = Field(0.4, ge=0.0, le=1.0) (public)
    - energy_threshold: float = Field(0.4, ge=0.0, le=1.0) (public)
    - job_arrival_buffer: int = Field(20, ge=0) (public)
  - Methods: None declared
- `SocialRewardScheduleEntry` (inherits BaseModel) — defined at line 430
  - Docstring: No class docstring provided.
  - Attributes:
    - cycle: int = Field(0, ge=0) (public)
    - stage: SocialRewardStage (public)
  - Methods: None declared
- `BCTrainingSettings` (inherits BaseModel) — defined at line 435
  - Docstring: No class docstring provided.
  - Attributes:
    - manifest: Path | None (public)
    - learning_rate: float = Field(0.001, gt=0.0) (public)
    - batch_size: int = Field(64, ge=1) (public)
    - epochs: int = Field(10, ge=1) (public)
    - weight_decay: float = Field(0.0, ge=0.0) (public)
    - device: str = 'cpu' (public)
  - Methods: None declared
- `AnnealStage` (inherits BaseModel) — defined at line 444
  - Docstring: No class docstring provided.
  - Attributes:
    - cycle: int = Field(0, ge=0) (public)
    - mode: Literal['bc', 'ppo'] = 'ppo' (public)
    - epochs: int = Field(1, ge=1) (public)
    - bc_weight: float = Field(1.0, ge=0.0, le=1.0) (public)
  - Methods: None declared
- `NarrationThrottleConfig` (inherits BaseModel) — defined at line 451
  - Docstring: No class docstring provided.
  - Attributes:
    - global_cooldown_ticks: int = Field(30, ge=0, le=10000) (public)
    - category_cooldown_ticks: dict[str, int] = Field(default_factory=dict) (public)
    - dedupe_window_ticks: int = Field(20, ge=0, le=10000) (public)
    - global_window_ticks: int = Field(600, ge=1, le=10000) (public)
    - global_window_limit: int = Field(10, ge=1, le=1000) (public)
    - priority_categories: list[str] = Field(default_factory=list) (public)
  - Methods:
    - `get_category_cooldown(self, category: str) -> int` — No docstring provided.
- `TelemetryRetryPolicy` (inherits BaseModel) — defined at line 463
  - Docstring: No class docstring provided.
  - Attributes:
    - max_attempts: int = Field(default=3, ge=0, le=10) (public)
    - backoff_seconds: float = Field(default=0.5, ge=0.0, le=30.0) (public)
  - Methods: None declared
- `TelemetryBufferConfig` (inherits BaseModel) — defined at line 468
  - Docstring: No class docstring provided.
  - Attributes:
    - max_batch_size: int = Field(default=32, ge=1, le=500) (public)
    - max_buffer_bytes: int = Field(default=256000, ge=1024, le=16777216) (public)
    - flush_interval_ticks: int = Field(default=1, ge=1, le=10000) (public)
  - Methods: None declared
- `TelemetryTransportConfig` (inherits BaseModel) — defined at line 474
  - Docstring: No class docstring provided.
  - Attributes:
    - type: TelemetryTransportType = 'stdout' (public)
    - endpoint: str | None (public)
    - file_path: Path | None (public)
    - connect_timeout_seconds: float = Field(default=5.0, ge=0.0, le=60.0) (public)
    - send_timeout_seconds: float = Field(default=1.0, ge=0.0, le=60.0) (public)
    - retry: TelemetryRetryPolicy = TelemetryRetryPolicy() (public)
    - buffer: TelemetryBufferConfig = TelemetryBufferConfig() (public)
  - Methods:
    - `_validate_transport(self) -> 'TelemetryTransportConfig'` — No docstring provided.
- `TelemetryConfig` (inherits BaseModel) — defined at line 512
  - Docstring: No class docstring provided.
  - Attributes:
    - narration: NarrationThrottleConfig = NarrationThrottleConfig() (public)
    - transport: TelemetryTransportConfig = TelemetryTransportConfig() (public)
  - Methods: None declared
- `SnapshotStorageConfig` (inherits BaseModel) — defined at line 517
  - Docstring: No class docstring provided.
  - Attributes:
    - root: Path = Field(default=Path('snapshots')) (public)
  - Methods:
    - `_validate_root(self) -> 'SnapshotStorageConfig'` — No docstring provided.
- `SnapshotAutosaveConfig` (inherits BaseModel) — defined at line 527
  - Docstring: No class docstring provided.
  - Attributes:
    - cadence_ticks: int | None = Field(default=None, ge=1) (public)
    - retain: int = Field(default=3, ge=1, le=1000) (public)
  - Methods:
    - `_validate_cadence(self) -> 'SnapshotAutosaveConfig'` — No docstring provided.
- `SnapshotIdentityConfig` (inherits BaseModel) — defined at line 540
  - Docstring: No class docstring provided.
  - Attributes:
    - policy_hash: str | None (public)
    - policy_artifact: Path | None (public)
    - observation_variant: ObservationVariant | Literal['infer'] = 'infer' (public)
    - anneal_ratio: float | None = Field(default=None, ge=0.0, le=1.0) (public)
    - _HEX40 = re.compile('^[0-9a-fA-F]{40}$') (private)
    - _HEX64 = re.compile('^[0-9a-fA-F]{64}$') (private)
    - _BASE64 = re.compile('^[A-Za-z0-9+/=]{32,88}$') (private)
  - Methods:
    - `_validate_policy_hash(self) -> 'SnapshotIdentityConfig'` — No docstring provided.
    - `_validate_variant(self) -> 'SnapshotIdentityConfig'` — No docstring provided.
- `SnapshotMigrationsConfig` (inherits BaseModel) — defined at line 581
  - Docstring: No class docstring provided.
  - Attributes:
    - handlers: dict[str, str] = Field(default_factory=dict) (public)
    - auto_apply: bool = False (public)
    - allow_minor: bool = False (public)
  - Methods:
    - `_validate_handlers(self) -> 'SnapshotMigrationsConfig'` — No docstring provided.
- `SnapshotGuardrailsConfig` (inherits BaseModel) — defined at line 596
  - Docstring: No class docstring provided.
  - Attributes:
    - require_exact_config: bool = True (public)
    - allow_downgrade: bool = False (public)
  - Methods: None declared
- `SnapshotConfig` (inherits BaseModel) — defined at line 601
  - Docstring: No class docstring provided.
  - Attributes:
    - storage: SnapshotStorageConfig = SnapshotStorageConfig() (public)
    - autosave: SnapshotAutosaveConfig = SnapshotAutosaveConfig() (public)
    - identity: SnapshotIdentityConfig = SnapshotIdentityConfig() (public)
    - migrations: SnapshotMigrationsConfig = SnapshotMigrationsConfig() (public)
    - guardrails: SnapshotGuardrailsConfig = SnapshotGuardrailsConfig() (public)
  - Methods:
    - `_validate_observation_override(self) -> 'SnapshotConfig'` — No docstring provided.
- `TrainingConfig` (inherits BaseModel) — defined at line 621
  - Docstring: No class docstring provided.
  - Attributes:
    - source: TrainingSource = 'replay' (public)
    - rollout_ticks: int = Field(100, ge=0) (public)
    - rollout_auto_seed_agents: bool = False (public)
    - replay_manifest: Path | None (public)
    - social_reward_stage_override: SocialRewardStage | None (public)
    - social_reward_schedule: list['SocialRewardScheduleEntry'] = Field(default_factory=list) (public)
    - bc: BCTrainingSettings = BCTrainingSettings() (public)
    - anneal_schedule: list[AnnealStage] = Field(default_factory=list) (public)
    - anneal_accuracy_threshold: float = Field(0.9, ge=0.0, le=1.0) (public)
    - anneal_enable_policy_blend: bool = False (public)
  - Methods: None declared
- `JobSpec` (inherits BaseModel) — defined at line 634
  - Docstring: No class docstring provided.
  - Attributes:
    - start_tick: int = 0 (public)
    - end_tick: int = 0 (public)
    - wage_rate: float = 0.0 (public)
    - lateness_penalty: float = 0.0 (public)
    - location: tuple[int, int] | None (public)
  - Methods: None declared
- `SimulationConfig` (inherits BaseModel) — defined at line 642
  - Docstring: No class docstring provided.
  - Attributes:
    - config_id: str (public)
    - features: FeatureFlags (public)
    - rewards: RewardsConfig (public)
    - economy: dict[str, float] = Field(default_factory=lambda: {'meal_cost': 0.4, 'cook_energy_cost': 0.05, 'cook_hygiene_cost': 0.02, 'wage_income': 0.02, 'ingredients_cost': 0.15, 'stove_stock_replenish': 2}) (public)
    - jobs: dict[str, JobSpec] = Field(default_factory=lambda: {'grocer': JobSpec(start_tick=180, end_tick=360, wage_rate=0.02, lateness_penalty=0.1, location=(0, 0)), 'barista': JobSpec(start_tick=400, end_tick=560, wage_rate=0.025, lateness_penalty=0.12, location=(1, 0))}) (public)
    - shaping: ShapingConfig | None (public)
    - curiosity: CuriosityConfig | None (public)
    - queue_fairness: QueueFairnessConfig = QueueFairnessConfig() (public)
    - conflict: ConflictConfig = ConflictConfig() (public)
    - ppo: PPOConfig | None (public)
    - training: TrainingConfig = TrainingConfig() (public)
    - embedding_allocator: EmbeddingAllocatorConfig = EmbeddingAllocatorConfig() (public)
    - observations_config: ObservationsConfig = ObservationsConfig() (public)
    - affordances: AffordanceConfig = AffordanceConfig() (public)
    - stability: StabilityConfig = StabilityConfig() (public)
    - behavior: BehaviorConfig = BehaviorConfig() (public)
    - policy_runtime: PolicyRuntimeConfig = PolicyRuntimeConfig() (public)
    - employment: EmploymentConfig = EmploymentConfig() (public)
    - telemetry: TelemetryConfig = TelemetryConfig() (public)
    - snapshot: SnapshotConfig = SnapshotConfig() (public)
    - perturbations: PerturbationSchedulerConfig = PerturbationSchedulerConfig() (public)
    - lifecycle: LifecycleConfig = LifecycleConfig() (public)
    - model_config = ConfigDict(extra='allow') (public)
  - Methods:
    - `_validate_observation_variant(self) -> 'SimulationConfig'` — No docstring provided.
    - `observation_variant(self) -> ObservationVariant` — No docstring provided.
    - `require_observation_variant(self, expected: ObservationVariant) -> None` — No docstring provided.
    - `snapshot_root(self) -> Path` — No docstring provided.
    - `build_snapshot_identity(self, *, policy_hash: str | None, runtime_observation_variant: ObservationVariant | None, runtime_anneal_ratio: float | None) -> dict[str, object]` — No docstring provided.
    - `register_snapshot_migrations(self) -> None` — No docstring provided.

### Functions
- `load_config(path: Path) -> SimulationConfig` — Load and validate a Townlet YAML configuration file.

### Constants and Configuration
- None

### Data Flow
- Inputs: category, expected, path, policy_hash, runtime_anneal_ratio, runtime_observation_variant, value, values
- Processing: Orchestrated via classes AffordanceConfig, AnnealStage, ArrangedMeetEventConfig, BCTrainingSettings, BasePerturbationEventConfig, BehaviorConfig, BlackoutEventConfig, ConflictConfig, ConsoleFlags, CuriosityConfig, EmbeddingAllocatorConfig, EmploymentConfig, FeatureFlags, FloatRange, HybridObservationConfig, IntRange, JobSpec, LifecycleConfig, NarrationThrottleConfig, NeedsWeights, ObservationsConfig, OptionThrashCanaryConfig, OutageEventConfig, PPOConfig, PerturbationKind, PerturbationSchedulerConfig, PolicyRuntimeConfig, PriceSpikeEventConfig, PromotionGateConfig, QueueFairnessConfig, RewardClips, RewardVarianceCanaryConfig, RewardsConfig, RivalryConfig, ShapingConfig, SimulationConfig, SnapshotAutosaveConfig, SnapshotConfig, SnapshotGuardrailsConfig, SnapshotIdentityConfig, SnapshotMigrationsConfig, SnapshotStorageConfig, SocialRewardScheduleEntry, SocialRewardWeights, SocialSnippetConfig, StabilityConfig, StageFlags, StarvationCanaryConfig, SystemFlags, TelemetryBufferConfig, TelemetryConfig, TelemetryRetryPolicy, TelemetryTransportConfig, TrainingConfig, TrainingFlags and functions load_config.
- Outputs: 'FloatRange', 'HybridObservationConfig', 'IntRange', 'PromotionGateConfig', 'RewardsConfig', 'RivalryConfig', 'SimulationConfig', 'SnapshotAutosaveConfig', 'SnapshotConfig', 'SnapshotIdentityConfig', 'SnapshotMigrationsConfig', 'SnapshotStorageConfig', 'SocialSnippetConfig', 'TelemetryTransportConfig', None, ObservationVariant, Path, SimulationConfig, dict[str, float], dict[str, int], dict[str, object], int, list[PerturbationEventConfig], object
- Downstream modules: townlet.snapshots

### Integration Points
- External libraries: importlib, pydantic, re, yaml
- Internal packages: townlet.snapshots

### Code Quality Notes
- Methods without docstrings: BasePerturbationEventConfig._normalise_duration, FloatRange._coerce, FloatRange._validate_bounds, HybridObservationConfig._validate_window, IntRange._coerce, IntRange._validate_bounds, NarrationThrottleConfig.get_category_cooldown, PerturbationSchedulerConfig.event_list, PriceSpikeEventConfig._normalise_magnitude, PromotionGateConfig._coerce_allowed, PromotionGateConfig._normalise, RewardsConfig._sanity_check_punctuality, RivalryConfig._validate_ranges, SimulationConfig._validate_observation_variant, SimulationConfig.build_snapshot_identity, SimulationConfig.observation_variant, SimulationConfig.register_snapshot_migrations, SimulationConfig.require_observation_variant, SimulationConfig.snapshot_root, SnapshotAutosaveConfig._validate_cadence, SnapshotConfig._validate_observation_override, SnapshotIdentityConfig._validate_policy_hash, SnapshotIdentityConfig._validate_variant, SnapshotMigrationsConfig._validate_handlers, SnapshotStorageConfig._validate_root, SocialSnippetConfig._validate_totals, StabilityConfig.as_dict, TelemetryTransportConfig._validate_transport.

## `src/townlet/console/__init__.py`

**Purpose**: Console command handling exports.
**Lines of code**: 15
**Dependencies**: stdlib=__future__, typing; external=importlib; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `__getattr__(name: str) -> Any` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: name
- Processing: Orchestrated via classes None and functions __getattr__.
- Outputs: Any
- Downstream modules: None

### Integration Points
- External libraries: importlib

### Code Quality Notes
- Functions without docstrings: __getattr__.

## `src/townlet/console/command.py`

**Purpose**: Console command envelope and result helpers.
**Lines of code**: 201
**Dependencies**: stdlib=__future__, dataclasses, typing; external=None; internal=None
**Related modules**: None

### Classes
- `ConsoleCommandError` (inherits RuntimeError) — defined at line 10
  - Docstring: Raised by handlers when a command should return an error response.
  - Methods:
    - `__init__(self, code: str, message: str, *, details: Mapping[str, Any] | None = None) -> None` — No docstring provided.
- `ConsoleCommandEnvelope` — defined at line 21; decorators: dataclass(frozen=True)
  - Docstring: Normalised representation of an incoming console command payload.
  - Attributes:
    - name: str (public)
    - args: list[Any] = field(default_factory=list) (public)
    - kwargs: dict[str, Any] = field(default_factory=dict) (public)
    - cmd_id: str | None (public)
    - issuer: str | None (public)
    - mode: str = 'viewer' (public)
    - timestamp_ms: int | None (public)
    - metadata: dict[str, Any] = field(default_factory=dict) (public)
    - raw: Mapping[str, Any] | None (public)
  - Methods:
    - `from_payload(cls, payload: object) -> 'ConsoleCommandEnvelope'` — Parse a payload emitted by the console transport.
- `ConsoleCommandResult` — defined at line 117; decorators: dataclass
  - Docstring: Standard response emitted after processing a console command.
  - Attributes:
    - name: str (public)
    - status: str (public)
    - result: dict[str, Any] | None (public)
    - error: dict[str, Any] | None (public)
    - cmd_id: str | None (public)
    - issuer: str | None (public)
    - tick: int | None (public)
    - latency_ms: int | None (public)
  - Methods:
    - `ok(cls, envelope: ConsoleCommandEnvelope, payload: Mapping[str, Any] | None = None, *, tick: int | None = None, latency_ms: int | None = None) -> 'ConsoleCommandResult'` — No docstring provided.
    - `from_error(cls, envelope: ConsoleCommandEnvelope, code: str, message: str, *, details: Mapping[str, Any] | None = None, tick: int | None = None, latency_ms: int | None = None) -> 'ConsoleCommandResult'` — No docstring provided.
    - `clone(self) -> 'ConsoleCommandResult'` — No docstring provided.
    - `to_dict(self) -> dict[str, Any]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- `_VALID_MODES = {'viewer', 'admin'}`

### Data Flow
- Inputs: code, details, envelope, latency_ms, message, payload, tick
- Processing: Orchestrated via classes ConsoleCommandEnvelope, ConsoleCommandError, ConsoleCommandResult and functions None.
- Outputs: 'ConsoleCommandEnvelope', 'ConsoleCommandResult', None, dict[str, Any]
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Methods without docstrings: ConsoleCommandResult.clone, ConsoleCommandResult.from_error, ConsoleCommandResult.ok, ConsoleCommandResult.to_dict.
- Uses dataclasses for structured state.

## `src/townlet/console/handlers.py`

**Purpose**: Console validation scaffolding.
**Lines of code**: 878
**Dependencies**: stdlib=__future__, dataclasses, json, pathlib, typing; external=None; internal=townlet.config, townlet.lifecycle.manager, townlet.policy.runner, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.promotion, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.lifecycle.manager, townlet.policy.runner, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.promotion, townlet.telemetry.publisher, townlet.world.grid

### Classes
- `ConsoleCommand` — defined at line 26; decorators: dataclass
  - Docstring: Represents a parsed console command ready for execution.
  - Attributes:
    - name: str (public)
    - args: tuple[object, ...] (public)
    - kwargs: dict[str, object] (public)
  - Methods: None declared
- `ConsoleHandler` (inherits Protocol) — defined at line 34
  - Docstring: No class docstring provided.
  - Methods:
    - `__call__(self, command: ConsoleCommand) -> object` — No docstring provided.
- `ConsoleRouter` — defined at line 38
  - Docstring: Routes validated commands to subsystem handlers.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `register(self, name: str, handler: ConsoleHandler) -> None` — No docstring provided.
    - `dispatch(self, command: ConsoleCommand) -> object` — No docstring provided.
- `EventStream` — defined at line 54
  - Docstring: Simple subscriber that records the latest simulation events.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `connect(self, publisher: TelemetryPublisher) -> None` — No docstring provided.
    - `_record(self, events: list[dict[str, object]]) -> None` — No docstring provided.
    - `latest(self) -> list[dict[str, object]]` — No docstring provided.
- `TelemetryBridge` — defined at line 70
  - Docstring: Provides access to the latest telemetry snapshots for console consumers.
  - Methods:
    - `__init__(self, publisher: TelemetryPublisher) -> None` — No docstring provided.
    - `snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.

### Functions
- `create_console_router(publisher: TelemetryPublisher, world: WorldState | None = None, scheduler: PerturbationScheduler | None = None, promotion: PromotionManager | None = None, *, policy: PolicyRuntime | None = None, mode: str = 'viewer', config: SimulationConfig | None = None, lifecycle: 'LifecycleManager' | None = None) -> ConsoleRouter` — No docstring provided.
- `_schema_metadata(publisher: TelemetryPublisher) -> tuple[str, str | None]` — No docstring provided.

### Constants and Configuration
- `SUPPORTED_SCHEMA_PREFIX = '0.9'`
- `SUPPORTED_SCHEMA_LABEL = f'{SUPPORTED_SCHEMA_PREFIX}.x'`

### Data Flow
- Inputs: command, config, events, handler, lifecycle, mode, name, policy, promotion, publisher, scheduler, world
- Processing: Orchestrated via classes ConsoleCommand, ConsoleHandler, ConsoleRouter, EventStream, TelemetryBridge and functions _schema_metadata, create_console_router.
- Outputs: ConsoleRouter, None, dict[str, dict[str, object]], list[dict[str, object]], object, tuple[str, str | None]
- Downstream modules: townlet.config, townlet.lifecycle.manager, townlet.policy.runner, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.promotion, townlet.telemetry.publisher, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.lifecycle.manager, townlet.policy.runner, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.promotion, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Functions without docstrings: _schema_metadata, create_console_router.
- Methods without docstrings: ConsoleRouter.dispatch, ConsoleRouter.register, EventStream._record, EventStream.connect, EventStream.latest, TelemetryBridge.snapshot.
- Uses dataclasses for structured state.

## `src/townlet/core/__init__.py`

**Purpose**: Core orchestration utilities.
**Lines of code**: 7
**Dependencies**: stdlib=__future__; external=None; internal=townlet.core.sim_loop
**Related modules**: townlet.core.sim_loop

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.core.sim_loop

### Integration Points
- External libraries: None
- Internal packages: townlet.core.sim_loop

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/core/sim_loop.py`

**Purpose**: Top-level simulation loop wiring.
**Lines of code**: 242
**Dependencies**: stdlib=__future__, collections.abc, dataclasses, hashlib, pathlib, random; external=None; internal=townlet.config, townlet.lifecycle.manager, townlet.observations.builder, townlet.policy.runner, townlet.rewards.engine, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid
**Related modules**: townlet.config, townlet.lifecycle.manager, townlet.observations.builder, townlet.policy.runner, townlet.rewards.engine, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Classes
- `TickArtifacts` — defined at line 36; decorators: dataclass
  - Docstring: Collects per-tick data for logging and testing.
  - Attributes:
    - observations: dict[str, object] (public)
    - rewards: dict[str, float] (public)
  - Methods: None declared
- `SimulationLoop` — defined at line 43
  - Docstring: Orchestrates the Townlet simulation tick-by-tick.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `_build_components(self) -> None` — No docstring provided.
    - `reset(self) -> None` — Reset the simulation loop to its initial state.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `save_snapshot(self, root: Path | None = None) -> Path` — Persist the current world relationships and tick to ``root``.
    - `load_snapshot(self, path: Path) -> None` — Restore world relationships and tick from the snapshot at ``path``.
    - `run(self, max_ticks: int | None = None) -> Iterable[TickArtifacts]` — Run the loop until `max_ticks` or indefinitely.
    - `step(self) -> TickArtifacts` — No docstring provided.
    - `_derive_seed(self, stream: str) -> int` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: config, max_ticks, path, ratio, root, stream
- Processing: Orchestrated via classes SimulationLoop, TickArtifacts and functions None.
- Outputs: Iterable[TickArtifacts], None, Path, TickArtifacts, int
- Downstream modules: townlet.config, townlet.lifecycle.manager, townlet.observations.builder, townlet.policy.runner, townlet.rewards.engine, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.lifecycle.manager, townlet.observations.builder, townlet.policy.runner, townlet.rewards.engine, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Code Quality Notes
- Methods without docstrings: SimulationLoop._build_components, SimulationLoop._derive_seed, SimulationLoop.set_anneal_ratio, SimulationLoop.step.
- Uses dataclasses for structured state.

## `src/townlet/lifecycle/__init__.py`

**Purpose**: Lifecycle management utilities.
**Lines of code**: 7
**Dependencies**: stdlib=__future__; external=None; internal=townlet.lifecycle.manager
**Related modules**: townlet.lifecycle.manager

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.lifecycle.manager

### Integration Points
- External libraries: None
- Internal packages: townlet.lifecycle.manager

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/lifecycle/manager.py`

**Purpose**: Agent lifecycle enforcement (exits, spawns, cooldowns).
**Lines of code**: 167
**Dependencies**: stdlib=__future__, dataclasses, typing; external=None; internal=townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- `_RespawnTicket` — defined at line 13; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - agent_id: str (public)
    - scheduled_tick: int (public)
    - blueprint: dict[str, Any] (public)
  - Methods: None declared
- `LifecycleManager` — defined at line 19
  - Docstring: Centralises lifecycle checks as outlined in the conceptual design snapshot.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `evaluate(self, world: WorldState, tick: int) -> dict[str, bool]` — Return a map of agent_id -> terminated flag.
    - `finalize(self, world: WorldState, tick: int, terminated: dict[str, bool]) -> None` — No docstring provided.
    - `process_respawns(self, world: WorldState, tick: int) -> None` — No docstring provided.
    - `set_respawn_delay(self, ticks: int) -> None` — No docstring provided.
    - `set_mortality_enabled(self, enabled: bool) -> None` — No docstring provided.
    - `export_state(self) -> dict[str, int]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `reset_state(self) -> None` — No docstring provided.
    - `termination_reasons(self) -> dict[str, str]` — Return termination reasons captured during the last evaluation.
    - `_evaluate_employment(self, world: WorldState, tick: int) -> dict[str, bool]` — No docstring provided.
    - `_employment_execute_exit(self, world: WorldState, agent_id: str, tick: int, *, reason: str) -> bool` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, config, enabled, payload, reason, terminated, tick, ticks, world
- Processing: Orchestrated via classes LifecycleManager, _RespawnTicket and functions None.
- Outputs: None, bool, dict[str, bool], dict[str, int], dict[str, str]
- Downstream modules: townlet.config, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.world.grid

### Code Quality Notes
- Methods without docstrings: LifecycleManager._employment_execute_exit, LifecycleManager._evaluate_employment, LifecycleManager.export_state, LifecycleManager.finalize, LifecycleManager.import_state, LifecycleManager.process_respawns, LifecycleManager.reset_state, LifecycleManager.set_mortality_enabled, LifecycleManager.set_respawn_delay.
- Uses dataclasses for structured state.

## `src/townlet/observations/__init__.py`

**Purpose**: Observation builders and utilities.
**Lines of code**: 7
**Dependencies**: stdlib=__future__; external=None; internal=townlet.observations.builder
**Related modules**: townlet.observations.builder

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.observations.builder

### Integration Points
- External libraries: None
- Internal packages: townlet.observations.builder

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/observations/builder.py`

**Purpose**: Observation encoding across variants.
**Lines of code**: 669
**Dependencies**: stdlib=__future__, collections.abc, hashlib, math, typing; external=numpy; internal=townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- `ObservationBuilder` — defined at line 18
  - Docstring: Constructs per-agent observation payloads.
  - Attributes:
    - MAP_CHANNELS = ('self', 'agents', 'objects', 'reservations') (public)
    - SHIFT_STATES = ('pre_shift', 'on_time', 'late', 'absent', 'post_shift') (public)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `build_batch(self, world: 'WorldState', terminated: dict[str, bool]) -> dict[str, dict[str, np.ndarray]]` — Return a mapping from agent_id to observation payloads.
    - `_encode_common_features(self, features: np.ndarray, *, context: dict[str, object], slot: int, snapshot: 'AgentSnapshot', world_tick: int) -> None` — No docstring provided.
    - `_encode_rivalry(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring provided.
    - `_encode_environmental_flags(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring provided.
    - `_encode_path_hint(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring provided.
    - `_build_single(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring provided.
    - `_map_from_view(self, channels: tuple[str, ...], local_view: dict[str, object], window: int, center: int, snapshot: 'AgentSnapshot') -> np.ndarray` — No docstring provided.
    - `_build_hybrid(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring provided.
    - `_build_full(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring provided.
    - `_build_compact(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring provided.
    - `_build_social_vector(self, world: 'WorldState', snapshot: 'AgentSnapshot') -> np.ndarray` — No docstring provided.
    - `_collect_social_slots(self, world: 'WorldState', snapshot: 'AgentSnapshot') -> list[dict[str, float]]` — No docstring provided.
    - `_resolve_relationships(self, world: 'WorldState', agent_id: str) -> list[dict[str, float]]` — No docstring provided.
    - `_encode_landmarks(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring provided.
    - `_encode_relationship(self, entry: dict[str, float]) -> dict[str, float]` — No docstring provided.
    - `_empty_relationship_entry(self) -> dict[str, float]` — No docstring provided.
    - `_embed_agent_id(self, other_id: str) -> np.ndarray` — No docstring provided.
    - `_compute_aggregates(self, trust_values: Iterable[float], rivalry_values: Iterable[float]) -> tuple[float, float, float, float]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, center, channels, config, context, entry, features, local_view, other_id, rivalry_values, slot, snapshot, terminated, trust_values, window, world, world_tick
- Processing: Orchestrated via classes ObservationBuilder and functions None.
- Outputs: None, dict[str, dict[str, np.ndarray]], dict[str, float], dict[str, np.ndarray | dict[str, object]], list[dict[str, float]], np.ndarray, tuple[float, float, float, float]
- Downstream modules: townlet.config, townlet.world.grid

### Integration Points
- External libraries: numpy
- Internal packages: townlet.config, townlet.world.grid

### Code Quality Notes
- Contains TODO markers at lines 293.
- Methods without docstrings: ObservationBuilder._build_compact, ObservationBuilder._build_full, ObservationBuilder._build_hybrid, ObservationBuilder._build_single, ObservationBuilder._build_social_vector, ObservationBuilder._collect_social_slots, ObservationBuilder._compute_aggregates, ObservationBuilder._embed_agent_id, ObservationBuilder._empty_relationship_entry, ObservationBuilder._encode_common_features, ObservationBuilder._encode_environmental_flags, ObservationBuilder._encode_landmarks, ObservationBuilder._encode_path_hint, ObservationBuilder._encode_relationship, ObservationBuilder._encode_rivalry, ObservationBuilder._map_from_view, ObservationBuilder._resolve_relationships.

## `src/townlet/observations/embedding.py`

**Purpose**: Embedding slot allocation with cooldown logging.
**Lines of code**: 160
**Dependencies**: stdlib=__future__, dataclasses; external=None; internal=townlet.config
**Related modules**: townlet.config

### Classes
- `_SlotState` — defined at line 11; decorators: dataclass
  - Docstring: Tracks release metadata for a slot.
  - Attributes:
    - released_at_tick: int | None (public)
  - Methods: None declared
- `EmbeddingAllocator` — defined at line 17
  - Docstring: Assigns stable embedding slots to agents with a reuse cooldown.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `allocate(self, agent_id: str, tick: int) -> int` — Return the embedding slot for the agent, allocating if necessary.
    - `release(self, agent_id: str, tick: int) -> None` — Release the slot held by the agent.
    - `has_assignment(self, agent_id: str) -> bool` — Return whether the allocator still tracks the agent.
    - `metrics(self) -> dict[str, float]` — Expose allocation metrics for telemetry.
    - `export_state(self) -> dict[str, object]` — Serialise allocator bookkeeping for snapshot persistence.
    - `import_state(self, payload: dict[str, object]) -> None` — Restore allocator bookkeeping from snapshot data.
    - `_select_slot(self, tick: int) -> tuple[int, bool]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, config, payload, tick
- Processing: Orchestrated via classes EmbeddingAllocator, _SlotState and functions None.
- Outputs: None, bool, dict[str, float], dict[str, object], int, tuple[int, bool]
- Downstream modules: townlet.config

### Integration Points
- External libraries: None
- Internal packages: townlet.config

### Code Quality Notes
- Methods without docstrings: EmbeddingAllocator._select_slot.
- Uses dataclasses for structured state.

## `src/townlet/policy/__init__.py`

**Purpose**: Policy integration layer.
**Lines of code**: 22
**Dependencies**: stdlib=__future__; external=None; internal=townlet.policy.bc, townlet.policy.runner
**Related modules**: townlet.policy.bc, townlet.policy.runner

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.policy.bc, townlet.policy.runner

### Integration Points
- External libraries: None
- Internal packages: townlet.policy.bc, townlet.policy.runner

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/policy/bc.py`

**Purpose**: Behaviour cloning utilities.
**Lines of code**: 201
**Dependencies**: stdlib=__future__, collections.abc, dataclasses, json, pathlib; external=numpy, torch, torch.utils.data; internal=townlet.policy.models, townlet.policy.replay
**Related modules**: townlet.policy.models, townlet.policy.replay

### Classes
- `BCTrainingConfig` — defined at line 32; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - learning_rate: float = 0.001 (public)
    - batch_size: int = 64 (public)
    - epochs: int = 5 (public)
    - weight_decay: float = 0.0 (public)
    - device: str = 'cpu' (public)
  - Methods: None declared
- `BCDatasetConfig` — defined at line 41; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - manifest: Path (public)
  - Methods: None declared
- `BCTrajectoryDataset` (inherits Dataset) — defined at line 45
  - Docstring: Torch dataset flattening replay samples for behaviour cloning.
  - Methods:
    - `__init__(self, samples: Sequence[ReplaySample]) -> None` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.
    - `__getitem__(self, index: int)` — No docstring provided.
- `BCTrainer` — defined at line 121
  - Docstring: Lightweight supervised trainer for behaviour cloning.
  - Methods:
    - `__init__(self, config: BCTrainingConfig, policy_config: ConflictAwarePolicyConfig) -> None` — No docstring provided.
    - `fit(self, dataset: BCTrajectoryDataset) -> Mapping[str, float]` — No docstring provided.
    - `evaluate(self, dataset: BCTrajectoryDataset) -> Mapping[str, float]` — No docstring provided.

### Functions
- `load_bc_samples(manifest_path: Path) -> list[ReplaySample]` — No docstring provided.
- `evaluate_bc_policy(model: ConflictAwarePolicyNetwork, dataset: BCTrajectoryDataset, device: str = 'cpu') -> Mapping[str, float]` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: config, dataset, device, index, manifest_path, model, policy_config, samples
- Processing: Orchestrated via classes BCDatasetConfig, BCTrainer, BCTrainingConfig, BCTrajectoryDataset and functions evaluate_bc_policy, load_bc_samples.
- Outputs: Mapping[str, float], None, int, list[ReplaySample]
- Downstream modules: townlet.policy.models, townlet.policy.replay

### Integration Points
- External libraries: numpy, torch, torch.utils.data
- Internal packages: townlet.policy.models, townlet.policy.replay

### Code Quality Notes
- Functions without docstrings: evaluate_bc_policy, load_bc_samples.
- Methods without docstrings: BCTrainer.evaluate, BCTrainer.fit.
- Uses dataclasses for structured state.

## `src/townlet/policy/behavior.py`

**Purpose**: Behavior controller interfaces for scripted decision logic.
**Lines of code**: 196
**Dependencies**: stdlib=__future__, dataclasses, typing; external=None; internal=townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- `AgentIntent` — defined at line 13; decorators: dataclass
  - Docstring: Represents the next action an agent wishes to perform.
  - Attributes:
    - kind: str (public)
    - object_id: Optional[str] (public)
    - affordance_id: Optional[str] (public)
    - blocked: bool = False (public)
    - position: Optional[tuple[int, int]] (public)
  - Methods: None declared
- `BehaviorController` (inherits Protocol) — defined at line 23
  - Docstring: Defines the interface for agent decision logic.
  - Methods:
    - `decide(self, world: WorldState, agent_id: str) -> AgentIntent` — No docstring provided.
- `IdleBehavior` (inherits BehaviorController) — defined at line 29
  - Docstring: Default no-op behavior that keeps agents idle.
  - Methods:
    - `decide(self, world: WorldState, agent_id: str) -> AgentIntent` — No docstring provided.
- `ScriptedBehavior` (inherits BehaviorController) — defined at line 36
  - Docstring: Simple rule-based controller used before RL policies are available.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `decide(self, world: WorldState, agent_id: str) -> AgentIntent` — No docstring provided.
    - `_cleanup_pending(self, world: WorldState, agent_id: str) -> None` — No docstring provided.
    - `_maybe_move_to_job(self, world: WorldState, agent_id: str, snapshot: object) -> Optional[AgentIntent]` — No docstring provided.
    - `_satisfy_needs(self, world: WorldState, agent_id: str, snapshot: object) -> Optional[AgentIntent]` — No docstring provided.
    - `_rivals_in_queue(self, world: WorldState, agent_id: str, object_id: str) -> bool` — No docstring provided.
    - `_plan_meal(self, world: WorldState, agent_id: str) -> Optional[AgentIntent]` — No docstring provided.
    - `_find_object_of_type(self, world: WorldState, object_type: str) -> Optional[str]` — No docstring provided.

### Functions
- `build_behavior(config: SimulationConfig) -> BehaviorController` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, config, object_id, object_type, snapshot, world
- Processing: Orchestrated via classes AgentIntent, BehaviorController, IdleBehavior, ScriptedBehavior and functions build_behavior.
- Outputs: AgentIntent, BehaviorController, None, Optional[AgentIntent], Optional[str], bool
- Downstream modules: townlet.config, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.world.grid

### Code Quality Notes
- Functions without docstrings: build_behavior.
- Methods without docstrings: BehaviorController.decide, IdleBehavior.decide, ScriptedBehavior._cleanup_pending, ScriptedBehavior._find_object_of_type, ScriptedBehavior._maybe_move_to_job, ScriptedBehavior._plan_meal, ScriptedBehavior._rivals_in_queue, ScriptedBehavior._satisfy_needs, ScriptedBehavior.decide.
- Uses dataclasses for structured state.

## `src/townlet/policy/metrics.py`

**Purpose**: Utility helpers for replay and rollout metrics.
**Lines of code**: 108
**Dependencies**: stdlib=__future__, json, typing; external=numpy; internal=townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- None

### Functions
- `compute_sample_metrics(sample: ReplaySample) -> dict[str, float]` — Compute summary metrics for a replay sample.

### Constants and Configuration
- None

### Data Flow
- Inputs: sample
- Processing: Orchestrated via classes None and functions compute_sample_metrics.
- Outputs: dict[str, float]
- Downstream modules: townlet.policy.replay

### Integration Points
- External libraries: numpy
- Internal packages: townlet.policy.replay

### Code Quality Notes
- No immediate code quality concerns detected from static scan.

## `src/townlet/policy/models.py`

**Purpose**: Torch-based policy/value networks for Townlet PPO.
**Lines of code**: 83
**Dependencies**: stdlib=__future__, dataclasses; external=torch, torch.nn; internal=None
**Related modules**: None

### Classes
- `TorchNotAvailableError` (inherits RuntimeError) — defined at line 20
  - Docstring: Raised when a Torch-dependent component is used without PyTorch.
  - Methods: None declared
- `ConflictAwarePolicyConfig` — defined at line 25; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - feature_dim: int (public)
    - map_shape: tuple[int, int, int] (public)
    - action_dim: int (public)
    - hidden_dim: int = 256 (public)
  - Methods: None declared

### Functions
- `torch_available() -> bool` — Return True if PyTorch is available in the runtime.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes ConflictAwarePolicyConfig, TorchNotAvailableError and functions torch_available.
- Outputs: bool
- Downstream modules: None

### Integration Points
- External libraries: torch, torch.nn

### Code Quality Notes
- Uses dataclasses for structured state.

## `src/townlet/policy/ppo/__init__.py`

**Purpose**: PPO utilities package.
**Lines of code**: 19
**Dependencies**: stdlib=None; external=None; internal=townlet.policy.ppo.utils
**Related modules**: townlet.policy.ppo.utils

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.policy.ppo.utils

### Integration Points
- External libraries: None
- Internal packages: townlet.policy.ppo.utils

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/policy/ppo/utils.py`

**Purpose**: Utility functions for PPO advantage and loss computation.
**Lines of code**: 140
**Dependencies**: stdlib=__future__, dataclasses; external=torch; internal=None
**Related modules**: None

### Classes
- `AdvantageReturns` — defined at line 11; decorators: dataclass
  - Docstring: Container for PPO advantage and return tensors.
  - Attributes:
    - advantages: torch.Tensor (public)
    - returns: torch.Tensor (public)
  - Methods: None declared

### Functions
- `compute_gae(rewards: torch.Tensor, value_preds: torch.Tensor, dones: torch.Tensor, gamma: float, gae_lambda: float) -> AdvantageReturns` — Compute Generalized Advantage Estimation (GAE).
- `normalize_advantages(advantages: torch.Tensor, eps: float = 1e-08) -> torch.Tensor` — Normalize advantage estimates to zero mean/unit variance.
- `value_baseline_from_old_preds(value_preds: torch.Tensor, timesteps: int) -> torch.Tensor` — Extract baseline values aligned with each timestep from stored predictions.
- `clipped_value_loss(new_values: torch.Tensor, returns: torch.Tensor, old_values: torch.Tensor, value_clip: float) -> torch.Tensor` — Compute the clipped value loss term.
- `policy_surrogate(new_log_probs: torch.Tensor, old_log_probs: torch.Tensor, advantages: torch.Tensor, clip_param: float) -> tuple[torch.Tensor, torch.Tensor]` — Compute PPO clipped policy loss and clip fraction.

### Constants and Configuration
- None

### Data Flow
- Inputs: advantages, clip_param, dones, eps, gae_lambda, gamma, new_log_probs, new_values, old_log_probs, old_values, returns, rewards, timesteps, value_clip, value_preds
- Processing: Orchestrated via classes AdvantageReturns and functions clipped_value_loss, compute_gae, normalize_advantages, policy_surrogate, value_baseline_from_old_preds.
- Outputs: AdvantageReturns, torch.Tensor, tuple[torch.Tensor, torch.Tensor]
- Downstream modules: None

### Integration Points
- External libraries: torch

### Code Quality Notes
- Uses dataclasses for structured state.

## `src/townlet/policy/replay.py`

**Purpose**: Utilities for replaying observation/telemetry samples.
**Lines of code**: 641
**Dependencies**: stdlib=__future__, collections.abc, dataclasses, json, pathlib, typing; external=numpy, yaml; internal=None
**Related modules**: None

### Classes
- `ReplaySample` — defined at line 20; decorators: dataclass
  - Docstring: Container for observation samples used in training replays.
  - Attributes:
    - map: np.ndarray (public)
    - features: np.ndarray (public)
    - actions: np.ndarray (public)
    - old_log_probs: np.ndarray (public)
    - value_preds: np.ndarray (public)
    - rewards: np.ndarray (public)
    - dones: np.ndarray (public)
    - metadata: dict[str, Any] (public)
  - Methods:
    - `__post_init__(self) -> None` — No docstring provided.
    - `feature_names(self) -> Optional[list[str]]` — No docstring provided.
    - `conflict_stats(self) -> dict[str, float]` — No docstring provided.
- `ReplayBatch` — defined at line 161; decorators: dataclass
  - Docstring: Mini-batch representation composed from replay samples.
  - Attributes:
    - maps: np.ndarray (public)
    - features: np.ndarray (public)
    - actions: np.ndarray (public)
    - old_log_probs: np.ndarray (public)
    - value_preds: np.ndarray (public)
    - rewards: np.ndarray (public)
    - dones: np.ndarray (public)
    - metadata: dict[str, Any] (public)
  - Methods:
    - `__post_init__(self) -> None` — No docstring provided.
    - `conflict_stats(self) -> dict[str, float]` — No docstring provided.
- `ReplayDatasetConfig` — defined at line 279; decorators: dataclass
  - Docstring: Configuration for building replay datasets.
  - Attributes:
    - entries: list[tuple[Path, Optional[Path]]] (public)
    - batch_size: int = 1 (public)
    - shuffle: bool = False (public)
    - seed: Optional[int] (public)
    - drop_last: bool = False (public)
    - streaming: bool = False (public)
    - metrics_map: Optional[dict[str, dict[str, float]]] (public)
    - label: Optional[str] (public)
  - Methods:
    - `from_manifest(cls, manifest_path: Path, batch_size: int = 1, shuffle: bool = False, seed: Optional[int] = None, drop_last: bool = False, streaming: bool = False) -> 'ReplayDatasetConfig'` — No docstring provided.
    - `from_capture_dir(cls, capture_dir: Path, batch_size: int = 1, shuffle: bool = False, seed: Optional[int] = None, drop_last: bool = False, streaming: bool = False) -> 'ReplayDatasetConfig'` — No docstring provided.
- `ReplayDataset` — defined at line 407
  - Docstring: Iterable dataset producing conflict-aware replay batches.
  - Methods:
    - `__init__(self, config: ReplayDatasetConfig) -> None` — No docstring provided.
    - `_ensure_homogeneous(self, samples: Sequence[ReplaySample]) -> None` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.
    - `__iter__(self) -> Iterator[ReplayBatch]` — No docstring provided.
    - `_fetch_sample(self, index: int) -> ReplaySample` — No docstring provided.
    - `_ensure_sample_metrics(self, sample: ReplaySample, entry: tuple[Path, Optional[Path]]) -> None` — No docstring provided.
    - `_aggregate_metrics(self) -> dict[str, float]` — No docstring provided.

### Functions
- `_ensure_conflict_features(metadata: dict[str, Any]) -> None` — No docstring provided.
- `load_replay_sample(sample_path: Path, meta_path: Optional[Path] = None) -> ReplaySample` — Load observation tensors and metadata for replay-driven training scaffolds.
- `build_batch(samples: Sequence[ReplaySample]) -> ReplayBatch` — Stack multiple replay samples into a batch for training consumers.
- `_resolve_manifest_path(path_spec: Path, base: Path) -> Path` — Resolve manifest path specs that may be absolute or repo-relative.
- `_load_manifest(manifest_path: Path) -> list[tuple[Path, Optional[Path]]]` — No docstring provided.
- `frames_to_replay_sample(frames: Sequence[dict[str, Any]]) -> ReplaySample` — Convert collected trajectory frames into a replay sample.

### Constants and Configuration
- `REQUIRED_CONFLICT_FEATURES: tuple[str, ...] = ('rivalry_max', 'rivalry_avoid_count')`
- `STEP_ARRAY_FIELDS: tuple[str, ...] = ('actions', 'old_log_probs', 'rewards', 'dones')`
- `TRAINING_ARRAY_FIELDS: tuple[str, ...] = STEP_ARRAY_FIELDS + ('value_preds',)`

### Data Flow
- Inputs: base, batch_size, capture_dir, config, drop_last, entry, frames, index, manifest_path, meta_path, metadata, path_spec, sample, sample_path, samples, seed, shuffle, streaming
- Processing: Orchestrated via classes ReplayBatch, ReplayDataset, ReplayDatasetConfig, ReplaySample and functions _ensure_conflict_features, _load_manifest, _resolve_manifest_path, build_batch, frames_to_replay_sample, load_replay_sample.
- Outputs: 'ReplayDatasetConfig', Iterator[ReplayBatch], None, Optional[list[str]], Path, ReplayBatch, ReplaySample, dict[str, float], int, list[tuple[Path, Optional[Path]]]
- Downstream modules: None

### Integration Points
- External libraries: numpy, yaml

### Code Quality Notes
- Functions without docstrings: _ensure_conflict_features, _load_manifest.
- Methods without docstrings: ReplayBatch.conflict_stats, ReplayDataset._aggregate_metrics, ReplayDataset._ensure_homogeneous, ReplayDataset._ensure_sample_metrics, ReplayDataset._fetch_sample, ReplayDatasetConfig.from_capture_dir, ReplayDatasetConfig.from_manifest, ReplaySample.conflict_stats, ReplaySample.feature_names.
- Uses dataclasses for structured state.

## `src/townlet/policy/replay_buffer.py`

**Purpose**: In-memory replay dataset used for rollout captures.
**Lines of code**: 62
**Dependencies**: stdlib=__future__, collections.abc, dataclasses; external=None; internal=townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- `InMemoryReplayDatasetConfig` — defined at line 12; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - entries: Sequence[ReplaySample] (public)
    - batch_size: int = 1 (public)
    - drop_last: bool = False (public)
    - rollout_ticks: int = 0 (public)
    - label: str | None (public)
  - Methods: None declared
- `InMemoryReplayDataset` — defined at line 20
  - Docstring: No class docstring provided.
  - Methods:
    - `__init__(self, config: InMemoryReplayDatasetConfig) -> None` — No docstring provided.
    - `_validate_shapes(self) -> None` — No docstring provided.
    - `__iter__(self) -> Iterator[ReplayBatch]` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: config
- Processing: Orchestrated via classes InMemoryReplayDataset, InMemoryReplayDatasetConfig and functions None.
- Outputs: Iterator[ReplayBatch], None, int
- Downstream modules: townlet.policy.replay

### Integration Points
- External libraries: None
- Internal packages: townlet.policy.replay

### Code Quality Notes
- Methods without docstrings: InMemoryReplayDataset._validate_shapes.
- Uses dataclasses for structured state.

## `src/townlet/policy/rollout.py`

**Purpose**: Rollout buffer scaffolding for future live PPO integration.
**Lines of code**: 206
**Dependencies**: stdlib=__future__, collections.abc, dataclasses, json, pathlib; external=numpy; internal=townlet.policy.metrics, townlet.policy.replay, townlet.policy.replay_buffer
**Related modules**: townlet.policy.metrics, townlet.policy.replay, townlet.policy.replay_buffer

### Classes
- `AgentRollout` — defined at line 21; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - agent_id: str (public)
    - frames: list[dict[str, object]] = field(default_factory=list) (public)
  - Methods:
    - `append(self, frame: dict[str, object]) -> None` — No docstring provided.
    - `to_replay_sample(self) -> ReplaySample` — No docstring provided.
- `RolloutBuffer` — defined at line 32
  - Docstring: Collects trajectory frames and exposes helpers to save or replay them.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `record_events(self, events: Iterable[dict[str, object]]) -> None` — No docstring provided.
    - `extend(self, frames: Iterable[dict[str, object]]) -> None` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.
    - `by_agent(self) -> dict[str, AgentRollout]` — No docstring provided.
    - `to_samples(self) -> dict[str, ReplaySample]` — No docstring provided.
    - `save(self, output_dir: Path, prefix: str = 'rollout_sample', compress: bool = True) -> None` — No docstring provided.
    - `build_dataset(self, batch_size: int = 1, drop_last: bool = False) -> InMemoryReplayDataset` — No docstring provided.
    - `is_empty(self) -> bool` — No docstring provided.
    - `set_tick_count(self, ticks: int) -> None` — No docstring provided.
    - `_aggregate_metrics(self, samples: list[ReplaySample]) -> dict[str, float]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: batch_size, compress, drop_last, events, frame, frames, output_dir, prefix, samples, ticks
- Processing: Orchestrated via classes AgentRollout, RolloutBuffer and functions None.
- Outputs: InMemoryReplayDataset, None, ReplaySample, bool, dict[str, AgentRollout], dict[str, ReplaySample], dict[str, float], int
- Downstream modules: townlet.policy.metrics, townlet.policy.replay, townlet.policy.replay_buffer

### Integration Points
- External libraries: numpy
- Internal packages: townlet.policy.metrics, townlet.policy.replay, townlet.policy.replay_buffer

### Code Quality Notes
- Methods without docstrings: AgentRollout.append, AgentRollout.to_replay_sample, RolloutBuffer._aggregate_metrics, RolloutBuffer.build_dataset, RolloutBuffer.by_agent, RolloutBuffer.extend, RolloutBuffer.is_empty, RolloutBuffer.record_events, RolloutBuffer.save, RolloutBuffer.set_tick_count, RolloutBuffer.to_samples.
- Uses dataclasses for structured state.

## `src/townlet/policy/runner.py`

**Purpose**: Policy orchestration scaffolding.
**Lines of code**: 1435
**Dependencies**: stdlib=__future__, collections.abc, json, math, pathlib, random, statistics, time, typing; external=numpy, torch, torch.distributions, torch.nn.utils; internal=townlet.config, townlet.core.sim_loop, townlet.policy.bc, townlet.policy.behavior, townlet.policy.models, townlet.policy.ppo.utils, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.rollout, townlet.policy.scenario_utils, townlet.stability.promotion, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.policy.bc, townlet.policy.behavior, townlet.policy.models, townlet.policy.ppo.utils, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.rollout, townlet.policy.scenario_utils, townlet.stability.promotion, townlet.world.grid

### Classes
- `PolicyRuntime` — defined at line 87
  - Docstring: Bridges the simulation with PPO/backends via PettingZoo.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `seed_anneal_rng(self, seed: int) -> None` — No docstring provided.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `enable_anneal_blend(self, enabled: bool) -> None` — No docstring provided.
    - `register_ctx_reset_callback(self, callback: Callable[[str], None] | None) -> None` — No docstring provided.
    - `set_policy_action_provider(self, provider: Callable[[WorldState, str, AgentIntent], AgentIntent | None]) -> None` — No docstring provided.
    - `decide(self, world: WorldState, tick: int) -> dict[str, object]` — Return a primitive action per agent.
    - `post_step(self, rewards: dict[str, float], terminated: dict[str, bool]) -> None` — Record rewards and termination signals into buffers.
    - `flush_transitions(self, observations: dict[str, dict[str, object]]) -> list[dict[str, object]]` — Combine stored transition data with observations and return trajectory frames.
    - `collect_trajectory(self, clear: bool = True) -> list[dict[str, object]]` — Return accumulated trajectory frames and reset internal buffer.
    - `consume_option_switch_counts(self) -> dict[str, int]` — Return per-agent option switch counts accumulated since last call.
    - `acquire_possession(self, agent_id: str) -> bool` — No docstring provided.
    - `release_possession(self, agent_id: str) -> bool` — No docstring provided.
    - `is_possessed(self, agent_id: str) -> bool` — No docstring provided.
    - `possessed_agents(self) -> list[str]` — No docstring provided.
    - `reset_state(self) -> None` — Reset transient buffers so snapshot loads don’t duplicate data.
    - `_select_intent_with_blend(self, world: WorldState, agent_id: str, scripted: AgentIntent) -> AgentIntent` — No docstring provided.
    - `_clone_intent(intent: AgentIntent) -> AgentIntent` — No docstring provided.
    - `_intents_match(lhs: AgentIntent, rhs: AgentIntent) -> bool` — No docstring provided.
    - `_enforce_option_commit(self, agent_id: str, tick: int, intent: AgentIntent) -> tuple[AgentIntent, bool]` — No docstring provided.
    - `_annotate_with_policy_outputs(self, frame: dict[str, object]) -> None` — No docstring provided.
    - `_update_policy_snapshot(self, frames: list[dict[str, object]]) -> None` — No docstring provided.
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `active_policy_hash(self) -> str | None` — Return the configured policy hash, if any.
    - `set_policy_hash(self, value: str | None) -> None` — Set the policy hash after loading a checkpoint.
    - `current_anneal_ratio(self) -> float | None` — Return the latest anneal ratio (0.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `_ensure_policy_network(self, map_shape: tuple[int, int, int], feature_dim: int, action_dim: int) -> bool` — No docstring provided.
    - `_build_policy_network(self, feature_dim: int, map_shape: tuple[int, int, int], action_dim: int) -> ConflictAwarePolicyNetwork` — No docstring provided.
- `TrainingHarness` — defined at line 534
  - Docstring: Coordinates RL training sessions.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `run(self) -> None` — Entry point for CLI training runs based on config.
    - `current_anneal_ratio(self) -> float | None` — No docstring provided.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `run_replay(self, sample_path: Path, meta_path: Path | None = None) -> dict[str, float]` — Load a replay observation sample and surface conflict-aware stats.
    - `run_replay_batch(self, pairs: Iterable[tuple[Path, Path | None]]) -> dict[str, float]` — No docstring provided.
    - `run_replay_dataset(self, dataset_config: ReplayDatasetConfig) -> dict[str, float]` — No docstring provided.
    - `capture_rollout(self, ticks: int, auto_seed_agents: bool = False, output_dir: Path | None = None, prefix: str = 'rollout_sample', compress: bool = True) -> RolloutBuffer` — Run the simulation loop for a fixed number of ticks and collect frames.
    - `run_rollout_ppo(self, ticks: int, batch_size: int = 1, auto_seed_agents: bool = False, output_dir: Path | None = None, prefix: str = 'rollout_sample', compress: bool = True, epochs: int = 1, log_path: Path | None = None, log_frequency: int = 1, max_log_entries: int | None = None) -> dict[str, float]` — No docstring provided.
    - `_load_bc_dataset(self, manifest: Path) -> BCTrajectoryDataset` — No docstring provided.
    - `run_bc_training(self, *, manifest: Path | None = None, config: BCTrainingParams | None = None) -> dict[str, float]` — No docstring provided.
    - `run_anneal(self, *, dataset_config: ReplayDatasetConfig | None = None, in_memory_dataset: InMemoryReplayDataset | None = None, log_dir: Path | None = None, bc_manifest: Path | None = None) -> list[dict[str, object]]` — No docstring provided.
    - `run_ppo(self, dataset_config: ReplayDatasetConfig | None = None, epochs: int = 1, log_path: Path | None = None, log_frequency: int = 1, max_log_entries: int | None = None, in_memory_dataset: InMemoryReplayDataset | None = None) -> dict[str, float]` — No docstring provided.
    - `evaluate_anneal_results(self, results: list[dict[str, object]]) -> str` — No docstring provided.
    - `last_anneal_status(self) -> str | None` — No docstring provided.
    - `_record_promotion_evaluation(self, *, status: str, results: list[dict[str, object]]) -> None` — No docstring provided.
    - `_select_social_reward_stage(self, cycle_id: int) -> str | None` — No docstring provided.
    - `_apply_social_reward_stage(self, cycle_id: int) -> None` — No docstring provided.
    - `_summarise_batch(self, batch: ReplayBatch, batch_index: int) -> dict[str, float]` — No docstring provided.
    - `build_replay_dataset(self, config: ReplayDatasetConfig) -> ReplayDataset` — No docstring provided.
    - `build_policy_network(self, feature_dim: int, map_shape: tuple[int, int, int], action_dim: int, hidden_dim: int | None = None) -> ConflictAwarePolicyNetwork` — No docstring provided.

### Functions
- `_softmax(logits: np.ndarray) -> np.ndarray` — No docstring provided.
- `_pretty_action(action_repr: str) -> str` — No docstring provided.

### Constants and Configuration
- `PPO_TELEMETRY_VERSION = 1.2`
- `ANNEAL_BC_MIN_DEFAULT = 0.9`
- `ANNEAL_LOSS_TOLERANCE_DEFAULT = 0.1`
- `ANNEAL_QUEUE_TOLERANCE_DEFAULT = 0.15`

### Data Flow
- Inputs: action_dim, action_repr, agent_id, auto_seed_agents, batch, batch_index, batch_size, bc_manifest, callback, clear, compress, config, cycle_id, dataset_config, enabled, epochs, feature_dim, frame, frames, hidden_dim, in_memory_dataset, intent, lhs, log_dir, log_frequency, log_path, logits, manifest, map_shape, max_log_entries, meta_path, observations, output_dir, pairs, prefix, provider, ratio, results, rewards, rhs, sample_path, scripted, seed, status, terminated, tick, ticks, value, world
- Processing: Orchestrated via classes PolicyRuntime, TrainingHarness and functions _pretty_action, _softmax.
- Outputs: AgentIntent, BCTrajectoryDataset, ConflictAwarePolicyNetwork, None, ReplayDataset, RolloutBuffer, bool, dict[str, dict[str, object]], dict[str, float], dict[str, int], dict[str, object], float | None, list[dict[str, object]], list[str], np.ndarray, str, str | None, tuple[AgentIntent, bool]
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.policy.bc, townlet.policy.behavior, townlet.policy.models, townlet.policy.ppo.utils, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.rollout, townlet.policy.scenario_utils, townlet.stability.promotion, townlet.world.grid

### Integration Points
- External libraries: numpy, torch, torch.distributions, torch.nn.utils
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.policy.bc, townlet.policy.behavior, townlet.policy.models, townlet.policy.ppo.utils, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.rollout, townlet.policy.scenario_utils, townlet.stability.promotion, townlet.world.grid

### Code Quality Notes
- Functions without docstrings: _pretty_action, _softmax.
- Methods without docstrings: PolicyRuntime._annotate_with_policy_outputs, PolicyRuntime._build_policy_network, PolicyRuntime._clone_intent, PolicyRuntime._enforce_option_commit, PolicyRuntime._ensure_policy_network, PolicyRuntime._intents_match, PolicyRuntime._select_intent_with_blend, PolicyRuntime._update_policy_snapshot, PolicyRuntime.acquire_possession, PolicyRuntime.enable_anneal_blend, PolicyRuntime.is_possessed, PolicyRuntime.latest_policy_snapshot, PolicyRuntime.possessed_agents, PolicyRuntime.register_ctx_reset_callback, PolicyRuntime.release_possession, PolicyRuntime.seed_anneal_rng, PolicyRuntime.set_anneal_ratio, PolicyRuntime.set_anneal_ratio, PolicyRuntime.set_policy_action_provider, TrainingHarness._apply_social_reward_stage, TrainingHarness._load_bc_dataset, TrainingHarness._record_promotion_evaluation, TrainingHarness._select_social_reward_stage, TrainingHarness._summarise_batch, TrainingHarness.build_policy_network, TrainingHarness.build_replay_dataset, TrainingHarness.current_anneal_ratio, TrainingHarness.evaluate_anneal_results, TrainingHarness.last_anneal_status, TrainingHarness.run_anneal, TrainingHarness.run_bc_training, TrainingHarness.run_ppo, TrainingHarness.run_replay_batch, TrainingHarness.run_replay_dataset, TrainingHarness.run_rollout_ppo, TrainingHarness.set_anneal_ratio.

## `src/townlet/policy/scenario_utils.py`

**Purpose**: Helpers for applying scenario initialisation to simulation loops.
**Lines of code**: 93
**Dependencies**: stdlib=__future__, typing; external=None; internal=townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid
**Related modules**: townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Classes
- `ScenarioBehavior` — defined at line 78
  - Docstring: Wraps an existing behavior controller with scripted schedules.
  - Methods:
    - `__init__(self, base_behavior, schedules: dict[str, list[AgentIntent]]) -> None` — No docstring provided.
    - `decide(self, world, agent_id)` — No docstring provided.

### Functions
- `apply_scenario(loop: SimulationLoop, scenario: dict[str, Any]) -> None` — No docstring provided.
- `seed_default_agents(loop: SimulationLoop) -> None` — No docstring provided.
- `has_agents(loop: SimulationLoop) -> bool` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, base_behavior, loop, scenario, schedules, world
- Processing: Orchestrated via classes ScenarioBehavior and functions apply_scenario, has_agents, seed_default_agents.
- Outputs: None, bool
- Downstream modules: townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Code Quality Notes
- Functions without docstrings: apply_scenario, has_agents, seed_default_agents.
- Methods without docstrings: ScenarioBehavior.decide.

## `src/townlet/policy/scripted.py`

**Purpose**: Simple scripted policy helpers for trajectory capture.
**Lines of code**: 126
**Dependencies**: stdlib=__future__, dataclasses; external=None; internal=townlet.world.grid
**Related modules**: townlet.world.grid

### Classes
- `ScriptedPolicy` — defined at line 10
  - Docstring: Base class for scripted policies used during BC trajectory capture.
  - Attributes:
    - name: str = 'scripted' (public)
  - Methods:
    - `decide(self, world: WorldState, tick: int) -> dict[str, dict]` — No docstring provided.
    - `describe(self) -> str` — No docstring provided.
    - `trajectory_prefix(self) -> str` — No docstring provided.
- `IdlePolicy` (inherits ScriptedPolicy) — defined at line 29; decorators: dataclass
  - Docstring: Default scripted policy: all agents wait every tick.
  - Attributes:
    - name: str = 'idle' (public)
  - Methods:
    - `decide(self, world: WorldState, tick: int) -> dict[str, dict]` — No docstring provided.
- `ScriptedPolicyAdapter` — defined at line 47
  - Docstring: Adapter so SimulationLoop can call scripted policies.
  - Methods:
    - `__init__(self, scripted_policy: ScriptedPolicy) -> None` — No docstring provided.
    - `decide(self, world: WorldState, tick: int) -> dict[str, dict]` — No docstring provided.
    - `post_step(self, rewards: dict[str, float], terminated: dict[str, bool]) -> None` — No docstring provided.
    - `flush_transitions(self, observations) -> None` — No docstring provided.
    - `collect_trajectory(self, *, clear: bool = False)` — No docstring provided.
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `possessed_agents(self) -> list[str]` — No docstring provided.
    - `consume_option_switch_counts(self) -> dict[str, int]` — No docstring provided.
    - `active_policy_hash(self) -> str | None` — No docstring provided.
    - `set_policy_hash(self, value: str | None) -> None` — No docstring provided.
    - `current_anneal_ratio(self) -> float | None` — No docstring provided.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `enable_anneal_blend(self, _: bool) -> None` — No docstring provided.

### Functions
- `get_scripted_policy(name: str) -> ScriptedPolicy` — Factory for scripted policies; extend with richer behaviours as needed.

### Constants and Configuration
- None

### Data Flow
- Inputs: _, clear, name, observations, ratio, rewards, scripted_policy, terminated, tick, value, world
- Processing: Orchestrated via classes IdlePolicy, ScriptedPolicy, ScriptedPolicyAdapter and functions get_scripted_policy.
- Outputs: None, ScriptedPolicy, dict[str, dict[str, object]], dict[str, dict], dict[str, int], float | None, list[str], str, str | None
- Downstream modules: townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.world.grid

### Code Quality Notes
- Methods without docstrings: IdlePolicy.decide, ScriptedPolicy.decide, ScriptedPolicy.describe, ScriptedPolicy.trajectory_prefix, ScriptedPolicyAdapter.active_policy_hash, ScriptedPolicyAdapter.collect_trajectory, ScriptedPolicyAdapter.consume_option_switch_counts, ScriptedPolicyAdapter.current_anneal_ratio, ScriptedPolicyAdapter.decide, ScriptedPolicyAdapter.enable_anneal_blend, ScriptedPolicyAdapter.flush_transitions, ScriptedPolicyAdapter.latest_policy_snapshot, ScriptedPolicyAdapter.possessed_agents, ScriptedPolicyAdapter.post_step, ScriptedPolicyAdapter.set_anneal_ratio, ScriptedPolicyAdapter.set_policy_hash.
- Uses dataclasses for structured state.

## `src/townlet/rewards/__init__.py`

**Purpose**: Reward computation utilities.
**Lines of code**: 7
**Dependencies**: stdlib=__future__; external=None; internal=townlet.rewards.engine
**Related modules**: townlet.rewards.engine

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.rewards.engine

### Integration Points
- External libraries: None
- Internal packages: townlet.rewards.engine

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/rewards/engine.py`

**Purpose**: Reward calculation guardrails and aggregation.
**Lines of code**: 257
**Dependencies**: stdlib=__future__, collections.abc; external=None; internal=townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- `RewardEngine` — defined at line 11
  - Docstring: Compute per-agent rewards with clipping and guardrails.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `compute(self, world: WorldState, terminated: dict[str, bool], reasons: Mapping[str, str] | None = None) -> dict[str, float]` — No docstring provided.
    - `_consume_chat_events(self, world: WorldState) -> Iterable[dict[str, object]]` — No docstring provided.
    - `_social_rewards_enabled(self) -> bool` — No docstring provided.
    - `_compute_chat_rewards(self, world: WorldState, events: Iterable[dict[str, object]]) -> dict[str, float]` — No docstring provided.
    - `_needs_override(self, snapshot) -> bool` — No docstring provided.
    - `_is_blocked(self, agent_id: str, tick: int, window: int) -> bool` — No docstring provided.
    - `_prune_termination_blocks(self, tick: int, window: int) -> None` — No docstring provided.
    - `_compute_wage_bonus(self, agent_id: str, world: WorldState, wage_rate: float) -> float` — No docstring provided.
    - `_compute_punctuality_bonus(self, agent_id: str, world: WorldState, bonus_rate: float) -> float` — No docstring provided.
    - `_compute_terminal_penalty(self, agent_id: str, terminated: Mapping[str, bool], reasons: Mapping[str, str]) -> float` — No docstring provided.
    - `_reset_episode_totals(self, terminated: dict[str, bool], world: WorldState) -> None` — No docstring provided.
    - `latest_reward_breakdown(self) -> dict[str, dict[str, float]]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, bonus_rate, config, events, reasons, snapshot, terminated, tick, wage_rate, window, world
- Processing: Orchestrated via classes RewardEngine and functions None.
- Outputs: Iterable[dict[str, object]], None, bool, dict[str, dict[str, float]], dict[str, float], float
- Downstream modules: townlet.config, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.world.grid

### Code Quality Notes
- Methods without docstrings: RewardEngine._compute_chat_rewards, RewardEngine._compute_punctuality_bonus, RewardEngine._compute_terminal_penalty, RewardEngine._compute_wage_bonus, RewardEngine._consume_chat_events, RewardEngine._is_blocked, RewardEngine._needs_override, RewardEngine._prune_termination_blocks, RewardEngine._reset_episode_totals, RewardEngine._social_rewards_enabled, RewardEngine.compute, RewardEngine.latest_reward_breakdown.

## `src/townlet/scheduler/__init__.py`

**Purpose**: Schedulers for perturbations and timers.
**Lines of code**: 7
**Dependencies**: stdlib=__future__; external=None; internal=townlet.scheduler.perturbations
**Related modules**: townlet.scheduler.perturbations

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.scheduler.perturbations

### Integration Points
- External libraries: None
- Internal packages: townlet.scheduler.perturbations

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/scheduler/perturbations.py`

**Purpose**: Perturbation scheduler scaffolding.
**Lines of code**: 562
**Dependencies**: stdlib=__future__, collections.abc, dataclasses, random, typing; external=None; internal=townlet.config, townlet.utils, townlet.world.grid
**Related modules**: townlet.config, townlet.utils, townlet.world.grid

### Classes
- `ScheduledPerturbation` — defined at line 25; decorators: dataclass
  - Docstring: Represents a perturbation that is pending or active in the world.
  - Attributes:
    - event_id: str (public)
    - spec_name: str (public)
    - kind: PerturbationKind (public)
    - started_at: int (public)
    - ends_at: int (public)
    - payload: dict[str, object] = field(default_factory=dict) (public)
    - targets: list[str] = field(default_factory=list) (public)
  - Methods: None declared
- `PerturbationScheduler` — defined at line 37
  - Docstring: Injects bounded random events into the world.
  - Methods:
    - `__init__(self, config: SimulationConfig, *, rng: Optional[random.Random] = None) -> None` — No docstring provided.
    - `tick(self, world: WorldState, current_tick: int) -> None` — No docstring provided.
    - `_expire_active(self, current_tick: int, world: WorldState) -> None` — No docstring provided.
    - `_expire_cooldowns(self, current_tick: int) -> None` — No docstring provided.
    - `_expire_window_events(self, current_tick: int) -> None` — No docstring provided.
    - `_drain_pending(self, world: WorldState, current_tick: int) -> None` — No docstring provided.
    - `_maybe_schedule(self, world: WorldState, current_tick: int) -> None` — No docstring provided.
    - `schedule_manual(self, world: WorldState, spec_name: str, current_tick: int, *, starts_in: int = 0, duration: int | None = None, targets: Optional[list[str]] = None, payload_overrides: Optional[dict[str, object]] = None) -> ScheduledPerturbation` — No docstring provided.
    - `cancel_event(self, world: WorldState, event_id: str) -> bool` — No docstring provided.
    - `_activate(self, world: WorldState, event: ScheduledPerturbation) -> None` — No docstring provided.
    - `_apply_event(self, world: WorldState, event: ScheduledPerturbation) -> None` — No docstring provided.
    - `_on_event_concluded(self, world: WorldState, event: ScheduledPerturbation) -> None` — No docstring provided.
    - `seed(self, value: int) -> None` — No docstring provided.
    - `_can_fire_spec(self, name: str, spec: PerturbationEventConfig, current_tick: int) -> bool` — No docstring provided.
    - `_per_tick_probability(self, spec: PerturbationEventConfig) -> float` — No docstring provided.
    - `_generate_event(self, name: str, spec: PerturbationEventConfig, current_tick: int, world: WorldState, *, duration_override: int | None = None, targets_override: Optional[list[str]] = None, payload_override: Optional[dict[str, object]] = None) -> Optional[ScheduledPerturbation]` — No docstring provided.
    - `_eligible_agents(self, world: WorldState, current_tick: int) -> list[str]` — No docstring provided.
    - `enqueue(self, events: Iterable[ScheduledPerturbation | Mapping[str, object]]) -> None` — No docstring provided.
    - `pending(self) -> list[ScheduledPerturbation]` — No docstring provided.
    - `active(self) -> dict[str, ScheduledPerturbation]` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `reset_state(self) -> None` — No docstring provided.
    - `allocate_event_id(self) -> str` — No docstring provided.
    - `spec_for(self, name: str) -> Optional[PerturbationEventConfig]` — No docstring provided.
    - `rng_state(self) -> tuple` — No docstring provided.
    - `set_rng_state(self, state: tuple) -> None` — No docstring provided.
    - `rng(self) -> random.Random` — No docstring provided.
    - `_coerce_event(self, data: Mapping[str, object]) -> ScheduledPerturbation` — No docstring provided.
    - `_serialize_event(event: ScheduledPerturbation) -> dict[str, object]` — No docstring provided.
    - `serialize_event(self, event: ScheduledPerturbation) -> dict[str, object]` — No docstring provided.
    - `latest_state(self) -> dict[str, object]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: config, current_tick, data, duration, duration_override, event, event_id, events, name, payload, payload_override, payload_overrides, rng, spec, spec_name, starts_in, state, targets, targets_override, value, world
- Processing: Orchestrated via classes PerturbationScheduler, ScheduledPerturbation and functions None.
- Outputs: None, Optional[PerturbationEventConfig], Optional[ScheduledPerturbation], ScheduledPerturbation, bool, dict[str, ScheduledPerturbation], dict[str, object], float, list[ScheduledPerturbation], list[str], random.Random, str, tuple
- Downstream modules: townlet.config, townlet.utils, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.utils, townlet.world.grid

### Code Quality Notes
- Methods without docstrings: PerturbationScheduler._activate, PerturbationScheduler._apply_event, PerturbationScheduler._can_fire_spec, PerturbationScheduler._coerce_event, PerturbationScheduler._drain_pending, PerturbationScheduler._eligible_agents, PerturbationScheduler._expire_active, PerturbationScheduler._expire_cooldowns, PerturbationScheduler._expire_window_events, PerturbationScheduler._generate_event, PerturbationScheduler._maybe_schedule, PerturbationScheduler._on_event_concluded, PerturbationScheduler._per_tick_probability, PerturbationScheduler._serialize_event, PerturbationScheduler.active, PerturbationScheduler.allocate_event_id, PerturbationScheduler.cancel_event, PerturbationScheduler.enqueue, PerturbationScheduler.export_state, PerturbationScheduler.import_state, PerturbationScheduler.latest_state, PerturbationScheduler.pending, PerturbationScheduler.reset_state, PerturbationScheduler.rng, PerturbationScheduler.rng_state, PerturbationScheduler.schedule_manual, PerturbationScheduler.seed, PerturbationScheduler.serialize_event, PerturbationScheduler.set_rng_state, PerturbationScheduler.spec_for, PerturbationScheduler.tick.
- Uses dataclasses for structured state.

## `src/townlet/snapshots/__init__.py`

**Purpose**: Snapshot and restore helpers.
**Lines of code**: 25
**Dependencies**: stdlib=__future__; external=None; internal=townlet.snapshots.migrations, townlet.snapshots.state
**Related modules**: townlet.snapshots.migrations, townlet.snapshots.state

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.snapshots.migrations, townlet.snapshots.state

### Integration Points
- External libraries: None
- Internal packages: townlet.snapshots.migrations, townlet.snapshots.state

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/snapshots/migrations.py`

**Purpose**: Snapshot migration registry and helpers.
**Lines of code**: 121
**Dependencies**: stdlib=__future__, collections, collections.abc, dataclasses, typing; external=None; internal=townlet.config, townlet.snapshots.state
**Related modules**: townlet.config, townlet.snapshots.state

### Classes
- `MigrationNotFoundError` (inherits Exception) — defined at line 19
  - Docstring: Raised when no migration path exists between config identifiers.
  - Methods: None declared
- `MigrationExecutionError` (inherits Exception) — defined at line 23
  - Docstring: Raised when a migration handler fails or leaves the snapshot unchanged.
  - Methods: None declared
- `MigrationEdge` — defined at line 28; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - source: str (public)
    - target: str (public)
    - handler: MigrationHandler (public)
  - Methods:
    - `identifier(self) -> str` — No docstring provided.
- `SnapshotMigrationRegistry` — defined at line 40
  - Docstring: Maintains registered snapshot migrations keyed by config identifiers.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `register(self, from_config: str, to_config: str, handler: MigrationHandler) -> None` — No docstring provided.
    - `clear(self) -> None` — No docstring provided.
    - `_neighbours(self, node: str) -> Iterable[MigrationEdge]` — No docstring provided.
    - `find_path(self, start: str, goal: str) -> list[MigrationEdge]` — No docstring provided.
    - `apply_path(self, path: list[MigrationEdge], state: 'SnapshotState', config: 'SimulationConfig') -> tuple['SnapshotState', list[str]]` — No docstring provided.

### Functions
- `register_migration(from_config: str, to_config: str, handler: MigrationHandler) -> None` — Register a snapshot migration handler.
- `clear_registry() -> None` — Reset registry (intended for test teardown).

### Constants and Configuration
- None

### Data Flow
- Inputs: config, from_config, goal, handler, node, path, start, state, to_config
- Processing: Orchestrated via classes MigrationEdge, MigrationExecutionError, MigrationNotFoundError, SnapshotMigrationRegistry and functions clear_registry, register_migration.
- Outputs: Iterable[MigrationEdge], None, list[MigrationEdge], str, tuple['SnapshotState', list[str]]
- Downstream modules: townlet.config, townlet.snapshots.state

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.snapshots.state

### Code Quality Notes
- Methods without docstrings: MigrationEdge.identifier, SnapshotMigrationRegistry._neighbours, SnapshotMigrationRegistry.apply_path, SnapshotMigrationRegistry.clear, SnapshotMigrationRegistry.find_path, SnapshotMigrationRegistry.register.
- Uses dataclasses for structured state.

## `src/townlet/snapshots/state.py`

**Purpose**: Snapshot persistence scaffolding.
**Lines of code**: 620
**Dependencies**: stdlib=__future__, collections.abc, dataclasses, json, logging, pathlib, random, typing; external=None; internal=townlet.agents.models, townlet.config, townlet.lifecycle.manager, townlet.scheduler.perturbations, townlet.snapshots.migrations, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid
**Related modules**: townlet.agents.models, townlet.config, townlet.lifecycle.manager, townlet.scheduler.perturbations, townlet.snapshots.migrations, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Classes
- `SnapshotState` — defined at line 50; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - config_id: str (public)
    - tick: int (public)
    - agents: dict[str, dict[str, object]] = field(default_factory=dict) (public)
    - objects: dict[str, dict[str, object]] = field(default_factory=dict) (public)
    - queues: dict[str, object] = field(default_factory=dict) (public)
    - embeddings: dict[str, object] = field(default_factory=dict) (public)
    - employment: dict[str, object] = field(default_factory=dict) (public)
    - lifecycle: dict[str, object] = field(default_factory=dict) (public)
    - rng_state: Optional[str] (public)
    - rng_streams: dict[str, str] = field(default_factory=dict) (public)
    - telemetry: dict[str, object] = field(default_factory=dict) (public)
    - console_buffer: list[object] = field(default_factory=list) (public)
    - perturbations: dict[str, object] = field(default_factory=dict) (public)
    - relationships: dict[str, dict[str, dict[str, float]]] = field(default_factory=dict) (public)
    - stability: dict[str, object] = field(default_factory=dict) (public)
    - promotion: dict[str, object] = field(default_factory=dict) (public)
    - identity: dict[str, object] = field(default_factory=dict) (public)
    - migrations: dict[str, object] = field(default_factory=lambda: {'applied': [], 'required': []}) (public)
  - Methods:
    - `as_dict(self) -> dict[str, object]` — No docstring provided.
    - `from_dict(cls, payload: Mapping[str, object]) -> 'SnapshotState'` — No docstring provided.
- `SnapshotManager` — defined at line 498
  - Docstring: Handles save/load of simulation state and RNG streams.
  - Methods:
    - `__init__(self, root: Path) -> None` — No docstring provided.
    - `save(self, state: SnapshotState) -> Path` — No docstring provided.
    - `load(self, path: Path, config: SimulationConfig, *, allow_migration: bool | None = None, allow_downgrade: bool | None = None, require_exact_config: bool | None = None) -> SnapshotState` — No docstring provided.

### Functions
- `_parse_version(value: str) -> tuple[int, ...]` — No docstring provided.
- `snapshot_from_world(config: SimulationConfig, world: WorldState, *, lifecycle: Optional[LifecycleManager] = None, telemetry: Optional['TelemetryPublisher'] = None, perturbations: Optional[PerturbationScheduler] = None, stability: Optional['StabilityMonitor'] = None, promotion: Optional['PromotionManager'] = None, rng_streams: Optional[Mapping[str, random.Random]] = None, identity: Optional[Mapping[str, object]] = None) -> SnapshotState` — Capture the current world state into a snapshot payload.
- `apply_snapshot_to_world(world: WorldState, snapshot: SnapshotState, *, lifecycle: Optional[LifecycleManager] = None) -> None` — Restore world, queue, embeddings, and lifecycle state from snapshot.
- `apply_snapshot_to_telemetry(telemetry: 'TelemetryPublisher', snapshot: SnapshotState) -> None` — No docstring provided.

### Constants and Configuration
- `SNAPSHOT_SCHEMA_VERSION = '1.5'`

### Data Flow
- Inputs: allow_downgrade, allow_migration, config, identity, lifecycle, path, payload, perturbations, promotion, require_exact_config, rng_streams, root, snapshot, stability, state, telemetry, value, world
- Processing: Orchestrated via classes SnapshotManager, SnapshotState and functions _parse_version, apply_snapshot_to_telemetry, apply_snapshot_to_world, snapshot_from_world.
- Outputs: 'SnapshotState', None, Path, SnapshotState, dict[str, object], tuple[int, ...]
- Downstream modules: townlet.agents.models, townlet.config, townlet.lifecycle.manager, townlet.scheduler.perturbations, townlet.snapshots.migrations, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.agents.models, townlet.config, townlet.lifecycle.manager, townlet.scheduler.perturbations, townlet.snapshots.migrations, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Code Quality Notes
- Functions without docstrings: _parse_version, apply_snapshot_to_telemetry.
- Methods without docstrings: SnapshotManager.load, SnapshotManager.save, SnapshotState.as_dict, SnapshotState.from_dict.
- Uses dataclasses for structured state.
- Logging statements present; ensure log levels are appropriate.

## `src/townlet/stability/__init__.py`

**Purpose**: Stability guardrails.
**Lines of code**: 8
**Dependencies**: stdlib=__future__; external=None; internal=townlet.stability.monitor, townlet.stability.promotion
**Related modules**: townlet.stability.monitor, townlet.stability.promotion

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.stability.monitor, townlet.stability.promotion

### Integration Points
- External libraries: None
- Internal packages: townlet.stability.monitor, townlet.stability.promotion

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/stability/monitor.py`

**Purpose**: Monitors KPIs and promotion guardrails.
**Lines of code**: 420
**Dependencies**: stdlib=__future__, collections, collections.abc; external=None; internal=townlet.config
**Related modules**: townlet.config

### Classes
- `StabilityMonitor` — defined at line 11
  - Docstring: Tracks rolling metrics and canaries.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `_promotion_snapshot(self) -> dict[str, object]` — No docstring provided.
    - `_finalise_promotion_window(self, window_end: int) -> None` — No docstring provided.
    - `_update_promotion_window(self, tick: int, alerts: Iterable[str]) -> None` — No docstring provided.
    - `track(self, *, tick: int, rewards: dict[str, float], terminated: dict[str, bool], queue_metrics: dict[str, int] | None = None, embedding_metrics: dict[str, float] | None = None, job_snapshot: dict[str, dict[str, object]] | None = None, events: Iterable[dict[str, object]] | None = None, employment_metrics: dict[str, object] | None = None, hunger_levels: dict[str, float] | None = None, option_switch_counts: dict[str, int] | None = None, rivalry_events: Iterable[dict[str, object]] | None = None) -> None` — No docstring provided.
    - `latest_metrics(self) -> dict[str, object]` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `reset_state(self) -> None` — No docstring provided.
    - `_update_starvation_state(self, *, tick: int, hunger_levels: dict[str, float] | None, terminated: dict[str, bool]) -> int` — No docstring provided.
    - `_update_reward_samples(self, *, tick: int, rewards: dict[str, float]) -> tuple[float | None, float | None, int]` — No docstring provided.
    - `_threshold_snapshot(self) -> dict[str, object]` — No docstring provided.
    - `_update_option_samples(self, *, tick: int, option_switch_counts: dict[str, int] | None, active_agent_count: int) -> float | None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: active_agent_count, alerts, config, embedding_metrics, employment_metrics, events, hunger_levels, job_snapshot, option_switch_counts, payload, queue_metrics, rewards, rivalry_events, terminated, tick, window_end
- Processing: Orchestrated via classes StabilityMonitor and functions None.
- Outputs: None, dict[str, object], float | None, int, tuple[float | None, float | None, int]
- Downstream modules: townlet.config

### Integration Points
- External libraries: None
- Internal packages: townlet.config

### Code Quality Notes
- Methods without docstrings: StabilityMonitor._finalise_promotion_window, StabilityMonitor._promotion_snapshot, StabilityMonitor._threshold_snapshot, StabilityMonitor._update_option_samples, StabilityMonitor._update_promotion_window, StabilityMonitor._update_reward_samples, StabilityMonitor._update_starvation_state, StabilityMonitor.export_state, StabilityMonitor.import_state, StabilityMonitor.latest_metrics, StabilityMonitor.reset_state, StabilityMonitor.track.

## `src/townlet/stability/promotion.py`

**Purpose**: Promotion gate state tracking.
**Lines of code**: 263
**Dependencies**: stdlib=__future__, collections, collections.abc, json, pathlib; external=None; internal=townlet.config
**Related modules**: townlet.config

### Classes
- `PromotionManager` — defined at line 13
  - Docstring: Tracks promotion readiness and release/shadow state.
  - Methods:
    - `__init__(self, config: SimulationConfig, log_path: Path | None = None) -> None` — No docstring provided.
    - `update_from_metrics(self, metrics: Mapping[str, object], *, tick: int) -> None` — Update state based on the latest stability metrics.
    - `mark_promoted(self, *, tick: int, metadata: Mapping[str, object] | None = None) -> None` — Record a promotion event and update release metadata.
    - `register_rollback(self, *, tick: int, metadata: Mapping[str, object] | None = None) -> None` — Record a rollback event and return to monitoring state.
    - `record_manual_swap(self, *, tick: int, metadata: Mapping[str, object]) -> dict[str, object]` — Record a manual policy swap without altering candidate readiness.
    - `set_candidate_metadata(self, metadata: Mapping[str, object] | None) -> None` — No docstring provided.
    - `snapshot(self) -> dict[str, object]` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: Mapping[str, object]) -> None` — No docstring provided.
    - `reset(self) -> None` — No docstring provided.
    - `_log_event(self, record: Mapping[str, object]) -> None` — No docstring provided.
    - `_normalise_release(self, metadata: Mapping[str, object] | None) -> dict[str, object]` — No docstring provided.
    - `_resolve_rollback_target(self, metadata: Mapping[str, object] | None) -> dict[str, object]` — No docstring provided.
    - `_latest_promoted_release(self) -> dict[str, object] | None` — No docstring provided.
    - `state(self) -> str` — No docstring provided.
    - `candidate_ready(self) -> bool` — No docstring provided.
    - `pass_streak(self) -> int` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: config, log_path, metadata, metrics, payload, record, tick
- Processing: Orchestrated via classes PromotionManager and functions None.
- Outputs: None, bool, dict[str, object], dict[str, object] | None, int, str
- Downstream modules: townlet.config

### Integration Points
- External libraries: None
- Internal packages: townlet.config

### Code Quality Notes
- Methods without docstrings: PromotionManager._latest_promoted_release, PromotionManager._log_event, PromotionManager._normalise_release, PromotionManager._resolve_rollback_target, PromotionManager.candidate_ready, PromotionManager.export_state, PromotionManager.import_state, PromotionManager.pass_streak, PromotionManager.reset, PromotionManager.set_candidate_metadata, PromotionManager.snapshot, PromotionManager.state.

## `src/townlet/telemetry/__init__.py`

**Purpose**: Telemetry publication surfaces.
**Lines of code**: 7
**Dependencies**: stdlib=__future__; external=None; internal=townlet.telemetry.publisher
**Related modules**: townlet.telemetry.publisher

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.telemetry.publisher

### Integration Points
- External libraries: None
- Internal packages: townlet.telemetry.publisher

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/telemetry/narration.py`

**Purpose**: Narration throttling utilities.
**Lines of code**: 133
**Dependencies**: stdlib=__future__, collections; external=None; internal=townlet.config
**Related modules**: townlet.config

### Classes
- `NarrationRateLimiter` — defined at line 10
  - Docstring: Apply global and per-category narration cooldowns with dedupe.
  - Methods:
    - `__init__(self, config: NarrationThrottleConfig) -> None` — No docstring provided.
    - `begin_tick(self, tick: int) -> None` — No docstring provided.
    - `allow(self, category: str, *, message: str, priority: bool = False, dedupe_key: str | None = None) -> bool` — Return True if a narration may be emitted for the given category.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `_expire_recent_entries(self) -> None` — No docstring provided.
    - `_expire_window(self) -> None` — No docstring provided.
    - `_check_global_cooldown(self) -> bool` — No docstring provided.
    - `_check_category_cooldown(self, category: str) -> bool` — No docstring provided.
    - `_check_window_limit(self) -> bool` — No docstring provided.
    - `_record_emission(self, category: str, dedupe_key: str) -> None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: category, config, dedupe_key, message, payload, priority, tick
- Processing: Orchestrated via classes NarrationRateLimiter and functions None.
- Outputs: None, bool, dict[str, object]
- Downstream modules: townlet.config

### Integration Points
- External libraries: None
- Internal packages: townlet.config

### Code Quality Notes
- Methods without docstrings: NarrationRateLimiter._check_category_cooldown, NarrationRateLimiter._check_global_cooldown, NarrationRateLimiter._check_window_limit, NarrationRateLimiter._expire_recent_entries, NarrationRateLimiter._expire_window, NarrationRateLimiter._record_emission, NarrationRateLimiter.begin_tick, NarrationRateLimiter.export_state, NarrationRateLimiter.import_state.

## `src/townlet/telemetry/publisher.py`

**Purpose**: Telemetry pipelines and console bridge.
**Lines of code**: 1301
**Dependencies**: stdlib=__future__, collections, collections.abc, json, logging, pathlib, time, typing; external=None; internal=townlet.config, townlet.console.command, townlet.telemetry.narration, townlet.telemetry.transport, townlet.world.grid
**Related modules**: townlet.config, townlet.console.command, townlet.telemetry.narration, townlet.telemetry.transport, townlet.world.grid

### Classes
- `TelemetryPublisher` — defined at line 28
  - Docstring: Publishes observer snapshots and consumes console commands.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `queue_console_command(self, command: object) -> None` — No docstring provided.
    - `drain_console_buffer(self) -> Iterable[object]` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `export_console_buffer(self) -> list[object]` — No docstring provided.
    - `import_console_buffer(self, buffer: Iterable[object]) -> None` — No docstring provided.
    - `record_console_results(self, results: Iterable['ConsoleCommandResult']) -> None` — No docstring provided.
    - `latest_console_results(self) -> list[dict[str, Any]]` — No docstring provided.
    - `console_history(self) -> list[dict[str, Any]]` — No docstring provided.
    - `record_possessed_agents(self, agents: Iterable[str]) -> None` — No docstring provided.
    - `latest_possessed_agents(self) -> list[str]` — No docstring provided.
    - `latest_precondition_failures(self) -> list[dict[str, object]]` — No docstring provided.
    - `latest_transport_status(self) -> dict[str, object]` — Return transport health and backlog counters for observability.
    - `_build_transport_client(self)` — No docstring provided.
    - `_reset_transport_client(self) -> None` — No docstring provided.
    - `_send_with_retry(self, payload: bytes, tick: int) -> bool` — No docstring provided.
    - `_flush_transport_buffer(self, tick: int) -> None` — No docstring provided.
    - `_enqueue_stream_payload(self, payload: Mapping[str, Any], *, tick: int) -> None` — No docstring provided.
    - `_build_stream_payload(self, tick: int) -> dict[str, Any]` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
    - `publish_tick(self, *, tick: int, world: WorldState, observations: dict[str, object], rewards: dict[str, float], events: Iterable[dict[str, object]] | None = None, policy_snapshot: Mapping[str, Mapping[str, object]] | None = None, kpi_history: bool = False, reward_breakdown: Mapping[str, Mapping[str, float]] | None = None, stability_inputs: Mapping[str, object] | None = None, perturbations: Mapping[str, object] | None = None, policy_identity: Mapping[str, object] | None = None, possessed_agents: Iterable[str] | None = None) -> None` — No docstring provided.
    - `latest_queue_metrics(self) -> dict[str, int] | None` — Expose the most recent queue-related telemetry counters.
    - `latest_queue_history(self) -> list[dict[str, object]]` — No docstring provided.
    - `latest_rivalry_events(self) -> list[dict[str, object]]` — No docstring provided.
    - `update_anneal_status(self, status: Mapping[str, object] | None) -> None` — Record the latest anneal status payload for observer dashboards.
    - `kpi_history(self) -> dict[str, list[float]]` — No docstring provided.
    - `latest_conflict_snapshot(self) -> dict[str, object]` — Return the conflict-focused telemetry payload (queues + rivalry).
    - `latest_affordance_manifest(self) -> dict[str, object]` — Expose the most recent affordance manifest metadata.
    - `latest_reward_breakdown(self) -> dict[str, dict[str, float]]` — No docstring provided.
    - `latest_stability_inputs(self) -> dict[str, object]` — No docstring provided.
    - `record_stability_metrics(self, metrics: Mapping[str, object]) -> None` — No docstring provided.
    - `latest_stability_metrics(self) -> dict[str, object]` — No docstring provided.
    - `latest_promotion_state(self) -> dict[str, object] | None` — No docstring provided.
    - `_append_console_audit(self, payload: Mapping[str, Any]) -> None` — No docstring provided.
    - `latest_stability_alerts(self) -> list[str]` — No docstring provided.
    - `latest_perturbations(self) -> dict[str, object]` — No docstring provided.
    - `update_policy_identity(self, identity: Mapping[str, object] | None) -> None` — No docstring provided.
    - `latest_policy_identity(self) -> dict[str, object] | None` — No docstring provided.
    - `record_snapshot_migrations(self, applied: Iterable[str]) -> None` — No docstring provided.
    - `latest_snapshot_migrations(self) -> list[str]` — No docstring provided.
    - `_normalize_perturbations_payload(self, payload: Mapping[str, object]) -> dict[str, object]` — No docstring provided.
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `latest_anneal_status(self) -> dict[str, object] | None` — No docstring provided.
    - `latest_relationship_metrics(self) -> dict[str, object] | None` — Expose relationship churn payload captured during publish.
    - `latest_relationship_snapshot(self) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
    - `latest_relationship_updates(self) -> list[dict[str, object]]` — No docstring provided.
    - `update_relationship_metrics(self, payload: dict[str, object]) -> None` — Allow external callers to seed the latest relationship metrics.
    - `latest_relationship_overlay(self) -> dict[str, list[dict[str, object]]]` — No docstring provided.
    - `latest_narrations(self) -> list[dict[str, object]]` — Expose narration entries emitted during the latest publish call.
    - `latest_embedding_metrics(self) -> dict[str, float] | None` — Expose embedding allocator counters.
    - `latest_events(self) -> Iterable[dict[str, object]]` — Return the most recent event batch.
    - `latest_narration_state(self) -> dict[str, object]` — Return the narration limiter state for snapshot export.
    - `register_event_subscriber(self, subscriber: Callable[[list[dict[str, object]]], None]) -> None` — Register a callback to receive each tick's event batch.
    - `latest_job_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `latest_economy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `latest_employment_metrics(self) -> dict[str, object]` — No docstring provided.
    - `schema(self) -> str` — No docstring provided.
    - `_capture_relationship_snapshot(self, world: WorldState) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
    - `_compute_relationship_updates(self, previous: dict[str, dict[str, dict[str, float]]], current: dict[str, dict[str, dict[str, float]]]) -> list[dict[str, object]]` — No docstring provided.
    - `_build_relationship_overlay(self) -> dict[str, list[dict[str, object]]]` — No docstring provided.
    - `_process_narrations(self, events: Iterable[dict[str, object]], tick: int) -> None` — No docstring provided.
    - `_handle_queue_conflict_narration(self, event: dict[str, object], tick: int) -> None` — No docstring provided.
    - `_handle_shower_power_outage_narration(self, event: dict[str, object], tick: int) -> None` — No docstring provided.
    - `_handle_shower_complete_narration(self, event: dict[str, object], tick: int) -> None` — No docstring provided.
    - `_handle_sleep_complete_narration(self, event: dict[str, object], tick: int) -> None` — No docstring provided.
    - `_copy_relationship_snapshot(snapshot: dict[str, dict[str, dict[str, float]]]) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
    - `_update_kpi_history(self, world: WorldState) -> None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: agents, applied, buffer, command, config, current, event, events, identity, kpi_history, metrics, observations, payload, perturbations, policy_identity, policy_snapshot, possessed_agents, previous, results, reward_breakdown, rewards, snapshot, stability_inputs, status, subscriber, tick, world
- Processing: Orchestrated via classes TelemetryPublisher and functions None.
- Outputs: Iterable[dict[str, object]], Iterable[object], None, bool, dict[str, Any], dict[str, dict[str, dict[str, float]]], dict[str, dict[str, float]], dict[str, dict[str, object]], dict[str, float] | None, dict[str, int] | None, dict[str, list[dict[str, object]]], dict[str, list[float]], dict[str, object], dict[str, object] | None, list[dict[str, Any]], list[dict[str, object]], list[object], list[str], str
- Downstream modules: townlet.config, townlet.console.command, townlet.telemetry.narration, townlet.telemetry.transport, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.console.command, townlet.telemetry.narration, townlet.telemetry.transport, townlet.world.grid

### Code Quality Notes
- Methods without docstrings: TelemetryPublisher._append_console_audit, TelemetryPublisher._build_relationship_overlay, TelemetryPublisher._build_stream_payload, TelemetryPublisher._build_transport_client, TelemetryPublisher._capture_relationship_snapshot, TelemetryPublisher._compute_relationship_updates, TelemetryPublisher._copy_relationship_snapshot, TelemetryPublisher._enqueue_stream_payload, TelemetryPublisher._flush_transport_buffer, TelemetryPublisher._handle_queue_conflict_narration, TelemetryPublisher._handle_shower_complete_narration, TelemetryPublisher._handle_shower_power_outage_narration, TelemetryPublisher._handle_sleep_complete_narration, TelemetryPublisher._normalize_perturbations_payload, TelemetryPublisher._process_narrations, TelemetryPublisher._reset_transport_client, TelemetryPublisher._send_with_retry, TelemetryPublisher._update_kpi_history, TelemetryPublisher.close, TelemetryPublisher.console_history, TelemetryPublisher.drain_console_buffer, TelemetryPublisher.export_console_buffer, TelemetryPublisher.export_state, TelemetryPublisher.import_console_buffer, TelemetryPublisher.import_state, TelemetryPublisher.kpi_history, TelemetryPublisher.latest_anneal_status, TelemetryPublisher.latest_console_results, TelemetryPublisher.latest_economy_snapshot, TelemetryPublisher.latest_employment_metrics, TelemetryPublisher.latest_job_snapshot, TelemetryPublisher.latest_perturbations, TelemetryPublisher.latest_policy_identity, TelemetryPublisher.latest_policy_snapshot, TelemetryPublisher.latest_possessed_agents, TelemetryPublisher.latest_precondition_failures, TelemetryPublisher.latest_promotion_state, TelemetryPublisher.latest_queue_history, TelemetryPublisher.latest_relationship_overlay, TelemetryPublisher.latest_relationship_snapshot, TelemetryPublisher.latest_relationship_updates, TelemetryPublisher.latest_reward_breakdown, TelemetryPublisher.latest_rivalry_events, TelemetryPublisher.latest_snapshot_migrations, TelemetryPublisher.latest_stability_alerts, TelemetryPublisher.latest_stability_inputs, TelemetryPublisher.latest_stability_metrics, TelemetryPublisher.publish_tick, TelemetryPublisher.queue_console_command, TelemetryPublisher.record_console_results, TelemetryPublisher.record_possessed_agents, TelemetryPublisher.record_snapshot_migrations, TelemetryPublisher.record_stability_metrics, TelemetryPublisher.schema, TelemetryPublisher.update_policy_identity.
- Logging statements present; ensure log levels are appropriate.

## `src/townlet/telemetry/relationship_metrics.py`

**Purpose**: Helpers for tracking relationship churn and eviction telemetry.
**Lines of code**: 182
**Dependencies**: stdlib=__future__, collections, collections.abc, dataclasses; external=None; internal=None
**Related modules**: None

### Classes
- `RelationshipEvictionSample` — defined at line 32; decorators: dataclass
  - Docstring: Aggregated eviction counts captured for a completed window.
  - Attributes:
    - window_start: int (public)
    - window_end: int (public)
    - total_evictions: int (public)
    - per_owner: dict[str, int] (public)
    - per_reason: dict[str, int] (public)
  - Methods:
    - `to_payload(self) -> dict[str, object]` — Serialise the sample into a telemetry-friendly payload.
- `RelationshipChurnAccumulator` — defined at line 52
  - Docstring: Tracks relationship eviction activity over fixed tick windows.
  - Methods:
    - `__init__(self, *, window_ticks: int, max_samples: int = 8) -> None` — No docstring provided.
    - `record_eviction(self, *, tick: int, owner_id: str, evicted_id: str, reason: str | None = None) -> None` — Record an eviction event for churn tracking.
    - `_roll_window(self, tick: int) -> None` — No docstring provided.
    - `snapshot(self) -> dict[str, object]` — Return aggregates for the active window.
    - `history(self) -> Iterable[RelationshipEvictionSample]` — Return a snapshot of the recorded history.
    - `history_payload(self) -> list[dict[str, object]]` — Convert history samples into telemetry payloads.
    - `latest_payload(self) -> dict[str, object]` — Return the live window payload for telemetry publishing.
    - `ingest_payload(self, payload: dict[str, object]) -> None` — Restore the accumulator from an external payload.

### Functions
- `_advance_window(*, current_tick: int, window_ticks: int, window_start: int) -> int` — Move the window start forward until it covers ``current_tick``.

### Constants and Configuration
- None

### Data Flow
- Inputs: current_tick, evicted_id, max_samples, owner_id, payload, reason, tick, window_start, window_ticks
- Processing: Orchestrated via classes RelationshipChurnAccumulator, RelationshipEvictionSample and functions _advance_window.
- Outputs: Iterable[RelationshipEvictionSample], None, dict[str, object], int, list[dict[str, object]]
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Methods without docstrings: RelationshipChurnAccumulator._roll_window.
- Uses dataclasses for structured state.

## `src/townlet/telemetry/transport.py`

**Purpose**: Transport primitives for telemetry publishing.
**Lines of code**: 186
**Dependencies**: stdlib=__future__, collections, pathlib, typing; external=socket, sys; internal=None
**Related modules**: None

### Classes
- `TelemetryTransportError` (inherits RuntimeError) — defined at line 12
  - Docstring: Raised when telemetry messages cannot be delivered.
  - Methods: None declared
- `TransportClient` (inherits Protocol) — defined at line 16
  - Docstring: Common interface for transport implementations.
  - Methods:
    - `send(self, payload: bytes) -> None` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
- `StdoutTransport` — defined at line 26
  - Docstring: Writes telemetry payloads to stdout (for development/debug).
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `send(self, payload: bytes) -> None` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
- `FileTransport` — defined at line 40
  - Docstring: Appends newline-delimited payloads to a local file.
  - Methods:
    - `__init__(self, path: Path) -> None` — No docstring provided.
    - `send(self, payload: bytes) -> None` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
- `TcpTransport` — defined at line 56
  - Docstring: Sends telemetry payloads to a TCP endpoint.
  - Methods:
    - `__init__(self, endpoint: str, *, connect_timeout: float, send_timeout: float) -> None` — No docstring provided.
    - `_connect(self) -> None` — No docstring provided.
    - `send(self, payload: bytes) -> None` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
- `TransportBuffer` — defined at line 113
  - Docstring: Accumulates payloads prior to flushing to the transport.
  - Methods:
    - `__init__(self, *, max_batch_size: int, max_buffer_bytes: int) -> None` — No docstring provided.
    - `append(self, payload: bytes) -> None` — No docstring provided.
    - `popleft(self) -> bytes` — No docstring provided.
    - `clear(self) -> None` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.
    - `total_bytes(self) -> int` — No docstring provided.
    - `is_over_capacity(self) -> bool` — No docstring provided.
    - `drop_until_within_capacity(self) -> int` — Drop oldest payloads until buffer fits limits; returns drop count.

### Functions
- `create_transport(*, transport_type: str, file_path: Path | None, endpoint: str | None, connect_timeout: float, send_timeout: float) -> TransportClient` — Factory helper for `TelemetryPublisher`.

### Constants and Configuration
- None

### Data Flow
- Inputs: connect_timeout, endpoint, file_path, max_batch_size, max_buffer_bytes, path, payload, send_timeout, transport_type
- Processing: Orchestrated via classes FileTransport, StdoutTransport, TcpTransport, TelemetryTransportError, TransportBuffer, TransportClient and functions create_transport.
- Outputs: None, TransportClient, bool, bytes, int
- Downstream modules: None

### Integration Points
- External libraries: socket, sys

### Code Quality Notes
- Methods without docstrings: FileTransport.close, FileTransport.send, StdoutTransport.close, StdoutTransport.send, TcpTransport._connect, TcpTransport.close, TcpTransport.send, TransportBuffer.append, TransportBuffer.clear, TransportBuffer.is_over_capacity, TransportBuffer.popleft, TransportBuffer.total_bytes, TransportClient.close, TransportClient.send.

## `src/townlet/utils/__init__.py`

**Purpose**: Utility helpers for Townlet.
**Lines of code**: 9
**Dependencies**: stdlib=None; external=None; internal=townlet.utils.rng
**Related modules**: townlet.utils.rng

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.utils.rng

### Integration Points
- External libraries: None
- Internal packages: townlet.utils.rng

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/utils/rng.py`

**Purpose**: Utility helpers for serialising deterministic RNG state.
**Lines of code**: 25
**Dependencies**: stdlib=__future__, base64, random; external=pickle; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `encode_rng_state(state: tuple[object, ...]) -> str` — Encode a Python ``random`` state tuple into a base64 string.
- `decode_rng_state(payload: str) -> tuple[object, ...]` — Decode a base64-encoded RNG state back into a Python tuple.
- `encode_rng(rng: random.Random) -> str` — Capture the current state of ``rng`` as a serialisable string.

### Constants and Configuration
- None

### Data Flow
- Inputs: payload, rng, state
- Processing: Orchestrated via classes None and functions decode_rng_state, encode_rng, encode_rng_state.
- Outputs: str, tuple[object, ...]
- Downstream modules: None

### Integration Points
- External libraries: pickle

### Code Quality Notes
- No immediate code quality concerns detected from static scan.

## `src/townlet/world/__init__.py`

**Purpose**: World modelling primitives.
**Lines of code**: 16
**Dependencies**: stdlib=__future__; external=None; internal=townlet.world.grid, townlet.world.queue_manager, townlet.world.relationships
**Related modules**: townlet.world.grid, townlet.world.queue_manager, townlet.world.relationships

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet.world.grid, townlet.world.queue_manager, townlet.world.relationships

### Integration Points
- External libraries: None
- Internal packages: townlet.world.grid, townlet.world.queue_manager, townlet.world.relationships

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet/world/grid.py`

**Purpose**: Grid world representation and affordance integration.
**Lines of code**: 2700
**Dependencies**: stdlib=__future__, collections, collections.abc, dataclasses, logging, os, pathlib, random, typing; external=None; internal=townlet.agents.models, townlet.agents.relationship_modifiers, townlet.config, townlet.config.affordance_manifest, townlet.console.command, townlet.observations.embedding, townlet.telemetry.relationship_metrics, townlet.world.hooks, townlet.world.preconditions, townlet.world.queue_manager, townlet.world.relationships, townlet.world.rivalry
**Related modules**: townlet.agents.models, townlet.agents.relationship_modifiers, townlet.config, townlet.config.affordance_manifest, townlet.console.command, townlet.observations.embedding, townlet.telemetry.relationship_metrics, townlet.world.hooks, townlet.world.preconditions, townlet.world.queue_manager, townlet.world.relationships, townlet.world.rivalry

### Classes
- `HookRegistry` — defined at line 50
  - Docstring: Registers named affordance hooks and returns handlers on demand.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `register(self, name: str, handler: Callable[[dict[str, Any]], None]) -> None` — No docstring provided.
    - `handlers_for(self, name: str) -> tuple[Callable[[dict[str, Any]], None], ...]` — No docstring provided.
    - `clear(self, name: str | None = None) -> None` — No docstring provided.
- `_ConsoleHandlerEntry` — defined at line 73
  - Docstring: Metadata for registered console handlers.
  - Attributes:
    - __slots__ = ('handler', 'mode', 'require_cmd_id') (private)
  - Methods:
    - `__init__(self, handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult], *, mode: str = 'viewer', require_cmd_id: bool = False) -> None` — No docstring provided.
- `AgentSnapshot` — defined at line 100; decorators: dataclass
  - Docstring: Minimal agent view used for scaffolding.
  - Attributes:
    - agent_id: str (public)
    - position: tuple[int, int] (public)
    - needs: dict[str, float] (public)
    - wallet: float = 0.0 (public)
    - home_position: tuple[int, int] | None (public)
    - origin_agent_id: str | None (public)
    - personality: Personality = field(default_factory=_default_personality) (public)
    - inventory: dict[str, int] = field(default_factory=dict) (public)
    - job_id: str | None (public)
    - on_shift: bool = False (public)
    - lateness_counter: int = 0 (public)
    - last_late_tick: int = -1 (public)
    - shift_state: str = 'pre_shift' (public)
    - late_ticks_today: int = 0 (public)
    - attendance_ratio: float = 0.0 (public)
    - absent_shifts_7d: int = 0 (public)
    - wages_withheld: float = 0.0 (public)
    - exit_pending: bool = False (public)
    - last_action_id: str = '' (public)
    - last_action_success: bool = False (public)
    - last_action_duration: int = 0 (public)
    - episode_tick: int = 0 (public)
  - Methods:
    - `__post_init__(self) -> None` — No docstring provided.
- `InteractiveObject` — defined at line 145; decorators: dataclass
  - Docstring: Represents an interactive world object with optional occupancy.
  - Attributes:
    - object_id: str (public)
    - object_type: str (public)
    - occupied_by: str | None (public)
    - stock: dict[str, int] = field(default_factory=dict) (public)
    - position: tuple[int, int] | None (public)
  - Methods: None declared
- `RunningAffordance` — defined at line 156; decorators: dataclass
  - Docstring: Tracks an affordance currently executing on an object.
  - Attributes:
    - agent_id: str (public)
    - affordance_id: str (public)
    - duration_remaining: int (public)
    - effects: dict[str, float] (public)
  - Methods: None declared
- `AffordanceSpec` — defined at line 166; decorators: dataclass
  - Docstring: Static affordance definition loaded from configuration.
  - Attributes:
    - affordance_id: str (public)
    - object_type: str (public)
    - duration: int (public)
    - effects: dict[str, float] (public)
    - preconditions: list[str] = field(default_factory=list) (public)
    - hooks: dict[str, list[str]] = field(default_factory=dict) (public)
    - compiled_preconditions: tuple[CompiledPrecondition, ...] = field(default_factory=tuple, repr=False) (public)
  - Methods: None declared
- `WorldState` — defined at line 182; decorators: dataclass
  - Docstring: Holds mutable world state for the simulation tick.
  - Attributes:
    - config: SimulationConfig (public)
    - agents: dict[str, AgentSnapshot] = field(default_factory=dict) (public)
    - tick: int = 0 (public)
    - queue_manager: QueueManager = field(init=False) (public)
    - embedding_allocator: EmbeddingAllocator = field(init=False) (public)
    - _active_reservations: dict[str, str] = field(init=False, default_factory=dict) (private)
    - objects: dict[str, InteractiveObject] = field(init=False, default_factory=dict) (public)
    - affordances: dict[str, AffordanceSpec] = field(init=False, default_factory=dict) (public)
    - _running_affordances: dict[str, RunningAffordance] = field(init=False, default_factory=dict) (private)
    - _pending_events: dict[int, list[dict[str, Any]]] = field(init=False, default_factory=dict) (private)
    - store_stock: dict[str, dict[str, int]] = field(init=False, default_factory=dict) (public)
    - _job_keys: list[str] = field(init=False, default_factory=list) (private)
    - _employment_state: dict[str, dict[str, Any]] = field(init=False, default_factory=dict) (private)
    - _employment_exit_queue: list[str] = field(init=False, default_factory=list) (private)
    - _employment_exits_today: int = field(init=False, default=0) (private)
    - _employment_exit_queue_timestamps: dict[str, int] = field(init=False, default_factory=dict) (private)
    - _employment_manual_exits: set[str] = field(init=False, default_factory=set) (private)
    - _rivalry_ledgers: dict[str, RivalryLedger] = field(init=False, default_factory=dict) (private)
    - _relationship_ledgers: dict[str, RelationshipLedger] = field(init=False, default_factory=dict) (private)
    - _relationship_churn: RelationshipChurnAccumulator = field(init=False) (private)
    - _rivalry_events: deque[dict[str, Any]] = field(init=False, default_factory=deque) (private)
    - _relationship_window_ticks: int = 600 (private)
    - _recent_meal_participants: dict[str, dict[str, Any]] = field(init=False, default_factory=dict) (private)
    - _chat_events: list[dict[str, Any]] = field(init=False, default_factory=list) (private)
    - _rng_seed: Optional[int] = field(init=False, default=None) (private)
    - _rng_state: Optional[tuple[Any, ...]] = field(init=False, default=None) (private)
    - _rng: Optional[random.Random] = field(init=False, default=None, repr=False) (private)
    - _affordance_manifest_info: dict[str, object] = field(init=False, default_factory=dict) (private)
    - _objects_by_position: dict[tuple[int, int], list[str]] = field(init=False, default_factory=dict) (private)
    - _console_handlers: dict[str, _ConsoleHandlerEntry] = field(init=False, default_factory=dict) (private)
    - _console_cmd_history: OrderedDict[str, ConsoleCommandResult] = field(init=False, default_factory=OrderedDict) (private)
    - _console_result_buffer: deque[ConsoleCommandResult] = field(init=False, default_factory=deque) (private)
    - _hook_registry: HookRegistry = field(init=False, repr=False) (private)
    - _ctx_reset_requests: set[str] = field(init=False, default_factory=set) (private)
    - _respawn_counters: dict[str, int] = field(init=False, default_factory=dict) (private)
  - Methods:
    - `from_config(cls, config: SimulationConfig, *, rng: Optional[random.Random] = None) -> 'WorldState'` — Bootstrap the initial world from config.
    - `__post_init__(self) -> None` — No docstring provided.
    - `generate_agent_id(self, base_id: str) -> str` — No docstring provided.
    - `apply_console(self, operations: Iterable[Any]) -> None` — Apply console operations before the tick sequence runs.
    - `attach_rng(self, rng: random.Random) -> None` — Attach a deterministic RNG used for world-level randomness.
    - `rng(self) -> random.Random` — No docstring provided.
    - `get_rng_state(self) -> tuple[Any, ...]` — No docstring provided.
    - `set_rng_state(self, state: tuple[Any, ...]) -> None` — No docstring provided.
    - `register_console_handler(self, name: str, handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult], *, mode: str = 'viewer', require_cmd_id: bool = False) -> None` — Register a console handler for queued commands.
    - `register_affordance_hook(self, name: str, handler: Callable[[dict[str, Any]], None]) -> None` — Register a callable invoked when a manifest hook fires.
    - `clear_affordance_hooks(self, name: str | None = None) -> None` — Clear registered affordance hooks (used primarily for tests).
    - `consume_console_results(self) -> list[ConsoleCommandResult]` — Return and clear buffered console results.
    - `_record_console_result(self, result: ConsoleCommandResult) -> None` — No docstring provided.
    - `_dispatch_affordance_hooks(self, stage: str, hook_names: Iterable[str], *, agent_id: str, object_id: str, spec: AffordanceSpec | None, extra: Mapping[str, Any] | None = None) -> bool` — No docstring provided.
    - `_build_precondition_context(self, *, agent_id: str, object_id: str, spec: AffordanceSpec) -> dict[str, Any]` — No docstring provided.
    - `_snapshot_precondition_context(self, context: Mapping[str, Any]) -> dict[str, Any]` — No docstring provided.
    - `_register_default_console_handlers(self) -> None` — No docstring provided.
    - `_console_noop_handler(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_employment_status(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_employment_exit(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_assign_job_if_missing(self, snapshot: AgentSnapshot) -> None` — No docstring provided.
    - `remove_agent(self, agent_id: str, tick: int) -> dict[str, Any] | None` — No docstring provided.
    - `respawn_agent(self, blueprint: Mapping[str, Any]) -> None` — No docstring provided.
    - `_sync_agent_spawn(self, snapshot: AgentSnapshot) -> None` — No docstring provided.
    - `_console_spawn_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_teleport_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_release_queue_membership(self, agent_id: str) -> None` — No docstring provided.
    - `_sync_reservation_for_agent(self, agent_id: str) -> None` — No docstring provided.
    - `_is_position_walkable(self, position: tuple[int, int]) -> bool` — No docstring provided.
    - `kill_agent(self, agent_id: str, *, reason: str | None = None) -> bool` — No docstring provided.
    - `_console_set_need(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_set_price(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_force_chat(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_set_relationship(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `register_object(self, *, object_id: str, object_type: str, position: tuple[int, int] | None = None) -> None` — Register or update an interactive object in the world.
    - `_index_object_position(self, object_id: str, position: tuple[int, int]) -> None` — No docstring provided.
    - `_unindex_object_position(self, object_id: str, position: tuple[int, int]) -> None` — No docstring provided.
    - `register_affordance(self, *, affordance_id: str, object_type: str, duration: int, effects: dict[str, float], preconditions: Iterable[str] | None = None, hooks: Mapping[str, Iterable[str]] | None = None) -> None` — Register an affordance available in the world.
    - `apply_actions(self, actions: dict[str, Any]) -> None` — Apply agent actions for the current tick.
    - `resolve_affordances(self, current_tick: int) -> None` — Resolve queued affordances and hooks.
    - `request_ctx_reset(self, agent_id: str) -> None` — Mark an agent so the next observation toggles ctx_reset_flag.
    - `consume_ctx_reset_requests(self) -> set[str]` — Return and clear pending ctx-reset requests.
    - `snapshot(self) -> dict[str, AgentSnapshot]` — Return a shallow copy of the agent dictionary for observers.
    - `local_view(self, agent_id: str, radius: int, *, include_agents: bool = True, include_objects: bool = True) -> dict[str, Any]` — Return local neighborhood information for observation builders.
    - `agent_context(self, agent_id: str) -> dict[str, object]` — Return scalar context fields for the requested agent.
    - `active_reservations(self) -> dict[str, str]` — Expose a copy of active reservations for diagnostics/tests.
    - `drain_events(self) -> list[dict[str, Any]]` — Return all pending events accumulated up to the current tick.
    - `_record_queue_conflict(self, *, object_id: str, actor: str, rival: str, reason: str, queue_length: int, intensity: float | None = None) -> None` — No docstring provided.
    - `register_rivalry_conflict(self, agent_a: str, agent_b: str, *, intensity: float = 1.0, reason: str = 'conflict') -> None` — Record a rivalry-inducing conflict between two agents.
    - `rivalry_snapshot(self) -> dict[str, dict[str, float]]` — Expose rivalry ledgers for telemetry/diagnostics.
    - `relationships_snapshot(self) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
    - `relationship_tie(self, agent_id: str, other_id: str) -> RelationshipTie | None` — Return the current relationship tie between two agents, if any.
    - `consume_chat_events(self) -> list[dict[str, Any]]` — Return chat events staged for reward calculations and clear the buffer.
    - `rivalry_value(self, agent_id: str, other_id: str) -> float` — Return the rivalry score between two agents, if present.
    - `rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool` — No docstring provided.
    - `rivalry_top(self, agent_id: str, limit: int) -> list[tuple[str, float]]` — No docstring provided.
    - `consume_rivalry_events(self) -> list[dict[str, Any]]` — Return rivalry events recorded since the last call.
    - `_record_rivalry_event(self, *, agent_a: str, agent_b: str, intensity: float, reason: str) -> None` — No docstring provided.
    - `_get_rivalry_ledger(self, agent_id: str) -> RivalryLedger` — No docstring provided.
    - `_get_relationship_ledger(self, agent_id: str) -> RelationshipLedger` — No docstring provided.
    - `_relationship_parameters(self) -> RelationshipParameters` — No docstring provided.
    - `_personality_for(self, agent_id: str) -> Personality` — No docstring provided.
    - `_apply_relationship_delta(self, owner_id: str, other_id: str, *, delta: RelationshipDelta, event: RelationshipEvent) -> None` — No docstring provided.
    - `_rivalry_parameters(self) -> RivalryParameters` — No docstring provided.
    - `_decay_rivalry_ledgers(self) -> None` — No docstring provided.
    - `_decay_relationship_ledgers(self) -> None` — No docstring provided.
    - `_record_relationship_eviction(self, owner_id: str, other_id: str, reason: str) -> None` — No docstring provided.
    - `relationship_metrics_snapshot(self) -> dict[str, object]` — No docstring provided.
    - `load_relationship_snapshot(self, snapshot: dict[str, dict[str, dict[str, float]]]) -> None` — Restore relationship ledgers from persisted snapshot data.
    - `update_relationship(self, agent_a: str, agent_b: str, *, trust: float = 0.0, familiarity: float = 0.0, rivalry: float = 0.0, event: RelationshipEvent = 'generic') -> None` — No docstring provided.
    - `record_chat_success(self, speaker: str, listener: str, quality: float) -> None` — No docstring provided.
    - `record_chat_failure(self, speaker: str, listener: str) -> None` — No docstring provided.
    - `_sync_reservation(self, object_id: str) -> None` — No docstring provided.
    - `_handle_blocked(self, object_id: str, tick: int) -> None` — No docstring provided.
    - `_start_affordance(self, agent_id: str, object_id: str, affordance_id: str) -> bool` — No docstring provided.
    - `_apply_affordance_effects(self, agent_id: str, effects: dict[str, float]) -> None` — No docstring provided.
    - `_emit_event(self, event: str, payload: dict[str, Any]) -> None` — No docstring provided.
    - `_load_affordance_definitions(self) -> None` — No docstring provided.
    - `affordance_manifest_metadata(self) -> dict[str, object]` — Expose manifest metadata (path, checksum, counts) for telemetry.
    - `find_nearest_object_of_type(self, object_type: str, origin: tuple[int, int]) -> tuple[int, int] | None` — No docstring provided.
    - `_apply_need_decay(self) -> None` — No docstring provided.
    - `apply_nightly_reset(self) -> list[str]` — Return agents home, refresh needs, and reset employment flags.
    - `_assign_jobs_to_agents(self) -> None` — No docstring provided.
    - `_apply_job_state(self) -> None` — No docstring provided.
    - `_apply_job_state_legacy(self) -> None` — No docstring provided.
    - `_apply_job_state_enforced(self) -> None` — No docstring provided.
    - `_employment_context_defaults(self) -> dict[str, Any]` — No docstring provided.
    - `_get_employment_context(self, agent_id: str) -> dict[str, Any]` — No docstring provided.
    - `_employment_context_wages(self, agent_id: str) -> float` — No docstring provided.
    - `_employment_context_punctuality(self, agent_id: str) -> float` — No docstring provided.
    - `_employment_idle_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None` — No docstring provided.
    - `_employment_prepare_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None` — No docstring provided.
    - `_employment_begin_shift(self, ctx: dict[str, Any], start: int, end: int) -> None` — No docstring provided.
    - `_employment_determine_state(self, *, ctx: dict[str, Any], tick: int, start: int, at_required_location: bool, employment_cfg: EmploymentConfig) -> str` — No docstring provided.
    - `_employment_apply_state_effects(self, *, snapshot: AgentSnapshot, ctx: dict[str, Any], state: str, at_required_location: bool, wage_rate: float, lateness_penalty: float, employment_cfg: EmploymentConfig) -> None` — No docstring provided.
    - `_employment_finalize_shift(self, *, snapshot: AgentSnapshot, ctx: dict[str, Any], employment_cfg: EmploymentConfig, job_id: str | None) -> None` — No docstring provided.
    - `_employment_coworkers_on_shift(self, snapshot: AgentSnapshot) -> list[str]` — No docstring provided.
    - `_employment_enqueue_exit(self, agent_id: str, tick: int) -> None` — No docstring provided.
    - `_employment_remove_from_queue(self, agent_id: str) -> None` — No docstring provided.
    - `employment_queue_snapshot(self) -> dict[str, Any]` — No docstring provided.
    - `employment_request_manual_exit(self, agent_id: str, tick: int) -> bool` — No docstring provided.
    - `employment_defer_exit(self, agent_id: str) -> bool` — No docstring provided.
    - `_update_basket_metrics(self) -> None` — No docstring provided.
    - `_restock_economy(self) -> None` — No docstring provided.

### Functions
- `_default_personality() -> Personality` — Provide a neutral personality for agents lacking explicit traits.

### Constants and Configuration
- `_CONSOLE_HISTORY_LIMIT = 512`
- `_CONSOLE_RESULT_BUFFER_LIMIT = 256`
- `_BASE_NEEDS: tuple[str, ...] = ('hunger', 'hygiene', 'energy')`
- Environment variables: environ

### Data Flow
- Inputs: actions, actor, affordance_id, agent_a, agent_b, agent_id, at_required_location, base_id, blueprint, config, context, ctx, current_tick, delta, duration, effects, employment_cfg, end, envelope, event, extra, familiarity, handler, hook_names, hooks, include_agents, include_objects, intensity, job_id, lateness_penalty, limit, listener, mode, name, object_id, object_type, operations, origin, other_id, owner_id, payload, position, preconditions, quality, queue_length, radius, reason, require_cmd_id, result, rival, rivalry, rng, snapshot, speaker, spec, stage, start, state, tick, trust, wage_rate
- Processing: Orchestrated via classes AffordanceSpec, AgentSnapshot, HookRegistry, InteractiveObject, RunningAffordance, WorldState, _ConsoleHandlerEntry and functions _default_personality.
- Outputs: 'WorldState', ConsoleCommandResult, None, Personality, RelationshipLedger, RelationshipParameters, RelationshipTie | None, RivalryLedger, RivalryParameters, bool, dict[str, AgentSnapshot], dict[str, Any], dict[str, Any] | None, dict[str, dict[str, dict[str, float]]], dict[str, dict[str, float]], dict[str, object], dict[str, str], float, list[ConsoleCommandResult], list[dict[str, Any]], list[str], list[tuple[str, float]], random.Random, set[str], str, tuple[Any, ...], tuple[Callable[[dict[str, Any]], None], ...], tuple[int, int] | None
- Downstream modules: townlet.agents.models, townlet.agents.relationship_modifiers, townlet.config, townlet.config.affordance_manifest, townlet.console.command, townlet.observations.embedding, townlet.telemetry.relationship_metrics, townlet.world.hooks, townlet.world.preconditions, townlet.world.queue_manager, townlet.world.relationships, townlet.world.rivalry

### Integration Points
- External libraries: None
- Environment hooks: environ
- Internal packages: townlet.agents.models, townlet.agents.relationship_modifiers, townlet.config, townlet.config.affordance_manifest, townlet.console.command, townlet.observations.embedding, townlet.telemetry.relationship_metrics, townlet.world.hooks, townlet.world.preconditions, townlet.world.queue_manager, townlet.world.relationships, townlet.world.rivalry

### Code Quality Notes
- Contains TODO markers at lines 1296, 1328.
- Methods without docstrings: HookRegistry.clear, HookRegistry.handlers_for, HookRegistry.register, WorldState._apply_affordance_effects, WorldState._apply_job_state, WorldState._apply_job_state_enforced, WorldState._apply_job_state_legacy, WorldState._apply_need_decay, WorldState._apply_relationship_delta, WorldState._assign_job_if_missing, WorldState._assign_jobs_to_agents, WorldState._build_precondition_context, WorldState._console_employment_exit, WorldState._console_employment_status, WorldState._console_force_chat, WorldState._console_noop_handler, WorldState._console_set_need, WorldState._console_set_price, WorldState._console_set_relationship, WorldState._console_spawn_agent, WorldState._console_teleport_agent, WorldState._decay_relationship_ledgers, WorldState._decay_rivalry_ledgers, WorldState._dispatch_affordance_hooks, WorldState._emit_event, WorldState._employment_apply_state_effects, WorldState._employment_begin_shift, WorldState._employment_context_defaults, WorldState._employment_context_punctuality, WorldState._employment_context_wages, WorldState._employment_coworkers_on_shift, WorldState._employment_determine_state, WorldState._employment_enqueue_exit, WorldState._employment_finalize_shift, WorldState._employment_idle_state, WorldState._employment_prepare_state, WorldState._employment_remove_from_queue, WorldState._get_employment_context, WorldState._get_relationship_ledger, WorldState._get_rivalry_ledger, WorldState._handle_blocked, WorldState._index_object_position, WorldState._is_position_walkable, WorldState._load_affordance_definitions, WorldState._personality_for, WorldState._record_console_result, WorldState._record_queue_conflict, WorldState._record_relationship_eviction, WorldState._record_rivalry_event, WorldState._register_default_console_handlers, WorldState._relationship_parameters, WorldState._release_queue_membership, WorldState._restock_economy, WorldState._rivalry_parameters, WorldState._snapshot_precondition_context, WorldState._start_affordance, WorldState._sync_agent_spawn, WorldState._sync_reservation, WorldState._sync_reservation_for_agent, WorldState._unindex_object_position, WorldState._update_basket_metrics, WorldState.employment_defer_exit, WorldState.employment_queue_snapshot, WorldState.employment_request_manual_exit, WorldState.find_nearest_object_of_type, WorldState.generate_agent_id, WorldState.get_rng_state, WorldState.kill_agent, WorldState.record_chat_failure, WorldState.record_chat_success, WorldState.relationship_metrics_snapshot, WorldState.relationships_snapshot, WorldState.remove_agent, WorldState.respawn_agent, WorldState.rivalry_should_avoid, WorldState.rivalry_top, WorldState.rng, WorldState.set_rng_state, WorldState.update_relationship.
- Uses dataclasses for structured state.
- Logging statements present; ensure log levels are appropriate.

## `src/townlet/world/hooks/__init__.py`

**Purpose**: Affordance hook plug-in namespace.
**Lines of code**: 20
**Dependencies**: stdlib=__future__, typing; external=importlib; internal=townlet.world.grid
**Related modules**: townlet.world.grid

### Classes
- None

### Functions
- `load_modules(world: 'WorldState', module_paths: Iterable[str]) -> None` — Import hook modules and let them register against the given world.

### Constants and Configuration
- None

### Data Flow
- Inputs: module_paths, world
- Processing: Orchestrated via classes None and functions load_modules.
- Outputs: None
- Downstream modules: townlet.world.grid

### Integration Points
- External libraries: importlib
- Internal packages: townlet.world.grid

### Code Quality Notes
- No immediate code quality concerns detected from static scan.

## `src/townlet/world/hooks/default.py`

**Purpose**: Built-in affordance hook handlers.
**Lines of code**: 313
**Dependencies**: stdlib=__future__, typing; external=None; internal=townlet.world.grid
**Related modules**: townlet.world.grid

### Classes
- None

### Functions
- `register_hooks(world: 'WorldState') -> None` — Register built-in affordance hooks with the provided world.
- `_on_attempt_shower(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_finish_shower(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_no_power(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_attempt_eat(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_finish_eat(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_attempt_cook(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_finish_cook(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_cook_fail(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_attempt_sleep(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_finish_sleep(context: dict[str, Any]) -> None` — No docstring provided.
- `_abort_affordance(world: 'WorldState', spec: Any, agent_id: str, object_id: str, reason: str) -> None` — No docstring provided.

### Constants and Configuration
- `_AFFORDANCE_FAIL_EVENT = 'affordance_fail'`
- `_SHOWER_COMPLETE_EVENT = 'shower_complete'`
- `_SHOWER_POWER_EVENT = 'shower_power_outage'`
- `_SLEEP_COMPLETE_EVENT = 'sleep_complete'`

### Data Flow
- Inputs: agent_id, context, object_id, reason, spec, world
- Processing: Orchestrated via classes None and functions _abort_affordance, _on_attempt_cook, _on_attempt_eat, _on_attempt_shower, _on_attempt_sleep, _on_cook_fail, _on_finish_cook, _on_finish_eat, _on_finish_shower, _on_finish_sleep, _on_no_power, register_hooks.
- Outputs: None
- Downstream modules: townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.world.grid

### Code Quality Notes
- Functions without docstrings: _abort_affordance, _on_attempt_cook, _on_attempt_eat, _on_attempt_shower, _on_attempt_sleep, _on_cook_fail, _on_finish_cook, _on_finish_eat, _on_finish_shower, _on_finish_sleep, _on_no_power.

## `src/townlet/world/preconditions.py`

**Purpose**: Affordance precondition compilation and evaluation helpers.
**Lines of code**: 289
**Dependencies**: stdlib=__future__, dataclasses, typing; external=ast, re; internal=None
**Related modules**: None

### Classes
- `PreconditionSyntaxError` (inherits ValueError) — defined at line 19
  - Docstring: Raised when a manifest precondition has invalid syntax.
  - Methods: None declared
- `PreconditionEvaluationError` (inherits RuntimeError) — defined at line 23
  - Docstring: Raised when evaluation fails due to missing context or type errors.
  - Methods: None declared
- `CompiledPrecondition` — defined at line 74; decorators: dataclass(frozen=True)
  - Docstring: Stores the parsed AST and metadata for a precondition.
  - Attributes:
    - source: str (public)
    - tree: ast.AST (public)
    - identifiers: tuple[str, ...] (public)
  - Methods: None declared
- `_IdentifierCollector` (inherits ast.NodeVisitor) — defined at line 82
  - Docstring: No class docstring provided.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `visit_Name(self, node: ast.Name) -> None` — Collect bare identifiers used in the expression.

### Functions
- `_normalize_expression(expression: str) -> str` — No docstring provided.
- `_validate_tree(tree: ast.AST, source: str) -> tuple[str, ...]` — No docstring provided.
- `compile_preconditions(expressions: Iterable[str]) -> tuple[CompiledPrecondition, ...]` — Compile manifest preconditions, raising on syntax errors.
- `compile_precondition(expression: str) -> CompiledPrecondition` — Compile a single precondition expression.
- `_resolve_name(name: str, context: Mapping[str, Any]) -> Any` — No docstring provided.
- `_resolve_attr(value: Any, attr: str) -> Any` — No docstring provided.
- `_resolve_subscript(value: Any, key: Any) -> Any` — No docstring provided.
- `_evaluate(node: ast.AST, context: Mapping[str, Any]) -> Any` — No docstring provided.
- `_apply_compare(operator: ast.cmpop, left: Any, right: Any) -> bool` — No docstring provided.
- `evaluate_preconditions(preconditions: Sequence[CompiledPrecondition], context: Mapping[str, Any]) -> tuple[bool, CompiledPrecondition | None]` — Evaluate compiled preconditions against the provided context.

### Constants and Configuration
- `_ALLOWED_COMPARE_OPS = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn)`
- `_ALLOWED_BOOL_OPS = (ast.And, ast.Or)`
- `_ALLOWED_UNARY_OPS = (ast.Not, ast.USub, ast.UAdd)`
- `_ALLOWED_NODE_TYPES = (ast.Expression, ast.BoolOp, ast.Compare, ast.Name, ast.Attribute, ast.Subscript, ast.Constant, ast.UnaryOp, ast.Tuple, ast.List, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.And, ast.Or, ast.Load, ast.USub, ast.UAdd, ast.Not)`

### Data Flow
- Inputs: attr, context, expression, expressions, key, left, name, node, operator, preconditions, right, source, tree, value
- Processing: Orchestrated via classes CompiledPrecondition, PreconditionEvaluationError, PreconditionSyntaxError, _IdentifierCollector and functions _apply_compare, _evaluate, _normalize_expression, _resolve_attr, _resolve_name, _resolve_subscript, _validate_tree, compile_precondition, compile_preconditions, evaluate_preconditions.
- Outputs: Any, CompiledPrecondition, None, bool, str, tuple[CompiledPrecondition, ...], tuple[bool, CompiledPrecondition | None], tuple[str, ...]
- Downstream modules: None

### Integration Points
- External libraries: ast, re

### Code Quality Notes
- Functions without docstrings: _apply_compare, _evaluate, _normalize_expression, _resolve_attr, _resolve_name, _resolve_subscript, _validate_tree.
- Uses dataclasses for structured state.

## `src/townlet/world/queue_manager.py`

**Purpose**: Queue management with fairness guardrails.
**Lines of code**: 273
**Dependencies**: stdlib=__future__, dataclasses, time; external=None; internal=townlet.config
**Related modules**: townlet.config

### Classes
- `QueueEntry` — defined at line 18; decorators: dataclass
  - Docstring: Represents an agent waiting to access an interactive object.
  - Attributes:
    - agent_id: str (public)
    - joined_tick: int (public)
  - Methods: None declared
- `QueueManager` — defined at line 25
  - Docstring: Coordinates reservations and fairness across interactive queues.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `on_tick(self, tick: int) -> None` — Expire cooldown entries whose window has elapsed.
    - `request_access(self, object_id: str, agent_id: str, tick: int) -> bool` — Attempt to reserve the object for the agent.
    - `release(self, object_id: str, agent_id: str, tick: int, *, success: bool = True) -> None` — Release the reservation and optionally apply cooldown.
    - `record_blocked_attempt(self, object_id: str) -> bool` — Register that the current head was blocked.
    - `active_agent(self, object_id: str) -> str | None` — Return the agent currently holding the reservation, if any.
    - `queue_snapshot(self, object_id: str) -> list[str]` — Return the queue as an ordered list of agent IDs for debugging.
    - `metrics(self) -> dict[str, int]` — Expose counters useful for telemetry.
    - `performance_metrics(self) -> dict[str, int]` — Expose aggregated nanosecond timings and call counts.
    - `reset_performance_metrics(self) -> None` — No docstring provided.
    - `requeue_to_tail(self, object_id: str, agent_id: str, tick: int) -> None` — Append `agent_id` to the end of the queue if not already present.
    - `remove_agent(self, agent_id: str, tick: int) -> None` — Remove `agent_id` from all queues and active reservations.
    - `export_state(self) -> dict[str, object]` — Serialise queue activity for snapshot persistence.
    - `import_state(self, payload: dict[str, object]) -> None` — Restore queue activity from persisted snapshot data.
    - `_assign_next(self, object_id: str, tick: int) -> str | None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, config, object_id, payload, success, tick
- Processing: Orchestrated via classes QueueEntry, QueueManager and functions None.
- Outputs: None, bool, dict[str, int], dict[str, object], list[str], str | None
- Downstream modules: townlet.config

### Integration Points
- External libraries: None
- Internal packages: townlet.config

### Code Quality Notes
- Methods without docstrings: QueueManager._assign_next, QueueManager.reset_performance_metrics.
- Uses dataclasses for structured state.

## `src/townlet/world/relationships.py`

**Purpose**: Relationship ledger for Phase 4 social systems.
**Lines of code**: 169
**Dependencies**: stdlib=__future__, collections.abc, dataclasses; external=None; internal=None
**Related modules**: None

### Classes
- `RelationshipParameters` — defined at line 14; decorators: dataclass
  - Docstring: Tuning knobs for relationship tie evolution.
  - Attributes:
    - max_edges: int = 6 (public)
    - trust_decay: float = 0.0 (public)
    - familiarity_decay: float = 0.0 (public)
    - rivalry_decay: float = 0.01 (public)
  - Methods: None declared
- `RelationshipTie` — defined at line 24; decorators: dataclass
  - Docstring: No class docstring provided.
  - Attributes:
    - trust: float = 0.0 (public)
    - familiarity: float = 0.0 (public)
    - rivalry: float = 0.0 (public)
  - Methods:
    - `as_dict(self) -> dict[str, float]` — No docstring provided.
- `RelationshipLedger` — defined at line 40
  - Docstring: Maintains multi-dimensional ties for a single agent.
  - Methods:
    - `__init__(self, *, owner_id: str, params: RelationshipParameters | None = None, eviction_hook: EvictionHook | None = None) -> None` — No docstring provided.
    - `apply_delta(self, other_id: str, *, trust: float = 0.0, familiarity: float = 0.0, rivalry: float = 0.0) -> RelationshipTie` — No docstring provided.
    - `tie_for(self, other_id: str) -> RelationshipTie | None` — Return the tie for ``other_id`` if it exists.
    - `decay(self) -> None` — No docstring provided.
    - `snapshot(self) -> dict[str, dict[str, float]]` — No docstring provided.
    - `inject(self, payload: dict[str, dict[str, float]]) -> None` — No docstring provided.
    - `set_eviction_hook(self, *, owner_id: str, hook: EvictionHook | None) -> None` — No docstring provided.
    - `top_friends(self, limit: int) -> list[tuple[str, RelationshipTie]]` — No docstring provided.
    - `top_rivals(self, limit: int) -> list[tuple[str, RelationshipTie]]` — No docstring provided.
    - `remove_tie(self, other_id: str, *, reason: str = 'removed') -> None` — No docstring provided.
    - `_prune_if_needed(self, *, reason: str) -> None` — No docstring provided.
    - `_emit_eviction(self, other_id: str, *, reason: str) -> None` — No docstring provided.

### Functions
- `_clamp(value: float, *, low: float, high: float) -> float` — No docstring provided.
- `_decay_value(value: float, decay: float, *, minimum: float = -1.0) -> float` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: decay, eviction_hook, familiarity, high, hook, limit, low, minimum, other_id, owner_id, params, payload, reason, rivalry, trust, value
- Processing: Orchestrated via classes RelationshipLedger, RelationshipParameters, RelationshipTie and functions _clamp, _decay_value.
- Outputs: None, RelationshipTie, RelationshipTie | None, dict[str, dict[str, float]], dict[str, float], float, list[tuple[str, RelationshipTie]]
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Functions without docstrings: _clamp, _decay_value.
- Methods without docstrings: RelationshipLedger._emit_eviction, RelationshipLedger._prune_if_needed, RelationshipLedger.apply_delta, RelationshipLedger.decay, RelationshipLedger.inject, RelationshipLedger.remove_tie, RelationshipLedger.set_eviction_hook, RelationshipLedger.snapshot, RelationshipLedger.top_friends, RelationshipLedger.top_rivals, RelationshipTie.as_dict.
- Uses dataclasses for structured state.

## `src/townlet/world/rivalry.py`

**Purpose**: Rivalry state helpers used by conflict intro scaffolding.
**Lines of code**: 135
**Dependencies**: stdlib=__future__, collections.abc, dataclasses, typing; external=None; internal=None
**Related modules**: None

### Classes
- `RivalryParameters` — defined at line 20; decorators: dataclass
  - Docstring: Tuning knobs for rivalry evolution.
  - Attributes:
    - increment_per_conflict: float = 0.15 (public)
    - decay_per_tick: float = 0.01 (public)
    - min_value: float = 0.0 (public)
    - max_value: float = 1.0 (public)
    - avoid_threshold: float = 0.7 (public)
    - eviction_threshold: float = 0.05 (public)
    - max_edges: int = 6 (public)
  - Methods: None declared
- `RivalryLedger` — defined at line 37; decorators: dataclass
  - Docstring: Maintains rivalry scores against other agents for a single actor.
  - Attributes:
    - owner_id: str (public)
    - params: RivalryParameters = field(default_factory=RivalryParameters) (public)
    - eviction_hook: Optional[Callable[[str, str, str], None]] (public)
    - _scores: dict[str, float] = field(default_factory=dict) (private)
  - Methods:
    - `apply_conflict(self, other_id: str, *, intensity: float = 1.0) -> float` — Increase rivalry against `other_id` based on the conflict intensity.
    - `decay(self, ticks: int = 1) -> None` — Apply passive decay across all rivalry edges.
    - `inject(self, pairs: Iterable[tuple[str, float]]) -> None` — Seed rivalry scores from persisted state for round-tripping tests.
    - `score_for(self, other_id: str) -> float` — No docstring provided.
    - `should_avoid(self, other_id: str) -> bool` — Return True when rivalry exceeds the avoidance threshold.
    - `top_rivals(self, limit: int) -> list[tuple[str, float]]` — Return the strongest rivalry edges sorted descending.
    - `remove(self, other_id: str, *, reason: str = 'removed') -> None` — No docstring provided.
    - `encode_features(self, limit: int) -> list[float]` — Encode rivalry magnitudes into a fixed-width list for observations.
    - `snapshot(self) -> dict[str, float]` — Return a copy of rivalry scores for telemetry serialization.
    - `_emit_eviction(self, other_id: str, *, reason: str) -> None` — No docstring provided.

### Functions
- `_clamp(value: float, *, low: float, high: float) -> float` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: high, intensity, limit, low, other_id, pairs, reason, ticks, value
- Processing: Orchestrated via classes RivalryLedger, RivalryParameters and functions _clamp.
- Outputs: None, bool, dict[str, float], float, list[float], list[tuple[str, float]]
- Downstream modules: None

### Integration Points
- External libraries: None

### Code Quality Notes
- Functions without docstrings: _clamp.
- Methods without docstrings: RivalryLedger._emit_eviction, RivalryLedger.remove, RivalryLedger.score_for.
- Uses dataclasses for structured state.

## `src/townlet_ui/__init__.py`

**Purpose**: Observer UI toolkit exports.
**Lines of code**: 19
**Dependencies**: stdlib=None; external=None; internal=townlet_ui.commands, townlet_ui.telemetry
**Related modules**: townlet_ui.commands, townlet_ui.telemetry

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: townlet_ui.commands, townlet_ui.telemetry

### Integration Points
- External libraries: None
- Internal packages: townlet_ui.commands, townlet_ui.telemetry

### Code Quality Notes
- Minimal type annotations detected; expand type hints.

## `src/townlet_ui/commands.py`

**Purpose**: Helper utilities for dispatching console commands asynchronously.
**Lines of code**: 41
**Dependencies**: stdlib=__future__, logging, typing; external=queue, threading; internal=townlet.console.handlers
**Related modules**: townlet.console.handlers

### Classes
- `ConsoleCommandExecutor` — defined at line 15
  - Docstring: Background dispatcher that forwards console commands via a router.
  - Methods:
    - `__init__(self, router: Any, *, daemon: bool = True) -> None` — No docstring provided.
    - `submit(self, command: ConsoleCommand) -> None` — No docstring provided.
    - `shutdown(self, timeout: float | None = 1.0) -> None` — No docstring provided.
    - `_worker(self) -> None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Inputs: command, daemon, router, timeout
- Processing: Orchestrated via classes ConsoleCommandExecutor and functions None.
- Outputs: None
- Downstream modules: townlet.console.handlers

### Integration Points
- External libraries: queue, threading
- Internal packages: townlet.console.handlers

### Code Quality Notes
- Methods without docstrings: ConsoleCommandExecutor._worker, ConsoleCommandExecutor.shutdown, ConsoleCommandExecutor.submit.
- Logging statements present; ensure log levels are appropriate.

## `src/townlet_ui/dashboard.py`

**Purpose**: Rich-based console dashboard for Townlet observer UI.
**Lines of code**: 756
**Dependencies**: stdlib=__future__, collections.abc, math, time, typing; external=numpy, rich.console, rich.panel, rich.table, rich.text; internal=townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.telemetry
**Related modules**: townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.telemetry

### Classes
- None

### Functions
- `render_snapshot(snapshot: TelemetrySnapshot, tick: int, refreshed: str) -> Iterable[Panel]` — Yield rich Panels representing the current telemetry snapshot.
- `_format_top_entries(entries: Mapping[str, int]) -> str` — No docstring provided.
- `_build_narration_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_build_anneal_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_promotion_border_style(promotion: PromotionSnapshot | None) -> str` — No docstring provided.
- `_derive_promotion_reason(promotion: PromotionSnapshot, status: AnnealStatus | None) -> str` — No docstring provided.
- `_format_metadata_summary(metadata: Mapping[str, Any]) -> str` — No docstring provided.
- `_build_promotion_history_panel(history: Iterable[Mapping[str, Any]], border_style: str) -> Panel` — No docstring provided.
- `_format_history_metadata(entry: Mapping[str, Any]) -> str` — No docstring provided.
- `_safe_format(value: float | None) -> str` — No docstring provided.
- `_format_optional_float(value: float | None) -> str` — No docstring provided.
- `_build_policy_inspector_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_build_relationship_overlay_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_format_delta(value: float, inverse: bool = False) -> str` — No docstring provided.
- `_build_kpi_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_trend_from_series(series: list[float]) -> tuple[str, str]` — No docstring provided.
- `_humanize_kpi(key: str) -> str` — No docstring provided.
- `run_dashboard(loop: SimulationLoop, *, refresh_interval: float = 1.0, max_ticks: int = 0, approve: str | None = None, defer: str | None = None, focus_agent: str | None = None, show_coords: bool = False) -> None` — Continuously render dashboard against a SimulationLoop instance.
- `_build_map_panel(snapshot: TelemetrySnapshot, obs_batch: Mapping[str, dict[str, np.ndarray]], focus_agent: str | None, show_coords: bool = False) -> Panel | None` — No docstring provided.

### Constants and Configuration
- `MAP_AGENT_CHAR = 'A'`
- `MAP_CENTER_CHAR = 'S'`
- `NARRATION_CATEGORY_STYLES: dict[str, tuple[str, str]] = {'utility_outage': ('Utility Outage', 'bold red'), 'shower_complete': ('Shower Complete', 'cyan'), 'sleep_complete': ('Sleep Complete', 'green'), 'queue_conflict': ('Queue Conflict', 'magenta')}`

### Data Flow
- Inputs: approve, border_style, defer, entries, entry, focus_agent, history, inverse, key, loop, max_ticks, metadata, obs_batch, promotion, refresh_interval, refreshed, series, show_coords, snapshot, status, tick, value
- Processing: Orchestrated via classes None and functions _build_anneal_panel, _build_kpi_panel, _build_map_panel, _build_narration_panel, _build_policy_inspector_panel, _build_promotion_history_panel, _build_relationship_overlay_panel, _derive_promotion_reason, _format_delta, _format_history_metadata, _format_metadata_summary, _format_optional_float, _format_top_entries, _humanize_kpi, _promotion_border_style, _safe_format, _trend_from_series, render_snapshot, run_dashboard.
- Outputs: Iterable[Panel], None, Panel, Panel | None, str, tuple[str, str]
- Downstream modules: townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.telemetry

### Integration Points
- External libraries: numpy, rich.console, rich.panel, rich.table, rich.text
- Internal packages: townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.telemetry

### Code Quality Notes
- Functions without docstrings: _build_anneal_panel, _build_kpi_panel, _build_map_panel, _build_narration_panel, _build_policy_inspector_panel, _build_promotion_history_panel, _build_relationship_overlay_panel, _derive_promotion_reason, _format_delta, _format_history_metadata, _format_metadata_summary, _format_optional_float, _format_top_entries, _humanize_kpi, _promotion_border_style, _safe_format, _trend_from_series.

## `src/townlet_ui/telemetry.py`

**Purpose**: Schema-aware telemetry client utilities for observer UI components.
**Lines of code**: 640
**Dependencies**: stdlib=__future__, collections.abc, dataclasses, typing; external=None; internal=townlet.console.handlers
**Related modules**: townlet.console.handlers

### Classes
- `EmploymentMetrics` — defined at line 51; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - pending: list[str] (public)
    - pending_count: int (public)
    - exits_today: int (public)
    - daily_exit_cap: int (public)
    - queue_limit: int (public)
    - review_window: int (public)
  - Methods: None declared
- `QueueHistoryEntry` — defined at line 61; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - tick: int (public)
    - cooldown_delta: int (public)
    - ghost_step_delta: int (public)
    - rotation_delta: int (public)
    - totals: Mapping[str, int] (public)
  - Methods: None declared
- `RivalryEventEntry` — defined at line 70; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - tick: int (public)
    - agent_a: str (public)
    - agent_b: str (public)
    - intensity: float (public)
    - reason: str (public)
  - Methods: None declared
- `ConflictMetrics` — defined at line 79; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - queue_cooldown_events: int (public)
    - queue_ghost_step_events: int (public)
    - queue_rotation_events: int (public)
    - queue_history: tuple[QueueHistoryEntry, ...] (public)
    - rivalry_agents: int (public)
    - rivalry_events: tuple[RivalryEventEntry, ...] (public)
    - raw: Mapping[str, Any] (public)
  - Methods: None declared
- `NarrationEntry` — defined at line 90; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - tick: int (public)
    - category: str (public)
    - message: str (public)
    - priority: bool (public)
    - data: Mapping[str, Any] (public)
  - Methods: None declared
- `RelationshipChurn` — defined at line 99; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - window_start: int (public)
    - window_end: int (public)
    - total_evictions: int (public)
    - per_owner: Mapping[str, int] (public)
    - per_reason: Mapping[str, int] (public)
  - Methods: None declared
- `RelationshipUpdate` — defined at line 108; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - owner: str (public)
    - other: str (public)
    - status: str (public)
    - trust: float (public)
    - familiarity: float (public)
    - rivalry: float (public)
    - delta_trust: float (public)
    - delta_familiarity: float (public)
    - delta_rivalry: float (public)
  - Methods: None declared
- `AgentSummary` — defined at line 121; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - agent_id: str (public)
    - wallet: float (public)
    - shift_state: str (public)
    - attendance_ratio: float (public)
    - wages_withheld: float (public)
    - lateness_counter: int (public)
    - on_shift: bool (public)
  - Methods: None declared
- `RelationshipOverlayEntry` — defined at line 132; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - other: str (public)
    - trust: float (public)
    - familiarity: float (public)
    - rivalry: float (public)
    - delta_trust: float (public)
    - delta_familiarity: float (public)
    - delta_rivalry: float (public)
  - Methods: None declared
- `PolicyInspectorAction` — defined at line 143; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - action: str (public)
    - probability: float (public)
  - Methods: None declared
- `PolicyInspectorEntry` — defined at line 149; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - agent_id: str (public)
    - tick: int (public)
    - selected_action: str (public)
    - log_prob: float (public)
    - value_pred: float (public)
    - top_actions: list[PolicyInspectorAction] (public)
  - Methods: None declared
- `AnnealStatus` — defined at line 159; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - stage: str (public)
    - cycle: float | None (public)
    - dataset: str (public)
    - bc_accuracy: float | None (public)
    - bc_threshold: float | None (public)
    - bc_passed: bool (public)
    - loss_flag: bool (public)
    - queue_flag: bool (public)
    - intensity_flag: bool (public)
    - loss_baseline: float | None (public)
    - queue_baseline: float | None (public)
    - intensity_baseline: float | None (public)
  - Methods: None declared
- `TransportStatus` — defined at line 175; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - connected: bool (public)
    - dropped_messages: int (public)
    - last_error: str | None (public)
    - last_success_tick: int | None (public)
    - last_failure_tick: int | None (public)
  - Methods: None declared
- `StabilitySnapshot` — defined at line 184; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - alerts: tuple[str, ...] (public)
    - metrics: Mapping[str, Any] (public)
  - Methods: None declared
- `PromotionSnapshot` — defined at line 190; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - state: str | None (public)
    - pass_streak: int (public)
    - required_passes: int (public)
    - candidate_ready: bool (public)
    - candidate_ready_tick: int | None (public)
    - last_result: str | None (public)
    - last_evaluated_tick: int | None (public)
    - candidate_metadata: Mapping[str, Any] | None (public)
    - current_release: Mapping[str, Any] | None (public)
    - history: tuple[Mapping[str, Any], ...] (public)
  - Methods: None declared
- `TelemetrySnapshot` — defined at line 204; decorators: dataclass(frozen=True)
  - Docstring: No class docstring provided.
  - Attributes:
    - schema_version: str (public)
    - schema_warning: str | None (public)
    - employment: EmploymentMetrics (public)
    - conflict: ConflictMetrics (public)
    - narrations: list[NarrationEntry] (public)
    - narration_state: Mapping[str, Any] (public)
    - relationships: RelationshipChurn | None (public)
    - relationship_snapshot: Mapping[str, Mapping[str, Mapping[str, float]]] (public)
    - relationship_updates: list[RelationshipUpdate] (public)
    - relationship_overlay: Mapping[str, list[RelationshipOverlayEntry]] (public)
    - agents: list[AgentSummary] (public)
    - anneal: AnnealStatus | None (public)
    - policy_inspector: list[PolicyInspectorEntry] (public)
    - promotion: PromotionSnapshot | None (public)
    - stability: StabilitySnapshot (public)
    - kpis: Mapping[str, list[float]] (public)
    - transport: TransportStatus (public)
    - raw: Mapping[str, Any] (public)
  - Methods: None declared
- `SchemaMismatchError` (inherits RuntimeError) — defined at line 225
  - Docstring: Raised when telemetry schema is newer than the client supports.
  - Methods: None declared
- `TelemetryClient` — defined at line 229
  - Docstring: Lightweight helper to parse telemetry payloads for the observer UI.
  - Methods:
    - `__init__(self, *, expected_schema_prefix: str = SUPPORTED_SCHEMA_PREFIX) -> None` — No docstring provided.
    - `parse_snapshot(self, payload: Mapping[str, Any]) -> TelemetrySnapshot` — Validate and convert a telemetry payload into dataclasses.
    - `from_console(self, router: Any) -> TelemetrySnapshot` — Fetch snapshot via console router (expects telemetry_snapshot command).
    - `_check_schema(self, version: str) -> str | None` — No docstring provided.
    - `_get_section(payload: Mapping[str, Any], key: str, expected: type) -> Mapping[str, Any]` — No docstring provided.

### Functions
- `_maybe_float(value: object) -> float | None` — No docstring provided.
- `_coerce_float(value: object, default: float = 0.0) -> float` — No docstring provided.
- `_coerce_mapping(value: object) -> Mapping[str, Any] | None` — No docstring provided.
- `_coerce_history_entries(value: object) -> tuple[Mapping[str, Any], ...]` — No docstring provided.
- `_console_command(name: str) -> Any` — Helper to build console command dataclass without importing CLI package.

### Constants and Configuration
- `SUPPORTED_SCHEMA_PREFIX = '0.9'`

### Data Flow
- Inputs: default, expected, expected_schema_prefix, key, name, payload, router, value, version
- Processing: Orchestrated via classes AgentSummary, AnnealStatus, ConflictMetrics, EmploymentMetrics, NarrationEntry, PolicyInspectorAction, PolicyInspectorEntry, PromotionSnapshot, QueueHistoryEntry, RelationshipChurn, RelationshipOverlayEntry, RelationshipUpdate, RivalryEventEntry, SchemaMismatchError, StabilitySnapshot, TelemetryClient, TelemetrySnapshot, TransportStatus and functions _coerce_float, _coerce_history_entries, _coerce_mapping, _console_command, _maybe_float.
- Outputs: Any, Mapping[str, Any], Mapping[str, Any] | None, None, TelemetrySnapshot, float, float | None, str | None, tuple[Mapping[str, Any], ...]
- Downstream modules: townlet.console.handlers

### Integration Points
- External libraries: None
- Internal packages: townlet.console.handlers

### Code Quality Notes
- Functions without docstrings: _coerce_float, _coerce_history_entries, _coerce_mapping, _maybe_float.
- Methods without docstrings: TelemetryClient._check_schema, TelemetryClient._get_section.
- Uses dataclasses for structured state.

## `tests/conftest.py`

**Purpose**: Pytest configuration ensuring project imports resolve during tests.
**Lines of code**: 13
**Dependencies**: stdlib=__future__, pathlib; external=sys; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- `ROOT = Path(__file__).resolve().parents[1]`
- `SRC = ROOT / 'src'`

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions None.
- Outputs: None
- Downstream modules: None

### Integration Points
- External libraries: sys

### Code Quality Notes
- No immediate code quality concerns detected from static scan.

## `tests/test_affordance_hooks.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 195
**Dependencies**: stdlib=__future__, pathlib; external=None; internal=townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `make_world() -> tuple[SimulationLoop, WorldState]` — No docstring provided.
- `request_object(world, object_id: str, agent_id: str) -> None` — No docstring provided.
- `test_affordance_before_after_hooks_fire_once() -> None` — No docstring provided.
- `test_affordance_fail_hook_runs_once_per_failure() -> None` — No docstring provided.
- `test_shower_requires_power() -> None` — No docstring provided.
- `test_shower_completion_emits_event() -> None` — No docstring provided.
- `test_sleep_slots_cycle_and_completion_event() -> None` — No docstring provided.
- `test_sleep_attempt_fails_when_no_slots() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, object_id, world
- Processing: Orchestrated via classes None and functions make_world, request_object, test_affordance_before_after_hooks_fire_once, test_affordance_fail_hook_runs_once_per_failure, test_shower_completion_emits_event, test_shower_requires_power, test_sleep_attempt_fails_when_no_slots, test_sleep_slots_cycle_and_completion_event.
- Outputs: None, tuple[SimulationLoop, WorldState]
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_world, request_object, test_affordance_before_after_hooks_fire_once, test_affordance_fail_hook_runs_once_per_failure, test_shower_completion_emits_event, test_shower_requires_power, test_sleep_attempt_fails_when_no_slots, test_sleep_slots_cycle_and_completion_event.

## `tests/test_affordance_manifest.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 114
**Dependencies**: stdlib=__future__, hashlib, pathlib; external=pytest; internal=townlet.config, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None

### Functions
- `_configure_with_manifest(manifest_path: Path) -> SimulationConfig` — No docstring provided.
- `test_affordance_manifest_loads_and_exposes_metadata(tmp_path: Path) -> None` — No docstring provided.
- `test_affordance_manifest_duplicate_ids_fail(tmp_path: Path) -> None` — No docstring provided.
- `test_affordance_manifest_missing_duration_fails(tmp_path: Path) -> None` — No docstring provided.
- `test_affordance_manifest_checksum_exposed_in_telemetry(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: manifest_path, tmp_path
- Processing: Orchestrated via classes None and functions _configure_with_manifest, test_affordance_manifest_checksum_exposed_in_telemetry, test_affordance_manifest_duplicate_ids_fail, test_affordance_manifest_loads_and_exposes_metadata, test_affordance_manifest_missing_duration_fails.
- Outputs: None, SimulationConfig
- Downstream modules: townlet.config, townlet.telemetry.publisher, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _configure_with_manifest, test_affordance_manifest_checksum_exposed_in_telemetry, test_affordance_manifest_duplicate_ids_fail, test_affordance_manifest_loads_and_exposes_metadata, test_affordance_manifest_missing_duration_fails.

## `tests/test_affordance_preconditions.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 120
**Dependencies**: stdlib=__future__, pathlib; external=pytest; internal=townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet.world.preconditions
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet.world.preconditions

### Classes
- None

### Functions
- `_make_loop() -> tuple[SimulationLoop, object]` — No docstring provided.
- `_request_object(world, object_id: str, agent_id: str) -> None` — No docstring provided.
- `test_compile_preconditions_normalises_booleans() -> None` — No docstring provided.
- `test_compile_preconditions_rejects_function_calls() -> None` — No docstring provided.
- `test_evaluate_preconditions_supports_nested_attributes() -> None` — No docstring provided.
- `test_precondition_failure_blocks_affordance_and_emits_event() -> None` — No docstring provided.
- `test_precondition_success_allows_affordance_start() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, object_id, world
- Processing: Orchestrated via classes None and functions _make_loop, _request_object, test_compile_preconditions_normalises_booleans, test_compile_preconditions_rejects_function_calls, test_evaluate_preconditions_supports_nested_attributes, test_precondition_failure_blocks_affordance_and_emits_event, test_precondition_success_allows_affordance_start.
- Outputs: None, tuple[SimulationLoop, object]
- Downstream modules: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet.world.preconditions

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet.world.preconditions

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_loop, _request_object, test_compile_preconditions_normalises_booleans, test_compile_preconditions_rejects_function_calls, test_evaluate_preconditions_supports_nested_attributes, test_precondition_failure_blocks_affordance_and_emits_event, test_precondition_success_allows_affordance_start.

## `tests/test_basket_telemetry.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 32
**Dependencies**: stdlib=pathlib; external=None; internal=townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `test_basket_cost_in_telemetry_snapshot() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_basket_cost_in_telemetry_snapshot.
- Outputs: None
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_basket_cost_in_telemetry_snapshot.

## `tests/test_bc_capture_prototype.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 64
**Dependencies**: stdlib=__future__, json, pathlib; external=numpy; internal=townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- None

### Functions
- `test_synthetic_bc_capture_round_trip(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_synthetic_bc_capture_round_trip.
- Outputs: None
- Downstream modules: townlet.policy.replay

### Integration Points
- External libraries: numpy
- Internal packages: townlet.policy.replay

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_synthetic_bc_capture_round_trip.

## `tests/test_bc_trainer.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 81
**Dependencies**: stdlib=__future__, pathlib; external=numpy, pytest; internal=townlet.policy, townlet.policy.models, townlet.policy.replay
**Related modules**: townlet.policy, townlet.policy.models, townlet.policy.replay

### Classes
- None

### Functions
- `test_bc_trainer_overfits_toy_dataset(tmp_path: Path) -> None` — No docstring provided.
- `test_bc_evaluate_accuracy(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_bc_evaluate_accuracy, test_bc_trainer_overfits_toy_dataset.
- Outputs: None
- Downstream modules: townlet.policy, townlet.policy.models, townlet.policy.replay

### Integration Points
- External libraries: numpy, pytest
- Internal packages: townlet.policy, townlet.policy.models, townlet.policy.replay

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_bc_evaluate_accuracy, test_bc_trainer_overfits_toy_dataset.

## `tests/test_behavior_rivalry.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 69
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.policy.behavior, townlet.world.grid
**Related modules**: townlet.config, townlet.policy.behavior, townlet.world.grid

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring provided.
- `test_scripted_behavior_avoids_queue_with_rival() -> None` — No docstring provided.
- `test_scripted_behavior_requests_when_no_rival() -> None` — No docstring provided.
- `test_behavior_retries_after_rival_leaves() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions _make_world, test_behavior_retries_after_rival_leaves, test_scripted_behavior_avoids_queue_with_rival, test_scripted_behavior_requests_when_no_rival.
- Outputs: None, WorldState
- Downstream modules: townlet.config, townlet.policy.behavior, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.policy.behavior, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_world, test_behavior_retries_after_rival_leaves, test_scripted_behavior_avoids_queue_with_rival, test_scripted_behavior_requests_when_no_rival.

## `tests/test_capture_scripted_cli.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 39
**Dependencies**: stdlib=json, pathlib; external=runpy; internal=townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- None

### Functions
- `test_capture_scripted_idle(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_capture_scripted_idle.
- Outputs: None
- Downstream modules: townlet.policy.replay

### Integration Points
- External libraries: runpy
- Internal packages: townlet.policy.replay

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_capture_scripted_idle.

## `tests/test_cli_validate_affordances.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 95
**Dependencies**: stdlib=__future__, pathlib; external=subprocess, sys; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `_run(*args: str) -> subprocess.CompletedProcess[str]` — No docstring provided.
- `test_validate_affordances_cli_success(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_affordances_cli_failure(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_affordances_cli_bad_precondition(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_affordances_cli_directory(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `SCRIPT = Path('scripts/validate_affordances.py').resolve()`

### Data Flow
- Inputs: args, tmp_path
- Processing: Orchestrated via classes None and functions _run, test_validate_affordances_cli_bad_precondition, test_validate_affordances_cli_directory, test_validate_affordances_cli_failure, test_validate_affordances_cli_success.
- Outputs: None, subprocess.CompletedProcess[str]
- Downstream modules: None

### Integration Points
- External libraries: subprocess, sys

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _run, test_validate_affordances_cli_bad_precondition, test_validate_affordances_cli_directory, test_validate_affordances_cli_failure, test_validate_affordances_cli_success.

## `tests/test_config_loader.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 259
**Dependencies**: stdlib=pathlib; external=pytest, sys, types, yaml; internal=townlet.config, townlet.snapshots.migrations
**Related modules**: townlet.config, townlet.snapshots.migrations

### Classes
- None

### Functions
- `poc_config(tmp_path: Path) -> Path` — No docstring provided.
- `test_load_config(poc_config: Path) -> None` — No docstring provided.
- `test_invalid_queue_cooldown_rejected(tmp_path: Path) -> None` — No docstring provided.
- `test_invalid_embedding_threshold_rejected(tmp_path: Path) -> None` — No docstring provided.
- `test_invalid_embedding_slot_count(tmp_path: Path) -> None` — No docstring provided.
- `test_invalid_affordance_file_absent(tmp_path: Path) -> None` — No docstring provided.
- `test_observation_variant_guard(tmp_path: Path) -> None` — No docstring provided.
- `test_ppo_config_defaults_roundtrip(tmp_path: Path) -> None` — No docstring provided.
- `test_observation_variant_full_supported(tmp_path: Path) -> None` — No docstring provided.
- `test_observation_variant_compact_supported(tmp_path: Path) -> None` — No docstring provided.
- `test_snapshot_autosave_cadence_validation(tmp_path: Path) -> None` — No docstring provided.
- `test_snapshot_identity_overrides_take_precedence(poc_config: Path) -> None` — No docstring provided.
- `test_register_snapshot_migrations_from_config(poc_config: Path) -> None` — No docstring provided.
- `test_telemetry_transport_defaults(poc_config: Path) -> None` — No docstring provided.
- `test_telemetry_file_transport_requires_path(tmp_path: Path) -> None` — No docstring provided.
- `test_telemetry_tcp_transport_requires_endpoint(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: poc_config, tmp_path
- Processing: Orchestrated via classes None and functions poc_config, test_invalid_affordance_file_absent, test_invalid_embedding_slot_count, test_invalid_embedding_threshold_rejected, test_invalid_queue_cooldown_rejected, test_load_config, test_observation_variant_compact_supported, test_observation_variant_full_supported, test_observation_variant_guard, test_ppo_config_defaults_roundtrip, test_register_snapshot_migrations_from_config, test_snapshot_autosave_cadence_validation, test_snapshot_identity_overrides_take_precedence, test_telemetry_file_transport_requires_path, test_telemetry_tcp_transport_requires_endpoint, test_telemetry_transport_defaults.
- Outputs: None, Path
- Downstream modules: townlet.config, townlet.snapshots.migrations

### Integration Points
- External libraries: pytest, sys, types, yaml
- Internal packages: townlet.config, townlet.snapshots.migrations

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: poc_config, test_invalid_affordance_file_absent, test_invalid_embedding_slot_count, test_invalid_embedding_threshold_rejected, test_invalid_queue_cooldown_rejected, test_load_config, test_observation_variant_compact_supported, test_observation_variant_full_supported, test_observation_variant_guard, test_ppo_config_defaults_roundtrip, test_register_snapshot_migrations_from_config, test_snapshot_autosave_cadence_validation, test_snapshot_identity_overrides_take_precedence, test_telemetry_file_transport_requires_path, test_telemetry_tcp_transport_requires_endpoint, test_telemetry_transport_defaults.

## `tests/test_conflict_scenarios.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 89
**Dependencies**: stdlib=__future__, pathlib, random; external=pytest, types; internal=townlet.config.loader, townlet.core.sim_loop, townlet.policy.scenario_utils, townlet.world.queue_manager
**Related modules**: townlet.config.loader, townlet.core.sim_loop, townlet.policy.scenario_utils, townlet.world.queue_manager

### Classes
- None

### Functions
- `_run_scenario(config_path: str, ticks: int) -> SimulationLoop` — No docstring provided.
- `test_queue_conflict_scenario_produces_alerts() -> None` — No docstring provided.
- `test_rivalry_decay_scenario_tracks_events() -> None` — No docstring provided.
- `test_queue_manager_randomised_regression(seed: int) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: config_path, seed, ticks
- Processing: Orchestrated via classes None and functions _run_scenario, test_queue_conflict_scenario_produces_alerts, test_queue_manager_randomised_regression, test_rivalry_decay_scenario_tracks_events.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config.loader, townlet.core.sim_loop, townlet.policy.scenario_utils, townlet.world.queue_manager

### Integration Points
- External libraries: pytest, types
- Internal packages: townlet.config.loader, townlet.core.sim_loop, townlet.policy.scenario_utils, townlet.world.queue_manager

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _run_scenario, test_queue_conflict_scenario_produces_alerts, test_queue_manager_randomised_regression, test_rivalry_decay_scenario_tracks_events.

## `tests/test_conflict_telemetry.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 125
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None

### Functions
- `test_conflict_snapshot_reports_rivalry_counts() -> None` — No docstring provided.
- `test_replay_sample_matches_schema(tmp_path: Path) -> None` — No docstring provided.
- `test_conflict_export_import_preserves_history() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_conflict_export_import_preserves_history, test_conflict_snapshot_reports_rivalry_counts, test_replay_sample_matches_schema.
- Outputs: None
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_conflict_export_import_preserves_history, test_conflict_snapshot_reports_rivalry_counts, test_replay_sample_matches_schema.

## `tests/test_console_commands.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 439
**Dependencies**: stdlib=dataclasses, pathlib; external=None; internal=townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.migrations, townlet.snapshots.state, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.migrations, townlet.snapshots.state, townlet.world.grid

### Classes
- None

### Functions
- `test_console_telemetry_snapshot_returns_payload() -> None` — No docstring provided.
- `test_console_conflict_status_reports_history() -> None` — No docstring provided.
- `test_console_queue_inspect_returns_queue_details() -> None` — No docstring provided.
- `test_console_set_spawn_delay_updates_lifecycle() -> None` — No docstring provided.
- `test_console_rivalry_dump_reports_pairs() -> None` — No docstring provided.
- `test_employment_console_commands_manage_queue() -> None` — No docstring provided.
- `test_console_schema_warning_for_newer_version() -> None` — No docstring provided.
- `test_console_perturbation_requires_admin_mode() -> None` — No docstring provided.
- `test_console_perturbation_commands_schedule_and_cancel() -> None` — No docstring provided.
- `test_console_arrange_meet_schedules_event() -> None` — No docstring provided.
- `test_console_arrange_meet_unknown_spec_returns_error() -> None` — No docstring provided.
- `test_console_snapshot_commands(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_console_arrange_meet_schedules_event, test_console_arrange_meet_unknown_spec_returns_error, test_console_conflict_status_reports_history, test_console_perturbation_commands_schedule_and_cancel, test_console_perturbation_requires_admin_mode, test_console_queue_inspect_returns_queue_details, test_console_rivalry_dump_reports_pairs, test_console_schema_warning_for_newer_version, test_console_set_spawn_delay_updates_lifecycle, test_console_snapshot_commands, test_console_telemetry_snapshot_returns_payload, test_employment_console_commands_manage_queue.
- Outputs: None
- Downstream modules: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.migrations, townlet.snapshots.state, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.migrations, townlet.snapshots.state, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_console_arrange_meet_schedules_event, test_console_arrange_meet_unknown_spec_returns_error, test_console_conflict_status_reports_history, test_console_perturbation_commands_schedule_and_cancel, test_console_perturbation_requires_admin_mode, test_console_queue_inspect_returns_queue_details, test_console_rivalry_dump_reports_pairs, test_console_schema_warning_for_newer_version, test_console_set_spawn_delay_updates_lifecycle, test_console_snapshot_commands, test_console_telemetry_snapshot_returns_payload, test_employment_console_commands_manage_queue.

## `tests/test_console_dispatcher.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 482
**Dependencies**: stdlib=__future__, pathlib; external=pytest; internal=townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `employment_loop() -> SimulationLoop` — No docstring provided.
- `_queue_command(loop: SimulationLoop, payload: dict[str, object]) -> None` — No docstring provided.
- `test_dispatcher_processes_employment_review(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_dispatcher_idempotency_reuses_history(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_dispatcher_requires_admin_mode(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_dispatcher_enforces_cmd_id_for_destructive_ops(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_spawn_command_creates_agent(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_spawn_rejects_duplicate_id(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_teleport_moves_agent(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_teleport_rejects_blocked_tile(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_setneed_updates_needs(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_setneed_rejects_unknown_need(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_price_updates_economy_and_basket(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_price_rejects_unknown_key(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_force_chat_updates_relationship(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_force_chat_requires_distinct_agents(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_set_rel_updates_ties(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_possess_acquire_and_release(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_possess_errors_on_duplicate_or_missing(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_kill_command_removes_agent(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_toggle_mortality_updates_flag(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_set_exit_cap_updates_config(employment_loop: SimulationLoop) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: employment_loop, loop, payload
- Processing: Orchestrated via classes None and functions _queue_command, employment_loop, test_dispatcher_enforces_cmd_id_for_destructive_ops, test_dispatcher_idempotency_reuses_history, test_dispatcher_processes_employment_review, test_dispatcher_requires_admin_mode, test_force_chat_requires_distinct_agents, test_force_chat_updates_relationship, test_kill_command_removes_agent, test_possess_acquire_and_release, test_possess_errors_on_duplicate_or_missing, test_price_rejects_unknown_key, test_price_updates_economy_and_basket, test_set_exit_cap_updates_config, test_set_rel_updates_ties, test_setneed_rejects_unknown_need, test_setneed_updates_needs, test_spawn_command_creates_agent, test_spawn_rejects_duplicate_id, test_teleport_moves_agent, test_teleport_rejects_blocked_tile, test_toggle_mortality_updates_flag.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _queue_command, employment_loop, test_dispatcher_enforces_cmd_id_for_destructive_ops, test_dispatcher_idempotency_reuses_history, test_dispatcher_processes_employment_review, test_dispatcher_requires_admin_mode, test_force_chat_requires_distinct_agents, test_force_chat_updates_relationship, test_kill_command_removes_agent, test_possess_acquire_and_release, test_possess_errors_on_duplicate_or_missing, test_price_rejects_unknown_key, test_price_updates_economy_and_basket, test_set_exit_cap_updates_config, test_set_rel_updates_ties, test_setneed_rejects_unknown_need, test_setneed_updates_needs, test_spawn_command_creates_agent, test_spawn_rejects_duplicate_id, test_teleport_moves_agent, test_teleport_rejects_blocked_tile, test_toggle_mortality_updates_flag.

## `tests/test_console_events.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 40
**Dependencies**: stdlib=pathlib; external=None; internal=townlet.config, townlet.console.handlers, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None

### Functions
- `test_event_stream_receives_published_events() -> None` — No docstring provided.
- `test_event_stream_handles_empty_batch() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_event_stream_handles_empty_batch, test_event_stream_receives_published_events.
- Outputs: None
- Downstream modules: townlet.config, townlet.console.handlers, townlet.telemetry.publisher, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.console.handlers, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_event_stream_handles_empty_batch, test_event_stream_receives_published_events.

## `tests/test_console_promotion.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 136
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.console.handlers, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Classes
- None

### Functions
- `admin_router() -> tuple[SimulationLoop, object]` — No docstring provided.
- `make_ready(loop: SimulationLoop) -> None` — No docstring provided.
- `test_promotion_status_command(admin_router: tuple[SimulationLoop, object]) -> None` — No docstring provided.
- `test_promote_and_rollback_commands(admin_router: tuple[SimulationLoop, object]) -> None` — No docstring provided.
- `test_policy_swap_command(admin_router: tuple[SimulationLoop, object], tmp_path: Path) -> None` — No docstring provided.
- `test_policy_swap_missing_file(admin_router: tuple[SimulationLoop, object]) -> None` — No docstring provided.
- `viewer_router() -> object` — No docstring provided.
- `test_viewer_mode_forbidden(viewer_router: object) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: admin_router, loop, tmp_path, viewer_router
- Processing: Orchestrated via classes None and functions admin_router, make_ready, test_policy_swap_command, test_policy_swap_missing_file, test_promote_and_rollback_commands, test_promotion_status_command, test_viewer_mode_forbidden, viewer_router.
- Outputs: None, object, tuple[SimulationLoop, object]
- Downstream modules: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: admin_router, make_ready, test_policy_swap_command, test_policy_swap_missing_file, test_promote_and_rollback_commands, test_promotion_status_command, test_viewer_mode_forbidden, viewer_router.

## `tests/test_curate_trajectories.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 81
**Dependencies**: stdlib=__future__, json, pathlib; external=numpy, runpy; internal=townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- None

### Functions
- `_write_sample(output_dir: Path, stem: str, rewards: np.ndarray, timesteps: int) -> None` — No docstring provided.
- `test_curate_trajectories(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: output_dir, rewards, stem, timesteps, tmp_path
- Processing: Orchestrated via classes None and functions _write_sample, test_curate_trajectories.
- Outputs: None
- Downstream modules: townlet.policy.replay

### Integration Points
- External libraries: numpy, runpy
- Internal packages: townlet.policy.replay

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _write_sample, test_curate_trajectories.

## `tests/test_embedding_allocator.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 142
**Dependencies**: stdlib=pathlib; external=None; internal=townlet.config, townlet.observations.builder, townlet.observations.embedding, townlet.stability.monitor, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.observations.builder, townlet.observations.embedding, townlet.stability.monitor, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None

### Functions
- `make_allocator(*, cooldown: int = 5, max_slots: int = 2) -> EmbeddingAllocator` — No docstring provided.
- `test_allocate_reuses_slot_after_cooldown() -> None` — No docstring provided.
- `test_allocator_respects_multiple_slots() -> None` — No docstring provided.
- `test_observation_builder_releases_on_termination() -> None` — No docstring provided.
- `test_telemetry_exposes_allocator_metrics() -> None` — No docstring provided.
- `test_stability_monitor_sets_alert_on_warning() -> None` — No docstring provided.
- `test_telemetry_records_events() -> None` — No docstring provided.
- `test_stability_alerts_on_affordance_failures() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: cooldown, max_slots
- Processing: Orchestrated via classes None and functions make_allocator, test_allocate_reuses_slot_after_cooldown, test_allocator_respects_multiple_slots, test_observation_builder_releases_on_termination, test_stability_alerts_on_affordance_failures, test_stability_monitor_sets_alert_on_warning, test_telemetry_exposes_allocator_metrics, test_telemetry_records_events.
- Outputs: EmbeddingAllocator, None
- Downstream modules: townlet.config, townlet.observations.builder, townlet.observations.embedding, townlet.stability.monitor, townlet.telemetry.publisher, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.observations.builder, townlet.observations.embedding, townlet.stability.monitor, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_allocator, test_allocate_reuses_slot_after_cooldown, test_allocator_respects_multiple_slots, test_observation_builder_releases_on_termination, test_stability_alerts_on_affordance_failures, test_stability_monitor_sets_alert_on_warning, test_telemetry_exposes_allocator_metrics, test_telemetry_records_events.

## `tests/test_employment_loop.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 120
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `make_loop_with_employment() -> SimulationLoop` — No docstring provided.
- `advance_ticks(loop: SimulationLoop, ticks: int) -> None` — No docstring provided.
- `test_on_time_shift_records_attendance() -> None` — No docstring provided.
- `test_late_arrival_accumulates_wages_withheld() -> None` — No docstring provided.
- `test_employment_exit_queue_respects_cap_and_manual_override() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: loop, ticks
- Processing: Orchestrated via classes None and functions advance_ticks, make_loop_with_employment, test_employment_exit_queue_respects_cap_and_manual_override, test_late_arrival_accumulates_wages_withheld, test_on_time_shift_records_attendance.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: advance_ticks, make_loop_with_employment, test_employment_exit_queue_respects_cap_and_manual_override, test_late_arrival_accumulates_wages_withheld, test_on_time_shift_records_attendance.

## `tests/test_lifecycle_manager.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 89
**Dependencies**: stdlib=__future__, pathlib; external=None; internal=townlet.config, townlet.lifecycle.manager, townlet.world.grid
**Related modules**: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Classes
- None

### Functions
- `_make_world(respawn_delay: int = 0) -> tuple[LifecycleManager, WorldState]` — No docstring provided.
- `_spawn_agent(world: WorldState, agent_id: str = 'alice') -> AgentSnapshot` — No docstring provided.
- `test_respawn_after_delay() -> None` — No docstring provided.
- `test_employment_exit_emits_event_and_resets_state() -> None` — No docstring provided.
- `test_employment_daily_reset() -> None` — No docstring provided.
- `test_termination_reasons_captured() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, respawn_delay, world
- Processing: Orchestrated via classes None and functions _make_world, _spawn_agent, test_employment_daily_reset, test_employment_exit_emits_event_and_resets_state, test_respawn_after_delay, test_termination_reasons_captured.
- Outputs: AgentSnapshot, None, tuple[LifecycleManager, WorldState]
- Downstream modules: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_world, _spawn_agent, test_employment_daily_reset, test_employment_exit_emits_event_and_resets_state, test_respawn_after_delay, test_termination_reasons_captured.

## `tests/test_need_decay.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 89
**Dependencies**: stdlib=__future__, pathlib; external=pytest; internal=townlet.config, townlet.lifecycle.manager, townlet.world.grid
**Related modules**: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Classes
- None

### Functions
- `_make_world() -> tuple[LifecycleManager, WorldState]` — No docstring provided.
- `_spawn_agent(world: WorldState, *, hunger: float = 0.8, hygiene: float = 0.7, energy: float = 0.6) -> AgentSnapshot` — No docstring provided.
- `test_need_decay_matches_config() -> None` — No docstring provided.
- `test_need_decay_clamps_at_zero() -> None` — No docstring provided.
- `test_lifecycle_hunger_threshold_applies() -> None` — No docstring provided.
- `test_agent_snapshot_clamps_on_init() -> None` — No docstring provided.

### Constants and Configuration
- `CONFIG_PATH = Path('configs/examples/poc_hybrid.yaml')`

### Data Flow
- Inputs: energy, hunger, hygiene, world
- Processing: Orchestrated via classes None and functions _make_world, _spawn_agent, test_agent_snapshot_clamps_on_init, test_lifecycle_hunger_threshold_applies, test_need_decay_clamps_at_zero, test_need_decay_matches_config.
- Outputs: AgentSnapshot, None, tuple[LifecycleManager, WorldState]
- Downstream modules: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_world, _spawn_agent, test_agent_snapshot_clamps_on_init, test_lifecycle_hunger_threshold_applies, test_need_decay_clamps_at_zero, test_need_decay_matches_config.

## `tests/test_observation_builder.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 194
**Dependencies**: stdlib=pathlib; external=numpy; internal=townlet.config, townlet.console.command, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid
**Related modules**: townlet.config, townlet.console.command, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Classes
- None

### Functions
- `make_world(enforce_job_loop: bool = False) -> SimulationLoop` — No docstring provided.
- `test_observation_builder_hybrid_map_and_features() -> None` — No docstring provided.
- `test_observation_ctx_reset_releases_slot() -> None` — No docstring provided.
- `test_observation_rivalry_features_reflect_conflict() -> None` — No docstring provided.
- `test_observation_queue_and_reservation_flags() -> None` — No docstring provided.
- `test_observation_respawn_resets_features() -> None` — No docstring provided.
- `test_ctx_reset_flag_on_teleport_and_possession() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: enforce_job_loop
- Processing: Orchestrated via classes None and functions make_world, test_ctx_reset_flag_on_teleport_and_possession, test_observation_builder_hybrid_map_and_features, test_observation_ctx_reset_releases_slot, test_observation_queue_and_reservation_flags, test_observation_respawn_resets_features, test_observation_rivalry_features_reflect_conflict.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.console.command, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Integration Points
- External libraries: numpy
- Internal packages: townlet.config, townlet.console.command, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_world, test_ctx_reset_flag_on_teleport_and_possession, test_observation_builder_hybrid_map_and_features, test_observation_ctx_reset_releases_slot, test_observation_queue_and_reservation_flags, test_observation_respawn_resets_features, test_observation_rivalry_features_reflect_conflict.

## `tests/test_observation_builder_compact.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 63
**Dependencies**: stdlib=__future__, pathlib; external=numpy; internal=townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Classes
- None

### Functions
- `make_compact_world() -> SimulationLoop` — No docstring provided.
- `test_compact_observation_features_only() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions make_compact_world, test_compact_observation_features_only.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Integration Points
- External libraries: numpy
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_compact_world, test_compact_observation_features_only.

## `tests/test_observation_builder_full.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 83
**Dependencies**: stdlib=__future__, pathlib; external=numpy; internal=townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Classes
- None

### Functions
- `make_full_world() -> SimulationLoop` — No docstring provided.
- `test_full_observation_map_and_features() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions make_full_world, test_full_observation_map_and_features.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Integration Points
- External libraries: numpy
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_full_world, test_full_observation_map_and_features.

## `tests/test_observations_social_snippet.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 95
**Dependencies**: stdlib=__future__, pathlib; external=numpy, pytest; internal=townlet.config, townlet.observations.builder, townlet.world.grid
**Related modules**: townlet.config, townlet.observations.builder, townlet.world.grid

### Classes
- None

### Functions
- `base_config() -> SimulationConfig` — No docstring provided.
- `_build_world(config: SimulationConfig) -> WorldState` — No docstring provided.
- `test_social_snippet_vector_length(base_config: SimulationConfig) -> None` — No docstring provided.
- `test_relationship_stage_required(base_config: SimulationConfig) -> None` — No docstring provided.
- `test_disable_aggregates_via_config(base_config: SimulationConfig) -> None` — No docstring provided.
- `test_observation_matches_golden_fixture(base_config: SimulationConfig) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: base_config, config
- Processing: Orchestrated via classes None and functions _build_world, base_config, test_disable_aggregates_via_config, test_observation_matches_golden_fixture, test_relationship_stage_required, test_social_snippet_vector_length.
- Outputs: None, SimulationConfig, WorldState
- Downstream modules: townlet.config, townlet.observations.builder, townlet.world.grid

### Integration Points
- External libraries: numpy, pytest
- Internal packages: townlet.config, townlet.observations.builder, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _build_world, base_config, test_disable_aggregates_via_config, test_observation_matches_golden_fixture, test_relationship_stage_required, test_social_snippet_vector_length.

## `tests/test_observer_payload.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 53
**Dependencies**: stdlib=pathlib; external=None; internal=townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring provided.
- `test_observer_payload_contains_job_and_economy() -> None` — No docstring provided.
- `test_planning_payload_consistency() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions make_loop, test_observer_payload_contains_job_and_economy, test_planning_payload_consistency.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_loop, test_observer_payload_contains_job_and_economy, test_planning_payload_consistency.

## `tests/test_observer_ui_dashboard.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 276
**Dependencies**: stdlib=dataclasses, pathlib; external=pytest, rich.console; internal=townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.policy.models, townlet.world.grid, townlet_ui.dashboard, townlet_ui.telemetry
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.policy.models, townlet.world.grid, townlet_ui.dashboard, townlet_ui.telemetry

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring provided.
- `test_render_snapshot_produces_panels() -> None` — No docstring provided.
- `test_run_dashboard_advances_loop(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.
- `test_build_map_panel_produces_table() -> None` — No docstring provided.
- `test_narration_panel_shows_styled_categories() -> None` — No docstring provided.
- `test_policy_inspector_snapshot_contains_entries() -> None` — No docstring provided.
- `test_promotion_reason_logic() -> None` — No docstring provided.
- `test_promotion_border_styles() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: monkeypatch
- Processing: Orchestrated via classes None and functions make_loop, test_build_map_panel_produces_table, test_narration_panel_shows_styled_categories, test_policy_inspector_snapshot_contains_entries, test_promotion_border_styles, test_promotion_reason_logic, test_render_snapshot_produces_panels, test_run_dashboard_advances_loop.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.policy.models, townlet.world.grid, townlet_ui.dashboard, townlet_ui.telemetry

### Integration Points
- External libraries: pytest, rich.console
- Internal packages: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.policy.models, townlet.world.grid, townlet_ui.dashboard, townlet_ui.telemetry

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_loop, test_build_map_panel_produces_table, test_narration_panel_shows_styled_categories, test_policy_inspector_snapshot_contains_entries, test_promotion_border_styles, test_promotion_reason_logic, test_render_snapshot_produces_panels, test_run_dashboard_advances_loop.

## `tests/test_observer_ui_executor.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 33
**Dependencies**: stdlib=time; external=None; internal=townlet.console.handlers, townlet_ui.commands
**Related modules**: townlet.console.handlers, townlet_ui.commands

### Classes
- `DummyRouter` — defined at line 7
  - Docstring: No class docstring provided.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `dispatch(self, command: ConsoleCommand) -> None` — No docstring provided.

### Functions
- `test_console_command_executor_dispatches_async() -> None` — No docstring provided.
- `test_console_command_executor_swallow_errors() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: command
- Processing: Orchestrated via classes DummyRouter and functions test_console_command_executor_dispatches_async, test_console_command_executor_swallow_errors.
- Outputs: None
- Downstream modules: townlet.console.handlers, townlet_ui.commands

### Integration Points
- External libraries: None
- Internal packages: townlet.console.handlers, townlet_ui.commands

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_console_command_executor_dispatches_async, test_console_command_executor_swallow_errors.
- Methods without docstrings: DummyRouter.dispatch.

## `tests/test_observer_ui_script.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 22
**Dependencies**: stdlib=pathlib; external=subprocess, sys; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `test_observer_ui_script_runs_single_tick(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_observer_ui_script_runs_single_tick.
- Outputs: None
- Downstream modules: None

### Integration Points
- External libraries: subprocess, sys

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_observer_ui_script_runs_single_tick.

## `tests/test_perturbation_config.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 38
**Dependencies**: stdlib=pathlib; external=None; internal=townlet.config
**Related modules**: townlet.config

### Classes
- None

### Functions
- `test_simulation_config_exposes_perturbations() -> None` — No docstring provided.
- `test_price_spike_event_config_parses_ranges() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_price_spike_event_config_parses_ranges, test_simulation_config_exposes_perturbations.
- Outputs: None
- Downstream modules: townlet.config

### Integration Points
- External libraries: None
- Internal packages: townlet.config

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_price_spike_event_config_parses_ranges, test_simulation_config_exposes_perturbations.

## `tests/test_perturbation_scheduler.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 106
**Dependencies**: stdlib=pathlib; external=None; internal=townlet.config, townlet.scheduler.perturbations, townlet.world.grid
**Related modules**: townlet.config, townlet.scheduler.perturbations, townlet.world.grid

### Classes
- None

### Functions
- `_base_config() -> SimulationConfig` — No docstring provided.
- `test_manual_event_activation_and_expiry() -> None` — No docstring provided.
- `test_auto_scheduling_respects_cooldowns() -> None` — No docstring provided.
- `test_cancel_event_removes_from_active() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions _base_config, test_auto_scheduling_respects_cooldowns, test_cancel_event_removes_from_active, test_manual_event_activation_and_expiry.
- Outputs: None, SimulationConfig
- Downstream modules: townlet.config, townlet.scheduler.perturbations, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.scheduler.perturbations, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _base_config, test_auto_scheduling_respects_cooldowns, test_cancel_event_removes_from_active, test_manual_event_activation_and_expiry.

## `tests/test_policy_anneal_blend.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 155
**Dependencies**: stdlib=pathlib; external=None; internal=townlet.config, townlet.policy.behavior, townlet.policy.runner, townlet.world.grid
**Related modules**: townlet.config, townlet.policy.behavior, townlet.policy.runner, townlet.world.grid

### Classes
- None

### Functions
- `_make_world(option_commit_ticks: int | None = None) -> tuple[PolicyRuntime, WorldState]` — No docstring provided.
- `test_anneal_ratio_uses_provider_when_enabled() -> None` — No docstring provided.
- `test_anneal_ratio_mix_respects_probability() -> None` — No docstring provided.
- `test_blend_disabled_returns_scripted() -> None` — No docstring provided.
- `test_option_commit_blocks_switch_until_expiry() -> None` — No docstring provided.
- `test_option_commit_clears_on_termination() -> None` — No docstring provided.
- `test_option_commit_respects_disabled_setting() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: option_commit_ticks
- Processing: Orchestrated via classes None and functions _make_world, test_anneal_ratio_mix_respects_probability, test_anneal_ratio_uses_provider_when_enabled, test_blend_disabled_returns_scripted, test_option_commit_blocks_switch_until_expiry, test_option_commit_clears_on_termination, test_option_commit_respects_disabled_setting.
- Outputs: None, tuple[PolicyRuntime, WorldState]
- Downstream modules: townlet.config, townlet.policy.behavior, townlet.policy.runner, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.policy.behavior, townlet.policy.runner, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_world, test_anneal_ratio_mix_respects_probability, test_anneal_ratio_uses_provider_when_enabled, test_blend_disabled_returns_scripted, test_option_commit_blocks_switch_until_expiry, test_option_commit_clears_on_termination, test_option_commit_respects_disabled_setting.

## `tests/test_policy_models.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 32
**Dependencies**: stdlib=None; external=pytest, torch; internal=townlet.policy.models
**Related modules**: townlet.policy.models

### Classes
- None

### Functions
- `test_conflict_policy_network_requires_torch_when_unavailable() -> None` — No docstring provided.
- `test_conflict_policy_network_forward() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_conflict_policy_network_forward, test_conflict_policy_network_requires_torch_when_unavailable.
- Outputs: None
- Downstream modules: townlet.policy.models

### Integration Points
- External libraries: pytest, torch
- Internal packages: townlet.policy.models

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_conflict_policy_network_forward, test_conflict_policy_network_requires_torch_when_unavailable.

## `tests/test_policy_rivalry_behavior.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 67
**Dependencies**: stdlib=__future__, pathlib; external=pytest; internal=townlet.config.loader, townlet.policy.behavior, townlet.world.grid
**Related modules**: townlet.config.loader, townlet.policy.behavior, townlet.world.grid

### Classes
- None

### Functions
- `base_config()` — No docstring provided.
- `_build_world(base_config)` — No docstring provided.
- `_occupy(world: WorldState, object_id: str, agent_id: str) -> None` — No docstring provided.
- `test_agents_avoid_rivals_when_rivalry_high(base_config)` — No docstring provided.
- `test_agents_request_again_after_rivalry_decay(base_config)` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, base_config, object_id, world
- Processing: Orchestrated via classes None and functions _build_world, _occupy, base_config, test_agents_avoid_rivals_when_rivalry_high, test_agents_request_again_after_rivalry_decay.
- Outputs: None
- Downstream modules: townlet.config.loader, townlet.policy.behavior, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config.loader, townlet.policy.behavior, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _build_world, _occupy, base_config, test_agents_avoid_rivals_when_rivalry_high, test_agents_request_again_after_rivalry_decay.

## `tests/test_ppo_utils.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 65
**Dependencies**: stdlib=__future__; external=torch; internal=townlet.policy.ppo
**Related modules**: townlet.policy.ppo

### Classes
- None

### Functions
- `test_compute_gae_single_step() -> None` — No docstring provided.
- `test_value_baseline_from_old_preds_handles_bootstrap() -> None` — No docstring provided.
- `test_policy_surrogate_clipping_behaviour() -> None` — No docstring provided.
- `test_clipped_value_loss_respects_clip() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_clipped_value_loss_respects_clip, test_compute_gae_single_step, test_policy_surrogate_clipping_behaviour, test_value_baseline_from_old_preds_handles_bootstrap.
- Outputs: None
- Downstream modules: townlet.policy.ppo

### Integration Points
- External libraries: torch
- Internal packages: townlet.policy.ppo

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_clipped_value_loss_respects_clip, test_compute_gae_single_step, test_policy_surrogate_clipping_behaviour, test_value_baseline_from_old_preds_handles_bootstrap.

## `tests/test_promotion_cli.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 52
**Dependencies**: stdlib=json, pathlib; external=pytest, subprocess, sys; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `write_summary(tmp_path: Path, accuracy: float, threshold: float = 0.9) -> Path` — No docstring provided.
- `test_promotion_cli_pass(tmp_path: Path) -> None` — No docstring provided.
- `test_promotion_cli_fail(tmp_path: Path) -> None` — No docstring provided.
- `test_promotion_drill(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `PYTHON = Path(sys.executable)`
- `SCRIPT = Path('scripts/promotion_evaluate.py')`

### Data Flow
- Inputs: accuracy, threshold, tmp_path
- Processing: Orchestrated via classes None and functions test_promotion_cli_fail, test_promotion_cli_pass, test_promotion_drill, write_summary.
- Outputs: None, Path
- Downstream modules: None

### Integration Points
- External libraries: pytest, subprocess, sys

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_promotion_cli_fail, test_promotion_cli_pass, test_promotion_drill, write_summary.

## `tests/test_promotion_evaluate_cli.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 84
**Dependencies**: stdlib=__future__, json, pathlib; external=subprocess, sys; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `_run(*args: str) -> subprocess.CompletedProcess[str]` — No docstring provided.
- `test_promotion_evaluate_promote(tmp_path: Path) -> None` — No docstring provided.
- `test_promotion_evaluate_hold_flags(tmp_path: Path) -> None` — No docstring provided.
- `test_promotion_evaluate_dry_run(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `SCRIPT = Path('scripts/promotion_evaluate.py').resolve()`

### Data Flow
- Inputs: args, tmp_path
- Processing: Orchestrated via classes None and functions _run, test_promotion_evaluate_dry_run, test_promotion_evaluate_hold_flags, test_promotion_evaluate_promote.
- Outputs: None, subprocess.CompletedProcess[str]
- Downstream modules: None

### Integration Points
- External libraries: subprocess, sys

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _run, test_promotion_evaluate_dry_run, test_promotion_evaluate_hold_flags, test_promotion_evaluate_promote.

## `tests/test_promotion_manager.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 110
**Dependencies**: stdlib=json, pathlib; external=None; internal=townlet.config, townlet.stability.promotion
**Related modules**: townlet.config, townlet.stability.promotion

### Classes
- None

### Functions
- `make_manager(log_path: Path | None = None) -> PromotionManager` — No docstring provided.
- `promotion_metrics(pass_streak: int, required: int, ready: bool, last_result: str | None = None, last_tick: int | None = None) -> dict[str, object]` — No docstring provided.
- `test_promotion_state_transitions() -> None` — No docstring provided.
- `test_promotion_manager_export_import() -> None` — No docstring provided.
- `test_mark_promoted_and_rollback() -> None` — No docstring provided.
- `test_rollback_without_metadata_reverts_to_initial() -> None` — No docstring provided.
- `test_promotion_log_written(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: last_result, last_tick, log_path, pass_streak, ready, required, tmp_path
- Processing: Orchestrated via classes None and functions make_manager, promotion_metrics, test_mark_promoted_and_rollback, test_promotion_log_written, test_promotion_manager_export_import, test_promotion_state_transitions, test_rollback_without_metadata_reverts_to_initial.
- Outputs: None, PromotionManager, dict[str, object]
- Downstream modules: townlet.config, townlet.stability.promotion

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.stability.promotion

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_manager, promotion_metrics, test_mark_promoted_and_rollback, test_promotion_log_written, test_promotion_manager_export_import, test_promotion_state_transitions, test_rollback_without_metadata_reverts_to_initial.

## `tests/test_queue_fairness.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 89
**Dependencies**: stdlib=__future__, pathlib; external=pytest; internal=townlet.config, townlet.world.queue_manager
**Related modules**: townlet.config, townlet.world.queue_manager

### Classes
- None

### Functions
- `_make_queue_manager() -> QueueManager` — No docstring provided.
- `test_cooldown_blocks_repeat_entry_and_tracks_metric() -> None` — No docstring provided.
- `test_ghost_step_promotes_waiter_after_blockages(ghost_limit: int) -> None` — No docstring provided.
- `test_queue_snapshot_reflects_waiting_order() -> None` — No docstring provided.
- `test_queue_performance_metrics_accumulate_time() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: ghost_limit
- Processing: Orchestrated via classes None and functions _make_queue_manager, test_cooldown_blocks_repeat_entry_and_tracks_metric, test_ghost_step_promotes_waiter_after_blockages, test_queue_performance_metrics_accumulate_time, test_queue_snapshot_reflects_waiting_order.
- Outputs: None, QueueManager
- Downstream modules: townlet.config, townlet.world.queue_manager

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.world.queue_manager

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_queue_manager, test_cooldown_blocks_repeat_entry_and_tracks_metric, test_ghost_step_promotes_waiter_after_blockages, test_queue_performance_metrics_accumulate_time, test_queue_snapshot_reflects_waiting_order.

## `tests/test_queue_manager.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 92
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.world.queue_manager
**Related modules**: townlet.config, townlet.world.queue_manager

### Classes
- None

### Functions
- `queue_manager() -> QueueManager` — No docstring provided.
- `test_queue_cooldown_enforced(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_queue_prioritises_wait_time(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_ghost_step_trigger(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_requeue_to_tail_rotates_agent(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_record_blocked_attempt_counts_and_triggers(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_cooldown_expiration_clears_entries(queue_manager: QueueManager) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: queue_manager
- Processing: Orchestrated via classes None and functions queue_manager, test_cooldown_expiration_clears_entries, test_ghost_step_trigger, test_queue_cooldown_enforced, test_queue_prioritises_wait_time, test_record_blocked_attempt_counts_and_triggers, test_requeue_to_tail_rotates_agent.
- Outputs: None, QueueManager
- Downstream modules: townlet.config, townlet.world.queue_manager

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.world.queue_manager

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: queue_manager, test_cooldown_expiration_clears_entries, test_ghost_step_trigger, test_queue_cooldown_enforced, test_queue_prioritises_wait_time, test_record_blocked_attempt_counts_and_triggers, test_requeue_to_tail_rotates_agent.

## `tests/test_queue_metrics.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 63
**Dependencies**: stdlib=__future__, pathlib; external=None; internal=townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring provided.
- `test_queue_metrics_capture_ghost_step_and_rotation() -> None` — No docstring provided.
- `test_nightly_reset_preserves_queue_metrics() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions _make_world, test_nightly_reset_preserves_queue_metrics, test_queue_metrics_capture_ghost_step_and_rotation.
- Outputs: None, WorldState
- Downstream modules: townlet.config, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_world, test_nightly_reset_preserves_queue_metrics, test_queue_metrics_capture_ghost_step_and_rotation.

## `tests/test_queue_resume.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 55
**Dependencies**: stdlib=__future__, pathlib, random; external=pytest; internal=townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `base_config()` — No docstring provided.
- `_setup_loop(config) -> SimulationLoop` — No docstring provided.
- `test_queue_metrics_resume(tmp_path: Path, base_config) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: base_config, config, tmp_path
- Processing: Orchestrated via classes None and functions _setup_loop, base_config, test_queue_metrics_resume.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _setup_loop, base_config, test_queue_metrics_resume.

## `tests/test_relationship_integration.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 66
**Dependencies**: stdlib=__future__, pathlib; external=pytest; internal=townlet.agents.models, townlet.config, townlet.world.grid
**Related modules**: townlet.agents.models, townlet.config, townlet.world.grid

### Classes
- None

### Functions
- `base_config() -> SimulationConfig` — No docstring provided.
- `_with_relationship_modifiers(config: SimulationConfig, enabled: bool) -> SimulationConfig` — No docstring provided.
- `_build_world(config: SimulationConfig) -> WorldState` — No docstring provided.
- `_familiarity(world: WorldState, owner: str, other: str) -> float` — No docstring provided.
- `test_chat_success_personality_bonus_applied(base_config: SimulationConfig) -> None` — No docstring provided.
- `test_chat_success_parity_when_disabled(base_config: SimulationConfig) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: base_config, config, enabled, other, owner, world
- Processing: Orchestrated via classes None and functions _build_world, _familiarity, _with_relationship_modifiers, base_config, test_chat_success_parity_when_disabled, test_chat_success_personality_bonus_applied.
- Outputs: None, SimulationConfig, WorldState, float
- Downstream modules: townlet.agents.models, townlet.config, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.agents.models, townlet.config, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _build_world, _familiarity, _with_relationship_modifiers, base_config, test_chat_success_parity_when_disabled, test_chat_success_personality_bonus_applied.

## `tests/test_relationship_ledger.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 64
**Dependencies**: stdlib=__future__; external=None; internal=townlet.world.relationships
**Related modules**: townlet.world.relationships

### Classes
- None

### Functions
- `test_apply_delta_clamps_and_prunes() -> None` — No docstring provided.
- `test_decay_removes_zero_ties() -> None` — No docstring provided.
- `test_eviction_hook_invoked_for_capacity() -> None` — No docstring provided.
- `test_eviction_hook_invoked_for_decay() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_apply_delta_clamps_and_prunes, test_decay_removes_zero_ties, test_eviction_hook_invoked_for_capacity, test_eviction_hook_invoked_for_decay.
- Outputs: None
- Downstream modules: townlet.world.relationships

### Integration Points
- External libraries: None
- Internal packages: townlet.world.relationships

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_apply_delta_clamps_and_prunes, test_decay_removes_zero_ties, test_eviction_hook_invoked_for_capacity, test_eviction_hook_invoked_for_decay.

## `tests/test_relationship_metrics.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 308
**Dependencies**: stdlib=__future__, pathlib; external=pytest; internal=townlet.config, townlet.telemetry.relationship_metrics, townlet.world.grid
**Related modules**: townlet.config, townlet.telemetry.relationship_metrics, townlet.world.grid

### Classes
- None

### Functions
- `test_record_eviction_tracks_counts() -> None` — No docstring provided.
- `test_window_rolls_and_history_records_samples() -> None` — No docstring provided.
- `test_latest_payload_round_trips_via_ingest() -> None` — No docstring provided.
- `test_invalid_configuration_raises() -> None` — No docstring provided.
- `test_world_relationship_metrics_records_evictions() -> None` — No docstring provided.
- `test_world_relationship_update_symmetry() -> None` — No docstring provided.
- `test_queue_events_modify_relationships() -> None` — No docstring provided.
- `test_shared_meal_updates_relationship() -> None` — No docstring provided.
- `test_absence_triggers_took_my_shift_relationships() -> None` — No docstring provided.
- `test_late_help_creates_positive_relationship() -> None` — No docstring provided.
- `test_chat_outcomes_adjust_relationships() -> None` — No docstring provided.
- `test_relationship_tie_helper_returns_current_values() -> None` — No docstring provided.
- `test_consume_chat_events_is_single_use() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_absence_triggers_took_my_shift_relationships, test_chat_outcomes_adjust_relationships, test_consume_chat_events_is_single_use, test_invalid_configuration_raises, test_late_help_creates_positive_relationship, test_latest_payload_round_trips_via_ingest, test_queue_events_modify_relationships, test_record_eviction_tracks_counts, test_relationship_tie_helper_returns_current_values, test_shared_meal_updates_relationship, test_window_rolls_and_history_records_samples, test_world_relationship_metrics_records_evictions, test_world_relationship_update_symmetry.
- Outputs: None
- Downstream modules: townlet.config, townlet.telemetry.relationship_metrics, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.telemetry.relationship_metrics, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_absence_triggers_took_my_shift_relationships, test_chat_outcomes_adjust_relationships, test_consume_chat_events_is_single_use, test_invalid_configuration_raises, test_late_help_creates_positive_relationship, test_latest_payload_round_trips_via_ingest, test_queue_events_modify_relationships, test_record_eviction_tracks_counts, test_relationship_tie_helper_returns_current_values, test_shared_meal_updates_relationship, test_window_rolls_and_history_records_samples, test_world_relationship_metrics_records_evictions, test_world_relationship_update_symmetry.

## `tests/test_relationship_personality_modifiers.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 67
**Dependencies**: stdlib=__future__; external=pytest; internal=townlet.agents
**Related modules**: townlet.agents

### Classes
- None

### Functions
- `test_modifiers_disabled_returns_baseline() -> None` — No docstring provided.
- `test_forgiveness_scales_negative_values() -> None` — No docstring provided.
- `test_extroversion_adds_chat_bonus() -> None` — No docstring provided.
- `test_ambition_scales_conflict_rivalry() -> None` — No docstring provided.
- `test_unforgiving_agent_intensifies_negative_hits() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_ambition_scales_conflict_rivalry, test_extroversion_adds_chat_bonus, test_forgiveness_scales_negative_values, test_modifiers_disabled_returns_baseline, test_unforgiving_agent_intensifies_negative_hits.
- Outputs: None
- Downstream modules: townlet.agents

### Integration Points
- External libraries: pytest
- Internal packages: townlet.agents

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_ambition_scales_conflict_rivalry, test_extroversion_adds_chat_bonus, test_forgiveness_scales_negative_values, test_modifiers_disabled_returns_baseline, test_unforgiving_agent_intensifies_negative_hits.

## `tests/test_reward_engine.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 261
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.rewards.engine, townlet.world.grid
**Related modules**: townlet.config, townlet.rewards.engine, townlet.world.grid

### Classes
- `StubSnapshot` — defined at line 10
  - Docstring: No class docstring provided.
  - Methods:
    - `__init__(self, needs: dict[str, float], wallet: float) -> None` — No docstring provided.
- `StubWorld` — defined at line 16
  - Docstring: No class docstring provided.
  - Methods:
    - `__init__(self, config, snapshot: StubSnapshot, context: dict[str, float]) -> None` — No docstring provided.
    - `consume_chat_events(self)` — No docstring provided.
    - `agent_context(self, agent_id: str) -> dict[str, float]` — No docstring provided.
    - `relationship_tie(self, subject: str, target: str)` — No docstring provided.
    - `rivalry_top(self, agent_id: str, limit: int)` — No docstring provided.

### Functions
- `_make_world(hunger: float = 0.5) -> WorldState` — No docstring provided.
- `test_reward_negative_with_high_deficit() -> None` — No docstring provided.
- `test_reward_clipped_by_config() -> None` — No docstring provided.
- `test_survival_tick_positive_when_balanced() -> None` — No docstring provided.
- `test_chat_reward_applied_for_successful_conversation() -> None` — No docstring provided.
- `test_chat_reward_skipped_when_needs_override_triggers() -> None` — No docstring provided.
- `test_chat_reward_blocked_within_termination_window() -> None` — No docstring provided.
- `test_episode_clip_enforced() -> None` — No docstring provided.
- `test_wage_and_punctuality_bonus() -> None` — No docstring provided.
- `test_terminal_penalty_applied_for_faint() -> None` — No docstring provided.
- `test_terminal_penalty_applied_for_eviction() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, config, context, hunger, limit, needs, snapshot, subject, target, wallet
- Processing: Orchestrated via classes StubSnapshot, StubWorld and functions _make_world, test_chat_reward_applied_for_successful_conversation, test_chat_reward_blocked_within_termination_window, test_chat_reward_skipped_when_needs_override_triggers, test_episode_clip_enforced, test_reward_clipped_by_config, test_reward_negative_with_high_deficit, test_survival_tick_positive_when_balanced, test_terminal_penalty_applied_for_eviction, test_terminal_penalty_applied_for_faint, test_wage_and_punctuality_bonus.
- Outputs: None, WorldState, dict[str, float]
- Downstream modules: townlet.config, townlet.rewards.engine, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.rewards.engine, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_world, test_chat_reward_applied_for_successful_conversation, test_chat_reward_blocked_within_termination_window, test_chat_reward_skipped_when_needs_override_triggers, test_episode_clip_enforced, test_reward_clipped_by_config, test_reward_negative_with_high_deficit, test_survival_tick_positive_when_balanced, test_terminal_penalty_applied_for_eviction, test_terminal_penalty_applied_for_faint, test_wage_and_punctuality_bonus.
- Methods without docstrings: StubWorld.agent_context, StubWorld.consume_chat_events, StubWorld.relationship_tie, StubWorld.rivalry_top.

## `tests/test_reward_summary.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 49
**Dependencies**: stdlib=json, pathlib; external=None; internal=scripts.reward_summary
**Related modules**: scripts.reward_summary

### Classes
- None

### Functions
- `test_component_stats_mean_and_extremes() -> None` — No docstring provided.
- `test_reward_aggregator_tracks_components(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_component_stats_mean_and_extremes, test_reward_aggregator_tracks_components.
- Outputs: None
- Downstream modules: scripts.reward_summary

### Integration Points
- External libraries: None
- Internal packages: scripts.reward_summary

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_component_stats_mean_and_extremes, test_reward_aggregator_tracks_components.

## `tests/test_rivalry_ledger.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 38
**Dependencies**: stdlib=None; external=pytest; internal=townlet.world.rivalry
**Related modules**: townlet.world.rivalry

### Classes
- None

### Functions
- `test_increment_and_clamp_and_eviction() -> None` — No docstring provided.
- `test_decay_and_eviction_threshold() -> None` — No docstring provided.
- `test_should_avoid_toggle() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_decay_and_eviction_threshold, test_increment_and_clamp_and_eviction, test_should_avoid_toggle.
- Outputs: None
- Downstream modules: townlet.world.rivalry

### Integration Points
- External libraries: pytest
- Internal packages: townlet.world.rivalry

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_decay_and_eviction_threshold, test_increment_and_clamp_and_eviction, test_should_avoid_toggle.

## `tests/test_rivalry_state.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 43
**Dependencies**: stdlib=__future__; external=None; internal=townlet.world.rivalry
**Related modules**: townlet.world.rivalry

### Classes
- None

### Functions
- `test_apply_conflict_clamps_to_max() -> None` — No docstring provided.
- `test_decay_evicts_low_scores() -> None` — No docstring provided.
- `test_should_avoid_threshold() -> None` — No docstring provided.
- `test_encode_features_fixed_width() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_apply_conflict_clamps_to_max, test_decay_evicts_low_scores, test_encode_features_fixed_width, test_should_avoid_threshold.
- Outputs: None
- Downstream modules: townlet.world.rivalry

### Integration Points
- External libraries: None
- Internal packages: townlet.world.rivalry

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_apply_conflict_clamps_to_max, test_decay_evicts_low_scores, test_encode_features_fixed_width, test_should_avoid_threshold.

## `tests/test_rollout_buffer.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 85
**Dependencies**: stdlib=__future__, json, pathlib; external=numpy, pytest; internal=townlet.config, townlet.policy.rollout, townlet.policy.runner
**Related modules**: townlet.config, townlet.policy.rollout, townlet.policy.runner

### Classes
- None

### Functions
- `_dummy_frame(agent_id: str, reward: float = 0.0, done: bool = False) -> dict[str, object]` — No docstring provided.
- `test_rollout_buffer_grouping_to_samples() -> None` — No docstring provided.
- `test_training_harness_capture_rollout(tmp_path: Path) -> None` — No docstring provided.
- `test_rollout_buffer_empty_build_dataset_raises() -> None` — No docstring provided.
- `test_rollout_buffer_single_timestep_metrics() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: agent_id, done, reward, tmp_path
- Processing: Orchestrated via classes None and functions _dummy_frame, test_rollout_buffer_empty_build_dataset_raises, test_rollout_buffer_grouping_to_samples, test_rollout_buffer_single_timestep_metrics, test_training_harness_capture_rollout.
- Outputs: None, dict[str, object]
- Downstream modules: townlet.config, townlet.policy.rollout, townlet.policy.runner

### Integration Points
- External libraries: numpy, pytest
- Internal packages: townlet.config, townlet.policy.rollout, townlet.policy.runner

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _dummy_frame, test_rollout_buffer_empty_build_dataset_raises, test_rollout_buffer_grouping_to_samples, test_rollout_buffer_single_timestep_metrics, test_training_harness_capture_rollout.

## `tests/test_rollout_capture.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 109
**Dependencies**: stdlib=__future__, json, pathlib; external=numpy, pytest, subprocess, sys; internal=townlet.config
**Related modules**: townlet.config

### Classes
- None

### Functions
- `test_capture_rollout_scenarios(tmp_path: Path, config_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `SCENARIO_CONFIGS = [Path('configs/scenarios/kitchen_breakfast.yaml'), Path('configs/scenarios/queue_conflict.yaml'), Path('configs/scenarios/employment_punctuality.yaml'), Path('configs/scenarios/rivalry_decay.yaml'), Path('configs/scenarios/observation_baseline.yaml')]`
- `GOLDEN_STATS_PATH = Path('docs/samples/rollout_scenario_stats.json')`
- `GOLDEN_STATS = json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {}`

### Data Flow
- Inputs: config_path, tmp_path
- Processing: Orchestrated via classes None and functions test_capture_rollout_scenarios.
- Outputs: None
- Downstream modules: townlet.config

### Integration Points
- External libraries: numpy, pytest, subprocess, sys
- Internal packages: townlet.config

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_capture_rollout_scenarios.

## `tests/test_run_anneal_rehearsal.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 33
**Dependencies**: stdlib=pathlib; external=importlib.util, pytest, sys; internal=townlet.policy.models
**Related modules**: townlet.policy.models

### Classes
- None

### Functions
- `test_run_anneal_rehearsal_pass(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_run_anneal_rehearsal_pass.
- Outputs: None
- Downstream modules: townlet.policy.models

### Integration Points
- External libraries: importlib.util, pytest, sys
- Internal packages: townlet.policy.models

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_run_anneal_rehearsal_pass.

## `tests/test_scripted_behavior.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 85
**Dependencies**: stdlib=__future__, pathlib; external=numpy; internal=townlet.config, townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Classes
- None

### Functions
- `test_scripted_behavior_determinism() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_scripted_behavior_determinism.
- Outputs: None
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Integration Points
- External libraries: numpy
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_scripted_behavior_determinism.

## `tests/test_sim_loop_snapshot.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 214
**Dependencies**: stdlib=__future__, json, pathlib, random; external=pytest; internal=townlet.config, townlet.core.sim_loop, townlet.snapshots.state, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.snapshots.state, townlet.world.grid

### Classes
- None

### Functions
- `base_config()` — No docstring provided.
- `test_simulation_loop_snapshot_round_trip(tmp_path: Path, base_config) -> None` — No docstring provided.
- `test_save_snapshot_uses_config_root_and_identity_override(tmp_path: Path, base_config) -> None` — No docstring provided.
- `test_simulation_resume_equivalence(tmp_path: Path, base_config) -> None` — No docstring provided.
- `test_policy_transitions_resume(tmp_path: Path, base_config) -> None` — No docstring provided.
- `_normalise_snapshot(snapshot: dict[str, object]) -> dict[str, object]` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: base_config, snapshot, tmp_path
- Processing: Orchestrated via classes None and functions _normalise_snapshot, base_config, test_policy_transitions_resume, test_save_snapshot_uses_config_root_and_identity_override, test_simulation_loop_snapshot_round_trip, test_simulation_resume_equivalence.
- Outputs: None, dict[str, object]
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.snapshots.state, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.snapshots.state, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _normalise_snapshot, base_config, test_policy_transitions_resume, test_save_snapshot_uses_config_root_and_identity_override, test_simulation_loop_snapshot_round_trip, test_simulation_resume_equivalence.

## `tests/test_sim_loop_structure.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 14
**Dependencies**: stdlib=pathlib; external=None; internal=townlet.config, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.core.sim_loop

### Classes
- None

### Functions
- `test_simulation_loop_runs_one_tick(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_simulation_loop_runs_one_tick.
- Outputs: None
- Downstream modules: townlet.config, townlet.core.sim_loop

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_simulation_loop_runs_one_tick.

## `tests/test_snapshot_manager.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 327
**Dependencies**: stdlib=__future__, json, pathlib, random; external=pytest; internal=townlet.config, townlet.scheduler.perturbations, townlet.snapshots.state, townlet.telemetry.publisher, townlet.utils, townlet.world.grid
**Related modules**: townlet.config, townlet.scheduler.perturbations, townlet.snapshots.state, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Classes
- None

### Functions
- `sample_config() -> SimulationConfig` — No docstring provided.
- `test_snapshot_round_trip(tmp_path: Path, sample_config) -> None` — No docstring provided.
- `test_snapshot_config_mismatch_raises(tmp_path: Path, sample_config) -> None` — No docstring provided.
- `test_snapshot_missing_relationships_field_rejected(tmp_path: Path, sample_config) -> None` — No docstring provided.
- `test_snapshot_schema_version_mismatch(tmp_path: Path, sample_config) -> None` — No docstring provided.
- `_config_with_snapshot_updates(config: SimulationConfig, updates: dict[str, object]) -> SimulationConfig` — No docstring provided.
- `test_snapshot_mismatch_allowed_when_guardrail_disabled(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.
- `test_snapshot_schema_downgrade_honours_allow_flag(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.
- `test_world_relationship_snapshot_round_trip(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: config, sample_config, tmp_path, updates
- Processing: Orchestrated via classes None and functions _config_with_snapshot_updates, sample_config, test_snapshot_config_mismatch_raises, test_snapshot_mismatch_allowed_when_guardrail_disabled, test_snapshot_missing_relationships_field_rejected, test_snapshot_round_trip, test_snapshot_schema_downgrade_honours_allow_flag, test_snapshot_schema_version_mismatch, test_world_relationship_snapshot_round_trip.
- Outputs: None, SimulationConfig
- Downstream modules: townlet.config, townlet.scheduler.perturbations, townlet.snapshots.state, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.scheduler.perturbations, townlet.snapshots.state, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _config_with_snapshot_updates, sample_config, test_snapshot_config_mismatch_raises, test_snapshot_mismatch_allowed_when_guardrail_disabled, test_snapshot_missing_relationships_field_rejected, test_snapshot_round_trip, test_snapshot_schema_downgrade_honours_allow_flag, test_snapshot_schema_version_mismatch, test_world_relationship_snapshot_round_trip.

## `tests/test_snapshot_migrations.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 82
**Dependencies**: stdlib=__future__, dataclasses, pathlib; external=pytest; internal=townlet.config, townlet.snapshots, townlet.snapshots.migrations
**Related modules**: townlet.config, townlet.snapshots, townlet.snapshots.migrations

### Classes
- None

### Functions
- `sample_config() -> SimulationConfig` — No docstring provided.
- `reset_registry() -> None` — No docstring provided.
- `_basic_state(config: SimulationConfig) -> SnapshotState` — No docstring provided.
- `test_snapshot_migration_applied(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.
- `test_snapshot_migration_multi_step(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.
- `test_snapshot_migration_missing_path_raises(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: config, sample_config, tmp_path
- Processing: Orchestrated via classes None and functions _basic_state, reset_registry, sample_config, test_snapshot_migration_applied, test_snapshot_migration_missing_path_raises, test_snapshot_migration_multi_step.
- Outputs: None, SimulationConfig, SnapshotState
- Downstream modules: townlet.config, townlet.snapshots, townlet.snapshots.migrations

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.snapshots, townlet.snapshots.migrations

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _basic_state, reset_registry, sample_config, test_snapshot_migration_applied, test_snapshot_migration_missing_path_raises, test_snapshot_migration_multi_step.

## `tests/test_stability_monitor.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 212
**Dependencies**: stdlib=pathlib; external=None; internal=townlet.config, townlet.stability.monitor
**Related modules**: townlet.config, townlet.stability.monitor

### Classes
- None

### Functions
- `make_monitor() -> StabilityMonitor` — No docstring provided.
- `_track_minimal(monitor: StabilityMonitor, *, tick: int, embedding_warning: bool = False, queue_alert: bool = False) -> None` — No docstring provided.
- `test_starvation_spike_alert_triggers_after_streak() -> None` — No docstring provided.
- `test_option_thrash_alert_averages_over_window() -> None` — No docstring provided.
- `test_reward_variance_alert_exports_state() -> None` — No docstring provided.
- `test_queue_fairness_alerts_include_metrics() -> None` — No docstring provided.
- `test_rivalry_spike_alert_triggers_on_intensity() -> None` — No docstring provided.
- `test_promotion_window_tracking() -> None` — No docstring provided.
- `test_promotion_window_respects_allowed_alerts() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: embedding_warning, monitor, queue_alert, tick
- Processing: Orchestrated via classes None and functions _track_minimal, make_monitor, test_option_thrash_alert_averages_over_window, test_promotion_window_respects_allowed_alerts, test_promotion_window_tracking, test_queue_fairness_alerts_include_metrics, test_reward_variance_alert_exports_state, test_rivalry_spike_alert_triggers_on_intensity, test_starvation_spike_alert_triggers_after_streak.
- Outputs: None, StabilityMonitor
- Downstream modules: townlet.config, townlet.stability.monitor

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.stability.monitor

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _track_minimal, make_monitor, test_option_thrash_alert_averages_over_window, test_promotion_window_respects_allowed_alerts, test_promotion_window_tracking, test_queue_fairness_alerts_include_metrics, test_reward_variance_alert_exports_state, test_rivalry_spike_alert_triggers_on_intensity, test_starvation_spike_alert_triggers_after_streak.

## `tests/test_stability_telemetry.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 47
**Dependencies**: stdlib=__future__, pathlib; external=pytest; internal=townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `test_stability_alerts_exposed_via_telemetry_snapshot(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_stability_alerts_exposed_via_telemetry_snapshot.
- Outputs: None
- Downstream modules: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_stability_alerts_exposed_via_telemetry_snapshot.

## `tests/test_telemetry_client.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 78
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry

### Classes
- None

### Functions
- `make_simulation(enforce_job_loop: bool = True) -> SimulationLoop` — No docstring provided.
- `test_telemetry_client_parses_console_snapshot() -> None` — No docstring provided.
- `test_telemetry_client_warns_on_newer_schema(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.
- `test_telemetry_client_raises_on_major_mismatch() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: enforce_job_loop, monkeypatch
- Processing: Orchestrated via classes None and functions make_simulation, test_telemetry_client_parses_console_snapshot, test_telemetry_client_raises_on_major_mismatch, test_telemetry_client_warns_on_newer_schema.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_simulation, test_telemetry_client_parses_console_snapshot, test_telemetry_client_raises_on_major_mismatch, test_telemetry_client_warns_on_newer_schema.

## `tests/test_telemetry_jobs.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 55
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.core.sim_loop, townlet.stability.monitor, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.stability.monitor, townlet.world.grid

### Classes
- None

### Functions
- `test_telemetry_captures_job_snapshot() -> None` — No docstring provided.
- `test_stability_monitor_lateness_alert() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_stability_monitor_lateness_alert, test_telemetry_captures_job_snapshot.
- Outputs: None
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.stability.monitor, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.stability.monitor, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_stability_monitor_lateness_alert, test_telemetry_captures_job_snapshot.

## `tests/test_telemetry_narration.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 107
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.telemetry.narration, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.telemetry.narration, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None

### Functions
- `test_narration_rate_limiter_enforces_cooldowns() -> None` — No docstring provided.
- `test_narration_rate_limiter_priority_bypass() -> None` — No docstring provided.
- `test_telemetry_publisher_emits_queue_conflict_narration(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_narration_rate_limiter_enforces_cooldowns, test_narration_rate_limiter_priority_bypass, test_telemetry_publisher_emits_queue_conflict_narration.
- Outputs: None
- Downstream modules: townlet.config, townlet.telemetry.narration, townlet.telemetry.publisher, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.telemetry.narration, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_narration_rate_limiter_enforces_cooldowns, test_narration_rate_limiter_priority_bypass, test_telemetry_publisher_emits_queue_conflict_narration.

## `tests/test_telemetry_new_events.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 236
**Dependencies**: stdlib=__future__, pathlib; external=None; internal=townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring provided.
- `test_shower_events_in_telemetry() -> None` — No docstring provided.
- `test_shower_complete_narration() -> None` — No docstring provided.
- `test_sleep_events_in_telemetry() -> None` — No docstring provided.
- `test_rivalry_events_surface_in_telemetry() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions make_loop, test_rivalry_events_surface_in_telemetry, test_shower_complete_narration, test_shower_events_in_telemetry, test_sleep_events_in_telemetry.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_loop, test_rivalry_events_surface_in_telemetry, test_shower_complete_narration, test_shower_events_in_telemetry, test_sleep_events_in_telemetry.

## `tests/test_telemetry_stream_smoke.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 51
**Dependencies**: stdlib=__future__, json, pathlib; external=None; internal=townlet.config, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry

### Classes
- None

### Functions
- `_ensure_agents(loop: SimulationLoop) -> None` — No docstring provided.
- `test_file_transport_stream_smoke(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: loop, tmp_path
- Processing: Orchestrated via classes None and functions _ensure_agents, test_file_transport_stream_smoke.
- Outputs: None
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _ensure_agents, test_file_transport_stream_smoke.

## `tests/test_telemetry_summary.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 69
**Dependencies**: stdlib=__future__, pathlib; external=importlib.util, sys; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `test_summary_includes_new_events(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: tmp_path
- Processing: Orchestrated via classes None and functions test_summary_includes_new_events.
- Outputs: None
- Downstream modules: None

### Integration Points
- External libraries: importlib.util, sys

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_summary_includes_new_events.

## `tests/test_telemetry_transport.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 116
**Dependencies**: stdlib=__future__, json, pathlib; external=pytest; internal=townlet.config, townlet.core.sim_loop, townlet.telemetry.transport, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.telemetry.transport, townlet.world.grid

### Classes
- None

### Functions
- `_ensure_agents(loop: SimulationLoop) -> None` — No docstring provided.
- `test_transport_buffer_drop_until_capacity() -> None` — No docstring provided.
- `test_telemetry_publisher_flushes_payload(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.
- `test_telemetry_publisher_retries_on_failure(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: loop, monkeypatch
- Processing: Orchestrated via classes None and functions _ensure_agents, test_telemetry_publisher_flushes_payload, test_telemetry_publisher_retries_on_failure, test_transport_buffer_drop_until_capacity.
- Outputs: None
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.telemetry.transport, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.telemetry.transport, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _ensure_agents, test_telemetry_publisher_flushes_payload, test_telemetry_publisher_retries_on_failure, test_transport_buffer_drop_until_capacity.

## `tests/test_telemetry_validator.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 119
**Dependencies**: stdlib=__future__, json, pathlib; external=pytest; internal=scripts.validate_ppo_telemetry
**Related modules**: scripts.validate_ppo_telemetry

### Classes
- None

### Functions
- `_write_ndjson(path: Path, record: dict[str, float]) -> None` — No docstring provided.
- `test_validate_ppo_telemetry_accepts_valid_log(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_ppo_telemetry_raises_for_missing_conflict(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_ppo_telemetry_accepts_version_1_1(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_ppo_telemetry_v1_1_missing_field_raises(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `VALID_RECORD = {'epoch': 1.0, 'updates': 2.0, 'transitions': 4.0, 'loss_policy': 0.1, 'loss_value': 0.2, 'loss_entropy': 0.3, 'loss_total': 0.4, 'clip_fraction': 0.1, 'adv_mean': 0.0, 'adv_std': 0.1, 'adv_zero_std_batches': 0.0, 'adv_min_std': 0.1, 'clip_triggered_minibatches': 0.0, 'clip_fraction_max': 0.1, 'grad_norm': 1.5, 'kl_divergence': 0.01, 'telemetry_version': 1.0, 'lr': 0.0003, 'steps': 4.0, 'baseline_sample_count': 2.0, 'baseline_reward_mean': 0.25, 'baseline_reward_sum': 1.0, 'baseline_reward_sum_mean': 0.5, 'baseline_log_prob_mean': -0.2, 'conflict.rivalry_max_mean_avg': 0.05, 'conflict.rivalry_max_max_avg': 0.1, 'conflict.rivalry_avoid_count_mean_avg': 0.0, 'conflict.rivalry_avoid_count_max_avg': 0.0}`

### Data Flow
- Inputs: path, record, tmp_path
- Processing: Orchestrated via classes None and functions _write_ndjson, test_validate_ppo_telemetry_accepts_valid_log, test_validate_ppo_telemetry_accepts_version_1_1, test_validate_ppo_telemetry_raises_for_missing_conflict, test_validate_ppo_telemetry_v1_1_missing_field_raises.
- Outputs: None
- Downstream modules: scripts.validate_ppo_telemetry

### Integration Points
- External libraries: pytest
- Internal packages: scripts.validate_ppo_telemetry

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _write_ndjson, test_validate_ppo_telemetry_accepts_valid_log, test_validate_ppo_telemetry_accepts_version_1_1, test_validate_ppo_telemetry_raises_for_missing_conflict, test_validate_ppo_telemetry_v1_1_missing_field_raises.

## `tests/test_telemetry_watch.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 105
**Dependencies**: stdlib=pathlib; external=importlib.util, pytest, sys; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `write_log(tmp_path: Path, records: list[dict[str, object]]) -> Path` — No docstring provided.
- `test_anneal_bc_threshold(tmp_path: Path, bc_accuracy: float) -> None` — No docstring provided.
- `test_new_event_thresholds(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: bc_accuracy, records, tmp_path
- Processing: Orchestrated via classes None and functions test_anneal_bc_threshold, test_new_event_thresholds, write_log.
- Outputs: None, Path
- Downstream modules: None

### Integration Points
- External libraries: importlib.util, pytest, sys

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_anneal_bc_threshold, test_new_event_thresholds, write_log.

## `tests/test_training_anneal.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 108
**Dependencies**: stdlib=__future__, json, pathlib; external=numpy, pytest; internal=townlet.config, townlet.policy.models, townlet.policy.replay, townlet.policy.runner
**Related modules**: townlet.config, townlet.policy.models, townlet.policy.replay, townlet.policy.runner

### Classes
- None

### Functions
- `_write_sample(output_dir: Path, stem: str, timesteps: int, action_dim: int = 2) -> tuple[Path, Path]` — No docstring provided.
- `test_run_anneal_bc_then_ppo(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: action_dim, output_dir, stem, timesteps, tmp_path
- Processing: Orchestrated via classes None and functions _write_sample, test_run_anneal_bc_then_ppo.
- Outputs: None, tuple[Path, Path]
- Downstream modules: townlet.config, townlet.policy.models, townlet.policy.replay, townlet.policy.runner

### Integration Points
- External libraries: numpy, pytest
- Internal packages: townlet.config, townlet.policy.models, townlet.policy.replay, townlet.policy.runner

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _write_sample, test_run_anneal_bc_then_ppo.

## `tests/test_training_cli.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 81
**Dependencies**: stdlib=__future__, argparse, pathlib; external=None; internal=scripts, townlet.config
**Related modules**: scripts, townlet.config

### Classes
- None

### Functions
- `_make_namespace(**kwargs: object) -> Namespace` — No docstring provided.
- `test_collect_ppo_overrides_handles_values() -> None` — No docstring provided.
- `test_apply_ppo_overrides_creates_config_when_missing() -> None` — No docstring provided.
- `test_apply_ppo_overrides_updates_existing_model() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: kwargs
- Processing: Orchestrated via classes None and functions _make_namespace, test_apply_ppo_overrides_creates_config_when_missing, test_apply_ppo_overrides_updates_existing_model, test_collect_ppo_overrides_handles_values.
- Outputs: Namespace, None
- Downstream modules: scripts, townlet.config

### Integration Points
- External libraries: None
- Internal packages: scripts, townlet.config

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_namespace, test_apply_ppo_overrides_creates_config_when_missing, test_apply_ppo_overrides_updates_existing_model, test_collect_ppo_overrides_handles_values.

## `tests/test_training_replay.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 955
**Dependencies**: stdlib=__future__, json, math, pathlib; external=numpy, pytest, subprocess, sys, torch; internal=townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.policy.models, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.runner, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.policy.models, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.runner, townlet.world.grid

### Classes
- None

### Functions
- `_validate_numeric(value: object) -> None` — No docstring provided.
- `_assert_ppo_log_schema(summary: dict[str, object], require_baseline: bool) -> None` — No docstring provided.
- `_load_expected_stats(config_path: Path) -> dict[str, dict[str, float]]` — No docstring provided.
- `_aggregate_expected_metrics(sample_stats: dict[str, dict[str, float]]) -> dict[str, float]` — No docstring provided.
- `_make_sample(base_dir: Path, rivalry_increment: float, avoid_threshold: float, suffix: str) -> tuple[Path, Path]` — No docstring provided.
- `_make_social_sample() -> ReplaySample` — No docstring provided.
- `test_training_harness_replay_stats(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_dataset_batch_iteration(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_loader_schema_guard(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_dataset_streaming(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_loader_missing_training_arrays(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_loader_value_length_mismatch(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_run_ppo_on_capture(tmp_path: Path, config_path: Path) -> None` — No docstring provided.
- `test_training_harness_run_ppo(tmp_path: Path) -> None` — No docstring provided.
- `test_run_ppo_rejects_nan_advantages(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_log_sampling_and_rotation(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_run_rollout_ppo(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_ppo_conflict_telemetry(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_run_rollout_ppo_multiple_cycles(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_rollout_capture_and_train_cycles(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_streaming_log_offsets(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_rollout_queue_conflict_metrics(tmp_path: Path) -> None` — No docstring provided.
- `test_ppo_social_chat_drift(tmp_path: Path) -> None` — No docstring provided.
- `test_policy_runtime_collects_frames(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `SCENARIO_CONFIGS = [Path('configs/scenarios/kitchen_breakfast.yaml'), Path('configs/scenarios/queue_conflict.yaml'), Path('configs/scenarios/employment_punctuality.yaml'), Path('configs/scenarios/rivalry_decay.yaml'), Path('configs/scenarios/observation_baseline.yaml')]`
- `GOLDEN_STATS_PATH = Path('docs/samples/rollout_scenario_stats.json')`
- `GOLDEN_STATS = json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {}`
- `REQUIRED_PPO_KEYS = {'epoch', 'updates', 'transitions', 'loss_policy', 'loss_value', 'loss_entropy', 'loss_total', 'clip_fraction', 'adv_mean', 'adv_std', 'adv_zero_std_batches', 'adv_min_std', 'clip_triggered_minibatches', 'clip_fraction_max', 'grad_norm', 'kl_divergence', 'telemetry_version', 'lr', 'steps', 'epoch_duration_sec', 'data_mode', 'cycle_id', 'batch_entropy_mean', 'batch_entropy_std', 'grad_norm_max', 'kl_divergence_max', 'reward_advantage_corr', 'rollout_ticks', 'log_stream_offset', 'queue_conflict_events', 'queue_conflict_intensity_sum', 'shared_meal_events', 'late_help_events', 'shift_takeover_events', 'chat_success_events', 'chat_failure_events', 'chat_quality_mean'}`
- `REQUIRED_PPO_NUMERIC_KEYS = REQUIRED_PPO_KEYS - {'data_mode'}`
- `BASELINE_KEYS_REQUIRED = {'baseline_sample_count', 'baseline_reward_sum', 'baseline_reward_sum_mean', 'baseline_reward_mean'}`
- `BASELINE_KEYS_OPTIONAL = {'baseline_log_prob_mean'}`
- `ALLOWED_KEY_PREFIXES = ('conflict.',)`

### Data Flow
- Inputs: avoid_threshold, base_dir, config_path, require_baseline, rivalry_increment, sample_stats, suffix, summary, tmp_path, value
- Processing: Orchestrated via classes None and functions _aggregate_expected_metrics, _assert_ppo_log_schema, _load_expected_stats, _make_sample, _make_social_sample, _validate_numeric, test_policy_runtime_collects_frames, test_ppo_social_chat_drift, test_replay_dataset_batch_iteration, test_replay_dataset_streaming, test_replay_loader_missing_training_arrays, test_replay_loader_schema_guard, test_replay_loader_value_length_mismatch, test_run_ppo_rejects_nan_advantages, test_training_harness_log_sampling_and_rotation, test_training_harness_ppo_conflict_telemetry, test_training_harness_replay_stats, test_training_harness_rollout_capture_and_train_cycles, test_training_harness_rollout_queue_conflict_metrics, test_training_harness_run_ppo, test_training_harness_run_ppo_on_capture, test_training_harness_run_rollout_ppo, test_training_harness_run_rollout_ppo_multiple_cycles, test_training_harness_streaming_log_offsets.
- Outputs: None, ReplaySample, dict[str, dict[str, float]], dict[str, float], tuple[Path, Path]
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.policy.models, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.runner, townlet.world.grid

### Integration Points
- External libraries: numpy, pytest, subprocess, sys, torch
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.policy.models, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.runner, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _aggregate_expected_metrics, _assert_ppo_log_schema, _load_expected_stats, _make_sample, _make_social_sample, _validate_numeric, test_policy_runtime_collects_frames, test_ppo_social_chat_drift, test_replay_dataset_batch_iteration, test_replay_dataset_streaming, test_replay_loader_missing_training_arrays, test_replay_loader_schema_guard, test_replay_loader_value_length_mismatch, test_run_ppo_rejects_nan_advantages, test_training_harness_log_sampling_and_rotation, test_training_harness_ppo_conflict_telemetry, test_training_harness_replay_stats, test_training_harness_rollout_capture_and_train_cycles, test_training_harness_rollout_queue_conflict_metrics, test_training_harness_run_ppo, test_training_harness_run_ppo_on_capture, test_training_harness_run_rollout_ppo, test_training_harness_run_rollout_ppo_multiple_cycles, test_training_harness_streaming_log_offsets.

## `tests/test_utils_rng.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 22
**Dependencies**: stdlib=__future__, random; external=pytest; internal=townlet.utils
**Related modules**: townlet.utils

### Classes
- None

### Functions
- `test_encode_decode_rng_state_round_trip() -> None` — No docstring provided.
- `test_decode_rng_state_invalid_payload() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions test_decode_rng_state_invalid_payload, test_encode_decode_rng_state_round_trip.
- Outputs: None
- Downstream modules: townlet.utils

### Integration Points
- External libraries: pytest
- Internal packages: townlet.utils

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: test_decode_rng_state_invalid_payload, test_encode_decode_rng_state_round_trip.

## `tests/test_world_local_view.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 71
**Dependencies**: stdlib=__future__, pathlib; external=None; internal=townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring provided.
- `tile_for_position(tiles, position)` — No docstring provided.
- `test_local_view_includes_objects_and_agents() -> None` — No docstring provided.
- `test_agent_context_defaults() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: position, tiles
- Processing: Orchestrated via classes None and functions make_loop, test_agent_context_defaults, test_local_view_includes_objects_and_agents, tile_for_position.
- Outputs: None, SimulationLoop
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: make_loop, test_agent_context_defaults, test_local_view_includes_objects_and_agents, tile_for_position.

## `tests/test_world_nightly_reset.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 74
**Dependencies**: stdlib=__future__, pathlib; external=None; internal=townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `_setup_world() -> WorldState` — No docstring provided.
- `test_apply_nightly_reset_returns_agents_home() -> None` — No docstring provided.
- `test_simulation_loop_triggers_nightly_reset() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions _setup_world, test_apply_nightly_reset_returns_agents_home, test_simulation_loop_triggers_nightly_reset.
- Outputs: None, WorldState
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: None
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _setup_world, test_apply_nightly_reset_returns_agents_home, test_simulation_loop_triggers_nightly_reset.

## `tests/test_world_queue_integration.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 280
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring provided.
- `test_queue_assignment_flow() -> None` — No docstring provided.
- `test_queue_ghost_step_promotes_waiter() -> None` — No docstring provided.
- `test_affordance_completion_applies_effects() -> None` — No docstring provided.
- `test_eat_meal_adjusts_needs_and_wallet() -> None` — No docstring provided.
- `test_affordance_failure_skips_effects() -> None` — No docstring provided.
- `test_affordances_loaded_from_yaml() -> None` — No docstring provided.
- `test_affordance_events_emitted() -> None` — No docstring provided.
- `test_need_decay_applied_each_tick() -> None` — No docstring provided.
- `test_eat_meal_deducts_wallet_and_stock() -> None` — No docstring provided.
- `test_wage_income_applied_on_shift() -> None` — No docstring provided.
- `test_stove_restock_event_emitted() -> None` — No docstring provided.
- `test_scripted_behavior_handles_sleep() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions _make_world, test_affordance_completion_applies_effects, test_affordance_events_emitted, test_affordance_failure_skips_effects, test_affordances_loaded_from_yaml, test_eat_meal_adjusts_needs_and_wallet, test_eat_meal_deducts_wallet_and_stock, test_need_decay_applied_each_tick, test_queue_assignment_flow, test_queue_ghost_step_promotes_waiter, test_scripted_behavior_handles_sleep, test_stove_restock_event_emitted, test_wage_income_applied_on_shift.
- Outputs: None, WorldState
- Downstream modules: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_world, test_affordance_completion_applies_effects, test_affordance_events_emitted, test_affordance_failure_skips_effects, test_affordances_loaded_from_yaml, test_eat_meal_adjusts_needs_and_wallet, test_eat_meal_deducts_wallet_and_stock, test_need_decay_applied_each_tick, test_queue_assignment_flow, test_queue_ghost_step_promotes_waiter, test_scripted_behavior_handles_sleep, test_stove_restock_event_emitted, test_wage_income_applied_on_shift.

## `tests/test_world_rivalry.py`

**Purpose**: No module docstring available; clarify responsibilities during implementation.
**Lines of code**: 94
**Dependencies**: stdlib=pathlib; external=pytest; internal=townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring provided.
- `test_register_rivalry_conflict_updates_snapshot() -> None` — No docstring provided.
- `test_rivalry_events_record_reason() -> None` — No docstring provided.
- `test_rivalry_decays_over_time() -> None` — No docstring provided.
- `test_queue_conflict_event_emitted_with_intensity() -> None` — No docstring provided.

### Constants and Configuration
- None

### Data Flow
- Inputs: None
- Processing: Orchestrated via classes None and functions _make_world, test_queue_conflict_event_emitted_with_intensity, test_register_rivalry_conflict_updates_snapshot, test_rivalry_decays_over_time, test_rivalry_events_record_reason.
- Outputs: None, WorldState
- Downstream modules: townlet.config, townlet.world.grid

### Integration Points
- External libraries: pytest
- Internal packages: townlet.config, townlet.world.grid

### Code Quality Notes
- Missing module docstring; add top-level context.
- Functions without docstrings: _make_world, test_queue_conflict_event_emitted_with_intensity, test_register_rivalry_conflict_updates_snapshot, test_rivalry_decays_over_time, test_rivalry_events_record_reason.
