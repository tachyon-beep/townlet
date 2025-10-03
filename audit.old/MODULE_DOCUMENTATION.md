# Module Documentation

## `scripts/audit_bc_datasets.py`

**Purpose**: Audit behaviour cloning datasets for checksum and metadata freshness.
**Lines of code**: 161
**Dependencies**: stdlib=__future__.annotations, argparse, datetime.datetime, hashlib, json, pathlib.Path, typing.Dict, typing.List, typing.Mapping; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 16)
- `load_versions(path: Path) -> Mapping[str, Mapping[str, object]]` — No docstring. (line 32)
- `audit_dataset(name: str, payload: Mapping[str, object]) -> dict[str, object]` — No docstring. (line 41)
- `audit_catalog(versions_path: Path) -> dict[str, object]` — No docstring. (line 129)
- `main() -> None` — No docstring. (line 152)

### Constants and Configuration
- `DEFAULT_VERSIONS_PATH` = Path('data/bc_datasets/versions.json') (line 12)
- `REQUIRED_VERSION_KEYS` = {'manifest', 'checksums', 'captures_dir'} (line 13)

### Data Flow
- Primary inputs: name, path, payload, versions_path
- Return payloads: Mapping[str, Mapping[str, object]], None, argparse.Namespace, dict[str, object]
- Audits datasets or configurations via audit_catalog, audit_dataset
- Loads configuration or datasets from disk via load_versions

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: audit_catalog, audit_dataset, load_versions, main, parse_args

## `scripts/bc_metrics_summary.py`

**Purpose**: Summarise behaviour cloning evaluation metrics.
**Lines of code**: 52
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 10)
- `load_metrics(path: Path) -> list[dict[str, float]]` — No docstring. (line 17)
- `summarise(metrics: list[dict[str, float]]) -> dict[str, float]` — No docstring. (line 26)
- `main() -> None` — No docstring. (line 37)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: metrics, path
- Return payloads: None, argparse.Namespace, dict[str, float], list[dict[str, float]]
- Loads configuration or datasets from disk via load_metrics
- Summarises metrics for review via summarise

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: load_metrics, main, parse_args, summarise

## `scripts/benchmark_tick.py`

**Purpose**: Simple benchmark to estimate average tick duration.
**Lines of code**: 38
**Dependencies**: stdlib=__future__.annotations, argparse, pathlib.Path, time; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 12)
- `benchmark(config_path: Path, ticks: int, enforce: bool) -> float` — No docstring. (line 20)
- `main() -> None` — No docstring. (line 31)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config_path, enforce, ticks
- Return payloads: None, argparse.Namespace, float
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop

### Code Quality Notes
- Missing docstrings: benchmark, main, parse_args

## `scripts/capture_rollout.py`

**Purpose**: CLI to capture Townlet rollout trajectories into replay samples.
**Lines of code**: 140
**Dependencies**: stdlib=__future__.annotations, argparse, datetime.datetime, datetime.timezone, json, pathlib.Path, typing.Any, typing.Dict; external=numpy; internal=townlet.config.loader.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.metrics.compute_sample_metrics, townlet.policy.replay.ReplaySample, townlet.policy.replay.frames_to_replay_sample, townlet.policy.scenario_utils.apply_scenario, townlet.policy.scenario_utils.seed_default_agents
**Related modules**: townlet.config.loader.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.metrics.compute_sample_metrics, townlet.policy.replay.ReplaySample, townlet.policy.replay.frames_to_replay_sample, townlet.policy.scenario_utils.apply_scenario, townlet.policy.scenario_utils.seed_default_agents

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 19)
- `main() -> None` — No docstring. (line 59)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, argparse.Namespace
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: numpy
- Internal: townlet.config.loader.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.metrics.compute_sample_metrics, townlet.policy.replay.ReplaySample, townlet.policy.replay.frames_to_replay_sample, townlet.policy.scenario_utils.apply_scenario, townlet.policy.scenario_utils.seed_default_agents

### Code Quality Notes
- Missing docstrings: main, parse_args

## `scripts/capture_rollout_suite.py`

**Purpose**: Run rollout capture across a suite of configs.
**Lines of code**: 112
**Dependencies**: stdlib=__future__.annotations, argparse, pathlib.Path, subprocess, sys, typing.List; external=None; internal=townlet.config.loader.load_config
**Related modules**: townlet.config.loader.load_config

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 13)
- `run_capture(config: Path, ticks: int, output: Path, auto_seed: bool, agent_filter: str | None, compress: bool, retries: int) -> None` — No docstring. (line 58)
- `main() -> None` — No docstring. (line 95)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_filter, auto_seed, compress, config, output, retries, ticks
- Return payloads: None, argparse.Namespace
- Captures trajectories or telemetry snapshots via run_capture

### Integration Points
- External: None
- Internal: townlet.config.loader.load_config

### Code Quality Notes
- Missing docstrings: main, parse_args, run_capture

## `scripts/capture_scripted.py`

**Purpose**: Capture scripted trajectories for behaviour cloning datasets.
**Lines of code**: 131
**Dependencies**: stdlib=__future__.annotations, argparse, collections.defaultdict, json, pathlib.Path, typing.Dict, typing.List; external=numpy; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.replay.frames_to_replay_sample, townlet.policy.scenario_utils.seed_default_agents, townlet.policy.scripted.ScriptedPolicyAdapter, townlet.policy.scripted.get_scripted_policy
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.replay.frames_to_replay_sample, townlet.policy.scenario_utils.seed_default_agents, townlet.policy.scripted.ScriptedPolicyAdapter, townlet.policy.scripted.get_scripted_policy

### Classes
- None

### Functions
- `parse_args(argv: List[str] | None = None) -> argparse.Namespace` — No docstring. (line 20)
- `_build_frame(adapter: ScriptedPolicyAdapter, agent_id: str, observation: Dict[str, np.ndarray], reward: float, terminated: bool, trajectory_id: str) -> Dict[str, object]` — No docstring. (line 35)
- `main(argv: List[str] | None = None) -> None` — No docstring. (line 65)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: adapter, agent_id, argv, observation, reward, terminated, trajectory_id
- Return payloads: Dict[str, object], None, argparse.Namespace
- Builds derived structures or observations via _build_frame

### Integration Points
- External: numpy
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.replay.frames_to_replay_sample, townlet.policy.scenario_utils.seed_default_agents, townlet.policy.scripted.ScriptedPolicyAdapter, townlet.policy.scripted.get_scripted_policy

### Code Quality Notes
- Missing docstrings: _build_frame, main, parse_args

## `scripts/console_dry_run.py`

**Purpose**: Employment console dry-run harness.
**Lines of code**: 126
**Dependencies**: stdlib=__future__.annotations, pathlib.Path, tempfile; external=None; internal=townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.snapshots.SnapshotManager, townlet.snapshots.state.snapshot_from_world, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.snapshots.SnapshotManager, townlet.snapshots.state.snapshot_from_world, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `main() -> None` — No docstring. (line 15)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.snapshots.SnapshotManager, townlet.snapshots.state.snapshot_from_world, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: main

## `scripts/curate_trajectories.py`

**Purpose**: Filter and summarise behaviour-cloning trajectories.
**Lines of code**: 104
**Dependencies**: stdlib=__future__.annotations, argparse, dataclasses.dataclass, json, pathlib.Path, typing.Iterable, typing.List, typing.Mapping; external=numpy; internal=townlet.policy.replay.load_replay_sample
**Related modules**: townlet.policy.replay.load_replay_sample

### Classes
- `EvaluationResult` (bases: object; decorators: dataclass) — No class docstring provided. (line 17)
  - Attributes:
    - name=`sample_path`, type=`Path` (line 18)
    - name=`meta_path`, type=`Path` (line 19)
    - name=`metrics`, type=`Mapping[str, float]` (line 20)
    - name=`accepted`, type=`bool` (line 21)

### Functions
- `parse_args(argv: List[str] | None = None) -> argparse.Namespace` — No docstring. (line 24)
- `_pair_files(directory: Path) -> Iterable[tuple[Path, Path]]` — No docstring. (line 33)
- `evaluate_sample(npz_path: Path, json_path: Path) -> EvaluationResult` — No docstring. (line 40)
- `curate(result: EvaluationResult, *, min_timesteps: int, min_reward: float | None) -> EvaluationResult` — No docstring. (line 57)
- `write_manifest(results: Iterable[EvaluationResult], output: Path) -> None` — No docstring. (line 65)
- `summarise(results: Iterable[EvaluationResult]) -> Mapping[str, float]` — No docstring. (line 79)
- `main(argv: List[str] | None = None) -> None` — No docstring. (line 89)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: argv, directory, json_path, min_reward, min_timesteps, npz_path, output, result, results
- Return payloads: EvaluationResult, Iterable[tuple[Path, Path]], Mapping[str, float], None, argparse.Namespace
- Curates datasets or metrics via curate
- Evaluates conditions or invariants via evaluate_sample
- Summarises metrics for review via summarise

### Integration Points
- External: numpy
- Internal: townlet.policy.replay.load_replay_sample

### Code Quality Notes
- Missing docstrings: _pair_files, curate, evaluate_sample, main, parse_args, summarise, write_manifest

## `scripts/manage_phase_c.py`

**Purpose**: Helper script to toggle Phase C social reward stages in configs.
**Lines of code**: 164
**Dependencies**: stdlib=__future__.annotations, argparse, pathlib.Path, typing.Any, typing.Dict, typing.List; external=yaml; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 13)
- `load_config(path: Path) -> Dict[str, Any]` — No docstring. (line 70)
- `ensure_nested(mapping: Dict[str, Any], keys: List[str]) -> Dict[str, Any]` — No docstring. (line 79)
- `write_config(data: Dict[str, Any], *, output: Path | None, in_place: bool, source: Path) -> None` — No docstring. (line 90)
- `handle_set_stage(args: argparse.Namespace) -> None` — No docstring. (line 104)
- `parse_schedule_entries(entries: List[str]) -> List[Dict[str, Any]]` — No docstring. (line 111)
- `handle_schedule(args: argparse.Namespace) -> None` — No docstring. (line 130)
- `main() -> None` — No docstring. (line 153)

### Constants and Configuration
- `VALID_STAGES` = {'OFF', 'C1', 'C2', 'C3'} (line 10)

### Data Flow
- Primary inputs: args, data, entries, in_place, keys, mapping, output, path, source
- Return payloads: Dict[str, Any], List[Dict[str, Any]], None, argparse.Namespace
- Loads configuration or datasets from disk via load_config

### Integration Points
- External: yaml
- Internal: None

### Code Quality Notes
- Missing docstrings: ensure_nested, handle_schedule, handle_set_stage, load_config, main, parse_args, parse_schedule_entries, write_config

## `scripts/merge_rollout_metrics.py`

**Purpose**: Merge captured rollout metrics into the golden stats JSON.
**Lines of code**: 132
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 12)
- `_load_metrics_from_dir(scenario_dir: Path) -> dict[str, dict[str, float]] | None` — No docstring. (line 55)
- `_collect_input_metrics(root: Path, allow_template: bool) -> dict[str, dict[str, dict[str, float]]]` — No docstring. (line 68)
- `main() -> None` — No docstring. (line 85)

### Constants and Configuration
- `DEFAULT_GOLDEN_PATH` = Path('docs/samples/rollout_scenario_stats.json') (line 8)
- `METRICS_FILENAME` = 'rollout_sample_metrics.json' (line 9)

### Data Flow
- Primary inputs: allow_template, root, scenario_dir
- Return payloads: None, argparse.Namespace, dict[str, dict[str, dict[str, float]]], dict[str, dict[str, float]] | None
- Loads configuration or datasets from disk via _load_metrics_from_dir

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: _collect_input_metrics, _load_metrics_from_dir, main, parse_args

## `scripts/observer_ui.py`

**Purpose**: Launch the Townlet observer dashboard against a local simulation.
**Lines of code**: 62
**Dependencies**: stdlib=__future__.annotations, argparse, pathlib.Path; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet_ui.dashboard.run_dashboard
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet_ui.dashboard.run_dashboard

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 13)
- `main() -> None` — No docstring. (line 46)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, argparse.Namespace
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet_ui.dashboard.run_dashboard

### Code Quality Notes
- Missing docstrings: main, parse_args

## `scripts/ppo_telemetry_plot.py`

**Purpose**: Quick-look plotting utility for PPO telemetry JSONL logs.
**Lines of code**: 101
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path, typing.Any; external=matplotlib.pyplot; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 10)
- `load_entries(log_path: Path) -> list[dict[str, Any]]` — No docstring. (line 33)
- `summarise(entries: list[dict[str, Any]]) -> None` — No docstring. (line 48)
- `plot(entries: list[dict[str, Any]], show: bool, output: Path | None) -> None` — No docstring. (line 57)
- `main() -> None` — No docstring. (line 93)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: entries, log_path, output, show
- Return payloads: None, argparse.Namespace, list[dict[str, Any]]
- Loads configuration or datasets from disk via load_entries
- Summarises metrics for review via summarise

### Integration Points
- External: matplotlib.pyplot
- Internal: None

### Code Quality Notes
- Missing docstrings: load_entries, main, parse_args, plot, summarise

## `scripts/profile_observation_tensor.py`

**Purpose**: Profile observation tensor dimensions for a given config.
**Lines of code**: 86
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path, statistics.mean; external=numpy; internal=townlet.config.load_config, townlet.observations.builder.ObservationBuilder, townlet.world.AgentSnapshot, townlet.world.WorldState
**Related modules**: townlet.config.load_config, townlet.observations.builder.ObservationBuilder, townlet.world.AgentSnapshot, townlet.world.WorldState

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 16)
- `bootstrap_world(config_path: Path, agent_count: int) -> tuple[WorldState, ObservationBuilder]` — No docstring. (line 25)
- `profile(world: WorldState, builder: ObservationBuilder, ticks: int) -> dict[str, object]` — No docstring. (line 41)
- `main() -> None` — No docstring. (line 74)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_count, builder, config_path, ticks, world
- Return payloads: None, argparse.Namespace, dict[str, object], tuple[WorldState, ObservationBuilder]
- Profiles performance characteristics via profile

### Integration Points
- External: numpy
- Internal: townlet.config.load_config, townlet.observations.builder.ObservationBuilder, townlet.world.AgentSnapshot, townlet.world.WorldState

### Code Quality Notes
- Missing docstrings: bootstrap_world, main, parse_args, profile

## `scripts/promotion_drill.py`

**Purpose**: Run a scripted promotion/rollback drill and capture artefacts.
**Lines of code**: 107
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path, typing.Any; external=None; internal=townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop
**Related modules**: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop

### Classes
- None

### Functions
- `_ensure_candidate_ready(loop: SimulationLoop) -> None` — No docstring. (line 16)
- `run_drill(config_path: Path, output_dir: Path, checkpoint: Path) -> dict[str, Any]` — No docstring. (line 31)
- `main(argv: list[str] | None = None) -> int` — No docstring. (line 80)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: argv, checkpoint, config_path, loop, output_dir
- Return payloads: None, dict[str, Any], int
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop

### Code Quality Notes
- Missing docstrings: _ensure_candidate_ready, main, run_drill

## `scripts/promotion_evaluate.py`

**Purpose**: Evaluate promotion readiness from anneal results payloads.
**Lines of code**: 190
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path, sys, typing.Any, typing.Dict, typing.List; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args(argv: list[str] | None = None) -> argparse.Namespace` — No docstring. (line 15)
- `_load_payload(path: Path | None) -> Dict[str, Any]` — No docstring. (line 50)
- `_derive_status(results: List[Dict[str, Any]]) -> str` — No docstring. (line 60)
- `_collect_reasons(results: List[Dict[str, Any]]) -> List[str]` — No docstring. (line 75)
- `evaluate(payload: Dict[str, Any]) -> Dict[str, Any]` — No docstring. (line 91)
- `_print_human(summary: Dict[str, Any]) -> None` — No docstring. (line 147)
- `main(argv: list[str] | None = None) -> int` — No docstring. (line 167)

### Constants and Configuration
- `DEFAULT_INPUT_PATH` = Path('artifacts/m7/anneal_results.json') (line 12)

### Data Flow
- Primary inputs: argv, path, payload, results, summary
- Return payloads: Dict[str, Any], List[str], None, argparse.Namespace, int, str
- Evaluates conditions or invariants via evaluate
- Loads configuration or datasets from disk via _load_payload

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: _collect_reasons, _derive_status, _load_payload, _print_human, evaluate, main, parse_args

## `scripts/reward_summary.py`

**Purpose**: Summarise reward breakdown telemetry for operations teams.
**Lines of code**: 323
**Dependencies**: stdlib=__future__.annotations, argparse, collections.defaultdict, dataclasses.dataclass, json, pathlib.Path, sys, typing.Iterable, typing.Iterator, typing.Mapping, typing.Sequence; external=None; internal=None
**Related modules**: None

### Classes
- `ComponentStats` (bases: object; decorators: dataclass) — No class docstring provided. (line 16)
  - Attributes:
    - name=`count`, type=`int`, default=`0` (line 17)
    - name=`total`, type=`float`, default=`0.0` (line 18)
    - name=`minimum`, type=`float`, default=`float('inf')` (line 19)
    - name=`maximum`, type=`float`, default=`float('-inf')` (line 20)
  - Methods:
    - `update(self, value: float) -> None` — No docstring. (line 22)
    - `mean(self) -> float` — No docstring. (line 30)
    - `as_dict(self) -> dict[str, float | int]` — No docstring. (line 35)
- `RewardAggregator` (bases: object; decorators: None) — Aggregate reward breakdowns from telemetry payloads. (line 46)
  - Methods:
    - `__init__(self) -> None` — No docstring. (line 49)
    - `add_payload(self, payload: Mapping[str, object], source: str) -> None` — No docstring. (line 58)
    - `summary(self) -> dict[str, object]` — No docstring. (line 85)

### Functions
- `_is_number(value: object) -> bool` — No docstring. (line 108)
- `iter_payloads(path: Path) -> Iterator[tuple[Mapping[str, object], str]]` — No docstring. (line 112)
- `collect_statistics(paths: Sequence[Path]) -> RewardAggregator` — No docstring. (line 138)
- `render_text(summary: Mapping[str, object], *, top: int, agent_filters: set[str] | None) -> str` — No docstring. (line 146)
- `render_markdown(summary: Mapping[str, object], *, top: int, agent_filters: set[str] | None) -> str` — No docstring. (line 218)
- `render_json(summary: Mapping[str, object]) -> str` — No docstring. (line 273)
- `parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace` — No docstring. (line 277)
- `main(argv: Sequence[str] | None = None) -> int` — No docstring. (line 301)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_filters, argv, path, paths, payload, source, summary, top, value
- Return payloads: Iterator[tuple[Mapping[str, object], str]], None, RewardAggregator, argparse.Namespace, bool, dict[str, float | int], dict[str, object], float, int, str
- Loads configuration or datasets from disk via RewardAggregator.add_payload, iter_payloads
- Updates internal caches or trackers via ComponentStats.update

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: ComponentStats.as_dict, ComponentStats.mean, ComponentStats.update, RewardAggregator.__init__, RewardAggregator.add_payload, RewardAggregator.summary, _is_number, collect_statistics, iter_payloads, main, parse_args, render_json, render_markdown, render_text

## `scripts/run_anneal_rehearsal.py`

**Purpose**: Run BC + anneal rehearsal using production manifests and capture artefacts.
**Lines of code**: 111
**Dependencies**: stdlib=__future__.annotations, argparse, importlib.util, json, pathlib.Path, sys, typing.Dict; external=promotion_evaluate; internal=townlet.config.load_config, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.runner.TrainingHarness
**Related modules**: townlet.config.load_config, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.runner.TrainingHarness

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 20)
- `run_rehearsal(config_path: Path, manifest_path: Path, log_dir: Path) -> Dict[str, object]` — No docstring. (line 49)
- `evaluate_summary(summary: Dict[str, object]) -> Dict[str, object]` — No docstring. (line 76)
- `main() -> None` — No docstring. (line 100)

### Constants and Configuration
- `DEFAULT_CONFIG` = Path('artifacts/m5/acceptance/config_idle_v1.yaml') (line 15)
- `DEFAULT_MANIFEST` = Path('data/bc_datasets/manifests/idle_v1.json') (line 16)
- `DEFAULT_LOG_DIR` = Path('artifacts/m5/acceptance/logs') (line 17)

### Data Flow
- Primary inputs: config_path, log_dir, manifest_path, summary
- Return payloads: Dict[str, object], None, argparse.Namespace
- Evaluates conditions or invariants via evaluate_summary

### Integration Points
- External: promotion_evaluate
- Internal: townlet.config.load_config, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.runner.TrainingHarness

### Code Quality Notes
- Missing docstrings: evaluate_summary, main, parse_args, run_rehearsal

## `scripts/run_employment_smoke.py`

**Purpose**: Employment loop smoke test runner for R2 mitigation.
**Lines of code**: 81
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path, typing.Any, typing.Dict, typing.List; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 13)
- `run_smoke(config_path: Path, ticks: int, enforce: bool) -> Dict[str, Any]` — No docstring. (line 36)
- `main() -> None` — No docstring. (line 73)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config_path, enforce, ticks
- Return payloads: Dict[str, Any], None, argparse.Namespace
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop

### Code Quality Notes
- Missing docstrings: main, parse_args, run_smoke

## `scripts/run_mixed_soak.py`

**Purpose**: Run alternating replay/rollout PPO cycles for soak testing.
**Lines of code**: 110
**Dependencies**: stdlib=__future__.annotations, argparse, pathlib.Path, sys; external=None; internal=townlet.config.loader.load_config, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.runner.TrainingHarness
**Related modules**: townlet.config.loader.load_config, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.runner.TrainingHarness

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 18)
- `main() -> None` — No docstring. (line 72)

### Constants and Configuration
- `ROOT` = Path(__file__).resolve().parents[1] (line 8)
- `SRC` = ROOT / 'src' (line 9)

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, argparse.Namespace
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.loader.load_config, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.runner.TrainingHarness

### Code Quality Notes
- Missing docstrings: main, parse_args

## `scripts/run_replay.py`

**Purpose**: Utility to replay observation/telemetry samples for analysis or tutorials.
**Lines of code**: 84
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path, typing.Any, typing.Dict; external=numpy; internal=townlet.policy.replay.load_replay_sample
**Related modules**: townlet.policy.replay.load_replay_sample

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 14)
- `render_observation(sample: Dict[str, Any]) -> None` — No docstring. (line 41)
- `inspect_telemetry(path: Path) -> None` — No docstring. (line 54)
- `main() -> None` — No docstring. (line 71)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: path, sample
- Return payloads: None, argparse.Namespace
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: numpy
- Internal: townlet.policy.replay.load_replay_sample

### Code Quality Notes
- Missing docstrings: inspect_telemetry, main, parse_args, render_observation

## `scripts/run_simulation.py`

**Purpose**: Run a headless Townlet simulation loop for debugging.
**Lines of code**: 31
**Dependencies**: stdlib=__future__.annotations, argparse, pathlib.Path; external=None; internal=townlet.config.loader.load_config, townlet.core.sim_loop.SimulationLoop
**Related modules**: townlet.config.loader.load_config, townlet.core.sim_loop.SimulationLoop

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 11)
- `main() -> None` — No docstring. (line 23)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, argparse.Namespace
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.loader.load_config, townlet.core.sim_loop.SimulationLoop

### Code Quality Notes
- Missing docstrings: main, parse_args

## `scripts/run_training.py`

**Purpose**: CLI entry point for training Townlet policies.
**Lines of code**: 466
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path; external=None; internal=townlet.config.PPOConfig, townlet.config.loader.load_config, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.runner.TrainingHarness
**Related modules**: townlet.config.PPOConfig, townlet.config.loader.load_config, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.runner.TrainingHarness

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 14)
- `_collect_ppo_overrides(args: argparse.Namespace) -> dict[str, object]` — No docstring. (line 224)
- `_apply_ppo_overrides(config, overrides: dict[str, object]) -> None` — No docstring. (line 247)
- `_build_dataset_config_from_args(args: argparse.Namespace, default_manifest: Path | None) -> ReplayDatasetConfig | None` — No docstring. (line 253)
- `main() -> None` — No docstring. (line 279)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: args, config, default_manifest, overrides
- Return payloads: None, ReplayDatasetConfig | None, argparse.Namespace, dict[str, object]
- Applies world or agent state updates via _apply_ppo_overrides
- Builds derived structures or observations via _build_dataset_config_from_args

### Integration Points
- External: None
- Internal: townlet.config.PPOConfig, townlet.config.loader.load_config, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.runner.TrainingHarness

### Code Quality Notes
- Missing docstrings: _apply_ppo_overrides, _build_dataset_config_from_args, _collect_ppo_overrides, main, parse_args

## `scripts/telemetry_check.py`

**Purpose**: Validate Townlet telemetry payloads against known schema versions.
**Lines of code**: 84
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path, typing.Any, typing.Dict; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 32)
- `load_payload(path: Path) -> Dict[str, Any]` — No docstring. (line 43)
- `validate(payload: Dict[str, Any], schema_version: str) -> None` — No docstring. (line 50)
- `main() -> None` — No docstring. (line 73)

### Constants and Configuration
- `SUPPORTED_SCHEMAS` = {'0.2.0': {'employment_keys': {'pending', 'pending_count', 'exits_today', 'daily_exit_cap', 'queue_limit', 'review_window'}, 'job_required_keys': {'job_id', 'on_shift', 'wallet', 'shift_state', 'attendance_ratio', 'late_ticks_today', 'wages_withheld'}}} (line 9)

### Data Flow
- Primary inputs: path, payload, schema_version
- Return payloads: Dict[str, Any], None, argparse.Namespace
- Loads configuration or datasets from disk via load_payload
- Validates inputs or configuration via validate

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: load_payload, main, parse_args, validate

## `scripts/telemetry_summary.py`

**Purpose**: Produce summaries for PPO telemetry logs.
**Lines of code**: 338
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path, typing.Sequence; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 10)
- `load_records(path: Path) -> list[dict[str, object]]` — No docstring. (line 33)
- `load_baseline(path: Path | None) -> dict[str, float] | None` — No docstring. (line 50)
- `summarise(records: Sequence[dict[str, object]], baseline: dict[str, float] | None) -> dict[str, object]` — No docstring. (line 59)
- `_format_optional_float(value: object, precision: int = 3) -> str` — No docstring. (line 183)
- `render_text(summary: dict[str, object]) -> str` — No docstring. (line 192)
- `render_markdown(summary: dict[str, object]) -> str` — No docstring. (line 263)
- `render(summary: dict[str, object], fmt: str) -> str` — No docstring. (line 319)
- `main() -> None` — No docstring. (line 327)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: baseline, fmt, path, precision, records, summary, value
- Return payloads: None, argparse.Namespace, dict[str, float] | None, dict[str, object], list[dict[str, object]], str
- Loads configuration or datasets from disk via load_baseline, load_records
- Records metrics or histories via load_records
- Summarises metrics for review via summarise

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: _format_optional_float, load_baseline, load_records, main, parse_args, render, render_markdown, render_text, summarise

## `scripts/telemetry_watch.py`

**Purpose**: Tail PPO telemetry logs and alert on metric thresholds.
**Lines of code**: 525
**Dependencies**: stdlib=__future__.annotations, argparse, json, pathlib.Path, sys, time, typing.Iterator; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `build_parser() -> argparse.ArgumentParser` — No docstring. (line 60)
- `parse_args() -> argparse.Namespace` — No docstring. (line 229)
- `parse_args_from_list(argv: list[str]) -> argparse.Namespace` — No docstring. (line 233)
- `stream_records(path: Path, follow: bool, interval: float) -> Iterator[dict[str, float]]` — No docstring. (line 237)
- `_parse_health_line(line: str) -> dict[str, float]` — No docstring. (line 284)
- `stream_health_records(path: Path, follow: bool, interval: float) -> Iterator[dict[str, float]]` — No docstring. (line 315)
- `check_thresholds(record: dict[str, object], args: argparse.Namespace) -> None` — No docstring. (line 341)
- `check_health_thresholds(record: dict[str, float], args: argparse.Namespace) -> None` — No docstring. (line 445)
- `main(args: list[str] | None = None) -> None` — No docstring. (line 473)

### Constants and Configuration
- `MODES` = {'ppo', 'health'} (line 11)
- `REQUIRED_KEYS` = {'epoch', 'loss_total', 'kl_divergence', 'grad_norm', 'batch_entropy_mean', 'reward_advantage_corr', 'log_stream_offset', 'data_mode', 'queue_conflict_events', 'queue_conflict_intensity_sum', 'shared_meal_events', 'late_help_events', 'shift_takeover_events', 'chat_success_events', 'chat_failure_events', 'chat_quality_mean'} (line 13)
- `OPTIONAL_NUMERIC_KEYS` = {'anneal_cycle', 'anneal_bc_accuracy', 'anneal_bc_threshold', 'anneal_loss_baseline', 'anneal_queue_baseline', 'anneal_intensity_baseline'} (line 32)
- `OPTIONAL_BOOL_KEYS` = {'anneal_bc_passed', 'anneal_loss_flag', 'anneal_queue_flag', 'anneal_intensity_flag'} (line 41)
- `OPTIONAL_TEXT_KEYS` = {'anneal_stage', 'anneal_dataset'} (line 48)
- `OPTIONAL_EVENT_KEYS` = {'utility_outage_events', 'shower_complete_events', 'sleep_complete_events'} (line 53)

### Data Flow
- Primary inputs: args, argv, follow, interval, line, path, record
- Return payloads: Iterator[dict[str, float]], None, argparse.ArgumentParser, argparse.Namespace, dict[str, float]
- Builds derived structures or observations via build_parser
- Records metrics or histories via stream_health_records, stream_records

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: _parse_health_line, build_parser, check_health_thresholds, check_thresholds, main, parse_args, parse_args_from_list, stream_health_records, stream_records

## `scripts/validate_affordances.py`

**Purpose**: Validate affordance manifest files for schema compliance.
**Lines of code**: 126
**Dependencies**: stdlib=__future__.annotations, argparse, pathlib.Path, sys, typing.Iterable, typing.List; external=None; internal=townlet.config.affordance_manifest.AffordanceManifest, townlet.config.affordance_manifest.AffordanceManifestError, townlet.config.affordance_manifest.load_affordance_manifest, townlet.world.preconditions.PreconditionSyntaxError, townlet.world.preconditions.compile_preconditions
**Related modules**: townlet.config.affordance_manifest.AffordanceManifest, townlet.config.affordance_manifest.AffordanceManifestError, townlet.config.affordance_manifest.load_affordance_manifest, townlet.world.preconditions.PreconditionSyntaxError, townlet.world.preconditions.compile_preconditions

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 27)
- `discover_manifests(inputs: Iterable[str]) -> List[Path]` — No docstring. (line 48)
- `validate_manifest(path: Path) -> AffordanceManifest` — No docstring. (line 74)
- `main() -> int` — No docstring. (line 93)

### Constants and Configuration
- `DEFAULT_SEARCH_ROOT` = Path('configs/affordances') (line 24)

### Data Flow
- Primary inputs: inputs, path
- Return payloads: AffordanceManifest, List[Path], argparse.Namespace, int
- Validates inputs or configuration via validate_manifest

### Integration Points
- External: None
- Internal: townlet.config.affordance_manifest.AffordanceManifest, townlet.config.affordance_manifest.AffordanceManifestError, townlet.config.affordance_manifest.load_affordance_manifest, townlet.world.preconditions.PreconditionSyntaxError, townlet.world.preconditions.compile_preconditions

### Code Quality Notes
- Missing docstrings: discover_manifests, main, parse_args, validate_manifest

## `scripts/validate_ppo_telemetry.py`

**Purpose**: Validate PPO telemetry NDJSON logs and report baseline drift.
**Lines of code**: 248
**Dependencies**: stdlib=__future__.annotations, argparse, json, math, pathlib.Path, typing.Iterable, typing.List; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring. (line 47)
- `_ensure_numeric(key: str, value: object) -> None` — No docstring. (line 69)
- `_load_records(path: Path) -> List[dict[str, object]]` — No docstring. (line 74)
- `_validate_record(record: dict[str, object], source: Path) -> None` — No docstring. (line 108)
- `_load_baseline(path: Path | None) -> dict[str, float] | None` — No docstring. (line 157)
- `_relative_delta(delta: float, base_value: float) -> float | None` — No docstring. (line 174)
- `_report_drift(records: list[dict[str, object]], baseline: dict[str, float], threshold: float | None, include_relative: bool) -> None` — No docstring. (line 180)
- `validate_logs(paths: Iterable[Path], baseline_path: Path | None, drift_threshold: float | None, include_relative: bool) -> None` — No docstring. (line 226)
- `main() -> None` — No docstring. (line 242)

### Constants and Configuration
- `BASE_REQUIRED_KEYS` = {'epoch', 'updates', 'transitions', 'loss_policy', 'loss_value', 'loss_entropy', 'loss_total', 'clip_fraction', 'clip_fraction_max', 'clip_triggered_minibatches', 'adv_mean', 'adv_std', 'adv_zero_std_batches', 'adv_min_std', 'grad_norm', 'kl_divergence', 'telemetry_version', 'lr', 'steps'} (line 10)
- `CONFLICT_KEYS` = {'conflict.rivalry_max_mean_avg', 'conflict.rivalry_max_max_avg', 'conflict.rivalry_avoid_count_mean_avg', 'conflict.rivalry_avoid_count_max_avg'} (line 32)
- `BASELINE_KEYS` = {'baseline_sample_count', 'baseline_reward_mean', 'baseline_reward_sum', 'baseline_reward_sum_mean'} (line 39)
- `REQUIRED_V1_1_NUMERIC_KEYS` = {'epoch_duration_sec', 'cycle_id', 'batch_entropy_mean', 'batch_entropy_std', 'grad_norm_max', 'kl_divergence_max', 'reward_advantage_corr', 'rollout_ticks', 'log_stream_offset', 'queue_conflict_events', 'queue_conflict_intensity_sum'} (line 91)
- `REQUIRED_V1_1_STRING_KEYS` = {'data_mode'} (line 105)

### Data Flow
- Primary inputs: base_value, baseline, baseline_path, delta, drift_threshold, include_relative, key, path, paths, record, records, source
- Return payloads: List[dict[str, object]], None, argparse.Namespace, dict[str, float] | None, float | None
- Loads configuration or datasets from disk via _load_baseline, _load_records
- Records metrics or histories via _load_records, _validate_record
- Validates inputs or configuration via _validate_record, validate_logs

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: _ensure_numeric, _load_baseline, _load_records, _relative_delta, _report_drift, _validate_record, main, parse_args, validate_logs

## `src/townlet/__init__.py`

**Purpose**: Townlet simulation package.
**Lines of code**: 9
**Dependencies**: stdlib=__future__.annotations; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/agents/__init__.py`

**Purpose**: Agent state models.
**Lines of code**: 19
**Dependencies**: stdlib=__future__.annotations; external=models.AgentState, models.Personality, models.RelationshipEdge, relationship_modifiers.RelationshipDelta, relationship_modifiers.RelationshipEvent, relationship_modifiers.apply_personality_modifiers; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: models.AgentState, models.Personality, models.RelationshipEdge, relationship_modifiers.RelationshipDelta, relationship_modifiers.RelationshipEvent, relationship_modifiers.apply_personality_modifiers
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/agents/models.py`

**Purpose**: Agent-related dataclasses and helpers.
**Lines of code**: 31
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass, dataclasses.field; external=None; internal=None
**Related modules**: None

### Classes
- `Personality` (bases: object; decorators: dataclass) — No class docstring provided. (line 9)
  - Attributes:
    - name=`extroversion`, type=`float` (line 10)
    - name=`forgiveness`, type=`float` (line 11)
    - name=`ambition`, type=`float` (line 12)
- `RelationshipEdge` (bases: object; decorators: dataclass) — No class docstring provided. (line 16)
  - Attributes:
    - name=`other_id`, type=`str` (line 17)
    - name=`trust`, type=`float` (line 18)
    - name=`familiarity`, type=`float` (line 19)
    - name=`rivalry`, type=`float` (line 20)
- `AgentState` (bases: object; decorators: dataclass) — Canonical agent state used across modules. (line 24)
  - Attributes:
    - name=`agent_id`, type=`str` (line 27)
    - name=`needs`, type=`dict[str, float]` (line 28)
    - name=`wallet`, type=`float` (line 29)
    - name=`personality`, type=`Personality` (line 30)
    - name=`relationships`, type=`list[RelationshipEdge]`, default=`field(default_factory=list)` (line 31)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/agents/relationship_modifiers.py`

**Purpose**: Relationship delta adjustment helpers respecting personality flags.
**Lines of code**: 102
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass, typing.Literal; external=None; internal=townlet.agents.models.Personality
**Related modules**: townlet.agents.models.Personality

### Classes
- `RelationshipDelta` (bases: object; decorators: dataclass(frozen=True)) — Represents trust/familiarity/rivalry deltas for a single event. (line 23)
  - Attributes:
    - name=`trust`, type=`float`, default=`0.0` (line 26)
    - name=`familiarity`, type=`float`, default=`0.0` (line 27)
    - name=`rivalry`, type=`float`, default=`0.0` (line 28)

### Functions
- `apply_personality_modifiers(*, delta: RelationshipDelta, personality: Personality, event: RelationshipEvent, enabled: bool) -> RelationshipDelta` — Adjust ``delta`` based on personality traits when enabled. (line 31)
- `_apply_forgiveness(value: float, forgiveness: float) -> float` — No docstring. (line 68)
- `_apply_extroversion(value: float, extroversion: float) -> float` — No docstring. (line 79)
- `_apply_ambition(value: float, ambition: float) -> float` — No docstring. (line 84)
- `_clamp(value: float, low: float, high: float) -> float` — No docstring. (line 94)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: ambition, delta, enabled, event, extroversion, forgiveness, high, low, personality, value
- Return payloads: RelationshipDelta, float
- Applies world or agent state updates via _apply_ambition, _apply_extroversion, _apply_forgiveness, apply_personality_modifiers

### Integration Points
- External: None
- Internal: townlet.agents.models.Personality

### Code Quality Notes
- Missing docstrings: _apply_ambition, _apply_extroversion, _apply_forgiveness, _clamp

## `src/townlet/config/__init__.py`

**Purpose**: Config utilities for Townlet.
**Lines of code**: 97
**Dependencies**: stdlib=__future__.annotations; external=loader.AffordanceConfig, loader.AnnealStage, loader.ArrangedMeetEventConfig, loader.BCTrainingSettings, loader.BlackoutEventConfig, loader.ConflictConfig, loader.ConsoleMode, loader.CuriosityToggle, loader.EmbeddingAllocatorConfig, loader.EmploymentConfig, loader.FloatRange, loader.IntRange, loader.LifecycleToggle, loader.NarrationThrottleConfig, loader.ObservationVariant, loader.ObservationsConfig, loader.OptionThrashCanaryConfig, loader.OutageEventConfig, loader.PPOConfig, loader.PerturbationEventConfig, loader.PerturbationKind, loader.PerturbationSchedulerConfig, loader.PriceSpikeEventConfig, loader.PromotionGateConfig, loader.QueueFairnessConfig, loader.RewardVarianceCanaryConfig, loader.RivalryConfig, loader.SimulationConfig, loader.SnapshotAutosaveConfig, loader.SnapshotConfig, loader.SnapshotGuardrailsConfig, loader.SnapshotIdentityConfig, loader.SnapshotMigrationsConfig, loader.SnapshotStorageConfig, loader.SocialRewardScheduleEntry, loader.SocialRewardStage, loader.StarvationCanaryConfig, loader.TelemetryBufferConfig, loader.TelemetryConfig, loader.TelemetryRetryPolicy, loader.TelemetryTransportConfig, loader.TrainingConfig, loader.TrainingSource, loader.load_config; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: loader.AffordanceConfig, loader.AnnealStage, loader.ArrangedMeetEventConfig, loader.BCTrainingSettings, loader.BlackoutEventConfig, loader.ConflictConfig, loader.ConsoleMode, loader.CuriosityToggle, loader.EmbeddingAllocatorConfig, loader.EmploymentConfig, loader.FloatRange, loader.IntRange, loader.LifecycleToggle, loader.NarrationThrottleConfig, loader.ObservationVariant, loader.ObservationsConfig, loader.OptionThrashCanaryConfig, loader.OutageEventConfig, loader.PPOConfig, loader.PerturbationEventConfig, loader.PerturbationKind, loader.PerturbationSchedulerConfig, loader.PriceSpikeEventConfig, loader.PromotionGateConfig, loader.QueueFairnessConfig, loader.RewardVarianceCanaryConfig, loader.RivalryConfig, loader.SimulationConfig, loader.SnapshotAutosaveConfig, loader.SnapshotConfig, loader.SnapshotGuardrailsConfig, loader.SnapshotIdentityConfig, loader.SnapshotMigrationsConfig, loader.SnapshotStorageConfig, loader.SocialRewardScheduleEntry, loader.SocialRewardStage, loader.StarvationCanaryConfig, loader.TelemetryBufferConfig, loader.TelemetryConfig, loader.TelemetryRetryPolicy, loader.TelemetryTransportConfig, loader.TrainingConfig, loader.TrainingSource, loader.load_config
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/config/affordance_manifest.py`

**Purpose**: Utilities for validating affordance manifest files.
**Lines of code**: 316
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterable, collections.abc.Mapping, dataclasses.dataclass, hashlib, logging, pathlib.Path; external=yaml; internal=None
**Related modules**: None

### Classes
- `ManifestObject` (bases: object; decorators: dataclass(frozen=True)) — Represents an interactive object entry from the manifest. (line 17)
  - Attributes:
    - name=`object_id`, type=`str` (line 20)
    - name=`object_type`, type=`str` (line 21)
    - name=`stock`, type=`dict[str, int]` (line 22)
    - name=`position`, type=`tuple[int, int] | None`, default=`None` (line 23)
- `ManifestAffordance` (bases: object; decorators: dataclass(frozen=True)) — Represents an affordance definition with preconditions and hooks. (line 27)
  - Attributes:
    - name=`affordance_id`, type=`str` (line 30)
    - name=`object_type`, type=`str` (line 31)
    - name=`duration`, type=`int` (line 32)
    - name=`effects`, type=`dict[str, float]` (line 33)
    - name=`preconditions`, type=`list[str]` (line 34)
    - name=`hooks`, type=`dict[str, list[str]]` (line 35)
- `AffordanceManifest` (bases: object; decorators: dataclass(frozen=True)) — Normalised manifest contents and checksum metadata. (line 39)
  - Attributes:
    - name=`path`, type=`Path` (line 42)
    - name=`checksum`, type=`str` (line 43)
    - name=`objects`, type=`list[ManifestObject]` (line 44)
    - name=`affordances`, type=`list[ManifestAffordance]` (line 45)
  - Methods:
    - `object_count(self) -> int` — No docstring. (line 48)
    - `affordance_count(self) -> int` — No docstring. (line 52)
- `AffordanceManifestError` (bases: ValueError; decorators: None) — Raised when an affordance manifest fails validation. (line 56)

### Functions
- `load_affordance_manifest(path: Path) -> AffordanceManifest` — Load and validate an affordance manifest, returning structured entries. (line 63)
- `_parse_object_entry(entry: Mapping[str, object], path: Path, index: int) -> ManifestObject` — No docstring. (line 123)
- `_parse_affordance_entry(entry: Mapping[str, object], path: Path, index: int) -> ManifestAffordance` — No docstring. (line 161)
- `_parse_position(value: object, *, path: Path, index: int, entry_id: str) -> tuple[int, int] | None` — No docstring. (line 240)
- `_parse_string_list(value: object, *, field: str, path: Path, index: int, entry_id: str) -> list[str]` — No docstring. (line 263)
- `_require_string(entry: Mapping[str, object], field: str, path: Path, index: int) -> str` — No docstring. (line 293)
- `_ensure_unique(entry_id: str, seen: set[str], path: Path, index: int) -> None` — No docstring. (line 311)

### Constants and Configuration
- `_ALLOWED_HOOK_KEYS` = {'before', 'after', 'fail'} (line 60)

### Data Flow
- Primary inputs: entry, entry_id, field, index, path, seen, value
- Return payloads: AffordanceManifest, ManifestAffordance, ManifestObject, None, int, list[str], str, tuple[int, int] | None
- Loads configuration or datasets from disk via load_affordance_manifest

### Integration Points
- External: yaml
- Internal: None

### Code Quality Notes
- Missing docstrings: AffordanceManifest.affordance_count, AffordanceManifest.object_count, _ensure_unique, _parse_affordance_entry, _parse_object_entry, _parse_position, _parse_string_list, _require_string

## `src/townlet/config/loader.py`

**Purpose**: Configuration loader and validation layer.
**Lines of code**: 807
**Dependencies**: stdlib=__future__.annotations, collections.abc.Mapping, enum.Enum, importlib, pathlib.Path, re, typing.Annotated, typing.Literal; external=pydantic.BaseModel, pydantic.ConfigDict, pydantic.Field, pydantic.ValidationError, pydantic.model_validator, yaml; internal=townlet.snapshots.register_migration
**Related modules**: townlet.snapshots.register_migration

### Classes
- `StageFlags` (bases: BaseModel; decorators: None) — No class docstring provided. (line 30)
  - Attributes:
    - name=`relationships`, type=`RelationshipStage`, default=`'OFF'` (line 31)
    - name=`social_rewards`, type=`SocialRewardStage`, default=`'OFF'` (line 32)
- `SystemFlags` (bases: BaseModel; decorators: None) — No class docstring provided. (line 35)
  - Attributes:
    - name=`lifecycle`, type=`LifecycleToggle`, default=`'on'` (line 36)
    - name=`observations`, type=`ObservationVariant`, default=`'hybrid'` (line 37)
- `TrainingFlags` (bases: BaseModel; decorators: None) — No class docstring provided. (line 40)
  - Attributes:
    - name=`curiosity`, type=`CuriosityToggle`, default=`'phase_A'` (line 41)
- `PolicyRuntimeConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 44)
  - Attributes:
    - name=`option_commit_ticks`, type=`int`, default=`Field(15, ge=0, le=100000)` (line 45)
- `ConsoleFlags` (bases: BaseModel; decorators: None) — No class docstring provided. (line 48)
  - Attributes:
    - name=`mode`, type=`ConsoleMode`, default=`'viewer'` (line 49)
- `FeatureFlags` (bases: BaseModel; decorators: None) — No class docstring provided. (line 52)
  - Attributes:
    - name=`stages`, type=`StageFlags` (line 53)
    - name=`systems`, type=`SystemFlags` (line 54)
    - name=`training`, type=`TrainingFlags` (line 55)
    - name=`console`, type=`ConsoleFlags` (line 56)
    - name=`relationship_modifiers`, type=`bool`, default=`False` (line 57)
- `NeedsWeights` (bases: BaseModel; decorators: None) — No class docstring provided. (line 60)
  - Attributes:
    - name=`hunger`, type=`float`, default=`Field(1.0, ge=0.5, le=2.0)` (line 61)
    - name=`hygiene`, type=`float`, default=`Field(0.6, ge=0.2, le=1.0)` (line 62)
    - name=`energy`, type=`float`, default=`Field(0.8, ge=0.4, le=1.5)` (line 63)
- `SocialRewardWeights` (bases: BaseModel; decorators: None) — No class docstring provided. (line 66)
  - Attributes:
    - name=`C1_chat_base`, type=`float`, default=`Field(0.01, ge=0.0, le=0.05)` (line 67)
    - name=`C1_coeff_trust`, type=`float`, default=`Field(0.3, ge=0.0, le=1.0)` (line 68)
    - name=`C1_coeff_fam`, type=`float`, default=`Field(0.2, ge=0.0, le=1.0)` (line 69)
    - name=`C2_avoid_conflict`, type=`float`, default=`Field(0.005, ge=0.0, le=0.02)` (line 70)
- `RewardClips` (bases: BaseModel; decorators: None) — No class docstring provided. (line 73)
  - Attributes:
    - name=`clip_per_tick`, type=`float`, default=`Field(0.2, ge=0.01, le=1.0)` (line 74)
    - name=`clip_per_episode`, type=`float`, default=`Field(50, ge=1, le=200)` (line 75)
    - name=`no_positive_within_death_ticks`, type=`int`, default=`Field(10, ge=0, le=200)` (line 76)
- `RewardsConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 79)
  - Attributes:
    - name=`needs_weights`, type=`NeedsWeights` (line 80)
    - name=`decay_rates`, type=`dict[str, float]`, default=`Field(default_factory=lambda: {'hunger': 0.01, 'hygiene': 0.005, 'energy': 0.008})` (line 81)
    - name=`punctuality_bonus`, type=`float`, default=`Field(0.05, ge=0.0, le=0.1)` (line 88)
    - name=`wage_rate`, type=`float`, default=`Field(0.01, ge=0.0, le=0.05)` (line 89)
    - name=`survival_tick`, type=`float`, default=`Field(0.002, ge=0.0, le=0.01)` (line 90)
    - name=`faint_penalty`, type=`float`, default=`Field(-1.0, ge=-5.0, le=0.0)` (line 91)
    - name=`eviction_penalty`, type=`float`, default=`Field(-2.0, ge=-5.0, le=0.0)` (line 92)
    - name=`social`, type=`SocialRewardWeights`, default=`SocialRewardWeights()` (line 93)
    - name=`clip`, type=`RewardClips`, default=`RewardClips()` (line 94)
  - Methods:
    - `_sanity_check_punctuality(self) -> 'RewardsConfig'` — No docstring. (line 97)
- `ShapingConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 105)
  - Attributes:
    - name=`use_potential`, type=`bool`, default=`True` (line 106)
- `CuriosityConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 109)
  - Attributes:
    - name=`phase_A_weight`, type=`float`, default=`Field(0.02, ge=0.0, le=0.1)` (line 110)
    - name=`decay_by_milestone`, type=`Literal['M2', 'never']`, default=`'M2'` (line 111)
- `QueueFairnessConfig` (bases: BaseModel; decorators: None) — Queue fairness tuning parameters (see REQUIREMENTS#5). (line 114)
  - Attributes:
    - name=`cooldown_ticks`, type=`int`, default=`Field(60, ge=0, le=600)` (line 117)
    - name=`ghost_step_after`, type=`int`, default=`Field(3, ge=0, le=100)` (line 118)
    - name=`age_priority_weight`, type=`float`, default=`Field(0.1, ge=0.0, le=1.0)` (line 119)
- `RivalryConfig` (bases: BaseModel; decorators: None) — Conflict/rivalry tuning knobs (see REQUIREMENTS#5). (line 122)
  - Attributes:
    - name=`increment_per_conflict`, type=`float`, default=`Field(0.15, ge=0.0, le=1.0)` (line 125)
    - name=`decay_per_tick`, type=`float`, default=`Field(0.005, ge=0.0, le=1.0)` (line 126)
    - name=`min_value`, type=`float`, default=`Field(0.0, ge=0.0, le=1.0)` (line 127)
    - name=`max_value`, type=`float`, default=`Field(1.0, ge=0.0, le=1.0)` (line 128)
    - name=`avoid_threshold`, type=`float`, default=`Field(0.7, ge=0.0, le=1.0)` (line 129)
    - name=`eviction_threshold`, type=`float`, default=`Field(0.05, ge=0.0, le=1.0)` (line 130)
    - name=`max_edges`, type=`int`, default=`Field(6, ge=1, le=32)` (line 131)
    - name=`ghost_step_boost`, type=`float`, default=`Field(1.5, ge=0.0, le=5.0)` (line 132)
    - name=`handover_boost`, type=`float`, default=`Field(0.4, ge=0.0, le=5.0)` (line 133)
    - name=`queue_length_boost`, type=`float`, default=`Field(0.25, ge=0.0, le=2.0)` (line 134)
  - Methods:
    - `_validate_ranges(self) -> 'RivalryConfig'` — No docstring. (line 137)
- `ConflictConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 147)
  - Attributes:
    - name=`rivalry`, type=`RivalryConfig`, default=`RivalryConfig()` (line 148)
- `PPOConfig` (bases: BaseModel; decorators: None) — Config for PPO training hyperparameters. (line 151)
  - Attributes:
    - name=`learning_rate`, type=`float`, default=`Field(0.0003, gt=0.0)` (line 154)
    - name=`clip_param`, type=`float`, default=`Field(0.2, ge=0.0, le=1.0)` (line 155)
    - name=`value_loss_coef`, type=`float`, default=`Field(0.5, ge=0.0)` (line 156)
    - name=`entropy_coef`, type=`float`, default=`Field(0.01, ge=0.0)` (line 157)
    - name=`num_epochs`, type=`int`, default=`Field(4, ge=1, le=64)` (line 158)
    - name=`mini_batch_size`, type=`int`, default=`Field(32, ge=1)` (line 159)
    - name=`gae_lambda`, type=`float`, default=`Field(0.95, ge=0.0, le=1.0)` (line 160)
    - name=`gamma`, type=`float`, default=`Field(0.99, ge=0.0, le=1.0)` (line 161)
    - name=`max_grad_norm`, type=`float`, default=`Field(0.5, ge=0.0)` (line 162)
    - name=`value_clip`, type=`float`, default=`Field(0.2, ge=0.0, le=1.0)` (line 163)
    - name=`advantage_normalization`, type=`bool`, default=`True` (line 164)
    - name=`num_mini_batches`, type=`int`, default=`Field(4, ge=1, le=1024)` (line 165)
- `EmbeddingAllocatorConfig` (bases: BaseModel; decorators: None) — Embedding slot reuse guardrails (see REQUIREMENTS#3). (line 168)
  - Attributes:
    - name=`cooldown_ticks`, type=`int`, default=`Field(2000, ge=0, le=10000)` (line 171)
    - name=`reuse_warning_threshold`, type=`float`, default=`Field(0.05, ge=0.0, le=0.5)` (line 172)
    - name=`log_forced_reuse`, type=`bool`, default=`True` (line 173)
    - name=`max_slots`, type=`int`, default=`Field(64, ge=1, le=256)` (line 174)
- `HybridObservationConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 177)
  - Attributes:
    - name=`local_window`, type=`int`, default=`Field(11, ge=3)` (line 178)
    - name=`include_targets`, type=`bool`, default=`False` (line 179)
    - name=`time_ticks_per_day`, type=`int`, default=`Field(1440, ge=1)` (line 180)
  - Methods:
    - `_validate_window(self) -> 'HybridObservationConfig'` — No docstring. (line 183)
- `SocialSnippetConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 189)
  - Attributes:
    - name=`top_friends`, type=`int`, default=`Field(2, ge=0, le=8)` (line 190)
    - name=`top_rivals`, type=`int`, default=`Field(2, ge=0, le=8)` (line 191)
    - name=`embed_dim`, type=`int`, default=`Field(8, ge=1, le=32)` (line 192)
    - name=`include_aggregates`, type=`bool`, default=`True` (line 193)
  - Methods:
    - `_validate_totals(self) -> 'SocialSnippetConfig'` — No docstring. (line 196)
- `ObservationsConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 204)
  - Attributes:
    - name=`hybrid`, type=`HybridObservationConfig`, default=`HybridObservationConfig()` (line 205)
    - name=`social_snippet`, type=`SocialSnippetConfig`, default=`SocialSnippetConfig()` (line 206)
- `StarvationCanaryConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 209)
  - Attributes:
    - name=`window_ticks`, type=`int`, default=`Field(1000, ge=1, le=100000)` (line 210)
    - name=`max_incidents`, type=`int`, default=`Field(0, ge=0, le=10000)` (line 211)
    - name=`hunger_threshold`, type=`float`, default=`Field(0.05, ge=0.0, le=1.0)` (line 212)
    - name=`min_duration_ticks`, type=`int`, default=`Field(30, ge=1, le=10000)` (line 213)
- `RewardVarianceCanaryConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 216)
  - Attributes:
    - name=`window_ticks`, type=`int`, default=`Field(1000, ge=1, le=100000)` (line 217)
    - name=`max_variance`, type=`float`, default=`Field(0.25, ge=0.0)` (line 218)
    - name=`min_samples`, type=`int`, default=`Field(20, ge=1, le=100000)` (line 219)
- `OptionThrashCanaryConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 222)
  - Attributes:
    - name=`window_ticks`, type=`int`, default=`Field(600, ge=1, le=100000)` (line 223)
    - name=`max_switch_rate`, type=`float`, default=`Field(0.25, ge=0.0, le=10.0)` (line 224)
    - name=`min_samples`, type=`int`, default=`Field(10, ge=1, le=100000)` (line 225)
- `PromotionGateConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 228)
  - Attributes:
    - name=`required_passes`, type=`int`, default=`Field(2, ge=1, le=10)` (line 229)
    - name=`window_ticks`, type=`int`, default=`Field(1000, ge=1, le=100000)` (line 230)
    - name=`allowed_alerts`, type=`tuple[str, ...]`, default=`()` (line 231)
    - name=`model_config`, default=`ConfigDict(extra='forbid')` (line 233)
  - Methods:
    - `_coerce_allowed(cls, value: object) -> object` — No docstring. (line 236)
    - `_normalise(self) -> 'PromotionGateConfig'` — No docstring. (line 246)
- `LifecycleConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 251)
  - Attributes:
    - name=`respawn_delay_ticks`, type=`int`, default=`Field(0, ge=0, le=100000)` (line 252)
- `StabilityConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 255)
  - Attributes:
    - name=`affordance_fail_threshold`, type=`int`, default=`Field(5, ge=0, le=100)` (line 256)
    - name=`lateness_threshold`, type=`int`, default=`Field(3, ge=0, le=100)` (line 257)
    - name=`starvation`, type=`StarvationCanaryConfig`, default=`StarvationCanaryConfig()` (line 258)
    - name=`reward_variance`, type=`RewardVarianceCanaryConfig`, default=`RewardVarianceCanaryConfig()` (line 259)
    - name=`option_thrash`, type=`OptionThrashCanaryConfig`, default=`OptionThrashCanaryConfig()` (line 260)
    - name=`promotion`, type=`PromotionGateConfig`, default=`PromotionGateConfig()` (line 261)
  - Methods:
    - `as_dict(self) -> dict[str, object]` — No docstring. (line 263)
- `IntRange` (bases: BaseModel; decorators: None) — No class docstring provided. (line 274)
  - Attributes:
    - name=`min`, type=`int`, default=`Field(ge=0)` (line 275)
    - name=`max`, type=`int`, default=`Field(ge=0)` (line 276)
    - name=`model_config`, default=`ConfigDict(extra='forbid')` (line 278)
  - Methods:
    - `_coerce(cls, value: object) -> dict[str, int]` — No docstring. (line 281)
    - `_validate_bounds(self) -> 'IntRange'` — No docstring. (line 297)
- `FloatRange` (bases: BaseModel; decorators: None) — No class docstring provided. (line 303)
  - Attributes:
    - name=`min`, type=`float` (line 304)
    - name=`max`, type=`float` (line 305)
    - name=`model_config`, default=`ConfigDict(extra='forbid')` (line 307)
  - Methods:
    - `_coerce(cls, value: object) -> dict[str, float]` — No docstring. (line 310)
    - `_validate_bounds(self) -> 'FloatRange'` — No docstring. (line 326)
- `PerturbationKind` (bases: str, Enum; decorators: None) — No class docstring provided. (line 332)
  - Attributes:
    - name=`PRICE_SPIKE`, default=`'price_spike'` (line 333)
    - name=`BLACKOUT`, default=`'blackout'` (line 334)
    - name=`OUTAGE`, default=`'outage'` (line 335)
    - name=`ARRANGED_MEET`, default=`'arranged_meet'` (line 336)
- `BasePerturbationEventConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 339)
  - Attributes:
    - name=`kind`, type=`PerturbationKind` (line 340)
    - name=`probability_per_day`, type=`float`, default=`Field(0.0, ge=0.0, alias='prob_per_day')` (line 341)
    - name=`cooldown_ticks`, type=`int`, default=`Field(0, ge=0)` (line 342)
    - name=`duration`, type=`IntRange`, default=`Field(default_factory=lambda: IntRange(min=0, max=0))` (line 343)
    - name=`model_config`, default=`ConfigDict(extra='forbid', populate_by_name=True)` (line 345)
  - Methods:
    - `_normalise_duration(cls, values: dict[str, object]) -> dict[str, object]` — No docstring. (line 348)
- `PriceSpikeEventConfig` (bases: BasePerturbationEventConfig; decorators: None) — No class docstring provided. (line 354)
  - Attributes:
    - name=`kind`, type=`Literal[PerturbationKind.PRICE_SPIKE]`, default=`PerturbationKind.PRICE_SPIKE` (line 355)
    - name=`magnitude`, type=`FloatRange`, default=`Field(default_factory=lambda: FloatRange(min=1.0, max=1.0))` (line 356)
    - name=`targets`, type=`list[str]`, default=`Field(default_factory=list)` (line 357)
  - Methods:
    - `_normalise_magnitude(cls, values: dict[str, object]) -> dict[str, object]` — No docstring. (line 360)
- `BlackoutEventConfig` (bases: BasePerturbationEventConfig; decorators: None) — No class docstring provided. (line 366)
  - Attributes:
    - name=`kind`, type=`Literal[PerturbationKind.BLACKOUT]`, default=`PerturbationKind.BLACKOUT` (line 367)
    - name=`utility`, type=`Literal['power']`, default=`'power'` (line 368)
- `OutageEventConfig` (bases: BasePerturbationEventConfig; decorators: None) — No class docstring provided. (line 371)
  - Attributes:
    - name=`kind`, type=`Literal[PerturbationKind.OUTAGE]`, default=`PerturbationKind.OUTAGE` (line 372)
    - name=`utility`, type=`Literal['water']`, default=`'water'` (line 373)
- `ArrangedMeetEventConfig` (bases: BasePerturbationEventConfig; decorators: None) — No class docstring provided. (line 376)
  - Attributes:
    - name=`kind`, type=`Literal[PerturbationKind.ARRANGED_MEET]`, default=`PerturbationKind.ARRANGED_MEET` (line 377)
    - name=`target`, type=`str`, default=`Field(default='top_rivals')` (line 378)
    - name=`location`, type=`str`, default=`Field(default='cafe')` (line 379)
    - name=`max_participants`, type=`int`, default=`Field(2, ge=2)` (line 380)
- `PerturbationSchedulerConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 389)
  - Attributes:
    - name=`max_concurrent_events`, type=`int`, default=`Field(1, ge=1)` (line 390)
    - name=`global_cooldown_ticks`, type=`int`, default=`Field(0, ge=0)` (line 391)
    - name=`per_agent_cooldown_ticks`, type=`int`, default=`Field(0, ge=0)` (line 392)
    - name=`grace_window_ticks`, type=`int`, default=`Field(60, ge=0)` (line 393)
    - name=`window_ticks`, type=`int`, default=`Field(1440, ge=1)` (line 394)
    - name=`max_events_per_window`, type=`int`, default=`Field(1, ge=0)` (line 395)
    - name=`events`, type=`dict[str, PerturbationEventConfig]`, default=`Field(default_factory=dict)` (line 396)
    - name=`model_config`, default=`ConfigDict(extra='allow', populate_by_name=True)` (line 398)
  - Methods:
    - `event_list(self) -> list[PerturbationEventConfig]` — No docstring. (line 401)
- `AffordanceConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 405)
  - Attributes:
    - name=`affordances_file`, type=`str`, default=`Field('configs/affordances/core.yaml')` (line 406)
- `EmploymentConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 409)
  - Attributes:
    - name=`grace_ticks`, type=`int`, default=`Field(5, ge=0, le=120)` (line 410)
    - name=`absent_cutoff`, type=`int`, default=`Field(30, ge=0, le=600)` (line 411)
    - name=`absence_slack`, type=`int`, default=`Field(20, ge=0, le=600)` (line 412)
    - name=`late_tick_penalty`, type=`float`, default=`Field(0.005, ge=0.0, le=1.0)` (line 413)
    - name=`absence_penalty`, type=`float`, default=`Field(0.2, ge=0.0, le=5.0)` (line 414)
    - name=`max_absent_shifts`, type=`int`, default=`Field(3, ge=0, le=20)` (line 415)
    - name=`attendance_window`, type=`int`, default=`Field(3, ge=1, le=14)` (line 416)
    - name=`daily_exit_cap`, type=`int`, default=`Field(2, ge=0, le=50)` (line 417)
    - name=`exit_queue_limit`, type=`int`, default=`Field(8, ge=0, le=100)` (line 418)
    - name=`exit_review_window`, type=`int`, default=`Field(1440, ge=1, le=100000)` (line 419)
    - name=`enforce_job_loop`, type=`bool`, default=`False` (line 420)
- `BehaviorConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 423)
  - Attributes:
    - name=`hunger_threshold`, type=`float`, default=`Field(0.4, ge=0.0, le=1.0)` (line 424)
    - name=`hygiene_threshold`, type=`float`, default=`Field(0.4, ge=0.0, le=1.0)` (line 425)
    - name=`energy_threshold`, type=`float`, default=`Field(0.4, ge=0.0, le=1.0)` (line 426)
    - name=`job_arrival_buffer`, type=`int`, default=`Field(20, ge=0)` (line 427)
- `SocialRewardScheduleEntry` (bases: BaseModel; decorators: None) — No class docstring provided. (line 430)
  - Attributes:
    - name=`cycle`, type=`int`, default=`Field(0, ge=0)` (line 431)
    - name=`stage`, type=`SocialRewardStage` (line 432)
- `BCTrainingSettings` (bases: BaseModel; decorators: None) — No class docstring provided. (line 435)
  - Attributes:
    - name=`manifest`, type=`Path | None`, default=`None` (line 436)
    - name=`learning_rate`, type=`float`, default=`Field(0.001, gt=0.0)` (line 437)
    - name=`batch_size`, type=`int`, default=`Field(64, ge=1)` (line 438)
    - name=`epochs`, type=`int`, default=`Field(10, ge=1)` (line 439)
    - name=`weight_decay`, type=`float`, default=`Field(0.0, ge=0.0)` (line 440)
    - name=`device`, type=`str`, default=`'cpu'` (line 441)
- `AnnealStage` (bases: BaseModel; decorators: None) — No class docstring provided. (line 444)
  - Attributes:
    - name=`cycle`, type=`int`, default=`Field(0, ge=0)` (line 445)
    - name=`mode`, type=`Literal['bc', 'ppo']`, default=`'ppo'` (line 446)
    - name=`epochs`, type=`int`, default=`Field(1, ge=1)` (line 447)
    - name=`bc_weight`, type=`float`, default=`Field(1.0, ge=0.0, le=1.0)` (line 448)
- `NarrationThrottleConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 451)
  - Attributes:
    - name=`global_cooldown_ticks`, type=`int`, default=`Field(30, ge=0, le=10000)` (line 452)
    - name=`category_cooldown_ticks`, type=`dict[str, int]`, default=`Field(default_factory=dict)` (line 453)
    - name=`dedupe_window_ticks`, type=`int`, default=`Field(20, ge=0, le=10000)` (line 454)
    - name=`global_window_ticks`, type=`int`, default=`Field(600, ge=1, le=10000)` (line 455)
    - name=`global_window_limit`, type=`int`, default=`Field(10, ge=1, le=1000)` (line 456)
    - name=`priority_categories`, type=`list[str]`, default=`Field(default_factory=list)` (line 457)
  - Methods:
    - `get_category_cooldown(self, category: str) -> int` — No docstring. (line 459)
- `TelemetryRetryPolicy` (bases: BaseModel; decorators: None) — No class docstring provided. (line 463)
  - Attributes:
    - name=`max_attempts`, type=`int`, default=`Field(default=3, ge=0, le=10)` (line 464)
    - name=`backoff_seconds`, type=`float`, default=`Field(default=0.5, ge=0.0, le=30.0)` (line 465)
- `TelemetryBufferConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 468)
  - Attributes:
    - name=`max_batch_size`, type=`int`, default=`Field(default=32, ge=1, le=500)` (line 469)
    - name=`max_buffer_bytes`, type=`int`, default=`Field(default=256000, ge=1024, le=16777216)` (line 470)
    - name=`flush_interval_ticks`, type=`int`, default=`Field(default=1, ge=1, le=10000)` (line 471)
- `TelemetryTransportConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 474)
  - Attributes:
    - name=`type`, type=`TelemetryTransportType`, default=`'stdout'` (line 475)
    - name=`endpoint`, type=`str | None`, default=`None` (line 476)
    - name=`file_path`, type=`Path | None`, default=`None` (line 477)
    - name=`connect_timeout_seconds`, type=`float`, default=`Field(default=5.0, ge=0.0, le=60.0)` (line 478)
    - name=`send_timeout_seconds`, type=`float`, default=`Field(default=1.0, ge=0.0, le=60.0)` (line 479)
    - name=`retry`, type=`TelemetryRetryPolicy`, default=`TelemetryRetryPolicy()` (line 480)
    - name=`buffer`, type=`TelemetryBufferConfig`, default=`TelemetryBufferConfig()` (line 481)
    - name=`worker_poll_seconds`, type=`float`, default=`Field(default=0.5, ge=0.01, le=10.0)` (line 482)
  - Methods:
    - `_validate_transport(self) -> 'TelemetryTransportConfig'` — No docstring. (line 485)
- `TelemetryConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 513)
  - Attributes:
    - name=`narration`, type=`NarrationThrottleConfig`, default=`NarrationThrottleConfig()` (line 514)
    - name=`transport`, type=`TelemetryTransportConfig`, default=`TelemetryTransportConfig()` (line 515)
- `SnapshotStorageConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 518)
  - Attributes:
    - name=`root`, type=`Path`, default=`Field(default=Path('snapshots'))` (line 519)
  - Methods:
    - `_validate_root(self) -> 'SnapshotStorageConfig'` — No docstring. (line 522)
- `SnapshotAutosaveConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 528)
  - Attributes:
    - name=`cadence_ticks`, type=`int | None`, default=`Field(default=None, ge=1)` (line 529)
    - name=`retain`, type=`int`, default=`Field(default=3, ge=1, le=1000)` (line 530)
  - Methods:
    - `_validate_cadence(self) -> 'SnapshotAutosaveConfig'` — No docstring. (line 533)
- `SnapshotIdentityConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 541)
  - Attributes:
    - name=`policy_hash`, type=`str | None`, default=`None` (line 542)
    - name=`policy_artifact`, type=`Path | None`, default=`None` (line 543)
    - name=`observation_variant`, type=`ObservationVariant | Literal['infer']`, default=`'infer'` (line 544)
    - name=`anneal_ratio`, type=`float | None`, default=`Field(default=None, ge=0.0, le=1.0)` (line 545)
    - name=`_HEX40`, default=`re.compile('^[0-9a-fA-F]{40}$')` (line 547)
    - name=`_HEX64`, default=`re.compile('^[0-9a-fA-F]{64}$')` (line 548)
    - name=`_BASE64`, default=`re.compile('^[A-Za-z0-9+/=]{32,88}$')` (line 549)
  - Methods:
    - `_validate_policy_hash(self) -> 'SnapshotIdentityConfig'` — No docstring. (line 552)
    - `_validate_variant(self) -> 'SnapshotIdentityConfig'` — No docstring. (line 570)
- `SnapshotMigrationsConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 582)
  - Attributes:
    - name=`handlers`, type=`dict[str, str]`, default=`Field(default_factory=dict)` (line 583)
    - name=`auto_apply`, type=`bool`, default=`False` (line 584)
    - name=`allow_minor`, type=`bool`, default=`False` (line 585)
  - Methods:
    - `_validate_handlers(self) -> 'SnapshotMigrationsConfig'` — No docstring. (line 588)
- `SnapshotGuardrailsConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 597)
  - Attributes:
    - name=`require_exact_config`, type=`bool`, default=`True` (line 598)
    - name=`allow_downgrade`, type=`bool`, default=`False` (line 599)
    - name=`allowed_paths`, type=`list[Path]`, default=`Field(default_factory=list)` (line 600)
- `SnapshotConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 603)
  - Attributes:
    - name=`storage`, type=`SnapshotStorageConfig`, default=`SnapshotStorageConfig()` (line 604)
    - name=`autosave`, type=`SnapshotAutosaveConfig`, default=`SnapshotAutosaveConfig()` (line 605)
    - name=`identity`, type=`SnapshotIdentityConfig`, default=`SnapshotIdentityConfig()` (line 606)
    - name=`migrations`, type=`SnapshotMigrationsConfig`, default=`SnapshotMigrationsConfig()` (line 607)
    - name=`guardrails`, type=`SnapshotGuardrailsConfig`, default=`SnapshotGuardrailsConfig()` (line 608)
  - Methods:
    - `_validate_observation_override(self) -> 'SnapshotConfig'` — No docstring. (line 611)
- `TrainingConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 623)
  - Attributes:
    - name=`source`, type=`TrainingSource`, default=`'replay'` (line 624)
    - name=`rollout_ticks`, type=`int`, default=`Field(100, ge=0)` (line 625)
    - name=`rollout_auto_seed_agents`, type=`bool`, default=`False` (line 626)
    - name=`replay_manifest`, type=`Path | None`, default=`None` (line 627)
    - name=`social_reward_stage_override`, type=`SocialRewardStage | None`, default=`None` (line 628)
    - name=`social_reward_schedule`, type=`list['SocialRewardScheduleEntry']`, default=`Field(default_factory=list)` (line 629)
    - name=`bc`, type=`BCTrainingSettings`, default=`BCTrainingSettings()` (line 630)
    - name=`anneal_schedule`, type=`list[AnnealStage]`, default=`Field(default_factory=list)` (line 631)
    - name=`anneal_accuracy_threshold`, type=`float`, default=`Field(0.9, ge=0.0, le=1.0)` (line 632)
    - name=`anneal_enable_policy_blend`, type=`bool`, default=`False` (line 633)
- `JobSpec` (bases: BaseModel; decorators: None) — No class docstring provided. (line 636)
  - Attributes:
    - name=`start_tick`, type=`int`, default=`0` (line 637)
    - name=`end_tick`, type=`int`, default=`0` (line 638)
    - name=`wage_rate`, type=`float`, default=`0.0` (line 639)
    - name=`lateness_penalty`, type=`float`, default=`0.0` (line 640)
    - name=`location`, type=`tuple[int, int] | None`, default=`None` (line 641)
- `SimulationConfig` (bases: BaseModel; decorators: None) — No class docstring provided. (line 644)
  - Attributes:
    - name=`config_id`, type=`str` (line 645)
    - name=`features`, type=`FeatureFlags` (line 646)
    - name=`rewards`, type=`RewardsConfig` (line 647)
    - name=`economy`, type=`dict[str, float]`, default=`Field(default_factory=lambda: {'meal_cost': 0.4, 'cook_energy_cost': 0.05, 'cook_hygiene_cost': 0.02, 'wage_income': 0.02, 'ingredients_cost': 0.15, 'stove_stock_replenish': 2})` (line 648)
    - name=`jobs`, type=`dict[str, JobSpec]`, default=`Field(default_factory=lambda: {'grocer': JobSpec(start_tick=180, end_tick=360, wage_rate=0.02, lateness_penalty=0.1, location=(0, 0)), 'barista': JobSpec(start_tick=400, end_tick=560, wage_rate=0.025, lateness_penalty=0.12, location=(1, 0))})` (line 658)
    - name=`shaping`, type=`ShapingConfig | None`, default=`None` (line 676)
    - name=`curiosity`, type=`CuriosityConfig | None`, default=`None` (line 677)
    - name=`queue_fairness`, type=`QueueFairnessConfig`, default=`QueueFairnessConfig()` (line 678)
    - name=`conflict`, type=`ConflictConfig`, default=`ConflictConfig()` (line 679)
    - name=`ppo`, type=`PPOConfig | None`, default=`None` (line 680)
    - name=`training`, type=`TrainingConfig`, default=`TrainingConfig()` (line 681)
    - name=`embedding_allocator`, type=`EmbeddingAllocatorConfig`, default=`EmbeddingAllocatorConfig()` (line 682)
    - name=`observations_config`, type=`ObservationsConfig`, default=`ObservationsConfig()` (line 683)
    - name=`affordances`, type=`AffordanceConfig`, default=`AffordanceConfig()` (line 684)
    - name=`stability`, type=`StabilityConfig`, default=`StabilityConfig()` (line 685)
    - name=`behavior`, type=`BehaviorConfig`, default=`BehaviorConfig()` (line 686)
    - name=`policy_runtime`, type=`PolicyRuntimeConfig`, default=`PolicyRuntimeConfig()` (line 687)
    - name=`employment`, type=`EmploymentConfig`, default=`EmploymentConfig()` (line 688)
    - name=`telemetry`, type=`TelemetryConfig`, default=`TelemetryConfig()` (line 689)
    - name=`snapshot`, type=`SnapshotConfig`, default=`SnapshotConfig()` (line 690)
    - name=`perturbations`, type=`PerturbationSchedulerConfig`, default=`PerturbationSchedulerConfig()` (line 691)
    - name=`lifecycle`, type=`LifecycleConfig`, default=`LifecycleConfig()` (line 692)
    - name=`model_config`, default=`ConfigDict(extra='allow')` (line 694)
  - Methods:
    - `_validate_observation_variant(self) -> 'SimulationConfig'` — No docstring. (line 697)
    - `observation_variant(self) -> ObservationVariant` — No docstring. (line 708)
    - `require_observation_variant(self, expected: ObservationVariant) -> None` — No docstring. (line 711)
    - `snapshot_root(self) -> Path` — No docstring. (line 721)
    - `snapshot_allowed_roots(self) -> tuple[Path, ...]` — No docstring. (line 725)
    - `build_snapshot_identity(self, *, policy_hash: str | None, runtime_observation_variant: ObservationVariant | None, runtime_anneal_ratio: float | None) -> dict[str, object]` — No docstring. (line 737)
    - `register_snapshot_migrations(self) -> None` — No docstring. (line 770)

### Functions
- `load_config(path: Path) -> SimulationConfig` — Load and validate a Townlet YAML configuration file. (line 797)

### Constants and Configuration
- `PRICE_SPIKE` = 'price_spike' (line 333)
- `BLACKOUT` = 'blackout' (line 334)
- `OUTAGE` = 'outage' (line 335)
- `ARRANGED_MEET` = 'arranged_meet' (line 336)
- `_HEX40` = re.compile('^[0-9a-fA-F]{40}$') (line 547)
- `_HEX64` = re.compile('^[0-9a-fA-F]{64}$') (line 548)
- `_BASE64` = re.compile('^[A-Za-z0-9+/=]{32,88}$') (line 549)

### Data Flow
- Primary inputs: category, expected, path, policy_hash, runtime_anneal_ratio, runtime_observation_variant, value, values
- Return payloads: 'FloatRange', 'HybridObservationConfig', 'IntRange', 'PromotionGateConfig', 'RewardsConfig', 'RivalryConfig', 'SimulationConfig', 'SnapshotAutosaveConfig', 'SnapshotConfig', 'SnapshotIdentityConfig', 'SnapshotMigrationsConfig', 'SnapshotStorageConfig'
- Builds derived structures or observations via SimulationConfig.build_snapshot_identity
- Loads configuration or datasets from disk via load_config
- Persists state or reports to disk via SnapshotAutosaveConfig._validate_cadence
- Registers handlers or callbacks via SimulationConfig.register_snapshot_migrations
- Validates inputs or configuration via FloatRange._validate_bounds, HybridObservationConfig._validate_window, IntRange._validate_bounds, RivalryConfig._validate_ranges, SimulationConfig._validate_observation_variant, SnapshotAutosaveConfig._validate_cadence, SnapshotConfig._validate_observation_override, SnapshotIdentityConfig._validate_policy_hash, SnapshotIdentityConfig._validate_variant, SnapshotMigrationsConfig._validate_handlers, SnapshotStorageConfig._validate_root, SocialSnippetConfig._validate_totals, TelemetryTransportConfig._validate_transport

### Integration Points
- External: pydantic.BaseModel, pydantic.ConfigDict, pydantic.Field, pydantic.ValidationError, pydantic.model_validator, yaml
- Internal: townlet.snapshots.register_migration

### Code Quality Notes
- Missing docstrings: BasePerturbationEventConfig._normalise_duration, FloatRange._coerce, FloatRange._validate_bounds, HybridObservationConfig._validate_window, IntRange._coerce, IntRange._validate_bounds, NarrationThrottleConfig.get_category_cooldown, PerturbationSchedulerConfig.event_list, PriceSpikeEventConfig._normalise_magnitude, PromotionGateConfig._coerce_allowed, PromotionGateConfig._normalise, RewardsConfig._sanity_check_punctuality, RivalryConfig._validate_ranges, SimulationConfig._validate_observation_variant, SimulationConfig.build_snapshot_identity, SimulationConfig.observation_variant, SimulationConfig.register_snapshot_migrations, SimulationConfig.require_observation_variant, SimulationConfig.snapshot_allowed_roots, SimulationConfig.snapshot_root
- ... 9 additional methods without docstrings
- Module exceeds 800 lines; consider refactoring into smaller components.

## `src/townlet/console/__init__.py`

**Purpose**: Console command handling exports.
**Lines of code**: 15
**Dependencies**: stdlib=__future__.annotations, importlib.import_module, typing.Any; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `__getattr__(name: str) -> Any` — No docstring. (line 11)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: name
- Return payloads: Any
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: __getattr__

## `src/townlet/console/command.py`

**Purpose**: Console command envelope and result helpers.
**Lines of code**: 201
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass, dataclasses.field, typing.Any, typing.Callable, typing.Mapping; external=None; internal=None
**Related modules**: None

### Classes
- `ConsoleCommandError` (bases: RuntimeError; decorators: None) — Raised by handlers when a command should return an error response. (line 10)
  - Methods:
    - `__init__(self, code: str, message: str, *, details: Mapping[str, Any] | None = None) -> None` — No docstring. (line 13)
- `ConsoleCommandEnvelope` (bases: object; decorators: dataclass(frozen=True)) — Normalised representation of an incoming console command payload. (line 21)
  - Attributes:
    - name=`name`, type=`str` (line 24)
    - name=`args`, type=`list[Any]`, default=`field(default_factory=list)` (line 25)
    - name=`kwargs`, type=`dict[str, Any]`, default=`field(default_factory=dict)` (line 26)
    - name=`cmd_id`, type=`str | None`, default=`None` (line 27)
    - name=`issuer`, type=`str | None`, default=`None` (line 28)
    - name=`mode`, type=`str`, default=`'viewer'` (line 29)
    - name=`timestamp_ms`, type=`int | None`, default=`None` (line 30)
    - name=`metadata`, type=`dict[str, Any]`, default=`field(default_factory=dict)` (line 31)
    - name=`raw`, type=`Mapping[str, Any] | None`, default=`None` (line 32)
  - Methods:
    - `from_payload(cls, payload: object) -> 'ConsoleCommandEnvelope'` — Parse a payload emitted by the console transport. (line 35)
- `ConsoleCommandResult` (bases: object; decorators: dataclass) — Standard response emitted after processing a console command. (line 117)
  - Attributes:
    - name=`name`, type=`str` (line 120)
    - name=`status`, type=`str` (line 121)
    - name=`result`, type=`dict[str, Any] | None`, default=`None` (line 122)
    - name=`error`, type=`dict[str, Any] | None`, default=`None` (line 123)
    - name=`cmd_id`, type=`str | None`, default=`None` (line 124)
    - name=`issuer`, type=`str | None`, default=`None` (line 125)
    - name=`tick`, type=`int | None`, default=`None` (line 126)
    - name=`latency_ms`, type=`int | None`, default=`None` (line 127)
  - Methods:
    - `ok(cls, envelope: ConsoleCommandEnvelope, payload: Mapping[str, Any] | None = None, *, tick: int | None = None, latency_ms: int | None = None) -> 'ConsoleCommandResult'` — No docstring. (line 130)
    - `from_error(cls, envelope: ConsoleCommandEnvelope, code: str, message: str, *, details: Mapping[str, Any] | None = None, tick: int | None = None, latency_ms: int | None = None) -> 'ConsoleCommandResult'` — No docstring. (line 150)
    - `clone(self) -> 'ConsoleCommandResult'` — No docstring. (line 173)
    - `to_dict(self) -> dict[str, Any]` — No docstring. (line 185)

### Functions
- None

### Constants and Configuration
- `_VALID_MODES` = {'viewer', 'admin'} (line 7)

### Data Flow
- Primary inputs: code, details, envelope, latency_ms, message, payload, tick
- Return payloads: 'ConsoleCommandEnvelope', 'ConsoleCommandResult', None, dict[str, Any]
- Loads configuration or datasets from disk via ConsoleCommandEnvelope.from_payload

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: ConsoleCommandError.__init__, ConsoleCommandResult.clone, ConsoleCommandResult.from_error, ConsoleCommandResult.ok, ConsoleCommandResult.to_dict

## `src/townlet/console/handlers.py`

**Purpose**: Console validation scaffolding.
**Lines of code**: 924
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass, json, pathlib.Path, typing.Mapping, typing.Protocol, typing.TYPE_CHECKING; external=None; internal=townlet.config.SimulationConfig, townlet.lifecycle.manager.LifecycleManager, townlet.policy.runner.PolicyRuntime, townlet.scheduler.perturbations.PerturbationScheduler, townlet.snapshots.SnapshotManager, townlet.stability.promotion.PromotionManager, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState
**Related modules**: townlet.config.SimulationConfig, townlet.lifecycle.manager.LifecycleManager, townlet.policy.runner.PolicyRuntime, townlet.scheduler.perturbations.PerturbationScheduler, townlet.snapshots.SnapshotManager, townlet.stability.promotion.PromotionManager, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState

### Classes
- `ConsoleCommand` (bases: object; decorators: dataclass) — Represents a parsed console command ready for execution. (line 26)
  - Attributes:
    - name=`name`, type=`str` (line 29)
    - name=`args`, type=`tuple[object, ...]` (line 30)
    - name=`kwargs`, type=`dict[str, object]` (line 31)
- `ConsoleHandler` (bases: Protocol; decorators: None) — No class docstring provided. (line 34)
  - Methods:
    - `__call__(self, command: ConsoleCommand) -> object` — No docstring. (line 35)
- `ConsoleRouter` (bases: object; decorators: None) — Routes validated commands to subsystem handlers. (line 38)
  - Methods:
    - `__init__(self) -> None` — No docstring. (line 41)
    - `register(self, name: str, handler: ConsoleHandler) -> None` — No docstring. (line 44)
    - `dispatch(self, command: ConsoleCommand) -> object` — No docstring. (line 47)
- `EventStream` (bases: object; decorators: None) — Simple subscriber that records the latest simulation events. (line 54)
  - Methods:
    - `__init__(self) -> None` — No docstring. (line 57)
    - `connect(self, publisher: TelemetryPublisher) -> None` — No docstring. (line 60)
    - `_record(self, events: list[dict[str, object]]) -> None` — No docstring. (line 63)
    - `latest(self) -> list[dict[str, object]]` — No docstring. (line 66)
- `TelemetryBridge` (bases: object; decorators: None) — Provides access to the latest telemetry snapshots for console consumers. (line 70)
  - Methods:
    - `__init__(self, publisher: TelemetryPublisher) -> None` — No docstring. (line 73)
    - `snapshot(self) -> dict[str, dict[str, object]]` — No docstring. (line 76)

### Functions
- `create_console_router(publisher: TelemetryPublisher, world: WorldState | None = None, scheduler: PerturbationScheduler | None = None, promotion: PromotionManager | None = None, *, policy: PolicyRuntime | None = None, mode: str = 'viewer', config: SimulationConfig | None = None, lifecycle: 'LifecycleManager' | None = None) -> ConsoleRouter` — No docstring. (line 113)
- `_schema_metadata(publisher: TelemetryPublisher) -> tuple[str, str | None]` — No docstring. (line 916)

### Constants and Configuration
- `SUPPORTED_SCHEMA_PREFIX` = '0.9' (line 21)
- `SUPPORTED_SCHEMA_LABEL` = f'{SUPPORTED_SCHEMA_PREFIX}.x' (line 22)

### Data Flow
- Primary inputs: command, config, events, handler, lifecycle, mode, name, policy, promotion, publisher, scheduler, world
- Return payloads: ConsoleRouter, None, dict[str, dict[str, object]], list[dict[str, object]], object, tuple[str, str | None]
- Establishes IO connections or sockets via EventStream.connect
- Records metrics or histories via EventStream._record
- Registers handlers or callbacks via ConsoleRouter.register

### Integration Points
- External: None
- Internal: townlet.config.SimulationConfig, townlet.lifecycle.manager.LifecycleManager, townlet.policy.runner.PolicyRuntime, townlet.scheduler.perturbations.PerturbationScheduler, townlet.snapshots.SnapshotManager, townlet.stability.promotion.PromotionManager, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: ConsoleHandler.__call__, ConsoleRouter.__init__, ConsoleRouter.dispatch, ConsoleRouter.register, EventStream.__init__, EventStream._record, EventStream.connect, EventStream.latest, TelemetryBridge.__init__, TelemetryBridge.snapshot, _schema_metadata, create_console_router
- Module exceeds 800 lines; consider refactoring into smaller components.

## `src/townlet/core/__init__.py`

**Purpose**: Core orchestration utilities.
**Lines of code**: 7
**Dependencies**: stdlib=__future__.annotations; external=sim_loop.SimulationLoop; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: sim_loop.SimulationLoop
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/core/sim_loop.py`

**Purpose**: Top-level simulation loop wiring.
**Lines of code**: 270
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterable, dataclasses.dataclass, hashlib, logging, pathlib.Path, random, time; external=None; internal=townlet.config.SimulationConfig, townlet.lifecycle.manager.LifecycleManager, townlet.observations.builder.ObservationBuilder, townlet.policy.runner.PolicyRuntime, townlet.rewards.engine.RewardEngine, townlet.scheduler.perturbations.PerturbationScheduler, townlet.snapshots.SnapshotManager, townlet.snapshots.apply_snapshot_to_telemetry, townlet.snapshots.apply_snapshot_to_world, townlet.snapshots.snapshot_from_world, townlet.stability.monitor.StabilityMonitor, townlet.stability.promotion.PromotionManager, townlet.telemetry.publisher.TelemetryPublisher, townlet.utils.decode_rng_state, townlet.world.grid.WorldState
**Related modules**: townlet.config.SimulationConfig, townlet.lifecycle.manager.LifecycleManager, townlet.observations.builder.ObservationBuilder, townlet.policy.runner.PolicyRuntime, townlet.rewards.engine.RewardEngine, townlet.scheduler.perturbations.PerturbationScheduler, townlet.snapshots.SnapshotManager, townlet.snapshots.apply_snapshot_to_telemetry, townlet.snapshots.apply_snapshot_to_world, townlet.snapshots.snapshot_from_world, townlet.stability.monitor.StabilityMonitor, townlet.stability.promotion.PromotionManager, townlet.telemetry.publisher.TelemetryPublisher, townlet.utils.decode_rng_state, townlet.world.grid.WorldState

### Classes
- `TickArtifacts` (bases: object; decorators: dataclass) — Collects per-tick data for logging and testing. (line 40)
  - Attributes:
    - name=`observations`, type=`dict[str, object]` (line 43)
    - name=`rewards`, type=`dict[str, float]` (line 44)
- `SimulationLoop` (bases: object; decorators: None) — Orchestrates the Townlet simulation tick-by-tick. (line 47)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 50)
    - `_build_components(self) -> None` — No docstring. (line 55)
    - `reset(self) -> None` — Reset the simulation loop to its initial state. (line 78)
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring. (line 82)
    - `save_snapshot(self, root: Path | None = None) -> Path` — Persist the current world relationships and tick to ``root``. (line 88)
    - `load_snapshot(self, path: Path) -> None` — Restore world relationships and tick from the snapshot at ``path``. (line 116)
    - `run(self, max_ticks: int | None = None) -> Iterable[TickArtifacts]` — Run the loop until `max_ticks` or indefinitely. (line 161)
    - `step(self) -> TickArtifacts` — No docstring. (line 167)
    - `_derive_seed(self, stream: str) -> int` — No docstring. (line 268)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config, max_ticks, path, ratio, root, stream
- Return payloads: Iterable[TickArtifacts], None, Path, TickArtifacts, int
- Builds derived structures or observations via SimulationLoop._build_components
- Loads configuration or datasets from disk via SimulationLoop.load_snapshot
- Persists state or reports to disk via SimulationLoop.save_snapshot
- Resets runtime state via SimulationLoop.reset

### Integration Points
- External: None
- Internal: townlet.config.SimulationConfig, townlet.lifecycle.manager.LifecycleManager, townlet.observations.builder.ObservationBuilder, townlet.policy.runner.PolicyRuntime, townlet.rewards.engine.RewardEngine, townlet.scheduler.perturbations.PerturbationScheduler, townlet.snapshots.SnapshotManager, townlet.snapshots.apply_snapshot_to_telemetry, townlet.snapshots.apply_snapshot_to_world, townlet.snapshots.snapshot_from_world, townlet.stability.monitor.StabilityMonitor, townlet.stability.promotion.PromotionManager, townlet.telemetry.publisher.TelemetryPublisher, townlet.utils.decode_rng_state, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: SimulationLoop.__init__, SimulationLoop._build_components, SimulationLoop._derive_seed, SimulationLoop.set_anneal_ratio, SimulationLoop.step

## `src/townlet/lifecycle/__init__.py`

**Purpose**: Lifecycle management utilities.
**Lines of code**: 7
**Dependencies**: stdlib=__future__.annotations; external=manager.LifecycleManager; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: manager.LifecycleManager
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/lifecycle/manager.py`

**Purpose**: Agent lifecycle enforcement (exits, spawns, cooldowns).
**Lines of code**: 167
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass, typing.Any, typing.List; external=None; internal=townlet.config.SimulationConfig, townlet.world.grid.WorldState
**Related modules**: townlet.config.SimulationConfig, townlet.world.grid.WorldState

### Classes
- `_RespawnTicket` (bases: object; decorators: dataclass) — No class docstring provided. (line 13)
  - Attributes:
    - name=`agent_id`, type=`str` (line 14)
    - name=`scheduled_tick`, type=`int` (line 15)
    - name=`blueprint`, type=`dict[str, Any]` (line 16)
- `LifecycleManager` (bases: object; decorators: None) — Centralises lifecycle checks as outlined in the conceptual design snapshot. (line 19)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 22)
    - `evaluate(self, world: WorldState, tick: int) -> dict[str, bool]` — Return a map of agent_id -> terminated flag. (line 31)
    - `finalize(self, world: WorldState, tick: int, terminated: dict[str, bool]) -> None` — No docstring. (line 47)
    - `process_respawns(self, world: WorldState, tick: int) -> None` — No docstring. (line 68)
    - `set_respawn_delay(self, ticks: int) -> None` — No docstring. (line 79)
    - `set_mortality_enabled(self, enabled: bool) -> None` — No docstring. (line 83)
    - `export_state(self) -> dict[str, int]` — No docstring. (line 86)
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring. (line 92)
    - `reset_state(self) -> None` — No docstring. (line 96)
    - `termination_reasons(self) -> dict[str, str]` — Return termination reasons captured during the last evaluation. (line 101)
    - `_evaluate_employment(self, world: WorldState, tick: int) -> dict[str, bool]` — No docstring. (line 105)
    - `_employment_execute_exit(self, world: WorldState, agent_id: str, tick: int, *, reason: str) -> bool` — No docstring. (line 141)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, config, enabled, payload, reason, terminated, tick, ticks, world
- Return payloads: None, bool, dict[str, bool], dict[str, int], dict[str, str]
- Evaluates conditions or invariants via LifecycleManager._evaluate_employment, LifecycleManager.evaluate
- Exports payloads for downstream consumers via LifecycleManager.export_state
- Resets runtime state via LifecycleManager.reset_state

### Integration Points
- External: None
- Internal: townlet.config.SimulationConfig, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: LifecycleManager.__init__, LifecycleManager._employment_execute_exit, LifecycleManager._evaluate_employment, LifecycleManager.export_state, LifecycleManager.finalize, LifecycleManager.import_state, LifecycleManager.process_respawns, LifecycleManager.reset_state, LifecycleManager.set_mortality_enabled, LifecycleManager.set_respawn_delay

## `src/townlet/observations/__init__.py`

**Purpose**: Observation builders and utilities.
**Lines of code**: 7
**Dependencies**: stdlib=__future__.annotations; external=builder.ObservationBuilder; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: builder.ObservationBuilder
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/observations/builder.py`

**Purpose**: Observation encoding across variants.
**Lines of code**: 669
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterable, hashlib, math.cos, math.sin, math.tau, typing.TYPE_CHECKING; external=numpy; internal=townlet.config.ObservationVariant, townlet.config.SimulationConfig, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.ObservationVariant, townlet.config.SimulationConfig, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- `ObservationBuilder` (bases: object; decorators: None) — Constructs per-agent observation payloads. (line 18)
  - Attributes:
    - name=`MAP_CHANNELS`, default=`('self', 'agents', 'objects', 'reservations')` (line 21)
    - name=`SHIFT_STATES`, default=`('pre_shift', 'on_time', 'late', 'absent', 'post_shift')` (line 22)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 24)
    - `build_batch(self, world: 'WorldState', terminated: dict[str, bool]) -> dict[str, dict[str, np.ndarray]]` — Return a mapping from agent_id to observation payloads. (line 133)
    - `_encode_common_features(self, features: np.ndarray, *, context: dict[str, object], slot: int, snapshot: 'AgentSnapshot', world_tick: int) -> None` — No docstring. (line 152)
    - `_encode_rivalry(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring. (line 217)
    - `_encode_environmental_flags(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring. (line 232)
    - `_encode_path_hint(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring. (line 254)
    - `_build_single(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring. (line 281)
    - `_map_from_view(self, channels: tuple[str, ...], local_view: dict[str, object], window: int, center: int, snapshot: 'AgentSnapshot') -> np.ndarray` — No docstring. (line 300)
    - `_build_hybrid(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring. (line 338)
    - `_build_full(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring. (line 391)
    - `_build_compact(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring. (line 444)
    - `_build_social_vector(self, world: 'WorldState', snapshot: 'AgentSnapshot') -> np.ndarray` — No docstring. (line 493)
    - `_collect_social_slots(self, world: 'WorldState', snapshot: 'AgentSnapshot') -> list[dict[str, float]]` — No docstring. (line 525)
    - `_resolve_relationships(self, world: 'WorldState', agent_id: str) -> list[dict[str, float]]` — No docstring. (line 564)
    - `_encode_landmarks(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring. (line 606)
    - `_encode_relationship(self, entry: dict[str, float]) -> dict[str, float]` — No docstring. (line 630)
    - `_empty_relationship_entry(self) -> dict[str, float]` — No docstring. (line 641)
    - `_embed_agent_id(self, other_id: str) -> np.ndarray` — No docstring. (line 650)
    - `_compute_aggregates(self, trust_values: Iterable[float], rivalry_values: Iterable[float]) -> tuple[float, float, float, float]` — No docstring. (line 658)

### Functions
- None

### Constants and Configuration
- `MAP_CHANNELS` = ('self', 'agents', 'objects', 'reservations') (line 21)
- `SHIFT_STATES` = ('pre_shift', 'on_time', 'late', 'absent', 'post_shift') (line 22)

### Data Flow
- Primary inputs: agent_id, center, channels, config, context, entry, features, local_view, other_id, rivalry_values, slot, snapshot
- Return payloads: None, dict[str, dict[str, np.ndarray]], dict[str, float], dict[str, np.ndarray | dict[str, object]], list[dict[str, float]], np.ndarray, tuple[float, float, float, float]
- Builds derived structures or observations via ObservationBuilder.__init__, ObservationBuilder._build_compact, ObservationBuilder._build_full, ObservationBuilder._build_hybrid, ObservationBuilder._build_single, ObservationBuilder._build_social_vector, ObservationBuilder._collect_social_slots, ObservationBuilder._compute_aggregates, ObservationBuilder._embed_agent_id, ObservationBuilder._empty_relationship_entry, ObservationBuilder._encode_common_features, ObservationBuilder._encode_environmental_flags, ObservationBuilder._encode_landmarks, ObservationBuilder._encode_path_hint, ObservationBuilder._encode_relationship, ObservationBuilder._encode_rivalry, ObservationBuilder._map_from_view, ObservationBuilder._resolve_relationships, ObservationBuilder.build_batch
- Computes metrics or rewards via ObservationBuilder._compute_aggregates

### Integration Points
- External: numpy
- Internal: townlet.config.ObservationVariant, townlet.config.SimulationConfig, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: ObservationBuilder.__init__, ObservationBuilder._build_compact, ObservationBuilder._build_full, ObservationBuilder._build_hybrid, ObservationBuilder._build_single, ObservationBuilder._build_social_vector, ObservationBuilder._collect_social_slots, ObservationBuilder._compute_aggregates, ObservationBuilder._embed_agent_id, ObservationBuilder._empty_relationship_entry, ObservationBuilder._encode_common_features, ObservationBuilder._encode_environmental_flags, ObservationBuilder._encode_landmarks, ObservationBuilder._encode_path_hint, ObservationBuilder._encode_relationship, ObservationBuilder._encode_rivalry, ObservationBuilder._map_from_view, ObservationBuilder._resolve_relationships

## `src/townlet/observations/embedding.py`

**Purpose**: Embedding slot allocation with cooldown logging.
**Lines of code**: 160
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass; external=None; internal=townlet.config.EmbeddingAllocatorConfig, townlet.config.SimulationConfig
**Related modules**: townlet.config.EmbeddingAllocatorConfig, townlet.config.SimulationConfig

### Classes
- `_SlotState` (bases: object; decorators: dataclass) — Tracks release metadata for a slot. (line 11)
  - Attributes:
    - name=`released_at_tick`, type=`int | None`, default=`None` (line 14)
- `EmbeddingAllocator` (bases: object; decorators: None) — Assigns stable embedding slots to agents with a reuse cooldown. (line 17)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 20)
    - `allocate(self, agent_id: str, tick: int) -> int` — Return the embedding slot for the agent, allocating if necessary. (line 35)
    - `release(self, agent_id: str, tick: int) -> None` — Release the slot held by the agent. (line 49)
    - `has_assignment(self, agent_id: str) -> bool` — Return whether the allocator still tracks the agent. (line 57)
    - `metrics(self) -> dict[str, float]` — Expose allocation metrics for telemetry. (line 61)
    - `export_state(self) -> dict[str, object]` — Serialise allocator bookkeeping for snapshot persistence. (line 74)
    - `import_state(self, payload: dict[str, object]) -> None` — Restore allocator bookkeeping from snapshot data. (line 86)
    - `_select_slot(self, tick: int) -> tuple[int, bool]` — No docstring. (line 130)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, config, payload, tick
- Return payloads: None, bool, dict[str, float], dict[str, object], int, tuple[int, bool]
- Exports payloads for downstream consumers via EmbeddingAllocator.export_state

### Integration Points
- External: None
- Internal: townlet.config.EmbeddingAllocatorConfig, townlet.config.SimulationConfig

### Code Quality Notes
- Missing docstrings: EmbeddingAllocator.__init__, EmbeddingAllocator._select_slot

## `src/townlet/policy/__init__.py`

**Purpose**: Policy integration layer.
**Lines of code**: 22
**Dependencies**: stdlib=__future__.annotations; external=bc.BCTrainer, bc.BCTrainingConfig, bc.BCTrajectoryDataset, bc.evaluate_bc_policy, bc.load_bc_samples, runner.PolicyRuntime, runner.TrainingHarness; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: bc.BCTrainer, bc.BCTrainingConfig, bc.BCTrajectoryDataset, bc.evaluate_bc_policy, bc.load_bc_samples, runner.PolicyRuntime, runner.TrainingHarness
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/policy/bc.py`

**Purpose**: Behaviour cloning utilities.
**Lines of code**: 201
**Dependencies**: stdlib=__future__.annotations, collections.abc.Mapping, collections.abc.Sequence, dataclasses.dataclass, json, pathlib.Path; external=numpy, torch, torch.nn, torch.utils.data.DataLoader, torch.utils.data.Dataset; internal=townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.ConflictAwarePolicyNetwork, townlet.policy.models.TorchNotAvailableError, townlet.policy.models.torch_available, townlet.policy.replay.ReplaySample, townlet.policy.replay.load_replay_sample
**Related modules**: townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.ConflictAwarePolicyNetwork, townlet.policy.models.TorchNotAvailableError, townlet.policy.models.torch_available, townlet.policy.replay.ReplaySample, townlet.policy.replay.load_replay_sample

### Classes
- `BCTrainingConfig` (bases: object; decorators: dataclass) — No class docstring provided. (line 32)
  - Attributes:
    - name=`learning_rate`, type=`float`, default=`0.001` (line 33)
    - name=`batch_size`, type=`int`, default=`64` (line 34)
    - name=`epochs`, type=`int`, default=`5` (line 35)
    - name=`weight_decay`, type=`float`, default=`0.0` (line 36)
    - name=`device`, type=`str`, default=`'cpu'` (line 37)
- `BCDatasetConfig` (bases: object; decorators: dataclass) — No class docstring provided. (line 41)
  - Attributes:
    - name=`manifest`, type=`Path` (line 42)
- `BCTrajectoryDataset` (bases: Dataset; decorators: None) — Torch dataset flattening replay samples for behaviour cloning. (line 45)
  - Methods:
    - `__init__(self, samples: Sequence[ReplaySample]) -> None` — No docstring. (line 48)
    - `__len__(self) -> int` — No docstring. (line 73)
    - `__getitem__(self, index: int)` — No docstring. (line 76)
- `BCTrainer` (bases: object; decorators: None) — Lightweight supervised trainer for behaviour cloning. (line 121)
  - Methods:
    - `__init__(self, config: BCTrainingConfig, policy_config: ConflictAwarePolicyConfig) -> None` — No docstring. (line 124)
    - `fit(self, dataset: BCTrajectoryDataset) -> Mapping[str, float]` — No docstring. (line 140)
    - `evaluate(self, dataset: BCTrajectoryDataset) -> Mapping[str, float]` — No docstring. (line 158)

### Functions
- `load_bc_samples(manifest_path: Path) -> list[ReplaySample]` — No docstring. (line 83)
- `evaluate_bc_policy(model: ConflictAwarePolicyNetwork, dataset: BCTrajectoryDataset, device: str = 'cpu') -> Mapping[str, float]` — No docstring. (line 176)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config, dataset, device, index, manifest_path, model, policy_config, samples
- Return payloads: Mapping[str, float], None, int, list[ReplaySample]
- Evaluates conditions or invariants via BCTrainer.evaluate, evaluate_bc_policy
- Loads configuration or datasets from disk via load_bc_samples
- Trains policies or models via BCTrainer.__init__, BCTrainer.evaluate, BCTrainer.fit

### Integration Points
- External: numpy, torch, torch.nn, torch.utils.data.DataLoader, torch.utils.data.Dataset
- Internal: townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.ConflictAwarePolicyNetwork, townlet.policy.models.TorchNotAvailableError, townlet.policy.models.torch_available, townlet.policy.replay.ReplaySample, townlet.policy.replay.load_replay_sample

### Code Quality Notes
- Missing docstrings: BCTrainer.__init__, BCTrainer.evaluate, BCTrainer.fit, BCTrajectoryDataset.__getitem__, BCTrajectoryDataset.__init__, BCTrajectoryDataset.__len__, evaluate_bc_policy, load_bc_samples

## `src/townlet/policy/behavior.py`

**Purpose**: Behavior controller interfaces for scripted decision logic.
**Lines of code**: 196
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass, typing.Optional, typing.Protocol; external=None; internal=townlet.config.SimulationConfig, townlet.world.grid.WorldState
**Related modules**: townlet.config.SimulationConfig, townlet.world.grid.WorldState

### Classes
- `AgentIntent` (bases: object; decorators: dataclass) — Represents the next action an agent wishes to perform. (line 13)
  - Attributes:
    - name=`kind`, type=`str` (line 16)
    - name=`object_id`, type=`Optional[str]`, default=`None` (line 17)
    - name=`affordance_id`, type=`Optional[str]`, default=`None` (line 18)
    - name=`blocked`, type=`bool`, default=`False` (line 19)
    - name=`position`, type=`Optional[tuple[int, int]]`, default=`None` (line 20)
- `BehaviorController` (bases: Protocol; decorators: None) — Defines the interface for agent decision logic. (line 23)
  - Methods:
    - `decide(self, world: WorldState, agent_id: str) -> AgentIntent` — No docstring. (line 26)
- `IdleBehavior` (bases: BehaviorController; decorators: None) — Default no-op behavior that keeps agents idle. (line 29)
  - Methods:
    - `decide(self, world: WorldState, agent_id: str) -> AgentIntent` — No docstring. (line 32)
- `ScriptedBehavior` (bases: BehaviorController; decorators: None) — Simple rule-based controller used before RL policies are available. (line 36)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 39)
    - `decide(self, world: WorldState, agent_id: str) -> AgentIntent` — No docstring. (line 44)
    - `_cleanup_pending(self, world: WorldState, agent_id: str) -> None` — No docstring. (line 78)
    - `_maybe_move_to_job(self, world: WorldState, agent_id: str, snapshot: object) -> Optional[AgentIntent]` — No docstring. (line 91)
    - `_satisfy_needs(self, world: WorldState, agent_id: str, snapshot: object) -> Optional[AgentIntent]` — No docstring. (line 110)
    - `_rivals_in_queue(self, world: WorldState, agent_id: str, object_id: str) -> bool` — No docstring. (line 139)
    - `_plan_meal(self, world: WorldState, agent_id: str) -> Optional[AgentIntent]` — No docstring. (line 157)
    - `_find_object_of_type(self, world: WorldState, object_type: str) -> Optional[str]` — No docstring. (line 186)

### Functions
- `build_behavior(config: SimulationConfig) -> BehaviorController` — No docstring. (line 195)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, config, object_id, object_type, snapshot, world
- Return payloads: AgentIntent, BehaviorController, None, Optional[AgentIntent], Optional[str], bool
- Builds derived structures or observations via build_behavior
- Selects actions or decisions via BehaviorController.decide, IdleBehavior.decide, ScriptedBehavior.decide

### Integration Points
- External: None
- Internal: townlet.config.SimulationConfig, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: BehaviorController.decide, IdleBehavior.decide, ScriptedBehavior.__init__, ScriptedBehavior._cleanup_pending, ScriptedBehavior._find_object_of_type, ScriptedBehavior._maybe_move_to_job, ScriptedBehavior._plan_meal, ScriptedBehavior._rivals_in_queue, ScriptedBehavior._satisfy_needs, ScriptedBehavior.decide, build_behavior

## `src/townlet/policy/metrics.py`

**Purpose**: Utility helpers for replay and rollout metrics.
**Lines of code**: 108
**Dependencies**: stdlib=__future__.annotations, json, typing.Any; external=numpy, replay.ReplaySample; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `compute_sample_metrics(sample: ReplaySample) -> dict[str, float]` — Compute summary metrics for a replay sample. (line 13)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: sample
- Return payloads: dict[str, float]
- Computes metrics or rewards via compute_sample_metrics

### Integration Points
- External: numpy, replay.ReplaySample
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/policy/models.py`

**Purpose**: Torch-based policy/value networks for Townlet PPO.
**Lines of code**: 83
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass; external=torch, torch.nn; internal=None
**Related modules**: None

### Classes
- `TorchNotAvailableError` (bases: RuntimeError; decorators: None) — Raised when a Torch-dependent component is used without PyTorch. (line 20)
- `ConflictAwarePolicyConfig` (bases: object; decorators: dataclass) — No class docstring provided. (line 25)
  - Attributes:
    - name=`feature_dim`, type=`int` (line 26)
    - name=`map_shape`, type=`tuple[int, int, int]` (line 27)
    - name=`action_dim`, type=`int` (line 28)
    - name=`hidden_dim`, type=`int`, default=`256` (line 29)

### Functions
- `torch_available() -> bool` — Return True if PyTorch is available in the runtime. (line 15)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: bool
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: torch, torch.nn
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/policy/ppo/__init__.py`

**Purpose**: PPO utilities package.
**Lines of code**: 19
**Dependencies**: stdlib=None; external=utils.AdvantageReturns, utils.clipped_value_loss, utils.compute_gae, utils.normalize_advantages, utils.policy_surrogate, utils.value_baseline_from_old_preds; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: utils.AdvantageReturns, utils.clipped_value_loss, utils.compute_gae, utils.normalize_advantages, utils.policy_surrogate, utils.value_baseline_from_old_preds
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/policy/ppo/utils.py`

**Purpose**: Utility functions for PPO advantage and loss computation.
**Lines of code**: 140
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass; external=torch; internal=None
**Related modules**: None

### Classes
- `AdvantageReturns` (bases: object; decorators: dataclass) — Container for PPO advantage and return tensors. (line 11)
  - Attributes:
    - name=`advantages`, type=`torch.Tensor` (line 14)
    - name=`returns`, type=`torch.Tensor` (line 15)

### Functions
- `compute_gae(rewards: torch.Tensor, value_preds: torch.Tensor, dones: torch.Tensor, gamma: float, gae_lambda: float) -> AdvantageReturns` — Compute Generalized Advantage Estimation (GAE). (line 18)
- `normalize_advantages(advantages: torch.Tensor, eps: float = 1e-08) -> torch.Tensor` — Normalize advantage estimates to zero mean/unit variance. (line 72)
- `value_baseline_from_old_preds(value_preds: torch.Tensor, timesteps: int) -> torch.Tensor` — Extract baseline values aligned with each timestep from stored predictions. (line 82)
- `clipped_value_loss(new_values: torch.Tensor, returns: torch.Tensor, old_values: torch.Tensor, value_clip: float) -> torch.Tensor` — Compute the clipped value loss term. (line 98)
- `policy_surrogate(new_log_probs: torch.Tensor, old_log_probs: torch.Tensor, advantages: torch.Tensor, clip_param: float) -> tuple[torch.Tensor, torch.Tensor]` — Compute PPO clipped policy loss and clip fraction. (line 124)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: advantages, clip_param, dones, eps, gae_lambda, gamma, new_log_probs, new_values, old_log_probs, old_values, returns, rewards
- Return payloads: AdvantageReturns, torch.Tensor, tuple[torch.Tensor, torch.Tensor]
- Computes metrics or rewards via compute_gae

### Integration Points
- External: torch
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/policy/replay.py`

**Purpose**: Utilities for replaying observation/telemetry samples.
**Lines of code**: 641
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterator, collections.abc.Sequence, dataclasses.dataclass, json, pathlib.Path, typing.Any, typing.Optional; external=numpy, yaml; internal=None
**Related modules**: None

### Classes
- `ReplaySample` (bases: object; decorators: dataclass) — Container for observation samples used in training replays. (line 20)
  - Attributes:
    - name=`map`, type=`np.ndarray` (line 23)
    - name=`features`, type=`np.ndarray` (line 24)
    - name=`actions`, type=`np.ndarray` (line 25)
    - name=`old_log_probs`, type=`np.ndarray` (line 26)
    - name=`value_preds`, type=`np.ndarray` (line 27)
    - name=`rewards`, type=`np.ndarray` (line 28)
    - name=`dones`, type=`np.ndarray` (line 29)
    - name=`metadata`, type=`dict[str, Any]` (line 30)
  - Methods:
    - `__post_init__(self) -> None` — No docstring. (line 32)
    - `feature_names(self) -> Optional[list[str]]` — No docstring. (line 91)
    - `conflict_stats(self) -> dict[str, float]` — No docstring. (line 97)
- `ReplayBatch` (bases: object; decorators: dataclass) — Mini-batch representation composed from replay samples. (line 161)
  - Attributes:
    - name=`maps`, type=`np.ndarray` (line 164)
    - name=`features`, type=`np.ndarray` (line 165)
    - name=`actions`, type=`np.ndarray` (line 166)
    - name=`old_log_probs`, type=`np.ndarray` (line 167)
    - name=`value_preds`, type=`np.ndarray` (line 168)
    - name=`rewards`, type=`np.ndarray` (line 169)
    - name=`dones`, type=`np.ndarray` (line 170)
    - name=`metadata`, type=`dict[str, Any]` (line 171)
  - Methods:
    - `__post_init__(self) -> None` — No docstring. (line 173)
    - `conflict_stats(self) -> dict[str, float]` — No docstring. (line 230)
- `ReplayDatasetConfig` (bases: object; decorators: dataclass) — Configuration for building replay datasets. (line 279)
  - Attributes:
    - name=`entries`, type=`list[tuple[Path, Optional[Path]]]` (line 282)
    - name=`batch_size`, type=`int`, default=`1` (line 283)
    - name=`shuffle`, type=`bool`, default=`False` (line 284)
    - name=`seed`, type=`Optional[int]`, default=`None` (line 285)
    - name=`drop_last`, type=`bool`, default=`False` (line 286)
    - name=`streaming`, type=`bool`, default=`False` (line 287)
    - name=`metrics_map`, type=`Optional[dict[str, dict[str, float]]]`, default=`None` (line 288)
    - name=`label`, type=`Optional[str]`, default=`None` (line 289)
  - Methods:
    - `from_manifest(cls, manifest_path: Path, batch_size: int = 1, shuffle: bool = False, seed: Optional[int] = None, drop_last: bool = False, streaming: bool = False) -> 'ReplayDatasetConfig'` — No docstring. (line 292)
    - `from_capture_dir(cls, capture_dir: Path, batch_size: int = 1, shuffle: bool = False, seed: Optional[int] = None, drop_last: bool = False, streaming: bool = False) -> 'ReplayDatasetConfig'` — No docstring. (line 313)
- `ReplayDataset` (bases: object; decorators: None) — Iterable dataset producing conflict-aware replay batches. (line 407)
  - Methods:
    - `__init__(self, config: ReplayDatasetConfig) -> None` — No docstring. (line 410)
    - `_ensure_homogeneous(self, samples: Sequence[ReplaySample]) -> None` — No docstring. (line 447)
    - `__len__(self) -> int` — No docstring. (line 462)
    - `__iter__(self) -> Iterator[ReplayBatch]` — No docstring. (line 469)
    - `_fetch_sample(self, index: int) -> ReplaySample` — No docstring. (line 480)
    - `_ensure_sample_metrics(self, sample: ReplaySample, entry: tuple[Path, Optional[Path]]) -> None` — No docstring. (line 512)
    - `_aggregate_metrics(self) -> dict[str, float]` — No docstring. (line 522)

### Functions
- `_ensure_conflict_features(metadata: dict[str, Any]) -> None` — No docstring. (line 110)
- `load_replay_sample(sample_path: Path, meta_path: Optional[Path] = None) -> ReplaySample` — Load observation tensors and metadata for replay-driven training scaffolds. (line 121)
- `build_batch(samples: Sequence[ReplaySample]) -> ReplayBatch` — Stack multiple replay samples into a batch for training consumers. (line 245)
- `_resolve_manifest_path(path_spec: Path, base: Path) -> Path` — Resolve manifest path specs that may be absolute or repo-relative. (line 346)
- `_load_manifest(manifest_path: Path) -> list[tuple[Path, Optional[Path]]]` — No docstring. (line 363)
- `frames_to_replay_sample(frames: Sequence[dict[str, Any]]) -> ReplaySample` — Convert collected trajectory frames into a replay sample. (line 561)

### Constants and Configuration
- `REQUIRED_CONFLICT_FEATURES`: `tuple[str, ...]` = ('rivalry_max', 'rivalry_avoid_count') (line 14)
- `STEP_ARRAY_FIELDS`: `tuple[str, ...]` = ('actions', 'old_log_probs', 'rewards', 'dones') (line 15)
- `TRAINING_ARRAY_FIELDS`: `tuple[str, ...]` = STEP_ARRAY_FIELDS + ('value_preds',) (line 16)

### Data Flow
- Primary inputs: base, batch_size, capture_dir, config, drop_last, entry, frames, index, manifest_path, meta_path, metadata, path_spec
- Return payloads: 'ReplayDatasetConfig', Iterator[ReplayBatch], None, Optional[list[str]], Path, ReplayBatch, ReplaySample, dict[str, float], int, list[tuple[Path, Optional[Path]]]
- Builds derived structures or observations via build_batch
- Captures trajectories or telemetry snapshots via ReplayDatasetConfig.from_capture_dir
- Handles replay buffers or datasets via ReplayBatch.__post_init__, ReplayBatch.conflict_stats, ReplayDataset.__init__, ReplayDataset.__iter__, ReplayDataset.__len__, ReplayDataset._aggregate_metrics, ReplayDataset._ensure_homogeneous, ReplayDataset._ensure_sample_metrics, ReplayDataset._fetch_sample, ReplayDatasetConfig.from_capture_dir, ReplayDatasetConfig.from_manifest, ReplaySample.__post_init__, ReplaySample.conflict_stats, ReplaySample.feature_names, frames_to_replay_sample, load_replay_sample
- Loads configuration or datasets from disk via _load_manifest, load_replay_sample

### Integration Points
- External: numpy, yaml
- Internal: None

### Code Quality Notes
- Missing docstrings: ReplayBatch.__post_init__, ReplayBatch.conflict_stats, ReplayDataset.__init__, ReplayDataset.__iter__, ReplayDataset.__len__, ReplayDataset._aggregate_metrics, ReplayDataset._ensure_homogeneous, ReplayDataset._ensure_sample_metrics, ReplayDataset._fetch_sample, ReplayDatasetConfig.from_capture_dir, ReplayDatasetConfig.from_manifest, ReplaySample.__post_init__, ReplaySample.conflict_stats, ReplaySample.feature_names, _ensure_conflict_features, _load_manifest

## `src/townlet/policy/replay_buffer.py`

**Purpose**: In-memory replay dataset used for rollout captures.
**Lines of code**: 62
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterator, collections.abc.Sequence, dataclasses.dataclass; external=None; internal=townlet.policy.replay.ReplayBatch, townlet.policy.replay.ReplaySample, townlet.policy.replay.build_batch
**Related modules**: townlet.policy.replay.ReplayBatch, townlet.policy.replay.ReplaySample, townlet.policy.replay.build_batch

### Classes
- `InMemoryReplayDatasetConfig` (bases: object; decorators: dataclass) — No class docstring provided. (line 12)
  - Attributes:
    - name=`entries`, type=`Sequence[ReplaySample]` (line 13)
    - name=`batch_size`, type=`int`, default=`1` (line 14)
    - name=`drop_last`, type=`bool`, default=`False` (line 15)
    - name=`rollout_ticks`, type=`int`, default=`0` (line 16)
    - name=`label`, type=`str | None`, default=`None` (line 17)
- `InMemoryReplayDataset` (bases: object; decorators: None) — No class docstring provided. (line 20)
  - Methods:
    - `__init__(self, config: InMemoryReplayDatasetConfig) -> None` — No docstring. (line 21)
    - `_validate_shapes(self) -> None` — No docstring. (line 41)
    - `__iter__(self) -> Iterator[ReplayBatch]` — No docstring. (line 50)
    - `__len__(self) -> int` — No docstring. (line 57)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config
- Return payloads: Iterator[ReplayBatch], None, int
- Handles replay buffers or datasets via InMemoryReplayDataset.__init__, InMemoryReplayDataset.__iter__, InMemoryReplayDataset.__len__, InMemoryReplayDataset._validate_shapes
- Validates inputs or configuration via InMemoryReplayDataset._validate_shapes

### Integration Points
- External: None
- Internal: townlet.policy.replay.ReplayBatch, townlet.policy.replay.ReplaySample, townlet.policy.replay.build_batch

### Code Quality Notes
- Missing docstrings: InMemoryReplayDataset.__init__, InMemoryReplayDataset.__iter__, InMemoryReplayDataset.__len__, InMemoryReplayDataset._validate_shapes

## `src/townlet/policy/rollout.py`

**Purpose**: Rollout buffer scaffolding for future live PPO integration.
**Lines of code**: 206
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterable, dataclasses.dataclass, dataclasses.field, json, pathlib.Path; external=numpy; internal=townlet.policy.metrics.compute_sample_metrics, townlet.policy.replay.ReplaySample, townlet.policy.replay.frames_to_replay_sample, townlet.policy.replay_buffer.InMemoryReplayDataset, townlet.policy.replay_buffer.InMemoryReplayDatasetConfig
**Related modules**: townlet.policy.metrics.compute_sample_metrics, townlet.policy.replay.ReplaySample, townlet.policy.replay.frames_to_replay_sample, townlet.policy.replay_buffer.InMemoryReplayDataset, townlet.policy.replay_buffer.InMemoryReplayDatasetConfig

### Classes
- `AgentRollout` (bases: object; decorators: dataclass) — No class docstring provided. (line 21)
  - Attributes:
    - name=`agent_id`, type=`str` (line 22)
    - name=`frames`, type=`list[dict[str, object]]`, default=`field(default_factory=list)` (line 23)
  - Methods:
    - `append(self, frame: dict[str, object]) -> None` — No docstring. (line 25)
    - `to_replay_sample(self) -> ReplaySample` — No docstring. (line 28)
- `RolloutBuffer` (bases: object; decorators: None) — Collects trajectory frames and exposes helpers to save or replay them. (line 32)
  - Methods:
    - `__init__(self) -> None` — No docstring. (line 35)
    - `record_events(self, events: Iterable[dict[str, object]]) -> None` — No docstring. (line 47)
    - `extend(self, frames: Iterable[dict[str, object]]) -> None` — No docstring. (line 73)
    - `__len__(self) -> int` — No docstring. (line 77)
    - `by_agent(self) -> dict[str, AgentRollout]` — No docstring. (line 80)
    - `to_samples(self) -> dict[str, ReplaySample]` — No docstring. (line 87)
    - `save(self, output_dir: Path, prefix: str = 'rollout_sample', compress: bool = True) -> None` — No docstring. (line 93)
    - `build_dataset(self, batch_size: int = 1, drop_last: bool = False) -> InMemoryReplayDataset` — No docstring. (line 131)
    - `is_empty(self) -> bool` — No docstring. (line 167)
    - `set_tick_count(self, ticks: int) -> None` — No docstring. (line 170)
    - `_aggregate_metrics(self, samples: list[ReplaySample]) -> dict[str, float]` — No docstring. (line 173)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: batch_size, compress, drop_last, events, frame, frames, output_dir, prefix, samples, ticks
- Return payloads: InMemoryReplayDataset, None, ReplaySample, bool, dict[str, AgentRollout], dict[str, ReplaySample], dict[str, float], int
- Advances tick or scheduler timelines via RolloutBuffer.set_tick_count
- Builds derived structures or observations via RolloutBuffer.build_dataset
- Handles replay buffers or datasets via AgentRollout.to_replay_sample
- Persists state or reports to disk via RolloutBuffer.save
- Records metrics or histories via RolloutBuffer.record_events

### Integration Points
- External: numpy
- Internal: townlet.policy.metrics.compute_sample_metrics, townlet.policy.replay.ReplaySample, townlet.policy.replay.frames_to_replay_sample, townlet.policy.replay_buffer.InMemoryReplayDataset, townlet.policy.replay_buffer.InMemoryReplayDatasetConfig

### Code Quality Notes
- Missing docstrings: AgentRollout.append, AgentRollout.to_replay_sample, RolloutBuffer.__init__, RolloutBuffer.__len__, RolloutBuffer._aggregate_metrics, RolloutBuffer.build_dataset, RolloutBuffer.by_agent, RolloutBuffer.extend, RolloutBuffer.is_empty, RolloutBuffer.record_events, RolloutBuffer.save, RolloutBuffer.set_tick_count, RolloutBuffer.to_samples

## `src/townlet/policy/runner.py`

**Purpose**: Policy orchestration scaffolding.
**Lines of code**: 1435
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterable, collections.abc.Mapping, json, math, pathlib.Path, random, statistics, time, typing.Callable; external=numpy, torch, torch.distributions.Categorical, torch.nn.utils.clip_grad_norm_; internal=townlet.config.PPOConfig, townlet.config.SimulationConfig, townlet.core.sim_loop.SimulationLoop, townlet.policy.bc.BCTrainer, townlet.policy.bc.BCTrainingConfig, townlet.policy.bc.BCTrajectoryDataset, townlet.policy.bc.load_bc_samples, townlet.policy.behavior.AgentIntent, townlet.policy.behavior.BehaviorController, townlet.policy.behavior.build_behavior, townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.ConflictAwarePolicyNetwork, townlet.policy.models.TorchNotAvailableError, townlet.policy.models.torch_available, townlet.policy.ppo.utils.AdvantageReturns, townlet.policy.ppo.utils.clipped_value_loss, townlet.policy.ppo.utils.compute_gae, townlet.policy.ppo.utils.normalize_advantages, townlet.policy.ppo.utils.policy_surrogate, townlet.policy.ppo.utils.value_baseline_from_old_preds, townlet.policy.replay.ReplayBatch, townlet.policy.replay.ReplayDataset, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.replay.ReplaySample, townlet.policy.replay.build_batch, townlet.policy.replay.load_replay_sample, townlet.policy.replay_buffer.InMemoryReplayDataset, townlet.policy.rollout.RolloutBuffer, townlet.policy.scenario_utils.apply_scenario, townlet.policy.scenario_utils.has_agents, townlet.policy.scenario_utils.seed_default_agents, townlet.stability.promotion.PromotionManager, townlet.world.grid.WorldState
**Related modules**: townlet.config.PPOConfig, townlet.config.SimulationConfig, townlet.core.sim_loop.SimulationLoop, townlet.policy.bc.BCTrainer, townlet.policy.bc.BCTrainingConfig, townlet.policy.bc.BCTrajectoryDataset, townlet.policy.bc.load_bc_samples, townlet.policy.behavior.AgentIntent, townlet.policy.behavior.BehaviorController, townlet.policy.behavior.build_behavior, townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.ConflictAwarePolicyNetwork, townlet.policy.models.TorchNotAvailableError, townlet.policy.models.torch_available, townlet.policy.ppo.utils.AdvantageReturns, townlet.policy.ppo.utils.clipped_value_loss, townlet.policy.ppo.utils.compute_gae, townlet.policy.ppo.utils.normalize_advantages, townlet.policy.ppo.utils.policy_surrogate, townlet.policy.ppo.utils.value_baseline_from_old_preds, townlet.policy.replay.ReplayBatch, townlet.policy.replay.ReplayDataset, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.replay.ReplaySample, townlet.policy.replay.build_batch, townlet.policy.replay.load_replay_sample, townlet.policy.replay_buffer.InMemoryReplayDataset, townlet.policy.rollout.RolloutBuffer, townlet.policy.scenario_utils.apply_scenario, townlet.policy.scenario_utils.has_agents, townlet.policy.scenario_utils.seed_default_agents, townlet.stability.promotion.PromotionManager, townlet.world.grid.WorldState

### Classes
- `PolicyRuntime` (bases: object; decorators: None) — Bridges the simulation with PPO/backends via PettingZoo. (line 87)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 90)
    - `seed_anneal_rng(self, seed: int) -> None` — No docstring. (line 126)
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring. (line 129)
    - `enable_anneal_blend(self, enabled: bool) -> None` — No docstring. (line 135)
    - `register_ctx_reset_callback(self, callback: Callable[[str], None] | None) -> None` — No docstring. (line 138)
    - `set_policy_action_provider(self, provider: Callable[[WorldState, str, AgentIntent], AgentIntent | None]) -> None` — No docstring. (line 141)
    - `decide(self, world: WorldState, tick: int) -> dict[str, object]` — Return a primitive action per agent. (line 146)
    - `post_step(self, rewards: dict[str, float], terminated: dict[str, bool]) -> None` — Record rewards and termination signals into buffers. (line 209)
    - `flush_transitions(self, observations: dict[str, dict[str, object]]) -> list[dict[str, object]]` — Combine stored transition data with observations and return trajectory frames. (line 226)
    - `collect_trajectory(self, clear: bool = True) -> list[dict[str, object]]` — Return accumulated trajectory frames and reset internal buffer. (line 256)
    - `consume_option_switch_counts(self) -> dict[str, int]` — Return per-agent option switch counts accumulated since last call. (line 263)
    - `acquire_possession(self, agent_id: str) -> bool` — No docstring. (line 270)
    - `release_possession(self, agent_id: str) -> bool` — No docstring. (line 280)
    - `is_possessed(self, agent_id: str) -> bool` — No docstring. (line 286)
    - `possessed_agents(self) -> list[str]` — No docstring. (line 289)
    - `reset_state(self) -> None` — Reset transient buffers so snapshot loads don’t duplicate data. (line 292)
    - `_select_intent_with_blend(self, world: WorldState, agent_id: str, scripted: AgentIntent) -> AgentIntent` — No docstring. (line 302)
    - `_clone_intent(intent: AgentIntent) -> AgentIntent` — No docstring. (line 328)
    - `_intents_match(lhs: AgentIntent, rhs: AgentIntent) -> bool` — No docstring. (line 338)
    - `_enforce_option_commit(self, agent_id: str, tick: int, intent: AgentIntent) -> tuple[AgentIntent, bool]` — No docstring. (line 347)
    - `_annotate_with_policy_outputs(self, frame: dict[str, object]) -> None` — No docstring. (line 369)
    - `_update_policy_snapshot(self, frames: list[dict[str, object]]) -> None` — No docstring. (line 415)
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring. (line 454)
    - `active_policy_hash(self) -> str | None` — Return the configured policy hash, if any. (line 461)
    - `set_policy_hash(self, value: str | None) -> None` — Set the policy hash after loading a checkpoint. (line 466)
    - `current_anneal_ratio(self) -> float | None` — Return the latest anneal ratio (0..1) if tracking available. (line 471)
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring. (line 476)
    - `_ensure_policy_network(self, map_shape: tuple[int, int, int], feature_dim: int, action_dim: int) -> bool` — No docstring. (line 483)
    - `_build_policy_network(self, feature_dim: int, map_shape: tuple[int, int, int], action_dim: int) -> ConflictAwarePolicyNetwork` — No docstring. (line 520)
- `TrainingHarness` (bases: object; decorators: None) — Coordinates RL training sessions. (line 534)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 537)
    - `run(self) -> None` — Entry point for CLI training runs based on config.training.source. (line 550)
    - `current_anneal_ratio(self) -> float | None` — No docstring. (line 564)
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring. (line 567)
    - `run_replay(self, sample_path: Path, meta_path: Path | None = None) -> dict[str, float]` — Load a replay observation sample and surface conflict-aware stats. (line 574)
    - `run_replay_batch(self, pairs: Iterable[tuple[Path, Path | None]]) -> dict[str, float]` — No docstring. (line 582)
    - `run_replay_dataset(self, dataset_config: ReplayDatasetConfig) -> dict[str, float]` — No docstring. (line 589)
    - `capture_rollout(self, ticks: int, auto_seed_agents: bool = False, output_dir: Path | None = None, prefix: str = 'rollout_sample', compress: bool = True) -> RolloutBuffer` — Run the simulation loop for a fixed number of ticks and collect frames. (line 599)
    - `run_rollout_ppo(self, ticks: int, batch_size: int = 1, auto_seed_agents: bool = False, output_dir: Path | None = None, prefix: str = 'rollout_sample', compress: bool = True, epochs: int = 1, log_path: Path | None = None, log_frequency: int = 1, max_log_entries: int | None = None) -> dict[str, float]` — No docstring. (line 649)
    - `_load_bc_dataset(self, manifest: Path) -> BCTrajectoryDataset` — No docstring. (line 681)
    - `run_bc_training(self, *, manifest: Path | None = None, config: BCTrainingParams | None = None) -> dict[str, float]` — No docstring. (line 685)
    - `run_anneal(self, *, dataset_config: ReplayDatasetConfig | None = None, in_memory_dataset: InMemoryReplayDataset | None = None, log_dir: Path | None = None, bc_manifest: Path | None = None) -> list[dict[str, object]]` — No docstring. (line 723)
    - `run_ppo(self, dataset_config: ReplayDatasetConfig | None = None, epochs: int = 1, log_path: Path | None = None, log_frequency: int = 1, max_log_entries: int | None = None, in_memory_dataset: InMemoryReplayDataset | None = None) -> dict[str, float]` — No docstring. (line 823)
    - `evaluate_anneal_results(self, results: list[dict[str, object]]) -> str` — No docstring. (line 1321)
    - `last_anneal_status(self) -> str | None` — No docstring. (line 1336)
    - `_record_promotion_evaluation(self, *, status: str, results: list[dict[str, object]]) -> None` — No docstring. (line 1339)
    - `_select_social_reward_stage(self, cycle_id: int) -> str | None` — No docstring. (line 1378)
    - `_apply_social_reward_stage(self, cycle_id: int) -> None` — No docstring. (line 1397)
    - `_summarise_batch(self, batch: ReplayBatch, batch_index: int) -> dict[str, float]` — No docstring. (line 1405)
    - `build_replay_dataset(self, config: ReplayDatasetConfig) -> ReplayDataset` — No docstring. (line 1415)
    - `build_policy_network(self, feature_dim: int, map_shape: tuple[int, int, int], action_dim: int, hidden_dim: int | None = None) -> ConflictAwarePolicyNetwork` — No docstring. (line 1418)

### Functions
- `_softmax(logits: np.ndarray) -> np.ndarray` — No docstring. (line 54)
- `_pretty_action(action_repr: str) -> str` — No docstring. (line 66)

### Constants and Configuration
- `PPO_TELEMETRY_VERSION` = 1.2 (line 48)
- `ANNEAL_BC_MIN_DEFAULT` = 0.9 (line 49)
- `ANNEAL_LOSS_TOLERANCE_DEFAULT` = 0.1 (line 50)
- `ANNEAL_QUEUE_TOLERANCE_DEFAULT` = 0.15 (line 51)

### Data Flow
- Primary inputs: action_dim, action_repr, agent_id, auto_seed_agents, batch, batch_index, batch_size, bc_manifest, callback, clear, compress, config
- Return payloads: AgentIntent, BCTrajectoryDataset, ConflictAwarePolicyNetwork, None, ReplayDataset, RolloutBuffer, bool, dict[str, dict[str, object]], dict[str, float], dict[str, int], dict[str, object], float | None
- Annotates trajectories or config via PolicyRuntime._annotate_with_policy_outputs
- Applies world or agent state updates via TrainingHarness._apply_social_reward_stage
- Builds derived structures or observations via PolicyRuntime._build_policy_network, TrainingHarness.build_policy_network, TrainingHarness.build_replay_dataset
- Captures trajectories or telemetry snapshots via TrainingHarness.capture_rollout
- Evaluates conditions or invariants via TrainingHarness.evaluate_anneal_results
- Flushes buffers or queues via PolicyRuntime.flush_transitions
- Handles replay buffers or datasets via TrainingHarness.build_replay_dataset, TrainingHarness.run_replay, TrainingHarness.run_replay_batch, TrainingHarness.run_replay_dataset
- Loads configuration or datasets from disk via TrainingHarness._load_bc_dataset
- Records metrics or histories via TrainingHarness._record_promotion_evaluation
- Registers handlers or callbacks via PolicyRuntime.register_ctx_reset_callback
- Resets runtime state via PolicyRuntime.register_ctx_reset_callback, PolicyRuntime.reset_state
- Selects actions or decisions via PolicyRuntime.decide
- Summarises metrics for review via TrainingHarness._summarise_batch
- Trains policies or models via TrainingHarness.__init__, TrainingHarness._apply_social_reward_stage, TrainingHarness._load_bc_dataset, TrainingHarness._record_promotion_evaluation, TrainingHarness._select_social_reward_stage, TrainingHarness._summarise_batch, TrainingHarness.build_policy_network, TrainingHarness.build_replay_dataset, TrainingHarness.capture_rollout, TrainingHarness.current_anneal_ratio, TrainingHarness.evaluate_anneal_results, TrainingHarness.last_anneal_status, TrainingHarness.run, TrainingHarness.run_anneal, TrainingHarness.run_bc_training, TrainingHarness.run_ppo, TrainingHarness.run_replay, TrainingHarness.run_replay_batch, TrainingHarness.run_replay_dataset, TrainingHarness.run_rollout_ppo, TrainingHarness.set_anneal_ratio
- Updates internal caches or trackers via PolicyRuntime._update_policy_snapshot

### Integration Points
- External: numpy, torch, torch.distributions.Categorical, torch.nn.utils.clip_grad_norm_
- Internal: townlet.config.PPOConfig, townlet.config.SimulationConfig, townlet.core.sim_loop.SimulationLoop, townlet.policy.bc.BCTrainer, townlet.policy.bc.BCTrainingConfig, townlet.policy.bc.BCTrajectoryDataset, townlet.policy.bc.load_bc_samples, townlet.policy.behavior.AgentIntent, townlet.policy.behavior.BehaviorController, townlet.policy.behavior.build_behavior, townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.ConflictAwarePolicyNetwork, townlet.policy.models.TorchNotAvailableError, townlet.policy.models.torch_available, townlet.policy.ppo.utils.AdvantageReturns, townlet.policy.ppo.utils.clipped_value_loss, townlet.policy.ppo.utils.compute_gae, townlet.policy.ppo.utils.normalize_advantages, townlet.policy.ppo.utils.policy_surrogate, townlet.policy.ppo.utils.value_baseline_from_old_preds, townlet.policy.replay.ReplayBatch, townlet.policy.replay.ReplayDataset, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.replay.ReplaySample, townlet.policy.replay.build_batch, townlet.policy.replay.load_replay_sample, townlet.policy.replay_buffer.InMemoryReplayDataset, townlet.policy.rollout.RolloutBuffer, townlet.policy.scenario_utils.apply_scenario, townlet.policy.scenario_utils.has_agents, townlet.policy.scenario_utils.seed_default_agents, townlet.stability.promotion.PromotionManager, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: PolicyRuntime.__init__, PolicyRuntime._annotate_with_policy_outputs, PolicyRuntime._build_policy_network, PolicyRuntime._clone_intent, PolicyRuntime._enforce_option_commit, PolicyRuntime._ensure_policy_network, PolicyRuntime._intents_match, PolicyRuntime._select_intent_with_blend, PolicyRuntime._update_policy_snapshot, PolicyRuntime.acquire_possession, PolicyRuntime.enable_anneal_blend, PolicyRuntime.is_possessed, PolicyRuntime.latest_policy_snapshot, PolicyRuntime.possessed_agents, PolicyRuntime.register_ctx_reset_callback, PolicyRuntime.release_possession, PolicyRuntime.seed_anneal_rng, PolicyRuntime.set_anneal_ratio, PolicyRuntime.set_policy_action_provider, TrainingHarness.__init__
- ... 19 additional methods without docstrings
- Module exceeds 800 lines; consider refactoring into smaller components.

## `src/townlet/policy/scenario_utils.py`

**Purpose**: Helpers for applying scenario initialisation to simulation loops.
**Lines of code**: 93
**Dependencies**: stdlib=__future__.annotations, typing.Any; external=None; internal=townlet.core.sim_loop.SimulationLoop, townlet.policy.behavior.AgentIntent, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.core.sim_loop.SimulationLoop, townlet.policy.behavior.AgentIntent, townlet.world.grid.AgentSnapshot

### Classes
- `ScenarioBehavior` (bases: object; decorators: None) — Wraps an existing behavior controller with scripted schedules. (line 78)
  - Methods:
    - `__init__(self, base_behavior, schedules: dict[str, list[AgentIntent]]) -> None` — No docstring. (line 81)
    - `decide(self, world, agent_id)` — No docstring. (line 86)

### Functions
- `apply_scenario(loop: SimulationLoop, scenario: dict[str, Any]) -> None` — No docstring. (line 12)
- `seed_default_agents(loop: SimulationLoop) -> None` — No docstring. (line 58)
- `has_agents(loop: SimulationLoop) -> bool` — No docstring. (line 74)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, base_behavior, loop, scenario, schedules, world
- Return payloads: None, bool
- Applies world or agent state updates via apply_scenario
- Selects actions or decisions via ScenarioBehavior.decide

### Integration Points
- External: None
- Internal: townlet.core.sim_loop.SimulationLoop, townlet.policy.behavior.AgentIntent, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: ScenarioBehavior.__init__, ScenarioBehavior.decide, apply_scenario, has_agents, seed_default_agents

## `src/townlet/policy/scripted.py`

**Purpose**: Simple scripted policy helpers for trajectory capture.
**Lines of code**: 126
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass; external=None; internal=townlet.world.grid.WorldState
**Related modules**: townlet.world.grid.WorldState

### Classes
- `ScriptedPolicy` (bases: object; decorators: None) — Base class for scripted policies used during BC trajectory capture. (line 10)
  - Attributes:
    - name=`name`, type=`str`, default=`'scripted'` (line 13)
  - Methods:
    - `decide(self, world: WorldState, tick: int) -> dict[str, dict]` — No docstring. (line 15)
    - `describe(self) -> str` — No docstring. (line 20)
    - `trajectory_prefix(self) -> str` — No docstring. (line 24)
- `IdlePolicy` (bases: ScriptedPolicy; decorators: dataclass) — Default scripted policy: all agents wait every tick. (line 29)
  - Attributes:
    - name=`name`, type=`str`, default=`'idle'` (line 32)
  - Methods:
    - `decide(self, world: WorldState, tick: int) -> dict[str, dict]` — No docstring. (line 34)
- `ScriptedPolicyAdapter` (bases: object; decorators: None) — Adapter so SimulationLoop can call scripted policies. (line 47)
  - Methods:
    - `__init__(self, scripted_policy: ScriptedPolicy) -> None` — No docstring. (line 50)
    - `decide(self, world: WorldState, tick: int) -> dict[str, dict]` — No docstring. (line 59)
    - `post_step(self, rewards: dict[str, float], terminated: dict[str, bool]) -> None` — No docstring. (line 84)
    - `flush_transitions(self, observations) -> None` — No docstring. (line 93)
    - `collect_trajectory(self, *, clear: bool = False)` — No docstring. (line 99)
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring. (line 104)
    - `possessed_agents(self) -> list[str]` — No docstring. (line 107)
    - `consume_option_switch_counts(self) -> dict[str, int]` — No docstring. (line 110)
    - `active_policy_hash(self) -> str | None` — No docstring. (line 113)
    - `set_policy_hash(self, value: str | None) -> None` — No docstring. (line 116)
    - `current_anneal_ratio(self) -> float | None` — No docstring. (line 119)
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring. (line 122)
    - `enable_anneal_blend(self, _: bool) -> None` — No docstring. (line 125)

### Functions
- `get_scripted_policy(name: str) -> ScriptedPolicy` — Factory for scripted policies; extend with richer behaviours as needed. (line 38)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: _, clear, name, observations, ratio, rewards, scripted_policy, terminated, tick, value, world
- Return payloads: None, ScriptedPolicy, dict[str, dict[str, object]], dict[str, dict], dict[str, int], float | None, list[str], str, str | None
- Flushes buffers or queues via ScriptedPolicyAdapter.flush_transitions
- Selects actions or decisions via IdlePolicy.decide, ScriptedPolicy.decide, ScriptedPolicyAdapter.decide

### Integration Points
- External: None
- Internal: townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: IdlePolicy.decide, ScriptedPolicy.decide, ScriptedPolicy.describe, ScriptedPolicy.trajectory_prefix, ScriptedPolicyAdapter.__init__, ScriptedPolicyAdapter.active_policy_hash, ScriptedPolicyAdapter.collect_trajectory, ScriptedPolicyAdapter.consume_option_switch_counts, ScriptedPolicyAdapter.current_anneal_ratio, ScriptedPolicyAdapter.decide, ScriptedPolicyAdapter.enable_anneal_blend, ScriptedPolicyAdapter.flush_transitions, ScriptedPolicyAdapter.latest_policy_snapshot, ScriptedPolicyAdapter.possessed_agents, ScriptedPolicyAdapter.post_step, ScriptedPolicyAdapter.set_anneal_ratio, ScriptedPolicyAdapter.set_policy_hash

## `src/townlet/rewards/__init__.py`

**Purpose**: Reward computation utilities.
**Lines of code**: 7
**Dependencies**: stdlib=__future__.annotations; external=engine.RewardEngine; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: engine.RewardEngine
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/rewards/engine.py`

**Purpose**: Reward calculation guardrails and aggregation.
**Lines of code**: 257
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterable, collections.abc.Mapping; external=None; internal=townlet.config.SimulationConfig, townlet.world.grid.WorldState
**Related modules**: townlet.config.SimulationConfig, townlet.world.grid.WorldState

### Classes
- `RewardEngine` (bases: object; decorators: None) — Compute per-agent rewards with clipping and guardrails. (line 11)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 14)
    - `compute(self, world: WorldState, terminated: dict[str, bool], reasons: Mapping[str, str] | None = None) -> dict[str, float]` — No docstring. (line 20)
    - `_consume_chat_events(self, world: WorldState) -> Iterable[dict[str, object]]` — No docstring. (line 122)
    - `_social_rewards_enabled(self) -> bool` — No docstring. (line 128)
    - `_compute_chat_rewards(self, world: WorldState, events: Iterable[dict[str, object]]) -> dict[str, float]` — No docstring. (line 132)
    - `_needs_override(self, snapshot) -> bool` — No docstring. (line 172)
    - `_is_blocked(self, agent_id: str, tick: int, window: int) -> bool` — No docstring. (line 182)
    - `_prune_termination_blocks(self, tick: int, window: int) -> None` — No docstring. (line 190)
    - `_compute_wage_bonus(self, agent_id: str, world: WorldState, wage_rate: float) -> float` — No docstring. (line 202)
    - `_compute_punctuality_bonus(self, agent_id: str, world: WorldState, bonus_rate: float) -> float` — No docstring. (line 215)
    - `_compute_terminal_penalty(self, agent_id: str, terminated: Mapping[str, bool], reasons: Mapping[str, str]) -> float` — No docstring. (line 227)
    - `_reset_episode_totals(self, terminated: dict[str, bool], world: WorldState) -> None` — No docstring. (line 242)
    - `latest_reward_breakdown(self) -> dict[str, dict[str, float]]` — No docstring. (line 253)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, bonus_rate, config, events, reasons, snapshot, terminated, tick, wage_rate, window, world
- Return payloads: Iterable[dict[str, object]], None, bool, dict[str, dict[str, float]], dict[str, float], float
- Computes metrics or rewards via RewardEngine._compute_chat_rewards, RewardEngine._compute_punctuality_bonus, RewardEngine._compute_terminal_penalty, RewardEngine._compute_wage_bonus, RewardEngine.compute
- Resets runtime state via RewardEngine._reset_episode_totals

### Integration Points
- External: None
- Internal: townlet.config.SimulationConfig, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: RewardEngine.__init__, RewardEngine._compute_chat_rewards, RewardEngine._compute_punctuality_bonus, RewardEngine._compute_terminal_penalty, RewardEngine._compute_wage_bonus, RewardEngine._consume_chat_events, RewardEngine._is_blocked, RewardEngine._needs_override, RewardEngine._prune_termination_blocks, RewardEngine._reset_episode_totals, RewardEngine._social_rewards_enabled, RewardEngine.compute, RewardEngine.latest_reward_breakdown

## `src/townlet/scheduler/__init__.py`

**Purpose**: Schedulers for perturbations and timers.
**Lines of code**: 7
**Dependencies**: stdlib=__future__.annotations; external=perturbations.PerturbationScheduler, perturbations.ScheduledPerturbation; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: perturbations.PerturbationScheduler, perturbations.ScheduledPerturbation
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/scheduler/perturbations.py`

**Purpose**: Perturbation scheduler scaffolding.
**Lines of code**: 568
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterable, collections.abc.Mapping, dataclasses.dataclass, dataclasses.field, random, typing.Optional; external=None; internal=townlet.config.ArrangedMeetEventConfig, townlet.config.BlackoutEventConfig, townlet.config.OutageEventConfig, townlet.config.PerturbationEventConfig, townlet.config.PerturbationKind, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.SimulationConfig, townlet.utils.decode_rng_state, townlet.utils.encode_rng_state, townlet.world.grid.WorldState
**Related modules**: townlet.config.ArrangedMeetEventConfig, townlet.config.BlackoutEventConfig, townlet.config.OutageEventConfig, townlet.config.PerturbationEventConfig, townlet.config.PerturbationKind, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.SimulationConfig, townlet.utils.decode_rng_state, townlet.utils.encode_rng_state, townlet.world.grid.WorldState

### Classes
- `ScheduledPerturbation` (bases: object; decorators: dataclass) — Represents a perturbation that is pending or active in the world. (line 25)
  - Attributes:
    - name=`event_id`, type=`str` (line 28)
    - name=`spec_name`, type=`str` (line 29)
    - name=`kind`, type=`PerturbationKind` (line 30)
    - name=`started_at`, type=`int` (line 31)
    - name=`ends_at`, type=`int` (line 32)
    - name=`payload`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 33)
    - name=`targets`, type=`list[str]`, default=`field(default_factory=list)` (line 34)
- `PerturbationScheduler` (bases: object; decorators: None) — Injects bounded random events into the world. (line 37)
  - Methods:
    - `__init__(self, config: SimulationConfig, *, rng: Optional[random.Random] = None) -> None` — No docstring. (line 40)
    - `pending_count(self) -> int` — No docstring. (line 63)
    - `active_count(self) -> int` — No docstring. (line 66)
    - `tick(self, world: WorldState, current_tick: int) -> None` — No docstring. (line 72)
    - `_expire_active(self, current_tick: int, world: WorldState) -> None` — No docstring. (line 79)
    - `_expire_cooldowns(self, current_tick: int) -> None` — No docstring. (line 88)
    - `_expire_window_events(self, current_tick: int) -> None` — No docstring. (line 100)
    - `_drain_pending(self, world: WorldState, current_tick: int) -> None` — No docstring. (line 110)
    - `_maybe_schedule(self, world: WorldState, current_tick: int) -> None` — No docstring. (line 121)
    - `schedule_manual(self, world: WorldState, spec_name: str, current_tick: int, *, starts_in: int = 0, duration: int | None = None, targets: Optional[list[str]] = None, payload_overrides: Optional[dict[str, object]] = None) -> ScheduledPerturbation` — No docstring. (line 147)
    - `cancel_event(self, world: WorldState, event_id: str) -> bool` — No docstring. (line 180)
    - `_activate(self, world: WorldState, event: ScheduledPerturbation) -> None` — No docstring. (line 209)
    - `_apply_event(self, world: WorldState, event: ScheduledPerturbation) -> None` — No docstring. (line 237)
    - `_on_event_concluded(self, world: WorldState, event: ScheduledPerturbation) -> None` — No docstring. (line 279)
    - `seed(self, value: int) -> None` — No docstring. (line 291)
    - `_can_fire_spec(self, name: str, spec: PerturbationEventConfig, current_tick: int) -> bool` — No docstring. (line 297)
    - `_per_tick_probability(self, spec: PerturbationEventConfig) -> float` — No docstring. (line 321)
    - `_generate_event(self, name: str, spec: PerturbationEventConfig, current_tick: int, world: WorldState, *, duration_override: int | None = None, targets_override: Optional[list[str]] = None, payload_override: Optional[dict[str, object]] = None) -> Optional[ScheduledPerturbation]` — No docstring. (line 324)
    - `_eligible_agents(self, world: WorldState, current_tick: int) -> list[str]` — No docstring. (line 386)
    - `enqueue(self, events: Iterable[ScheduledPerturbation | Mapping[str, object]]) -> None` — No docstring. (line 397)
    - `pending(self) -> list[ScheduledPerturbation]` — No docstring. (line 408)
    - `active(self) -> dict[str, ScheduledPerturbation]` — No docstring. (line 412)
    - `export_state(self) -> dict[str, object]` — No docstring. (line 418)
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring. (line 432)
    - `reset_state(self) -> None` — No docstring. (line 478)
    - `allocate_event_id(self) -> str` — No docstring. (line 489)
    - `spec_for(self, name: str) -> Optional[PerturbationEventConfig]` — No docstring. (line 494)
    - `rng_state(self) -> tuple` — No docstring. (line 497)
    - `set_rng_state(self, state: tuple) -> None` — No docstring. (line 500)
    - `rng(self) -> random.Random` — No docstring. (line 504)
    - `_coerce_event(self, data: Mapping[str, object]) -> ScheduledPerturbation` — No docstring. (line 507)
    - `_serialize_event(event: ScheduledPerturbation) -> dict[str, object]` — No docstring. (line 543)
    - `serialize_event(self, event: ScheduledPerturbation) -> dict[str, object]` — No docstring. (line 554)
    - `latest_state(self) -> dict[str, object]` — No docstring. (line 557)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config, current_tick, data, duration, duration_override, event, event_id, events, name, payload, payload_override, payload_overrides
- Return payloads: None, Optional[PerturbationEventConfig], Optional[ScheduledPerturbation], ScheduledPerturbation, bool, dict[str, ScheduledPerturbation], dict[str, object], float, int, list[ScheduledPerturbation], list[str], random.Random
- Advances tick or scheduler timelines via PerturbationScheduler._per_tick_probability, PerturbationScheduler.tick
- Applies world or agent state updates via PerturbationScheduler._apply_event
- Exports payloads for downstream consumers via PerturbationScheduler.export_state
- Resets runtime state via PerturbationScheduler.reset_state

### Integration Points
- External: None
- Internal: townlet.config.ArrangedMeetEventConfig, townlet.config.BlackoutEventConfig, townlet.config.OutageEventConfig, townlet.config.PerturbationEventConfig, townlet.config.PerturbationKind, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.SimulationConfig, townlet.utils.decode_rng_state, townlet.utils.encode_rng_state, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: PerturbationScheduler.__init__, PerturbationScheduler._activate, PerturbationScheduler._apply_event, PerturbationScheduler._can_fire_spec, PerturbationScheduler._coerce_event, PerturbationScheduler._drain_pending, PerturbationScheduler._eligible_agents, PerturbationScheduler._expire_active, PerturbationScheduler._expire_cooldowns, PerturbationScheduler._expire_window_events, PerturbationScheduler._generate_event, PerturbationScheduler._maybe_schedule, PerturbationScheduler._on_event_concluded, PerturbationScheduler._per_tick_probability, PerturbationScheduler._serialize_event, PerturbationScheduler.active, PerturbationScheduler.active_count, PerturbationScheduler.allocate_event_id, PerturbationScheduler.cancel_event, PerturbationScheduler.enqueue
- ... 14 additional methods without docstrings

## `src/townlet/snapshots/__init__.py`

**Purpose**: Snapshot and restore helpers.
**Lines of code**: 25
**Dependencies**: stdlib=__future__.annotations; external=migrations.clear_registry, migrations.register_migration, migrations.registry, state.SnapshotManager, state.SnapshotState, state.apply_snapshot_to_telemetry, state.apply_snapshot_to_world, state.snapshot_from_world; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: migrations.clear_registry, migrations.register_migration, migrations.registry, state.SnapshotManager, state.SnapshotState, state.apply_snapshot_to_telemetry, state.apply_snapshot_to_world, state.snapshot_from_world
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/snapshots/migrations.py`

**Purpose**: Snapshot migration registry and helpers.
**Lines of code**: 121
**Dependencies**: stdlib=__future__.annotations, collections.abc.Callable, collections.abc.Iterable, collections.deque, dataclasses.dataclass, typing.TYPE_CHECKING; external=None; internal=townlet.config.SimulationConfig, townlet.snapshots.state.SnapshotState
**Related modules**: townlet.config.SimulationConfig, townlet.snapshots.state.SnapshotState

### Classes
- `MigrationNotFoundError` (bases: Exception; decorators: None) — Raised when no migration path exists between config identifiers. (line 19)
- `MigrationExecutionError` (bases: Exception; decorators: None) — Raised when a migration handler fails or leaves the snapshot unchanged. (line 23)
- `MigrationEdge` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 28)
  - Attributes:
    - name=`source`, type=`str` (line 29)
    - name=`target`, type=`str` (line 30)
    - name=`handler`, type=`MigrationHandler` (line 31)
  - Methods:
    - `identifier(self) -> str` — No docstring. (line 34)
- `SnapshotMigrationRegistry` (bases: object; decorators: None) — Maintains registered snapshot migrations keyed by config identifiers. (line 40)
  - Methods:
    - `__init__(self) -> None` — No docstring. (line 43)
    - `register(self, from_config: str, to_config: str, handler: MigrationHandler) -> None` — No docstring. (line 46)
    - `clear(self) -> None` — No docstring. (line 54)
    - `_neighbours(self, node: str) -> Iterable[MigrationEdge]` — No docstring. (line 57)
    - `find_path(self, start: str, goal: str) -> list[MigrationEdge]` — No docstring. (line 60)
    - `apply_path(self, path: list[MigrationEdge], state: 'SnapshotState', config: 'SimulationConfig') -> tuple['SnapshotState', list[str]]` — No docstring. (line 81)

### Functions
- `register_migration(from_config: str, to_config: str, handler: MigrationHandler) -> None` — Register a snapshot migration handler. (line 110)
- `clear_registry() -> None` — Reset registry (intended for test teardown). (line 118)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config, from_config, goal, handler, node, path, start, state, to_config
- Return payloads: Iterable[MigrationEdge], None, list[MigrationEdge], str, tuple['SnapshotState', list[str]]
- Applies world or agent state updates via SnapshotMigrationRegistry.apply_path
- Registers handlers or callbacks via SnapshotMigrationRegistry.register, register_migration

### Integration Points
- External: None
- Internal: townlet.config.SimulationConfig, townlet.snapshots.state.SnapshotState

### Code Quality Notes
- Missing docstrings: MigrationEdge.identifier, SnapshotMigrationRegistry.__init__, SnapshotMigrationRegistry._neighbours, SnapshotMigrationRegistry.apply_path, SnapshotMigrationRegistry.clear, SnapshotMigrationRegistry.find_path, SnapshotMigrationRegistry.register

## `src/townlet/snapshots/state.py`

**Purpose**: Snapshot persistence scaffolding.
**Lines of code**: 625
**Dependencies**: stdlib=__future__.annotations, collections.abc.Mapping, dataclasses.dataclass, dataclasses.field, json, logging, pathlib.Path, random, typing.Optional, typing.TYPE_CHECKING; external=None; internal=townlet.agents.models.Personality, townlet.config.SimulationConfig, townlet.lifecycle.manager.LifecycleManager, townlet.scheduler.perturbations.PerturbationScheduler, townlet.snapshots.migrations.MigrationExecutionError, townlet.snapshots.migrations.MigrationNotFoundError, townlet.snapshots.migrations.migration_registry, townlet.stability.monitor.StabilityMonitor, townlet.stability.promotion.PromotionManager, townlet.telemetry.publisher.TelemetryPublisher, townlet.utils.decode_rng_state, townlet.utils.encode_rng, townlet.utils.encode_rng_state, townlet.world.grid.AgentSnapshot, townlet.world.grid.InteractiveObject, townlet.world.grid.WorldState
**Related modules**: townlet.agents.models.Personality, townlet.config.SimulationConfig, townlet.lifecycle.manager.LifecycleManager, townlet.scheduler.perturbations.PerturbationScheduler, townlet.snapshots.migrations.MigrationExecutionError, townlet.snapshots.migrations.MigrationNotFoundError, townlet.snapshots.migrations.migration_registry, townlet.stability.monitor.StabilityMonitor, townlet.stability.promotion.PromotionManager, townlet.telemetry.publisher.TelemetryPublisher, townlet.utils.decode_rng_state, townlet.utils.encode_rng, townlet.utils.encode_rng_state, townlet.world.grid.AgentSnapshot, townlet.world.grid.InteractiveObject, townlet.world.grid.WorldState

### Classes
- `SnapshotState` (bases: object; decorators: dataclass) — No class docstring provided. (line 50)
  - Attributes:
    - name=`config_id`, type=`str` (line 51)
    - name=`tick`, type=`int` (line 52)
    - name=`agents`, type=`dict[str, dict[str, object]]`, default=`field(default_factory=dict)` (line 53)
    - name=`objects`, type=`dict[str, dict[str, object]]`, default=`field(default_factory=dict)` (line 54)
    - name=`queues`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 55)
    - name=`embeddings`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 56)
    - name=`employment`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 57)
    - name=`lifecycle`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 58)
    - name=`rng_state`, type=`Optional[str]`, default=`None` (line 59)
    - name=`rng_streams`, type=`dict[str, str]`, default=`field(default_factory=dict)` (line 60)
    - name=`telemetry`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 61)
    - name=`console_buffer`, type=`list[object]`, default=`field(default_factory=list)` (line 62)
    - name=`perturbations`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 63)
    - name=`relationships`, type=`dict[str, dict[str, dict[str, float]]]`, default=`field(default_factory=dict)` (line 64)
    - name=`stability`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 65)
    - name=`promotion`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 66)
    - name=`identity`, type=`dict[str, object]`, default=`field(default_factory=dict)` (line 67)
    - name=`migrations`, type=`dict[str, object]`, default=`field(default_factory=lambda: {'applied': [], 'required': []})` (line 68)
  - Methods:
    - `as_dict(self) -> dict[str, object]` — No docstring. (line 72)
    - `from_dict(cls, payload: Mapping[str, object]) -> 'SnapshotState'` — No docstring. (line 102)
- `SnapshotManager` (bases: object; decorators: None) — Handles save/load of simulation state and RNG streams. (line 498)
  - Methods:
    - `__init__(self, root: Path) -> None` — No docstring. (line 501)
    - `save(self, state: SnapshotState) -> Path` — No docstring. (line 504)
    - `load(self, path: Path, config: SimulationConfig, *, allow_migration: bool | None = None, allow_downgrade: bool | None = None, require_exact_config: bool | None = None) -> SnapshotState` — No docstring. (line 516)

### Functions
- `_parse_version(value: str) -> tuple[int, ...]` — No docstring. (line 34)
- `snapshot_from_world(config: SimulationConfig, world: WorldState, *, lifecycle: Optional[LifecycleManager] = None, telemetry: Optional['TelemetryPublisher'] = None, perturbations: Optional[PerturbationScheduler] = None, stability: Optional['StabilityMonitor'] = None, promotion: Optional['PromotionManager'] = None, rng_streams: Optional[Mapping[str, random.Random]] = None, identity: Optional[Mapping[str, object]] = None) -> SnapshotState` — Capture the current world state into a snapshot payload. (line 251)
- `apply_snapshot_to_world(world: WorldState, snapshot: SnapshotState, *, lifecycle: Optional[LifecycleManager] = None) -> None` — Restore world, queue, embeddings, and lifecycle state from snapshot. (line 381)
- `apply_snapshot_to_telemetry(telemetry: 'TelemetryPublisher', snapshot: SnapshotState) -> None` — No docstring. (line 478)

### Constants and Configuration
- `SNAPSHOT_SCHEMA_VERSION` = '1.5' (line 31)

### Data Flow
- Primary inputs: allow_downgrade, allow_migration, config, identity, lifecycle, path, payload, perturbations, promotion, require_exact_config, rng_streams, root
- Return payloads: 'SnapshotState', None, Path, SnapshotState, dict[str, object], tuple[int, ...]
- Applies world or agent state updates via apply_snapshot_to_telemetry, apply_snapshot_to_world
- Loads configuration or datasets from disk via SnapshotManager.load
- Persists state or reports to disk via SnapshotManager.save

### Integration Points
- External: None
- Internal: townlet.agents.models.Personality, townlet.config.SimulationConfig, townlet.lifecycle.manager.LifecycleManager, townlet.scheduler.perturbations.PerturbationScheduler, townlet.snapshots.migrations.MigrationExecutionError, townlet.snapshots.migrations.MigrationNotFoundError, townlet.snapshots.migrations.migration_registry, townlet.stability.monitor.StabilityMonitor, townlet.stability.promotion.PromotionManager, townlet.telemetry.publisher.TelemetryPublisher, townlet.utils.decode_rng_state, townlet.utils.encode_rng, townlet.utils.encode_rng_state, townlet.world.grid.AgentSnapshot, townlet.world.grid.InteractiveObject, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: SnapshotManager.__init__, SnapshotManager.load, SnapshotManager.save, SnapshotState.as_dict, SnapshotState.from_dict, _parse_version, apply_snapshot_to_telemetry

## `src/townlet/stability/__init__.py`

**Purpose**: Stability guardrails.
**Lines of code**: 8
**Dependencies**: stdlib=__future__.annotations; external=monitor.StabilityMonitor, promotion.PromotionManager; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: monitor.StabilityMonitor, promotion.PromotionManager
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/stability/monitor.py`

**Purpose**: Monitors KPIs and promotion guardrails.
**Lines of code**: 420
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterable, collections.deque; external=None; internal=townlet.config.SimulationConfig
**Related modules**: townlet.config.SimulationConfig

### Classes
- `StabilityMonitor` (bases: object; decorators: None) — Tracks rolling metrics and canaries. (line 11)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 14)
    - `_promotion_snapshot(self) -> dict[str, object]` — No docstring. (line 51)
    - `_finalise_promotion_window(self, window_end: int) -> None` — No docstring. (line 64)
    - `_update_promotion_window(self, tick: int, alerts: Iterable[str]) -> None` — No docstring. (line 79)
    - `track(self, *, tick: int, rewards: dict[str, float], terminated: dict[str, bool], queue_metrics: dict[str, int] | None = None, embedding_metrics: dict[str, float] | None = None, job_snapshot: dict[str, dict[str, object]] | None = None, events: Iterable[dict[str, object]] | None = None, employment_metrics: dict[str, object] | None = None, hunger_levels: dict[str, float] | None = None, option_switch_counts: dict[str, int] | None = None, rivalry_events: Iterable[dict[str, object]] | None = None) -> None` — No docstring. (line 89)
    - `latest_metrics(self) -> dict[str, object]` — No docstring. (line 218)
    - `export_state(self) -> dict[str, object]` — No docstring. (line 221)
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring. (line 241)
    - `reset_state(self) -> None` — No docstring. (line 309)
    - `_update_starvation_state(self, *, tick: int, hunger_levels: dict[str, float] | None, terminated: dict[str, bool]) -> int` — No docstring. (line 329)
    - `_update_reward_samples(self, *, tick: int, rewards: dict[str, float]) -> tuple[float | None, float | None, int]` — No docstring. (line 364)
    - `_threshold_snapshot(self) -> dict[str, object]` — No docstring. (line 388)
    - `_update_option_samples(self, *, tick: int, option_switch_counts: dict[str, int] | None, active_agent_count: int) -> float | None` — No docstring. (line 397)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: active_agent_count, alerts, config, embedding_metrics, employment_metrics, events, hunger_levels, job_snapshot, option_switch_counts, payload, queue_metrics, rewards
- Return payloads: None, dict[str, object], float | None, int, tuple[float | None, float | None, int]
- Exports payloads for downstream consumers via StabilityMonitor.export_state
- Resets runtime state via StabilityMonitor.reset_state
- Updates internal caches or trackers via StabilityMonitor._update_option_samples, StabilityMonitor._update_promotion_window, StabilityMonitor._update_reward_samples, StabilityMonitor._update_starvation_state

### Integration Points
- External: None
- Internal: townlet.config.SimulationConfig

### Code Quality Notes
- Missing docstrings: StabilityMonitor.__init__, StabilityMonitor._finalise_promotion_window, StabilityMonitor._promotion_snapshot, StabilityMonitor._threshold_snapshot, StabilityMonitor._update_option_samples, StabilityMonitor._update_promotion_window, StabilityMonitor._update_reward_samples, StabilityMonitor._update_starvation_state, StabilityMonitor.export_state, StabilityMonitor.import_state, StabilityMonitor.latest_metrics, StabilityMonitor.reset_state, StabilityMonitor.track

## `src/townlet/stability/promotion.py`

**Purpose**: Promotion gate state tracking.
**Lines of code**: 263
**Dependencies**: stdlib=__future__.annotations, collections.abc.Mapping, collections.deque, json, pathlib.Path; external=None; internal=townlet.config.SimulationConfig
**Related modules**: townlet.config.SimulationConfig

### Classes
- `PromotionManager` (bases: object; decorators: None) — Tracks promotion readiness and release/shadow state. (line 13)
  - Methods:
    - `__init__(self, config: SimulationConfig, log_path: Path | None = None) -> None` — No docstring. (line 16)
    - `update_from_metrics(self, metrics: Mapping[str, object], *, tick: int) -> None` — Update state based on the latest stability metrics. (line 39)
    - `mark_promoted(self, *, tick: int, metadata: Mapping[str, object] | None = None) -> None` — Record a promotion event and update release metadata. (line 62)
    - `register_rollback(self, *, tick: int, metadata: Mapping[str, object] | None = None) -> None` — Record a rollback event and return to monitoring state. (line 86)
    - `record_manual_swap(self, *, tick: int, metadata: Mapping[str, object]) -> dict[str, object]` — Record a manual policy swap without altering candidate readiness. (line 110)
    - `set_candidate_metadata(self, metadata: Mapping[str, object] | None) -> None` — No docstring. (line 136)
    - `snapshot(self) -> dict[str, object]` — No docstring. (line 139)
    - `export_state(self) -> dict[str, object]` — No docstring. (line 156)
    - `import_state(self, payload: Mapping[str, object]) -> None` — No docstring. (line 159)
    - `reset(self) -> None` — No docstring. (line 189)
    - `_log_event(self, record: Mapping[str, object]) -> None` — No docstring. (line 200)
    - `_normalise_release(self, metadata: Mapping[str, object] | None) -> dict[str, object]` — No docstring. (line 215)
    - `_resolve_rollback_target(self, metadata: Mapping[str, object] | None) -> dict[str, object]` — No docstring. (line 227)
    - `_latest_promoted_release(self) -> dict[str, object] | None` — No docstring. (line 241)
    - `state(self) -> str` — No docstring. (line 254)
    - `candidate_ready(self) -> bool` — No docstring. (line 258)
    - `pass_streak(self) -> int` — No docstring. (line 262)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config, log_path, metadata, metrics, payload, record, tick
- Return payloads: None, bool, dict[str, object], dict[str, object] | None, int, str
- Exports payloads for downstream consumers via PromotionManager.export_state
- Promotes builds or policies via PromotionManager._latest_promoted_release, PromotionManager.mark_promoted
- Records metrics or histories via PromotionManager.record_manual_swap
- Registers handlers or callbacks via PromotionManager.register_rollback
- Resets runtime state via PromotionManager.reset
- Updates internal caches or trackers via PromotionManager.update_from_metrics

### Integration Points
- External: None
- Internal: townlet.config.SimulationConfig

### Code Quality Notes
- Missing docstrings: PromotionManager.__init__, PromotionManager._latest_promoted_release, PromotionManager._log_event, PromotionManager._normalise_release, PromotionManager._resolve_rollback_target, PromotionManager.candidate_ready, PromotionManager.export_state, PromotionManager.import_state, PromotionManager.pass_streak, PromotionManager.reset, PromotionManager.set_candidate_metadata, PromotionManager.snapshot, PromotionManager.state

## `src/townlet/telemetry/__init__.py`

**Purpose**: Telemetry publication surfaces.
**Lines of code**: 7
**Dependencies**: stdlib=__future__.annotations; external=publisher.TelemetryPublisher; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: publisher.TelemetryPublisher
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/telemetry/narration.py`

**Purpose**: Narration throttling utilities.
**Lines of code**: 133
**Dependencies**: stdlib=__future__.annotations, collections.deque; external=None; internal=townlet.config.NarrationThrottleConfig
**Related modules**: townlet.config.NarrationThrottleConfig

### Classes
- `NarrationRateLimiter` (bases: object; decorators: None) — Apply global and per-category narration cooldowns with dedupe. (line 10)
  - Methods:
    - `__init__(self, config: NarrationThrottleConfig) -> None` — No docstring. (line 13)
    - `begin_tick(self, tick: int) -> None` — No docstring. (line 21)
    - `allow(self, category: str, *, message: str, priority: bool = False, dedupe_key: str | None = None) -> bool` — Return True if a narration may be emitted for the given category. (line 26)
    - `export_state(self) -> dict[str, object]` — No docstring. (line 61)
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring. (line 69)
    - `_expire_recent_entries(self) -> None` — No docstring. (line 88)
    - `_expire_window(self) -> None` — No docstring. (line 100)
    - `_check_global_cooldown(self) -> bool` — No docstring. (line 108)
    - `_check_category_cooldown(self, category: str) -> bool` — No docstring. (line 114)
    - `_check_window_limit(self) -> bool` — No docstring. (line 121)
    - `_record_emission(self, category: str, dedupe_key: str) -> None` — No docstring. (line 127)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: category, config, dedupe_key, message, payload, priority, tick
- Return payloads: None, bool, dict[str, object]
- Advances tick or scheduler timelines via NarrationRateLimiter.begin_tick
- Exports payloads for downstream consumers via NarrationRateLimiter.export_state
- Records metrics or histories via NarrationRateLimiter._record_emission

### Integration Points
- External: None
- Internal: townlet.config.NarrationThrottleConfig

### Code Quality Notes
- Missing docstrings: NarrationRateLimiter.__init__, NarrationRateLimiter._check_category_cooldown, NarrationRateLimiter._check_global_cooldown, NarrationRateLimiter._check_window_limit, NarrationRateLimiter._expire_recent_entries, NarrationRateLimiter._expire_window, NarrationRateLimiter._record_emission, NarrationRateLimiter.begin_tick, NarrationRateLimiter.export_state, NarrationRateLimiter.import_state

## `src/townlet/telemetry/publisher.py`

**Purpose**: Telemetry pipelines and console bridge.
**Lines of code**: 1393
**Dependencies**: stdlib=__future__.annotations, collections.abc.Callable, collections.abc.Iterable, collections.abc.Mapping, collections.deque, json, logging, pathlib.Path, threading, time, typing.Any, typing.TYPE_CHECKING; external=None; internal=townlet.config.SimulationConfig, townlet.console.command.ConsoleCommandResult, townlet.telemetry.narration.NarrationRateLimiter, townlet.telemetry.transport.TelemetryTransportError, townlet.telemetry.transport.TransportBuffer, townlet.telemetry.transport.create_transport, townlet.world.grid.WorldState
**Related modules**: townlet.config.SimulationConfig, townlet.console.command.ConsoleCommandResult, townlet.telemetry.narration.NarrationRateLimiter, townlet.telemetry.transport.TelemetryTransportError, townlet.telemetry.transport.TransportBuffer, townlet.telemetry.transport.create_transport, townlet.world.grid.WorldState

### Classes
- `TelemetryPublisher` (bases: object; decorators: None) — Publishes observer snapshots and consumes console commands. (line 29)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 32)
    - `queue_console_command(self, command: object) -> None` — No docstring. (line 110)
    - `drain_console_buffer(self) -> Iterable[object]` — No docstring. (line 113)
    - `export_state(self) -> dict[str, object]` — No docstring. (line 118)
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring. (line 174)
    - `export_console_buffer(self) -> list[object]` — No docstring. (line 362)
    - `import_console_buffer(self, buffer: Iterable[object]) -> None` — No docstring. (line 365)
    - `record_console_results(self, results: Iterable['ConsoleCommandResult']) -> None` — No docstring. (line 368)
    - `latest_console_results(self) -> list[dict[str, Any]]` — No docstring. (line 377)
    - `console_history(self) -> list[dict[str, Any]]` — No docstring. (line 380)
    - `record_possessed_agents(self, agents: Iterable[str]) -> None` — No docstring. (line 383)
    - `latest_possessed_agents(self) -> list[str]` — No docstring. (line 386)
    - `latest_precondition_failures(self) -> list[dict[str, object]]` — No docstring. (line 389)
    - `latest_transport_status(self) -> dict[str, object]` — Return transport health and backlog counters for observability. (line 392)
    - `record_health_metrics(self, metrics: Mapping[str, object]) -> None` — No docstring. (line 397)
    - `latest_health_status(self) -> dict[str, object]` — No docstring. (line 400)
    - `_build_transport_client(self)` — No docstring. (line 403)
    - `_reset_transport_client(self) -> None` — No docstring. (line 418)
    - `_send_with_retry(self, payload: bytes, tick: int) -> bool` — No docstring. (line 427)
    - `_flush_transport_buffer(self, tick: int) -> None` — No docstring. (line 461)
    - `_flush_loop(self) -> None` — No docstring. (line 499)
    - `_enqueue_stream_payload(self, payload: Mapping[str, Any], *, tick: int) -> None` — No docstring. (line 516)
    - `_build_stream_payload(self, tick: int) -> dict[str, Any]` — No docstring. (line 548)
    - `close(self) -> None` — No docstring. (line 591)
    - `stop_worker(self, *, wait: bool = True, timeout: float = 2.0) -> None` — Stop the background flush worker without closing transports. (line 603)
    - `publish_tick(self, *, tick: int, world: WorldState, observations: dict[str, object], rewards: dict[str, float], events: Iterable[dict[str, object]] | None = None, policy_snapshot: Mapping[str, Mapping[str, object]] | None = None, kpi_history: bool = False, reward_breakdown: Mapping[str, Mapping[str, float]] | None = None, stability_inputs: Mapping[str, object] | None = None, perturbations: Mapping[str, object] | None = None, policy_identity: Mapping[str, object] | None = None, possessed_agents: Iterable[str] | None = None) -> None` — No docstring. (line 612)
    - `latest_queue_metrics(self) -> dict[str, int] | None` — Expose the most recent queue-related telemetry counters. (line 802)
    - `latest_queue_history(self) -> list[dict[str, object]]` — No docstring. (line 808)
    - `latest_rivalry_events(self) -> list[dict[str, object]]` — No docstring. (line 813)
    - `update_anneal_status(self, status: Mapping[str, object] | None) -> None` — Record the latest anneal status payload for observer dashboards. (line 818)
    - `kpi_history(self) -> dict[str, list[float]]` — No docstring. (line 822)
    - `latest_conflict_snapshot(self) -> dict[str, object]` — Return the conflict-focused telemetry payload (queues + rivalry). (line 825)
    - `latest_affordance_manifest(self) -> dict[str, object]` — Expose the most recent affordance manifest metadata. (line 858)
    - `latest_reward_breakdown(self) -> dict[str, dict[str, float]]` — No docstring. (line 863)
    - `latest_stability_inputs(self) -> dict[str, object]` — No docstring. (line 868)
    - `record_stability_metrics(self, metrics: Mapping[str, object]) -> None` — No docstring. (line 887)
    - `latest_stability_metrics(self) -> dict[str, object]` — No docstring. (line 890)
    - `latest_promotion_state(self) -> dict[str, object] | None` — No docstring. (line 893)
    - `_append_console_audit(self, payload: Mapping[str, Any]) -> None` — No docstring. (line 902)
    - `latest_stability_alerts(self) -> list[str]` — No docstring. (line 910)
    - `latest_perturbations(self) -> dict[str, object]` — No docstring. (line 917)
    - `update_policy_identity(self, identity: Mapping[str, object] | None) -> None` — No docstring. (line 930)
    - `latest_policy_identity(self) -> dict[str, object] | None` — No docstring. (line 942)
    - `record_snapshot_migrations(self, applied: Iterable[str]) -> None` — No docstring. (line 947)
    - `latest_snapshot_migrations(self) -> list[str]` — No docstring. (line 950)
    - `_normalize_perturbations_payload(self, payload: Mapping[str, object]) -> dict[str, object]` — No docstring. (line 953)
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring. (line 990)
    - `latest_anneal_status(self) -> dict[str, object] | None` — No docstring. (line 993)
    - `latest_relationship_metrics(self) -> dict[str, object] | None` — Expose relationship churn payload captured during publish. (line 998)
    - `latest_relationship_snapshot(self) -> dict[str, dict[str, dict[str, float]]]` — No docstring. (line 1008)
    - `latest_relationship_updates(self) -> list[dict[str, object]]` — No docstring. (line 1011)
    - `update_relationship_metrics(self, payload: dict[str, object]) -> None` — Allow external callers to seed the latest relationship metrics. (line 1014)
    - `latest_relationship_overlay(self) -> dict[str, list[dict[str, object]]]` — No docstring. (line 1018)
    - `latest_narrations(self) -> list[dict[str, object]]` — Expose narration entries emitted during the latest publish call. (line 1024)
    - `latest_embedding_metrics(self) -> dict[str, float] | None` — Expose embedding allocator counters. (line 1029)
    - `latest_events(self) -> Iterable[dict[str, object]]` — Return the most recent event batch. (line 1035)
    - `latest_narration_state(self) -> dict[str, object]` — Return the narration limiter state for snapshot export. (line 1039)
    - `register_event_subscriber(self, subscriber: Callable[[list[dict[str, object]]], None]) -> None` — Register a callback to receive each tick's event batch. (line 1044)
    - `latest_job_snapshot(self) -> dict[str, dict[str, object]]` — No docstring. (line 1050)
    - `latest_economy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring. (line 1053)
    - `latest_employment_metrics(self) -> dict[str, object]` — No docstring. (line 1056)
    - `schema(self) -> str` — No docstring. (line 1059)
    - `_capture_relationship_snapshot(self, world: WorldState) -> dict[str, dict[str, dict[str, float]]]` — No docstring. (line 1062)
    - `_compute_relationship_updates(self, previous: dict[str, dict[str, dict[str, float]]], current: dict[str, dict[str, dict[str, float]]]) -> list[dict[str, object]]` — No docstring. (line 1087)
    - `_build_relationship_overlay(self) -> dict[str, list[dict[str, object]]]` — No docstring. (line 1166)
    - `_process_narrations(self, events: Iterable[dict[str, object]], tick: int) -> None` — No docstring. (line 1206)
    - `_handle_queue_conflict_narration(self, event: dict[str, object], tick: int) -> None` — No docstring. (line 1222)
    - `_handle_shower_power_outage_narration(self, event: dict[str, object], tick: int) -> None` — No docstring. (line 1270)
    - `_handle_shower_complete_narration(self, event: dict[str, object], tick: int) -> None` — No docstring. (line 1297)
    - `_handle_sleep_complete_narration(self, event: dict[str, object], tick: int) -> None` — No docstring. (line 1327)
    - `_copy_relationship_snapshot(snapshot: dict[str, dict[str, dict[str, float]]]) -> dict[str, dict[str, dict[str, float]]]` — No docstring. (line 1358)
    - `_update_kpi_history(self, world: WorldState) -> None` — No docstring. (line 1373)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agents, applied, buffer, command, config, current, event, events, identity, kpi_history, metrics, observations
- Return payloads: Iterable[dict[str, object]], Iterable[object], None, bool, dict[str, Any], dict[str, dict[str, dict[str, float]]], dict[str, dict[str, float]], dict[str, dict[str, object]], dict[str, float] | None, dict[str, int] | None, dict[str, list[dict[str, object]]], dict[str, list[float]]
- Advances tick or scheduler timelines via TelemetryPublisher.publish_tick
- Audits datasets or configurations via TelemetryPublisher._append_console_audit
- Builds derived structures or observations via TelemetryPublisher._build_relationship_overlay, TelemetryPublisher._build_stream_payload, TelemetryPublisher._build_transport_client
- Captures trajectories or telemetry snapshots via TelemetryPublisher._capture_relationship_snapshot
- Computes metrics or rewards via TelemetryPublisher._compute_relationship_updates
- Exports payloads for downstream consumers via TelemetryPublisher.export_console_buffer, TelemetryPublisher.export_state
- Flushes buffers or queues via TelemetryPublisher._flush_loop, TelemetryPublisher._flush_transport_buffer
- Loads configuration or datasets from disk via TelemetryPublisher._build_stream_payload, TelemetryPublisher._enqueue_stream_payload, TelemetryPublisher._normalize_perturbations_payload
- Publishes telemetry or events via TelemetryPublisher.__init__, TelemetryPublisher._append_console_audit, TelemetryPublisher._build_relationship_overlay, TelemetryPublisher._build_stream_payload, TelemetryPublisher._build_transport_client, TelemetryPublisher._capture_relationship_snapshot, TelemetryPublisher._compute_relationship_updates, TelemetryPublisher._copy_relationship_snapshot, TelemetryPublisher._enqueue_stream_payload, TelemetryPublisher._flush_loop, TelemetryPublisher._flush_transport_buffer, TelemetryPublisher._handle_queue_conflict_narration, TelemetryPublisher._handle_shower_complete_narration, TelemetryPublisher._handle_shower_power_outage_narration, TelemetryPublisher._handle_sleep_complete_narration, TelemetryPublisher._normalize_perturbations_payload, TelemetryPublisher._process_narrations, TelemetryPublisher._reset_transport_client, TelemetryPublisher._send_with_retry, TelemetryPublisher._update_kpi_history, TelemetryPublisher.close, TelemetryPublisher.console_history, TelemetryPublisher.drain_console_buffer, TelemetryPublisher.export_console_buffer, TelemetryPublisher.export_state, TelemetryPublisher.import_console_buffer, TelemetryPublisher.import_state, TelemetryPublisher.kpi_history, TelemetryPublisher.latest_affordance_manifest, TelemetryPublisher.latest_anneal_status, TelemetryPublisher.latest_conflict_snapshot, TelemetryPublisher.latest_console_results, TelemetryPublisher.latest_economy_snapshot, TelemetryPublisher.latest_embedding_metrics, TelemetryPublisher.latest_employment_metrics, TelemetryPublisher.latest_events, TelemetryPublisher.latest_health_status, TelemetryPublisher.latest_job_snapshot, TelemetryPublisher.latest_narration_state, TelemetryPublisher.latest_narrations, TelemetryPublisher.latest_perturbations, TelemetryPublisher.latest_policy_identity, TelemetryPublisher.latest_policy_snapshot, TelemetryPublisher.latest_possessed_agents, TelemetryPublisher.latest_precondition_failures, TelemetryPublisher.latest_promotion_state, TelemetryPublisher.latest_queue_history, TelemetryPublisher.latest_queue_metrics, TelemetryPublisher.latest_relationship_metrics, TelemetryPublisher.latest_relationship_overlay, TelemetryPublisher.latest_relationship_snapshot, TelemetryPublisher.latest_relationship_updates, TelemetryPublisher.latest_reward_breakdown, TelemetryPublisher.latest_rivalry_events, TelemetryPublisher.latest_snapshot_migrations, TelemetryPublisher.latest_stability_alerts, TelemetryPublisher.latest_stability_inputs, TelemetryPublisher.latest_stability_metrics, TelemetryPublisher.latest_transport_status, TelemetryPublisher.publish_tick, TelemetryPublisher.queue_console_command, TelemetryPublisher.record_console_results, TelemetryPublisher.record_health_metrics, TelemetryPublisher.record_possessed_agents, TelemetryPublisher.record_snapshot_migrations, TelemetryPublisher.record_stability_metrics, TelemetryPublisher.register_event_subscriber, TelemetryPublisher.schema, TelemetryPublisher.stop_worker, TelemetryPublisher.update_anneal_status, TelemetryPublisher.update_policy_identity, TelemetryPublisher.update_relationship_metrics
- Records metrics or histories via TelemetryPublisher.record_console_results, TelemetryPublisher.record_health_metrics, TelemetryPublisher.record_possessed_agents, TelemetryPublisher.record_snapshot_migrations, TelemetryPublisher.record_stability_metrics
- Registers handlers or callbacks via TelemetryPublisher.register_event_subscriber
- Resets runtime state via TelemetryPublisher._reset_transport_client
- Updates internal caches or trackers via TelemetryPublisher._compute_relationship_updates, TelemetryPublisher._update_kpi_history, TelemetryPublisher.latest_relationship_updates, TelemetryPublisher.update_anneal_status, TelemetryPublisher.update_policy_identity, TelemetryPublisher.update_relationship_metrics

### Integration Points
- External: None
- Internal: townlet.config.SimulationConfig, townlet.console.command.ConsoleCommandResult, townlet.telemetry.narration.NarrationRateLimiter, townlet.telemetry.transport.TelemetryTransportError, townlet.telemetry.transport.TransportBuffer, townlet.telemetry.transport.create_transport, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: TelemetryPublisher.__init__, TelemetryPublisher._append_console_audit, TelemetryPublisher._build_relationship_overlay, TelemetryPublisher._build_stream_payload, TelemetryPublisher._build_transport_client, TelemetryPublisher._capture_relationship_snapshot, TelemetryPublisher._compute_relationship_updates, TelemetryPublisher._copy_relationship_snapshot, TelemetryPublisher._enqueue_stream_payload, TelemetryPublisher._flush_loop, TelemetryPublisher._flush_transport_buffer, TelemetryPublisher._handle_queue_conflict_narration, TelemetryPublisher._handle_shower_complete_narration, TelemetryPublisher._handle_shower_power_outage_narration, TelemetryPublisher._handle_sleep_complete_narration, TelemetryPublisher._normalize_perturbations_payload, TelemetryPublisher._process_narrations, TelemetryPublisher._reset_transport_client, TelemetryPublisher._send_with_retry, TelemetryPublisher._update_kpi_history
- ... 39 additional methods without docstrings
- Module exceeds 800 lines; consider refactoring into smaller components.

## `src/townlet/telemetry/relationship_metrics.py`

**Purpose**: Helpers for tracking relationship churn and eviction telemetry.
**Lines of code**: 182
**Dependencies**: stdlib=__future__.annotations, collections.Counter, collections.abc.Iterable, collections.deque, dataclasses.dataclass; external=None; internal=None
**Related modules**: None

### Classes
- `RelationshipEvictionSample` (bases: object; decorators: dataclass) — Aggregated eviction counts captured for a completed window. (line 32)
  - Attributes:
    - name=`window_start`, type=`int` (line 35)
    - name=`window_end`, type=`int` (line 36)
    - name=`total_evictions`, type=`int` (line 37)
    - name=`per_owner`, type=`dict[str, int]` (line 38)
    - name=`per_reason`, type=`dict[str, int]` (line 39)
  - Methods:
    - `to_payload(self) -> dict[str, object]` — Serialise the sample into a telemetry-friendly payload. (line 41)
- `RelationshipChurnAccumulator` (bases: object; decorators: None) — Tracks relationship eviction activity over fixed tick windows. (line 52)
  - Methods:
    - `__init__(self, *, window_ticks: int, max_samples: int = 8) -> None` — No docstring. (line 55)
    - `record_eviction(self, *, tick: int, owner_id: str, evicted_id: str, reason: str | None = None) -> None` — Record an eviction event for churn tracking. (line 72)
    - `_roll_window(self, tick: int) -> None` — No docstring. (line 104)
    - `snapshot(self) -> dict[str, object]` — Return aggregates for the active window. (line 126)
    - `history(self) -> Iterable[RelationshipEvictionSample]` — Return a snapshot of the recorded history. (line 136)
    - `history_payload(self) -> list[dict[str, object]]` — Convert history samples into telemetry payloads. (line 140)
    - `latest_payload(self) -> dict[str, object]` — Return the live window payload for telemetry publishing. (line 144)
    - `ingest_payload(self, payload: dict[str, object]) -> None` — Restore the accumulator from an external payload. (line 150)

### Functions
- `_advance_window(*, current_tick: int, window_ticks: int, window_start: int) -> int` — Move the window start forward until it covers ``current_tick``. (line 15)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: current_tick, evicted_id, max_samples, owner_id, payload, reason, tick, window_start, window_ticks
- Return payloads: Iterable[RelationshipEvictionSample], None, dict[str, object], int, list[dict[str, object]]
- Ingests external commands or payloads via RelationshipChurnAccumulator.ingest_payload
- Loads configuration or datasets from disk via RelationshipChurnAccumulator.history_payload, RelationshipChurnAccumulator.ingest_payload, RelationshipChurnAccumulator.latest_payload, RelationshipEvictionSample.to_payload
- Records metrics or histories via RelationshipChurnAccumulator.record_eviction

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: RelationshipChurnAccumulator.__init__, RelationshipChurnAccumulator._roll_window

## `src/townlet/telemetry/transport.py`

**Purpose**: Transport primitives for telemetry publishing.
**Lines of code**: 186
**Dependencies**: stdlib=__future__.annotations, collections.deque, pathlib.Path, socket, sys, typing.Protocol; external=None; internal=None
**Related modules**: None

### Classes
- `TelemetryTransportError` (bases: RuntimeError; decorators: None) — Raised when telemetry messages cannot be delivered. (line 12)
- `TransportClient` (bases: Protocol; decorators: None) — Common interface for transport implementations. (line 16)
  - Methods:
    - `send(self, payload: bytes) -> None` — No docstring. (line 19)
    - `close(self) -> None` — No docstring. (line 22)
- `StdoutTransport` (bases: object; decorators: None) — Writes telemetry payloads to stdout (for development/debug). (line 26)
  - Methods:
    - `__init__(self) -> None` — No docstring. (line 29)
    - `send(self, payload: bytes) -> None` — No docstring. (line 32)
    - `close(self) -> None` — No docstring. (line 36)
- `FileTransport` (bases: object; decorators: None) — Appends newline-delimited payloads to a local file. (line 40)
  - Methods:
    - `__init__(self, path: Path) -> None` — No docstring. (line 43)
    - `send(self, payload: bytes) -> None` — No docstring. (line 48)
    - `close(self) -> None` — No docstring. (line 52)
- `TcpTransport` (bases: object; decorators: None) — Sends telemetry payloads to a TCP endpoint. (line 56)
  - Methods:
    - `__init__(self, endpoint: str, *, connect_timeout: float, send_timeout: float) -> None` — No docstring. (line 59)
    - `_connect(self) -> None` — No docstring. (line 83)
    - `send(self, payload: bytes) -> None` — No docstring. (line 96)
    - `close(self) -> None` — No docstring. (line 105)
- `TransportBuffer` (bases: object; decorators: None) — Accumulates payloads prior to flushing to the transport. (line 113)
  - Methods:
    - `__init__(self, *, max_batch_size: int, max_buffer_bytes: int) -> None` — No docstring. (line 116)
    - `append(self, payload: bytes) -> None` — No docstring. (line 122)
    - `popleft(self) -> bytes` — No docstring. (line 126)
    - `clear(self) -> None` — No docstring. (line 131)
    - `__len__(self) -> int` — No docstring. (line 135)
    - `total_bytes(self) -> int` — No docstring. (line 139)
    - `is_over_capacity(self) -> bool` — No docstring. (line 142)
    - `drop_until_within_capacity(self) -> int` — Drop oldest payloads until buffer fits limits; returns drop count. (line 145)

### Functions
- `create_transport(*, transport_type: str, file_path: Path | None, endpoint: str | None, connect_timeout: float, send_timeout: float) -> TransportClient` — Factory helper for `TelemetryPublisher`. (line 156)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: connect_timeout, endpoint, file_path, max_batch_size, max_buffer_bytes, path, payload, send_timeout, transport_type
- Return payloads: None, TransportClient, bool, bytes, int
- Establishes IO connections or sockets via TcpTransport._connect

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: FileTransport.__init__, FileTransport.close, FileTransport.send, StdoutTransport.__init__, StdoutTransport.close, StdoutTransport.send, TcpTransport.__init__, TcpTransport._connect, TcpTransport.close, TcpTransport.send, TransportBuffer.__init__, TransportBuffer.__len__, TransportBuffer.append, TransportBuffer.clear, TransportBuffer.is_over_capacity, TransportBuffer.popleft, TransportBuffer.total_bytes, TransportClient.close, TransportClient.send

## `src/townlet/utils/__init__.py`

**Purpose**: Utility helpers for Townlet.
**Lines of code**: 9
**Dependencies**: stdlib=None; external=rng.decode_rng_state, rng.encode_rng, rng.encode_rng_state; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: rng.decode_rng_state, rng.encode_rng, rng.encode_rng_state
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/utils/rng.py`

**Purpose**: Utility helpers for serialising deterministic RNG state.
**Lines of code**: 25
**Dependencies**: stdlib=__future__.annotations, base64, pickle, random; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `encode_rng_state(state: tuple[object, ...]) -> str` — Encode a Python ``random`` state tuple into a base64 string. (line 10)
- `decode_rng_state(payload: str) -> tuple[object, ...]` — Decode a base64-encoded RNG state back into a Python tuple. (line 16)
- `encode_rng(rng: random.Random) -> str` — Capture the current state of ``rng`` as a serialisable string. (line 22)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: payload, rng, state
- Return payloads: str, tuple[object, ...]
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/world/__init__.py`

**Purpose**: World modelling primitives.
**Lines of code**: 16
**Dependencies**: stdlib=__future__.annotations; external=grid.AgentSnapshot, grid.WorldState, queue_manager.QueueManager, relationships.RelationshipLedger, relationships.RelationshipParameters, relationships.RelationshipTie; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: grid.AgentSnapshot, grid.WorldState, queue_manager.QueueManager, relationships.RelationshipLedger, relationships.RelationshipParameters, relationships.RelationshipTie
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/world/grid.py`

**Purpose**: Grid world representation and affordance integration.
**Lines of code**: 2701
**Dependencies**: stdlib=__future__.annotations, collections.OrderedDict, collections.abc.Iterable, collections.abc.Mapping, collections.deque, copy, dataclasses.dataclass, dataclasses.field, logging, os, pathlib.Path, random, typing.Any, typing.Callable, typing.Optional; external=None; internal=townlet.agents.models.Personality, townlet.agents.relationship_modifiers.RelationshipDelta, townlet.agents.relationship_modifiers.RelationshipEvent, townlet.agents.relationship_modifiers.apply_personality_modifiers, townlet.config.EmploymentConfig, townlet.config.SimulationConfig, townlet.config.affordance_manifest.AffordanceManifestError, townlet.config.affordance_manifest.load_affordance_manifest, townlet.console.command.ConsoleCommandEnvelope, townlet.console.command.ConsoleCommandError, townlet.console.command.ConsoleCommandResult, townlet.observations.embedding.EmbeddingAllocator, townlet.telemetry.relationship_metrics.RelationshipChurnAccumulator, townlet.world.hooks.load_modules, townlet.world.preconditions.CompiledPrecondition, townlet.world.preconditions.PreconditionSyntaxError, townlet.world.preconditions.compile_preconditions, townlet.world.preconditions.evaluate_preconditions, townlet.world.queue_manager.QueueManager, townlet.world.relationships.RelationshipLedger, townlet.world.relationships.RelationshipParameters, townlet.world.rivalry.RivalryLedger, townlet.world.rivalry.RivalryParameters
**Related modules**: townlet.agents.models.Personality, townlet.agents.relationship_modifiers.RelationshipDelta, townlet.agents.relationship_modifiers.RelationshipEvent, townlet.agents.relationship_modifiers.apply_personality_modifiers, townlet.config.EmploymentConfig, townlet.config.SimulationConfig, townlet.config.affordance_manifest.AffordanceManifestError, townlet.config.affordance_manifest.load_affordance_manifest, townlet.console.command.ConsoleCommandEnvelope, townlet.console.command.ConsoleCommandError, townlet.console.command.ConsoleCommandResult, townlet.observations.embedding.EmbeddingAllocator, townlet.telemetry.relationship_metrics.RelationshipChurnAccumulator, townlet.world.hooks.load_modules, townlet.world.preconditions.CompiledPrecondition, townlet.world.preconditions.PreconditionSyntaxError, townlet.world.preconditions.compile_preconditions, townlet.world.preconditions.evaluate_preconditions, townlet.world.queue_manager.QueueManager, townlet.world.relationships.RelationshipLedger, townlet.world.relationships.RelationshipParameters, townlet.world.rivalry.RivalryLedger, townlet.world.rivalry.RivalryParameters

### Classes
- `HookRegistry` (bases: object; decorators: None) — Registers named affordance hooks and returns handlers on demand. (line 51)
  - Methods:
    - `__init__(self) -> None` — No docstring. (line 54)
    - `register(self, name: str, handler: Callable[[dict[str, Any]], None]) -> None` — No docstring. (line 57)
    - `handlers_for(self, name: str) -> tuple[Callable[[dict[str, Any]], None], ...]` — No docstring. (line 64)
    - `clear(self, name: str | None = None) -> None` — No docstring. (line 67)
- `_ConsoleHandlerEntry` (bases: object; decorators: None) — Metadata for registered console handlers. (line 74)
  - Attributes:
    - name=`__slots__`, default=`('handler', 'mode', 'require_cmd_id')` (line 77)
  - Methods:
    - `__init__(self, handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult], *, mode: str = 'viewer', require_cmd_id: bool = False) -> None` — No docstring. (line 79)
- `AgentSnapshot` (bases: object; decorators: dataclass) — Minimal agent view used for scaffolding. (line 101)
  - Attributes:
    - name=`agent_id`, type=`str` (line 104)
    - name=`position`, type=`tuple[int, int]` (line 105)
    - name=`needs`, type=`dict[str, float]` (line 106)
    - name=`wallet`, type=`float`, default=`0.0` (line 107)
    - name=`home_position`, type=`tuple[int, int] | None`, default=`None` (line 108)
    - name=`origin_agent_id`, type=`str | None`, default=`None` (line 109)
    - name=`personality`, type=`Personality`, default=`field(default_factory=_default_personality)` (line 110)
    - name=`inventory`, type=`dict[str, int]`, default=`field(default_factory=dict)` (line 111)
    - name=`job_id`, type=`str | None`, default=`None` (line 112)
    - name=`on_shift`, type=`bool`, default=`False` (line 113)
    - name=`lateness_counter`, type=`int`, default=`0` (line 114)
    - name=`last_late_tick`, type=`int`, default=`-1` (line 115)
    - name=`shift_state`, type=`str`, default=`'pre_shift'` (line 116)
    - name=`late_ticks_today`, type=`int`, default=`0` (line 117)
    - name=`attendance_ratio`, type=`float`, default=`0.0` (line 118)
    - name=`absent_shifts_7d`, type=`int`, default=`0` (line 119)
    - name=`wages_withheld`, type=`float`, default=`0.0` (line 120)
    - name=`exit_pending`, type=`bool`, default=`False` (line 121)
    - name=`last_action_id`, type=`str`, default=`''` (line 122)
    - name=`last_action_success`, type=`bool`, default=`False` (line 123)
    - name=`last_action_duration`, type=`int`, default=`0` (line 124)
    - name=`episode_tick`, type=`int`, default=`0` (line 125)
  - Methods:
    - `__post_init__(self) -> None` — No docstring. (line 127)
- `InteractiveObject` (bases: object; decorators: dataclass) — Represents an interactive world object with optional occupancy. (line 146)
  - Attributes:
    - name=`object_id`, type=`str` (line 149)
    - name=`object_type`, type=`str` (line 150)
    - name=`occupied_by`, type=`str | None`, default=`None` (line 151)
    - name=`stock`, type=`dict[str, int]`, default=`field(default_factory=dict)` (line 152)
    - name=`position`, type=`tuple[int, int] | None`, default=`None` (line 153)
- `RunningAffordance` (bases: object; decorators: dataclass) — Tracks an affordance currently executing on an object. (line 157)
  - Attributes:
    - name=`agent_id`, type=`str` (line 160)
    - name=`affordance_id`, type=`str` (line 161)
    - name=`duration_remaining`, type=`int` (line 162)
    - name=`effects`, type=`dict[str, float]` (line 163)
- `AffordanceSpec` (bases: object; decorators: dataclass) — Static affordance definition loaded from configuration. (line 167)
  - Attributes:
    - name=`affordance_id`, type=`str` (line 170)
    - name=`object_type`, type=`str` (line 171)
    - name=`duration`, type=`int` (line 172)
    - name=`effects`, type=`dict[str, float]` (line 173)
    - name=`preconditions`, type=`list[str]`, default=`field(default_factory=list)` (line 174)
    - name=`hooks`, type=`dict[str, list[str]]`, default=`field(default_factory=dict)` (line 175)
    - name=`compiled_preconditions`, type=`tuple[CompiledPrecondition, ...]`, default=`field(default_factory=tuple, repr=False)` (line 176)
- `WorldState` (bases: object; decorators: dataclass) — Holds mutable world state for the simulation tick. (line 183)
  - Attributes:
    - name=`config`, type=`SimulationConfig` (line 186)
    - name=`agents`, type=`dict[str, AgentSnapshot]`, default=`field(default_factory=dict)` (line 187)
    - name=`tick`, type=`int`, default=`0` (line 188)
    - name=`queue_manager`, type=`QueueManager`, default=`field(init=False)` (line 189)
    - name=`embedding_allocator`, type=`EmbeddingAllocator`, default=`field(init=False)` (line 190)
    - name=`_active_reservations`, type=`dict[str, str]`, default=`field(init=False, default_factory=dict)` (line 191)
    - name=`objects`, type=`dict[str, InteractiveObject]`, default=`field(init=False, default_factory=dict)` (line 192)
    - name=`affordances`, type=`dict[str, AffordanceSpec]`, default=`field(init=False, default_factory=dict)` (line 193)
    - name=`_running_affordances`, type=`dict[str, RunningAffordance]`, default=`field(init=False, default_factory=dict)` (line 194)
    - name=`_pending_events`, type=`dict[int, list[dict[str, Any]]]`, default=`field(init=False, default_factory=dict)` (line 195)
    - name=`store_stock`, type=`dict[str, dict[str, int]]`, default=`field(init=False, default_factory=dict)` (line 196)
    - name=`_job_keys`, type=`list[str]`, default=`field(init=False, default_factory=list)` (line 197)
    - name=`_employment_state`, type=`dict[str, dict[str, Any]]`, default=`field(init=False, default_factory=dict)` (line 198)
    - name=`_employment_exit_queue`, type=`list[str]`, default=`field(init=False, default_factory=list)` (line 199)
    - name=`_employment_exits_today`, type=`int`, default=`field(init=False, default=0)` (line 200)
    - name=`_employment_exit_queue_timestamps`, type=`dict[str, int]`, default=`field(init=False, default_factory=dict)` (line 201)
    - name=`_employment_manual_exits`, type=`set[str]`, default=`field(init=False, default_factory=set)` (line 202)
    - name=`_rivalry_ledgers`, type=`dict[str, RivalryLedger]`, default=`field(init=False, default_factory=dict)` (line 204)
    - name=`_relationship_ledgers`, type=`dict[str, RelationshipLedger]`, default=`field(init=False, default_factory=dict)` (line 205)
    - name=`_relationship_churn`, type=`RelationshipChurnAccumulator`, default=`field(init=False)` (line 206)
    - name=`_rivalry_events`, type=`deque[dict[str, Any]]`, default=`field(init=False, default_factory=deque)` (line 207)
    - name=`_relationship_window_ticks`, type=`int`, default=`600` (line 208)
    - name=`_recent_meal_participants`, type=`dict[str, dict[str, Any]]`, default=`field(init=False, default_factory=dict)` (line 209)
    - name=`_chat_events`, type=`list[dict[str, Any]]`, default=`field(init=False, default_factory=list)` (line 210)
    - name=`_rng_seed`, type=`Optional[int]`, default=`field(init=False, default=None)` (line 211)
    - name=`_rng_state`, type=`Optional[tuple[Any, ...]]`, default=`field(init=False, default=None)` (line 212)
    - name=`_rng`, type=`Optional[random.Random]`, default=`field(init=False, default=None, repr=False)` (line 213)
    - name=`_affordance_manifest_info`, type=`dict[str, object]`, default=`field(init=False, default_factory=dict)` (line 214)
    - name=`_objects_by_position`, type=`dict[tuple[int, int], list[str]]`, default=`field(init=False, default_factory=dict)` (line 215)
    - name=`_console_handlers`, type=`dict[str, _ConsoleHandlerEntry]`, default=`field(init=False, default_factory=dict)` (line 216)
    - name=`_console_cmd_history`, type=`OrderedDict[str, ConsoleCommandResult]`, default=`field(init=False, default_factory=OrderedDict)` (line 217)
    - name=`_console_result_buffer`, type=`deque[ConsoleCommandResult]`, default=`field(init=False, default_factory=deque)` (line 220)
    - name=`_hook_registry`, type=`HookRegistry`, default=`field(init=False, repr=False)` (line 221)
    - name=`_ctx_reset_requests`, type=`set[str]`, default=`field(init=False, default_factory=set)` (line 222)
    - name=`_respawn_counters`, type=`dict[str, int]`, default=`field(init=False, default_factory=dict)` (line 223)
  - Methods:
    - `from_config(cls, config: SimulationConfig, *, rng: Optional[random.Random] = None) -> 'WorldState'` — Bootstrap the initial world from config. (line 226)
    - `__post_init__(self) -> None` — No docstring. (line 238)
    - `generate_agent_id(self, base_id: str) -> str` — No docstring. (line 279)
    - `apply_console(self, operations: Iterable[Any]) -> None` — Apply console operations before the tick sequence runs. (line 289)
    - `attach_rng(self, rng: random.Random) -> None` — Attach a deterministic RNG used for world-level randomness. (line 382)
    - `rng(self) -> random.Random` — No docstring. (line 389)
    - `get_rng_state(self) -> tuple[Any, ...]` — No docstring. (line 394)
    - `set_rng_state(self, state: tuple[Any, ...]) -> None` — No docstring. (line 397)
    - `register_console_handler(self, name: str, handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult], *, mode: str = 'viewer', require_cmd_id: bool = False) -> None` — Register a console handler for queued commands. (line 405)
    - `register_affordance_hook(self, name: str, handler: Callable[[dict[str, Any]], None]) -> None` — Register a callable invoked when a manifest hook fires. (line 419)
    - `clear_affordance_hooks(self, name: str | None = None) -> None` — Clear registered affordance hooks (used primarily for tests). (line 426)
    - `consume_console_results(self) -> list[ConsoleCommandResult]` — Return and clear buffered console results. (line 431)
    - `_record_console_result(self, result: ConsoleCommandResult) -> None` — No docstring. (line 438)
    - `_dispatch_affordance_hooks(self, stage: str, hook_names: Iterable[str], *, agent_id: str, object_id: str, spec: AffordanceSpec | None, extra: Mapping[str, Any] | None = None) -> bool` — No docstring. (line 445)
    - `_build_precondition_context(self, *, agent_id: str, object_id: str, spec: AffordanceSpec) -> dict[str, Any]` — No docstring. (line 486)
    - `_snapshot_precondition_context(self, context: Mapping[str, Any]) -> dict[str, Any]` — No docstring. (line 565)
    - `_register_default_console_handlers(self) -> None` — No docstring. (line 577)
    - `_console_noop_handler(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring. (line 630)
    - `_console_employment_status(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring. (line 633)
    - `_console_employment_exit(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring. (line 641)
    - `_assign_job_if_missing(self, snapshot: AgentSnapshot) -> None` — No docstring. (line 670)
    - `remove_agent(self, agent_id: str, tick: int) -> dict[str, Any] | None` — No docstring. (line 674)
    - `respawn_agent(self, blueprint: Mapping[str, Any]) -> None` — No docstring. (line 730)
    - `_sync_agent_spawn(self, snapshot: AgentSnapshot) -> None` — No docstring. (line 788)
    - `_console_spawn_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring. (line 796)
    - `_console_teleport_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring. (line 871)
    - `_release_queue_membership(self, agent_id: str) -> None` — No docstring. (line 906)
    - `_sync_reservation_for_agent(self, agent_id: str) -> None` — No docstring. (line 912)
    - `_is_position_walkable(self, position: tuple[int, int]) -> bool` — No docstring. (line 917)
    - `kill_agent(self, agent_id: str, *, reason: str | None = None) -> bool` — No docstring. (line 924)
    - `_console_set_need(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring. (line 947)
    - `_console_set_price(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring. (line 989)
    - `_console_force_chat(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring. (line 1011)
    - `_console_set_relationship(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring. (line 1053)
    - `register_object(self, *, object_id: str, object_type: str, position: tuple[int, int] | None = None) -> None` — Register or update an interactive object in the world. (line 1139)
    - `_index_object_position(self, object_id: str, position: tuple[int, int]) -> None` — No docstring. (line 1171)
    - `_unindex_object_position(self, object_id: str, position: tuple[int, int]) -> None` — No docstring. (line 1176)
    - `register_affordance(self, *, affordance_id: str, object_type: str, duration: int, effects: dict[str, float], preconditions: Iterable[str] | None = None, hooks: Mapping[str, Iterable[str]] | None = None) -> None` — Register an affordance available in the world. (line 1187)
    - `apply_actions(self, actions: dict[str, Any]) -> None` — Apply agent actions for the current tick. (line 1216)
    - `resolve_affordances(self, current_tick: int) -> None` — Resolve queued affordances and hooks. (line 1304)
    - `request_ctx_reset(self, agent_id: str) -> None` — Mark an agent so the next observation toggles ctx_reset_flag. (line 1369)
    - `consume_ctx_reset_requests(self) -> set[str]` — Return and clear pending ctx-reset requests. (line 1374)
    - `snapshot(self) -> dict[str, AgentSnapshot]` — Return a shallow copy of the agent dictionary for observers. (line 1380)
    - `local_view(self, agent_id: str, radius: int, *, include_agents: bool = True, include_objects: bool = True) -> dict[str, Any]` — Return local neighborhood information for observation builders. (line 1384)
    - `agent_context(self, agent_id: str) -> dict[str, object]` — Return scalar context fields for the requested agent. (line 1483)
    - `active_reservations(self) -> dict[str, str]` — Expose a copy of active reservations for diagnostics/tests. (line 1505)
    - `drain_events(self) -> list[dict[str, Any]]` — Return all pending events accumulated up to the current tick. (line 1509)
    - `_record_queue_conflict(self, *, object_id: str, actor: str, rival: str, reason: str, queue_length: int, intensity: float | None = None) -> None` — No docstring. (line 1517)
    - `register_rivalry_conflict(self, agent_a: str, agent_b: str, *, intensity: float = 1.0, reason: str = 'conflict') -> None` — Record a rivalry-inducing conflict between two agents. (line 1569)
    - `rivalry_snapshot(self) -> dict[str, dict[str, float]]` — Expose rivalry ledgers for telemetry/diagnostics. (line 1598)
    - `relationships_snapshot(self) -> dict[str, dict[str, dict[str, float]]]` — No docstring. (line 1607)
    - `relationship_tie(self, agent_id: str, other_id: str) -> RelationshipTie | None` — Return the current relationship tie between two agents, if any. (line 1615)
    - `consume_chat_events(self) -> list[dict[str, Any]]` — Return chat events staged for reward calculations and clear the buffer. (line 1623)
    - `rivalry_value(self, agent_id: str, other_id: str) -> float` — Return the rivalry score between two agents, if present. (line 1630)
    - `rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool` — No docstring. (line 1637)
    - `rivalry_top(self, agent_id: str, limit: int) -> list[tuple[str, float]]` — No docstring. (line 1643)
    - `consume_rivalry_events(self) -> list[dict[str, Any]]` — Return rivalry events recorded since the last call. (line 1649)
    - `_record_rivalry_event(self, *, agent_a: str, agent_b: str, intensity: float, reason: str) -> None` — No docstring. (line 1658)
    - `_get_rivalry_ledger(self, agent_id: str) -> RivalryLedger` — No docstring. (line 1671)
    - `_get_relationship_ledger(self, agent_id: str) -> RelationshipLedger` — No docstring. (line 1684)
    - `_relationship_parameters(self) -> RelationshipParameters` — No docstring. (line 1700)
    - `_personality_for(self, agent_id: str) -> Personality` — No docstring. (line 1703)
    - `_apply_relationship_delta(self, owner_id: str, other_id: str, *, delta: RelationshipDelta, event: RelationshipEvent) -> None` — No docstring. (line 1709)
    - `_rivalry_parameters(self) -> RivalryParameters` — No docstring. (line 1731)
    - `_decay_rivalry_ledgers(self) -> None` — No docstring. (line 1743)
    - `_decay_relationship_ledgers(self) -> None` — No docstring. (line 1755)
    - `_record_relationship_eviction(self, owner_id: str, other_id: str, reason: str) -> None` — No docstring. (line 1766)
    - `relationship_metrics_snapshot(self) -> dict[str, object]` — No docstring. (line 1774)
    - `load_relationship_snapshot(self, snapshot: dict[str, dict[str, dict[str, float]]]) -> None` — Restore relationship ledgers from persisted snapshot data. (line 1777)
    - `update_relationship(self, agent_a: str, agent_b: str, *, trust: float = 0.0, familiarity: float = 0.0, rivalry: float = 0.0, event: RelationshipEvent = 'generic') -> None` — No docstring. (line 1796)
    - `record_chat_success(self, speaker: str, listener: str, quality: float) -> None` — No docstring. (line 1812)
    - `record_chat_failure(self, speaker: str, listener: str) -> None` — No docstring. (line 1839)
    - `_sync_reservation(self, object_id: str) -> None` — No docstring. (line 1867)
    - `_handle_blocked(self, object_id: str, tick: int) -> None` — No docstring. (line 1879)
    - `_start_affordance(self, agent_id: str, object_id: str, affordance_id: str) -> bool` — No docstring. (line 1898)
    - `_apply_affordance_effects(self, agent_id: str, effects: dict[str, float]) -> None` — No docstring. (line 1994)
    - `_emit_event(self, event: str, payload: dict[str, Any]) -> None` — No docstring. (line 2005)
    - `_load_affordance_definitions(self) -> None` — No docstring. (line 2009)
    - `affordance_manifest_metadata(self) -> dict[str, object]` — Expose manifest metadata (path, checksum, counts) for telemetry. (line 2054)
    - `find_nearest_object_of_type(self, object_type: str, origin: tuple[int, int]) -> tuple[int, int] | None` — No docstring. (line 2059)
    - `_apply_need_decay(self) -> None` — No docstring. (line 2073)
    - `apply_nightly_reset(self) -> list[str]` — Return agents home, refresh needs, and reset employment flags. (line 2083)
    - `_assign_jobs_to_agents(self) -> None` — No docstring. (line 2150)
    - `_apply_job_state(self) -> None` — No docstring. (line 2160)
    - `_apply_job_state_legacy(self) -> None` — No docstring. (line 2166)
    - `_apply_job_state_enforced(self) -> None` — No docstring. (line 2210)
    - `_employment_context_defaults(self) -> dict[str, Any]` — No docstring. (line 2294)
    - `_get_employment_context(self, agent_id: str) -> dict[str, Any]` — No docstring. (line 2320)
    - `_employment_context_wages(self, agent_id: str) -> float` — No docstring. (line 2333)
    - `_employment_context_punctuality(self, agent_id: str) -> float` — No docstring. (line 2339)
    - `_employment_idle_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None` — No docstring. (line 2348)
    - `_employment_prepare_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None` — No docstring. (line 2368)
    - `_employment_begin_shift(self, ctx: dict[str, Any], start: int, end: int) -> None` — No docstring. (line 2373)
    - `_employment_determine_state(self, *, ctx: dict[str, Any], tick: int, start: int, at_required_location: bool, employment_cfg: EmploymentConfig) -> str` — No docstring. (line 2393)
    - `_employment_apply_state_effects(self, *, snapshot: AgentSnapshot, ctx: dict[str, Any], state: str, at_required_location: bool, wage_rate: float, lateness_penalty: float, employment_cfg: EmploymentConfig) -> None` — No docstring. (line 2427)
    - `_employment_finalize_shift(self, *, snapshot: AgentSnapshot, ctx: dict[str, Any], employment_cfg: EmploymentConfig, job_id: str | None) -> None` — No docstring. (line 2552)
    - `_employment_coworkers_on_shift(self, snapshot: AgentSnapshot) -> list[str]` — No docstring. (line 2589)
    - `_employment_enqueue_exit(self, agent_id: str, tick: int) -> None` — No docstring. (line 2602)
    - `_employment_remove_from_queue(self, agent_id: str) -> None` — No docstring. (line 2628)
    - `employment_queue_snapshot(self) -> dict[str, Any]` — No docstring. (line 2636)
    - `employment_request_manual_exit(self, agent_id: str, tick: int) -> bool` — No docstring. (line 2646)
    - `employment_defer_exit(self, agent_id: str) -> bool` — No docstring. (line 2659)
    - `_update_basket_metrics(self) -> None` — No docstring. (line 2673)
    - `_restock_economy(self) -> None` — No docstring. (line 2684)

### Functions
- `_default_personality() -> Personality` — Provide a neutral personality for agents lacking explicit traits. (line 91)

### Constants and Configuration
- `_CONSOLE_HISTORY_LIMIT` = 512 (line 47)
- `_CONSOLE_RESULT_BUFFER_LIMIT` = 256 (line 48)
- `_BASE_NEEDS`: `tuple[str, ...]` = ('hunger', 'hygiene', 'energy') (line 97)

### Data Flow
- Primary inputs: actions, actor, affordance_id, agent_a, agent_b, agent_id, at_required_location, base_id, blueprint, config, context, ctx
- Return payloads: 'WorldState', ConsoleCommandResult, None, Personality, RelationshipLedger, RelationshipParameters, RelationshipTie | None, RivalryLedger, RivalryParameters, bool, dict[str, AgentSnapshot], dict[str, Any]
- Applies world or agent state updates via WorldState._apply_affordance_effects, WorldState._apply_job_state, WorldState._apply_job_state_enforced, WorldState._apply_job_state_legacy, WorldState._apply_need_decay, WorldState._apply_relationship_delta, WorldState._employment_apply_state_effects, WorldState.apply_actions, WorldState.apply_console, WorldState.apply_nightly_reset
- Builds derived structures or observations via WorldState._build_precondition_context
- Loads configuration or datasets from disk via WorldState._load_affordance_definitions, WorldState.load_relationship_snapshot
- Records metrics or histories via WorldState._record_console_result, WorldState._record_queue_conflict, WorldState._record_relationship_eviction, WorldState._record_rivalry_event, WorldState.record_chat_failure, WorldState.record_chat_success
- Registers handlers or callbacks via HookRegistry.register, WorldState._register_default_console_handlers, WorldState.register_affordance, WorldState.register_affordance_hook, WorldState.register_console_handler, WorldState.register_object, WorldState.register_rivalry_conflict
- Resets runtime state via WorldState.apply_nightly_reset, WorldState.consume_ctx_reset_requests, WorldState.request_ctx_reset
- Updates internal caches or trackers via WorldState._update_basket_metrics, WorldState.update_relationship

### Integration Points
- External: None
- Internal: townlet.agents.models.Personality, townlet.agents.relationship_modifiers.RelationshipDelta, townlet.agents.relationship_modifiers.RelationshipEvent, townlet.agents.relationship_modifiers.apply_personality_modifiers, townlet.config.EmploymentConfig, townlet.config.SimulationConfig, townlet.config.affordance_manifest.AffordanceManifestError, townlet.config.affordance_manifest.load_affordance_manifest, townlet.console.command.ConsoleCommandEnvelope, townlet.console.command.ConsoleCommandError, townlet.console.command.ConsoleCommandResult, townlet.observations.embedding.EmbeddingAllocator, townlet.telemetry.relationship_metrics.RelationshipChurnAccumulator, townlet.world.hooks.load_modules, townlet.world.preconditions.CompiledPrecondition, townlet.world.preconditions.PreconditionSyntaxError, townlet.world.preconditions.compile_preconditions, townlet.world.preconditions.evaluate_preconditions, townlet.world.queue_manager.QueueManager, townlet.world.relationships.RelationshipLedger, townlet.world.relationships.RelationshipParameters, townlet.world.rivalry.RivalryLedger, townlet.world.rivalry.RivalryParameters

### Code Quality Notes
- Missing docstrings: AgentSnapshot.__post_init__, HookRegistry.__init__, HookRegistry.clear, HookRegistry.handlers_for, HookRegistry.register, WorldState.__post_init__, WorldState._apply_affordance_effects, WorldState._apply_job_state, WorldState._apply_job_state_enforced, WorldState._apply_job_state_legacy, WorldState._apply_need_decay, WorldState._apply_relationship_delta, WorldState._assign_job_if_missing, WorldState._assign_jobs_to_agents, WorldState._build_precondition_context, WorldState._console_employment_exit, WorldState._console_employment_status, WorldState._console_force_chat, WorldState._console_noop_handler, WorldState._console_set_need
- ... 63 additional methods without docstrings
- Module exceeds 800 lines; consider refactoring into smaller components.

## `src/townlet/world/hooks/__init__.py`

**Purpose**: Affordance hook plug-in namespace.
**Lines of code**: 20
**Dependencies**: stdlib=__future__.annotations, importlib.import_module, typing.Iterable, typing.TYPE_CHECKING; external=None; internal=townlet.world.grid.WorldState
**Related modules**: townlet.world.grid.WorldState

### Classes
- None

### Functions
- `load_modules(world: 'WorldState', module_paths: Iterable[str]) -> None` — Import hook modules and let them register against the given world. (line 11)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: module_paths, world
- Return payloads: None
- Loads configuration or datasets from disk via load_modules

### Integration Points
- External: None
- Internal: townlet.world.grid.WorldState

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet/world/hooks/default.py`

**Purpose**: Built-in affordance hook handlers.
**Lines of code**: 313
**Dependencies**: stdlib=__future__.annotations, typing.Any, typing.TYPE_CHECKING; external=None; internal=townlet.world.grid.WorldState
**Related modules**: townlet.world.grid.WorldState

### Classes
- None

### Functions
- `register_hooks(world: 'WorldState') -> None` — Register built-in affordance hooks with the provided world. (line 16)
- `_on_attempt_shower(context: dict[str, Any]) -> None` — No docstring. (line 31)
- `_on_finish_shower(context: dict[str, Any]) -> None` — No docstring. (line 61)
- `_on_no_power(context: dict[str, Any]) -> None` — No docstring. (line 80)
- `_on_attempt_eat(context: dict[str, Any]) -> None` — No docstring. (line 96)
- `_on_finish_eat(context: dict[str, Any]) -> None` — No docstring. (line 136)
- `_on_attempt_cook(context: dict[str, Any]) -> None` — No docstring. (line 165)
- `_on_finish_cook(context: dict[str, Any]) -> None` — No docstring. (line 193)
- `_on_cook_fail(context: dict[str, Any]) -> None` — No docstring. (line 207)
- `_on_attempt_sleep(context: dict[str, Any]) -> None` — No docstring. (line 217)
- `_on_finish_sleep(context: dict[str, Any]) -> None` — No docstring. (line 249)
- `_abort_affordance(world: 'WorldState', spec: Any, agent_id: str, object_id: str, reason: str) -> None` — No docstring. (line 277)

### Constants and Configuration
- `_AFFORDANCE_FAIL_EVENT` = 'affordance_fail' (line 10)
- `_SHOWER_COMPLETE_EVENT` = 'shower_complete' (line 11)
- `_SHOWER_POWER_EVENT` = 'shower_power_outage' (line 12)
- `_SLEEP_COMPLETE_EVENT` = 'sleep_complete' (line 13)

### Data Flow
- Primary inputs: agent_id, context, object_id, reason, spec, world
- Return payloads: None
- Registers handlers or callbacks via register_hooks

### Integration Points
- External: None
- Internal: townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _abort_affordance, _on_attempt_cook, _on_attempt_eat, _on_attempt_shower, _on_attempt_sleep, _on_cook_fail, _on_finish_cook, _on_finish_eat, _on_finish_shower, _on_finish_sleep, _on_no_power

## `src/townlet/world/preconditions.py`

**Purpose**: Affordance precondition compilation and evaluation helpers.
**Lines of code**: 289
**Dependencies**: stdlib=__future__.annotations, ast, dataclasses.dataclass, re, typing.Any, typing.Iterable, typing.Mapping, typing.Sequence; external=None; internal=None
**Related modules**: None

### Classes
- `PreconditionSyntaxError` (bases: ValueError; decorators: None) — Raised when a manifest precondition has invalid syntax. (line 19)
- `PreconditionEvaluationError` (bases: RuntimeError; decorators: None) — Raised when evaluation fails due to missing context or type errors. (line 23)
- `CompiledPrecondition` (bases: object; decorators: dataclass(frozen=True)) — Stores the parsed AST and metadata for a precondition. (line 74)
  - Attributes:
    - name=`source`, type=`str` (line 77)
    - name=`tree`, type=`ast.AST` (line 78)
    - name=`identifiers`, type=`tuple[str, ...]` (line 79)
- `_IdentifierCollector` (bases: ast.NodeVisitor; decorators: None) — No class docstring provided. (line 82)
  - Methods:
    - `__init__(self) -> None` — No docstring. (line 83)
    - `visit_Name(self, node: ast.Name) -> None` — Collect bare identifiers used in the expression. (line 87)

### Functions
- `_normalize_expression(expression: str) -> str` — No docstring. (line 94)
- `_validate_tree(tree: ast.AST, source: str) -> tuple[str, ...]` — No docstring. (line 102)
- `compile_preconditions(expressions: Iterable[str]) -> tuple[CompiledPrecondition, ...]` — Compile manifest preconditions, raising on syntax errors. (line 134)
- `compile_precondition(expression: str) -> CompiledPrecondition` — Compile a single precondition expression. (line 156)
- `_resolve_name(name: str, context: Mapping[str, Any]) -> Any` — No docstring. (line 162)
- `_resolve_attr(value: Any, attr: str) -> Any` — No docstring. (line 169)
- `_resolve_subscript(value: Any, key: Any) -> Any` — No docstring. (line 177)
- `_evaluate(node: ast.AST, context: Mapping[str, Any]) -> Any` — No docstring. (line 184)
- `_apply_compare(operator: ast.cmpop, left: Any, right: Any) -> bool` — No docstring. (line 241)
- `evaluate_preconditions(preconditions: Sequence[CompiledPrecondition], context: Mapping[str, Any]) -> tuple[bool, CompiledPrecondition | None]` — Evaluate compiled preconditions against the provided context. (line 269)

### Constants and Configuration
- `_ALLOWED_COMPARE_OPS` = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn) (line 27)
- `_ALLOWED_BOOL_OPS` = (ast.And, ast.Or) (line 37)
- `_ALLOWED_UNARY_OPS` = (ast.Not, ast.USub, ast.UAdd) (line 38)
- `_ALLOWED_NODE_TYPES` = (ast.Expression, ast.BoolOp, ast.Compare, ast.Name, ast.Attribute, ast.Subscript, ast.Constant, ast.UnaryOp, ast.Tuple, ast.List, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.And, ast.Or, ast.Load, ast.USub, ast.UAdd, ast.Not) (line 39)

### Data Flow
- Primary inputs: attr, context, expression, expressions, key, left, name, node, operator, preconditions, right, source
- Return payloads: Any, CompiledPrecondition, None, bool, str, tuple[CompiledPrecondition, ...], tuple[bool, CompiledPrecondition | None], tuple[str, ...]
- Applies world or agent state updates via _apply_compare
- Evaluates conditions or invariants via _evaluate, evaluate_preconditions
- Validates inputs or configuration via _validate_tree

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: _IdentifierCollector.__init__, _apply_compare, _evaluate, _normalize_expression, _resolve_attr, _resolve_name, _resolve_subscript, _validate_tree

## `src/townlet/world/queue_manager.py`

**Purpose**: Queue management with fairness guardrails.
**Lines of code**: 273
**Dependencies**: stdlib=__future__.annotations, dataclasses.dataclass, time; external=None; internal=townlet.config.QueueFairnessConfig, townlet.config.SimulationConfig
**Related modules**: townlet.config.QueueFairnessConfig, townlet.config.SimulationConfig

### Classes
- `QueueEntry` (bases: object; decorators: dataclass) — Represents an agent waiting to access an interactive object. (line 18)
  - Attributes:
    - name=`agent_id`, type=`str` (line 21)
    - name=`joined_tick`, type=`int` (line 22)
- `QueueManager` (bases: object; decorators: None) — Coordinates reservations and fairness across interactive queues. (line 25)
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring. (line 28)
    - `on_tick(self, tick: int) -> None` — Expire cooldown entries whose window has elapsed. (line 53)
    - `request_access(self, object_id: str, agent_id: str, tick: int) -> bool` — Attempt to reserve the object for the agent. (line 59)
    - `release(self, object_id: str, agent_id: str, tick: int, *, success: bool = True) -> None` — Release the reservation and optionally apply cooldown. (line 88)
    - `record_blocked_attempt(self, object_id: str) -> bool` — Register that the current head was blocked. (line 110)
    - `active_agent(self, object_id: str) -> str | None` — Return the agent currently holding the reservation, if any. (line 133)
    - `queue_snapshot(self, object_id: str) -> list[str]` — Return the queue as an ordered list of agent IDs for debugging. (line 137)
    - `metrics(self) -> dict[str, int]` — Expose counters useful for telemetry. (line 141)
    - `performance_metrics(self) -> dict[str, int]` — Expose aggregated nanosecond timings and call counts. (line 145)
    - `reset_performance_metrics(self) -> None` — No docstring. (line 149)
    - `requeue_to_tail(self, object_id: str, agent_id: str, tick: int) -> None` — Append `agent_id` to the end of the queue if not already present. (line 153)
    - `remove_agent(self, agent_id: str, tick: int) -> None` — Remove `agent_id` from all queues and active reservations. (line 162)
    - `export_state(self) -> dict[str, object]` — Serialise queue activity for snapshot persistence. (line 176)
    - `import_state(self, payload: dict[str, object]) -> None` — Restore queue activity from persisted snapshot data. (line 199)
    - `_assign_next(self, object_id: str, tick: int) -> str | None` — No docstring. (line 243)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, config, object_id, payload, success, tick
- Return payloads: None, bool, dict[str, int], dict[str, object], list[str], str | None
- Advances tick or scheduler timelines via QueueManager.on_tick
- Exports payloads for downstream consumers via QueueManager.export_state
- Records metrics or histories via QueueManager.record_blocked_attempt
- Resets runtime state via QueueManager.reset_performance_metrics

### Integration Points
- External: None
- Internal: townlet.config.QueueFairnessConfig, townlet.config.SimulationConfig

### Code Quality Notes
- Missing docstrings: QueueManager.__init__, QueueManager._assign_next, QueueManager.reset_performance_metrics

## `src/townlet/world/relationships.py`

**Purpose**: Relationship ledger for Phase 4 social systems.
**Lines of code**: 169
**Dependencies**: stdlib=__future__.annotations, collections.abc.Callable, dataclasses.dataclass; external=None; internal=None
**Related modules**: None

### Classes
- `RelationshipParameters` (bases: object; decorators: dataclass) — Tuning knobs for relationship tie evolution. (line 14)
  - Attributes:
    - name=`max_edges`, type=`int`, default=`6` (line 17)
    - name=`trust_decay`, type=`float`, default=`0.0` (line 18)
    - name=`familiarity_decay`, type=`float`, default=`0.0` (line 19)
    - name=`rivalry_decay`, type=`float`, default=`0.01` (line 20)
- `RelationshipTie` (bases: object; decorators: dataclass) — No class docstring provided. (line 24)
  - Attributes:
    - name=`trust`, type=`float`, default=`0.0` (line 25)
    - name=`familiarity`, type=`float`, default=`0.0` (line 26)
    - name=`rivalry`, type=`float`, default=`0.0` (line 27)
  - Methods:
    - `as_dict(self) -> dict[str, float]` — No docstring. (line 29)
- `RelationshipLedger` (bases: object; decorators: None) — Maintains multi-dimensional ties for a single agent. (line 40)
  - Methods:
    - `__init__(self, *, owner_id: str, params: RelationshipParameters | None = None, eviction_hook: EvictionHook | None = None) -> None` — No docstring. (line 43)
    - `apply_delta(self, other_id: str, *, trust: float = 0.0, familiarity: float = 0.0, rivalry: float = 0.0) -> RelationshipTie` — No docstring. (line 55)
    - `tie_for(self, other_id: str) -> RelationshipTie | None` — Return the tie for ``other_id`` if it exists. (line 73)
    - `decay(self) -> None` — No docstring. (line 78)
    - `snapshot(self) -> dict[str, dict[str, float]]` — No docstring. (line 91)
    - `inject(self, payload: dict[str, dict[str, float]]) -> None` — No docstring. (line 94)
    - `set_eviction_hook(self, *, owner_id: str, hook: EvictionHook | None) -> None` — No docstring. (line 105)
    - `top_friends(self, limit: int) -> list[tuple[str, RelationshipTie]]` — No docstring. (line 109)
    - `top_rivals(self, limit: int) -> list[tuple[str, RelationshipTie]]` — No docstring. (line 119)
    - `remove_tie(self, other_id: str, *, reason: str = 'removed') -> None` — No docstring. (line 129)
    - `_prune_if_needed(self, *, reason: str) -> None` — No docstring. (line 134)
    - `_emit_eviction(self, other_id: str, *, reason: str) -> None` — No docstring. (line 147)

### Functions
- `_clamp(value: float, *, low: float, high: float) -> float` — No docstring. (line 9)
- `_decay_value(value: float, decay: float, *, minimum: float = -1.0) -> float` — No docstring. (line 155)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: decay, eviction_hook, familiarity, high, hook, limit, low, minimum, other_id, owner_id, params, payload
- Return payloads: None, RelationshipTie, RelationshipTie | None, dict[str, dict[str, float]], dict[str, float], float, list[tuple[str, RelationshipTie]]
- Applies world or agent state updates via RelationshipLedger.apply_delta

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: RelationshipLedger.__init__, RelationshipLedger._emit_eviction, RelationshipLedger._prune_if_needed, RelationshipLedger.apply_delta, RelationshipLedger.decay, RelationshipLedger.inject, RelationshipLedger.remove_tie, RelationshipLedger.set_eviction_hook, RelationshipLedger.snapshot, RelationshipLedger.top_friends, RelationshipLedger.top_rivals, RelationshipTie.as_dict, _clamp, _decay_value

## `src/townlet/world/rivalry.py`

**Purpose**: Rivalry state helpers used by conflict intro scaffolding.
**Lines of code**: 135
**Dependencies**: stdlib=__future__.annotations, collections.abc.Callable, collections.abc.Iterable, dataclasses.dataclass, dataclasses.field, typing.Optional; external=None; internal=None
**Related modules**: None

### Classes
- `RivalryParameters` (bases: object; decorators: dataclass) — Tuning knobs for rivalry evolution. (line 20)
  - Attributes:
    - name=`increment_per_conflict`, type=`float`, default=`0.15` (line 27)
    - name=`decay_per_tick`, type=`float`, default=`0.01` (line 28)
    - name=`min_value`, type=`float`, default=`0.0` (line 29)
    - name=`max_value`, type=`float`, default=`1.0` (line 30)
    - name=`avoid_threshold`, type=`float`, default=`0.7` (line 31)
    - name=`eviction_threshold`, type=`float`, default=`0.05` (line 32)
    - name=`max_edges`, type=`int`, default=`6` (line 33)
- `RivalryLedger` (bases: object; decorators: dataclass) — Maintains rivalry scores against other agents for a single actor. (line 37)
  - Attributes:
    - name=`owner_id`, type=`str` (line 40)
    - name=`params`, type=`RivalryParameters`, default=`field(default_factory=RivalryParameters)` (line 41)
    - name=`eviction_hook`, type=`Optional[Callable[[str, str, str], None]]`, default=`None` (line 42)
    - name=`_scores`, type=`dict[str, float]`, default=`field(default_factory=dict)` (line 43)
  - Methods:
    - `apply_conflict(self, other_id: str, *, intensity: float = 1.0) -> float` — Increase rivalry against `other_id` based on the conflict intensity. (line 45)
    - `decay(self, ticks: int = 1) -> None` — Apply passive decay across all rivalry edges. (line 69)
    - `inject(self, pairs: Iterable[tuple[str, float]]) -> None` — Seed rivalry scores from persisted state for round-tripping tests. (line 86)
    - `score_for(self, other_id: str) -> float` — No docstring. (line 95)
    - `should_avoid(self, other_id: str) -> bool` — Return True when rivalry exceeds the avoidance threshold. (line 98)
    - `top_rivals(self, limit: int) -> list[tuple[str, float]]` — Return the strongest rivalry edges sorted descending. (line 102)
    - `remove(self, other_id: str, *, reason: str = 'removed') -> None` — No docstring. (line 113)
    - `encode_features(self, limit: int) -> list[float]` — Encode rivalry magnitudes into a fixed-width list for observations. (line 119)
    - `snapshot(self) -> dict[str, float]` — Return a copy of rivalry scores for telemetry serialization. (line 128)
    - `_emit_eviction(self, other_id: str, *, reason: str) -> None` — No docstring. (line 132)

### Functions
- `_clamp(value: float, *, low: float, high: float) -> float` — No docstring. (line 15)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: high, intensity, limit, low, other_id, pairs, reason, ticks, value
- Return payloads: None, bool, dict[str, float], float, list[float], list[tuple[str, float]]
- Applies world or agent state updates via RivalryLedger.apply_conflict

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: RivalryLedger._emit_eviction, RivalryLedger.remove, RivalryLedger.score_for, _clamp

## `src/townlet_ui/__init__.py`

**Purpose**: Observer UI toolkit exports.
**Lines of code**: 19
**Dependencies**: stdlib=None; external=commands.ConsoleCommandExecutor, telemetry.AgentSummary, telemetry.EmploymentMetrics, telemetry.TelemetryClient, telemetry.TelemetrySnapshot, telemetry.TransportStatus; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: commands.ConsoleCommandExecutor, telemetry.AgentSummary, telemetry.EmploymentMetrics, telemetry.TelemetryClient, telemetry.TelemetrySnapshot, telemetry.TransportStatus
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `src/townlet_ui/commands.py`

**Purpose**: Helper utilities for dispatching console commands asynchronously.
**Lines of code**: 41
**Dependencies**: stdlib=__future__.annotations, logging, queue, threading, typing.Any; external=None; internal=townlet.console.handlers.ConsoleCommand
**Related modules**: townlet.console.handlers.ConsoleCommand

### Classes
- `ConsoleCommandExecutor` (bases: object; decorators: None) — Background dispatcher that forwards console commands via a router. (line 15)
  - Methods:
    - `__init__(self, router: Any, *, daemon: bool = True) -> None` — No docstring. (line 18)
    - `submit(self, command: ConsoleCommand) -> None` — No docstring. (line 26)
    - `shutdown(self, timeout: float | None = 1.0) -> None` — No docstring. (line 29)
    - `_worker(self) -> None` — No docstring. (line 33)

### Functions
- None

### Constants and Configuration
- None

### Data Flow
- Primary inputs: command, daemon, router, timeout
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.console.handlers.ConsoleCommand

### Code Quality Notes
- Missing docstrings: ConsoleCommandExecutor.__init__, ConsoleCommandExecutor._worker, ConsoleCommandExecutor.shutdown, ConsoleCommandExecutor.submit

## `src/townlet_ui/dashboard.py`

**Purpose**: Rich-based console dashboard for Townlet observer UI.
**Lines of code**: 777
**Dependencies**: stdlib=__future__.annotations, collections.abc.Iterable, collections.abc.Mapping, math, time, typing.Any, typing.TYPE_CHECKING; external=numpy, rich.console.Console, rich.console.Group, rich.console.RenderableType, rich.panel.Panel, rich.table.Table, rich.text.Text; internal=townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet_ui.commands.ConsoleCommandExecutor, townlet_ui.telemetry.TelemetryClient, townlet_ui.telemetry.TelemetrySnapshot
**Related modules**: townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet_ui.commands.ConsoleCommandExecutor, townlet_ui.telemetry.TelemetryClient, townlet_ui.telemetry.TelemetrySnapshot

### Classes
- None

### Functions
- `render_snapshot(snapshot: TelemetrySnapshot, tick: int, refreshed: str) -> Iterable[Panel]` — Yield rich Panels representing the current telemetry snapshot. (line 36)
- `_format_top_entries(entries: Mapping[str, int]) -> str` — No docstring. (line 277)
- `_build_narration_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring. (line 284)
- `_build_anneal_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring. (line 312)
- `_promotion_border_style(promotion: PromotionSnapshot | None) -> str` — No docstring. (line 434)
- `_derive_promotion_reason(promotion: PromotionSnapshot, status: AnnealStatus | None) -> str` — No docstring. (line 444)
- `_format_metadata_summary(metadata: Mapping[str, Any]) -> str` — No docstring. (line 468)
- `_build_promotion_history_panel(history: Iterable[Mapping[str, Any]], border_style: str) -> Panel` — No docstring. (line 484)
- `_format_history_metadata(entry: Mapping[str, Any]) -> str` — No docstring. (line 501)
- `_safe_format(value: float | None) -> str` — No docstring. (line 519)
- `_format_optional_float(value: float | None) -> str` — No docstring. (line 525)
- `_build_policy_inspector_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring. (line 531)
- `_build_relationship_overlay_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring. (line 569)
- `_format_delta(value: float, inverse: bool = False) -> str` — No docstring. (line 604)
- `_build_kpi_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring. (line 612)
- `_trend_from_series(series: list[float]) -> tuple[str, str]` — No docstring. (line 642)
- `_humanize_kpi(key: str) -> str` — No docstring. (line 657)
- `run_dashboard(loop: SimulationLoop, *, refresh_interval: float = 1.0, max_ticks: int = 0, approve: str | None = None, defer: str | None = None, focus_agent: str | None = None, show_coords: bool = False) -> None` — Continuously render dashboard against a SimulationLoop instance. (line 666)
- `_build_map_panel(snapshot: TelemetrySnapshot, obs_batch: Mapping[str, dict[str, np.ndarray]], focus_agent: str | None, show_coords: bool = False) -> Panel | None` — No docstring. (line 731)

### Constants and Configuration
- `MAP_AGENT_CHAR` = 'A' (line 25)
- `MAP_CENTER_CHAR` = 'S' (line 26)
- `NARRATION_CATEGORY_STYLES`: `dict[str, tuple[str, str]]` = {'utility_outage': ('Utility Outage', 'bold red'), 'shower_complete': ('Shower Complete', 'cyan'), 'sleep_complete': ('Sleep Complete', 'green'), 'queue_conflict': ('Queue Conflict', 'magenta')} (line 28)

### Data Flow
- Primary inputs: approve, border_style, defer, entries, entry, focus_agent, history, inverse, key, loop, max_ticks, metadata
- Return payloads: Iterable[Panel], None, Panel, Panel | None, str, tuple[str, str]
- Builds derived structures or observations via _build_anneal_panel, _build_kpi_panel, _build_map_panel, _build_narration_panel, _build_policy_inspector_panel, _build_promotion_history_panel, _build_relationship_overlay_panel

### Integration Points
- External: numpy, rich.console.Console, rich.console.Group, rich.console.RenderableType, rich.panel.Panel, rich.table.Table, rich.text.Text
- Internal: townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet_ui.commands.ConsoleCommandExecutor, townlet_ui.telemetry.TelemetryClient, townlet_ui.telemetry.TelemetrySnapshot

### Code Quality Notes
- Missing docstrings: _build_anneal_panel, _build_kpi_panel, _build_map_panel, _build_narration_panel, _build_policy_inspector_panel, _build_promotion_history_panel, _build_relationship_overlay_panel, _derive_promotion_reason, _format_delta, _format_history_metadata, _format_metadata_summary, _format_optional_float, _format_top_entries, _humanize_kpi, _promotion_border_style, _safe_format, _trend_from_series

## `src/townlet_ui/telemetry.py`

**Purpose**: Schema-aware telemetry client utilities for observer UI components.
**Lines of code**: 678
**Dependencies**: stdlib=__future__.annotations, collections.abc.Mapping, dataclasses.dataclass, typing.Any, typing.Iterable, typing.cast; external=None; internal=townlet.console.handlers.ConsoleCommand
**Related modules**: townlet.console.handlers.ConsoleCommand

### Classes
- `EmploymentMetrics` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 51)
  - Attributes:
    - name=`pending`, type=`list[str]` (line 52)
    - name=`pending_count`, type=`int` (line 53)
    - name=`exits_today`, type=`int` (line 54)
    - name=`daily_exit_cap`, type=`int` (line 55)
    - name=`queue_limit`, type=`int` (line 56)
    - name=`review_window`, type=`int` (line 57)
- `QueueHistoryEntry` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 61)
  - Attributes:
    - name=`tick`, type=`int` (line 62)
    - name=`cooldown_delta`, type=`int` (line 63)
    - name=`ghost_step_delta`, type=`int` (line 64)
    - name=`rotation_delta`, type=`int` (line 65)
    - name=`totals`, type=`Mapping[str, int]` (line 66)
- `RivalryEventEntry` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 70)
  - Attributes:
    - name=`tick`, type=`int` (line 71)
    - name=`agent_a`, type=`str` (line 72)
    - name=`agent_b`, type=`str` (line 73)
    - name=`intensity`, type=`float` (line 74)
    - name=`reason`, type=`str` (line 75)
- `ConflictMetrics` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 79)
  - Attributes:
    - name=`queue_cooldown_events`, type=`int` (line 80)
    - name=`queue_ghost_step_events`, type=`int` (line 81)
    - name=`queue_rotation_events`, type=`int` (line 82)
    - name=`queue_history`, type=`tuple[QueueHistoryEntry, ...]` (line 83)
    - name=`rivalry_agents`, type=`int` (line 84)
    - name=`rivalry_events`, type=`tuple[RivalryEventEntry, ...]` (line 85)
    - name=`raw`, type=`Mapping[str, Any]` (line 86)
- `NarrationEntry` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 90)
  - Attributes:
    - name=`tick`, type=`int` (line 91)
    - name=`category`, type=`str` (line 92)
    - name=`message`, type=`str` (line 93)
    - name=`priority`, type=`bool` (line 94)
    - name=`data`, type=`Mapping[str, Any]` (line 95)
- `RelationshipChurn` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 99)
  - Attributes:
    - name=`window_start`, type=`int` (line 100)
    - name=`window_end`, type=`int` (line 101)
    - name=`total_evictions`, type=`int` (line 102)
    - name=`per_owner`, type=`Mapping[str, int]` (line 103)
    - name=`per_reason`, type=`Mapping[str, int]` (line 104)
- `RelationshipUpdate` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 108)
  - Attributes:
    - name=`owner`, type=`str` (line 109)
    - name=`other`, type=`str` (line 110)
    - name=`status`, type=`str` (line 111)
    - name=`trust`, type=`float` (line 112)
    - name=`familiarity`, type=`float` (line 113)
    - name=`rivalry`, type=`float` (line 114)
    - name=`delta_trust`, type=`float` (line 115)
    - name=`delta_familiarity`, type=`float` (line 116)
    - name=`delta_rivalry`, type=`float` (line 117)
- `AgentSummary` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 121)
  - Attributes:
    - name=`agent_id`, type=`str` (line 122)
    - name=`wallet`, type=`float` (line 123)
    - name=`shift_state`, type=`str` (line 124)
    - name=`attendance_ratio`, type=`float` (line 125)
    - name=`wages_withheld`, type=`float` (line 126)
    - name=`lateness_counter`, type=`int` (line 127)
    - name=`on_shift`, type=`bool` (line 128)
- `RelationshipOverlayEntry` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 132)
  - Attributes:
    - name=`other`, type=`str` (line 133)
    - name=`trust`, type=`float` (line 134)
    - name=`familiarity`, type=`float` (line 135)
    - name=`rivalry`, type=`float` (line 136)
    - name=`delta_trust`, type=`float` (line 137)
    - name=`delta_familiarity`, type=`float` (line 138)
    - name=`delta_rivalry`, type=`float` (line 139)
- `PolicyInspectorAction` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 143)
  - Attributes:
    - name=`action`, type=`str` (line 144)
    - name=`probability`, type=`float` (line 145)
- `PolicyInspectorEntry` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 149)
  - Attributes:
    - name=`agent_id`, type=`str` (line 150)
    - name=`tick`, type=`int` (line 151)
    - name=`selected_action`, type=`str` (line 152)
    - name=`log_prob`, type=`float` (line 153)
    - name=`value_pred`, type=`float` (line 154)
    - name=`top_actions`, type=`list[PolicyInspectorAction]` (line 155)
- `AnnealStatus` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 159)
  - Attributes:
    - name=`stage`, type=`str` (line 160)
    - name=`cycle`, type=`float | None` (line 161)
    - name=`dataset`, type=`str` (line 162)
    - name=`bc_accuracy`, type=`float | None` (line 163)
    - name=`bc_threshold`, type=`float | None` (line 164)
    - name=`bc_passed`, type=`bool` (line 165)
    - name=`loss_flag`, type=`bool` (line 166)
    - name=`queue_flag`, type=`bool` (line 167)
    - name=`intensity_flag`, type=`bool` (line 168)
    - name=`loss_baseline`, type=`float | None` (line 169)
    - name=`queue_baseline`, type=`float | None` (line 170)
    - name=`intensity_baseline`, type=`float | None` (line 171)
- `TransportStatus` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 175)
  - Attributes:
    - name=`connected`, type=`bool` (line 176)
    - name=`dropped_messages`, type=`int` (line 177)
    - name=`last_error`, type=`str | None` (line 178)
    - name=`last_success_tick`, type=`int | None` (line 179)
    - name=`last_failure_tick`, type=`int | None` (line 180)
    - name=`queue_length`, type=`int` (line 181)
    - name=`last_flush_duration_ms`, type=`float | None` (line 182)
- `StabilitySnapshot` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 186)
  - Attributes:
    - name=`alerts`, type=`tuple[str, ...]` (line 187)
    - name=`metrics`, type=`Mapping[str, Any]` (line 188)
- `HealthStatus` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 192)
  - Attributes:
    - name=`tick`, type=`int` (line 193)
    - name=`tick_duration_ms`, type=`float` (line 194)
    - name=`telemetry_queue`, type=`int` (line 195)
    - name=`telemetry_dropped`, type=`int` (line 196)
    - name=`perturbations_pending`, type=`int` (line 197)
    - name=`perturbations_active`, type=`int` (line 198)
    - name=`employment_exit_queue`, type=`int` (line 199)
    - name=`raw`, type=`Mapping[str, Any]` (line 200)
- `PromotionSnapshot` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 204)
  - Attributes:
    - name=`state`, type=`str | None` (line 205)
    - name=`pass_streak`, type=`int` (line 206)
    - name=`required_passes`, type=`int` (line 207)
    - name=`candidate_ready`, type=`bool` (line 208)
    - name=`candidate_ready_tick`, type=`int | None` (line 209)
    - name=`last_result`, type=`str | None` (line 210)
    - name=`last_evaluated_tick`, type=`int | None` (line 211)
    - name=`candidate_metadata`, type=`Mapping[str, Any] | None` (line 212)
    - name=`current_release`, type=`Mapping[str, Any] | None` (line 213)
    - name=`history`, type=`tuple[Mapping[str, Any], ...]` (line 214)
- `TelemetrySnapshot` (bases: object; decorators: dataclass(frozen=True)) — No class docstring provided. (line 218)
  - Attributes:
    - name=`schema_version`, type=`str` (line 219)
    - name=`schema_warning`, type=`str | None` (line 220)
    - name=`employment`, type=`EmploymentMetrics` (line 221)
    - name=`conflict`, type=`ConflictMetrics` (line 222)
    - name=`narrations`, type=`list[NarrationEntry]` (line 223)
    - name=`narration_state`, type=`Mapping[str, Any]` (line 224)
    - name=`relationships`, type=`RelationshipChurn | None` (line 225)
    - name=`relationship_snapshot`, type=`Mapping[str, Mapping[str, Mapping[str, float]]]` (line 226)
    - name=`relationship_updates`, type=`list[RelationshipUpdate]` (line 227)
    - name=`relationship_overlay`, type=`Mapping[str, list[RelationshipOverlayEntry]]` (line 228)
    - name=`agents`, type=`list[AgentSummary]` (line 229)
    - name=`anneal`, type=`AnnealStatus | None` (line 230)
    - name=`policy_inspector`, type=`list[PolicyInspectorEntry]` (line 231)
    - name=`promotion`, type=`PromotionSnapshot | None` (line 232)
    - name=`stability`, type=`StabilitySnapshot` (line 233)
    - name=`kpis`, type=`Mapping[str, list[float]]` (line 234)
    - name=`transport`, type=`TransportStatus` (line 235)
    - name=`health`, type=`HealthStatus | None` (line 236)
    - name=`raw`, type=`Mapping[str, Any]` (line 237)
- `SchemaMismatchError` (bases: RuntimeError; decorators: None) — Raised when telemetry schema is newer than the client supports. (line 240)
- `TelemetryClient` (bases: object; decorators: None) — Lightweight helper to parse telemetry payloads for the observer UI. (line 244)
  - Methods:
    - `__init__(self, *, expected_schema_prefix: str = SUPPORTED_SCHEMA_PREFIX) -> None` — No docstring. (line 247)
    - `parse_snapshot(self, payload: Mapping[str, Any]) -> TelemetrySnapshot` — Validate and convert a telemetry payload into dataclasses. (line 250)
    - `from_console(self, router: Any) -> TelemetrySnapshot` — Fetch snapshot via console router (expects telemetry_snapshot command). (line 642)
    - `_check_schema(self, version: str) -> str | None` — No docstring. (line 655)
    - `_get_section(payload: Mapping[str, Any], key: str, expected: type) -> Mapping[str, Any]` — No docstring. (line 667)

### Functions
- `_maybe_float(value: object) -> float | None` — No docstring. (line 10)
- `_coerce_float(value: object, default: float = 0.0) -> float` — No docstring. (line 16)
- `_coerce_mapping(value: object) -> Mapping[str, Any] | None` — No docstring. (line 21)
- `_coerce_history_entries(value: object) -> tuple[Mapping[str, Any], ...]` — No docstring. (line 27)
- `_console_command(name: str) -> Any` — Helper to build console command dataclass without importing CLI package. (line 674)

### Constants and Configuration
- `SUPPORTED_SCHEMA_PREFIX` = '0.9' (line 47)

### Data Flow
- Primary inputs: default, expected, expected_schema_prefix, key, name, payload, router, value, version
- Return payloads: Any, Mapping[str, Any], Mapping[str, Any] | None, None, TelemetrySnapshot, float, float | None, str | None, tuple[Mapping[str, Any], ...]
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.console.handlers.ConsoleCommand

### Code Quality Notes
- Missing docstrings: TelemetryClient.__init__, TelemetryClient._check_schema, TelemetryClient._get_section, _coerce_float, _coerce_history_entries, _coerce_mapping, _maybe_float

## `tests/conftest.py`

**Purpose**: Pytest configuration ensuring project imports resolve during tests.
**Lines of code**: 13
**Dependencies**: stdlib=__future__.annotations, pathlib.Path, sys; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- None

### Constants and Configuration
- `ROOT` = Path(__file__).resolve().parents[1] (line 7)
- `SRC` = ROOT / 'src' (line 8)

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None (procedural side-effects only).
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No immediate issues detected from static scan.

## `tests/test_affordance_hooks.py`

**Purpose**: No module docstring provided.
**Lines of code**: 195
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `make_world() -> tuple[SimulationLoop, WorldState]` — No docstring. (line 9)
- `request_object(world, object_id: str, agent_id: str) -> None` — No docstring. (line 17)
- `test_affordance_before_after_hooks_fire_once() -> None` — No docstring. (line 23)
- `test_affordance_fail_hook_runs_once_per_failure() -> None` — No docstring. (line 58)
- `test_shower_requires_power() -> None` — No docstring. (line 102)
- `test_shower_completion_emits_event() -> None` — No docstring. (line 129)
- `test_sleep_slots_cycle_and_completion_event() -> None` — No docstring. (line 153)
- `test_sleep_attempt_fails_when_no_slots() -> None` — No docstring. (line 177)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, object_id, world
- Return payloads: None, tuple[SimulationLoop, WorldState]
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: make_world, request_object, test_affordance_before_after_hooks_fire_once, test_affordance_fail_hook_runs_once_per_failure, test_shower_completion_emits_event, test_shower_requires_power, test_sleep_attempt_fails_when_no_slots, test_sleep_slots_cycle_and_completion_event

## `tests/test_affordance_manifest.py`

**Purpose**: No module docstring provided.
**Lines of code**: 114
**Dependencies**: stdlib=__future__.annotations, hashlib, pathlib.Path; external=pytest; internal=townlet.config.SimulationConfig, townlet.config.load_config, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState
**Related modules**: townlet.config.SimulationConfig, townlet.config.load_config, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_configure_with_manifest(manifest_path: Path) -> SimulationConfig` — No docstring. (line 13)
- `test_affordance_manifest_loads_and_exposes_metadata(tmp_path: Path) -> None` — No docstring. (line 20)
- `test_affordance_manifest_duplicate_ids_fail(tmp_path: Path) -> None` — No docstring. (line 52)
- `test_affordance_manifest_missing_duration_fails(tmp_path: Path) -> None` — No docstring. (line 72)
- `test_affordance_manifest_checksum_exposed_in_telemetry(tmp_path: Path) -> None` — No docstring. (line 87)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: manifest_path, tmp_path
- Return payloads: None, SimulationConfig
- Loads configuration or datasets from disk via test_affordance_manifest_loads_and_exposes_metadata

### Integration Points
- External: pytest
- Internal: townlet.config.SimulationConfig, townlet.config.load_config, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _configure_with_manifest, test_affordance_manifest_checksum_exposed_in_telemetry, test_affordance_manifest_duplicate_ids_fail, test_affordance_manifest_loads_and_exposes_metadata, test_affordance_manifest_missing_duration_fails

## `tests/test_affordance_preconditions.py`

**Purpose**: No module docstring provided.
**Lines of code**: 120
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.preconditions.PreconditionSyntaxError, townlet.world.preconditions.compile_preconditions, townlet.world.preconditions.evaluate_preconditions
**Related modules**: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.preconditions.PreconditionSyntaxError, townlet.world.preconditions.compile_preconditions, townlet.world.preconditions.evaluate_preconditions

### Classes
- None

### Functions
- `_make_loop() -> tuple[SimulationLoop, object]` — No docstring. (line 18)
- `_request_object(world, object_id: str, agent_id: str) -> None` — No docstring. (line 25)
- `test_compile_preconditions_normalises_booleans() -> None` — No docstring. (line 31)
- `test_compile_preconditions_rejects_function_calls() -> None` — No docstring. (line 38)
- `test_evaluate_preconditions_supports_nested_attributes() -> None` — No docstring. (line 43)
- `test_precondition_failure_blocks_affordance_and_emits_event() -> None` — No docstring. (line 51)
- `test_precondition_success_allows_affordance_start() -> None` — No docstring. (line 101)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, object_id, world
- Return payloads: None, tuple[SimulationLoop, object]
- Evaluates conditions or invariants via test_evaluate_preconditions_supports_nested_attributes

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.preconditions.PreconditionSyntaxError, townlet.world.preconditions.compile_preconditions, townlet.world.preconditions.evaluate_preconditions

### Code Quality Notes
- Missing docstrings: _make_loop, _request_object, test_compile_preconditions_normalises_booleans, test_compile_preconditions_rejects_function_calls, test_evaluate_preconditions_supports_nested_attributes, test_precondition_failure_blocks_affordance_and_emits_event, test_precondition_success_allows_affordance_start

## `tests/test_basket_telemetry.py`

**Purpose**: No module docstring provided.
**Lines of code**: 32
**Dependencies**: stdlib=pathlib.Path; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `test_basket_cost_in_telemetry_snapshot() -> None` — No docstring. (line 8)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: test_basket_cost_in_telemetry_snapshot

## `tests/test_bc_capture_prototype.py`

**Purpose**: No module docstring provided.
**Lines of code**: 64
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path; external=numpy; internal=townlet.policy.replay.frames_to_replay_sample, townlet.policy.replay.load_replay_sample
**Related modules**: townlet.policy.replay.frames_to_replay_sample, townlet.policy.replay.load_replay_sample

### Classes
- None

### Functions
- `test_synthetic_bc_capture_round_trip(tmp_path: Path) -> None` — No docstring. (line 11)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Captures trajectories or telemetry snapshots via test_synthetic_bc_capture_round_trip

### Integration Points
- External: numpy
- Internal: townlet.policy.replay.frames_to_replay_sample, townlet.policy.replay.load_replay_sample

### Code Quality Notes
- Missing docstrings: test_synthetic_bc_capture_round_trip

## `tests/test_bc_trainer.py`

**Purpose**: No module docstring provided.
**Lines of code**: 81
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=numpy, pytest; internal=townlet.policy.BCTrainer, townlet.policy.BCTrainingConfig, townlet.policy.BCTrajectoryDataset, townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.torch_available, townlet.policy.replay.frames_to_replay_sample
**Related modules**: townlet.policy.BCTrainer, townlet.policy.BCTrainingConfig, townlet.policy.BCTrajectoryDataset, townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.torch_available, townlet.policy.replay.frames_to_replay_sample

### Classes
- None

### Functions
- `test_bc_trainer_overfits_toy_dataset(tmp_path: Path) -> None` — No docstring. (line 14)
- `test_bc_evaluate_accuracy(tmp_path: Path) -> None` — No docstring. (line 50)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Evaluates conditions or invariants via test_bc_evaluate_accuracy
- Trains policies or models via test_bc_trainer_overfits_toy_dataset

### Integration Points
- External: numpy, pytest
- Internal: townlet.policy.BCTrainer, townlet.policy.BCTrainingConfig, townlet.policy.BCTrajectoryDataset, townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.torch_available, townlet.policy.replay.frames_to_replay_sample

### Code Quality Notes
- Missing docstrings: test_bc_evaluate_accuracy, test_bc_trainer_overfits_toy_dataset

## `tests/test_behavior_rivalry.py`

**Purpose**: No module docstring provided.
**Lines of code**: 69
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.policy.behavior.ScriptedBehavior, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.policy.behavior.ScriptedBehavior, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring. (line 10)
- `test_scripted_behavior_avoids_queue_with_rival() -> None` — No docstring. (line 33)
- `test_scripted_behavior_requests_when_no_rival() -> None` — No docstring. (line 48)
- `test_behavior_retries_after_rival_leaves() -> None` — No docstring. (line 57)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, WorldState
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.policy.behavior.ScriptedBehavior, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _make_world, test_behavior_retries_after_rival_leaves, test_scripted_behavior_avoids_queue_with_rival, test_scripted_behavior_requests_when_no_rival

## `tests/test_capture_scripted_cli.py`

**Purpose**: No module docstring provided.
**Lines of code**: 39
**Dependencies**: stdlib=json, pathlib.Path, runpy; external=None; internal=townlet.policy.replay.load_replay_sample
**Related modules**: townlet.policy.replay.load_replay_sample

### Classes
- None

### Functions
- `test_capture_scripted_idle(tmp_path: Path) -> None` — No docstring. (line 8)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Captures trajectories or telemetry snapshots via test_capture_scripted_idle

### Integration Points
- External: None
- Internal: townlet.policy.replay.load_replay_sample

### Code Quality Notes
- Missing docstrings: test_capture_scripted_idle

## `tests/test_cli_validate_affordances.py`

**Purpose**: No module docstring provided.
**Lines of code**: 95
**Dependencies**: stdlib=__future__.annotations, pathlib.Path, subprocess, sys; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `_run(*args: str) -> subprocess.CompletedProcess[str]` — No docstring. (line 10)
- `test_validate_affordances_cli_success(tmp_path: Path) -> None` — No docstring. (line 15)
- `test_validate_affordances_cli_failure(tmp_path: Path) -> None` — No docstring. (line 35)
- `test_validate_affordances_cli_bad_precondition(tmp_path: Path) -> None` — No docstring. (line 50)
- `test_validate_affordances_cli_directory(tmp_path: Path) -> None` — No docstring. (line 68)

### Constants and Configuration
- `SCRIPT` = Path('scripts/validate_affordances.py').resolve() (line 7)

### Data Flow
- Primary inputs: args, tmp_path
- Return payloads: None, subprocess.CompletedProcess[str]
- Validates inputs or configuration via test_validate_affordances_cli_bad_precondition, test_validate_affordances_cli_directory, test_validate_affordances_cli_failure, test_validate_affordances_cli_success

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: _run, test_validate_affordances_cli_bad_precondition, test_validate_affordances_cli_directory, test_validate_affordances_cli_failure, test_validate_affordances_cli_success

## `tests/test_config_loader.py`

**Purpose**: No module docstring provided.
**Lines of code**: 259
**Dependencies**: stdlib=pathlib.Path, sys, types; external=pytest, yaml; internal=townlet.config.SimulationConfig, townlet.config.load_config, townlet.snapshots.migrations.clear_registry, townlet.snapshots.migrations.migration_registry
**Related modules**: townlet.config.SimulationConfig, townlet.config.load_config, townlet.snapshots.migrations.clear_registry, townlet.snapshots.migrations.migration_registry

### Classes
- None

### Functions
- `poc_config(tmp_path: Path) -> Path` — No docstring. (line 13)
- `test_load_config(poc_config: Path) -> None` — No docstring. (line 20)
- `test_invalid_queue_cooldown_rejected(tmp_path: Path) -> None` — No docstring. (line 68)
- `test_invalid_embedding_threshold_rejected(tmp_path: Path) -> None` — No docstring. (line 79)
- `test_invalid_embedding_slot_count(tmp_path: Path) -> None` — No docstring. (line 90)
- `test_invalid_affordance_file_absent(tmp_path: Path) -> None` — No docstring. (line 101)
- `test_observation_variant_guard(tmp_path: Path) -> None` — No docstring. (line 112)
- `test_ppo_config_defaults_roundtrip(tmp_path: Path) -> None` — No docstring. (line 123)
- `test_observation_variant_full_supported(tmp_path: Path) -> None` — No docstring. (line 139)
- `test_observation_variant_compact_supported(tmp_path: Path) -> None` — No docstring. (line 150)
- `test_snapshot_autosave_cadence_validation(tmp_path: Path) -> None` — No docstring. (line 161)
- `test_snapshot_identity_overrides_take_precedence(poc_config: Path) -> None` — No docstring. (line 174)
- `test_register_snapshot_migrations_from_config(poc_config: Path) -> None` — No docstring. (line 199)
- `test_telemetry_transport_defaults(poc_config: Path) -> None` — No docstring. (line 231)
- `test_telemetry_file_transport_requires_path(tmp_path: Path) -> None` — No docstring. (line 240)
- `test_telemetry_tcp_transport_requires_endpoint(tmp_path: Path) -> None` — No docstring. (line 251)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: poc_config, tmp_path
- Return payloads: None, Path
- Loads configuration or datasets from disk via test_load_config
- Persists state or reports to disk via test_snapshot_autosave_cadence_validation
- Registers handlers or callbacks via test_register_snapshot_migrations_from_config

### Integration Points
- External: pytest, yaml
- Internal: townlet.config.SimulationConfig, townlet.config.load_config, townlet.snapshots.migrations.clear_registry, townlet.snapshots.migrations.migration_registry

### Code Quality Notes
- Missing docstrings: poc_config, test_invalid_affordance_file_absent, test_invalid_embedding_slot_count, test_invalid_embedding_threshold_rejected, test_invalid_queue_cooldown_rejected, test_load_config, test_observation_variant_compact_supported, test_observation_variant_full_supported, test_observation_variant_guard, test_ppo_config_defaults_roundtrip, test_register_snapshot_migrations_from_config, test_snapshot_autosave_cadence_validation, test_snapshot_identity_overrides_take_precedence, test_telemetry_file_transport_requires_path, test_telemetry_tcp_transport_requires_endpoint, test_telemetry_transport_defaults

## `tests/test_conflict_scenarios.py`

**Purpose**: No module docstring provided.
**Lines of code**: 89
**Dependencies**: stdlib=__future__.annotations, pathlib.Path, random, types.SimpleNamespace; external=pytest; internal=townlet.config.loader.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.scenario_utils.apply_scenario, townlet.world.queue_manager.QueueManager
**Related modules**: townlet.config.loader.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.scenario_utils.apply_scenario, townlet.world.queue_manager.QueueManager

### Classes
- None

### Functions
- `_run_scenario(config_path: str, ticks: int) -> SimulationLoop` — No docstring. (line 15)
- `test_queue_conflict_scenario_produces_alerts() -> None` — No docstring. (line 31)
- `test_rivalry_decay_scenario_tracks_events() -> None` — No docstring. (line 47)
- `test_queue_manager_randomised_regression(seed: int) -> None` — No docstring. (line 59)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config_path, seed, ticks
- Return payloads: None, SimulationLoop
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: townlet.config.loader.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.scenario_utils.apply_scenario, townlet.world.queue_manager.QueueManager

### Code Quality Notes
- Missing docstrings: _run_scenario, test_queue_conflict_scenario_produces_alerts, test_queue_manager_randomised_regression, test_rivalry_decay_scenario_tracks_events

## `tests/test_conflict_telemetry.py`

**Purpose**: No module docstring provided.
**Lines of code**: 125
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `test_conflict_snapshot_reports_rivalry_counts() -> None` — No docstring. (line 10)
- `test_replay_sample_matches_schema(tmp_path: Path) -> None` — No docstring. (line 73)
- `test_conflict_export_import_preserves_history() -> None` — No docstring. (line 82)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Exports payloads for downstream consumers via test_conflict_export_import_preserves_history
- Handles replay buffers or datasets via test_replay_sample_matches_schema

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: test_conflict_export_import_preserves_history, test_conflict_snapshot_reports_rivalry_counts, test_replay_sample_matches_schema

## `tests/test_console_commands.py`

**Purpose**: No module docstring provided.
**Lines of code**: 463
**Dependencies**: stdlib=dataclasses.replace, pathlib.Path; external=None; internal=townlet.config.ArrangedMeetEventConfig, townlet.config.FloatRange, townlet.config.IntRange, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.snapshots.SnapshotManager, townlet.snapshots.migrations.clear_registry, townlet.snapshots.migrations.register_migration, townlet.snapshots.state.SnapshotState, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.ArrangedMeetEventConfig, townlet.config.FloatRange, townlet.config.IntRange, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.snapshots.SnapshotManager, townlet.snapshots.migrations.clear_registry, townlet.snapshots.migrations.register_migration, townlet.snapshots.state.SnapshotState, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `test_console_telemetry_snapshot_returns_payload() -> None` — No docstring. (line 20)
- `test_console_conflict_status_reports_history() -> None` — No docstring. (line 55)
- `test_console_queue_inspect_returns_queue_details() -> None` — No docstring. (line 91)
- `test_console_set_spawn_delay_updates_lifecycle() -> None` — No docstring. (line 109)
- `test_console_rivalry_dump_reports_pairs() -> None` — No docstring. (line 133)
- `test_employment_console_commands_manage_queue() -> None` — No docstring. (line 168)
- `test_console_schema_warning_for_newer_version() -> None` — No docstring. (line 207)
- `test_console_perturbation_requires_admin_mode() -> None` — No docstring. (line 220)
- `test_console_perturbation_commands_schedule_and_cancel() -> None` — No docstring. (line 237)
- `test_console_arrange_meet_schedules_event() -> None` — No docstring. (line 295)
- `test_console_arrange_meet_unknown_spec_returns_error() -> None` — No docstring. (line 339)
- `test_console_snapshot_commands(tmp_path: Path) -> None` — No docstring. (line 365)
- `test_console_snapshot_rejects_outside_roots(tmp_path: Path) -> None` — No docstring. (line 447)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Loads configuration or datasets from disk via test_console_telemetry_snapshot_returns_payload
- Updates internal caches or trackers via test_console_set_spawn_delay_updates_lifecycle

### Integration Points
- External: None
- Internal: townlet.config.ArrangedMeetEventConfig, townlet.config.FloatRange, townlet.config.IntRange, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.snapshots.SnapshotManager, townlet.snapshots.migrations.clear_registry, townlet.snapshots.migrations.register_migration, townlet.snapshots.state.SnapshotState, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: test_console_arrange_meet_schedules_event, test_console_arrange_meet_unknown_spec_returns_error, test_console_conflict_status_reports_history, test_console_perturbation_commands_schedule_and_cancel, test_console_perturbation_requires_admin_mode, test_console_queue_inspect_returns_queue_details, test_console_rivalry_dump_reports_pairs, test_console_schema_warning_for_newer_version, test_console_set_spawn_delay_updates_lifecycle, test_console_snapshot_commands, test_console_snapshot_rejects_outside_roots, test_console_telemetry_snapshot_returns_payload, test_employment_console_commands_manage_queue

## `tests/test_console_dispatcher.py`

**Purpose**: No module docstring provided.
**Lines of code**: 482
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `employment_loop() -> SimulationLoop` — No docstring. (line 14)
- `_queue_command(loop: SimulationLoop, payload: dict[str, object]) -> None` — No docstring. (line 28)
- `test_dispatcher_processes_employment_review(employment_loop: SimulationLoop) -> None` — No docstring. (line 32)
- `test_dispatcher_idempotency_reuses_history(employment_loop: SimulationLoop) -> None` — No docstring. (line 52)
- `test_dispatcher_requires_admin_mode(employment_loop: SimulationLoop) -> None` — No docstring. (line 74)
- `test_dispatcher_enforces_cmd_id_for_destructive_ops(employment_loop: SimulationLoop) -> None` — No docstring. (line 94)
- `test_spawn_command_creates_agent(employment_loop: SimulationLoop) -> None` — No docstring. (line 112)
- `test_spawn_rejects_duplicate_id(employment_loop: SimulationLoop) -> None` — No docstring. (line 134)
- `test_teleport_moves_agent(employment_loop: SimulationLoop) -> None` — No docstring. (line 151)
- `test_teleport_rejects_blocked_tile(employment_loop: SimulationLoop) -> None` — No docstring. (line 166)
- `test_setneed_updates_needs(employment_loop: SimulationLoop) -> None` — No docstring. (line 187)
- `test_setneed_rejects_unknown_need(employment_loop: SimulationLoop) -> None` — No docstring. (line 210)
- `test_price_updates_economy_and_basket(employment_loop: SimulationLoop) -> None` — No docstring. (line 230)
- `test_price_rejects_unknown_key(employment_loop: SimulationLoop) -> None` — No docstring. (line 252)
- `test_force_chat_updates_relationship(employment_loop: SimulationLoop) -> None` — No docstring. (line 267)
- `test_force_chat_requires_distinct_agents(employment_loop: SimulationLoop) -> None` — No docstring. (line 297)
- `test_set_rel_updates_ties(employment_loop: SimulationLoop) -> None` — No docstring. (line 312)
- `test_possess_acquire_and_release(employment_loop: SimulationLoop) -> None` — No docstring. (line 343)
- `test_possess_errors_on_duplicate_or_missing(employment_loop: SimulationLoop) -> None` — No docstring. (line 375)
- `test_kill_command_removes_agent(employment_loop: SimulationLoop) -> None` — No docstring. (line 419)
- `test_toggle_mortality_updates_flag(employment_loop: SimulationLoop) -> None` — No docstring. (line 441)
- `test_set_exit_cap_updates_config(employment_loop: SimulationLoop) -> None` — No docstring. (line 463)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: employment_loop, loop, payload
- Return payloads: None, SimulationLoop
- Updates internal caches or trackers via test_force_chat_updates_relationship, test_price_updates_economy_and_basket, test_set_exit_cap_updates_config, test_set_rel_updates_ties, test_setneed_updates_needs, test_toggle_mortality_updates_flag

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: _queue_command, employment_loop, test_dispatcher_enforces_cmd_id_for_destructive_ops, test_dispatcher_idempotency_reuses_history, test_dispatcher_processes_employment_review, test_dispatcher_requires_admin_mode, test_force_chat_requires_distinct_agents, test_force_chat_updates_relationship, test_kill_command_removes_agent, test_possess_acquire_and_release, test_possess_errors_on_duplicate_or_missing, test_price_rejects_unknown_key, test_price_updates_economy_and_basket, test_set_exit_cap_updates_config, test_set_rel_updates_ties, test_setneed_rejects_unknown_need, test_setneed_updates_needs, test_spawn_command_creates_agent, test_spawn_rejects_duplicate_id, test_teleport_moves_agent
- ... 2 additional methods without docstrings

## `tests/test_console_events.py`

**Purpose**: No module docstring provided.
**Lines of code**: 40
**Dependencies**: stdlib=pathlib.Path; external=None; internal=townlet.config.load_config, townlet.console.handlers.EventStream, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.console.handlers.EventStream, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `test_event_stream_receives_published_events() -> None` — No docstring. (line 9)
- `test_event_stream_handles_empty_batch() -> None` — No docstring. (line 32)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Publishes telemetry or events via test_event_stream_receives_published_events

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.console.handlers.EventStream, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: test_event_stream_handles_empty_batch, test_event_stream_receives_published_events

## `tests/test_console_promotion.py`

**Purpose**: No module docstring provided.
**Lines of code**: 136
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop
**Related modules**: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop

### Classes
- None

### Functions
- `admin_router() -> tuple[SimulationLoop, object]` — No docstring. (line 11)
- `make_ready(loop: SimulationLoop) -> None` — No docstring. (line 27)
- `test_promotion_status_command(admin_router: tuple[SimulationLoop, object]) -> None` — No docstring. (line 42)
- `test_promote_and_rollback_commands(admin_router: tuple[SimulationLoop, object]) -> None` — No docstring. (line 48)
- `test_policy_swap_command(admin_router: tuple[SimulationLoop, object], tmp_path: Path) -> None` — No docstring. (line 83)
- `test_policy_swap_missing_file(admin_router: tuple[SimulationLoop, object]) -> None` — No docstring. (line 106)
- `viewer_router() -> object` — No docstring. (line 119)
- `test_viewer_mode_forbidden(viewer_router: object) -> None` — No docstring. (line 134)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: admin_router, loop, tmp_path, viewer_router
- Return payloads: None, object, tuple[SimulationLoop, object]
- Promotes builds or policies via test_promote_and_rollback_commands

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop

### Code Quality Notes
- Missing docstrings: admin_router, make_ready, test_policy_swap_command, test_policy_swap_missing_file, test_promote_and_rollback_commands, test_promotion_status_command, test_viewer_mode_forbidden, viewer_router

## `tests/test_curate_trajectories.py`

**Purpose**: No module docstring provided.
**Lines of code**: 81
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path, runpy; external=numpy; internal=townlet.policy.replay.frames_to_replay_sample
**Related modules**: townlet.policy.replay.frames_to_replay_sample

### Classes
- None

### Functions
- `_write_sample(output_dir: Path, stem: str, rewards: np.ndarray, timesteps: int) -> None` — No docstring. (line 12)
- `test_curate_trajectories(tmp_path: Path) -> None` — No docstring. (line 49)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: output_dir, rewards, stem, timesteps, tmp_path
- Return payloads: None
- Curates datasets or metrics via test_curate_trajectories

### Integration Points
- External: numpy
- Internal: townlet.policy.replay.frames_to_replay_sample

### Code Quality Notes
- Missing docstrings: _write_sample, test_curate_trajectories

## `tests/test_embedding_allocator.py`

**Purpose**: No module docstring provided.
**Lines of code**: 142
**Dependencies**: stdlib=pathlib.Path; external=None; internal=townlet.config.load_config, townlet.observations.builder.ObservationBuilder, townlet.observations.embedding.EmbeddingAllocator, townlet.stability.monitor.StabilityMonitor, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.observations.builder.ObservationBuilder, townlet.observations.embedding.EmbeddingAllocator, townlet.stability.monitor.StabilityMonitor, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `make_allocator(*, cooldown: int = 5, max_slots: int = 2) -> EmbeddingAllocator` — No docstring. (line 11)
- `test_allocate_reuses_slot_after_cooldown() -> None` — No docstring. (line 19)
- `test_allocator_respects_multiple_slots() -> None` — No docstring. (line 39)
- `test_observation_builder_releases_on_termination() -> None` — No docstring. (line 59)
- `test_telemetry_exposes_allocator_metrics() -> None` — No docstring. (line 82)
- `test_stability_monitor_sets_alert_on_warning() -> None` — No docstring. (line 97)
- `test_telemetry_records_events() -> None` — No docstring. (line 110)
- `test_stability_alerts_on_affordance_failures() -> None` — No docstring. (line 129)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: cooldown, max_slots
- Return payloads: EmbeddingAllocator, None
- Builds derived structures or observations via test_observation_builder_releases_on_termination
- Records metrics or histories via test_telemetry_records_events

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.observations.builder.ObservationBuilder, townlet.observations.embedding.EmbeddingAllocator, townlet.stability.monitor.StabilityMonitor, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: make_allocator, test_allocate_reuses_slot_after_cooldown, test_allocator_respects_multiple_slots, test_observation_builder_releases_on_termination, test_stability_alerts_on_affordance_failures, test_stability_monitor_sets_alert_on_warning, test_telemetry_exposes_allocator_metrics, test_telemetry_records_events

## `tests/test_employment_loop.py`

**Purpose**: No module docstring provided.
**Lines of code**: 120
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `make_loop_with_employment() -> SimulationLoop` — No docstring. (line 10)
- `advance_ticks(loop: SimulationLoop, ticks: int) -> None` — No docstring. (line 41)
- `test_on_time_shift_records_attendance() -> None` — No docstring. (line 46)
- `test_late_arrival_accumulates_wages_withheld() -> None` — No docstring. (line 64)
- `test_employment_exit_queue_respects_cap_and_manual_override() -> None` — No docstring. (line 82)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: loop, ticks
- Return payloads: None, SimulationLoop
- Advances tick or scheduler timelines via advance_ticks
- Records metrics or histories via test_on_time_shift_records_attendance

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: advance_ticks, make_loop_with_employment, test_employment_exit_queue_respects_cap_and_manual_override, test_late_arrival_accumulates_wages_withheld, test_on_time_shift_records_attendance

## `tests/test_lifecycle_manager.py`

**Purpose**: No module docstring provided.
**Lines of code**: 89
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=None; internal=townlet.config.load_config, townlet.lifecycle.manager.LifecycleManager, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.lifecycle.manager.LifecycleManager, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_make_world(respawn_delay: int = 0) -> tuple[LifecycleManager, WorldState]` — No docstring. (line 10)
- `_spawn_agent(world: WorldState, agent_id: str = 'alice') -> AgentSnapshot` — No docstring. (line 20)
- `test_respawn_after_delay() -> None` — No docstring. (line 33)
- `test_employment_exit_emits_event_and_resets_state() -> None` — No docstring. (line 53)
- `test_employment_daily_reset() -> None` — No docstring. (line 70)
- `test_termination_reasons_captured() -> None` — No docstring. (line 79)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, respawn_delay, world
- Return payloads: AgentSnapshot, None, tuple[LifecycleManager, WorldState]
- Captures trajectories or telemetry snapshots via test_termination_reasons_captured
- Resets runtime state via test_employment_daily_reset, test_employment_exit_emits_event_and_resets_state

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.lifecycle.manager.LifecycleManager, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _make_world, _spawn_agent, test_employment_daily_reset, test_employment_exit_emits_event_and_resets_state, test_respawn_after_delay, test_termination_reasons_captured

## `tests/test_need_decay.py`

**Purpose**: No module docstring provided.
**Lines of code**: 89
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.lifecycle.manager.LifecycleManager, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.lifecycle.manager.LifecycleManager, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_make_world() -> tuple[LifecycleManager, WorldState]` — No docstring. (line 14)
- `_spawn_agent(world: WorldState, *, hunger: float = 0.8, hygiene: float = 0.7, energy: float = 0.6) -> AgentSnapshot` — No docstring. (line 23)
- `test_need_decay_matches_config() -> None` — No docstring. (line 42)
- `test_need_decay_clamps_at_zero() -> None` — No docstring. (line 55)
- `test_lifecycle_hunger_threshold_applies() -> None` — No docstring. (line 66)
- `test_agent_snapshot_clamps_on_init() -> None` — No docstring. (line 79)

### Constants and Configuration
- `CONFIG_PATH` = Path('configs/examples/poc_hybrid.yaml') (line 11)

### Data Flow
- Primary inputs: energy, hunger, hygiene, world
- Return payloads: AgentSnapshot, None, tuple[LifecycleManager, WorldState]
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.lifecycle.manager.LifecycleManager, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _make_world, _spawn_agent, test_agent_snapshot_clamps_on_init, test_lifecycle_hunger_threshold_applies, test_need_decay_clamps_at_zero, test_need_decay_matches_config

## `tests/test_observation_builder.py`

**Purpose**: No module docstring provided.
**Lines of code**: 194
**Dependencies**: stdlib=pathlib.Path; external=numpy; internal=townlet.config.load_config, townlet.console.command.ConsoleCommandEnvelope, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.console.command.ConsoleCommandEnvelope, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `make_world(enforce_job_loop: bool = False) -> SimulationLoop` — No docstring. (line 12)
- `test_observation_builder_hybrid_map_and_features() -> None` — No docstring. (line 40)
- `test_observation_ctx_reset_releases_slot() -> None` — No docstring. (line 88)
- `test_observation_rivalry_features_reflect_conflict() -> None` — No docstring. (line 102)
- `test_observation_queue_and_reservation_flags() -> None` — No docstring. (line 114)
- `test_observation_respawn_resets_features() -> None` — No docstring. (line 137)
- `test_ctx_reset_flag_on_teleport_and_possession() -> None` — No docstring. (line 162)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: enforce_job_loop
- Return payloads: None, SimulationLoop
- Builds derived structures or observations via test_observation_builder_hybrid_map_and_features
- Resets runtime state via test_ctx_reset_flag_on_teleport_and_possession, test_observation_ctx_reset_releases_slot, test_observation_respawn_resets_features

### Integration Points
- External: numpy
- Internal: townlet.config.load_config, townlet.console.command.ConsoleCommandEnvelope, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: make_world, test_ctx_reset_flag_on_teleport_and_possession, test_observation_builder_hybrid_map_and_features, test_observation_ctx_reset_releases_slot, test_observation_queue_and_reservation_flags, test_observation_respawn_resets_features, test_observation_rivalry_features_reflect_conflict

## `tests/test_observation_builder_compact.py`

**Purpose**: No module docstring provided.
**Lines of code**: 63
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=numpy; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `make_compact_world() -> SimulationLoop` — No docstring. (line 13)
- `test_compact_observation_features_only() -> None` — No docstring. (line 30)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, SimulationLoop
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: numpy
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: make_compact_world, test_compact_observation_features_only

## `tests/test_observation_builder_full.py`

**Purpose**: No module docstring provided.
**Lines of code**: 83
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=numpy; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `make_full_world() -> SimulationLoop` — No docstring. (line 13)
- `test_full_observation_map_and_features() -> None` — No docstring. (line 40)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, SimulationLoop
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: numpy
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: make_full_world, test_full_observation_map_and_features

## `tests/test_observations_social_snippet.py`

**Purpose**: No module docstring provided.
**Lines of code**: 95
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=numpy, pytest; internal=townlet.config.SimulationConfig, townlet.config.load_config, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.SimulationConfig, townlet.config.load_config, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `base_config() -> SimulationConfig` — No docstring. (line 14)
- `_build_world(config: SimulationConfig) -> WorldState` — No docstring. (line 18)
- `test_social_snippet_vector_length(base_config: SimulationConfig) -> None` — No docstring. (line 38)
- `test_relationship_stage_required(base_config: SimulationConfig) -> None` — No docstring. (line 58)
- `test_disable_aggregates_via_config(base_config: SimulationConfig) -> None` — No docstring. (line 66)
- `test_observation_matches_golden_fixture(base_config: SimulationConfig) -> None` — No docstring. (line 84)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: base_config, config
- Return payloads: None, SimulationConfig, WorldState
- Builds derived structures or observations via _build_world

### Integration Points
- External: numpy, pytest
- Internal: townlet.config.SimulationConfig, townlet.config.load_config, townlet.observations.builder.ObservationBuilder, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _build_world, base_config, test_disable_aggregates_via_config, test_observation_matches_golden_fixture, test_relationship_stage_required, test_social_snippet_vector_length

## `tests/test_observer_payload.py`

**Purpose**: No module docstring provided.
**Lines of code**: 53
**Dependencies**: stdlib=pathlib.Path; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring. (line 9)
- `test_observer_payload_contains_job_and_economy() -> None` — No docstring. (line 23)
- `test_planning_payload_consistency() -> None` — No docstring. (line 38)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, SimulationLoop
- Loads configuration or datasets from disk via test_observer_payload_contains_job_and_economy, test_planning_payload_consistency

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: make_loop, test_observer_payload_contains_job_and_economy, test_planning_payload_consistency

## `tests/test_observer_ui_dashboard.py`

**Purpose**: No module docstring provided.
**Lines of code**: 280
**Dependencies**: stdlib=dataclasses.replace, pathlib.Path; external=pytest, rich.console.Console; internal=townlet.config.load_config, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.policy.models.torch_available, townlet.world.grid.AgentSnapshot, townlet_ui.dashboard._build_map_panel, townlet_ui.dashboard._derive_promotion_reason, townlet_ui.dashboard._promotion_border_style, townlet_ui.dashboard.render_snapshot, townlet_ui.dashboard.run_dashboard, townlet_ui.telemetry.AnnealStatus, townlet_ui.telemetry.PromotionSnapshot, townlet_ui.telemetry.TelemetryClient
**Related modules**: townlet.config.load_config, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.policy.models.torch_available, townlet.world.grid.AgentSnapshot, townlet_ui.dashboard._build_map_panel, townlet_ui.dashboard._derive_promotion_reason, townlet_ui.dashboard._promotion_border_style, townlet_ui.dashboard.render_snapshot, townlet_ui.dashboard.run_dashboard, townlet_ui.telemetry.AnnealStatus, townlet_ui.telemetry.PromotionSnapshot, townlet_ui.telemetry.TelemetryClient

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring. (line 15)
- `test_render_snapshot_produces_panels() -> None` — No docstring. (line 39)
- `test_run_dashboard_advances_loop(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring. (line 73)
- `test_build_map_panel_produces_table() -> None` — No docstring. (line 85)
- `test_narration_panel_shows_styled_categories() -> None` — No docstring. (line 97)
- `test_policy_inspector_snapshot_contains_entries() -> None` — No docstring. (line 184)
- `test_promotion_reason_logic() -> None` — No docstring. (line 197)
- `test_promotion_border_styles() -> None` — No docstring. (line 262)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: monkeypatch
- Return payloads: None, SimulationLoop
- Builds derived structures or observations via test_build_map_panel_produces_table

### Integration Points
- External: pytest, rich.console.Console
- Internal: townlet.config.load_config, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.policy.models.torch_available, townlet.world.grid.AgentSnapshot, townlet_ui.dashboard._build_map_panel, townlet_ui.dashboard._derive_promotion_reason, townlet_ui.dashboard._promotion_border_style, townlet_ui.dashboard.render_snapshot, townlet_ui.dashboard.run_dashboard, townlet_ui.telemetry.AnnealStatus, townlet_ui.telemetry.PromotionSnapshot, townlet_ui.telemetry.TelemetryClient

### Code Quality Notes
- Missing docstrings: make_loop, test_build_map_panel_produces_table, test_narration_panel_shows_styled_categories, test_policy_inspector_snapshot_contains_entries, test_promotion_border_styles, test_promotion_reason_logic, test_render_snapshot_produces_panels, test_run_dashboard_advances_loop

## `tests/test_observer_ui_executor.py`

**Purpose**: No module docstring provided.
**Lines of code**: 33
**Dependencies**: stdlib=time; external=None; internal=townlet.console.handlers.ConsoleCommand, townlet_ui.commands.ConsoleCommandExecutor
**Related modules**: townlet.console.handlers.ConsoleCommand, townlet_ui.commands.ConsoleCommandExecutor

### Classes
- `DummyRouter` (bases: object; decorators: None) — No class docstring provided. (line 7)
  - Methods:
    - `__init__(self) -> None` — No docstring. (line 8)
    - `dispatch(self, command: ConsoleCommand) -> None` — No docstring. (line 11)

### Functions
- `test_console_command_executor_dispatches_async() -> None` — No docstring. (line 16)
- `test_console_command_executor_swallow_errors() -> None` — No docstring. (line 26)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: command
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.console.handlers.ConsoleCommand, townlet_ui.commands.ConsoleCommandExecutor

### Code Quality Notes
- Missing docstrings: DummyRouter.__init__, DummyRouter.dispatch, test_console_command_executor_dispatches_async, test_console_command_executor_swallow_errors

## `tests/test_observer_ui_script.py`

**Purpose**: No module docstring provided.
**Lines of code**: 22
**Dependencies**: stdlib=pathlib.Path, subprocess, sys; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `test_observer_ui_script_runs_single_tick(tmp_path: Path) -> None` — No docstring. (line 6)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Advances tick or scheduler timelines via test_observer_ui_script_runs_single_tick

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: test_observer_ui_script_runs_single_tick

## `tests/test_perturbation_config.py`

**Purpose**: No module docstring provided.
**Lines of code**: 38
**Dependencies**: stdlib=pathlib.Path; external=None; internal=townlet.config.PerturbationKind, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.SimulationConfig, townlet.config.load_config
**Related modules**: townlet.config.PerturbationKind, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.SimulationConfig, townlet.config.load_config

### Classes
- None

### Functions
- `test_simulation_config_exposes_perturbations() -> None` — No docstring. (line 12)
- `test_price_spike_event_config_parses_ranges() -> None` — No docstring. (line 22)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.PerturbationKind, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.SimulationConfig, townlet.config.load_config

### Code Quality Notes
- Missing docstrings: test_price_spike_event_config_parses_ranges, test_simulation_config_exposes_perturbations

## `tests/test_perturbation_scheduler.py`

**Purpose**: No module docstring provided.
**Lines of code**: 106
**Dependencies**: stdlib=pathlib.Path; external=None; internal=townlet.config.ArrangedMeetEventConfig, townlet.config.FloatRange, townlet.config.IntRange, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.SimulationConfig, townlet.config.load_config, townlet.scheduler.perturbations.PerturbationScheduler, townlet.world.grid.WorldState
**Related modules**: townlet.config.ArrangedMeetEventConfig, townlet.config.FloatRange, townlet.config.IntRange, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.SimulationConfig, townlet.config.load_config, townlet.scheduler.perturbations.PerturbationScheduler, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_base_config() -> SimulationConfig` — No docstring. (line 16)
- `test_manual_event_activation_and_expiry() -> None` — No docstring. (line 48)
- `test_auto_scheduling_respects_cooldowns() -> None` — No docstring. (line 75)
- `test_cancel_event_removes_from_active() -> None` — No docstring. (line 96)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, SimulationConfig
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.ArrangedMeetEventConfig, townlet.config.FloatRange, townlet.config.IntRange, townlet.config.PerturbationSchedulerConfig, townlet.config.PriceSpikeEventConfig, townlet.config.SimulationConfig, townlet.config.load_config, townlet.scheduler.perturbations.PerturbationScheduler, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _base_config, test_auto_scheduling_respects_cooldowns, test_cancel_event_removes_from_active, test_manual_event_activation_and_expiry

## `tests/test_policy_anneal_blend.py`

**Purpose**: No module docstring provided.
**Lines of code**: 155
**Dependencies**: stdlib=pathlib.Path; external=None; internal=townlet.config.load_config, townlet.policy.behavior.AgentIntent, townlet.policy.runner.PolicyRuntime, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.policy.behavior.AgentIntent, townlet.policy.runner.PolicyRuntime, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_make_world(option_commit_ticks: int | None = None) -> tuple[PolicyRuntime, WorldState]` — No docstring. (line 9)
- `test_anneal_ratio_uses_provider_when_enabled() -> None` — No docstring. (line 24)
- `test_anneal_ratio_mix_respects_probability() -> None` — No docstring. (line 41)
- `test_blend_disabled_returns_scripted() -> None` — No docstring. (line 64)
- `test_option_commit_blocks_switch_until_expiry() -> None` — No docstring. (line 77)
- `test_option_commit_clears_on_termination() -> None` — No docstring. (line 128)
- `test_option_commit_respects_disabled_setting() -> None` — No docstring. (line 143)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: option_commit_ticks
- Return payloads: None, tuple[PolicyRuntime, WorldState]
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.policy.behavior.AgentIntent, townlet.policy.runner.PolicyRuntime, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _make_world, test_anneal_ratio_mix_respects_probability, test_anneal_ratio_uses_provider_when_enabled, test_blend_disabled_returns_scripted, test_option_commit_blocks_switch_until_expiry, test_option_commit_clears_on_termination, test_option_commit_respects_disabled_setting

## `tests/test_policy_models.py`

**Purpose**: No module docstring provided.
**Lines of code**: 32
**Dependencies**: stdlib=None; external=pytest, torch; internal=townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.ConflictAwarePolicyNetwork, townlet.policy.models.TorchNotAvailableError, townlet.policy.models.torch_available
**Related modules**: townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.ConflictAwarePolicyNetwork, townlet.policy.models.TorchNotAvailableError, townlet.policy.models.torch_available

### Classes
- None

### Functions
- `test_conflict_policy_network_requires_torch_when_unavailable() -> None` — No docstring. (line 11)
- `test_conflict_policy_network_forward() -> None` — No docstring. (line 20)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest, torch
- Internal: townlet.policy.models.ConflictAwarePolicyConfig, townlet.policy.models.ConflictAwarePolicyNetwork, townlet.policy.models.TorchNotAvailableError, townlet.policy.models.torch_available

### Code Quality Notes
- Missing docstrings: test_conflict_policy_network_forward, test_conflict_policy_network_requires_torch_when_unavailable

## `tests/test_policy_rivalry_behavior.py`

**Purpose**: No module docstring provided.
**Lines of code**: 67
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=pytest; internal=townlet.config.loader.load_config, townlet.policy.behavior.ScriptedBehavior, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.loader.load_config, townlet.policy.behavior.ScriptedBehavior, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `base_config()` — No docstring. (line 13)
- `_build_world(base_config)` — No docstring. (line 17)
- `_occupy(world: WorldState, object_id: str, agent_id: str) -> None` — No docstring. (line 41)
- `test_agents_avoid_rivals_when_rivalry_high(base_config)` — No docstring. (line 45)
- `test_agents_request_again_after_rivalry_decay(base_config)` — No docstring. (line 56)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, base_config, object_id, world
- Return payloads: None
- Builds derived structures or observations via _build_world

### Integration Points
- External: pytest
- Internal: townlet.config.loader.load_config, townlet.policy.behavior.ScriptedBehavior, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _build_world, _occupy, base_config, test_agents_avoid_rivals_when_rivalry_high, test_agents_request_again_after_rivalry_decay

## `tests/test_ppo_utils.py`

**Purpose**: No module docstring provided.
**Lines of code**: 65
**Dependencies**: stdlib=__future__.annotations; external=torch; internal=townlet.policy.ppo.utils
**Related modules**: townlet.policy.ppo.utils

### Classes
- None

### Functions
- `test_compute_gae_single_step() -> None` — No docstring. (line 8)
- `test_value_baseline_from_old_preds_handles_bootstrap() -> None` — No docstring. (line 23)
- `test_policy_surrogate_clipping_behaviour() -> None` — No docstring. (line 33)
- `test_clipped_value_loss_respects_clip() -> None` — No docstring. (line 47)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Computes metrics or rewards via test_compute_gae_single_step

### Integration Points
- External: torch
- Internal: townlet.policy.ppo.utils

### Code Quality Notes
- Missing docstrings: test_clipped_value_loss_respects_clip, test_compute_gae_single_step, test_policy_surrogate_clipping_behaviour, test_value_baseline_from_old_preds_handles_bootstrap

## `tests/test_promotion_cli.py`

**Purpose**: No module docstring provided.
**Lines of code**: 52
**Dependencies**: stdlib=json, pathlib.Path, subprocess, sys; external=pytest; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `write_summary(tmp_path: Path, accuracy: float, threshold: float = 0.9) -> Path` — No docstring. (line 12)
- `test_promotion_cli_pass(tmp_path: Path) -> None` — No docstring. (line 26)
- `test_promotion_cli_fail(tmp_path: Path) -> None` — No docstring. (line 34)
- `test_promotion_drill(tmp_path: Path) -> None` — No docstring. (line 42)

### Constants and Configuration
- `PYTHON` = Path(sys.executable) (line 8)
- `SCRIPT` = Path('scripts/promotion_evaluate.py') (line 9)

### Data Flow
- Primary inputs: accuracy, threshold, tmp_path
- Return payloads: None, Path
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: None

### Code Quality Notes
- Missing docstrings: test_promotion_cli_fail, test_promotion_cli_pass, test_promotion_drill, write_summary

## `tests/test_promotion_evaluate_cli.py`

**Purpose**: No module docstring provided.
**Lines of code**: 84
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path, subprocess, sys; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `_run(*args: str) -> subprocess.CompletedProcess[str]` — No docstring. (line 11)
- `test_promotion_evaluate_promote(tmp_path: Path) -> None` — No docstring. (line 16)
- `test_promotion_evaluate_hold_flags(tmp_path: Path) -> None` — No docstring. (line 40)
- `test_promotion_evaluate_dry_run(tmp_path: Path) -> None` — No docstring. (line 64)

### Constants and Configuration
- `SCRIPT` = Path('scripts/promotion_evaluate.py').resolve() (line 8)

### Data Flow
- Primary inputs: args, tmp_path
- Return payloads: None, subprocess.CompletedProcess[str]
- Evaluates conditions or invariants via test_promotion_evaluate_dry_run, test_promotion_evaluate_hold_flags, test_promotion_evaluate_promote
- Promotes builds or policies via test_promotion_evaluate_promote

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: _run, test_promotion_evaluate_dry_run, test_promotion_evaluate_hold_flags, test_promotion_evaluate_promote

## `tests/test_promotion_manager.py`

**Purpose**: No module docstring provided.
**Lines of code**: 110
**Dependencies**: stdlib=json, pathlib.Path; external=None; internal=townlet.config.load_config, townlet.stability.promotion.PromotionManager
**Related modules**: townlet.config.load_config, townlet.stability.promotion.PromotionManager

### Classes
- None

### Functions
- `make_manager(log_path: Path | None = None) -> PromotionManager` — No docstring. (line 8)
- `promotion_metrics(pass_streak: int, required: int, ready: bool, last_result: str | None = None, last_tick: int | None = None) -> dict[str, object]` — No docstring. (line 15)
- `test_promotion_state_transitions() -> None` — No docstring. (line 34)
- `test_promotion_manager_export_import() -> None` — No docstring. (line 52)
- `test_mark_promoted_and_rollback() -> None` — No docstring. (line 73)
- `test_rollback_without_metadata_reverts_to_initial() -> None` — No docstring. (line 92)
- `test_promotion_log_written(tmp_path: Path) -> None` — No docstring. (line 100)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: last_result, last_tick, log_path, pass_streak, ready, required, tmp_path
- Return payloads: None, PromotionManager, dict[str, object]
- Exports payloads for downstream consumers via test_promotion_manager_export_import
- Promotes builds or policies via test_mark_promoted_and_rollback

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.stability.promotion.PromotionManager

### Code Quality Notes
- Missing docstrings: make_manager, promotion_metrics, test_mark_promoted_and_rollback, test_promotion_log_written, test_promotion_manager_export_import, test_promotion_state_transitions, test_rollback_without_metadata_reverts_to_initial

## `tests/test_queue_fairness.py`

**Purpose**: No module docstring provided.
**Lines of code**: 89
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.world.queue_manager.QueueManager
**Related modules**: townlet.config.load_config, townlet.world.queue_manager.QueueManager

### Classes
- None

### Functions
- `_make_queue_manager() -> QueueManager` — No docstring. (line 11)
- `test_cooldown_blocks_repeat_entry_and_tracks_metric() -> None` — No docstring. (line 16)
- `test_ghost_step_promotes_waiter_after_blockages(ghost_limit: int) -> None` — No docstring. (line 38)
- `test_queue_snapshot_reflects_waiting_order() -> None` — No docstring. (line 61)
- `test_queue_performance_metrics_accumulate_time() -> None` — No docstring. (line 79)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: ghost_limit
- Return payloads: None, QueueManager
- Promotes builds or policies via test_ghost_step_promotes_waiter_after_blockages

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.world.queue_manager.QueueManager

### Code Quality Notes
- Missing docstrings: _make_queue_manager, test_cooldown_blocks_repeat_entry_and_tracks_metric, test_ghost_step_promotes_waiter_after_blockages, test_queue_performance_metrics_accumulate_time, test_queue_snapshot_reflects_waiting_order

## `tests/test_queue_manager.py`

**Purpose**: No module docstring provided.
**Lines of code**: 92
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.world.queue_manager.QueueManager
**Related modules**: townlet.config.load_config, townlet.world.queue_manager.QueueManager

### Classes
- None

### Functions
- `queue_manager() -> QueueManager` — No docstring. (line 10)
- `test_queue_cooldown_enforced(queue_manager: QueueManager) -> None` — No docstring. (line 16)
- `test_queue_prioritises_wait_time(queue_manager: QueueManager) -> None` — No docstring. (line 26)
- `test_ghost_step_trigger(queue_manager: QueueManager) -> None` — No docstring. (line 43)
- `test_requeue_to_tail_rotates_agent(queue_manager: QueueManager) -> None` — No docstring. (line 57)
- `test_record_blocked_attempt_counts_and_triggers(queue_manager: QueueManager) -> None` — No docstring. (line 79)
- `test_cooldown_expiration_clears_entries(queue_manager: QueueManager) -> None` — No docstring. (line 86)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: queue_manager
- Return payloads: None, QueueManager
- Records metrics or histories via test_record_blocked_attempt_counts_and_triggers

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.world.queue_manager.QueueManager

### Code Quality Notes
- Missing docstrings: queue_manager, test_cooldown_expiration_clears_entries, test_ghost_step_trigger, test_queue_cooldown_enforced, test_queue_prioritises_wait_time, test_record_blocked_attempt_counts_and_triggers, test_requeue_to_tail_rotates_agent

## `tests/test_queue_metrics.py`

**Purpose**: No module docstring provided.
**Lines of code**: 63
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=None; internal=townlet.config.load_config, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring. (line 9)
- `test_queue_metrics_capture_ghost_step_and_rotation() -> None` — No docstring. (line 17)
- `test_nightly_reset_preserves_queue_metrics() -> None` — No docstring. (line 49)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, WorldState
- Captures trajectories or telemetry snapshots via test_queue_metrics_capture_ghost_step_and_rotation
- Resets runtime state via test_nightly_reset_preserves_queue_metrics

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _make_world, test_nightly_reset_preserves_queue_metrics, test_queue_metrics_capture_ghost_step_and_rotation

## `tests/test_queue_resume.py`

**Purpose**: No module docstring provided.
**Lines of code**: 55
**Dependencies**: stdlib=__future__.annotations, pathlib.Path, random; external=pytest; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `base_config()` — No docstring. (line 14)
- `_setup_loop(config) -> SimulationLoop` — No docstring. (line 21)
- `test_queue_metrics_resume(tmp_path: Path, base_config) -> None` — No docstring. (line 36)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: base_config, config, tmp_path
- Return payloads: None, SimulationLoop
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: _setup_loop, base_config, test_queue_metrics_resume

## `tests/test_relationship_integration.py`

**Purpose**: No module docstring provided.
**Lines of code**: 66
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=pytest; internal=townlet.agents.models.Personality, townlet.config.SimulationConfig, townlet.config.load_config, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.agents.models.Personality, townlet.config.SimulationConfig, townlet.config.load_config, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `base_config() -> SimulationConfig` — No docstring. (line 13)
- `_with_relationship_modifiers(config: SimulationConfig, enabled: bool) -> SimulationConfig` — No docstring. (line 17)
- `_build_world(config: SimulationConfig) -> WorldState` — No docstring. (line 25)
- `_familiarity(world: WorldState, owner: str, other: str) -> float` — No docstring. (line 44)
- `test_chat_success_personality_bonus_applied(base_config: SimulationConfig) -> None` — No docstring. (line 49)
- `test_chat_success_parity_when_disabled(base_config: SimulationConfig) -> None` — No docstring. (line 59)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: base_config, config, enabled, other, owner, world
- Return payloads: None, SimulationConfig, WorldState, float
- Builds derived structures or observations via _build_world

### Integration Points
- External: pytest
- Internal: townlet.agents.models.Personality, townlet.config.SimulationConfig, townlet.config.load_config, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _build_world, _familiarity, _with_relationship_modifiers, base_config, test_chat_success_parity_when_disabled, test_chat_success_personality_bonus_applied

## `tests/test_relationship_ledger.py`

**Purpose**: No module docstring provided.
**Lines of code**: 64
**Dependencies**: stdlib=__future__.annotations; external=None; internal=townlet.world.relationships.RelationshipLedger, townlet.world.relationships.RelationshipParameters
**Related modules**: townlet.world.relationships.RelationshipLedger, townlet.world.relationships.RelationshipParameters

### Classes
- None

### Functions
- `test_apply_delta_clamps_and_prunes() -> None` — No docstring. (line 6)
- `test_decay_removes_zero_ties() -> None` — No docstring. (line 19)
- `test_eviction_hook_invoked_for_capacity() -> None` — No docstring. (line 31)
- `test_eviction_hook_invoked_for_decay() -> None` — No docstring. (line 48)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Applies world or agent state updates via test_apply_delta_clamps_and_prunes

### Integration Points
- External: None
- Internal: townlet.world.relationships.RelationshipLedger, townlet.world.relationships.RelationshipParameters

### Code Quality Notes
- Missing docstrings: test_apply_delta_clamps_and_prunes, test_decay_removes_zero_ties, test_eviction_hook_invoked_for_capacity, test_eviction_hook_invoked_for_decay

## `tests/test_relationship_metrics.py`

**Purpose**: No module docstring provided.
**Lines of code**: 308
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.telemetry.relationship_metrics.RelationshipChurnAccumulator, townlet.telemetry.relationship_metrics.RelationshipEvictionSample, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.telemetry.relationship_metrics.RelationshipChurnAccumulator, townlet.telemetry.relationship_metrics.RelationshipEvictionSample, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `test_record_eviction_tracks_counts() -> None` — No docstring. (line 15)
- `test_window_rolls_and_history_records_samples() -> None` — No docstring. (line 25)
- `test_latest_payload_round_trips_via_ingest() -> None` — No docstring. (line 48)
- `test_invalid_configuration_raises() -> None` — No docstring. (line 65)
- `test_world_relationship_metrics_records_evictions() -> None` — No docstring. (line 73)
- `test_world_relationship_update_symmetry() -> None` — No docstring. (line 86)
- `test_queue_events_modify_relationships() -> None` — No docstring. (line 97)
- `test_shared_meal_updates_relationship() -> None` — No docstring. (line 136)
- `test_absence_triggers_took_my_shift_relationships() -> None` — No docstring. (line 170)
- `test_late_help_creates_positive_relationship() -> None` — No docstring. (line 212)
- `test_chat_outcomes_adjust_relationships() -> None` — No docstring. (line 254)
- `test_relationship_tie_helper_returns_current_values() -> None` — No docstring. (line 276)
- `test_consume_chat_events_is_single_use() -> None` — No docstring. (line 287)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Ingests external commands or payloads via test_latest_payload_round_trips_via_ingest
- Loads configuration or datasets from disk via test_latest_payload_round_trips_via_ingest
- Records metrics or histories via test_record_eviction_tracks_counts, test_window_rolls_and_history_records_samples, test_world_relationship_metrics_records_evictions
- Updates internal caches or trackers via test_shared_meal_updates_relationship, test_world_relationship_update_symmetry

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.telemetry.relationship_metrics.RelationshipChurnAccumulator, townlet.telemetry.relationship_metrics.RelationshipEvictionSample, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: test_absence_triggers_took_my_shift_relationships, test_chat_outcomes_adjust_relationships, test_consume_chat_events_is_single_use, test_invalid_configuration_raises, test_late_help_creates_positive_relationship, test_latest_payload_round_trips_via_ingest, test_queue_events_modify_relationships, test_record_eviction_tracks_counts, test_relationship_tie_helper_returns_current_values, test_shared_meal_updates_relationship, test_window_rolls_and_history_records_samples, test_world_relationship_metrics_records_evictions, test_world_relationship_update_symmetry

## `tests/test_relationship_personality_modifiers.py`

**Purpose**: No module docstring provided.
**Lines of code**: 67
**Dependencies**: stdlib=__future__.annotations; external=pytest; internal=townlet.agents.Personality, townlet.agents.RelationshipDelta, townlet.agents.apply_personality_modifiers
**Related modules**: townlet.agents.Personality, townlet.agents.RelationshipDelta, townlet.agents.apply_personality_modifiers

### Classes
- None

### Functions
- `test_modifiers_disabled_returns_baseline() -> None` — No docstring. (line 8)
- `test_forgiveness_scales_negative_values() -> None` — No docstring. (line 20)
- `test_extroversion_adds_chat_bonus() -> None` — No docstring. (line 34)
- `test_ambition_scales_conflict_rivalry() -> None` — No docstring. (line 46)
- `test_unforgiving_agent_intensifies_negative_hits() -> None` — No docstring. (line 58)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: townlet.agents.Personality, townlet.agents.RelationshipDelta, townlet.agents.apply_personality_modifiers

### Code Quality Notes
- Missing docstrings: test_ambition_scales_conflict_rivalry, test_extroversion_adds_chat_bonus, test_forgiveness_scales_negative_values, test_modifiers_disabled_returns_baseline, test_unforgiving_agent_intensifies_negative_hits

## `tests/test_reward_engine.py`

**Purpose**: No module docstring provided.
**Lines of code**: 261
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.rewards.engine.RewardEngine, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.rewards.engine.RewardEngine, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- `StubSnapshot` (bases: object; decorators: None) — No class docstring provided. (line 10)
  - Methods:
    - `__init__(self, needs: dict[str, float], wallet: float) -> None` — No docstring. (line 11)
- `StubWorld` (bases: object; decorators: None) — No class docstring provided. (line 16)
  - Methods:
    - `__init__(self, config, snapshot: StubSnapshot, context: dict[str, float]) -> None` — No docstring. (line 17)
    - `consume_chat_events(self)` — No docstring. (line 28)
    - `agent_context(self, agent_id: str) -> dict[str, float]` — No docstring. (line 31)
    - `relationship_tie(self, subject: str, target: str)` — No docstring. (line 34)
    - `rivalry_top(self, agent_id: str, limit: int)` — No docstring. (line 37)

### Functions
- `_make_world(hunger: float = 0.5) -> WorldState` — No docstring. (line 41)
- `test_reward_negative_with_high_deficit() -> None` — No docstring. (line 53)
- `test_reward_clipped_by_config() -> None` — No docstring. (line 59)
- `test_survival_tick_positive_when_balanced() -> None` — No docstring. (line 66)
- `test_chat_reward_applied_for_successful_conversation() -> None` — No docstring. (line 81)
- `test_chat_reward_skipped_when_needs_override_triggers() -> None` — No docstring. (line 109)
- `test_chat_reward_blocked_within_termination_window() -> None` — No docstring. (line 135)
- `test_episode_clip_enforced() -> None` — No docstring. (line 164)
- `test_wage_and_punctuality_bonus() -> None` — No docstring. (line 181)
- `test_terminal_penalty_applied_for_faint() -> None` — No docstring. (line 217)
- `test_terminal_penalty_applied_for_eviction() -> None` — No docstring. (line 240)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, config, context, hunger, limit, needs, snapshot, subject, target, wallet
- Return payloads: None, WorldState, dict[str, float]
- Advances tick or scheduler timelines via test_survival_tick_positive_when_balanced

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.rewards.engine.RewardEngine, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: StubSnapshot.__init__, StubWorld.__init__, StubWorld.agent_context, StubWorld.consume_chat_events, StubWorld.relationship_tie, StubWorld.rivalry_top, _make_world, test_chat_reward_applied_for_successful_conversation, test_chat_reward_blocked_within_termination_window, test_chat_reward_skipped_when_needs_override_triggers, test_episode_clip_enforced, test_reward_clipped_by_config, test_reward_negative_with_high_deficit, test_survival_tick_positive_when_balanced, test_terminal_penalty_applied_for_eviction, test_terminal_penalty_applied_for_faint, test_wage_and_punctuality_bonus

## `tests/test_reward_summary.py`

**Purpose**: No module docstring provided.
**Lines of code**: 49
**Dependencies**: stdlib=json, pathlib.Path; external=None; internal=scripts.reward_summary.ComponentStats, scripts.reward_summary.RewardAggregator, scripts.reward_summary.collect_statistics, scripts.reward_summary.render_text
**Related modules**: scripts.reward_summary.ComponentStats, scripts.reward_summary.RewardAggregator, scripts.reward_summary.collect_statistics, scripts.reward_summary.render_text

### Classes
- None

### Functions
- `test_component_stats_mean_and_extremes() -> None` — No docstring. (line 8)
- `test_reward_aggregator_tracks_components(tmp_path: Path) -> None` — No docstring. (line 19)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: scripts.reward_summary.ComponentStats, scripts.reward_summary.RewardAggregator, scripts.reward_summary.collect_statistics, scripts.reward_summary.render_text

### Code Quality Notes
- Missing docstrings: test_component_stats_mean_and_extremes, test_reward_aggregator_tracks_components

## `tests/test_rivalry_ledger.py`

**Purpose**: No module docstring provided.
**Lines of code**: 38
**Dependencies**: stdlib=None; external=pytest; internal=townlet.world.rivalry.RivalryLedger, townlet.world.rivalry.RivalryParameters
**Related modules**: townlet.world.rivalry.RivalryLedger, townlet.world.rivalry.RivalryParameters

### Classes
- None

### Functions
- `test_increment_and_clamp_and_eviction() -> None` — No docstring. (line 6)
- `test_decay_and_eviction_threshold() -> None` — No docstring. (line 20)
- `test_should_avoid_toggle() -> None` — No docstring. (line 32)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: townlet.world.rivalry.RivalryLedger, townlet.world.rivalry.RivalryParameters

### Code Quality Notes
- Missing docstrings: test_decay_and_eviction_threshold, test_increment_and_clamp_and_eviction, test_should_avoid_toggle

## `tests/test_rivalry_state.py`

**Purpose**: No module docstring provided.
**Lines of code**: 43
**Dependencies**: stdlib=__future__.annotations; external=None; internal=townlet.world.rivalry.RivalryLedger, townlet.world.rivalry.RivalryParameters
**Related modules**: townlet.world.rivalry.RivalryLedger, townlet.world.rivalry.RivalryParameters

### Classes
- None

### Functions
- `test_apply_conflict_clamps_to_max() -> None` — No docstring. (line 6)
- `test_decay_evicts_low_scores() -> None` — No docstring. (line 17)
- `test_should_avoid_threshold() -> None` — No docstring. (line 26)
- `test_encode_features_fixed_width() -> None` — No docstring. (line 35)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Applies world or agent state updates via test_apply_conflict_clamps_to_max

### Integration Points
- External: None
- Internal: townlet.world.rivalry.RivalryLedger, townlet.world.rivalry.RivalryParameters

### Code Quality Notes
- Missing docstrings: test_apply_conflict_clamps_to_max, test_decay_evicts_low_scores, test_encode_features_fixed_width, test_should_avoid_threshold

## `tests/test_rollout_buffer.py`

**Purpose**: No module docstring provided.
**Lines of code**: 85
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path; external=numpy, pytest; internal=townlet.config.load_config, townlet.policy.rollout.RolloutBuffer, townlet.policy.runner.TrainingHarness
**Related modules**: townlet.config.load_config, townlet.policy.rollout.RolloutBuffer, townlet.policy.runner.TrainingHarness

### Classes
- None

### Functions
- `_dummy_frame(agent_id: str, reward: float = 0.0, done: bool = False) -> dict[str, object]` — No docstring. (line 14)
- `test_rollout_buffer_grouping_to_samples() -> None` — No docstring. (line 28)
- `test_training_harness_capture_rollout(tmp_path: Path) -> None` — No docstring. (line 41)
- `test_rollout_buffer_empty_build_dataset_raises() -> None` — No docstring. (line 67)
- `test_rollout_buffer_single_timestep_metrics() -> None` — No docstring. (line 73)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: agent_id, done, reward, tmp_path
- Return payloads: None, dict[str, object]
- Builds derived structures or observations via test_rollout_buffer_empty_build_dataset_raises
- Captures trajectories or telemetry snapshots via test_training_harness_capture_rollout
- Trains policies or models via test_training_harness_capture_rollout

### Integration Points
- External: numpy, pytest
- Internal: townlet.config.load_config, townlet.policy.rollout.RolloutBuffer, townlet.policy.runner.TrainingHarness

### Code Quality Notes
- Missing docstrings: _dummy_frame, test_rollout_buffer_empty_build_dataset_raises, test_rollout_buffer_grouping_to_samples, test_rollout_buffer_single_timestep_metrics, test_training_harness_capture_rollout

## `tests/test_rollout_capture.py`

**Purpose**: No module docstring provided.
**Lines of code**: 109
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path, subprocess, sys; external=numpy, pytest; internal=townlet.config.load_config
**Related modules**: townlet.config.load_config

### Classes
- None

### Functions
- `test_capture_rollout_scenarios(tmp_path: Path, config_path: Path) -> None` — No docstring. (line 27)

### Constants and Configuration
- `SCENARIO_CONFIGS` = [Path('configs/scenarios/kitchen_breakfast.yaml'), Path('configs/scenarios/queue_conflict.yaml'), Path('configs/scenarios/employment_punctuality.yaml'), Path('configs/scenarios/rivalry_decay.yaml'), Path('configs/scenarios/observation_baseline.yaml')] (line 12)
- `GOLDEN_STATS_PATH` = Path('docs/samples/rollout_scenario_stats.json') (line 20)
- `GOLDEN_STATS` = json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {} (line 21)

### Data Flow
- Primary inputs: config_path, tmp_path
- Return payloads: None
- Captures trajectories or telemetry snapshots via test_capture_rollout_scenarios

### Integration Points
- External: numpy, pytest
- Internal: townlet.config.load_config

### Code Quality Notes
- Missing docstrings: test_capture_rollout_scenarios

## `tests/test_run_anneal_rehearsal.py`

**Purpose**: No module docstring provided.
**Lines of code**: 33
**Dependencies**: stdlib=importlib.util, pathlib.Path, sys; external=pytest; internal=townlet.policy.models.torch_available
**Related modules**: townlet.policy.models.torch_available

### Classes
- None

### Functions
- `test_run_anneal_rehearsal_pass(tmp_path: Path) -> None` — No docstring. (line 23)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: townlet.policy.models.torch_available

### Code Quality Notes
- Missing docstrings: test_run_anneal_rehearsal_pass

## `tests/test_scripted_behavior.py`

**Purpose**: No module docstring provided.
**Lines of code**: 85
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=numpy; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.behavior.AgentIntent, townlet.policy.behavior.BehaviorController, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.behavior.AgentIntent, townlet.policy.behavior.BehaviorController, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `test_scripted_behavior_determinism() -> None` — No docstring. (line 13)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: numpy
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.policy.behavior.AgentIntent, townlet.policy.behavior.BehaviorController, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: test_scripted_behavior_determinism

## `tests/test_sim_loop_snapshot.py`

**Purpose**: No module docstring provided.
**Lines of code**: 214
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path, random; external=pytest; internal=townlet.config.SimulationConfig, townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.snapshots.state.snapshot_from_world, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.SimulationConfig, townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.snapshots.state.snapshot_from_world, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `base_config()` — No docstring. (line 16)
- `test_simulation_loop_snapshot_round_trip(tmp_path: Path, base_config) -> None` — No docstring. (line 23)
- `test_save_snapshot_uses_config_root_and_identity_override(tmp_path: Path, base_config) -> None` — No docstring. (line 70)
- `test_simulation_resume_equivalence(tmp_path: Path, base_config) -> None` — No docstring. (line 98)
- `test_policy_transitions_resume(tmp_path: Path, base_config) -> None` — No docstring. (line 174)
- `_normalise_snapshot(snapshot: dict[str, object]) -> dict[str, object]` — No docstring. (line 201)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: base_config, snapshot, tmp_path
- Return payloads: None, dict[str, object]
- Persists state or reports to disk via test_save_snapshot_uses_config_root_and_identity_override

### Integration Points
- External: pytest
- Internal: townlet.config.SimulationConfig, townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.snapshots.state.snapshot_from_world, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: _normalise_snapshot, base_config, test_policy_transitions_resume, test_save_snapshot_uses_config_root_and_identity_override, test_simulation_loop_snapshot_round_trip, test_simulation_resume_equivalence

## `tests/test_sim_loop_structure.py`

**Purpose**: No module docstring provided.
**Lines of code**: 14
**Dependencies**: stdlib=pathlib.Path; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.core.sim_loop.TickArtifacts
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.core.sim_loop.TickArtifacts

### Classes
- None

### Functions
- `test_simulation_loop_runs_one_tick(tmp_path: Path) -> None` — No docstring. (line 7)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Advances tick or scheduler timelines via test_simulation_loop_runs_one_tick

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.core.sim_loop.TickArtifacts

### Code Quality Notes
- Missing docstrings: test_simulation_loop_runs_one_tick

## `tests/test_snapshot_manager.py`

**Purpose**: No module docstring provided.
**Lines of code**: 327
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path, random; external=pytest; internal=townlet.config.PerturbationKind, townlet.config.SimulationConfig, townlet.config.load_config, townlet.scheduler.perturbations.PerturbationScheduler, townlet.scheduler.perturbations.ScheduledPerturbation, townlet.snapshots.state.SNAPSHOT_SCHEMA_VERSION, townlet.snapshots.state.SnapshotManager, townlet.snapshots.state.SnapshotState, townlet.snapshots.state.apply_snapshot_to_telemetry, townlet.snapshots.state.apply_snapshot_to_world, townlet.snapshots.state.snapshot_from_world, townlet.telemetry.publisher.TelemetryPublisher, townlet.utils.encode_rng_state, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.PerturbationKind, townlet.config.SimulationConfig, townlet.config.load_config, townlet.scheduler.perturbations.PerturbationScheduler, townlet.scheduler.perturbations.ScheduledPerturbation, townlet.snapshots.state.SNAPSHOT_SCHEMA_VERSION, townlet.snapshots.state.SnapshotManager, townlet.snapshots.state.SnapshotState, townlet.snapshots.state.apply_snapshot_to_telemetry, townlet.snapshots.state.apply_snapshot_to_world, townlet.snapshots.state.snapshot_from_world, townlet.telemetry.publisher.TelemetryPublisher, townlet.utils.encode_rng_state, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `sample_config() -> SimulationConfig` — No docstring. (line 24)
- `test_snapshot_round_trip(tmp_path: Path, sample_config) -> None` — No docstring. (line 31)
- `test_snapshot_config_mismatch_raises(tmp_path: Path, sample_config) -> None` — No docstring. (line 120)
- `test_snapshot_missing_relationships_field_rejected(tmp_path: Path, sample_config) -> None` — No docstring. (line 128)
- `test_snapshot_schema_version_mismatch(tmp_path: Path, sample_config) -> None` — No docstring. (line 142)
- `_config_with_snapshot_updates(config: SimulationConfig, updates: dict[str, object]) -> SimulationConfig` — No docstring. (line 153)
- `test_snapshot_mismatch_allowed_when_guardrail_disabled(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring. (line 163)
- `test_snapshot_schema_downgrade_honours_allow_flag(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring. (line 179)
- `test_world_relationship_snapshot_round_trip(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring. (line 200)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config, sample_config, tmp_path, updates
- Return payloads: None, SimulationConfig
- Updates internal caches or trackers via _config_with_snapshot_updates

### Integration Points
- External: pytest
- Internal: townlet.config.PerturbationKind, townlet.config.SimulationConfig, townlet.config.load_config, townlet.scheduler.perturbations.PerturbationScheduler, townlet.scheduler.perturbations.ScheduledPerturbation, townlet.snapshots.state.SNAPSHOT_SCHEMA_VERSION, townlet.snapshots.state.SnapshotManager, townlet.snapshots.state.SnapshotState, townlet.snapshots.state.apply_snapshot_to_telemetry, townlet.snapshots.state.apply_snapshot_to_world, townlet.snapshots.state.snapshot_from_world, townlet.telemetry.publisher.TelemetryPublisher, townlet.utils.encode_rng_state, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _config_with_snapshot_updates, sample_config, test_snapshot_config_mismatch_raises, test_snapshot_mismatch_allowed_when_guardrail_disabled, test_snapshot_missing_relationships_field_rejected, test_snapshot_round_trip, test_snapshot_schema_downgrade_honours_allow_flag, test_snapshot_schema_version_mismatch, test_world_relationship_snapshot_round_trip

## `tests/test_snapshot_migrations.py`

**Purpose**: No module docstring provided.
**Lines of code**: 82
**Dependencies**: stdlib=__future__.annotations, dataclasses.replace, pathlib.Path; external=pytest; internal=townlet.config.SimulationConfig, townlet.config.load_config, townlet.snapshots.SnapshotManager, townlet.snapshots.SnapshotState, townlet.snapshots.migrations.clear_registry, townlet.snapshots.migrations.register_migration
**Related modules**: townlet.config.SimulationConfig, townlet.config.load_config, townlet.snapshots.SnapshotManager, townlet.snapshots.SnapshotState, townlet.snapshots.migrations.clear_registry, townlet.snapshots.migrations.register_migration

### Classes
- None

### Functions
- `sample_config() -> SimulationConfig` — No docstring. (line 14)
- `reset_registry() -> None` — No docstring. (line 22)
- `_basic_state(config: SimulationConfig) -> SnapshotState` — No docstring. (line 28)
- `test_snapshot_migration_applied(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring. (line 32)
- `test_snapshot_migration_multi_step(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring. (line 51)
- `test_snapshot_migration_missing_path_raises(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring. (line 74)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: config, sample_config, tmp_path
- Return payloads: None, SimulationConfig, SnapshotState
- Resets runtime state via reset_registry

### Integration Points
- External: pytest
- Internal: townlet.config.SimulationConfig, townlet.config.load_config, townlet.snapshots.SnapshotManager, townlet.snapshots.SnapshotState, townlet.snapshots.migrations.clear_registry, townlet.snapshots.migrations.register_migration

### Code Quality Notes
- Missing docstrings: _basic_state, reset_registry, sample_config, test_snapshot_migration_applied, test_snapshot_migration_missing_path_raises, test_snapshot_migration_multi_step

## `tests/test_stability_monitor.py`

**Purpose**: No module docstring provided.
**Lines of code**: 212
**Dependencies**: stdlib=pathlib.Path; external=None; internal=townlet.config.load_config, townlet.stability.monitor.StabilityMonitor
**Related modules**: townlet.config.load_config, townlet.stability.monitor.StabilityMonitor

### Classes
- None

### Functions
- `make_monitor() -> StabilityMonitor` — No docstring. (line 7)
- `_track_minimal(monitor: StabilityMonitor, *, tick: int, embedding_warning: bool = False, queue_alert: bool = False) -> None` — No docstring. (line 19)
- `test_starvation_spike_alert_triggers_after_streak() -> None` — No docstring. (line 42)
- `test_option_thrash_alert_averages_over_window() -> None` — No docstring. (line 59)
- `test_reward_variance_alert_exports_state() -> None` — No docstring. (line 76)
- `test_queue_fairness_alerts_include_metrics() -> None` — No docstring. (line 107)
- `test_rivalry_spike_alert_triggers_on_intensity() -> None` — No docstring. (line 128)
- `test_promotion_window_tracking() -> None` — No docstring. (line 147)
- `test_promotion_window_respects_allowed_alerts() -> None` — No docstring. (line 188)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: embedding_warning, monitor, queue_alert, tick
- Return payloads: None, StabilityMonitor
- Exports payloads for downstream consumers via test_reward_variance_alert_exports_state

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.stability.monitor.StabilityMonitor

### Code Quality Notes
- Missing docstrings: _track_minimal, make_monitor, test_option_thrash_alert_averages_over_window, test_promotion_window_respects_allowed_alerts, test_promotion_window_tracking, test_queue_fairness_alerts_include_metrics, test_reward_variance_alert_exports_state, test_rivalry_spike_alert_triggers_on_intensity, test_starvation_spike_alert_triggers_after_streak

## `tests/test_stability_telemetry.py`

**Purpose**: No module docstring provided.
**Lines of code**: 47
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `test_stability_alerts_exposed_via_telemetry_snapshot(tmp_path: Path) -> None` — No docstring. (line 13)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.console.handlers.ConsoleCommand, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: test_stability_alerts_exposed_via_telemetry_snapshot

## `tests/test_telemetry_client.py`

**Purpose**: No module docstring provided.
**Lines of code**: 78
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet_ui.telemetry.SchemaMismatchError, townlet_ui.telemetry.TelemetryClient
**Related modules**: townlet.config.load_config, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet_ui.telemetry.SchemaMismatchError, townlet_ui.telemetry.TelemetryClient

### Classes
- None

### Functions
- `make_simulation(enforce_job_loop: bool = True) -> SimulationLoop` — No docstring. (line 11)
- `test_telemetry_client_parses_console_snapshot() -> None` — No docstring. (line 30)
- `test_telemetry_client_warns_on_newer_schema(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring. (line 59)
- `test_telemetry_client_raises_on_major_mismatch() -> None` — No docstring. (line 74)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: enforce_job_loop, monkeypatch
- Return payloads: None, SimulationLoop
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.console.handlers.create_console_router, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet_ui.telemetry.SchemaMismatchError, townlet_ui.telemetry.TelemetryClient

### Code Quality Notes
- Missing docstrings: make_simulation, test_telemetry_client_parses_console_snapshot, test_telemetry_client_raises_on_major_mismatch, test_telemetry_client_warns_on_newer_schema

## `tests/test_telemetry_jobs.py`

**Purpose**: No module docstring provided.
**Lines of code**: 55
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.stability.monitor.StabilityMonitor, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.stability.monitor.StabilityMonitor, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `test_telemetry_captures_job_snapshot() -> None` — No docstring. (line 11)
- `test_stability_monitor_lateness_alert() -> None` — No docstring. (line 40)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Captures trajectories or telemetry snapshots via test_telemetry_captures_job_snapshot

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.stability.monitor.StabilityMonitor, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: test_stability_monitor_lateness_alert, test_telemetry_captures_job_snapshot

## `tests/test_telemetry_narration.py`

**Purpose**: No module docstring provided.
**Lines of code**: 107
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.NarrationThrottleConfig, townlet.config.load_config, townlet.telemetry.narration.NarrationRateLimiter, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState
**Related modules**: townlet.config.NarrationThrottleConfig, townlet.config.load_config, townlet.telemetry.narration.NarrationRateLimiter, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `test_narration_rate_limiter_enforces_cooldowns() -> None` — No docstring. (line 11)
- `test_narration_rate_limiter_priority_bypass() -> None` — No docstring. (line 32)
- `test_telemetry_publisher_emits_queue_conflict_narration(tmp_path: Path) -> None` — No docstring. (line 49)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Publishes telemetry or events via test_telemetry_publisher_emits_queue_conflict_narration

### Integration Points
- External: pytest
- Internal: townlet.config.NarrationThrottleConfig, townlet.config.load_config, townlet.telemetry.narration.NarrationRateLimiter, townlet.telemetry.publisher.TelemetryPublisher, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: test_narration_rate_limiter_enforces_cooldowns, test_narration_rate_limiter_priority_bypass, test_telemetry_publisher_emits_queue_conflict_narration

## `tests/test_telemetry_new_events.py`

**Purpose**: No module docstring provided.
**Lines of code**: 236
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring. (line 10)
- `test_shower_events_in_telemetry() -> None` — No docstring. (line 17)
- `test_shower_complete_narration() -> None` — No docstring. (line 80)
- `test_sleep_events_in_telemetry() -> None` — No docstring. (line 139)
- `test_rivalry_events_surface_in_telemetry() -> None` — No docstring. (line 200)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, SimulationLoop
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: make_loop, test_rivalry_events_surface_in_telemetry, test_shower_complete_narration, test_shower_events_in_telemetry, test_sleep_events_in_telemetry

## `tests/test_telemetry_stream_smoke.py`

**Purpose**: No module docstring provided.
**Lines of code**: 51
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet_ui.telemetry.TelemetryClient
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet_ui.telemetry.TelemetryClient

### Classes
- None

### Functions
- `_ensure_agents(loop: SimulationLoop) -> None` — No docstring. (line 11)
- `test_file_transport_stream_smoke(tmp_path: Path) -> None` — No docstring. (line 26)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: loop, tmp_path
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet_ui.telemetry.TelemetryClient

### Code Quality Notes
- Missing docstrings: _ensure_agents, test_file_transport_stream_smoke

## `tests/test_telemetry_summary.py`

**Purpose**: No module docstring provided.
**Lines of code**: 69
**Dependencies**: stdlib=__future__.annotations, importlib.util, pathlib.Path, sys; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `test_summary_includes_new_events(tmp_path: Path) -> None` — No docstring. (line 17)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: test_summary_includes_new_events

## `tests/test_telemetry_transport.py`

**Purpose**: No module docstring provided.
**Lines of code**: 154
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path, time; external=pytest; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.telemetry.transport.TransportBuffer, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.telemetry.transport.TransportBuffer, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `_ensure_agents(loop: SimulationLoop) -> None` — No docstring. (line 14)
- `test_transport_buffer_drop_until_capacity() -> None` — No docstring. (line 29)
- `test_telemetry_publisher_flushes_payload(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring. (line 40)
- `test_telemetry_publisher_retries_on_failure(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring. (line 71)
- `test_telemetry_worker_metrics_and_stop(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring. (line 120)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: loop, monkeypatch
- Return payloads: None
- Flushes buffers or queues via test_telemetry_publisher_flushes_payload
- Loads configuration or datasets from disk via test_telemetry_publisher_flushes_payload
- Publishes telemetry or events via test_telemetry_publisher_flushes_payload, test_telemetry_publisher_retries_on_failure

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.telemetry.transport.TransportBuffer, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: _ensure_agents, test_telemetry_publisher_flushes_payload, test_telemetry_publisher_retries_on_failure, test_telemetry_worker_metrics_and_stop, test_transport_buffer_drop_until_capacity

## `tests/test_telemetry_validator.py`

**Purpose**: No module docstring provided.
**Lines of code**: 119
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path; external=pytest; internal=scripts.validate_ppo_telemetry.validate_logs
**Related modules**: scripts.validate_ppo_telemetry.validate_logs

### Classes
- None

### Functions
- `_write_ndjson(path: Path, record: dict[str, float]) -> None` — No docstring. (line 42)
- `test_validate_ppo_telemetry_accepts_valid_log(tmp_path: Path) -> None` — No docstring. (line 46)
- `test_validate_ppo_telemetry_raises_for_missing_conflict(tmp_path: Path) -> None` — No docstring. (line 66)
- `test_validate_ppo_telemetry_accepts_version_1_1(tmp_path: Path) -> None` — No docstring. (line 81)
- `test_validate_ppo_telemetry_v1_1_missing_field_raises(tmp_path: Path) -> None` — No docstring. (line 106)

### Constants and Configuration
- `VALID_RECORD` = {'epoch': 1.0, 'updates': 2.0, 'transitions': 4.0, 'loss_policy': 0.1, 'loss_value': 0.2, 'loss_entropy': 0.3, 'loss_total': 0.4, 'clip_fraction': 0.1, 'adv_mean': 0.0, 'adv_std': 0.1, 'adv_zero_std_batches': 0.0, 'adv_min_std': 0.1, 'clip_triggered_minibatches': 0.0, 'clip_fraction_max': 0.1, 'grad_norm': 1.5, 'kl_divergence': 0.01, 'telemetry_version': 1.0, 'lr': 0.0003, 'steps': 4.0, 'baseline_sample_count': 2.0, 'baseline_reward_mean': 0.25, 'baseline_reward_sum': 1.0, 'baseline_reward_sum_mean': 0.5, 'baseline_log_prob_mean': -0.2, 'conflict.rivalry_max_mean_avg': 0.05, 'conflict.rivalry_max_max_avg': 0.1, 'conflict.rivalry_avoid_count_mean_avg': 0.0, 'conflict.rivalry_avoid_count_max_avg': 0.0} (line 10)

### Data Flow
- Primary inputs: path, record, tmp_path
- Return payloads: None
- Validates inputs or configuration via test_validate_ppo_telemetry_accepts_valid_log, test_validate_ppo_telemetry_accepts_version_1_1, test_validate_ppo_telemetry_raises_for_missing_conflict, test_validate_ppo_telemetry_v1_1_missing_field_raises

### Integration Points
- External: pytest
- Internal: scripts.validate_ppo_telemetry.validate_logs

### Code Quality Notes
- Missing docstrings: _write_ndjson, test_validate_ppo_telemetry_accepts_valid_log, test_validate_ppo_telemetry_accepts_version_1_1, test_validate_ppo_telemetry_raises_for_missing_conflict, test_validate_ppo_telemetry_v1_1_missing_field_raises

## `tests/test_telemetry_watch.py`

**Purpose**: No module docstring provided.
**Lines of code**: 64
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=pytest; internal=scripts.telemetry_watch._parse_health_line, scripts.telemetry_watch.check_health_thresholds, scripts.telemetry_watch.stream_health_records
**Related modules**: scripts.telemetry_watch._parse_health_line, scripts.telemetry_watch.check_health_thresholds, scripts.telemetry_watch.stream_health_records

### Classes
- None

### Functions
- `test_parse_health_line() -> None` — No docstring. (line 14)
- `test_stream_health_records(tmp_path: Path) -> None` — No docstring. (line 27)
- `test_health_thresholds_raise() -> None` — No docstring. (line 39)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: tmp_path
- Return payloads: None
- Records metrics or histories via test_stream_health_records

### Integration Points
- External: pytest
- Internal: scripts.telemetry_watch._parse_health_line, scripts.telemetry_watch.check_health_thresholds, scripts.telemetry_watch.stream_health_records

### Code Quality Notes
- Missing docstrings: test_health_thresholds_raise, test_parse_health_line, test_stream_health_records

## `tests/test_training_anneal.py`

**Purpose**: No module docstring provided.
**Lines of code**: 108
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path; external=numpy, pytest; internal=townlet.config.AnnealStage, townlet.config.load_config, townlet.policy.models.torch_available, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.replay.frames_to_replay_sample, townlet.policy.runner.TrainingHarness
**Related modules**: townlet.config.AnnealStage, townlet.config.load_config, townlet.policy.models.torch_available, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.replay.frames_to_replay_sample, townlet.policy.runner.TrainingHarness

### Classes
- None

### Functions
- `_write_sample(output_dir: Path, stem: str, timesteps: int, action_dim: int = 2) -> tuple[Path, Path]` — No docstring. (line 15)
- `test_run_anneal_bc_then_ppo(tmp_path: Path) -> None` — No docstring. (line 56)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: action_dim, output_dir, stem, timesteps, tmp_path
- Return payloads: None, tuple[Path, Path]
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: numpy, pytest
- Internal: townlet.config.AnnealStage, townlet.config.load_config, townlet.policy.models.torch_available, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.replay.frames_to_replay_sample, townlet.policy.runner.TrainingHarness

### Code Quality Notes
- Missing docstrings: _write_sample, test_run_anneal_bc_then_ppo

## `tests/test_training_cli.py`

**Purpose**: No module docstring provided.
**Lines of code**: 81
**Dependencies**: stdlib=__future__.annotations, argparse.Namespace, pathlib.Path; external=None; internal=scripts.run_training, townlet.config.PPOConfig, townlet.config.load_config
**Related modules**: scripts.run_training, townlet.config.PPOConfig, townlet.config.load_config

### Classes
- None

### Functions
- `_make_namespace(**kwargs: object) -> Namespace` — No docstring. (line 10)
- `test_collect_ppo_overrides_handles_values() -> None` — No docstring. (line 29)
- `test_apply_ppo_overrides_creates_config_when_missing() -> None` — No docstring. (line 59)
- `test_apply_ppo_overrides_updates_existing_model() -> None` — No docstring. (line 74)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: kwargs
- Return payloads: Namespace, None
- Applies world or agent state updates via test_apply_ppo_overrides_creates_config_when_missing, test_apply_ppo_overrides_updates_existing_model
- Updates internal caches or trackers via test_apply_ppo_overrides_updates_existing_model

### Integration Points
- External: None
- Internal: scripts.run_training, townlet.config.PPOConfig, townlet.config.load_config

### Code Quality Notes
- Missing docstrings: _make_namespace, test_apply_ppo_overrides_creates_config_when_missing, test_apply_ppo_overrides_updates_existing_model, test_collect_ppo_overrides_handles_values

## `tests/test_training_replay.py`

**Purpose**: No module docstring provided.
**Lines of code**: 955
**Dependencies**: stdlib=__future__.annotations, json, math, pathlib.Path, subprocess, sys; external=numpy, pytest, torch; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.policy.models.torch_available, townlet.policy.replay.ReplayDataset, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.replay.ReplaySample, townlet.policy.replay.frames_to_replay_sample, townlet.policy.replay.load_replay_sample, townlet.policy.replay_buffer.InMemoryReplayDataset, townlet.policy.replay_buffer.InMemoryReplayDatasetConfig, townlet.policy.runner.TrainingHarness, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.policy.models.torch_available, townlet.policy.replay.ReplayDataset, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.replay.ReplaySample, townlet.policy.replay.frames_to_replay_sample, townlet.policy.replay.load_replay_sample, townlet.policy.replay_buffer.InMemoryReplayDataset, townlet.policy.replay_buffer.InMemoryReplayDatasetConfig, townlet.policy.runner.TrainingHarness, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_validate_numeric(value: object) -> None` — No docstring. (line 97)
- `_assert_ppo_log_schema(summary: dict[str, object], require_baseline: bool) -> None` — No docstring. (line 102)
- `_load_expected_stats(config_path: Path) -> dict[str, dict[str, float]]` — No docstring. (line 138)
- `_aggregate_expected_metrics(sample_stats: dict[str, dict[str, float]]) -> dict[str, float]` — No docstring. (line 146)
- `_make_sample(base_dir: Path, rivalry_increment: float, avoid_threshold: float, suffix: str) -> tuple[Path, Path]` — No docstring. (line 184)
- `_make_social_sample() -> ReplaySample` — No docstring. (line 251)
- `test_training_harness_replay_stats(tmp_path: Path) -> None` — No docstring. (line 309)
- `test_replay_dataset_batch_iteration(tmp_path: Path) -> None` — No docstring. (line 318)
- `test_replay_loader_schema_guard(tmp_path: Path) -> None` — No docstring. (line 348)
- `test_replay_dataset_streaming(tmp_path: Path) -> None` — No docstring. (line 357)
- `test_replay_loader_missing_training_arrays(tmp_path: Path) -> None` — No docstring. (line 383)
- `test_replay_loader_value_length_mismatch(tmp_path: Path) -> None` — No docstring. (line 400)
- `test_training_harness_run_ppo_on_capture(tmp_path: Path, config_path: Path) -> None` — No docstring. (line 423)
- `test_training_harness_run_ppo(tmp_path: Path) -> None` — No docstring. (line 539)
- `test_run_ppo_rejects_nan_advantages(tmp_path: Path) -> None` — No docstring. (line 554)
- `test_training_harness_log_sampling_and_rotation(tmp_path: Path) -> None` — No docstring. (line 566)
- `test_training_harness_run_rollout_ppo(tmp_path: Path) -> None` — No docstring. (line 609)
- `test_training_harness_ppo_conflict_telemetry(tmp_path: Path) -> None` — No docstring. (line 629)
- `test_training_harness_run_rollout_ppo_multiple_cycles(tmp_path: Path) -> None` — No docstring. (line 685)
- `test_training_harness_rollout_capture_and_train_cycles(tmp_path: Path) -> None` — No docstring. (line 727)
- `test_training_harness_streaming_log_offsets(tmp_path: Path) -> None` — No docstring. (line 794)
- `test_training_harness_rollout_queue_conflict_metrics(tmp_path: Path) -> None` — No docstring. (line 844)
- `test_ppo_social_chat_drift(tmp_path: Path) -> None` — No docstring. (line 873)
- `test_policy_runtime_collects_frames(tmp_path: Path) -> None` — No docstring. (line 918)

### Constants and Configuration
- `SCENARIO_CONFIGS` = [Path('configs/scenarios/kitchen_breakfast.yaml'), Path('configs/scenarios/queue_conflict.yaml'), Path('configs/scenarios/employment_punctuality.yaml'), Path('configs/scenarios/rivalry_decay.yaml'), Path('configs/scenarios/observation_baseline.yaml')] (line 29)
- `GOLDEN_STATS_PATH` = Path('docs/samples/rollout_scenario_stats.json') (line 37)
- `GOLDEN_STATS` = json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {} (line 38)
- `REQUIRED_PPO_KEYS` = {'epoch', 'updates', 'transitions', 'loss_policy', 'loss_value', 'loss_entropy', 'loss_total', 'clip_fraction', 'adv_mean', 'adv_std', 'adv_zero_std_batches', 'adv_min_std', 'clip_triggered_minibatches', 'clip_fraction_max', 'grad_norm', 'kl_divergence', 'telemetry_version', 'lr', 'steps', 'epoch_duration_sec', 'data_mode', 'cycle_id', 'batch_entropy_mean', 'batch_entropy_std', 'grad_norm_max', 'kl_divergence_max', 'reward_advantage_corr', 'rollout_ticks', 'log_stream_offset', 'queue_conflict_events', 'queue_conflict_intensity_sum', 'shared_meal_events', 'late_help_events', 'shift_takeover_events', 'chat_success_events', 'chat_failure_events', 'chat_quality_mean'} (line 43)
- `REQUIRED_PPO_NUMERIC_KEYS` = REQUIRED_PPO_KEYS - {'data_mode'} (line 83)
- `BASELINE_KEYS_REQUIRED` = {'baseline_sample_count', 'baseline_reward_sum', 'baseline_reward_sum_mean', 'baseline_reward_mean'} (line 85)
- `BASELINE_KEYS_OPTIONAL` = {'baseline_log_prob_mean'} (line 92)
- `ALLOWED_KEY_PREFIXES` = ('conflict.',) (line 94)

### Data Flow
- Primary inputs: avoid_threshold, base_dir, config_path, require_baseline, rivalry_increment, sample_stats, suffix, summary, tmp_path, value
- Return payloads: None, ReplaySample, dict[str, dict[str, float]], dict[str, float], tuple[Path, Path]
- Captures trajectories or telemetry snapshots via test_training_harness_rollout_capture_and_train_cycles, test_training_harness_run_ppo_on_capture
- Handles replay buffers or datasets via test_replay_dataset_batch_iteration, test_replay_dataset_streaming, test_replay_loader_missing_training_arrays, test_replay_loader_schema_guard, test_replay_loader_value_length_mismatch, test_training_harness_replay_stats
- Loads configuration or datasets from disk via _load_expected_stats, test_replay_loader_missing_training_arrays, test_replay_loader_schema_guard, test_replay_loader_value_length_mismatch
- Trains policies or models via test_replay_loader_missing_training_arrays, test_training_harness_log_sampling_and_rotation, test_training_harness_ppo_conflict_telemetry, test_training_harness_replay_stats, test_training_harness_rollout_capture_and_train_cycles, test_training_harness_rollout_queue_conflict_metrics, test_training_harness_run_ppo, test_training_harness_run_ppo_on_capture, test_training_harness_run_rollout_ppo, test_training_harness_run_rollout_ppo_multiple_cycles, test_training_harness_streaming_log_offsets
- Validates inputs or configuration via _validate_numeric

### Integration Points
- External: numpy, pytest, torch
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.observations.builder.ObservationBuilder, townlet.policy.models.torch_available, townlet.policy.replay.ReplayDataset, townlet.policy.replay.ReplayDatasetConfig, townlet.policy.replay.ReplaySample, townlet.policy.replay.frames_to_replay_sample, townlet.policy.replay.load_replay_sample, townlet.policy.replay_buffer.InMemoryReplayDataset, townlet.policy.replay_buffer.InMemoryReplayDatasetConfig, townlet.policy.runner.TrainingHarness, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _aggregate_expected_metrics, _assert_ppo_log_schema, _load_expected_stats, _make_sample, _make_social_sample, _validate_numeric, test_policy_runtime_collects_frames, test_ppo_social_chat_drift, test_replay_dataset_batch_iteration, test_replay_dataset_streaming, test_replay_loader_missing_training_arrays, test_replay_loader_schema_guard, test_replay_loader_value_length_mismatch, test_run_ppo_rejects_nan_advantages, test_training_harness_log_sampling_and_rotation, test_training_harness_ppo_conflict_telemetry, test_training_harness_replay_stats, test_training_harness_rollout_capture_and_train_cycles, test_training_harness_rollout_queue_conflict_metrics, test_training_harness_run_ppo
- ... 4 additional methods without docstrings
- Module exceeds 800 lines; consider refactoring into smaller components.

## `tests/test_utils_rng.py`

**Purpose**: No module docstring provided.
**Lines of code**: 22
**Dependencies**: stdlib=__future__.annotations, random; external=pytest; internal=townlet.utils.decode_rng_state, townlet.utils.encode_rng_state
**Related modules**: townlet.utils.decode_rng_state, townlet.utils.encode_rng_state

### Classes
- None

### Functions
- `test_encode_decode_rng_state_round_trip() -> None` — No docstring. (line 10)
- `test_decode_rng_state_invalid_payload() -> None` — No docstring. (line 20)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None
- Loads configuration or datasets from disk via test_decode_rng_state_invalid_payload

### Integration Points
- External: pytest
- Internal: townlet.utils.decode_rng_state, townlet.utils.encode_rng_state

### Code Quality Notes
- Missing docstrings: test_decode_rng_state_invalid_payload, test_encode_decode_rng_state_round_trip

## `tests/test_world_local_view.py`

**Purpose**: No module docstring provided.
**Lines of code**: 90
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring. (line 10)
- `tile_for_position(tiles, position)` — No docstring. (line 17)
- `test_local_view_includes_objects_and_agents() -> None` — No docstring. (line 25)
- `test_agent_context_defaults() -> None` — No docstring. (line 55)
- `test_world_snapshot_returns_defensive_copies() -> None` — No docstring. (line 74)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: position, tiles
- Return payloads: None, SimulationLoop
- Primarily data container definitions; minimal runtime logic.

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot

### Code Quality Notes
- Missing docstrings: make_loop, test_agent_context_defaults, test_local_view_includes_objects_and_agents, test_world_snapshot_returns_defensive_copies, tile_for_position

## `tests/test_world_nightly_reset.py`

**Purpose**: No module docstring provided.
**Lines of code**: 74
**Dependencies**: stdlib=__future__.annotations, pathlib.Path; external=None; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_setup_world() -> WorldState` — No docstring. (line 10)
- `test_apply_nightly_reset_returns_agents_home() -> None` — No docstring. (line 18)
- `test_simulation_loop_triggers_nightly_reset() -> None` — No docstring. (line 50)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, WorldState
- Applies world or agent state updates via test_apply_nightly_reset_returns_agents_home
- Resets runtime state via test_apply_nightly_reset_returns_agents_home, test_simulation_loop_triggers_nightly_reset

### Integration Points
- External: None
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _setup_world, test_apply_nightly_reset_returns_agents_home, test_simulation_loop_triggers_nightly_reset

## `tests/test_world_queue_integration.py`

**Purpose**: No module docstring provided.
**Lines of code**: 280
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring. (line 10)
- `test_queue_assignment_flow() -> None` — No docstring. (line 34)
- `test_queue_ghost_step_promotes_waiter() -> None` — No docstring. (line 54)
- `test_affordance_completion_applies_effects() -> None` — No docstring. (line 75)
- `test_eat_meal_adjusts_needs_and_wallet() -> None` — No docstring. (line 101)
- `test_affordance_failure_skips_effects() -> None` — No docstring. (line 132)
- `test_affordances_loaded_from_yaml() -> None` — No docstring. (line 164)
- `test_affordance_events_emitted() -> None` — No docstring. (line 172)
- `test_need_decay_applied_each_tick() -> None` — No docstring. (line 199)
- `test_eat_meal_deducts_wallet_and_stock() -> None` — No docstring. (line 210)
- `test_wage_income_applied_on_shift() -> None` — No docstring. (line 237)
- `test_stove_restock_event_emitted() -> None` — No docstring. (line 253)
- `test_scripted_behavior_handles_sleep() -> None` — No docstring. (line 263)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, WorldState
- Advances tick or scheduler timelines via test_need_decay_applied_each_tick
- Loads configuration or datasets from disk via test_affordances_loaded_from_yaml
- Promotes builds or policies via test_queue_ghost_step_promotes_waiter

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.core.sim_loop.SimulationLoop, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _make_world, test_affordance_completion_applies_effects, test_affordance_events_emitted, test_affordance_failure_skips_effects, test_affordances_loaded_from_yaml, test_eat_meal_adjusts_needs_and_wallet, test_eat_meal_deducts_wallet_and_stock, test_need_decay_applied_each_tick, test_queue_assignment_flow, test_queue_ghost_step_promotes_waiter, test_scripted_behavior_handles_sleep, test_stove_restock_event_emitted, test_wage_income_applied_on_shift

## `tests/test_world_rivalry.py`

**Purpose**: No module docstring provided.
**Lines of code**: 94
**Dependencies**: stdlib=pathlib.Path; external=pytest; internal=townlet.config.load_config, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState
**Related modules**: townlet.config.load_config, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring. (line 9)
- `test_register_rivalry_conflict_updates_snapshot() -> None` — No docstring. (line 28)
- `test_rivalry_events_record_reason() -> None` — No docstring. (line 35)
- `test_rivalry_decays_over_time() -> None` — No docstring. (line 51)
- `test_queue_conflict_event_emitted_with_intensity() -> None` — No docstring. (line 73)

### Constants and Configuration
- None

### Data Flow
- Primary inputs: None (pure module constants/types).
- Return payloads: None, WorldState
- Records metrics or histories via test_rivalry_events_record_reason
- Registers handlers or callbacks via test_register_rivalry_conflict_updates_snapshot
- Updates internal caches or trackers via test_register_rivalry_conflict_updates_snapshot

### Integration Points
- External: pytest
- Internal: townlet.config.load_config, townlet.world.grid.AgentSnapshot, townlet.world.grid.WorldState

### Code Quality Notes
- Missing docstrings: _make_world, test_queue_conflict_event_emitted_with_intensity, test_register_rivalry_conflict_updates_snapshot, test_rivalry_decays_over_time, test_rivalry_events_record_reason

## `tmp/analyze_modules.py`

**Purpose**: No module docstring provided.
**Lines of code**: 535
**Dependencies**: stdlib=__future__.annotations, ast, collections.defaultdict, dataclasses.dataclass, dataclasses.field, json, os, pathlib.Path, typing.Any, typing.Iterable; external=None; internal=None
**Related modules**: None

### Classes
- `FunctionInfo` (bases: object; decorators: dataclass) — No class docstring provided. (line 62)
  - Attributes:
    - name=`name`, type=`str` (line 63)
    - name=`signature`, type=`str` (line 64)
    - name=`lineno`, type=`int` (line 65)
    - name=`docstring`, type=`str | None` (line 66)
    - name=`params`, type=`list[dict[str, Any]]` (line 67)
    - name=`return_type`, type=`str | None` (line 68)
    - name=`is_async`, type=`bool`, default=`False` (line 69)
- `ClassInfo` (bases: object; decorators: dataclass) — No class docstring provided. (line 73)
  - Attributes:
    - name=`name`, type=`str` (line 74)
    - name=`bases`, type=`list[str]`, default=`field(default_factory=list)` (line 75)
    - name=`decorators`, type=`list[str]`, default=`field(default_factory=list)` (line 76)
    - name=`lineno`, type=`int`, default=`0` (line 77)
    - name=`docstring`, type=`str | None`, default=`None` (line 78)
    - name=`methods`, type=`list[FunctionInfo]`, default=`field(default_factory=list)` (line 79)
    - name=`attributes`, type=`list[dict[str, Any]]`, default=`field(default_factory=list)` (line 80)
- `ModuleInfo` (bases: object; decorators: dataclass) — No class docstring provided. (line 84)
  - Attributes:
    - name=`path`, type=`Path` (line 85)
    - name=`module`, type=`str` (line 86)
    - name=`module_name`, type=`str` (line 87)
    - name=`docstring`, type=`str | None` (line 88)
    - name=`imports`, type=`dict[str, set[str]]` (line 89)
    - name=`classes`, type=`list[ClassInfo]` (line 90)
    - name=`functions`, type=`list[FunctionInfo]` (line 91)
    - name=`constants`, type=`list[dict[str, Any]]` (line 92)
    - name=`env_vars`, type=`list[str]` (line 93)
    - name=`todos`, type=`list[int]` (line 94)
    - name=`has_logging`, type=`bool` (line 95)
    - name=`has_type_hints`, type=`bool` (line 96)
    - name=`has_dataclasses`, type=`bool` (line 97)
    - name=`lines`, type=`int` (line 98)

### Functions
- `unparse(node: ast.AST | None) -> str | None` — No docstring. (line 101)
- `_format_param_entry(name: str, annotation: str | None, default: str | None) -> str` — No docstring. (line 110)
- `build_signature(arguments: ast.arguments) -> tuple[str, list[dict[str, Any]]]` — No docstring. (line 119)
- `format_return(annotation: ast.expr | None) -> str` — No docstring. (line 210)
- `module_name_from_path(path: Path) -> str` — No docstring. (line 216)
- `classify_import(module: str) -> str` — No docstring. (line 233)
- `collect_imports(tree: ast.AST, package_parts: list[str]) -> dict[str, set[str]]` — No docstring. (line 244)
- `gather_class_attributes(body: list[ast.stmt]) -> list[dict[str, Any]]` — No docstring. (line 273)
- `gather_constants(body: list[ast.stmt]) -> list[dict[str, Any]]` — No docstring. (line 318)
- `detect_env_usage(tree: ast.AST) -> list[str]` — No docstring. (line 345)
- `gather_functions(body: Iterable[ast.stmt]) -> list[FunctionInfo]` — No docstring. (line 358)
- `analyze_module(path: Path) -> ModuleInfo` — No docstring. (line 383)
- `find_python_files(root: Path) -> list[Path]` — No docstring. (line 451)
- `main() -> None` — No docstring. (line 462)

### Constants and Configuration
- `PROJECT_ROOT` = Path(__file__).resolve().parents[1] (line 11)
- `PACKAGE_PREFIXES` = {'townlet', 'townlet_ui', 'scripts'} (line 13)
- `STD_LIB_MODULES` = {'__future__', 'abc', 'argparse', 'asyncio', 'base64', 'bisect', 'collections', 'collections.abc', 'contextlib', 'copy', 'dataclasses', 'datetime', 'decimal', 'enum', 'functools', 'hashlib', 'heapq', 'itertools', 'json', 'logging', 'math', 'os', 'pathlib', 'random', 'statistics', 'textwrap', 'time', 'typing', 'typing_extensions', 'uuid', 'weakref'} (line 19)
- `NON_STANDARD_PREFIXES` = ('townlet', 'townlet_ui', 'scripts') (line 54)

### Data Flow
- Primary inputs: annotation, arguments, body, default, module, name, node, package_parts, path, root, tree
- Return payloads: ModuleInfo, None, dict[str, set[str]], list[FunctionInfo], list[Path], list[dict[str, Any]], list[str], str, str | None, tuple[str, list[dict[str, Any]]]
- Builds derived structures or observations via build_signature

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: _format_param_entry, analyze_module, build_signature, classify_import, collect_imports, detect_env_usage, find_python_files, format_return, gather_class_attributes, gather_constants, gather_functions, main, module_name_from_path, unparse

## `tmp/render_module_docs.py`

**Purpose**: No module docstring provided.
**Lines of code**: 232
**Dependencies**: stdlib=__future__.annotations, json, pathlib.Path, typing.Any; external=None; internal=None
**Related modules**: None

### Classes
- None

### Functions
- `summarise_docstring(text: str | None, fallback: str) -> str` — No docstring. (line 12)
- `format_list(values: list[str]) -> str` — No docstring. (line 24)
- `indent(text: str, level: int = 1) -> str` — No docstring. (line 30)
- `build_class_section(cls: dict[str, Any]) -> str` — No docstring. (line 35)
- `build_function_section(fn: dict[str, Any]) -> str` — No docstring. (line 67)
- `collect_inputs(module: dict[str, Any]) -> list[str]` — No docstring. (line 73)
- `collect_outputs(module: dict[str, Any]) -> list[str]` — No docstring. (line 91)
- `build_code_quality_notes(module: dict[str, Any]) -> list[str]` — No docstring. (line 105)
- `main() -> None` — No docstring. (line 139)

### Constants and Configuration
- `PROJECT_ROOT` = Path(__file__).resolve().parents[1] (line 7)
- `METADATA_PATH` = PROJECT_ROOT / 'audit' / 'module_metadata.json' (line 8)
- `OUTPUT_PATH` = PROJECT_ROOT / 'audit' / 'MODULE_DOCUMENTATION.md' (line 9)

### Data Flow
- Primary inputs: fallback, fn, level, module, text, values
- Return payloads: None, list[str], str
- Builds derived structures or observations via build_class_section, build_code_quality_notes, build_function_section
- Summarises metrics for review via summarise_docstring

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing docstrings: build_class_section, build_code_quality_notes, build_function_section, collect_inputs, collect_outputs, format_list, indent, main, summarise_docstring