from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = EXPERIMENT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

import reconstruct  # noqa: E402
from bundle import (  # noqa: E402
    RunSpec,
    create_new_run_directory,
    generate_lifetimes,
    seal_run_bundle,
    validate_run_bundle,
)
from contract import (  # noqa: E402
    ContractError,
    canonical_json_bytes,
    load_and_validate_constants,
    load_and_validate_inputs,
    load_and_validate_sources,
    sha256_file,
    verify_environment,
)


class SetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.toy = json.loads((EXPERIMENT_DIR / "tests/fixtures/toy-inputs.json").read_text(encoding="utf-8"))

    def toy_spec(self, path_prefix: str = "setup-toy/toy-run") -> RunSpec:
        return RunSpec(
            experiment="muon-survival-two-frames",
            purpose="setup-toy",
            run_id="toy-run",
            command="setup-only toy smoke; not a production command",
            seed=self.toy["seed"],
            draw_count=self.toy["draw_count"],
            scale_s=self.toy["proper_mean_lifetime_s"],
            lineage={},
            platform={"environment": "setup-toy"},
            path_prefix=path_prefix,
        )

    def test_frozen_manifests_and_environment_validate_without_calculation(self) -> None:
        load_and_validate_constants()
        load_and_validate_sources()
        load_and_validate_inputs()
        versions = verify_environment()
        self.assertEqual(versions["pip_version"], "26.2.1")
        self.assertEqual(versions["numpy_version"], "2.5.1")
        self.assertEqual(versions["matplotlib_version"], "3.11.1")
        self.assertFalse((EXPERIMENT_DIR / "runs/run-001").exists())

    def test_json_serialization_is_deterministic_and_rejects_nan(self) -> None:
        self.assertEqual(canonical_json_bytes({"b": 2, "a": 1}), b'{\n  "a": 1,\n  "b": 2\n}\n')
        with self.assertRaises(ValueError):
            canonical_json_bytes({"bad": float("nan")})

    def test_toy_rng_is_reproducible_and_enforces_setup_boundary(self) -> None:
        first = generate_lifetimes(self.toy_spec())
        second = generate_lifetimes(self.toy_spec())
        np.testing.assert_array_equal(first, second)
        self.assertEqual(first.shape, (16,))
        with self.assertRaises(ContractError):
            generate_lifetimes(self.toy_spec().__class__(**{**self.toy_spec().__dict__, "seed": 1}))
        with self.assertRaises(ContractError):
            generate_lifetimes(self.toy_spec().__class__(**{**self.toy_spec().__dict__, "draw_count": 17}))

    def test_new_namespace_bundle_completion_and_hash_contract(self) -> None:
        with tempfile.TemporaryDirectory(prefix="muon-setup-nonproduction-") as temporary:
            parent = Path(temporary) / "setup-toy-runs"
            run_dir = create_new_run_directory(parent, "toy-run")
            spec = self.toy_spec()
            sample = generate_lifetimes(spec)
            seal_run_bundle(
                run_dir,
                sample,
                spec,
                started_at="2000-01-01T00:00:00Z",
                completed_at="2000-01-01T00:00:01Z",
            )
            report = validate_run_bundle(run_dir, spec)
            self.assertTrue(report["valid"])
            self.assertEqual(report["sample_shape"], [16])
            with self.assertRaises(ContractError):
                create_new_run_directory(parent, "toy-run")
            (run_dir / "stdout.log").write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "checksum mismatch"):
                validate_run_bundle(run_dir, spec)

    def test_independent_frame_routes_agree_on_toy_primitives(self) -> None:
        kwargs = {
            "momentum_mev_c": self.toy["momentum_mev_c"],
            "mass_energy_mev": self.toy["mass_energy_mev"],
            "tau0_s": self.toy["proper_mean_lifetime_s"],
            "c_m_s": self.toy["speed_of_light_m_s"],
        }
        paths = np.asarray(self.toy["paths_m"], dtype=np.float64)
        detector = reconstruct.detector_frame(paths, **kwargs)
        with mock.patch.object(reconstruct, "detector_frame", side_effect=AssertionError("must not be called")):
            muon = reconstruct.muon_frame(paths, **kwargs)
        np.testing.assert_allclose(detector["survival_probability"], muon["survival_probability"], rtol=1e-14, atol=0.0)
        np.testing.assert_allclose(detector["decay_exponent"], muon["decay_exponent"], rtol=1e-14, atol=0.0)
        self.assertEqual(detector["decay_exponent"][0], 0.0)
        self.assertEqual(muon["decay_exponent"][0], 0.0)

    def test_inclusive_empirical_comparison_and_invalid_boundaries(self) -> None:
        lifetimes = np.asarray([0.0, 1.0, 2.0], dtype=np.float64)
        counts, probabilities = reconstruct.empirical_survival(lifetimes, np.asarray([0.0, 1.0, 2.0]))
        np.testing.assert_array_equal(counts, [3, 2, 1])
        np.testing.assert_allclose(probabilities, [1.0, 2.0 / 3.0, 1.0 / 3.0])
        with self.assertRaises(ContractError):
            reconstruct.detector_frame(np.asarray([0.0, -1.0]), momentum_mev_c=1.0, mass_energy_mev=1.0, tau0_s=1.0, c_m_s=1.0)
        with self.assertRaises(ContractError):
            reconstruct.empirical_survival(np.asarray([0.0, -1.0]), np.asarray([0.0]))

    def _synthetic_check_packet(self):
        exponent = np.asarray([0.0, np.log(2.0), np.log(4.0)], dtype=np.float64)
        probability = np.asarray([1.0, 0.5, 0.25], dtype=np.float64)
        detector = {"beta": 0.5, "gamma": 2.0, "decay_exponent": exponent, "survival_probability": probability}
        muon = copy.deepcopy(detector)
        counts = np.asarray([16, 8, 4], dtype=np.int64)
        empirical = counts.astype(np.float64) / 16
        lifetimes = np.linspace(0.0, 1.0, 16, dtype=np.float64)
        return detector, muon, counts, empirical, lifetimes

    def _checks(self, *packet, integrity=True):
        return reconstruct.evaluate_checks(
            *packet,
            focal_index=1,
            expected_grid_size=3,
            expected_draw_count=16,
            frame_relative_tolerance=1e-12,
            standard_error_multiplier=4.0,
            maximum_grid_discrepancy=0.01,
            integrity_flags={"schema": integrity, "manifest": True, "provenance": True, "hashes": True},
        )

    def test_all_acceptance_branches_pass_on_consistent_synthetic_data(self) -> None:
        checks = self._checks(*self._synthetic_check_packet())
        self.assertTrue(checks["all_passed"])

    def test_failure_branches_are_observable_without_a_verdict(self) -> None:
        packet = list(self._synthetic_check_packet())
        packet[1]["survival_probability"] = np.asarray([1.0, 0.6, 0.25])
        self.assertFalse(self._checks(*packet)["frame_agreement"])

        packet = list(self._synthetic_check_packet())
        packet[2] = np.asarray([16, 4, 8], dtype=np.int64)
        packet[3] = packet[2].astype(np.float64) / 16
        checks = self._checks(*packet)
        self.assertFalse(checks["counts_valid_and_monotonic"])
        self.assertFalse(checks["maximum_grid_discrepancy_at_most_threshold"])

        self.assertFalse(self._checks(*self._synthetic_check_packet(), integrity=False)["schema_manifest_provenance_and_hashes_valid"])

    def test_schema_documents_parse_and_declare_draft(self) -> None:
        for path in sorted((EXPERIMENT_DIR / "schemas").glob("*.json")):
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(document["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(document["type"], "object")


if __name__ == "__main__":
    unittest.main()
