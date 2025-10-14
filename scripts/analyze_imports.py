#!/usr/bin/env python3
"""Generate CSV matrix of all package-to-package imports.

This script analyzes the townlet codebase and produces a matrix showing
the import relationships between packages. Used for WP5 Phase 4 baseline analysis.

Usage:
    python scripts/analyze_imports.py > docs/architecture_review/WP5_PHASE4_import_matrix.csv
"""

import ast
from collections import defaultdict
from pathlib import Path


def find_imports(file_path: Path) -> set[str]:
    """Extract all townlet imports from a Python file.

    Args:
        file_path: Path to Python source file

    Returns:
        Set of top-level package names (e.g., {"townlet.world", "townlet.dto"})
    """
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        # Skip files that can't be parsed
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("townlet."):
                # Extract top-level package (e.g., "townlet.world" from "townlet.world.grid")
                parts = node.module.split(".")
                if len(parts) >= 2:
                    pkg = ".".join(parts[:2])
                    imports.add(pkg)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("townlet."):
                    parts = alias.name.split(".")
                    if len(parts) >= 2:
                        pkg = ".".join(parts[:2])
                        imports.add(pkg)
    return imports


def main():
    """Generate import matrix CSV."""
    src_dir = Path("src/townlet")

    # Define packages to analyze
    packages = [
        "dto",
        "ports",
        "core",
        "config",
        "world",
        "policy",
        "telemetry",
        "rewards",
        "observations",
        "snapshots",
        "stability",
        "lifecycle",
        "benchmark",
        "agents",
        "utils",
        "factories",
    ]

    # Build import matrix: matrix[from_pkg][to_pkg] = count
    matrix = defaultdict(lambda: defaultdict(int))

    for pkg in packages:
        pkg_dir = src_dir / pkg
        if not pkg_dir.exists():
            continue

        # Find all Python files in package
        for py_file in pkg_dir.rglob("*.py"):
            # Skip test files
            if py_file.name.startswith("test_"):
                continue
            if "tests" in py_file.parts:
                continue

            imports = find_imports(py_file)
            for imported_pkg in imports:
                # Extract package name after townlet.
                imported_name = imported_pkg.split(".")[1] if "." in imported_pkg else imported_pkg
                # Only count cross-package imports
                if imported_name != pkg and imported_name in packages:
                    matrix[pkg][imported_name] += 1

    # Output CSV header
    print("From/To," + ",".join(packages))

    # Output each row
    for from_pkg in packages:
        counts = [str(matrix[from_pkg][to_pkg]) if matrix[from_pkg][to_pkg] > 0 else "" for to_pkg in packages]
        print(f"{from_pkg}," + ",".join(counts))


if __name__ == "__main__":
    main()
