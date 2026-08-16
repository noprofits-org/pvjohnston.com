#!/usr/bin/env python
"""
Why the second transition sits where it does: the HOMO/HOMO-1 splitting.

At the H and F rungs the next state up is HOMO-1 -> LUMO under CAM-B3LYP, the
adjudicating functional (73-94% of the dominant amplitude; under B3LYP
dcdhf-h's neighbour is instead HOMO-2 -> LUMO dominant), while the first
bright state is HOMO -> LUMO. Where both
terminate on the SAME orbital, the spacing between them is largely set by how
far HOMO-1 lies below HOMO. That makes eps(HOMO) - eps(HOMO-1) the mechanistic
quantity behind the isolation gap, and it is a ground-state SCF number that
needs no excited-state threshold at all. The mapping is partial: at NH2 and
NMe2 the second state's dominant component is HOMO -> LUMO+1 (57-62% under
CAM-B3LYP), so the two transitions no longer share the LUMO there.

PROVENANCE, stated plainly because it is weaker than the rest of this
experiment. Psi4 prints orbital energies to its output log, and this
repository does not commit those logs -- they are large, regenerable, and they
embed absolute scratch paths (see .gitignore). So this script PARSES THE LOGS
produced by the canonical run and writes the extracted values into
results/orbital_gaps.json, which is committed. A reader who re-runs the
pipeline regenerates the logs and can re-derive every number here; a reader who
only clones the repository gets the committed JSON and this explanation, not
the ability to re-derive it independently.

That is the same pattern the prior experiment used for `tdscf_effective`,
which is also parsed from the solver's own printout rather than asserted. The
difference is that this extraction happens after the run rather than during
it, which is why it is a separate script and a separate file rather than a
field inside the states records. Nothing here feeds a preregistered criterion.

Usage: orbital_gaps.py [--force]
"""
import os, re, json, glob, argparse, datetime, platform

HERE = os.path.dirname(os.path.abspath(__file__))
HA2EV = 27.211386245988


def parse_occupied_energies(log_path):
    """Occupied orbital energies in hartree, ascending, from the SCF printout.

    Psi4 prints exactly one 'Doubly Occupied:' block per job, after the SCF has
    converged. The caller checks the count against the wavefunction's own
    n_occupied, so a parse that silently grabbed the wrong block or dropped a
    line fails loudly instead of shifting which orbital is called the HOMO.
    """
    with open(log_path) as fh:
        text = fh.read()
    blocks = text.split("Doubly Occupied:")
    if len(blocks) != 2:
        raise ValueError(f"{log_path}: expected exactly 1 'Doubly Occupied:' "
                         f"block, found {len(blocks) - 1}")
    segment = blocks[1].split("Virtual:")[0]
    energies = [float(m.group(1))
                for m in re.finditer(r"\d+A\s+(-?\d+\.\d+)", segment)]
    if energies != sorted(energies):
        raise ValueError(f"{log_path}: occupied energies are not ascending; "
                         f"the HOMO cannot be identified as the last entry")
    return energies


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    out_path = os.path.join(HERE, "results", "orbital_gaps.json")
    if os.path.exists(out_path) and not args.force:
        raise SystemExit(f"{out_path} exists; pass --force to overwrite")

    records, missing = [], []
    for states_path in sorted(glob.glob(os.path.join(HERE, "results", "states_*.json"))):
        with open(states_path) as fh:
            run = json.load(fh)
        # The states filename encodes the exact tag run_tddft.py used for both
        # the output JSON and the log, including any non-default suffixes such
        # as _tda or _sN. Derive the log name from the filename rather than
        # reconstructing the tag from the record fields, which silently drops
        # those suffixes.
        tag = os.path.basename(states_path)[len("states_"):-len(".json")]
        log_path = os.path.join(HERE, "logs", f"td_{tag}.out")
        if not os.path.exists(log_path):
            missing.append(os.path.relpath(log_path, HERE))
            continue

        occupied = parse_occupied_energies(log_path)
        nocc = run["n_occupied"]
        if len(occupied) != nocc:
            raise SystemExit(f"{log_path}: parsed {len(occupied)} occupied "
                             f"orbitals but the wavefunction reports {nocc}")
        homo, homo_1 = occupied[-1], occupied[-2]

        states = sorted(run["states"], key=lambda s: (s["energy_eV"], s["state"]))
        spacing = (states[1]["energy_eV"] - states[0]["energy_eV"]
                   if len(states) > 1 else None)
        split_ev = (homo - homo_1) * HA2EV
        records.append({
            "molecule_slug": run["molecule_slug"],
            "molecule": run["molecule"],
            "scaffold": run["scaffold"],
            "acceptor": run["acceptor"],
            "acceptor_strength": run["acceptor_strength"],
            "functional": run["functional"],
            "n_occupied": nocc,
            "homo_eV": round(homo * HA2EV, 4),
            "homo_minus_1_eV": round(homo_1 * HA2EV, 4),
            "homo_homo1_splitting_eV": round(split_ev, 4),
            "s1_s2_spacing_eV": round(spacing, 4) if spacing is not None else None,
            # How much of the orbital splitting survives into the excitation
            # spacing. Roughly constant within a scaffold means the spacing is
            # tracking the splitting; a different value on another scaffold
            # means something beyond the splitting is also acting.
            "spacing_over_splitting": (round(spacing / split_ev, 4)
                                       if spacing is not None and split_ev else None),
            "parsed_from_log": os.path.relpath(log_path, HERE),
        })

    if not records:
        raise SystemExit(
            "no Psi4 logs found. This script reads orbital energies out of "
            "logs/, which are NOT committed (regenerable, and they embed "
            "absolute scratch paths). Re-run the pipeline to regenerate them, "
            "or read the committed results/orbital_gaps.json instead.")

    out = {
        "note": ("HOMO and HOMO-1 energies parsed from the Psi4 output logs of "
                 "the canonical run. The logs are NOT committed (see "
                 ".gitignore); this file is the committed record of what they "
                 "contained. Re-running the pipeline regenerates the logs and "
                 "allows every number here to be re-derived. Nothing here feeds "
                 "a preregistered criterion."),
        "why_this_quantity": ("At the H and F rungs, under CAM-B3LYP, the second "
                              "state is HOMO-1 -> LUMO and the first is "
                              "HOMO -> LUMO, so "
                              "both terminate on the same orbital and their "
                              "spacing is largely set by the HOMO/HOMO-1 "
                              "splitting. At NH2 and NMe2 (again under "
                              "CAM-B3LYP) the second state's dominant component "
                              "is HOMO -> LUMO+1, so the "
                              "mapping is partial there. Unlike the isolation "
                              "gap, this is a ground-state quantity with no "
                              "brightness threshold in it."),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                                 .isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "logs_missing": missing,
        "molecules": records,
    }
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)

    for r in sorted(records, key=lambda r: (r["functional"], r["scaffold"],
                                            r["acceptor_strength"])):
        print("[%-10s %-9s] HOMO %8.4f  HOMO-1 %8.4f  split %.3f eV  "
              "S1-S2 %.3f eV  ratio %s" % (
                  r["functional"], r["molecule_slug"], r["homo_eV"],
                  r["homo_minus_1_eV"], r["homo_homo1_splitting_eV"],
                  r["s1_s2_spacing_eV"] or 0.0, r["spacing_over_splitting"]))
    if missing:
        print(f"\n{len(missing)} log(s) absent, skipped: {missing[0]} ...")
    print(f"wrote {os.path.relpath(out_path, HERE)}")


if __name__ == "__main__":
    main()
