#!/usr/bin/env python3
"""Analysis for the CEPB increment-spread experiment.

Arm A is arithmetic on the source's published values (inputs.json). Two
statistics are produced, in the order the preregistration fixes them:

  primary   - the spread across three published contrasts that share the
              identical bond-count swap C=C -> C-C + 2 C-H, in which every
              other bond class cancels exactly;
  secondary - the raw effective-increment spread, which attributes a whole
              molecule's CEPB residual to its C=C bonds and is reported as
              descriptive only (see Amendment 1).

Arm B reads the committed Psi4 run records and forms the six pairwise
correlation-energy differences among the C4H8 positional isomers, which CEPB
predicts are all exactly zero.
"""

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS_PATH = HERE / "inputs.json"
RUNS = HERE / "runs"
RESULTS_PATH = HERE / "results.json"

# The three published pairs differing by exactly one C=C -> C-C + 2 C-H swap.
CONTRASTS = (
    ("ethene", "ethane"),
    ("1,4-cyclohexadiene", "cyclohexene"),
    ("cyclohexene", "cyclohexane"),
)
C4H8 = ("1-butene", "cis-2-butene", "trans-2-butene", "isobutene")


def molecule_table(inputs: dict) -> dict:
    """Every molecule with a published correlation energy, from all sections."""
    table = dict(inputs["molecules"])
    table.update(inputs["saturated_reference"])
    table.update(inputs["aromatic_reference"])
    return table


def effective_increment(record: dict, increments: dict, level: str) -> float:
    counts = record.get("bond_counts") or record["bond_counts_kekule"]
    energy = record["correlation_energy_hartree"][level]
    residual = (
        energy
        - counts["c_h"] * increments["c_h"][level]
        - counts["c_c_single"] * increments["c_c_single"][level]
    )
    return residual / counts["c_c_double"]


def arm_a(inputs: dict) -> dict:
    kcal = inputs["constants"]["hartree_per_kcal_mol"]
    increments = inputs["increments_hartree"]
    molecules = molecule_table(inputs)
    out = {}

    for level in inputs["levels"]:
        # Primary: the bond-count-cancelling contrasts.
        predicted = (
            increments["c_c_single"][level]
            + 2.0 * increments["c_h"][level]
            - increments["c_c_double"][level]
        )
        contrasts = {}
        for start, end in CONTRASTS:
            measured = (
                molecules[end]["correlation_energy_hartree"][level]
                - molecules[start]["correlation_energy_hartree"][level]
            )
            contrasts[f"{start} -> {end}"] = {
                "measured_hartree": measured,
                "measured_kcal_per_mol": measured * kcal,
                "deviation_from_cepb_kcal_mol": (measured - predicted) * kcal,
            }
        values = [c["measured_kcal_per_mol"] for c in contrasts.values()]
        contrast_spread = max(values) - min(values)

        # Secondary: the raw effective increment (descriptive only).
        effective = {
            name: effective_increment(record, increments, level)
            for name, record in inputs["molecules"].items()
        }
        raw_values = list(effective.values())
        raw_spread = (max(raw_values) - min(raw_values)) * kcal

        out[level] = {
            "cepb_predicted_contrast_hartree": predicted,
            "cepb_predicted_contrast_kcal_per_mol": predicted * kcal,
            "contrasts": contrasts,
            "primary_contrast_spread_kcal_per_mol": contrast_spread,
            "primary_gate_passed": contrast_spread
            <= inputs["decision"]["spread_threshold_kcal_mol"],
            "secondary_effective_increments_hartree": effective,
            "secondary_effective_increment_spread_kcal_per_mol": raw_spread,
            "benzene_effective_increment_hartree": effective_increment(
                inputs["aromatic_reference"]["benzene"], increments, level
            ),
        }
    return out


def arm_b(inputs: dict) -> dict:
    kcal = inputs["constants"]["hartree_per_kcal_mol"]
    out = {}
    for basis_dir in sorted({p.parent.name for p in RUNS.glob("*/*/result.json")}):
        pass
    bases = sorted({p.name for p in RUNS.glob("*/*") if (p / "result.json").is_file()})
    for basis in bases:
        records = {}
        for name in C4H8:
            path = RUNS / name / basis / "result.json"
            if not path.is_file():
                break
            records[name] = json.loads(path.read_text(encoding="utf-8"))
        if len(records) != len(C4H8):
            continue
        pairs = {}
        for first, second in combinations(C4H8, 2):
            difference = (
                records[second]["ccsd_t_correlation_energy_hartree"]
                - records[first]["ccsd_t_correlation_energy_hartree"]
            )
            pairs[f"{first} vs {second}"] = {
                "difference_hartree": difference,
                "difference_kcal_per_mol": difference * kcal,
            }
        magnitudes = [abs(p["difference_kcal_per_mol"]) for p in pairs.values()]
        t1 = {name: records[name]["t1_diagnostic"] for name in C4H8}
        out[basis] = {
            "correlation_energies_hartree": {
                name: records[name]["ccsd_t_correlation_energy_hartree"] for name in C4H8
            },
            "pairwise_differences": pairs,
            "max_absolute_difference_kcal_per_mol": max(magnitudes),
            "cepb_predicted_difference_kcal_per_mol": 0.0,
            "t1_diagnostics": t1,
            "max_t1_diagnostic": max(t1.values()),
            "t1_gate_passed": max(t1.values()) <= 0.02,
        }
    return out


def verdicts(inputs: dict, a: dict, b: dict) -> dict:
    threshold = inputs["decision"]["spread_threshold_kcal_mol"]

    a_exceeds = [
        level for level, data in a.items()
        if data["primary_contrast_spread_kcal_per_mol"] > threshold
    ]
    if not a:
        verdict_a, reason_a = "inconclusive", "no basis level produced a contrast set"
    elif len(a_exceeds) == len(a):
        verdict_a = "supported"
        reason_a = "the contrast spread exceeds the registered threshold at every level"
    elif not a_exceeds:
        verdict_a = "falsified"
        reason_a = "the contrast spread is within the registered threshold at every level"
    else:
        verdict_a = "inconclusive"
        reason_a = f"the contrast spread exceeds the threshold only at {', '.join(a_exceeds)}"

    if len(b) < 2:
        verdict_b = "inconclusive"
        reason_b = "the registered two-basis sensitivity check is not complete"
    elif not all(data["t1_gate_passed"] for data in b.values()):
        verdict_b = "inconclusive"
        reason_b = "a T1 diagnostic exceeded the registered 0.02 fidelity gate"
    else:
        bases = sorted(b)
        signs_agree = all(
            (b[bases[0]]["pairwise_differences"][pair]["difference_hartree"] > 0)
            == (b[basis]["pairwise_differences"][pair]["difference_hartree"] > 0)
            for basis in bases[1:]
            for pair in b[bases[0]]["pairwise_differences"]
        )
        exceeds = {
            basis: data["max_absolute_difference_kcal_per_mol"] > threshold
            for basis, data in b.items()
        }
        if not signs_agree:
            verdict_b = "inconclusive"
            reason_b = "a pairwise difference changed sign between the two bases"
        elif all(exceeds.values()):
            verdict_b = "supported"
            reason_b = (
                "at least one pairwise difference exceeds the registered threshold "
                "at every basis, with all signs in agreement"
            )
        elif not any(exceeds.values()):
            verdict_b = "falsified"
            reason_b = "every pairwise difference is within the registered threshold at both bases"
        else:
            verdict_b = "inconclusive"
            reason_b = "the two bases disagree about whether the threshold is crossed"

    return {
        "arm_a": {"value": verdict_a, "reason": reason_a},
        "arm_b": {"value": verdict_b, "reason": reason_b},
    }


def build(inputs: dict) -> dict:
    a = arm_a(inputs)
    b = arm_b(inputs)
    return {
        "schema_version": 1,
        "experiment": inputs["experiment"],
        "source": inputs["source"],
        "decision": inputs["decision"],
        "arm_a": a,
        "arm_b": b,
        "verdicts": verdicts(inputs, a, b),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    inputs = json.loads(INPUTS_PATH.read_text(encoding="utf-8"))
    serialized = json.dumps(build(inputs), indent=2) + "\n"

    if args.check:
        if not RESULTS_PATH.is_file():
            print("results.json is missing", file=sys.stderr)
            return 1
        if RESULTS_PATH.read_text(encoding="utf-8") != serialized:
            print("results.json is stale", file=sys.stderr)
            return 1
        print("cepb-increment-spread: results.json is internally consistent")
        return 0

    RESULTS_PATH.write_text(serialized, encoding="utf-8")
    print(f"wrote {RESULTS_PATH.relative_to(HERE.parent.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
