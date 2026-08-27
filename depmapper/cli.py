from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .config import Config
from .extract import extract_refs
from .graph import DependencyGraph
from .parser import read_notebook_code


def build_graph(folder: str, config: Config) -> DependencyGraph:
    graph = DependencyGraph()
    for path in sorted(Path(folder).rglob("*")):
        if path.is_file() and path.suffix in config.extensions:
            refs = extract_refs(read_notebook_code(path), config.read_schemas)
            graph.add(path.stem, refs)
    return graph


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="depmapper",
        description="Map table-level dependencies between data notebooks and build an execution DAG.",
    )
    parser.add_argument("folder", help="Folder containing notebooks (.py / .ipynb), scanned recursively.")
    parser.add_argument("-c", "--config", help="Optional YAML config file.")
    parser.add_argument(
        "-f",
        "--format",
        choices=["mermaid", "json", "csv", "levels"],
        default="mermaid",
        help="Output format (default: mermaid).",
    )
    args = parser.parse_args(argv)

    graph = build_graph(args.folder, Config.load(args.config))
    if not graph.notebooks:
        print(f"No notebooks found under {args.folder}", file=sys.stderr)
        return 1

    if args.format == "mermaid":
        print(graph.to_mermaid())
    elif args.format == "json":
        print(json.dumps(graph.to_activities(), indent=2))
    elif args.format == "csv":
        rows = graph.to_activities()
        writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    elif args.format == "levels":
        for i, level in enumerate(graph.topological_levels()):
            print(f"Level {i}: {', '.join(level)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
