#!/usr/bin/env python3

"""Calculate a deterministic single-relaxation-time Debye demonstration."""

from __future__ import annotations

import cmath
import json
import math
import sys
from pathlib import Path
from typing import Any


EXPERIMENT_DIR = Path(__file__).resolve().parent
INPUTS_PATH = EXPERIMENT_DIR / "inputs.json"
RESULTS_PATH = EXPERIMENT_DIR / "results.json"


def require_finite_number(value: Any, label: str) -> float:
    """Return one finite, non-boolean JSON number or raise a useful error."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def validate_inputs(source: dict[str, Any]) -> None:
    """Validate the small declared-input surface before calculating."""

    if not isinstance(source, dict):
        raise ValueError("inputs root must be an object")
    if source.get("schema_version") != 1:
        raise ValueError("inputs schema_version must be 1")

    constants = source.get("constants")
    conditions = source.get("conditions")
    materials = source.get("materials")
    frequencies = source.get("frequencies_hz")
    checks = source.get("checks")
    if not all(
        isinstance(section, dict)
        for section in (constants, conditions, materials, frequencies, checks)
    ):
        raise ValueError(
            "constants, conditions, materials, frequencies_hz, and checks "
            "must be objects"
        )

    for name in (
        "speed_of_light_m_per_s",
        "planck_constant_j_s",
        "elementary_charge_c",
        "boltzmann_constant_j_per_k",
    ):
        if require_finite_number(constants.get(name), f"constants.{name}") <= 0:
            raise ValueError(f"constants.{name} must be positive")

    if require_finite_number(
        conditions.get("room_temperature_k"),
        "conditions.room_temperature_k",
    ) <= 0:
        raise ValueError("conditions.room_temperature_k must be positive")

    for material_name in ("liquid_water_25_c", "ice_minus_10_c"):
        material = materials.get(material_name)
        if not isinstance(material, dict):
            raise ValueError(f"materials.{material_name} must be an object")
        require_finite_number(
            material.get("temperature_c"),
            f"materials.{material_name}.temperature_c",
        )
        static = require_finite_number(
            material.get("static_relative_permittivity"),
            f"materials.{material_name}.static_relative_permittivity",
        )
        high_frequency = require_finite_number(
            material.get("high_frequency_relative_permittivity"),
            f"materials.{material_name}.high_frequency_relative_permittivity",
        )
        if not (static > high_frequency > 0):
            raise ValueError(
                f"materials.{material_name} must satisfy static permittivity "
                "> high-frequency permittivity > 0"
            )

    water_relaxation_time = require_finite_number(
        materials["liquid_water_25_c"].get("relaxation_time_s"),
        "materials.liquid_water_25_c.relaxation_time_s",
    )
    if water_relaxation_time <= 0:
        raise ValueError(
            "materials.liquid_water_25_c.relaxation_time_s must be positive"
        )

    ice_relaxation_frequency = require_finite_number(
        materials["ice_minus_10_c"].get("relaxation_frequency_hz"),
        "materials.ice_minus_10_c.relaxation_frequency_hz",
    )
    if ice_relaxation_frequency <= 0:
        raise ValueError(
            "materials.ice_minus_10_c.relaxation_frequency_hz must be positive"
        )

    frequency_values = []
    for name in (
        "industrial_ism",
        "microwave_oven_ism",
        "high_frequency_evaluation",
    ):
        frequency = require_finite_number(
            frequencies.get(name), f"frequencies_hz.{name}"
        )
        if frequency <= 0:
            raise ValueError(f"frequencies_hz.{name} must be positive")
        frequency_values.append(frequency)
    if len(set(frequency_values)) != len(frequency_values):
        raise ValueError("declared evaluation frequencies must be distinct")

    for name in ("dimensionless_absolute_tolerance", "relative_tolerance"):
        if require_finite_number(checks.get(name), f"checks.{name}") < 0:
            raise ValueError(f"checks.{name} must be nonnegative")


def evaluate_debye(
    frequency_hz: float,
    material: dict[str, float],
    speed_of_light_m_per_s: float,
) -> dict[str, float]:
    """Evaluate complex permittivity and 1/e power depth at one frequency."""

    angular_frequency = 2.0 * math.pi * frequency_hz
    relaxation_time = float(material["relaxation_time_s"])
    static = float(material["static_relative_permittivity"])
    high_frequency = float(material["high_frequency_relative_permittivity"])
    omega_tau = angular_frequency * relaxation_time
    # With fields proportional to exp(-i omega t), passive loss has positive
    # imaginary permittivity: epsilon*=epsilon'+i epsilon''.
    relative_permittivity = high_frequency + (static - high_frequency) / (
        1.0 - 1j * omega_tau
    )
    relative_permittivity_real = relative_permittivity.real
    relative_permittivity_loss = relative_permittivity.imag
    loss_tangent = relative_permittivity_loss / relative_permittivity_real
    loss_angle_degrees = math.degrees(math.atan(loss_tangent))
    refractive_index = cmath.sqrt(
        complex(relative_permittivity_real, relative_permittivity_loss)
    )
    attenuation_coefficient = (
        angular_frequency / speed_of_light_m_per_s
    ) * refractive_index.imag
    penetration_depth = 1.0 / (2.0 * attenuation_coefficient)

    return {
        "frequency_hz": frequency_hz,
        "angular_frequency_rad_per_s": angular_frequency,
        "omega_tau": omega_tau,
        "relative_permittivity_real": relative_permittivity_real,
        "relative_permittivity_loss": relative_permittivity_loss,
        "loss_tangent": loss_tangent,
        "loss_angle_degrees": loss_angle_degrees,
        "attenuation_coefficient_per_m": attenuation_coefficient,
        "power_penetration_depth_m": penetration_depth,
    }


def relative_error(actual: float, expected: float) -> float:
    """Return a scale-independent error for a nonzero expected value."""

    return abs(actual - expected) / abs(expected)


def build_results() -> dict[str, Any]:
    source = json.loads(INPUTS_PATH.read_text(encoding="utf-8"))
    validate_inputs(source)

    constants = source["constants"]
    conditions = source["conditions"]
    materials = source["materials"]
    frequencies = source["frequencies_hz"]
    criteria = source["checks"]
    water = materials["liquid_water_25_c"]
    ice_input = materials["ice_minus_10_c"]
    speed_of_light = float(constants["speed_of_light_m_per_s"])
    water_relaxation_time = float(water["relaxation_time_s"])
    ice_relaxation_time = 1.0 / (
        2.0 * math.pi * float(ice_input["relaxation_frequency_hz"])
    )
    ice = {**ice_input, "relaxation_time_s": ice_relaxation_time}
    oven_frequency = float(frequencies["microwave_oven_ism"])
    dielectric_loss_peak_frequency = 1.0 / (
        2.0 * math.pi * water_relaxation_time
    )

    water_rows = {
        "industrial_ism_915_mhz": evaluate_debye(
            float(frequencies["industrial_ism"]), water, speed_of_light
        ),
        "microwave_oven_245_ghz": evaluate_debye(
            oven_frequency, water, speed_of_light
        ),
        "dielectric_loss_factor_peak": evaluate_debye(
            dielectric_loss_peak_frequency, water, speed_of_light
        ),
        "high_frequency_60_ghz": evaluate_debye(
            float(frequencies["high_frequency_evaluation"]), water, speed_of_light
        ),
    }
    ice_oven = evaluate_debye(oven_frequency, ice, speed_of_light)
    independently_evaluated_water_oven = evaluate_debye(
        oven_frequency, water, speed_of_light
    )

    planck_constant = float(constants["planck_constant_j_s"])
    elementary_charge = float(constants["elementary_charge_c"])
    boltzmann_constant = float(constants["boltzmann_constant_j_per_k"])
    room_temperature = float(conditions["room_temperature_k"])
    photon_energy_j = planck_constant * oven_frequency
    thermal_energy_j = boltzmann_constant * room_temperature
    photon_to_thermal_ratio = photon_energy_j / thermal_energy_j
    thermal_to_photon_ratio = thermal_energy_j / photon_energy_j
    relaxation_time_ratio = ice_relaxation_time / water_relaxation_time

    peak_row = water_rows["dielectric_loss_factor_peak"]
    expected_peak_loss = (
        float(water["static_relative_permittivity"])
        - float(water["high_frequency_relative_permittivity"])
    ) / 2.0
    peak_condition_error = abs(peak_row["omega_tau"] - 1.0)
    peak_loss_relative_error = relative_error(
        peak_row["relative_permittivity_loss"], expected_peak_loss
    )
    water_oven_rows_match = (
        independently_evaluated_water_oven
        == water_rows["microwave_oven_245_ghz"]
    )

    evaluated_rows = [
        *((row, water) for row in water_rows.values()),
        (ice_oven, ice),
    ]
    all_rows_physical = all(
        row["frequency_hz"] > 0
        and float(material["high_frequency_relative_permittivity"])
        <= row["relative_permittivity_real"]
        <= float(material["static_relative_permittivity"])
        and row["relative_permittivity_loss"] > 0
        and row["loss_tangent"] > 0
        and 0 < row["loss_angle_degrees"] < 90
        and row["attenuation_coefficient_per_m"] > 0
        and row["power_penetration_depth_m"] > 0
        and all(math.isfinite(value) for value in row.values())
        for row, material in evaluated_rows
    )

    absolute_tolerance = float(criteria["dimensionless_absolute_tolerance"])
    relative_tolerance = float(criteria["relative_tolerance"])
    return {
        "schema_version": 1,
        "model": {
            "constants": constants,
            "conditions": conditions,
            "materials": materials,
            "evaluation_frequencies_hz": frequencies,
        },
        "derived_parameters": {
            "ice_minus_10_c": {
                "relaxation_time_s": ice_relaxation_time,
            }
        },
        "criteria": criteria,
        "liquid_water": {
            "dielectric_loss_factor_peak_frequency_hz": (
                dielectric_loss_peak_frequency
            ),
            "evaluations": water_rows,
        },
        "microwave_oven_comparison": {
            "frequency_hz": oven_frequency,
            "liquid_water": independently_evaluated_water_oven,
            "ice": ice_oven,
            "ice_to_water_relaxation_time_ratio": relaxation_time_ratio,
            "relaxation_time_order_difference": math.log10(relaxation_time_ratio),
        },
        "photon_thermal_comparison": {
            "frequency_hz": oven_frequency,
            "temperature_k": room_temperature,
            "photon_energy_j": photon_energy_j,
            "photon_energy_electronvolt": photon_energy_j / elementary_charge,
            "photon_energy_microelectronvolt": (
                photon_energy_j / elementary_charge
            ) * 1.0e6,
            "thermal_energy_j": thermal_energy_j,
            "thermal_energy_electronvolt": thermal_energy_j / elementary_charge,
            "thermal_energy_millielectronvolt": (
                thermal_energy_j / elementary_charge
            ) * 1.0e3,
            "photon_to_thermal_energy_ratio": photon_to_thermal_ratio,
            "thermal_to_photon_energy_ratio": thermal_to_photon_ratio,
            "photon_energy_orders_below_thermal": math.log10(
                thermal_to_photon_ratio
            ),
        },
        "consistency": {
            "water_dielectric_loss_peak_omega_tau_absolute_error": (
                peak_condition_error
            ),
            "water_dielectric_loss_peak_identity_relative_error": (
                peak_loss_relative_error
            ),
            "water_oven_rows_match": water_oven_rows_match,
            "all_evaluations_physical": all_rows_physical,
        },
        "checks": {
            "water_dielectric_loss_peak_condition_within_tolerance": (
                peak_condition_error <= absolute_tolerance
            ),
            "water_dielectric_loss_peak_identity_within_tolerance": (
                peak_loss_relative_error <= relative_tolerance
            ),
            "water_oven_rows_match": water_oven_rows_match,
            "all_evaluations_physical": all_rows_physical,
            "ice_relaxation_slower_than_water": (
                ice_relaxation_time > water_relaxation_time
            ),
        },
    }


def main() -> int:
    arguments = sys.argv[1:]
    if arguments not in ([], ["--check"]):
        print(f"usage: {Path(sys.argv[0]).name} [--check]", file=sys.stderr)
        return 2

    try:
        expected = json.dumps(
            build_results(), indent=2, sort_keys=True, allow_nan=False
        ) + "\n"
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"calculation failed: {error}", file=sys.stderr)
        return 1

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
