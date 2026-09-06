#!/usr/bin/env python3
"""Run safe, offline validation for repository examples.

Checks:
- JSON files parse with the Python standard library and reject duplicate keys.
- YAML files parse with PyYAML SafeLoader semantics and reject duplicate keys.
- OpenTelemetry collector pipelines retain the required memory_limiter and batch processors.
- Fluent Bit OpenSearch outputs retain TLS, AWS authentication, and HTTPS port settings.
- Markdown files are UTF-8, have balanced fenced code blocks, and use valid repository-local links.
- Public example files do not contain obvious high-confidence credential shapes.

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
PUBLIC_EXAMPLE_PATHS = (
    "README.md",
    "CONTRIBUTING.md",
    "docs",
    "configs",
    "ecs",
    "terraform",
)
PUBLIC_TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".tf", ".conf"}
CREDENTIAL_PATTERNS = (
    ("AWS access-key ID", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,255}\b")),
    ("OpenAI-style API key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    (
        "PEM private-key header",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
)
OTEL_CONFIG_PATH = Path("configs/otel-collector-config.yaml")
FLUENT_BIT_CONFIG_PATH = Path("configs/fluent-bit-opensearch.conf")
REQUIRED_OTEL_PROCESSORS = {"memory_limiter", "batch"}
ValidationFunction = Callable[[Path, Path], list[str]]


class UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeySafeLoader, node: object, deep: bool = False
) -> dict[object, object]:
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


def public_example_files(root: Path) -> list[Path]:
    """Return public documentation/configuration files that must stay credential-free."""
    files: set[Path] = set()
    for relative_path in PUBLIC_EXAMPLE_PATHS:
        path = root / relative_path
        if path.is_file() and path.suffix.lower() in PUBLIC_TEXT_SUFFIXES:
            files.add(path)
        elif path.is_dir():
            files.update(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file()
                and candidate.suffix.lower() in PUBLIC_TEXT_SUFFIXES
                and not any(
                    part in EXCLUDED_PARTS
                    for part in candidate.relative_to(root).parts
                )
            )
    return sorted(files)


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


def validate_otel_pipeline_processors(
    path: Path, _root: Path | None = None
) -> list[str]:
    """Keep basic collector reliability processors wired into every pipeline."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            document = yaml.load(handle, Loader=UniqueKeySafeLoader)
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return []  # Generic YAML validation reports parse failures.

    if not isinstance(document, dict):
        return ["collector configuration must be a YAML mapping"]

    processor_definitions = document.get("processors")
    errors: list[str] = []
    if not isinstance(processor_definitions, dict):
        errors.append("processors: mapping is missing")
    else:
        missing_definitions = sorted(
            REQUIRED_OTEL_PROCESSORS - set(processor_definitions)
        )
        if missing_definitions:
            errors.append(
                "processors: missing required processor definition(s): "
                + ", ".join(missing_definitions)
            )

    service = document.get("service")
    pipelines = service.get("pipelines") if isinstance(service, dict) else None
    if not isinstance(pipelines, dict) or not pipelines:
        errors.append("service.pipelines: mapping is missing or empty")
        return errors

    for pipeline_name, pipeline in sorted(pipelines.items()):
        processors = pipeline.get("processors") if isinstance(pipeline, dict) else None
        if not isinstance(processors, list):
            errors.append(
                f"service.pipelines.{pipeline_name}: processors must be a list"
            )
            continue
        missing = sorted(REQUIRED_OTEL_PROCESSORS - set(processors))
        if missing:
            errors.append(
                f"service.pipelines.{pipeline_name}: missing required processor(s): "
                + ", ".join(missing)
            )
    return errors


def _fluent_bit_blocks(text: str) -> list[tuple[str, dict[str, str]]]:
    """Parse the small key/value subset needed for offline Fluent Bit checks."""
    blocks: list[tuple[str, dict[str, str]]] = []
    section: str | None = None
    values: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("[") and line.endswith("]"):
            if section is not None:
                blocks.append((section, values))
            section = line[1:-1].strip().lower()
            values = {}
            continue
        if section is None:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            values[parts[0].lower()] = parts[1].strip()

    if section is not None:
        blocks.append((section, values))
    return blocks


def validate_fluent_bit_opensearch_security(
    path: Path, _root: Path | None = None
) -> list[str]:
    """Require encrypted, authenticated HTTPS settings on OpenSearch outputs."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"cannot read Fluent Bit configuration: {exc}"]

    opensearch_outputs = [
        values
        for section, values in _fluent_bit_blocks(text)
        if section == "output" and values.get("name", "").lower() == "opensearch"
    ]
    if not opensearch_outputs:
        return ["no OpenSearch OUTPUT block found"]

    errors: list[str] = []
    for index, output in enumerate(opensearch_outputs, start=1):
        if output.get("tls", "").lower() != "on":
            errors.append(f"OpenSearch OUTPUT #{index}: TLS must be On")
        if output.get("aws_auth", "").lower() != "on":
            errors.append(f"OpenSearch OUTPUT #{index}: AWS_Auth must be On")
        if output.get("port", "") != "443":
            errors.append(f"OpenSearch OUTPUT #{index}: Port must be 443")
    return errors


def validate_credential_shapes(path: Path, _root: Path | None = None) -> list[str]:
    """Reject high-confidence credential shapes without printing the matched value."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"cannot scan text for credential shapes: {exc}"]

    errors: list[str] = []
    for label, pattern in CREDENTIAL_PATTERNS:
        if pattern.search(text):
            errors.append(f"contains a value matching the {label} pattern")
    return errors


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

    otel_config = root / OTEL_CONFIG_PATH
    otel_config_count = 0
    if otel_config.is_file():
        otel_config_count = 1
        errors.extend(
            f"{OTEL_CONFIG_PATH}: {error}"
            for error in validate_otel_pipeline_processors(otel_config, root)
        )

    fluent_bit_config = root / FLUENT_BIT_CONFIG_PATH
    fluent_bit_config_count = 0
    if fluent_bit_config.is_file():
        fluent_bit_config_count = 1
        errors.extend(
            f"{FLUENT_BIT_CONFIG_PATH}: {error}"
            for error in validate_fluent_bit_opensearch_security(fluent_bit_config, root)
        )

    credential_scan_count = 0
    for path in public_example_files(root):
        credential_scan_count += 1
        relative_path = path.relative_to(root)
        errors.extend(
            f"{relative_path}: {error}"
            for error in validate_credential_shapes(path, root)
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
        f"{counts['.md']} Markdown, {otel_config_count} OpenTelemetry collector config, "
        f"{fluent_bit_config_count} Fluent Bit OpenSearch config, and "
        f"{credential_scan_count} public example files scanned for credential shapes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
