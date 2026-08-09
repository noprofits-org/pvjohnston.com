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
    load_json,
    validate_json_schema,
    verify_environment,
)


class ReconstructionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.toy = json.loads((EXPERIMENT_DIR / "tests/fixtures/toy-inputs.json").read_text(encoding="utf-8"))

    def toy_spec(self) -> RunSpec:
        lineage = {
            name: {"path": f"setup-toy/{name}", "sha256": "0" * 64}
            for name in (
                "protocol", "setup_manifest", "inputs", "constants", "sources",
                "environment", "requirements", "workflow_graph", "workflow_cli",
            )
        }
        return RunSpec(
            experiment="muon-survival-two-frames",
            purpose="setup-toy",
            run_id="toy-run",
            command="setup-only toy smoke; not a production command",
            seed=0,
            draw_count=16,
            scale_s=1e-6,
            lineage=lineage,
            authorization={
                "kind": "setup-toy", "workflow_path": "setup-toy/workflow.jsonl",
                "event_id": "00000000-0000-4000-8000-000000000001",
                "sequence": 1, "submission_sequence": 1, "decision": "setup-toy",
                "graph_version": 1, "graph_sha256": "0" * 64, "event_sha256": "0" * 64,
            },
            platform={
                "os": "setup-toy", "release": "setup-toy", "architecture": "setup-toy",
                "python_implementation": "setup-toy", "python_version": "setup-toy",
                "numpy_version": "setup-toy", "matplotlib_version": "setup-toy",
                "pip_version": "setup-toy", "node_version": "setup-toy",
            },
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

    def checks(
        self,
        packet,
        *,
        integrity_overrides=None,
        standard_error_multiplier=4.0,
        maximum_grid_discrepancy=0.01,
    ):
        integrity = {"schema": True, "manifest": True, "provenance": True, "hashes": True, "run_bundle": True, "run_admission": True}
        if integrity_overrides:
            integrity.update(integrity_overrides)
        return reconstruct.evaluate_checks(
            *packet,
            focal_index=1,
            expected_grid_size=3,
            expected_draw_count=16,
            frame_relative_tolerance=1e-12,
            standard_error_multiplier=standard_error_multiplier,
            maximum_grid_discrepancy=maximum_grid_discrepancy,
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
        packet = list(self.packet(focal_probability=0.9))
        packet[5] = np.asarray([16, 8, 4], dtype=np.int64)
        packet[6] = packet[5].astype(np.float64) / 16
        checks = self.checks(tuple(packet), maximum_grid_discrepancy=0.5)
        self.assertFalse(checks["focal_monte_carlo_within_four_standard_errors"])
        self.assertTrue(checks["maximum_grid_discrepancy_at_most_threshold"])
        self.assertTrue(checks["counts_valid_and_monotonic"])
        packet = list(self.packet())
        packet[5] = np.asarray([16, 7, 4], dtype=np.int64)
        packet[6] = packet[5].astype(np.float64) / 16
        checks = self.checks(tuple(packet))
        self.assertFalse(checks["maximum_grid_discrepancy_at_most_threshold"])
        self.assertTrue(checks["focal_monte_carlo_within_four_standard_errors"])
        self.assertTrue(checks["counts_valid_and_monotonic"])

    def test_each_count_and_dtype_branch_fails(self) -> None:
        mutations = [
            ("upper_bound", lambda packet: packet.__setitem__(5, np.asarray([17, 17, 4], dtype=np.int64)), "count_bounds_valid", {"counts_monotonic": True}),
            ("lower_bound", lambda packet: packet.__setitem__(5, np.asarray([16, 8, -1], dtype=np.int64)), "count_bounds_valid", {"counts_monotonic": True}),
            ("zero_count", lambda packet: packet.__setitem__(5, np.asarray([15, 8, 4], dtype=np.int64)), "zero_distance_count_valid", {"count_bounds_valid": True, "counts_monotonic": True}),
            ("monotonic", lambda packet: packet.__setitem__(5, np.asarray([16, 4, 8], dtype=np.int64)), "counts_monotonic", {"count_bounds_valid": True, "zero_distance_count_valid": True}),
            ("count_dtype", lambda packet: packet.__setitem__(5, packet[5].astype(np.int32)), "count_dtype_valid", {"count_bounds_valid": True, "counts_monotonic": True}),
            ("empirical_equality", lambda packet: packet[6].__setitem__(1, 0.4), "empirical_matches_counts", {"count_bounds_valid": True, "counts_monotonic": True}),
        ]
        for name, mutate, detail, independent in mutations:
            with self.subTest(name=name):
                packet = list(copy.deepcopy(self.packet()))
                mutate(packet)
                if name != "empirical_equality":
                    packet[6] = packet[5].astype(np.float64) / 16
                checks = self.checks(tuple(packet))
                self.assertFalse(checks["counts_valid_and_monotonic"])
                self.assertFalse(checks["details"][detail])
                for independent_detail, expected in independent.items():
                    self.assertEqual(checks["details"][independent_detail], expected)

    def test_every_bound_derived_and_counterfactual_field_fails_independently(self) -> None:
        mutations = [
            ("detector_beta", lambda p: p[0].__setitem__("beta", p[0]["beta"] * 0.99), "detector_beta_valid"),
            ("detector_gamma", lambda p: p[0].__setitem__("gamma", p[0]["gamma"] * 1.01), "detector_gamma_valid"),
            ("detector_distance", lambda p: p[0].__setitem__("laboratory_distance_m", np.asarray([0.0, 99.0, p[0]["laboratory_distance_m"][2]], dtype=np.float64)), "detector_laboratory_distance_valid"),
            ("detector_time", lambda p: p[0]["elapsed_time_s"].__setitem__(1, 99.0), "detector_elapsed_time_valid"),
            ("detector_lifetime", lambda p: p[0].__setitem__("mean_lifetime_s", 99.0), "detector_mean_lifetime_valid"),
            ("detector_exponent", lambda p: p[0]["decay_exponent"].__setitem__(1, 99.0), "detector_decay_exponent_valid"),
            ("detector_survival", lambda p: p[0]["survival_probability"].__setitem__(1, 0.4), "detector_survival_probability_valid"),
            ("muon_beta", lambda p: p[1].__setitem__("beta", p[1]["beta"] * 0.99), "muon_beta_valid"),
            ("muon_gamma", lambda p: p[1].__setitem__("gamma", p[1]["gamma"] * 1.01), "muon_gamma_valid"),
            ("muon_distance", lambda p: p[1]["contracted_distance_m"].__setitem__(1, 99.0), "muon_contracted_distance_valid"),
            ("muon_time", lambda p: p[1]["elapsed_time_s"].__setitem__(1, 99.0), "muon_elapsed_time_valid"),
            ("muon_lifetime", lambda p: p[1].__setitem__("mean_lifetime_s", 99.0), "muon_mean_lifetime_valid"),
            ("muon_exponent", lambda p: p[1]["decay_exponent"].__setitem__(1, 99.0), "muon_decay_exponent_valid"),
            ("muon_survival", lambda p: p[1]["survival_probability"].__setitem__(1, 0.4), "muon_survival_probability_valid"),
            ("counter_label", lambda p: p[2].__setitem__("label", "third frame"), "counterfactual_label_valid"),
            ("counter_distance", lambda p: p[2].__setitem__("laboratory_distance_m", np.asarray([0.0, 99.0, p[2]["laboratory_distance_m"][2]], dtype=np.float64)), "counterfactual_laboratory_distance_valid"),
            ("counter_time", lambda p: p[2]["elapsed_time_s"].__setitem__(1, 99.0), "counterfactual_elapsed_time_valid"),
            ("counter_exponent", lambda p: p[2]["decay_exponent"].__setitem__(1, 99.0), "counterfactual_decay_exponent_valid"),
            ("counter_survival", lambda p: p[2]["survival_probability"].__setitem__(1, 0.4), "counterfactual_survival_probability_valid"),
        ]
        for name, mutate, detail in mutations:
            with self.subTest(name=name):
                packet = list(copy.deepcopy(self.packet()))
                mutate(packet)
                checks = self.checks(tuple(packet))
                self.assertFalse(checks["numeric_shapes_dtypes_units_valid"])
                self.assertFalse(checks["details"][detail])

    def test_every_bound_unit_primitive_grid_and_raw_field_fails(self) -> None:
        for namespace, units, detail in (
            (0, reconstruct.DETECTOR_UNITS, "detector_units_valid"),
            (1, reconstruct.MUON_UNITS, "muon_units_valid"),
            (2, reconstruct.COUNTERFACTUAL_UNITS, "counterfactual_units_valid"),
            (4, reconstruct.PRIMITIVE_UNITS, "primitive_units_valid"),
        ):
            for key in units:
                with self.subTest(namespace=namespace, unit=key):
                    packet = list(copy.deepcopy(self.packet()))
                    packet[namespace]["units"][key] = "setup-toy-wrong-unit"
                    checks = self.checks(tuple(packet))
                    self.assertFalse(checks["numeric_shapes_dtypes_units_valid"])
                    self.assertFalse(checks["details"][detail])
        mutations = [
            ("raw_dtype", lambda p: p.__setitem__(7, p[7].astype(np.float32)), "dtypes_valid"),
            ("raw_finite", lambda p: p[7].__setitem__(1, np.nan), "raw_lifetimes_finite_nonnegative"),
            ("grid", lambda p: p.__setitem__(3, np.asarray([0.0, 0.0, p[3][2]], dtype=np.float64)), "grid_valid"),
            ("momentum", lambda p: p[4].__setitem__("momentum_mev_c", 1.1), "derived_fields_valid"),
            ("mass", lambda p: p[4].__setitem__("mass_energy_mev", 1.1), "derived_fields_valid"),
            ("tau0", lambda p: p[4].__setitem__("tau0_s", 1.1), "derived_fields_valid"),
            ("c", lambda p: p[4].__setitem__("c_m_s", 1.1), "derived_fields_valid"),
        ]
        for name, mutate, detail in mutations:
            with self.subTest(name=name):
                packet = list(copy.deepcopy(self.packet()))
                mutate(packet)
                checks = self.checks(tuple(packet))
                self.assertFalse(checks["numeric_shapes_dtypes_units_valid"])
                self.assertFalse(checks["details"][detail])

    def test_each_integrity_branch_fails_independently(self) -> None:
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
        for document_name, schema_name in (
            ("inputs.json", "inputs.schema.json"),
            ("constants.json", "constants.schema.json"),
            ("sources.json", "sources.schema.json"),
        ):
            self.assertTrue(validate_json_schema(
                load_json(EXPERIMENT_DIR / document_name),
                EXPERIMENT_DIR / "schemas" / schema_name,
            ))


if __name__ == "__main__":
    unittest.main()
