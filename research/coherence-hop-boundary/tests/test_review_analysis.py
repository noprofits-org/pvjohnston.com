#!/usr/bin/env python3
"""Integration checks for the reviewed dual-lane canonical analysis."""

from __future__ import annotations

import copy
import hashlib
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

FROZEN_SCHEMA_V2_ENVIRONMENT = {
    "schema_version": 2,
    "python_implementation": "CPython",
    "python": "3.12.9",
    "numpy": "2.2.5",
    "operating_system": "Linux",
    "machine": "x86_64",
    "openblas_num_threads": "1",
}


def environment_artifact(environment: dict[str, object]) -> dict[str, object]:
    return {
        "environment": environment,
        "environment_fingerprint": hashlib.sha256(
            module._canonical_json(environment).encode("utf-8")
        ).hexdigest(),
    }


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

    def test_schema_v1_environment_remains_accepted_and_self_verifying(self) -> None:
        module._validate_environment_fingerprint(
            self.legacy_convergence, "legacy convergence"
        )
        artifact = copy.deepcopy(self.legacy_convergence)
        artifact["environment"]["platform"] = "Linux-different-kernel"
        with self.assertRaisesRegex(ValueError, "fingerprint is stale or edited"):
            module._validate_environment_fingerprint(
                artifact, "legacy convergence"
            )

    def test_complete_frozen_schema_v2_environment_is_accepted(self) -> None:
        artifact = environment_artifact(
            copy.deepcopy(FROZEN_SCHEMA_V2_ENVIRONMENT)
        )
        module._validate_environment_fingerprint(artifact, "schema-v2 fixture")
        self.assertEqual(
            module.FROZEN_STABLE_ENVIRONMENT,
            FROZEN_SCHEMA_V2_ENVIRONMENT,
        )

    def test_schema_v2_rejects_self_consistent_tamper_of_every_frozen_value(
        self,
    ) -> None:
        replacements = {
            "schema_version": 3,
            "python_implementation": "PyPy",
            "python": "3.12.8",
            "numpy": "2.2.4",
            "operating_system": "Darwin",
            "machine": "aarch64",
            "openblas_num_threads": "2",
        }
        self.assertEqual(
            set(replacements), set(FROZEN_SCHEMA_V2_ENVIRONMENT)
        )
        for field, replacement in replacements.items():
            with self.subTest(field=field):
                environment = copy.deepcopy(FROZEN_SCHEMA_V2_ENVIRONMENT)
                environment[field] = replacement
                artifact = environment_artifact(environment)
                with self.assertRaises(ValueError):
                    module._validate_environment_fingerprint(
                        artifact, f"tampered {field}"
                    )


if __name__ == "__main__":
    unittest.main()
