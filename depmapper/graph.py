from __future__ import annotations

import re
from collections import defaultdict, deque

from .extract import TableRefs


class CycleError(Exception):
    """Raised when the notebooks form a circular dependency."""


def _slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


class DependencyGraph:
    def __init__(self) -> None:
        self.notebooks: dict[str, TableRefs] = {}

    def add(self, name: str, refs: TableRefs) -> None:
        self.notebooks[name] = refs

    def producers(self) -> dict[str, str]:
        """Map each written table to the notebook that produces it."""
        producer: dict[str, str] = {}
        for name, refs in self.notebooks.items():
            for table in refs.writes:
                producer[table] = name
        return producer

    def dependencies(self) -> dict[str, set[str]]:
        """For each notebook, the set of notebooks it depends on."""
        producer = self.producers()
        deps: dict[str, set[str]] = {name: set() for name in self.notebooks}
        for name, refs in self.notebooks.items():
            for table in refs.reads:
                src = producer.get(table)
                if src and src != name:
                    deps[name].add(src)
        return deps

    def edges(self) -> set[tuple[str, str]]:
        return {(src, name) for name, srcs in self.dependencies().items() for src in srcs}

    def topological_levels(self) -> list[list[str]]:
        """Group notebooks into execution levels (each level can run in parallel)."""
        deps = self.dependencies()
        remaining = {name: len(ds) for name, ds in deps.items()}
        children: dict[str, list[str]] = defaultdict(list)
        for name, ds in deps.items():
            for d in ds:
                children[d].append(name)

        levels: list[list[str]] = []
        ready = deque(sorted(n for n, deg in remaining.items() if deg == 0))
        done = 0
        while ready:
            level = sorted(ready)
            levels.append(level)
            nxt: list[str] = []
            for name in level:
                done += 1
                for child in children[name]:
                    remaining[child] -= 1
                    if remaining[child] == 0:
                        nxt.append(child)
            ready = deque(nxt)

        if done != len(self.notebooks):
            stuck = sorted(n for n, deg in remaining.items() if deg > 0)
            raise CycleError(f"Circular dependency involving: {', '.join(stuck)}")
        return levels

    def to_activities(self) -> list[dict[str, str]]:
        """Flat table of notebook, reads, writes and dependencies (orchestration config)."""
        deps = self.dependencies()
        rows = []
        for name in sorted(self.notebooks):
            refs = self.notebooks[name]
            rows.append(
                {
                    "notebook": name,
                    "reads": ",".join(sorted(refs.reads)),
                    "writes": ",".join(sorted(refs.writes)),
                    "dependencies": ",".join(sorted(deps[name])),
                }
            )
        return rows

    def to_mermaid(self) -> str:
        edges = sorted(self.edges())
        lines = ["flowchart LR"]
        connected: set[str] = set()
        for src, dst in edges:
            lines.append(f"    {_slug(src)}[{src}] --> {_slug(dst)}[{dst}]")
            connected.update((src, dst))
        for name in sorted(self.notebooks):
            if name not in connected:
                lines.append(f"    {_slug(name)}[{name}]")
        return "\n".join(lines)
