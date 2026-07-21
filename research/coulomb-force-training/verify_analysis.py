"""Cheap analysis-reproducibility check for the Coulomb force-training sweep.

Does NOT retrain the networks (that is the expensive step in run_experiment.py).
It re-validates the analytic H2+ model, then reloads the committed per-seed RMSE
table in results.json and recomputes the median A/B ratios and the crossover
cutoffs from it, asserting they match the stored `derived` projection. This is
what `generate-metrics.mjs --check` and `scripts/verify-metrics.mjs` invoke.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

import h2plus_model as h2


def main(argv):
    if argv and argv[0] not in ("--check",):
        print("usage: python3 verify_analysis.py [--check]", file=sys.stderr)
        return 2

    h2._self_test()

    results_path = Path(__file__).parent / "results.json"
    if not results_path.exists():
        print("results.json missing; run run_experiment.py first", file=sys.stderr)
        return 1
    data = json.loads(results_path.read_text())

    cutoffs = data["protocol"]["cutoffs_bohr"]
    seeds = data["protocol"]["init_seeds"]
    rmse = data["rmse_cm"]

    for loss_name in ("energy", "energy_force"):
        per_cutoff = data["derived"][loss_name]["per_cutoff"]
        recomputed_cross = None
        for cutoff in cutoffs:
            key = f"{cutoff:.2f}"
            ratios, a_list, b_list = [], [], []
            for seed in seeds:
                a = rmse[loss_name]["A"][str(seed)][key]
                b = rmse[loss_name]["B"][str(seed)][key]
                ratios.append(a / b)
                a_list.append(a)
                b_list.append(b)
            med = float(np.median(ratios))
            stored = per_cutoff[key]["median_ab_ratio"]
            assert abs(med - stored) < 1e-9, (loss_name, key, med, stored)
            assert abs(float(np.median(a_list)) - per_cutoff[key]["median_rmse_a_cm"]) < 1e-6
            assert abs(float(np.median(b_list)) - per_cutoff[key]["median_rmse_b_cm"]) < 1e-6
            if recomputed_cross is None and med <= 1.0:
                recomputed_cross = cutoff
        assert recomputed_cross == data["derived"][loss_name]["crossover_cutoff"], (
            loss_name, recomputed_cross, data["derived"][loss_name]["crossover_cutoff"])

    print("verify_analysis: model and derived projection are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
