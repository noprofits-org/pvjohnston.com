"""Independent frame reconstructions and frozen Understanding checks.

This module has no command-line entry point. Setup tests use only visibly toy
inputs. The analyst later calls these functions on an admitted sealed sample.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from contract import ContractError


DIMENSIONLESS = "1"
DETECTOR_UNITS = {
    "beta": DIMENSIONLESS,
    "gamma": DIMENSIONLESS,
    "laboratory_distance_m": "m",
    "elapsed_time_s": "s",
    "mean_lifetime_s": "s",
    "decay_exponent": DIMENSIONLESS,
    "survival_probability": DIMENSIONLESS,
}
MUON_UNITS = {
    "beta": DIMENSIONLESS,
    "gamma": DIMENSIONLESS,
    "contracted_distance_m": "m",
    "elapsed_time_s": "s",
    "mean_lifetime_s": "s",
    "decay_exponent": DIMENSIONLESS,
    "survival_probability": DIMENSIONLESS,
}
COUNTERFACTUAL_UNITS = {
    "laboratory_distance_m": "m",
    "elapsed_time_s": "s",
    "decay_exponent": DIMENSIONLESS,
    "survival_probability": DIMENSIONLESS,
}
PRIMITIVE_UNITS = {
    "momentum_mev_c": "MeV/c",
    "mass_energy_mev": "MeV",
    "tau0_s": "s",
    "c_m_s": "m/s",
    "paths_m": "m",
}


def _validated_paths(paths_m: np.ndarray) -> np.ndarray:
    paths = np.asarray(paths_m, dtype=np.float64)
    if paths.ndim != 1 or paths.size == 0:
        raise ContractError("path grid must be a nonempty one-dimensional array")
    if not bool(np.all(np.isfinite(paths))) or bool(np.any(paths < 0.0)):
        raise ContractError("path grid must contain finite nonnegative distances")
    if bool(np.any(np.diff(paths) < 0.0)):
        raise ContractError("path grid must be monotonically nondecreasing")
    return paths


def _positive_primitives(momentum_mev_c: float, mass_energy_mev: float, tau0_s: float, c_m_s: float) -> None:
    values = np.asarray([momentum_mev_c, mass_energy_mev, tau0_s, c_m_s], dtype=np.float64)
    if not bool(np.all(np.isfinite(values))) or bool(np.any(values <= 0.0)):
        raise ContractError("frame primitives must be finite and positive")


def detector_frame(
    paths_m: np.ndarray,
    *,
    momentum_mev_c: float,
    mass_energy_mev: float,
    tau0_s: float,
    c_m_s: float,
) -> dict[str, Any]:
    """Detector route: laboratory time divided by the dilated mean lifetime."""

    paths = _validated_paths(paths_m)
    _positive_primitives(momentum_mev_c, mass_energy_mev, tau0_s, c_m_s)
    energy_mev = np.sqrt(momentum_mev_c * momentum_mev_c + mass_energy_mev * mass_energy_mev)
    gamma = energy_mev / mass_energy_mev
    beta = momentum_mev_c / energy_mev
    laboratory_time_s = paths / (beta * c_m_s)
    dilated_lifetime_s = gamma * tau0_s
    exponent = laboratory_time_s / dilated_lifetime_s
    survival = np.exp(-exponent)
    return {
        "beta": float(beta),
        "gamma": float(gamma),
        "laboratory_distance_m": paths,
        "elapsed_time_s": laboratory_time_s,
        "mean_lifetime_s": float(dilated_lifetime_s),
        "decay_exponent": exponent,
        "survival_probability": survival,
        "units": dict(DETECTOR_UNITS),
    }


def muon_frame(
    paths_m: np.ndarray,
    *,
    momentum_mev_c: float,
    mass_energy_mev: float,
    tau0_s: float,
    c_m_s: float,
) -> dict[str, Any]:
    """Muon route, independently deriving kinematics and contracted distance."""

    paths = _validated_paths(paths_m)
    _positive_primitives(momentum_mev_c, mass_energy_mev, tau0_s, c_m_s)
    momentum_to_mass_ratio = momentum_mev_c / mass_energy_mev
    gamma = np.sqrt(1.0 + momentum_to_mass_ratio * momentum_to_mass_ratio)
    beta = np.sqrt(1.0 - 1.0 / (gamma * gamma))
    contracted_distance_m = paths / gamma
    proper_elapsed_time_s = contracted_distance_m / (beta * c_m_s)
    exponent = proper_elapsed_time_s / tau0_s
    survival = np.exp(-exponent)
    return {
        "beta": float(beta),
        "gamma": float(gamma),
        "contracted_distance_m": contracted_distance_m,
        "elapsed_time_s": proper_elapsed_time_s,
        "mean_lifetime_s": float(tau0_s),
        "decay_exponent": exponent,
        "survival_probability": survival,
        "units": dict(MUON_UNITS),
    }


def same_speed_no_lifetime_dilation_counterfactual(
    paths_m: np.ndarray,
    *,
    detector_beta: float,
    tau0_s: float,
    c_m_s: float,
) -> dict[str, Any]:
    paths = _validated_paths(paths_m)
    values = np.asarray([detector_beta, tau0_s, c_m_s], dtype=np.float64)
    if not bool(np.all(np.isfinite(values))) or not 0.0 < detector_beta < 1.0 or tau0_s <= 0.0 or c_m_s <= 0.0:
        raise ContractError("counterfactual primitives are invalid")
    laboratory_time_s = paths / (detector_beta * c_m_s)
    exponent = laboratory_time_s / tau0_s
    return {
        "label": "same-speed, no-lifetime-dilation counterfactual",
        "laboratory_distance_m": paths,
        "elapsed_time_s": laboratory_time_s,
        "decay_exponent": exponent,
        "survival_probability": np.exp(-exponent),
        "units": dict(COUNTERFACTUAL_UNITS),
    }


def empirical_survival(proper_lifetimes_s: np.ndarray, proper_time_thresholds_s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lifetimes = np.asarray(proper_lifetimes_s)
    thresholds = np.asarray(proper_time_thresholds_s, dtype=np.float64)
    if lifetimes.ndim != 1 or lifetimes.dtype != np.dtype("float64") or lifetimes.size == 0:
        raise ContractError("proper lifetimes must be a nonempty one-dimensional float64 array")
    if thresholds.ndim != 1 or thresholds.size == 0:
        raise ContractError("proper-time thresholds must be one-dimensional and nonempty")
    if not bool(np.all(np.isfinite(lifetimes))) or bool(np.any(lifetimes < 0.0)):
        raise ContractError("proper lifetimes contain an invalid value")
    if not bool(np.all(np.isfinite(thresholds))) or bool(np.any(thresholds < 0.0)) or bool(np.any(np.diff(thresholds) < 0.0)):
        raise ContractError("proper-time thresholds are invalid or unordered")
    counts = np.asarray([np.count_nonzero(lifetimes >= threshold) for threshold in thresholds], dtype=np.int64)
    return counts, counts.astype(np.float64) / lifetimes.size


def _relative_error(left: np.ndarray | float, right: np.ndarray | float) -> np.ndarray:
    left_array = np.asarray(left, dtype=np.float64)
    right_array = np.asarray(right, dtype=np.float64)
    denominator = np.maximum(np.abs(left_array), np.abs(right_array))
    return np.divide(
        np.abs(left_array - right_array),
        denominator,
        out=np.where(np.abs(left_array - right_array) == 0.0, 0.0, np.inf),
        where=denominator != 0.0,
    )


def evaluate_checks(
    detector: Mapping[str, Any],
    muon: Mapping[str, Any],
    counterfactual: Mapping[str, Any],
    paths_m: np.ndarray,
    primitives: Mapping[str, Any],
    counts: np.ndarray,
    empirical_probability: np.ndarray,
    proper_lifetimes_s: np.ndarray,
    *,
    focal_index: int,
    expected_grid_size: int,
    expected_draw_count: int,
    frame_relative_tolerance: float,
    standard_error_multiplier: float,
    maximum_grid_discrepancy: float,
    integrity_flags: Mapping[str, bool],
) -> dict[str, Any]:
    """Evaluate every frozen fidelity branch; tests inject only tiny dimensions."""

    paths = np.asarray(paths_m)
    detector_probability = np.asarray(detector["survival_probability"])
    muon_probability = np.asarray(muon["survival_probability"])
    detector_exponent = np.asarray(detector["decay_exponent"])
    muon_exponent = np.asarray(muon["decay_exponent"])
    counts_array = np.asarray(counts)
    empirical_array = np.asarray(empirical_probability)
    lifetimes = np.asarray(proper_lifetimes_s)
    required_arrays = (
        paths,
        detector_probability,
        muon_probability,
        detector_exponent,
        muon_exponent,
        np.asarray(detector["laboratory_distance_m"]),
        np.asarray(detector["elapsed_time_s"]),
        np.asarray(muon["contracted_distance_m"]),
        np.asarray(muon["elapsed_time_s"]),
        np.asarray(counterfactual["laboratory_distance_m"]),
        np.asarray(counterfactual["elapsed_time_s"]),
        np.asarray(counterfactual["decay_exponent"]),
        np.asarray(counterfactual["survival_probability"]),
        empirical_array,
    )
    shapes_ok = all(
        array.shape == (expected_grid_size,)
        for array in (*required_arrays, counts_array)
    ) and lifetimes.shape == (expected_draw_count,)
    if not shapes_ok or not 0 <= focal_index < expected_grid_size:
        passes = {
            "frame_agreement": False,
            "focal_monte_carlo_within_four_standard_errors": False,
            "maximum_grid_discrepancy_at_most_threshold": False,
            "counts_valid_and_monotonic": False,
            "numeric_shapes_dtypes_units_valid": False,
            "schema_manifest_provenance_and_hashes_valid": False,
        }
        return {**passes, "all_passed": False, "details": {"shapes_valid": False}, "diagnostics": {}}

    momentum = primitives.get("momentum_mev_c")
    mass = primitives.get("mass_energy_mev")
    tau0 = primitives.get("tau0_s")
    c_m_s = primitives.get("c_m_s")
    primitive_values = np.asarray([momentum, mass, tau0, c_m_s], dtype=np.float64)
    primitive_field_valid = {
        "primitive_momentum_mev_c_valid": bool(np.isfinite(momentum) and momentum > 0.0),
        "primitive_mass_energy_mev_valid": bool(np.isfinite(mass) and mass > 0.0),
        "primitive_tau0_s_valid": bool(np.isfinite(tau0) and tau0 > 0.0),
        "primitive_c_m_s_valid": bool(np.isfinite(c_m_s) and c_m_s > 0.0),
        "primitive_units_valid": primitives.get("units") == PRIMITIVE_UNITS,
    }
    primitives_valid = all(primitive_field_valid.values())
    grid_valid = (
        paths.dtype == np.dtype("float64")
        and bool(np.all(np.isfinite(paths)))
        and bool(np.all(paths >= 0.0))
        and paths[0] == 0.0
        and bool(np.all(np.diff(paths) > 0.0))
    )

    detector_energy = np.sqrt(momentum * momentum + mass * mass)
    expected_detector_gamma = detector_energy / mass
    expected_detector_beta = momentum / detector_energy
    expected_detector_time = paths / (expected_detector_beta * c_m_s)
    expected_detector_lifetime = expected_detector_gamma * tau0
    expected_detector_exponent = expected_detector_time / expected_detector_lifetime
    ratio = momentum / mass
    expected_muon_gamma = np.sqrt(1.0 + ratio * ratio)
    expected_muon_beta = np.sqrt(1.0 - 1.0 / (expected_muon_gamma * expected_muon_gamma))
    expected_contracted_distance = paths / expected_muon_gamma
    expected_muon_time = expected_contracted_distance / (expected_muon_beta * c_m_s)
    expected_muon_exponent = expected_muon_time / tau0
    expected_counter_time = paths / (expected_detector_beta * c_m_s)
    expected_counter_exponent = expected_counter_time / tau0

    def close(actual: Any, expected: Any) -> bool:
        return bool(np.allclose(np.asarray(actual), np.asarray(expected), rtol=frame_relative_tolerance, atol=0.0, equal_nan=False))

    derived_field_valid = {
        "detector_beta_valid": close(detector["beta"], expected_detector_beta),
        "detector_gamma_valid": close(detector["gamma"], expected_detector_gamma),
        "detector_laboratory_distance_valid": bool(np.array_equal(np.asarray(detector["laboratory_distance_m"]), paths)),
        "detector_elapsed_time_valid": close(detector["elapsed_time_s"], expected_detector_time),
        "detector_mean_lifetime_valid": close(detector["mean_lifetime_s"], expected_detector_lifetime),
        "detector_decay_exponent_valid": close(detector_exponent, expected_detector_exponent),
        "detector_survival_probability_valid": close(detector_probability, np.exp(-expected_detector_exponent)),
        "muon_beta_valid": close(muon["beta"], expected_muon_beta),
        "muon_gamma_valid": close(muon["gamma"], expected_muon_gamma),
        "muon_contracted_distance_valid": close(muon["contracted_distance_m"], expected_contracted_distance),
        "muon_elapsed_time_valid": close(muon["elapsed_time_s"], expected_muon_time),
        "muon_mean_lifetime_valid": close(muon["mean_lifetime_s"], tau0),
        "muon_decay_exponent_valid": close(muon_exponent, expected_muon_exponent),
        "muon_survival_probability_valid": close(muon_probability, np.exp(-expected_muon_exponent)),
    }
    derived_fields_valid = all(derived_field_valid.values())
    counterfactual_field_valid = {
        "counterfactual_label_valid": counterfactual.get("label") == "same-speed, no-lifetime-dilation counterfactual",
        "counterfactual_units_valid": counterfactual.get("units") == COUNTERFACTUAL_UNITS,
        "counterfactual_laboratory_distance_valid": bool(np.array_equal(np.asarray(counterfactual["laboratory_distance_m"]), paths)),
        "counterfactual_elapsed_time_valid": close(counterfactual["elapsed_time_s"], expected_counter_time),
        "counterfactual_decay_exponent_valid": close(counterfactual["decay_exponent"], expected_counter_exponent),
        "counterfactual_survival_probability_valid": close(counterfactual["survival_probability"], np.exp(-expected_counter_exponent)),
    }
    counterfactual_valid = all(counterfactual_field_valid.values())
    detector_units_valid = detector.get("units") == DETECTOR_UNITS
    muon_units_valid = muon.get("units") == MUON_UNITS
    units_valid = detector_units_valid and muon_units_valid
    dtype_valid = (
        all(array.dtype == np.dtype("float64") for array in required_arrays)
        and counts_array.dtype == np.dtype("int64")
        and lifetimes.dtype == np.dtype("float64")
    )
    frame_probability_error = float(np.max(_relative_error(detector_probability, muon_probability)))
    nonzero = np.arange(expected_grid_size) != 0
    exponent_error = float(np.max(_relative_error(detector_exponent[nonzero], muon_exponent[nonzero]))) if bool(np.any(nonzero)) else 0.0
    beta_error = float(_relative_error(detector["beta"], muon["beta"]))
    gamma_error = float(_relative_error(detector["gamma"], muon["gamma"]))
    zero_exponents_exact = detector_exponent[0] == 0.0 and muon_exponent[0] == 0.0
    frame_agreement = (
        frame_probability_error <= frame_relative_tolerance
        and exponent_error <= frame_relative_tolerance
        and beta_error <= frame_relative_tolerance
        and gamma_error <= frame_relative_tolerance
        and zero_exponents_exact
    )
    focal_analytic = float(detector_probability[focal_index])
    focal_empirical = float(empirical_array[focal_index])
    standard_error = float(np.sqrt(focal_analytic * (1.0 - focal_analytic) / expected_draw_count))
    focal_within_error = abs(focal_empirical - focal_analytic) <= standard_error_multiplier * standard_error
    max_grid_discrepancy = float(np.max(np.abs(empirical_array - detector_probability)))
    max_grid_ok = max_grid_discrepancy <= maximum_grid_discrepancy
    count_field_valid = {
        "count_dtype_valid": counts_array.dtype == np.dtype("int64"),
        "count_bounds_valid": bool(np.all((0 <= counts_array) & (counts_array <= expected_draw_count))),
        "zero_distance_count_valid": int(counts_array[0]) == expected_draw_count,
        "counts_monotonic": bool(np.all(np.diff(counts_array) <= 0)),
        "empirical_matches_counts": bool(np.array_equal(empirical_array, counts_array.astype(np.float64) / expected_draw_count)),
    }
    counts_valid = all(count_field_valid.values())
    numeric_valid = (
        shapes_ok
        and dtype_valid
        and primitives_valid
        and grid_valid
        and derived_fields_valid
        and counterfactual_valid
        and units_valid
        and bool(np.all(np.isfinite(lifetimes)))
        and not bool(np.any(lifetimes < 0.0))
        and all(bool(np.all(np.isfinite(array))) for array in required_arrays)
    )
    integrity_ok = set(integrity_flags) == {"schema", "manifest", "provenance", "hashes", "run_bundle", "run_admission"} and all(value is True for value in integrity_flags.values())
    passes = {
        "frame_agreement": bool(frame_agreement),
        "focal_monte_carlo_within_four_standard_errors": bool(focal_within_error),
        "maximum_grid_discrepancy_at_most_threshold": bool(max_grid_ok),
        "counts_valid_and_monotonic": bool(counts_valid),
        "numeric_shapes_dtypes_units_valid": bool(numeric_valid),
        "schema_manifest_provenance_and_hashes_valid": bool(integrity_ok),
    }
    return {
        **passes,
        "all_passed": all(passes.values()),
        "details": {
            "shapes_valid": bool(shapes_ok),
            "dtypes_valid": bool(dtype_valid),
            "primitive_inputs_valid": bool(primitives_valid),
            "grid_valid": bool(grid_valid),
            "derived_fields_valid": bool(derived_fields_valid),
            "counterfactual_valid": bool(counterfactual_valid),
            "units_valid": bool(units_valid),
            "detector_units_valid": bool(detector_units_valid),
            "muon_units_valid": bool(muon_units_valid),
            "raw_lifetimes_finite_nonnegative": bool(np.all(np.isfinite(lifetimes)) and not np.any(lifetimes < 0.0)),
            **primitive_field_valid,
            **derived_field_valid,
            **counterfactual_field_valid,
            **count_field_valid,
        },
        "diagnostics": {
            "frame_probability_max_relative_error": frame_probability_error,
            "frame_exponent_max_relative_error_nonzero_path": exponent_error,
            "beta_relative_error": beta_error,
            "gamma_relative_error": gamma_error,
            "focal_binomial_standard_error": standard_error,
            "focal_absolute_discrepancy": abs(focal_empirical - focal_analytic),
            "maximum_grid_absolute_discrepancy": max_grid_discrepancy,
        },
    }


def to_json_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: to_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_value(item) for item in value]
    return value


def assemble_understanding_result(
    *,
    source_run: Mapping[str, Any],
    primitive_inputs: Mapping[str, Any],
    paths_m: np.ndarray,
    detector: Mapping[str, Any],
    muon: Mapping[str, Any],
    counterfactual: Mapping[str, Any],
    counts: np.ndarray,
    empirical_probability: np.ndarray,
    focal_index: int,
    checks: Mapping[str, Any],
) -> dict[str, Any]:
    return to_json_value({
        "schema_version": 1,
        "experiment": "muon-survival-two-frames",
        "post_type": "understanding",
        "outcome_kind": "understanding-observations-no-verdict",
        "source_run": dict(source_run),
        "primitive_inputs": dict(primitive_inputs),
        "grid_m": np.asarray(paths_m, dtype=np.float64),
        "detector_frame": dict(detector),
        "muon_frame": dict(muon),
        "same_speed_no_lifetime_dilation_counterfactual": dict(counterfactual),
        "empirical": {
            "counts": counts,
            "survival_probability": empirical_probability,
            "inclusive_comparison": "proper_lifetime_s >= proper_elapsed_time_s",
        },
        "focal": {
            "index": focal_index,
            "detector": {key: value[focal_index] if isinstance(value, np.ndarray) else value for key, value in detector.items()},
            "muon": {key: value[focal_index] if isinstance(value, np.ndarray) else value for key, value in muon.items()},
            "counterfactual": {key: value[focal_index] if isinstance(value, np.ndarray) else value for key, value in counterfactual.items()},
            "empirical_count": counts[focal_index],
            "empirical_survival_probability": empirical_probability[focal_index],
        },
        "checks": dict(checks),
    })
