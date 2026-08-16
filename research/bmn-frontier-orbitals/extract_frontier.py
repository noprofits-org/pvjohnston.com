#!/usr/bin/env python
"""
Frontier-orbital energies (HOMO-1, HOMO, LUMO, LUMO+1) for the BMN series.

This experiment directory holds copied canonical results from the
donor-strength-ladder run of 2026-08-14 (see README.md for the provenance
chain). The per-state JSON records commit excitation energies and oscillator
strengths, and the copied orbital_gaps.json commits the occupied frontier
energies -- but no committed artifact records the VIRTUAL orbital energies,
because the original experiment never needed them. This script closes that
gap the same way orbital_gaps.py closed its own: Psi4 prints every orbital
energy to its output log, the logs are not committed (large, regenerable,
absolute scratch paths -- see the original experiment's .gitignore), so we
parse the logs once and commit the extracted values here as
results/frontier_orbitals.json.

Cross-checks, all fatal on failure:
  * exactly one 'Doubly Occupied:' block per log;
  * occupied and virtual energies each ascending, so HOMO and LUMO are
    identified positionally rather than assumed;
  * occupied count equals the wavefunction's own n_occupied from the states
    record, and occupied + virtual equals its n_mo;
  * HOMO and HOMO-1 agree with the independently committed orbital_gaps.json
    to 1e-3 eV, tying this extraction to the record the original experiment
    published.

A reader who re-runs the original pipeline regenerates the logs and can
re-derive every number here; a reader who only clones the repository gets
this committed JSON, the parse code, and the sha256 of each log it read.

Usage: extract_frontier.py --logs-dir PATH [--force]
"""
import os, re, json, glob, argparse, datetime, hashlib, platform

HERE = os.path.dirname(os.path.abspath(__file__))
HA2EV = 27.211386245988


def parse_orbital_energies(log_path):
    """(occupied, virtual) orbital energies in hartree, each ascending."""
    with open(log_path) as fh:
        text = fh.read()
    blocks = text.split("Doubly Occupied:")
    if len(blocks) != 2:
        raise ValueError(f"{log_path}: expected exactly 1 'Doubly Occupied:' "
                         f"block, found {len(blocks) - 1}")
    occ_seg, _, rest = blocks[1].partition("Virtual:")
    if not rest:
        raise ValueError(f"{log_path}: no 'Virtual:' block after the occupied one")
    vir_seg = rest.split("Final Occupation")[0]
    grab = lambda seg: [float(m.group(1))
                        for m in re.finditer(r"\d+A\s+(-?\d+\.\d+)", seg)]
    occupied, virtual = grab(occ_seg), grab(vir_seg)
    for name, seq in (("occupied", occupied), ("virtual", virtual)):
        if seq != sorted(seq):
            raise ValueError(f"{log_path}: {name} energies are not ascending; "
                             f"the frontier cannot be identified positionally")
    return occupied, virtual


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--logs-dir", required=True,
                   help="directory holding the canonical run's td_*.out logs")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    out_path = os.path.join(HERE, "results", "frontier_orbitals.json")
    if os.path.exists(out_path) and not args.force:
        raise SystemExit(f"{out_path} exists; pass --force to overwrite")

    with open(os.path.join(HERE, "results", "orbital_gaps.json")) as fh:
        committed = {(r["molecule_slug"], r["functional"]): r
                     for r in json.load(fh)["molecules"]}

    records = []
    for states_path in sorted(glob.glob(os.path.join(HERE, "results", "states_*.json"))):
        with open(states_path) as fh:
            run = json.load(fh)
        # Derive the log tag from the states filename so that non-default
        # suffixes (_tda, _sN) are preserved and paired with the correct log.
        tag = os.path.basename(states_path)[len("states_"):-len(".json")]
        log_path = os.path.join(args.logs_dir, f"td_{tag}.out")
        if not os.path.exists(log_path):
            raise SystemExit(f"missing log for {tag}: {log_path}")

        occupied, virtual = parse_orbital_energies(log_path)
        if len(occupied) != run["n_occupied"]:
            raise SystemExit(f"{log_path}: parsed {len(occupied)} occupied "
                             f"orbitals but the wavefunction reports "
                             f"{run['n_occupied']}")
        if len(occupied) + len(virtual) != run["n_mo"]:
            raise SystemExit(f"{log_path}: parsed {len(occupied)} + "
                             f"{len(virtual)} orbitals but the wavefunction "
                             f"reports n_mo = {run['n_mo']}")

        homo_1, homo = (e * HA2EV for e in occupied[-2:])
        lumo, lumo_1 = (e * HA2EV for e in virtual[:2])
        ref = committed[(run["molecule_slug"], run["functional"])]
        for name, ours, theirs in (("HOMO", homo, ref["homo_eV"]),
                                   ("HOMO-1", homo_1, ref["homo_minus_1_eV"])):
            if abs(ours - theirs) > 1e-3:
                raise SystemExit(f"{log_path}: {name} = {ours:.4f} eV disagrees "
                                 f"with orbital_gaps.json ({theirs} eV)")

        with open(log_path, "rb") as fh:
            log_sha = hashlib.sha256(fh.read()).hexdigest()
        records.append({
            "molecule_slug": run["molecule_slug"],
            "molecule": run["molecule"],
            "substituent": run["substituent"],
            "sigma_p_plus": run["sigma_p_plus"],
            "functional": run["functional"],
            "basis": run["basis"],
            "n_occupied": run["n_occupied"],
            "homo_minus_1_eV": round(homo_1, 4),
            "homo_eV": round(homo, 4),
            "lumo_eV": round(lumo, 4),
            "lumo_plus_1_eV": round(lumo_1, 4),
            "gap_eV": round(lumo - homo, 4),
            "parsed_from_log": f"td_{tag}.out",
            "log_sha256": log_sha,
        })

    out = {
        "note": ("Frontier orbital energies parsed from the Psi4 output logs "
                 "of the donor-strength-ladder canonical run (2026-08-14). "
                 "The logs are NOT committed; this file is the committed "
                 "record of what they contained, with the sha256 of each log "
                 "read. HOMO and HOMO-1 are cross-checked against the "
                 "independently committed orbital_gaps.json; the virtual "
                 "energies (LUMO, LUMO+1) exist in no other committed "
                 "artifact, which is why this extraction exists."),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                                 .isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "molecules": records,
    }
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")

    for r in records:
        print("[%-9s %-9s] HOMO-1 %8.4f  HOMO %8.4f  LUMO %8.4f  "
              "LUMO+1 %8.4f  gap %.4f eV" % (
                  r["functional"], r["molecule_slug"], r["homo_minus_1_eV"],
                  r["homo_eV"], r["lumo_eV"], r["lumo_plus_1_eV"], r["gap_eV"]))
    print(f"wrote {os.path.relpath(out_path, HERE)}")


if __name__ == "__main__":
    main()
