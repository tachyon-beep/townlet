import json
from pathlib import Path

from scripts.reward_summary import ComponentStats, collect_statistics, render_text


def test_component_stats_mean_and_extremes() -> None:
    stats = ComponentStats()
    stats.update(1.0)
    stats.update(-1.0)
    summary = stats.as_dict()
    assert summary["count"] == 2
    assert summary["mean"] == 0.0
    assert summary["min"] == -1.0
    assert summary["max"] == 1.0


def test_reward_aggregator_tracks_components(tmp_path: Path) -> None:
    payloads = [
        {
            "reward_breakdown": {
                "alice": {"survival": 0.002, "needs_penalty": -0.1, "total": -0.098},
                "bob": {"survival": 0.002, "total": 0.002},
            }
        },
        {
            "reward_breakdown": {
                "alice": {"survival": 0.002, "terminal_penalty": -1.0, "total": -0.998},
            }
        },
    ]
    path = tmp_path / "sample.json"
    path.write_text(json.dumps(payloads))

    aggregator = collect_statistics([path])
    summary = aggregator.summary()

    components = summary["components"]
    assert components["survival"]["count"] == 3
    assert components["terminal_penalty"]["count"] == 1
    agents = summary["agents"]
    assert agents["alice"]["samples"] == 2
    assert agents["bob"]["samples"] == 1

    text = render_text(summary, top=2, agent_filters=None)
    assert "terminal_penalty" in text
    assert "alice" in text
    assert "bob" in text
