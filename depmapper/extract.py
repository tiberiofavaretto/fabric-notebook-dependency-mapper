from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class TableRefs:
    """Tables a notebook reads (inputs) and writes (outputs), as `schema.table`."""

    reads: set[str]
    writes: set[str]


def _strip_comments(code: str) -> str:
    no_block = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    kept = []
    for line in no_block.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or stripped.startswith("#"):
            continue
        kept.append(line)
    return "\n".join(kept)


def _compile(read_schemas: list[str]) -> dict[str, re.Pattern]:
    schemas = "|".join(re.escape(s) for s in read_schemas)
    tbl = r"`?([A-Za-z0-9_]+)`?"
    schema = rf"`?({schemas})`?"
    flags = re.IGNORECASE
    return {
        "ref": re.compile(rf"\b{schema}\.{tbl}", flags),
        "create": re.compile(rf"create\s+table\s+(?:if\s+not\s+exists\s+)?{schema}\.{tbl}", flags),
        "insert": re.compile(rf"insert\s+(?:into|overwrite)\s+(?:table\s+)?{schema}\.{tbl}", flags),
        "save": re.compile(rf"""saveastable\s*\(\s*["']{schema}\.{tbl}["']""", flags),
    }


def extract_refs(code: str, read_schemas: list[str]) -> TableRefs:
    """Extract read/write table references from notebook code."""
    code = _strip_comments(code)
    patterns = _compile([s.lower() for s in read_schemas])

    def norm(match: re.Match) -> str:
        return f"{match.group(1).lower()}.{match.group(2).lower()}"

    all_refs = {norm(m) for m in patterns["ref"].finditer(code)}
    writes: set[str] = set()
    for key in ("create", "insert", "save"):
        writes |= {norm(m) for m in patterns[key].finditer(code)}

    reads = all_refs - writes
    return TableRefs(reads=reads, writes=writes)
