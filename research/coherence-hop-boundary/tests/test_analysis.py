#!/usr/bin/env python3
"""Fast fixture tests for the canonical coherence-hop analysis."""

from __future__ import annotations

import gzip
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "analyse.py"
SPEC = importlib.util.spec_from_file_location("coherence_hop_analysis", MODULE_PATH)
assert SPEC and SPEC.loader
analysis_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis_module)


FINGERPRINTS = {
    "model_fingerprint": "fixture-model",
    "simulator_sha256": "fixture-simulator",
    "config_sha256": "fixture-config",
    "environment_fingerprint": "fixture-environment",
}


def exact_trace(grid_n: int) -> dict:
    return {
        "configuration": {
            "grid_n": grid_n,
            "half_width": 96.0,
            "requested_dt_fs": 0.025,
            "total_fs": 20.0,
            "center_fraction": 0.5,
            "momentum_kick_toward_ci_sigma_px": 0.0,
            **FINGERPRINTS,
        },
        "time_fs": [0.0, 6.0, 12.0, 20.0],
        "upper_population": [0.20, 0.24, 0.30, 0.34],
        "product_qx_lt_0": [0.10, 0.20, 0.40, 0.60],
        "centroid_x": [1.0, 0.5, 0.0, -0.5],
        "ensemble_coherence_real": [1.0, 0.8, 0.3, 0.2],
        "ensemble_coherence_imag": [0.0, 0.0, 0.0, 0.0],
        "coherence_amplitude": [1.0, 0.8, 0.3, 0.2],
        "mean_trajectory_coherence_magnitude": [1.0, 0.8, 0.3, 0.2],
        "norm": [1.0, 1.0, 1.0, 1.0],
    }


def trajectory_run(scale: float, seed: int, rank: int, *, dt_fs: float = 0.025, substeps: int = 10) -> dict:
    magnitude = 0.015 + 0.018 * rank
    full = {
        "upper_population": [0.20, 0.24, 0.30, 0.34],
        "product_qx_lt_0": [0.10, 0.20, 0.40, 0.60],
        "centroid_x": [1.0, 0.5, 0.0, -0.5],
        "ensemble_coherence_real": [1.0, 0.8, 0.3, 0.2],
        "ensemble_coherence_imag": [0.0, 0.0, 0.0, 0.0],
        "coherence_amplitude": [1.0, 0.8, 0.3, 0.2],
        "mean_trajectory_coherence_magnitude": [1.0, 0.8, 0.3, 0.2],
    }
    rp_coherence = [value - 0.7 * magnitude for value in full["coherence_amplitude"]]
    rp = {
        "upper_population": [value - magnitude for value in full["upper_population"]],
        "product_qx_lt_0": [value - 0.9 * magnitude for value in full["product_qx_lt_0"]],
        "centroid_x": [value - 8.035823190306067 * 1.5 * magnitude for value in full["centroid_x"]],
        "ensemble_coherence_real": rp_coherence,
        "ensemble_coherence_imag": [0.0, 0.0, 0.0, 0.0],
        "coherence_amplitude": rp_coherence,
        "mean_trajectory_coherence_magnitude": full["mean_trajectory_coherence_magnitude"],
    }
    records = []
    early_count = rank + 1
    for trajectory_id in range(7):
        records.append({
            "trajectory_id": trajectory_id,
            "time_fs": 5.0 if trajectory_id < early_count else 15.0,
            "from_state": trajectory_id % 2,
            "to_state": 1 - trajectory_id % 2,
            "outcome": "accepted",
            "recrossing": False,
        })
    records.extend([
        {
            "trajectory_id": 0, "time_fs": 8.0, "from_state": 1,
            "to_state": 0, "outcome": "accepted", "recrossing": True,
        },
        {
            "trajectory_id": 8, "time_fs": 7.0, "from_state": 0,
            "to_state": 1, "outcome": "frustrated", "recrossing": False,
        },
    ])
    return {
        "configuration": {
            "pfm_rate_scale": scale, "seed": seed, "geometry_count": 4000,
            "dt_fs": dt_fs, "electronic_substeps": substeps,
            "initial_sigma_x": 8.035823190306067,
            "total_fs": 20.0, "center_fraction": 0.5,
            "momentum_kick_toward_ci_sigma_px": 0.0,
            **FINGERPRINTS,
        },
        "time_fs": [0.0, 6.0, 12.0, 20.0],
        "full": full,
        "reprop_axe": rp,
        "events": {"full": records, "axe": []},
    }


class AnalysisFixtureTest(unittest.TestCase):
    def test_load_accepts_deterministic_gzip_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.json.gz"
            path.write_bytes(gzip.compress(json.dumps({"ok": True}).encode(), mtime=0))
            self.assertEqual(analysis_module._load(path), {"ok": True})

    def test_full_projection_and_figure_are_deterministic(self) -> None:
        scales = analysis_module.DECLARED_SCALES
        runs = [
            trajectory_run(scale, seed, rank, dt_fs=0.0125, substeps=20)
            for rank, scale in enumerate(scales)
            for seed in (2701, 2702, 2703, 2704)
        ]
        lineage = {**FINGERPRINTS, "comparison": {
            "accepted_events_identical": True,
            "max_abs_observable_difference": 0.0,
            "tolerance": 1.0e-12,
            "passed": True,
        }}
        convergence = {
            **FINGERPRINTS,
            "complete": True,
            "candidate": [
                trajectory_run(0.05, seed, 6, dt_fs=0.0125, substeps=20)
                for seed in (2687, 2688, 2689, 2690, 2691, 2692, 2693, 2694)
            ],
            "reference": [
                trajectory_run(0.05, seed, 6, dt_fs=0.00625, substeps=40)
                for seed in (2687, 2688, 2689, 2690, 2691, 2692, 2693, 2694)
            ],
        }
        exact = {**FINGERPRINTS, "coarse": exact_trace(384), "fine": exact_trace(512)}
        document = analysis_module.build_analysis(
            lineage, convergence, exact, {
                **FINGERPRINTS,
                "complete": True,
                "scales": list(scales),
                "seeds": [2701, 2702, 2703, 2704],
                "declared_replicates": 28,
                "completed_replicates": 28,
                "runs": runs,
            }
        )

        self.assertEqual(document["schema_version"], 1)
        self.assertEqual(len(document["regimes"]), 7)
        self.assertTrue(document["exact_grid_gate"]["coarse_grid_accepted"])
        self.assertTrue(document["convergence_gate"]["candidate_setting_accepted"])
        self.assertEqual(document["hypothesis"]["verdict"], "supported")
        self.assertEqual(
            document["exploratory_spearman_early_hop_vs_error"]
            ["upper_population"]["rho"],
            1.0,
        )
        final = document["regimes"][-1]
        self.assertEqual(final["event_diagnostics"]["accepted"], 32)
        self.assertEqual(final["event_diagnostics"]["repeat_hop_events"], 4)
        self.assertEqual(final["event_diagnostics"]["recrossing_events"], 4)
        self.assertEqual(final["event_diagnostics"]["trajectory_count"], 16000)
        self.assertAlmostEqual(
            final["event_diagnostics"]["repeat_hopping_trajectory_fraction"],
            4 / 16000,
        )
        self.assertEqual(
            final["event_diagnostics"]["timing"]["early"]["first_accepted"], 28
        )
        self.assertEqual(
            final["event_diagnostics"]["timing"]["early"]["repeat_accepted"], 4
        )
        self.assertEqual(final["intervals_95"]["early_hop_fraction"]["n"], 4)
        self.assertIn("coherence_amplitude", final["rmse_to_exact"]["full"])

        try:
            from PIL import Image
            import matplotlib  # noqa: F401
        except ImportError:
            self.skipTest("publication-figure dependencies are not installed")
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first.png"
            second = Path(temporary) / "second.png"
            analysis_module.render_figure(document, first)
            analysis_module.render_figure(document, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with Image.open(first) as image:
                self.assertEqual(image.size, (1200, 630))


if __name__ == "__main__":
    unittest.main()
