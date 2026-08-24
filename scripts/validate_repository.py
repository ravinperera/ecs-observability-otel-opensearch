#!/usr/bin/env python3
"""Run safe, offline validation for repository examples.

Checks:
- JSON files parse with the Python standard library.
- YAML files parse with PyYAML SafeLoader semantics.
- Markdown files are UTF-8, have balanced fenced code blocks, and use valid repository-local links.

This script intentionally does not contact AWS, OpenSearch, or collector services.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency setup failure
    raise SystemExit(
        "PyYAML is required. Install it with "
        "`python3 -m pip install PyYAML==6.0.2`."
    ) from exc


EXCLUDED_PARTS = {".git", ".venv", "node_modules", "__pycache__"}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\n]+)\)")
ValidationFunction = Callable[[Path, Path], list[str]]


class UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate mapping keys."""


def _construct_unique_mapping(loader: UniqueKeySafeLoader, node: object, deep: bool = False) -> dict[object, object]:
    loader.flatten_mapping(node)
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def repository_files(root: Path, suffixes: set[str]) -> Iterable[Path]:
    """Yield matching files while skipping generated directories."""
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in EXCLUDED_PARTS for part in relative_parts):
            continue
        yield path


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build a JSON object while rejecting duplicate keys."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def validate_json(path: Path, _root: Path | None = None) -> list[str]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            json.load(handle, object_pairs_hook=reject_duplicate_json_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return [f"invalid JSON: {exc}"]
    return []


def validate_yaml(path: Path, _root: Path | None = None) -> list[str]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            list(yaml.load_all(handle, Loader=UniqueKeySafeLoader))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return [f"invalid YAML: {exc}"]
    return []


def _link_destination(raw_target: str) -> str:
    """Return a Markdown destination without an optional title."""
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split(maxsplit=1)[0] if target else ""


def validate_markdown(path: Path, root: Path | None = None) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"cannot read Markdown as UTF-8: {exc}"]

    errors: list[str] = []
    if "\x00" in text:
        errors.append("contains a NUL byte")

    repository_root = (root or path.parent).resolve()
    active_fence: str | None = None
    active_line = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        marker = None
        if stripped.startswith("```"):
            marker = "```"
        elif stripped.startswith("~~~"):
            marker = "~~~"

        if marker is not None:
            if active_fence is None:
                active_fence = marker
                active_line = line_number
            elif active_fence == marker:
                active_fence = None
                active_line = 0
            continue

        if active_fence is not None:
            continue

        for match in MARKDOWN_LINK.finditer(line):
            destination = _link_destination(match.group(1))
            if not destination or destination.startswith("#"):
                continue

            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc:
                continue

            local_target = unquote(parsed.path)
            if not local_target:
                continue

            candidate = (path.parent / local_target).resolve()
            try:
                candidate.relative_to(repository_root)
            except ValueError:
                errors.append(
                    f"line {line_number}: link target escapes repository: {destination}"
                )
                continue

            if not candidate.exists():
                errors.append(
                    f"line {line_number}: missing local link target: {destination}"
                )

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
            f"{relative_path}: {error}" for error in validators[suffix](path, root)
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
