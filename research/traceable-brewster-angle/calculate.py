#!/usr/bin/env python3

"""Calculate a small, deterministic Fresnel/Brewster-angle demonstration."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
INPUTS_PATH = EXPERIMENT_DIR / "inputs.json"
RESULTS_PATH = EXPERIMENT_DIR / "results.json"


def fresnel(angle_degrees: float, n1: float, n2: float) -> dict[str, float]:
    """Return lossless s/p power coefficients for one incident angle."""

    incident = math.radians(angle_degrees)
    transmitted = math.asin((n1 / n2) * math.sin(incident))
    cos_i = math.cos(incident)
    cos_t = math.cos(transmitted)

    r_s = (n1 * cos_i - n2 * cos_t) / (n1 * cos_i + n2 * cos_t)
    r_p = (n2 * cos_i - n1 * cos_t) / (n2 * cos_i + n1 * cos_t)
    t_s = (2 * n1 * cos_i) / (n1 * cos_i + n2 * cos_t)
    t_p = (2 * n1 * cos_i) / (n2 * cos_i + n1 * cos_t)
    power_scale = (n2 * cos_t) / (n1 * cos_i)

    return {
        "angle_degrees": angle_degrees,
        "transmitted_angle_degrees": math.degrees(transmitted),
        "s_reflectance": r_s * r_s,
        "p_reflectance": r_p * r_p,
        "s_transmittance": power_scale * t_s * t_s,
        "p_transmittance": power_scale * t_p * t_p,
    }


def build_results() -> dict[str, object]:
    source = json.loads(INPUTS_PATH.read_text(encoding="utf-8"))
    model = source["model"]
    checks = source["checks"]
    n1 = float(model["incident_refractive_index"])
    n2 = float(model["transmitted_refractive_index"])
    start = float(model["sweep_start_degrees"])
    stop = float(model["sweep_stop_degrees"])
    step = float(model["sweep_step_degrees"])
    grid_tolerance = float(checks["grid_angle_tolerance_degrees"])
    analytic_tolerance = float(checks["analytic_p_reflectance_max"])
    energy_tolerance = float(checks["energy_balance_error_max"])

    if not all(
        math.isfinite(value)
        for value in (
            n1,
            n2,
            start,
            stop,
            step,
            grid_tolerance,
            analytic_tolerance,
            energy_tolerance,
        )
    ):
        raise ValueError("model inputs and tolerances must be finite")
    if not (0 < n1 < n2):
        raise ValueError("this demonstration requires 0 < n1 < n2")
    if not (0 <= start < stop < 90):
        raise ValueError("the sweep must satisfy 0 <= start < stop < 90 degrees")
    if step <= 0:
        raise ValueError("the sweep step must be positive")
    if min(grid_tolerance, analytic_tolerance, energy_tolerance) < 0:
        raise ValueError("check tolerances must be nonnegative")
    step_count_float = (stop - start) / step
    step_count = round(step_count_float)
    if not math.isclose(step_count_float, step_count, rel_tol=0, abs_tol=1e-12):
        raise ValueError("the angle interval must contain an integer number of steps")

    angles = [start + index * step for index in range(step_count + 1)]
    sweep = [fresnel(angle, n1, n2) for angle in angles]
    minimum = min(sweep, key=lambda row: (row["p_reflectance"], row["angle_degrees"]))

    max_energy_error = -1.0
    max_energy_angle = start
    max_energy_polarization = "s"
    for row in sweep:
        for polarization in ("s", "p"):
            error = abs(
                row[f"{polarization}_reflectance"]
                + row[f"{polarization}_transmittance"]
                - 1.0
            )
            if error > max_energy_error:
                max_energy_error = error
                max_energy_angle = row["angle_degrees"]
                max_energy_polarization = polarization

    brewster_angle = math.degrees(math.atan(n2 / n1))
    analytic = fresnel(brewster_angle, n1, n2)
    normal = fresnel(0.0, n1, n2)
    grid_angle_error = abs(minimum["angle_degrees"] - brewster_angle)

    return {
        "schema_version": 1,
        "model": model,
        "criteria": checks,
        "analytic": {
            "index_ratio": n2 / n1,
            "brewster_angle_degrees": brewster_angle,
            "p_reflectance": analytic["p_reflectance"],
            "s_reflectance": analytic["s_reflectance"],
            "unpolarized_reflectance": (
                analytic["p_reflectance"] + analytic["s_reflectance"]
            )
            / 2,
        },
        "normal_incidence": {
            "reflectance": normal["p_reflectance"],
        },
        "sweep": {
            "sample_count": len(sweep),
            "minimum_p_reflectance": minimum["p_reflectance"],
            "minimum_angle_degrees": minimum["angle_degrees"],
            "analytic_angle_error_degrees": grid_angle_error,
            "maximum_energy_balance_error": max_energy_error,
            "maximum_energy_balance_angle_degrees": max_energy_angle,
            "maximum_energy_balance_polarization": max_energy_polarization,
        },
        "checks": {
            "analytic_null_within_tolerance": (
                analytic["p_reflectance"] <= analytic_tolerance
            ),
            "grid_angle_within_tolerance": (
                grid_angle_error <= grid_tolerance
            ),
            "energy_balance_within_tolerance": (
                max_energy_error <= energy_tolerance
            ),
        },
    }


def main() -> int:
    arguments = sys.argv[1:]
    if arguments not in ([], ["--check"]):
        print(f"usage: {Path(sys.argv[0]).name} [--check]", file=sys.stderr)
        return 2

    expected = json.dumps(build_results(), indent=2, sort_keys=True) + "\n"
    if arguments == ["--check"]:
        if not RESULTS_PATH.exists():
            print("results.json is missing; run calculate.py first", file=sys.stderr)
            return 1
        if RESULTS_PATH.read_text(encoding="utf-8") != expected:
            print("results.json is stale; rerun calculate.py", file=sys.stderr)
            return 1
        print("calculate.py: results.json is current")
        return 0

    RESULTS_PATH.write_text(expected, encoding="utf-8")
    print(f"wrote {RESULTS_PATH.relative_to(EXPERIMENT_DIR.parents[1])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
