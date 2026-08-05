"""Fast contract tests for the frozen simulator."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src" / "simulate.py"
SPEC = importlib.util.spec_from_file_location("coherence_hop_simulate", SOURCE)
assert SPEC is not None and SPEC.loader is not None
simulate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = simulate
SPEC.loader.exec_module(simulate)


class SimulatorContractTests(unittest.TestCase):
    def test_scale_one_matches_direct_legacy_lineage(self) -> None:
        result = simulate.run_lineage_comparison(output=None)
        self.assertTrue(result["comparison"]["accepted_events_identical"])
        self.assertTrue(result["comparison"]["passed"])
        self.assertTrue(
            result["accepted_hop_record_comparison"]["instrumentation_complete"]
        )
        self.assertGreater(
            len(result["accepted_hop_record_comparison"]["reference_records"]), 0
        )
        self.assertLessEqual(
            result["comparison"]["max_abs_observable_difference"], 1e-12
        )

    def test_nonunit_scale_reaches_all_three_pfm_applications(self) -> None:
        observed_scales = []
        original = simulate.pfm_rate

        def observing_rate(p_aux, f_aux, *, pfm_rate_scale):
            observed_scales.append(pfm_rate_scale)
            return original(
                p_aux, f_aux, pfm_rate_scale=pfm_rate_scale
            )

        simulate.pfm_rate = observing_rate
        try:
            simulate.run_trajectory_regime(
                pfm_rate_scale=0.075,
                seed=42,
                geometry_count=6,
                dt_fs=0.05,
                electronic_substeps=2,
                total_fs=0.10,
            )
        finally:
            simulate.pfm_rate = original
        self.assertEqual(len(observed_scales), 12)
        self.assertTrue(all(scale == 0.075 for scale in observed_scales))

    def test_censoring_promotes_instead_of_crashing(self) -> None:
        self.assertIsNone(simulate._finite_abs_difference(None, None))
        self.assertIsNone(simulate._finite_abs_difference(None, 1.0))

    def test_exact_grid_failure_promotes_fine_reference(self) -> None:
        common = {
            "time_fs": [0.0, 1.0],
            "upper_population": [0.2, 0.3],
            "centroid_x": [0.0, 0.0],
            "coherence_amplitude": [0.8, 0.4],
            "norm": [1.0, 1.0],
        }
        coarse = {**common, "product_qx_lt_0": [0.1, 0.2]}
        fine = {**common, "product_qx_lt_0": [0.1, 0.21]}
        result = simulate.compare_exact_grids(coarse, fine)
        self.assertFalse(result["gate"]["passed"])
        self.assertTrue(result["valid_reference"])
        self.assertEqual(result["production_grid_n"], 512)

    def test_missing_lineage_blocks_later_stages(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "lineage.json"
            with self.assertRaises(FileNotFoundError):
                simulate.require_passing_lineage(missing)

    def test_resume_key_distinguishes_every_control(self) -> None:
        baseline = {
            "pfm_rate_scale": 0.05,
            "seed": 2701,
            "geometry_count": 4000,
            "dt_fs": 0.025,
            "electronic_substeps": 10,
            "total_fs": 20.0,
            "model_fingerprint": simulate.MODEL_FINGERPRINT,
            "simulator_sha256": simulate.runtime_fingerprints()["simulator_sha256"],
            "config_sha256": simulate.runtime_fingerprints()["config_sha256"],
            "environment_fingerprint": simulate.runtime_fingerprints()[
                "environment_fingerprint"
            ],
        }
        variants = [baseline]
        for name, replacement in (
            ("pfm_rate_scale", 0.075),
            ("seed", 2702),
            ("geometry_count", 3999),
            ("dt_fs", 0.0125),
            ("electronic_substeps", 20),
            ("total_fs", 19.0),
            ("model_fingerprint", "different-model-fingerprint"),
            ("simulator_sha256", "different-simulator-fingerprint"),
            ("config_sha256", "different-config-fingerprint"),
            ("environment_fingerprint", "different-environment-fingerprint"),
        ):
            variant = dict(baseline)
            variant[name] = replacement
            variants.append(variant)
        keys = [simulate.make_resume_key(**variant) for variant in variants]
        self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()
