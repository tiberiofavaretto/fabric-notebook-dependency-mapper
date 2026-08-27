from __future__ import annotations

from dataclasses import dataclass, field

# Schemas whose `schema.table` references are treated as data assets. Keeping the
# match restricted to a known set avoids matching ordinary code like `spark.read`.
DEFAULT_READ_SCHEMAS = ["bronze", "silver", "staging", "gold", "raw", "mart"]
DEFAULT_EXTENSIONS = [".py", ".ipynb"]


@dataclass
class Config:
    read_schemas: list[str] = field(default_factory=lambda: list(DEFAULT_READ_SCHEMAS))
    extensions: list[str] = field(default_factory=lambda: list(DEFAULT_EXTENSIONS))

    @classmethod
    def load(cls, path: str | None = None) -> "Config":
        if not path:
            return cls()
        import yaml  # imported lazily so the tool works without a config file

        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return cls(
            read_schemas=[s.lower() for s in data.get("read_schemas", DEFAULT_READ_SCHEMAS)],
            extensions=data.get("extensions", list(DEFAULT_EXTENSIONS)),
        )
