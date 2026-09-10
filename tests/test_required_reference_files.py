from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_REFERENCE_FILES = (
    Path("configs/otel-collector-config.yaml"),
    Path("configs/fluent-bit-opensearch.conf"),
)


class RequiredReferenceFilesTests(unittest.TestCase):
    """Keep the canonical telemetry examples present so policy checks cannot disappear."""

    def test_required_reference_files_exist(self) -> None:
        missing = [
            str(relative_path)
            for relative_path in REQUIRED_REFERENCE_FILES
            if not (ROOT / relative_path).is_file()
        ]

        self.assertEqual(
            [],
            missing,
            "Missing required reference file(s): " + ", ".join(missing),
        )


if __name__ == "__main__":
    unittest.main()
