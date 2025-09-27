from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.observations.builder import ObservationBuilder
from townlet.policy.models import torch_available
from townlet.policy.replay import (
    ReplayDataset,
    ReplayDatasetConfig,
    ReplaySample,
    frames_to_replay_sample,
    load_replay_sample,
)
from townlet.policy.replay_buffer import InMemoryReplayDataset, InMemoryReplayDatasetConfig
from townlet.policy.runner import TrainingHarness
from townlet.world.grid import AgentSnapshot, WorldState

SCENARIO_CONFIGS = [
    Path("configs/scenarios/kitchen_breakfast.yaml"),
    Path("configs/scenarios/queue_conflict.yaml"),
    Path("configs/scenarios/employment_punctuality.yaml"),
    Path("configs/scenarios/rivalry_decay.yaml"),
    Path("configs/scenarios/observation_baseline.yaml"),
]

GOLDEN_STATS_PATH = Path("docs/samples/rollout_scenario_stats.json")
GOLDEN_STATS = json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {}


REQUIRED_PPO_KEYS = {
    "epoch",
    "updates",
    "transitions",
    "loss_policy",
    "loss_value",
    "loss_entropy",
    "loss_total",
    "clip_fraction",
    "adv_mean",
    "adv_std",
    "grad_norm",
    "kl_divergence",
    "telemetry_version",
    "lr",
    "steps",
    "epoch_duration_sec",
    "data_mode",
    "cycle_id",
    "batch_entropy_mean",
    "batch_entropy_std",
    "grad_norm_max",
    "kl_divergence_max",
    "reward_advantage_corr",
    "rollout_ticks",
    "log_stream_offset",
    "queue_conflict_events",
    "queue_conflict_intensity_sum",
    "shared_meal_events",
    "late_help_events",
    "shift_takeover_events",
    "chat_success_events",
    "chat_failure_events",
    "chat_quality_mean",
}

REQUIRED_PPO_NUMERIC_KEYS = REQUIRED_PPO_KEYS - {"data_mode"}

BASELINE_KEYS_REQUIRED = {
    "baseline_sample_count",
    "baseline_reward_sum",
    "baseline_reward_sum_mean",
    "baseline_reward_mean",
}

BASELINE_KEYS_OPTIONAL = {"baseline_log_prob_mean"}

ALLOWED_KEY_PREFIXES = ("conflict.",)


def _validate_numeric(value: object) -> None:
    assert isinstance(value, (int, float)), f"Expected numeric value, got {type(value)}"
    assert math.isfinite(float(value)), "Expected finite numeric value"


def _assert_ppo_log_schema(summary: dict[str, object], require_baseline: bool) -> None:
    missing_keys = REQUIRED_PPO_KEYS - summary.keys()
    assert not missing_keys, f"Missing required PPO summary keys: {sorted(missing_keys)}"

    for key in REQUIRED_PPO_NUMERIC_KEYS:
        _validate_numeric(summary[key])

    assert isinstance(summary["data_mode"], str)

    seen_baseline = {key for key in summary if key.startswith("baseline_")}
    if require_baseline:
        missing_baseline = BASELINE_KEYS_REQUIRED - seen_baseline
        assert not missing_baseline, f"Missing baseline keys: {sorted(missing_baseline)}"
        for key in BASELINE_KEYS_REQUIRED | (seen_baseline & BASELINE_KEYS_OPTIONAL):
            if key in summary:
                _validate_numeric(summary[key])
    else:
        # Baseline keys are optional in this mode but must still be numeric if present.
        for key in seen_baseline:
            _validate_numeric(summary[key])

    for key, value in summary.items():
        if key in REQUIRED_PPO_KEYS:
            continue
        if key.startswith("baseline_"):
            continue
        if any(key.startswith(prefix) for prefix in ALLOWED_KEY_PREFIXES):
            _validate_numeric(value)
            continue
        raise AssertionError(f"Unexpected PPO summary key encountered: {key}")


def _load_expected_stats(config_path: Path) -> dict[str, dict[str, float]]:
    scenario_key = config_path.stem
    stats = GOLDEN_STATS.get(scenario_key)
    if not stats:
        pytest.skip(f"Golden stats not available for scenario '{scenario_key}'")
    return stats


def _aggregate_expected_metrics(sample_stats: dict[str, dict[str, float]]) -> dict[str, float]:
    sample_count = float(len(sample_stats))
    if sample_count == 0:
        return {"sample_count": 0.0, "reward_sum": 0.0, "reward_sum_mean": 0.0, "reward_mean": 0.0}
    reward_sums = [float(stats.get("reward_sum", 0.0)) for stats in sample_stats.values()]
    reward_means = [
        float(stats.get("reward_mean", 0.0))
        for stats in sample_stats.values()
        if "reward_mean" in stats
    ]
    log_prob_means = [
        float(stats.get("log_prob_mean", 0.0))
        for stats in sample_stats.values()
        if "log_prob_mean" in stats
    ]

    aggregated: dict[str, float] = {
        "sample_count": sample_count,
        "reward_sum": float(sum(reward_sums)),
        "reward_sum_mean": float(sum(reward_sums) / sample_count),
        "reward_mean": float(sum(reward_means) / len(reward_means)) if reward_means else 0.0,
    }
    if log_prob_means:
        aggregated["log_prob_mean"] = float(sum(log_prob_means) / len(log_prob_means))
    return aggregated


def _make_sample(
    base_dir: Path,
    rivalry_increment: float,
    avoid_threshold: float,
    suffix: str,
) -> tuple[Path, Path]:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.conflict.rivalry.increment_per_conflict = rivalry_increment
    config.conflict.rivalry.avoid_threshold = avoid_threshold
    world = WorldState.from_config(config)
    world.register_object(object_id="stove_1", object_type="stove")
    world.agents["alice"] = AgentSnapshot(
        "alice",
        (0, 0),
        {"hunger": 0.3, "hygiene": 0.4, "energy": 0.5},
        wallet=2.0,
    )
    world.agents["bob"] = AgentSnapshot(
        "bob",
        (1, 0),
        {"hunger": 0.6, "hygiene": 0.7, "energy": 0.8},
        wallet=3.0,
    )
    world.register_rivalry_conflict("alice", "bob")
    builder = ObservationBuilder(config)
    obs = builder.build_batch(world, terminated={})["alice"]
    timesteps = 2
    map_seq = np.stack([obs["map"], obs["map"]], axis=0)
    feature_seq = np.stack([obs["features"], obs["features"]], axis=0)
    sample_path = base_dir / f"replay_sample_{suffix}.npz"
    meta_path = base_dir / f"replay_sample_{suffix}.json"
    actions = np.array([1, 0], dtype=np.int64)
    old_log_probs = np.array([-0.5, -0.4], dtype=np.float32)
    value_preds = np.array([0.1, 0.05, 0.02], dtype=np.float32)
    rewards = np.array([0.05, 0.02], dtype=np.float32)
    dones = np.array([False, True], dtype=np.bool_)
    np.savez(
        sample_path,
        map=map_seq,
        features=feature_seq,
        actions=actions,
        old_log_probs=old_log_probs,
        value_preds=value_preds,
        rewards=rewards,
        dones=dones,
    )
    feature_names = obs["metadata"]["feature_names"]
    obs["metadata"]["rivalry_example"] = {
        "rivalry_max": float(obs["features"][feature_names.index("rivalry_max")]),
        "rivalry_avoid_count": float(obs["features"][feature_names.index("rivalry_avoid_count")]),
    }
    obs["metadata"]["training_arrays"] = [
        "actions",
        "old_log_probs",
        "value_preds",
        "rewards",
        "dones",
    ]
    obs["metadata"]["timesteps"] = timesteps
    obs["metadata"]["value_pred_steps"] = len(value_preds)
    obs["metadata"]["action_dim"] = 3
    meta_path.write_text(json.dumps(obs["metadata"], indent=2))
    return sample_path, meta_path


def _make_social_sample() -> ReplaySample:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.95, "hygiene": 0.85, "energy": 0.9},
        wallet=2.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 1),
        needs={"hunger": 0.92, "hygiene": 0.8, "energy": 0.88},
        wallet=2.0,
    )
    world.record_chat_success("alice", "bob", quality=0.8)

    builder = ObservationBuilder(config)
    observation = builder.build_batch(world, terminated={"alice": False, "bob": False})[
        "alice"
    ]
    map_seq = np.stack([observation["map"], observation["map"]], axis=0)
    feature_seq = np.stack([observation["features"], observation["features"]], axis=0)
    actions = np.array([1, 2], dtype=np.int64)
    old_log_probs = np.array([-0.2, -0.3], dtype=np.float32)
    value_preds = np.array([0.1, 0.05, 0.01], dtype=np.float32)
    rewards = np.array([0.06, 0.08], dtype=np.float32)
    dones = np.array([False, True], dtype=np.bool_)
    metadata = json.loads(json.dumps(observation["metadata"]))
    metadata["training_arrays"] = [
        "actions",
        "old_log_probs",
        "value_preds",
        "rewards",
        "dones",
    ]
    metadata["timesteps"] = 2
    metadata["value_pred_steps"] = len(value_preds)
    metadata["action_dim"] = 4
    metadata["metrics"] = {
        "reward_sum": float(rewards.sum()),
        "reward_sum_mean": float(rewards.sum()),
        "reward_mean": float(rewards.mean()),
        "log_prob_mean": float(old_log_probs.mean()),
    }

    return ReplaySample(
        map=map_seq,
        features=feature_seq,
        actions=actions,
        old_log_probs=old_log_probs,
        value_preds=value_preds,
        rewards=rewards,
        dones=dones,
        metadata=metadata,
    )


def test_training_harness_replay_stats(tmp_path: Path) -> None:
    sample_path, meta_path = _make_sample(tmp_path, 0.2, 0.3, "single")
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    harness = TrainingHarness(config)
    stats = harness.run_replay(sample_path=sample_path, meta_path=meta_path)
    assert stats["feature_dim"] > 0
    assert stats["conflict.rivalry_max_mean"] >= 0.0


def test_replay_dataset_batch_iteration(tmp_path: Path) -> None:
    sample_a = _make_sample(tmp_path, 0.2, 0.3, "a")
    sample_b = _make_sample(tmp_path, 0.6, 0.2, "b")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {"sample": str(sample_a[0]), "meta": str(sample_a[1])},
                {"sample": str(sample_b[0]), "meta": str(sample_b[1])},
            ],
            indent=2,
        )
    )
    dataset_config = ReplayDatasetConfig.from_manifest(
        manifest,
        batch_size=1,
        shuffle=True,
        seed=42,
    )
    dataset = ReplayDataset(dataset_config)
    batches = list(dataset)
    assert len(batches) == 2
    for batch in batches:
        assert batch.maps.shape == (1, 2, *batch.maps.shape[2:])
        assert batch.features.shape == (1, 2, batch.features.shape[2])
        assert batch.conflict_stats()
        assert batch.actions.shape == (1, 2)
        assert batch.value_preds.shape[1] in {2, 3}


def test_replay_loader_schema_guard(tmp_path: Path) -> None:
    sample_path, meta_path = _make_sample(tmp_path, 0.2, 0.3, "guard")
    meta = json.loads(meta_path.read_text())
    meta["feature_names"].remove("rivalry_max")
    meta_path.write_text(json.dumps(meta, indent=2))
    with pytest.raises(ValueError):
        load_replay_sample(sample_path, meta_path)


def test_replay_dataset_streaming(tmp_path: Path) -> None:
    sample_a = _make_sample(tmp_path, 0.3, 0.4, "stream_a")
    sample_b = _make_sample(tmp_path, 0.4, 0.5, "stream_b")
    manifest = tmp_path / "manifest_stream.json"
    manifest.write_text(
        json.dumps(
            [
                {"sample": str(sample_a[0]), "meta": str(sample_a[1])},
                {"sample": str(sample_b[0]), "meta": str(sample_b[1])},
            ],
            indent=2,
        )
    )
    config = ReplayDatasetConfig.from_manifest(manifest, batch_size=2, streaming=True)
    dataset = ReplayDataset(config)
    batches = list(dataset)
    assert batches
    for batch in batches:
        assert batch.maps.ndim == 5
        assert batch.maps.shape[1] == 2
        assert batch.conflict_stats()
        assert batch.actions.shape[0] == batch.features.shape[0]
        assert batch.actions.shape[1] == 2
        assert batch.value_preds.shape[1] in {2, 3}


def test_replay_loader_missing_training_arrays(tmp_path: Path) -> None:
    sample_path, meta_path = _make_sample(tmp_path, 0.2, 0.3, "missing")
    stripped_path = tmp_path / "replay_sample_missing_actions.npz"
    with np.load(sample_path) as handle:
        np.savez(
            stripped_path,
            map=handle["map"],
            features=handle["features"],
            old_log_probs=handle["old_log_probs"],
            value_preds=handle["value_preds"],
            rewards=handle["rewards"],
            dones=handle["dones"],
        )
    with pytest.raises(ValueError):
        load_replay_sample(stripped_path, meta_path)


def test_replay_loader_value_length_mismatch(tmp_path: Path) -> None:
    sample_path, meta_path = _make_sample(tmp_path, 0.2, 0.3, "value_mismatch")
    broken_path = tmp_path / "replay_sample_value_mismatch.npz"
    with np.load(sample_path) as handle:
        value_preds = np.concatenate([handle["value_preds"], np.array([0.0], dtype=np.float32)])
        np.savez(
            broken_path,
            map=handle["map"],
            features=handle["features"],
            actions=handle["actions"],
            old_log_probs=handle["old_log_probs"],
            value_preds=value_preds,
            rewards=handle["rewards"],
            dones=handle["dones"],
        )
    with pytest.raises(ValueError):
        load_replay_sample(broken_path, meta_path)



@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
@pytest.mark.parametrize("config_path", SCENARIO_CONFIGS)
def test_training_harness_run_ppo_on_capture(tmp_path: Path, config_path: Path) -> None:
    import subprocess

    scenario_stats = _load_expected_stats(config_path)
    capture_dir = tmp_path / config_path.stem
    capture_dir.mkdir()

    subprocess.run(
        [
            sys.executable,
            "scripts/capture_rollout.py",
            str(config_path),
            "--output",
            str(capture_dir),
            "--compress",
        ],
        check=True,
    )

    manifest_path = capture_dir / "rollout_sample_manifest.json"
    assert manifest_path.exists(), "Capture manifest missing"
    manifest = json.loads(manifest_path.read_text())
    assert len(manifest) == len(scenario_stats)

    metrics_path = capture_dir / "rollout_sample_metrics.json"
    assert metrics_path.exists(), "Capture metrics missing"
    metrics_data = json.loads(metrics_path.read_text())
    assert set(metrics_data) == set(scenario_stats), "Captured samples differ from golden stats"

    for sample_name, expected_metrics in scenario_stats.items():
        observed_metrics = metrics_data.get(sample_name)
        assert observed_metrics is not None
        for key in ("timesteps", "reward_sum", "reward_mean", "log_prob_mean"):
            if key in expected_metrics:
                assert observed_metrics.get(key) == pytest.approx(
                    expected_metrics[key], rel=5e-2, abs=5e-3
                )

    dataset_config = ReplayDatasetConfig.from_capture_dir(
        capture_dir,
        batch_size=1,
        shuffle=True,
        seed=7,
    )
    harness = TrainingHarness(load_config(config_path))
    log_path = capture_dir / "ppo_log.jsonl"
    summary = harness.run_ppo(dataset_config, epochs=1, log_path=log_path)

    aggregated_expected = _aggregate_expected_metrics(scenario_stats)
    _assert_ppo_log_schema(summary, require_baseline=True)
    assert summary["baseline_sample_count"] == pytest.approx(
        aggregated_expected["sample_count"], rel=5e-2, abs=5e-3
    )
    assert summary["baseline_reward_sum"] == pytest.approx(
        aggregated_expected["reward_sum"], rel=5e-2, abs=5e-3
    )
    assert "baseline_reward_sum_mean" in summary
    assert summary["baseline_reward_sum_mean"] == pytest.approx(
        aggregated_expected["reward_sum_mean"], rel=5e-2, abs=5e-3
    )
    assert summary["baseline_reward_mean"] == pytest.approx(
        aggregated_expected["reward_mean"], rel=5e-2, abs=5e-3
    )
    if "log_prob_mean" in aggregated_expected and "baseline_log_prob_mean" in summary:
        assert summary["baseline_log_prob_mean"] == pytest.approx(
            aggregated_expected["log_prob_mean"], rel=5e-2, abs=5e-3
        )

    for metric_key in (
        "loss_policy",
        "loss_value",
        "loss_total",
        "loss_entropy",
        "clip_fraction",
        "adv_mean",
        "adv_std",
        "grad_norm",
    ):
        assert metric_key in summary
        assert math.isfinite(summary[metric_key])
    assert summary["transitions"] > 0
    for social_key in (
        "shared_meal_events",
        "late_help_events",
        "shift_takeover_events",
        "chat_success_events",
        "chat_failure_events",
        "chat_quality_mean",
    ):
        assert social_key in summary
        assert math.isfinite(float(summary[social_key]))

    log_contents = log_path.read_text().strip()
    assert log_contents
    log_lines = log_contents.splitlines()
    assert len(log_lines) == 1
    logged_summary = json.loads(log_lines[0])
    _assert_ppo_log_schema(logged_summary, require_baseline=True)
    for key in (
        "baseline_sample_count",
        "baseline_reward_sum",
        "baseline_reward_mean",
        "loss_policy",
    ):
        assert logged_summary[key] == pytest.approx(summary[key], rel=5e-2, abs=5e-3)


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_training_harness_run_ppo(tmp_path: Path) -> None:
    sample_a = _make_sample(tmp_path, 0.2, 0.3, 'ppo_a')
    sample_b = _make_sample(tmp_path, 0.5, 0.2, 'ppo_b')
    dataset_config = ReplayDatasetConfig(
        entries=[sample_a, sample_b],
        batch_size=2,
        shuffle=False,
    )
    harness = TrainingHarness(load_config(Path('configs/examples/poc_hybrid.yaml')))
    log_path = tmp_path / 'ppo_log.jsonl'
    summary = harness.run_ppo(dataset_config, epochs=2, log_path=log_path)
    _assert_ppo_log_schema(summary, require_baseline=False)
    assert summary['epoch'] == 2.0
    assert 'loss_total' in summary
    assert summary['transitions'] == pytest.approx(4.0)
    assert summary['data_mode'] == 'replay'
    assert summary['cycle_id'] == pytest.approx(0.0)
    assert summary['rollout_ticks'] == pytest.approx(0.0)
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 2
    last = json.loads(lines[-1])
    assert last['epoch'] == 2.0
    assert 'loss_policy' in last
    assert last['data_mode'] == 'replay'


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_training_harness_log_sampling_and_rotation(tmp_path: Path) -> None:
    sample = _make_sample(tmp_path, 0.2, 0.3, "sample")
    dataset_config = ReplayDatasetConfig(
        entries=[sample],
        batch_size=1,
        shuffle=False,
    )
    log_path = tmp_path / "ppo_log.jsonl"

    harness = TrainingHarness(load_config(Path("configs/examples/poc_hybrid.yaml")))
    harness.run_ppo(
        dataset_config,
        epochs=3,
        log_path=log_path,
        log_frequency=2,
    )
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["epoch"] == 2.0

    log_path.unlink()

    harness = TrainingHarness(load_config(Path("configs/examples/poc_hybrid.yaml")))
    harness.run_ppo(
        dataset_config,
        epochs=3,
        log_path=log_path,
        log_frequency=1,
        max_log_entries=1,
    )
    base_lines = log_path.read_text().strip().splitlines()
    assert len(base_lines) == 1
    assert json.loads(base_lines[0])["epoch"] == 1.0

    rotated_one = log_path.with_name(f"{log_path.name}.1")
    rotated_two = log_path.with_name(f"{log_path.name}.2")
    assert rotated_one.exists()
    assert rotated_two.exists()
    assert json.loads(rotated_one.read_text().strip().splitlines()[-1])["epoch"] == 2.0
    assert json.loads(rotated_two.read_text().strip().splitlines()[-1])["epoch"] == 3.0


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_training_harness_run_rollout_ppo(tmp_path: Path) -> None:
    harness = TrainingHarness(load_config(Path("configs/scenarios/observation_baseline.yaml")))
    log_path = tmp_path / "rollout_ppo.jsonl"
    summary = harness.run_rollout_ppo(
        ticks=3,
        batch_size=1,
        epochs=1,
        log_path=log_path,
    )
    _assert_ppo_log_schema(summary, require_baseline=True)
    assert log_path.exists()
    logged = json.loads(log_path.read_text().strip().splitlines()[-1])
    _assert_ppo_log_schema(logged, require_baseline=True)
    assert summary["data_mode"] == "rollout"
    assert logged["data_mode"] == "rollout"


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_training_harness_ppo_conflict_telemetry(tmp_path: Path) -> None:
    sample = _make_sample(tmp_path, 0.4, 0.2, "telemetry")
    dataset_config = ReplayDatasetConfig(entries=[sample], batch_size=1, shuffle=False)
    harness = TrainingHarness(load_config(Path("configs/examples/poc_hybrid.yaml")))
    log_path = tmp_path / "ppo_conflict.jsonl"

    summary = harness.run_ppo(
        dataset_config=dataset_config,
        epochs=1,
        log_path=log_path,
        log_frequency=1,
    )

    _assert_ppo_log_schema(summary, require_baseline=False)
    conflict_keys = {
        "conflict.rivalry_max_mean_avg",
        "conflict.rivalry_max_max_avg",
        "conflict.rivalry_avoid_count_mean_avg",
        "conflict.rivalry_avoid_count_max_avg",
    }
    missing = conflict_keys - summary.keys()
    assert not missing, f"Missing conflict telemetry keys: {sorted(missing)}"
    for key in conflict_keys:
        _validate_numeric(summary[key])

    numeric_expectations = (
        "epoch_duration_sec",
        "batch_entropy_mean",
        "batch_entropy_std",
        "grad_norm_max",
        "kl_divergence_max",
        "reward_advantage_corr",
        "rollout_ticks",
        "queue_conflict_events",
        "queue_conflict_intensity_sum",
    )
    for key in numeric_expectations:
        _validate_numeric(summary[key])

    assert summary["data_mode"] == "replay"
    assert summary["cycle_id"] == pytest.approx(0.0)
    assert summary["log_stream_offset"] == pytest.approx(1.0)

    log_lines = log_path.read_text().strip().splitlines()
    assert len(log_lines) == 1
    logged_summary = json.loads(log_lines[0])
    _assert_ppo_log_schema(logged_summary, require_baseline=False)
    for key in conflict_keys:
        assert key in logged_summary
        _validate_numeric(logged_summary[key])
    for key in numeric_expectations:
        _validate_numeric(logged_summary[key])
    assert logged_summary["data_mode"] == "replay"


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_training_harness_run_rollout_ppo_multiple_cycles(tmp_path: Path) -> None:
    harness = TrainingHarness(load_config(Path("configs/scenarios/observation_baseline.yaml")))
    summaries: list[dict[str, float]] = []

    for cycle in range(3):
        log_path = tmp_path / f"rollout_ppo_cycle_{cycle}.jsonl"
        summary = harness.run_rollout_ppo(
            ticks=4,
            batch_size=1,
            epochs=2,
            log_path=log_path,
            log_frequency=1,
            max_log_entries=4,
        )
        _assert_ppo_log_schema(summary, require_baseline=True)
        assert summary["epoch"] == 2.0
        assert summary["transitions"] > 0.0
        assert summary["baseline_sample_count"] >= 1.0
        assert summary["data_mode"] == "rollout"
        assert summary["rollout_ticks"] == pytest.approx(4.0)
        assert summary["cycle_id"] == pytest.approx(float(cycle))

        log_lines = log_path.read_text().strip().splitlines()
        assert len(log_lines) == 2
        last_entry = json.loads(log_lines[-1])
        _assert_ppo_log_schema(last_entry, require_baseline=True)
        assert last_entry["epoch"] == 2.0
        assert last_entry["baseline_reward_sum"] == pytest.approx(
            summary["baseline_reward_sum"], rel=1e-5, abs=1e-6
        )
        assert last_entry["data_mode"] == "rollout"
        summaries.append(summary)

    baseline_counts = {summary["baseline_sample_count"] for summary in summaries}
    transitions_seen = {summary["transitions"] for summary in summaries}
    assert len(baseline_counts) == 1
    assert len(transitions_seen) == 1


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_training_harness_rollout_capture_and_train_cycles(tmp_path: Path) -> None:
    harness = TrainingHarness(load_config(Path("configs/scenarios/observation_baseline.yaml")))

    baseline_counts: list[float] = []
    baseline_reward_sums: list[float] = []
    transitions_seen: list[float] = []

    for cycle in range(3):
        buffer = harness.capture_rollout(ticks=4)
        assert not buffer.is_empty()

        dataset = buffer.build_dataset(batch_size=1)
        baseline_metrics = getattr(dataset, "baseline_metrics", {})
        assert baseline_metrics.get("sample_count", 0.0) >= 1.0

        log_path = tmp_path / f"continuous_rollout_{cycle}.jsonl"
        summary = harness.run_ppo(
            epochs=1,
            log_path=log_path,
            log_frequency=1,
            max_log_entries=1,
            in_memory_dataset=dataset,
        )

        _assert_ppo_log_schema(summary, require_baseline=True)
        assert summary["transitions"] > 0.0
        assert summary["data_mode"] == "rollout"
        assert summary["cycle_id"] == pytest.approx(float(cycle))

        baseline_counts.append(summary["baseline_sample_count"])
        baseline_reward_sums.append(summary["baseline_reward_sum"])
        transitions_seen.append(summary["transitions"])

        expected_sum = baseline_metrics.get("reward_sum", 0.0)
        assert summary["baseline_reward_sum"] == pytest.approx(
            expected_sum,
            rel=1e-5,
            abs=1e-6,
        )
        expected_sum_mean = baseline_metrics.get("reward_sum_mean")
        if expected_sum_mean is not None:
            assert summary["baseline_reward_sum_mean"] == pytest.approx(
                expected_sum_mean,
                rel=1e-5,
                abs=1e-6,
            )

        log_lines = log_path.read_text().strip().splitlines()
        assert len(log_lines) == 1
        logged = json.loads(log_lines[-1])
        _assert_ppo_log_schema(logged, require_baseline=True)
        assert logged["epoch"] == 1.0
        assert logged["baseline_reward_sum"] == pytest.approx(
            summary["baseline_reward_sum"],
            rel=1e-5,
            abs=1e-6,
        )
        assert logged["data_mode"] == "rollout"

    assert len(set(baseline_counts)) == 1
    assert len(set(baseline_reward_sums)) == 1
    assert len(set(transitions_seen)) == 1


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_training_harness_streaming_log_offsets(tmp_path: Path) -> None:
    sample = _make_sample(tmp_path, 0.1, 0.2, "stream")
    dataset_config = ReplayDatasetConfig(entries=[sample], batch_size=1, shuffle=False)
    harness = TrainingHarness(load_config(Path("configs/examples/poc_hybrid.yaml")))
    log_path = tmp_path / "streaming.jsonl"

    summary_replay = harness.run_ppo(
        dataset_config=dataset_config,
        epochs=1,
        log_path=log_path,
        log_frequency=1,
    )
    _assert_ppo_log_schema(summary_replay, require_baseline=False)
    assert summary_replay["data_mode"] == "replay"
    assert summary_replay["log_stream_offset"] == pytest.approx(1.0)

    summary_rollout = harness.run_rollout_ppo(
        ticks=2,
        batch_size=1,
        auto_seed_agents=True,
        epochs=1,
        log_path=log_path,
        log_frequency=1,
    )
    _assert_ppo_log_schema(summary_rollout, require_baseline=True)
    assert summary_rollout["data_mode"] == "rollout"
    assert summary_rollout["cycle_id"] == pytest.approx(0.0)
    assert summary_rollout["log_stream_offset"] == pytest.approx(2.0)

    buffer = harness.capture_rollout(ticks=2, auto_seed_agents=True)
    dataset_mixed = buffer.build_dataset(batch_size=1)
    summary_mixed = harness.run_ppo(
        dataset_config=dataset_config,
        in_memory_dataset=dataset_mixed,
        epochs=1,
        log_path=log_path,
        log_frequency=1,
    )
    _assert_ppo_log_schema(summary_mixed, require_baseline=True)
    assert summary_mixed["data_mode"] == "mixed"
    assert summary_mixed["cycle_id"] == pytest.approx(1.0)
    assert summary_mixed["log_stream_offset"] == pytest.approx(3.0)

    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 3
    offsets = [json.loads(line)["log_stream_offset"] for line in lines]
    assert offsets == [1.0, 2.0, 3.0]


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_training_harness_rollout_queue_conflict_metrics(tmp_path: Path) -> None:
    harness = TrainingHarness(load_config(Path("configs/scenarios/queue_conflict.yaml")))
    log_path = tmp_path / "queue_conflict_log.jsonl"
    summary = harness.run_rollout_ppo(
        ticks=40,
        batch_size=2,
        epochs=1,
        log_path=log_path,
    )
    _assert_ppo_log_schema(summary, require_baseline=True)
    assert summary["data_mode"] == "rollout"
    assert summary["queue_conflict_events"] >= 1.0
    assert summary["queue_conflict_intensity_sum"] > 0.0

    logged = json.loads(log_path.read_text().strip())
    _assert_ppo_log_schema(logged, require_baseline=True)
    assert logged["queue_conflict_events"] == pytest.approx(
        summary["queue_conflict_events"], rel=1e-5
    )
    assert logged["queue_conflict_intensity_sum"] == pytest.approx(
        summary["queue_conflict_intensity_sum"], rel=1e-5
    )


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_ppo_social_chat_drift(tmp_path: Path) -> None:
    import torch

    sample = _make_social_sample()
    dataset = InMemoryReplayDataset(
        InMemoryReplayDatasetConfig(entries=[sample], batch_size=1)
    )
    dataset.baseline_metrics = sample.metadata.get("metrics", {}) | {"sample_count": 1.0}
    dataset.chat_success_count = 1.0
    dataset.chat_failure_count = 0.0
    dataset.chat_quality_mean = 0.8

    harness = TrainingHarness(load_config(Path("configs/examples/poc_hybrid.yaml")))
    torch.manual_seed(0)
    log_path = tmp_path / "social_chat.jsonl"
    summary = harness.run_ppo(
        in_memory_dataset=dataset,
        epochs=1,
        log_path=log_path,
        log_frequency=1,
    )

    golden_path = Path("tests/golden/ppo_social/baseline.json")
    expected = json.loads(golden_path.read_text())
    for key, value in expected.items():
        assert summary[key] == pytest.approx(value, rel=1e-5, abs=1e-6)

    logged_lines = log_path.read_text().strip().splitlines()
    assert logged_lines, "PPO log should contain at least one entry"
    logged = json.loads(logged_lines[-1])
    for key, value in expected.items():
        assert logged[key] == pytest.approx(value, rel=1e-5, abs=1e-6)

    assert summary["chat_success_events"] == pytest.approx(dataset.chat_success_count)
    assert summary["chat_failure_events"] == pytest.approx(dataset.chat_failure_count)
    assert summary["chat_quality_mean"] == pytest.approx(dataset.chat_quality_mean)


def test_policy_runtime_collects_frames(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.register_object(object_id="stove_1", object_type="stove")
    loop.world.agents["alice"] = AgentSnapshot(
        "alice",
        (0, 0),
        {"hunger": 0.3, "hygiene": 0.5, "energy": 0.4},
        wallet=1.0,
    )
    loop.world.agents["bob"] = AgentSnapshot(
        "bob",
        (1, 0),
        {"hunger": 0.6, "hygiene": 0.6, "energy": 0.7},
        wallet=1.5,
    )

    for _ in range(3):
        loop.step()

    frames = [frame for frame in loop.policy.collect_trajectory() if frame["agent_id"] == "alice"]
    assert len(frames) == 3
    sample = frames_to_replay_sample(frames)
    assert sample.map.shape[0] == 3
    assert sample.features.shape[0] == 3
    assert sample.actions.shape[0] == 3
    assert sample.value_preds.shape[0] == 4
    assert sample.metadata["timesteps"] == 3
    assert "action_lookup" in sample.metadata
    if torch_available():
        assert not np.allclose(sample.old_log_probs, 0.0)
        assert not np.allclose(sample.value_preds[:-1], 0.0)
    else:
        assert np.allclose(sample.old_log_probs, 0.0)
