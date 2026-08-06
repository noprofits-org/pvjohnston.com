#!/usr/bin/env python3
"""Integration checks for the reviewed dual-lane canonical analysis."""

from __future__ import annotations

import copy
import importlib.util
import json
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
        cls.legacy_convergence = module.core._load(
            results / "legacy-convergence.json"
        )
        cls.exact = module.core._load(results / "exact.json")
        cls.analysis = module.build(
            module.core._load(results / "lineage.json"),
            module.core._load(results / "convergence.json"),
            cls.legacy_convergence,
            cls.exact,
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

    def test_reviewed_analysis_stays_byte_for_byte_current(self) -> None:
        serialized = json.dumps(
            self.analysis, indent=2, sort_keys=True, allow_nan=False
        ) + "\n"
        stored = (
            EXPERIMENT_DIR / "results" / "analysis.json"
        ).read_text(encoding="utf-8")
        self.assertEqual(serialized, stored)

    def test_legacy_convergence_is_recomputed_from_retained_inputs(self) -> None:
        recomputed = module._verified_legacy_convergence(
            self.legacy_convergence
        )
        self.assertEqual(recomputed, self.legacy_convergence["comparison"])
        self.assertFalse(recomputed["gate"]["passed"])

    def test_legacy_convergence_rejects_tampered_stored_summary(self) -> None:
        artifact = copy.deepcopy(self.legacy_convergence)
        artifact["comparison"]["accepted_event_fraction_abs_difference"] = 0.0
        with self.assertRaisesRegex(ValueError, "summary is stale or edited"):
            module._verified_legacy_convergence(artifact)

    def test_legacy_convergence_rejects_divergent_retained_hop_times(self) -> None:
        artifact = copy.deepcopy(self.legacy_convergence)
        artifact["coarse"]["full_hop_time_fs"][0] += 0.001
        with self.assertRaisesRegex(ValueError, "accepted-event inputs disagree"):
            module._verified_legacy_convergence(artifact)

    def test_legacy_convergence_rejects_tampered_retained_series(self) -> None:
        artifact = copy.deepcopy(self.legacy_convergence)
        artifact["coarse"]["full"]["upper_population"][100] += 0.1
        with self.assertRaisesRegex(ValueError, "summary is stale or edited"):
            module._verified_legacy_convergence(artifact)

    def test_legacy_exact_rejects_each_off_protocol_control(self) -> None:
        replacements = {
            "grid_n": 383,
            "half_width": 95.0,
            "dx": 0.25,
            "requested_dt_fs": 0.05,
            "actual_dt_fs": 0.05,
            "sample_every_fs": 0.05,
            "total_fs": 19.0,
            "center_fraction": 0.25,
            "center_x": 3.88125,
            "momentum_kick_toward_ci_sigma_px": 1.0,
            "mean_momentum_x": 1.0,
            "initial_sigma_x": 8.0,
        }
        for field, replacement in replacements.items():
            with self.subTest(field=field):
                artifact = copy.deepcopy(self.exact)
                artifact["coarse"]["configuration"][field] = replacement
                with self.assertRaisesRegex(ValueError, f"off-protocol {field}"):
                    module._legacy_exact(artifact)

    def test_legacy_exact_rejects_foreign_embedded_fingerprint(self) -> None:
        artifact = copy.deepcopy(self.exact)
        artifact["fine"]["configuration"]["environment_fingerprint"] = "edited"
        with self.assertRaisesRegex(ValueError, "foreign environment_fingerprint"):
            module._legacy_exact(artifact)

    def test_historical_environment_fingerprint_is_self_verifying(self) -> None:
        module._validate_environment_fingerprint(
            self.legacy_convergence, "legacy convergence"
        )
        artifact = copy.deepcopy(self.legacy_convergence)
        artifact["environment"]["platform"] = "Linux-different-kernel"
        with self.assertRaisesRegex(ValueError, "fingerprint is stale or edited"):
            module._validate_environment_fingerprint(
                artifact, "legacy convergence"
            )


if __name__ == "__main__":
    unittest.main()
