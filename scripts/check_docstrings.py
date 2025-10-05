#!/usr/bin/env python
"""Docstring coverage checker used by WP-307 tooling.

This script scans Python modules, reports module and callable docstring
coverage, and can enforce minimum thresholds. It intentionally avoids external
packages so it runs inside the Townlet sandbox.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass
class ModuleStat:
    path: Path
    has_docstring: bool


@dataclass
class CallableStat:
    name: str
    has_docstring: bool


@dataclass
class CoverageReport:
    modules: list[ModuleStat]
    callables: list[CallableStat]

    @property
    def module_total(self) -> int:
        return len(self.modules)

    @property
    def module_with_doc(self) -> int:
        return sum(1 for entry in self.modules if entry.has_docstring)

    @property
    def callable_total(self) -> int:
        return len(self.callables)

    @property
    def callable_with_doc(self) -> int:
        return sum(1 for entry in self.callables if entry.has_docstring)

    def to_dict(self) -> dict[str, float | int | list[dict[str, str | bool]]]:
        return {
            "module_total": self.module_total,
            "module_with_doc": self.module_with_doc,
            "module_coverage_pct": percentage(self.module_with_doc, self.module_total),
            "callable_total": self.callable_total,
            "callable_with_doc": self.callable_with_doc,
            "callable_coverage_pct": percentage(self.callable_with_doc, self.callable_total),
            "modules": [
                {"path": str(entry.path), "has_docstring": entry.has_docstring}
                for entry in self.modules
            ],
            "callables": [
                {"name": entry.name, "has_docstring": entry.has_docstring}
                for entry in self.callables
            ],
        }


def percentage(numerator: int, denominator: int) -> float:
    return round((numerator / denominator * 100.0) if denominator else 0.0, 2)


def collect_stats(paths: Sequence[Path]) -> CoverageReport:
    modules: list[ModuleStat] = []
    callables: list[CallableStat] = []

    for base in paths:
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            modules.append(
                ModuleStat(
                    path=path,
                    has_docstring=_has_module_docstring(path),
                )
            )
            callables.extend(_collect_callable_stats(path))
    return CoverageReport(modules=modules, callables=callables)


def _has_module_docstring(path: Path) -> bool:
    tree = _parse(path)
    return bool(ast.get_docstring(tree, clean=False))


def _collect_callable_stats(path: Path) -> Iterable[CallableStat]:
    tree = _parse(path)
    _attach_parents(tree)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            qualname = _qualname(node)
            leaf_name = qualname.split(".")[-1]
            if leaf_name.startswith("_"):
                continue
            has_doc = bool(ast.get_docstring(node, clean=False))
            yield CallableStat(name=f"{path}:{qualname}", has_docstring=has_doc)


def _parse(path: Path) -> ast.AST:
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        source = path.read_text()
    return ast.parse(source, filename=str(path))


def _qualname(node: ast.AST) -> str:
    components: list[str] = []
    current: ast.AST | None = node
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            components.append(current.name)
        current = getattr(current, "parent", None)
    return ".".join(reversed(components))


def _attach_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "parent", parent)


def render_report(report: CoverageReport) -> str:
    lines = [
        "Docstring coverage report",
        f"  Modules: {report.module_with_doc}/{report.module_total} "
        f"({percentage(report.module_with_doc, report.module_total)}%)",
        f"  Callables: {report.callable_with_doc}/{report.callable_total} "
        f"({percentage(report.callable_with_doc, report.callable_total)}%)",
        "",
    ]
    missing_modules = [entry for entry in report.modules if not entry.has_docstring]
    if missing_modules:
        lines.append("Modules missing docstrings:")
        for entry in missing_modules:
            lines.append(f"  - {entry.path}")
        lines.append("")
    missing_callables = [entry for entry in report.callables if not entry.has_docstring][:50]
    if missing_callables:
        lines.append("Sample missing callables:")
        for entry in missing_callables:
            lines.append(f"  - {entry.name}")
        lines.append("")
    return "\n".join(lines)


def enforce_threshold(report: CoverageReport, min_module: float, min_callable: float) -> None:
    module_pct = percentage(report.module_with_doc, report.module_total)
    callable_pct = percentage(report.callable_with_doc, report.callable_total)
    failures: list[str] = []
    if module_pct < min_module:
        failures.append(
            f"Module coverage {module_pct}% fell below threshold {min_module}%"
        )
    if callable_pct < min_callable:
        failures.append(
            f"Callable coverage {callable_pct}% fell below threshold {min_callable}%"
        )
    if failures:
        for line in failures:
            print(f"ERROR: {line}", file=sys.stderr)
        raise SystemExit(1)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        default=["src/townlet"],
        help="Paths (files or directories) to scan for docstrings.",
    )
    parser.add_argument(
        "--min-module",
        type=float,
        default=0.0,
        help="Minimum acceptable module docstring coverage percentage.",
    )
    parser.add_argument(
        "--min-callable",
        type=float,
        default=0.0,
        help="Minimum acceptable callable docstring coverage percentage.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional path to write the coverage report as JSON.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print coverage summary without detailed missing lists.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    paths = [Path(path) for path in args.paths]
    for path in paths:
        if not path.exists():
            print(f"ERROR: path '{path}' does not exist", file=sys.stderr)
            return 2

    report = collect_stats(paths)
    if args.json_output:
        args.json_output.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")

    output = render_report(report)
    if args.summary_only:
        print("\n".join(output.splitlines()[:3]))
    else:
        print(output)

    enforce_threshold(report, args.min_module, args.min_callable)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    sys.exit(main())
