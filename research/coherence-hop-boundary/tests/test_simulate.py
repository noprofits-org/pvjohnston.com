"""Fast contract tests for the frozen simulator."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


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

    def test_phase_cancellation_precedes_magnitude(self) -> None:
        inverse_sqrt_two = 1.0 / np.sqrt(2.0)
        coefficients = np.asarray([
            [inverse_sqrt_two, inverse_sqrt_two],
            [inverse_sqrt_two, -inverse_sqrt_two],
        ], dtype=np.complex128)
        observed = simulate.coherence_observables(coefficients)
        self.assertAlmostEqual(observed["ensemble_coherence_real"], 0.0)
        self.assertAlmostEqual(observed["ensemble_coherence_imag"], 0.0)
        self.assertAlmostEqual(observed["coherence_amplitude"], 0.0)
        self.assertAlmostEqual(
            observed["mean_trajectory_coherence_magnitude"], 1.0
        )

    def test_recrossing_is_a_return_not_every_repeat(self) -> None:
        recorder = simulate.HopRecorder(
            1, keep_events=True, initial_state=np.asarray([0])
        )
        for index, from_state in enumerate((0, 1, 0), start=1):
            recorder.record(
                simulate.HopAttempt(
                    proposed=np.asarray([True]),
                    frustrated=np.asarray([False]),
                    accepted=np.asarray([True]),
                    from_state=np.asarray([from_state]),
                ),
                time_fs=float(index),
                nuclear_step=index,
                electronic_substep=1,
            )
        records = recorder.as_dict()["records"]
        self.assertEqual(
            [record["accepted_hop_class"] for record in records],
            ["first", "repeat", "repeat"],
        )
        self.assertEqual(
            [record["recrossing"] for record in records],
            [False, True, False],
        )

    def test_component_pooling_preserves_cross_seed_phase_cancellation(self) -> None:
        runs = [
            {"full": {
                "ensemble_coherence_real": [sign],
                "ensemble_coherence_imag": [0.0],
                "coherence_amplitude": [1.0],
                "mean_trajectory_coherence_magnitude": [1.0],
            }}
            for sign in (1.0, -1.0)
        ]
        pooled = simulate.aggregate_observations(runs, "full")
        self.assertEqual(pooled["coherence_amplitude"], [0.0])
        self.assertEqual(pooled["mean_trajectory_coherence_magnitude"], [1.0])

    def test_small_canonical_run_excludes_clock_and_reproduces_bytes(self) -> None:
        controls = {
            "pfm_rate_scale": 0.075,
            "seed": 43,
            "geometry_count": 6,
            "dt_fs": 0.05,
            "electronic_substeps": 2,
            "total_fs": 0.10,
        }
        first = simulate.run_trajectory_regime(**controls)
        second = simulate.run_trajectory_regime(**controls)
        self.assertNotIn("runtime_seconds", first)
        self.assertEqual(
            simulate.canonical_json(simulate._json_safe(first)),
            simulate.canonical_json(simulate._json_safe(second)),
        )

    def test_exact_grid_failure_promotes_fine_reference(self) -> None:
        common = {
            "time_fs": [0.0, 1.0],
            "upper_population": [0.2, 0.3],
            "centroid_x": [0.0, 0.0],
            "ensemble_coherence_real": [0.8, 0.4],
            "ensemble_coherence_imag": [0.0, 0.0],
            "coherence_amplitude": [0.8, 0.4],
            "mean_trajectory_coherence_magnitude": [0.8, 0.4],
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

    def test_kernel_release_does_not_change_environment_or_resume_identity(self) -> None:
        controls = {
            "pfm_rate_scale": 0.05,
            "seed": 2701,
            "geometry_count": 6,
            "dt_fs": 0.05,
            "electronic_substeps": 2,
            "total_fs": 0.10,
        }
        with mock.patch.dict(
            simulate.os.environ, {"OPENBLAS_NUM_THREADS": "1"}
        ):
            with mock.patch.object(
                simulate.platform, "platform", return_value="Linux-kernel-A"
            ):
                first_record = simulate.environment_record()
                first_fingerprint = simulate.runtime_fingerprints()[
                    "environment_fingerprint"
                ]
                first_key = simulate.make_resume_key(**controls)
            with mock.patch.object(
                simulate.platform, "platform", return_value="Linux-kernel-B"
            ):
                second_record = simulate.environment_record()
                second_fingerprint = simulate.runtime_fingerprints()[
                    "environment_fingerprint"
                ]
                second_key = simulate.make_resume_key(**controls)
        self.assertEqual(first_record["schema_version"], 2)
        self.assertNotIn("platform", first_record)
        self.assertEqual(first_record, second_record)
        self.assertEqual(first_fingerprint, second_fingerprint)
        self.assertEqual(first_key, second_key)

    def test_each_declared_environment_control_changes_v2_fingerprint(self) -> None:
        with mock.patch.dict(
            simulate.os.environ, {"OPENBLAS_NUM_THREADS": "1"}
        ):
            baseline = simulate.runtime_fingerprints()["environment_fingerprint"]
            replacements = (
                (simulate.platform, "python_implementation", "PyPy"),
                (simulate.platform, "python_version", "3.12.8"),
                (simulate.platform, "system", "Darwin"),
                (simulate.platform, "machine", "aarch64"),
            )
            for owner, name, replacement in replacements:
                with self.subTest(control=name):
                    with mock.patch.object(owner, name, return_value=replacement):
                        observed = simulate.runtime_fingerprints()[
                            "environment_fingerprint"
                        ]
                    self.assertNotEqual(observed, baseline)
            with self.subTest(control="numpy"):
                with mock.patch.object(simulate.np, "__version__", "2.2.4"):
                    observed = simulate.runtime_fingerprints()[
                        "environment_fingerprint"
                    ]
                self.assertNotEqual(observed, baseline)
            with self.subTest(control="openblas_num_threads"):
                with mock.patch.dict(
                    simulate.os.environ, {"OPENBLAS_NUM_THREADS": "2"}
                ):
                    observed = simulate.runtime_fingerprints()[
                        "environment_fingerprint"
                    ]
                self.assertNotEqual(observed, baseline)


if __name__ == "__main__":
    unittest.main()
