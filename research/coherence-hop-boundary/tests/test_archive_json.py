#!/usr/bin/env python3
"""Tests for deterministic publication archiving of the canonical sweep."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "archive_json.py"
SPEC = importlib.util.spec_from_file_location("coherence_hop_archive", MODULE_PATH)
assert SPEC and SPEC.loader
archive_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archive_module)


class ArchiveJsonTest(unittest.TestCase):
    def test_round_trip_is_byte_preserving_and_deterministic(self) -> None:
        original = b'{\n  "experiment": "fixture",\n  "value": -0.0\n}\n'
        first = archive_module._compress(original)
        second = archive_module._compress(original)
        self.assertEqual(first, second)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            output = root / "source.json.gz"
            source.write_bytes(original)
            archive_module._write(source, output)
            archive_module._check(output)
            self.assertEqual(output.read_bytes(), first)

    def test_non_object_json_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            archive_module._validate_json(b"[1, 2, 3]", Path("fixture.json"))


if __name__ == "__main__":
    unittest.main()
