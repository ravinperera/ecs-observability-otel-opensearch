#!/usr/bin/env python3
"""Run safe, offline validation for repository examples.

Checks:
- JSON files parse with the Python standard library.
- YAML files parse with PyYAML safe_load_all.
- Markdown files are UTF-8 and have balanced fenced code blocks.

This script intentionally does not contact AWS, OpenSearch, or collector services.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency setup failure
    raise SystemExit(
        "PyYAML is required. Install it with "
        "`python3 -m pip install PyYAML==6.0.2`."
    ) from exc


EXCLUDED_PARTS = {".git", ".venv", "node_modules", "__pycache__"}
ValidationFunction = Callable[[Path], list[str]]


def repository_files(root: Path, suffixes: set[str]) -> Iterable[Path]:
    """Yield matching files while skipping generated directories."""
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in EXCLUDED_PARTS for part in relative_parts):
            continue
        yield path


def validate_json(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"invalid JSON: {exc}"]
    return []


def validate_yaml(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            list(yaml.safe_load_all(handle))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return [f"invalid YAML: {exc}"]
    return []


def validate_markdown(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"cannot read Markdown as UTF-8: {exc}"]

    errors: list[str] = []
    if "\x00" in text:
        errors.append("contains a NUL byte")

    active_fence: str | None = None
    active_line = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        marker = None
        if stripped.startswith("```"):
            marker = "```"
        elif stripped.startswith("~~~"):
            marker = "~~~"

        if marker is None:
            continue
        if active_fence is None:
            active_fence = marker
            active_line = line_number
        elif active_fence == marker:
            active_fence = None
            active_line = 0

    if active_fence is not None:
        errors.append(
            f"line {active_line}: unclosed Markdown fence starting with {active_fence}"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate repository examples without live-service access."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current directory.",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    validators: dict[str, ValidationFunction] = {
        ".json": validate_json,
        ".yaml": validate_yaml,
        ".yml": validate_yaml,
        ".md": validate_markdown,
    }
    counts = {suffix: 0 for suffix in validators}
    errors: list[str] = []

    for path in repository_files(root, set(validators)):
        suffix = path.suffix.lower()
        counts[suffix] += 1
        relative_path = path.relative_to(root)
        errors.extend(
            f"{relative_path}: {error}" for error in validators[suffix](path)
        )

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    yaml_count = counts[".yaml"] + counts[".yml"]
    print(
        "Validation passed: "
        f"{counts['.json']} JSON, {yaml_count} YAML, "
        f"and {counts['.md']} Markdown files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
