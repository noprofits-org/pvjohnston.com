from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT_DIR / "src"))

import reconstruct  # noqa: E402
from bundle import RunSpec, generate_lifetimes  # noqa: E402
from contract import (  # noqa: E402
    ContractError,
    canonical_json_bytes,
    load_and_validate_constants,
    load_and_validate_inputs,
    load_and_validate_sources,
    verify_environment,
)


class ReconstructionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.toy = json.loads((EXPERIMENT_DIR / "tests/fixtures/toy-inputs.json").read_text(encoding="utf-8"))

    def toy_spec(self) -> RunSpec:
        return RunSpec(
            experiment="muon-survival-two-frames",
            purpose="setup-toy",
            run_id="toy-run",
            command="setup-only toy smoke; not a production command",
            seed=0,
            draw_count=16,
            scale_s=1e-6,
            lineage={},
            authorization={"kind": "setup-toy"},
            platform={"environment": "setup-toy"},
            path_prefix="setup-toy/toy-run",
        )

    def test_frozen_manifests_and_environment_validate_without_calculation(self) -> None:
        load_and_validate_constants()
        load_and_validate_sources()
        load_and_validate_inputs()
        versions = verify_environment()
        self.assertEqual(versions["python_version"], "3.12.3")
        self.assertEqual(versions["pip_version"], "26.2.1")
        self.assertEqual(versions["numpy_version"], "2.5.1")
        self.assertEqual(versions["matplotlib_version"], "3.11.1")
        self.assertFalse((EXPERIMENT_DIR / "runs").exists())

    def test_json_serialization_and_toy_rng_boundary(self) -> None:
        self.assertEqual(canonical_json_bytes({"b": 2, "a": 1}), b'{\n  "a": 1,\n  "b": 2\n}\n')
        with self.assertRaises(ValueError):
            canonical_json_bytes({"bad": float("nan")})
        first = generate_lifetimes(self.toy_spec())
        second = generate_lifetimes(self.toy_spec())
        np.testing.assert_array_equal(first, second)
        with self.assertRaises(ContractError):
            generate_lifetimes(RunSpec(**{**self.toy_spec().__dict__, "seed": 1}))
        with self.assertRaises(ContractError):
            generate_lifetimes(RunSpec(**{**self.toy_spec().__dict__, "draw_count": 17}))

    def test_independent_routes_zero_path_and_inclusive_counts(self) -> None:
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
        self.assertEqual(detector["decay_exponent"][0], 0.0)
        self.assertEqual(muon["decay_exponent"][0], 0.0)
        counts, probabilities = reconstruct.empirical_survival(
            np.asarray([0.0, 1.0, 2.0], dtype=np.float64),
            np.asarray([0.0, 1.0, 2.0], dtype=np.float64),
        )
        np.testing.assert_array_equal(counts, [3, 2, 1])
        np.testing.assert_allclose(probabilities, [1.0, 2.0 / 3.0, 1.0 / 3.0])

    def packet(self, *, focal_probability: float = 0.5):
        primitives = {
            "momentum_mev_c": 1.0,
            "mass_energy_mev": 1.0,
            "tau0_s": 1.0,
            "c_m_s": 1.0,
            "units": dict(reconstruct.PRIMITIVE_UNITS),
        }
        paths = np.asarray([0.0, -np.log(focal_probability), -np.log(0.25)], dtype=np.float64)
        kwargs = {key: primitives[key] for key in ("momentum_mev_c", "mass_energy_mev", "tau0_s", "c_m_s")}
        detector = reconstruct.detector_frame(paths, **kwargs)
        muon = reconstruct.muon_frame(paths, **kwargs)
        counterfactual = reconstruct.same_speed_no_lifetime_dilation_counterfactual(
            paths, detector_beta=detector["beta"], tau0_s=1.0, c_m_s=1.0
        )
        counts = np.asarray([16, int(round(focal_probability * 16)), 4], dtype=np.int64)
        empirical = counts.astype(np.float64) / 16
        lifetimes = np.linspace(0.0, 1.0, 16, dtype=np.float64)
        return detector, muon, counterfactual, paths, primitives, counts, empirical, lifetimes

    def checks(self, packet, *, integrity_overrides=None):
        integrity = {"schema": True, "manifest": True, "provenance": True, "hashes": True, "run_bundle": True, "run_admission": True}
        if integrity_overrides:
            integrity.update(integrity_overrides)
        return reconstruct.evaluate_checks(
            *packet,
            focal_index=1,
            expected_grid_size=3,
            expected_draw_count=16,
            frame_relative_tolerance=1e-12,
            standard_error_multiplier=4.0,
            maximum_grid_discrepancy=0.01,
            integrity_flags=integrity,
        )

    def test_all_registered_checks_pass_for_consistent_synthetic_packet(self) -> None:
        checks = self.checks(self.packet())
        self.assertTrue(checks["all_passed"])
        self.assertTrue(all(checks["details"].values()))

    def test_each_frame_agreement_subbranch_fails_independently(self) -> None:
        mutations = [
            ("probability", lambda packet: packet[1]["survival_probability"].__setitem__(1, 0.6)),
            ("exponent", lambda packet: packet[1]["decay_exponent"].__setitem__(1, packet[1]["decay_exponent"][1] * 1.01)),
            ("beta", lambda packet: packet[1].__setitem__("beta", packet[1]["beta"] * 0.99)),
            ("gamma", lambda packet: packet[1].__setitem__("gamma", packet[1]["gamma"] * 1.01)),
            ("zero", lambda packet: packet[1]["decay_exponent"].__setitem__(0, 1e-15)),
        ]
        for name, mutate in mutations:
            with self.subTest(name=name):
                packet = list(copy.deepcopy(self.packet()))
                mutate(packet)
                self.assertFalse(self.checks(tuple(packet))["frame_agreement"])

    def test_focal_and_grid_discrepancy_fail_separately(self) -> None:
        packet = list(self.packet(focal_probability=0.75))
        packet[5] = np.asarray([16, 0, 4], dtype=np.int64)
        packet[6] = packet[5].astype(np.float64) / 16
        self.assertFalse(self.checks(tuple(packet))["focal_monte_carlo_within_four_standard_errors"])
        packet = list(self.packet())
        packet[5] = np.asarray([16, 7, 4], dtype=np.int64)
        packet[6] = packet[5].astype(np.float64) / 16
        self.assertFalse(self.checks(tuple(packet))["maximum_grid_discrepancy_at_most_threshold"])

    def test_each_count_and_dtype_branch_fails(self) -> None:
        mutations = [
            ("upper_bound", lambda packet: packet.__setitem__(5, np.asarray([16, 17, 4], dtype=np.int64))),
            ("zero_count", lambda packet: packet.__setitem__(5, np.asarray([15, 8, 4], dtype=np.int64))),
            ("monotonic", lambda packet: packet.__setitem__(5, np.asarray([16, 4, 8], dtype=np.int64))),
            ("count_dtype", lambda packet: packet.__setitem__(5, packet[5].astype(np.int32))),
            ("empirical_equality", lambda packet: packet[6].__setitem__(1, 0.4)),
        ]
        for name, mutate in mutations:
            with self.subTest(name=name):
                packet = list(copy.deepcopy(self.packet()))
                mutate(packet)
                if name != "empirical_equality":
                    packet[6] = packet[5].astype(np.float64) / 16
                self.assertFalse(self.checks(tuple(packet))["counts_valid_and_monotonic"])

    def test_numeric_derived_units_counterfactual_and_integrity_branches(self) -> None:
        mutations = [
            ("raw_dtype", lambda packet: packet.__setitem__(7, packet[7].astype(np.float32)), "dtypes_valid"),
            ("raw_finite", lambda packet: packet[7].__setitem__(1, np.nan), "raw_lifetimes_finite_nonnegative"),
            ("primitive", lambda packet: packet[4].__setitem__("momentum_mev_c", 1.1), "derived_fields_valid"),
            ("grid", lambda packet: packet[3].__setitem__(1, packet[3][1] + 0.1), "derived_fields_valid"),
            ("distance", lambda packet: packet[0]["laboratory_distance_m"].__setitem__(1, 99.0), "derived_fields_valid"),
            ("elapsed", lambda packet: packet[1]["elapsed_time_s"].__setitem__(1, 99.0), "derived_fields_valid"),
            ("mean_lifetime", lambda packet: packet[0].__setitem__("mean_lifetime_s", 99.0), "derived_fields_valid"),
            ("units", lambda packet: packet[0]["units"].__setitem__("elapsed_time_s", "ms"), "units_valid"),
            ("counter_label", lambda packet: packet[2].__setitem__("label", "third frame"), "counterfactual_valid"),
            ("counter_value", lambda packet: packet[2]["decay_exponent"].__setitem__(1, 99.0), "counterfactual_valid"),
        ]
        for name, mutate, detail in mutations:
            with self.subTest(name=name):
                packet = list(copy.deepcopy(self.packet()))
                mutate(packet)
                checks = self.checks(tuple(packet))
                self.assertFalse(checks["numeric_shapes_dtypes_units_valid"])
                self.assertFalse(checks["details"][detail])
        for key in ("schema", "manifest", "provenance", "hashes", "run_bundle", "run_admission"):
            with self.subTest(integrity=key):
                self.assertFalse(self.checks(self.packet(), integrity_overrides={key: False})["schema_manifest_provenance_and_hashes_valid"])

    def test_invalid_public_boundaries_raise(self) -> None:
        with self.assertRaises(ContractError):
            reconstruct.detector_frame(np.asarray([0.0, -1.0]), momentum_mev_c=1.0, mass_energy_mev=1.0, tau0_s=1.0, c_m_s=1.0)
        with self.assertRaises(ContractError):
            reconstruct.empirical_survival(np.asarray([0.0, -1.0]), np.asarray([0.0]))

    def test_schema_documents_parse_and_declare_draft(self) -> None:
        for path in sorted((EXPERIMENT_DIR / "schemas").glob("*.json")):
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(document["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(document["type"], "object")


if __name__ == "__main__":
    unittest.main()
