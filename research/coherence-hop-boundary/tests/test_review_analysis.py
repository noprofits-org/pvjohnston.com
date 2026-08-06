#!/usr/bin/env python3
"""Integration checks for the reviewed dual-lane canonical analysis."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = EXPERIMENT_DIR / "src" / "review_analysis.py"
SPEC = importlib.util.spec_from_file_location("review_analysis", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class ReviewAnalysisIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        results = EXPERIMENT_DIR / "results"
        cls.analysis = module.build(
            module.core._load(results / "lineage.json"),
            module.core._load(results / "convergence.json"),
            module.core._load(results / "legacy-convergence.json"),
            module.core._load(results / "exact.json"),
            module.core._load(results / "sweep.json.gz"),
            {
                "lineage": module.core._sha256(results / "lineage.json"),
                "corrective_convergence": module.core._sha256(results / "convergence.json"),
                "legacy_convergence": module.core._sha256(results / "legacy-convergence.json"),
                "legacy_exact": module.core._sha256(results / "exact.json"),
                "legacy_sweep": module.core._sha256(results / "sweep.json.gz"),
            },
        )

    def test_optical_verdict_stays_withdrawn_and_inconclusive(self) -> None:
        verdict = self.analysis["hypothesis"]
        self.assertTrue(verdict["inconclusive"])
        self.assertFalse(verdict["optical_coherence_claim_supported"])
        self.assertFalse(verdict["corrective_production_run"])
        self.assertFalse(self.analysis["convergence_gate"]["passed"])

    def test_corrected_recrossing_counts_match_event_sequences(self) -> None:
        by_scale = {regime["pfm_rate_scale"]: regime for regime in self.analysis["regimes"]}
        self.assertEqual(by_scale[0.075]["event_diagnostics"]["recrossing_events"], 4559)
        self.assertEqual(by_scale[0.075]["event_diagnostics"]["repeat_hop_events"], 5411)
        self.assertEqual(by_scale[0.05]["event_diagnostics"]["recrossing_events"], 4448)
        self.assertEqual(by_scale[0.05]["event_diagnostics"]["repeat_hop_events"], 5353)


if __name__ == "__main__":
    unittest.main()
