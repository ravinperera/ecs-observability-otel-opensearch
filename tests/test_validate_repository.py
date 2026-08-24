from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_repository.py"
SPEC = importlib.util.spec_from_file_location("validate_repository", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RepositoryValidatorTests(unittest.TestCase):
    def test_repository_files_are_sorted_and_exclude_generated_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "b.json").write_text("{}", encoding="utf-8")
            (root / "a.json").write_text("{}", encoding="utf-8")
            (root / ".venv").mkdir()
            (root / ".venv" / "ignored.json").write_text("{}", encoding="utf-8")

            files = list(MODULE.repository_files(root, {".json"}))

            self.assertEqual([root / "a.json", root / "b.json"], files)

    def test_json_validation_accepts_valid_and_rejects_invalid_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "valid.json"
            invalid = root / "invalid.json"
            valid.write_text('{"enabled": true}\n', encoding="utf-8")
            invalid.write_text('{"enabled": }\n', encoding="utf-8")

            self.assertEqual([], MODULE.validate_json(valid))
            self.assertIn("invalid JSON", MODULE.validate_json(invalid)[0])

    def test_json_validation_rejects_duplicate_object_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task-definition.json"
            path.write_text(
                '{"family": "example", "family": "overridden"}\n',
                encoding="utf-8",
            )

            errors = MODULE.validate_json(path)

        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate JSON object key", errors[0])

    def test_yaml_validation_accepts_valid_and_rejects_invalid_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "valid.yaml"
            invalid = root / "invalid.yaml"
            valid.write_text("enabled: true\n", encoding="utf-8")
            invalid.write_text("items: [one, two\n", encoding="utf-8")

            self.assertEqual([], MODULE.validate_yaml(valid))
            self.assertIn("invalid YAML", MODULE.validate_yaml(invalid)[0])

    def test_yaml_validation_rejects_duplicate_mapping_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "collector.yaml"
            path.write_text(
                "exporters:\n"
                "  otlp:\n"
                "    endpoint: first.example:4317\n"
                "    endpoint: second.example:4317\n",
                encoding="utf-8",
            )

            errors = MODULE.validate_yaml(path)

        self.assertEqual(len(errors), 1)
        self.assertIn("found duplicate key 'endpoint'", errors[0])

    def test_markdown_validation_accepts_balanced_fences(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "guide.md"
            path.write_text("# Guide\n\n```json\n{}\n```\n", encoding="utf-8")

            self.assertEqual([], MODULE.validate_markdown(path))

    def test_markdown_validation_rejects_unclosed_fence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "guide.md"
            path.write_text("# Guide\n\n```json\n{}\n", encoding="utf-8")

            errors = MODULE.validate_markdown(path)
            self.assertIn("unclosed Markdown fence", errors[0])

    def test_markdown_validation_rejects_nul_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "guide.md"
            path.write_text("# Guide\n\x00\n", encoding="utf-8")

            self.assertEqual(["contains a NUL byte"], MODULE.validate_markdown(path))

    def test_markdown_validation_accepts_existing_local_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text("# Root\n", encoding="utf-8")
            guide = docs / "guide.md"
            guide.write_text("[Root](../README.md#root)\n", encoding="utf-8")

            self.assertEqual([], MODULE.validate_markdown(guide, root))

    def test_markdown_validation_rejects_missing_local_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            guide = root / "guide.md"
            guide.write_text("[Missing](docs/missing.md)\n", encoding="utf-8")

            errors = MODULE.validate_markdown(guide, root)
            self.assertIn("missing local link target", errors[0])

    def test_markdown_validation_ignores_external_anchor_and_fenced_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            guide = root / "guide.md"
            guide.write_text(
                "[External](https://example.com)\n"
                "[Anchor](#section)\n"
                "```markdown\n"
                "[Example only](missing.md)\n"
                "```\n",
                encoding="utf-8",
            )

            self.assertEqual([], MODULE.validate_markdown(guide, root))

    def test_markdown_validation_rejects_repository_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            guide = docs / "guide.md"
            guide.write_text("[Outside](../../outside.md)\n", encoding="utf-8")

            errors = MODULE.validate_markdown(guide, root)
            self.assertIn("link target escapes repository", errors[0])


if __name__ == "__main__":
    unittest.main()
