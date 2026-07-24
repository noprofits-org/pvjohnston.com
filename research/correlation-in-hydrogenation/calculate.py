#!/usr/bin/env python3
"""How much of a hydrogenation enthalpy is electron correlation, and is the
per-pi-bond correlation contribution transferable?

For each closed-shell species in ``inputs.json`` this:
  1. optimizes the geometry and runs harmonic frequencies at
     ``method.geometry_and_thermal`` (B3LYP/def2-TZVP), giving the geometry, the
     ideal-gas RRHO enthalpy correction H(298.15 K) - E_elec, and a
     true-minimum check;
  2. runs one CCSD(T)/cc-pVTZ single point at that geometry, whose SCF total is
     the Hartree-Fock baseline and whose total is the correlated energy.

Reaction quantities (Hess's law over stoichiometry), per reaction:
  dE_hf      = reaction energy at HF/cc-pVTZ
  dE_ccsdt   = reaction energy at CCSD(T)/cc-pVTZ
  dcorr      = dE_ccsdt - dE_hf         (correlation contribution)
  dthermal   = reaction sum of B3LYP enthalpy corrections
  dh_hf      = dE_hf    + dthermal
  dh_ccsdt   = dE_ccsdt + dthermal
Because the thermal correction is shared, the correlation contribution to the
enthalpy equals ``dcorr`` exactly.

Worked comparison:
    Compare |dcorr(acetylene->ethylene) - dcorr(ethylene->ethane)| with
    1 kcal/mol (4.184 kJ/mol). This shows whether one reaction-level increment
    describes both single-C-C-pi-bond hydrogenations at that practical scale;
    it does not partition correlation energy among bonds.

Usage:
    python3 research/correlation-in-hydrogenation/calculate.py          # full run -> results.json
    python3 research/correlation-in-hydrogenation/calculate.py --check  # no psi4; re-derive arithmetic
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS_PATH = HERE / "inputs.json"
RESULTS_PATH = HERE / "results.json"

# Only a mode more negative than this (cm^-1) counts as genuinely imaginary;
# psi4 reports near-zero translational/rotational residuals as tiny imaginaries.
IMAGINARY_FREQ_TOL_CM = -10.0


def load_inputs() -> dict:
    with INPUTS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def molecule_string(spec: dict) -> str:
    # Let psi4 detect the point group so the thermochemistry rotational
    # symmetry number is correct (sigma = 2 for N2, 3 for NH3, and so on).
    return "\n".join([f"{spec['charge']} {spec['multiplicity']}", *spec["zmatrix"], "units angstrom"])


def run_species(spec: dict, geom_method: str, energy_method: str, conv: dict,
                freeze_core: bool, temperature_k: float, pressure_pa: float) -> dict:
    """Optimize + frequencies at geom_method, then a CCSD(T) single point."""
    import psi4  # lazy: --check never needs psi4

    # Purge any scratch/QC-variable state left by the previous species. Driving
    # several molecules through one psi4 process without this corrupts the PSIO
    # scratch files ("Incorrect block end address").
    psi4.core.clean()
    psi4.core.clean_variables()

    mol = psi4.geometry(molecule_string(spec))
    psi4.set_options(
        {
            "e_convergence": conv["e_convergence"],
            "d_convergence": conv["d_convergence"],
            "geom_maxiter": conv["geom_maxiter"],
            "g_convergence": conv["g_convergence"],
            "freeze_core": freeze_core,
            "thermo__t": temperature_k,
            "thermo__p": pressure_pa,
        }
    )

    psi4.optimize(geom_method, molecule=mol)
    _, wfn = psi4.frequencies(geom_method, molecule=mol, return_wfn=True)
    freqs = [float(f) for f in wfn.frequencies().to_array()]
    imaginary = [f for f in freqs if f < IMAGINARY_FREQ_TOL_CM]

    # ENTHALPY CORRECTION = H(T) - E_elec at the geometry method.
    enthalpy_correction_hartree = float(psi4.variable("ENTHALPY CORRECTION"))

    # One CCSD(T) run yields both the HF baseline (SCF total) and CCSD(T) total.
    e_ccsdt = psi4.energy(energy_method, molecule=mol)
    e_hf = float(psi4.variable("SCF TOTAL ENERGY"))

    return {
        "hf_energy_hartree": e_hf,
        "ccsdt_energy_hartree": float(e_ccsdt),
        "enthalpy_correction_hartree": enthalpy_correction_hartree,
        "harmonic_frequencies_cm": freqs,
        "n_imaginary_modes": len(imaginary),
        "is_true_minimum": len(imaginary) == 0,
    }


def hess(products: dict, reactants: dict, per_species: dict, key: str) -> float:
    """Sum(products) - Sum(reactants) of per_species[..][key], stoichiometry-weighted."""
    total = 0.0
    for name, n in products.items():
        total += n * per_species[name][key]
    for name, n in reactants.items():
        total -= n * per_species[name][key]
    return total


def build_reactions(inputs: dict, per_species: dict) -> list:
    h2kj = inputs["constants"]["hartree_to_kj_per_mol"]
    reactions = []
    for rxn in inputs["reactions"]:
        p, r = rxn["products"], rxn["reactants"]
        de_hf = hess(p, r, per_species, "hf_energy_hartree") * h2kj
        de_ccsdt = hess(p, r, per_species, "ccsdt_energy_hartree") * h2kj
        dthermal = hess(p, r, per_species, "enthalpy_correction_hartree") * h2kj
        dcorr = de_ccsdt - de_hf
        dh_ccsdt = de_ccsdt + dthermal
        dh_hf = de_hf + dthermal
        reactions.append(
            {
                "slug": rxn["slug"],
                "equation": rxn["equation"],
                "pi_bonds_hydrogenated": rxn["pi_bonds_hydrogenated"],
                "bond_class": rxn["bond_class"],
                "dh_hf_kj": dh_hf,
                "dh_ccsdt_kj": dh_ccsdt,
                "correlation_content_kj": dcorr,
                "correlation_fraction": dcorr / dh_ccsdt if dh_ccsdt != 0 else float("nan"),
                "correlation_per_pi_bond_kj": dcorr / rxn["pi_bonds_hydrogenated"],
            }
        )
    return reactions


def summarize(inputs: dict, reactions: list, all_true_minima: bool) -> dict:
    threshold_kj = (
        inputs["constants"]["chemical_accuracy_kcal_per_mol"]
        * inputs["constants"]["kcal_to_kj"]
    )
    by_slug = {r["slug"]: r for r in reactions}
    comparison = inputs["transferability_comparison"]
    corr_a = by_slug[comparison["rung_a"]]["correlation_content_kj"]
    corr_b = by_slug[comparison["rung_b"]]["correlation_content_kj"]
    gap = abs(corr_a - corr_b)
    return {
        "temperature_k": inputs["conditions"]["temperature_k"],
        "chemical_accuracy_threshold_kj": threshold_kj,
        "reaction_count": len(reactions),
        "mean_abs_correlation_content_kj": sum(abs(r["correlation_content_kj"]) for r in reactions) / len(reactions),
        "max_abs_correlation_content_kj": max(abs(r["correlation_content_kj"]) for r in reactions),
        "pi_bond_correlation_transferability_gap_kj": gap,
        "cc_pi_rungs_within_chemical_accuracy": gap <= threshold_kj,
        "all_species_true_minima": all_true_minima,
    }


def assemble(inputs: dict, per_species: dict) -> dict:
    reactions = build_reactions(inputs, per_species)
    all_true_minima = all(s["is_true_minimum"] for s in per_species.values())
    return {
        "method": inputs["method"],
        "conditions": inputs["conditions"],
        "species": per_species,
        "reactions": reactions,
        "summary": summarize(inputs, reactions, all_true_minima),
    }


def full_run() -> dict:
    import psi4

    inputs = load_inputs()
    m = inputs["method"]

    # Isolate scratch to this experiment so nothing collides with other psi4
    # runs and cleanup is total.
    scratch = HERE / "_scratch"
    scratch.mkdir(exist_ok=True)
    psi4.core.IOManager.shared_object().set_default_path(str(scratch))

    psi4.core.set_output_file(str(HERE / "psi4.out"), False)
    psi4.core.set_num_threads(1)
    psi4.set_memory("2 GB")

    # Build sequentially (not a comprehension) so a clean() runs between species.
    per_species = {}
    for name, spec in inputs["species"].items():
        per_species[name] = run_species(
            spec,
            m["geometry_and_thermal"],
            m["electronic_energy"],
            inputs["convergence"],
            m["freeze_core"],
            inputs["conditions"]["temperature_k"],
            inputs["conditions"]["pressure_atm"] * inputs["constants"]["atm_to_pa"],
        )
    psi4.core.clean()
    return assemble(inputs, per_species)


def check() -> int:
    """Re-derive all reaction arithmetic from committed results.json, no psi4."""
    if not RESULTS_PATH.exists():
        print("results.json not found; run without --check first", file=sys.stderr)
        return 1

    inputs = load_inputs()
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    rebuilt = assemble(inputs, results["species"])

    ok = True

    def close(a, b):
        return math.isclose(a, b, rel_tol=0, abs_tol=1e-6)

    for committed, fresh in zip(results["reactions"], rebuilt["reactions"]):
        for field in ("dh_hf_kj", "dh_ccsdt_kj", "correlation_content_kj",
                      "correlation_fraction", "correlation_per_pi_bond_kj"):
            cv, fv = committed[field], fresh[field]
            if isinstance(fv, float) and math.isnan(fv):
                continue
            if not close(cv, fv):
                print(f"mismatch {committed['slug']}.{field}: {cv} != {fv}", file=sys.stderr)
                ok = False
    for field, value in rebuilt["summary"].items():
        cv = results["summary"][field]
        if isinstance(value, float):
            if not close(cv, value):
                print(f"summary mismatch {field}: {cv} != {value}", file=sys.stderr)
                ok = False
        elif cv != value:
            print(f"summary mismatch {field}: {cv} != {value}", file=sys.stderr)
            ok = False

    print("check: OK" if ok else "check: FAILED")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="re-derive arithmetic from results.json without running psi4")
    args = parser.parse_args()
    if args.check:
        return check()
    results = full_run()
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {RESULTS_PATH.relative_to(HERE.parents[1])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
