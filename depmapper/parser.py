from __future__ import annotations

import json
from pathlib import Path

# Marker/metadata lines used by Fabric and Databricks notebook source files.
_MARKER_PREFIXES = ("# META", "# MAGIC", "# CELL", "# MARKDOWN", "# METADATA")


def read_notebook_code(path: str | Path) -> str:
    """Return the concatenated code of a notebook (.ipynb or .py source format)."""
    path = Path(path)
    if path.suffix == ".ipynb":
        return _read_ipynb(path)
    return _read_source(path)


def _read_ipynb(path: Path) -> str:
    nb = json.loads(path.read_text(encoding="utf-8"))
    chunks = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            source = cell.get("source", [])
            chunks.append("".join(source) if isinstance(source, list) else str(source))
    return "\n".join(chunks)


def _read_source(path: Path) -> str:
    # Fabric/Databricks `.py` notebook source: drop the metadata/marker comment lines.
    kept = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith(_MARKER_PREFIXES)
    ]
    return "\n".join(kept)
