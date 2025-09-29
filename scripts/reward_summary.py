"""Summarise reward breakdown telemetry for operations teams."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

Number = float | int


@dataclass
class ComponentStats:
    count: int = 0
    total: float = 0.0
    minimum: float = float("inf")
    maximum: float = float("-inf")

    def update(self, value: float) -> None:
        self.count += 1
        self.total += value
        if value < self.minimum:
            self.minimum = value
        if value > self.maximum:
            self.maximum = value

    def mean(self) -> float:
        if not self.count:
            return 0.0
        return self.total / self.count

    def as_dict(self) -> dict[str, float | int]:
        if not self.count:
            return {"count": 0, "mean": 0.0, "min": 0.0, "max": 0.0}
        return {
            "count": self.count,
            "mean": self.mean(),
            "min": self.minimum,
            "max": self.maximum,
        }


class RewardAggregator:
    """Aggregate reward breakdowns from telemetry payloads."""

    def __init__(self) -> None:
        self.component_stats: dict[str, ComponentStats] = defaultdict(ComponentStats)
        self.agent_totals: dict[str, float] = defaultdict(float)
        self.agent_counts: dict[str, int] = defaultdict(int)
        self.agent_latest: dict[str, dict[str, float]] = {}
        self.payloads: int = 0
        self.records_with_rewards: int = 0
        self.missing_sources: list[str] = []

    def add_payload(self, payload: Mapping[str, object], source: str) -> None:
        self.payloads += 1
        breakdown = payload.get("reward_breakdown")
        if not isinstance(breakdown, Mapping):
            self.missing_sources.append(source)
            return
        processed = False
        for agent_id, components in breakdown.items():
            if not isinstance(components, Mapping):
                continue
            processed = True
            numeric_components: dict[str, float] = {}
            for key, value in components.items():
                if isinstance(value, (int, float)):
                    numeric_value = float(value)
                    numeric_components[key] = numeric_value
                    self.component_stats[key].update(numeric_value)
                    if key == "total":
                        self.agent_totals[agent_id] += numeric_value
            if numeric_components:
                self.agent_counts[agent_id] += 1
                self.agent_latest[agent_id] = numeric_components
        if processed:
            self.records_with_rewards += 1
        else:
            self.missing_sources.append(source)

    def summary(self) -> dict[str, object]:
        components = {
            name: stats.as_dict() for name, stats in sorted(self.component_stats.items())
        }
        agents: dict[str, dict[str, object]] = {}
        for agent_id, count in sorted(self.agent_counts.items()):
            total = self.agent_totals.get(agent_id, 0.0)
            agents[agent_id] = {
                "samples": count,
                "total_sum": total,
                "total_mean": total / count if count else 0.0,
                "latest": self.agent_latest.get(agent_id, {}),
            }
        return {
            "payloads": self.payloads,
            "records_with_reward_breakdown": self.records_with_rewards,
            "agents_seen": len(agents),
            "components": components,
            "agents": agents,
            "missing_sources": self.missing_sources,
        }


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float))


def iter_payloads(path: Path) -> Iterator[tuple[Mapping[str, object], str]]:
    text = path.read_text()
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        for idx, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if isinstance(payload, Mapping):
                yield payload, f"{path}:{idx}"
            else:
                raise ValueError(f"{path}:{idx}: expected JSON object")
    else:
        data = json.loads(text)
        if isinstance(data, Mapping):
            yield data, str(path)
        elif isinstance(data, Sequence):
            for idx, item in enumerate(data):
                if isinstance(item, Mapping):
                    yield item, f"{path}[{idx}]"
                else:
                    raise ValueError(f"{path}[{idx}] expected JSON object")
        else:
            raise ValueError(f"{path}: expected JSON object or array")


def collect_statistics(paths: Sequence[Path]) -> RewardAggregator:
    aggregator = RewardAggregator()
    for path in paths:
        for payload, source in iter_payloads(path):
            aggregator.add_payload(payload, source)
    return aggregator


def render_text(summary: Mapping[str, object], *, top: int, agent_filters: set[str] | None) -> str:
    lines: list[str] = []
    lines.append(
        "Payloads processed: {payloads} | records with reward_breakdown: {records}".format(
            payloads=summary.get("payloads", 0),
            records=summary.get("records_with_reward_breakdown", 0),
        )
    )
    lines.append(f"Agents observed: {summary.get('agents_seen', 0)}")

    components = summary.get("components", {})
    if components:
        lines.append("Component summary (mean over samples):")
        for name, stats in components.items():
            count = stats.get("count", 0)
            mean = stats.get("mean", 0.0)
            minimum = stats.get("min", 0.0)
            maximum = stats.get("max", 0.0)
            lines.append(
                f"  - {name}: mean={mean:.6f} (min={minimum:.6f}, max={maximum:.6f}, samples={count})"
            )
    else:
        lines.append("Component summary: no reward breakdown entries found.")

    agents = summary.get("agents", {})
    agent_filters = agent_filters or set()
    if agent_filters:
        lines.append("Filtered agents:")
        for agent_id in sorted(agent_filters):
            info = agents.get(agent_id)
            if info is None:
                lines.append(f"  - {agent_id}: no samples")
                continue
            latest = info.get("latest", {})
            latest_parts = ", ".join(
                f"{key}={value:.6f}" for key, value in sorted(latest.items())
            )
            lines.append(
                "  - {agent}: avg_total={avg:.6f} (samples={count}) :: {details}".format(
                    agent=agent_id,
                    avg=info.get("total_mean", 0.0),
                    count=info.get("samples", 0),
                    details=latest_parts or "no numeric components",
                )
            )
    elif agents:
        agent_items = list(agents.items())
        sorted_by_total = sorted(agent_items, key=lambda item: item[1].get("total_mean", 0.0))
        worst = sorted_by_total[:top]
        best = list(reversed(sorted_by_total[-top:]))
        lines.append("Top negative average totals:")
        for agent_id, info in worst:
            lines.append(
                f"  - {agent_id}: avg_total={info.get('total_mean', 0.0):.6f} (samples={info.get('samples', 0)})"
            )
        lines.append("Top positive average totals:")
        for agent_id, info in best:
            lines.append(
                f"  - {agent_id}: avg_total={info.get('total_mean', 0.0):.6f} (samples={info.get('samples', 0)})"
            )

    missing = summary.get("missing_sources", [])
    if missing:
        preview = ", ".join(list(missing)[:3])
        more = len(missing) - 3
        if more > 0:
            preview += f", … ({more} more)"
        lines.append(f"Payloads without reward_breakdown: {len(missing)} :: {preview}")

    return "\n".join(lines)


def render_markdown(summary: Mapping[str, object], *, top: int, agent_filters: set[str] | None) -> str:
    lines: list[str] = []
    lines.append(f"**Payloads** | {summary.get('payloads', 0)}")
    lines.append(f"**Records** | {summary.get('records_with_reward_breakdown', 0)}")
    lines.append(f"**Agents Observed** | {summary.get('agents_seen', 0)}")
    lines.append("\n| Component | Mean | Min | Max | Samples |")
    lines.append("| --- | --- | --- | --- | --- |")
    components = summary.get("components", {})
    for name, stats in components.items():
        lines.append(
            "| {name} | {mean:.6f} | {min:.6f} | {max:.6f} | {count} |".format(
                name=name,
                mean=stats.get("mean", 0.0),
                min=stats.get("min", 0.0),
                max=stats.get("max", 0.0),
                count=stats.get("count", 0),
            )
        )
    agents = summary.get("agents", {})
    if agent_filters:
        lines.append("\n**Filtered Agents**")
        for agent_id in sorted(agent_filters):
            info = agents.get(agent_id)
            if info is None:
                lines.append(f"- {agent_id}: no samples")
                continue
            latest = info.get("latest", {})
            latest_parts = ", ".join(
                f"`{key}={value:.6f}`" for key, value in sorted(latest.items())
            )
            lines.append(
                "- {agent}: avg_total={avg:.6f} (samples={samples}) — {parts}".format(
                    agent=agent_id,
                    avg=info.get("total_mean", 0.0),
                    samples=info.get("samples", 0),
                    parts=latest_parts or "no numeric components",
                )
            )
    elif agents:
        agent_items = list(agents.items())
        worst = sorted(agent_items, key=lambda item: item[1].get("total_mean", 0.0))[:top]
        best = list(reversed(sorted(agent_items, key=lambda item: item[1].get("total_mean", 0.0))[-top:]))
        lines.append("\n**Top Negative Totals**")
        for agent_id, info in worst:
            lines.append(
                f"- {agent_id}: avg_total={info.get('total_mean', 0.0):.6f} (samples={info.get('samples', 0)})"
            )
        lines.append("\n**Top Positive Totals**")
        for agent_id, info in best:
            lines.append(
                f"- {agent_id}: avg_total={info.get('total_mean', 0.0):.6f} (samples={info.get('samples', 0)})"
            )
    return "\n".join(lines)


def render_json(summary: Mapping[str, object]) -> str:
    return json.dumps(summary, indent=2, sort_keys=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarise reward breakdown telemetry")
    parser.add_argument("paths", nargs="+", type=Path, help="Telemetry JSON/JSONL files to analyse")
    parser.add_argument(
        "--format",
        choices={"text", "markdown", "json"},
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--agent",
        action="append",
        dest="agents",
        help="Limit output to specific agent IDs (can be repeated)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of agents to show in top/bottom lists (default: 5)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = collect_statistics(args.paths).summary()
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1

    agent_filters = set(args.agents or [])
    top = max(1, int(args.top))

    if args.format == "text":
        output = render_text(summary, top=top, agent_filters=agent_filters)
    elif args.format == "markdown":
        output = render_markdown(summary, top=top, agent_filters=agent_filters)
    else:
        output = render_json(summary)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
