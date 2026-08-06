#!/usr/bin/env python3
"""Tests for deterministic artifact correction and compaction."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "correct_artifacts.py"
SPEC = importlib.util.spec_from_file_location("correct_artifacts", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class CorrectArtifactsTest(unittest.TestCase):
    def test_recrossing_is_only_a_return_to_the_initial_state(self) -> None:
        records = [
            {"trajectory_id": 7, "from_state": 0, "to_state": 1, "outcome": "accepted"},
            {"trajectory_id": 7, "from_state": 1, "to_state": 1, "outcome": "frustrated"},
            {"trajectory_id": 7, "from_state": 1, "to_state": 0, "outcome": "accepted"},
            {"trajectory_id": 7, "from_state": 0, "to_state": 1, "outcome": "accepted"},
        ]
        counts = module._correct_event_records(records)
        self.assertEqual([record["recrossing"] for record in records], [False, False, True, False])
        self.assertEqual(counts["accepted_repeat"], 2)
        self.assertEqual(counts["accepted_recrossing"], 1)

    def test_volatile_metadata_is_removed_recursively(self) -> None:
        value = {"runtime_seconds": 1.2, "nested": [{"generated_at": "now", "x": 1}]}
        self.assertEqual(module._strip_volatile(value), {"nested": [{"x": 1}]})

    def test_convergence_compaction_retains_gate_inputs(self) -> None:
        run = {
            "events": {"full": [{"outcome": "accepted"}]},
            "full_hop_time_fs": [1.0],
            "full": {"upper_population": [0.5]},
            "comparison": {"coherence_lifetime_fs": 2.0},
            "event_summary": {"full": {
                "counts": {"accepted": 1}, "records": [{}],
                "per_trajectory_accepted_counts": [1],
            }},
        }
        data = {
            "complete": True,
            "comparison": {"gate": {"passed": False}},
            "candidate": [run],
            "reference": [],
            "runs": [],
        }
        output = module.compact_convergence(data, "abc")
        self.assertNotIn("runs", output)
        compact = output["candidate"][0]
        self.assertNotIn("events", compact)
        self.assertNotIn("records", compact["event_summary"]["full"])
        self.assertEqual(compact["full_hop_time_fs"], [1.0])
        self.assertEqual(compact["full"]["upper_population"], [0.5])

    def test_legacy_convergence_is_explicitly_failed(self) -> None:
        run = {
            "events": {"full": [], "axe": []},
            "event_summary": {"full": {"records": []}, "axe": {"records": []}},
        }
        output = module.sanitize_legacy_convergence(
            {"coarse": run, "fine": run, "comparison": {}}, "abc"
        )
        self.assertEqual(
            output["scientific_status"],
            "failed_gate_fine_selected_without_finer_audit",
        )
        self.assertNotIn("events", output["coarse"])

    def test_serialization_is_deterministic(self) -> None:
        first = module._serialize({"b": 2, "a": 1}, True)
        second = module._serialize({"a": 1, "b": 2}, True)
        self.assertEqual(first, second)

    def test_permanent_source_url_is_repository_scoped(self) -> None:
        module._validate_source_url(
            "https://raw.githubusercontent.com/noprofits-org/"
            "pvjohnston.com/77a27f6/results/example.json"
        )
        with self.assertRaises(ValueError):
            module._validate_source_url("https://example.com/results/example.json")


if __name__ == "__main__":
    unittest.main()
