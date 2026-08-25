#!/usr/bin/env python3
"""Sequential rematch of the four haloacetate ions.

Psi4 1.11 parser for rematch optimizations: Cartesian tables, MBIS and
Löwdin charges, optking convergence, and wall time. This script is the
canonical rematch driver. It is not a CI rerun.

Binding q(O) is the arithmetic mean of the two carboxylate oxygen
charges (atoms 1 and 2, 0-based). q(COO) is the sum of atoms 0+1+2.
The same aggregates are written for Löwdin. Acetate and CClF2 MBIS
columns are left blank in the public summary; Löwdin is written for
all four ions. Δ(C–X) is out-of-plane minus in-plane C–X and is
blank for acetate (no C–X) and CClF2 (mixed halogen).

Raw output.dat / timer.dat / stdout.log / done.json stay local and
are not publication files. Set PSI4 to the executable; it defaults
to "psi4".
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PSI4 = os.environ.get("PSI4", "psi4")
ROOT = Path(__file__).resolve().parent.parent
ORDER = ["m0_acetate", "m1_cf3", "m2_cclf2", "m3_ccl3"]
NATOM = 7

SHORT = {
    "m0_acetate": "acetate",
    "m1_cf3": "cf3",
    "m2_cclf2": "cclf2",
    "m3_ccl3": "ccl3",
}
FORMULA = {
    "m0_acetate": "CH3COO-",
    "m1_cf3": "CF3COO-",
    "m2_cclf2": "CClF2COO-",
    "m3_ccl3": "CCl3COO-",
}
# Public projection blanks MBIS for these ions (Löwdin stays).
MBIS_BLANK = {"m0_acetate", "m2_cclf2"}
# Δ(C–X) is undefined when the three CX3 substituents are not one element.
DELTA_BLANK = {"m0_acetate", "m2_cclf2"}

CART_HEADER_RE = re.compile(
    r"Center\s+X\s+Y\s+Z\s+Mass\s*\n"
    r"\s*-+(?:\s+-+){3,}\s*\n"
    r"((?:[ \t]+\S+[ \t]+[+\-]?\d+\.\d+[ \t]+[+\-]?\d+\.\d+[ \t]+[+\-]?\d+\.\d+[ \t]+[+\-]?\d+\.\d+\s*\n)+)",
)
ATOM_LINE_RE = re.compile(
    r"^\s+(\S+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s*$"
)
LOWDIN_RE = re.compile(
    r"Lowdin Charges:\s*\(a\.u\.\)\s*\n"
    r"[^\n]*Center[^\n]*Total[^\n]*\n"
    r"((?:[ \t]+\d+[ \t]+\S+[ \t]+[+\-]?\d+\.\d+[ \t]+[+\-]?\d+\.\d+[ \t]+[+\-]?\d+\.\d+[ \t]+[+\-]?\d+\.\d+\s*\n)+)",
    re.I,
)
MBIS_RE = re.compile(
    r"(?<!Valence )MBIS Charges:\s*\(a\.u\.\)\s*\n"
    r"[^\n]*Center[^\n]*Charge[^\n]*\n"
    r"((?:[ \t]+\d+[ \t]+\S+[ \t]+\d+[ \t]+[+\-]?\d+\.\d+[ \t]+[+\-]?\d+\.\d+\s*\n)+)",
    re.I,
)
ENERGY_RE = re.compile(r"Total Energy =\s+([+\-]?\d+\.\d+)")
STEP_RE = re.compile(
    r"^\s+(\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+(?:[eE][+\-]?\d+)?)\s+\*?\s+"
    r"([+\-]?\d+\.\d+(?:[eE][+\-]?\d+)?)",
    re.M,
)
WALL_RE = re.compile(r"Psi4 wall time for execution:\s+(\d+):(\d+):(\d+\.?\d*)")
OPTKING_TRUE = "Convergence check returned True"
EXIT_OK = "Psi4 exiting successfully"

LOWDIN_LINE_RE = re.compile(
    r"^\s+(\d+)\s+(\S+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s+"
    r"([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s*$"
)
MBIS_LINE_RE = re.compile(
    r"^\s+(\d+)\s+(\S+)\s+(\d+)\s+([+\-]?\d+\.\d+)\s+([+\-]?\d+\.\d+)\s*$"
)


def canon_el(sym: str) -> str:
    """Canonical element symbol from a Psi4 center label."""
    letters = "".join(ch for ch in str(sym) if ch.isalpha())
    if not letters:
        raise ValueError(f"not an element symbol: {sym!r}")
    return letters[0].upper() + letters[1:].lower()


def _vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(a):
    return math.sqrt(_dot(a, a))


def _dist(a, b):
    return _norm(_vec_sub(a, b))


def dihedral_deg(p1, p2, p3, p4):
    """Signed dihedral of p1-p2-p3-p4 in degrees."""
    b1 = _vec_sub(p2, p1)
    b2 = _vec_sub(p3, p2)
    b3 = _vec_sub(p4, p3)
    n1 = _cross(b1, b2)
    n2 = _cross(b2, b3)
    n1n = _norm(n1)
    n2n = _norm(n2)
    b2n = _norm(b2)
    if n1n == 0.0 or n2n == 0.0 or b2n == 0.0:
        return float("nan")
    n1u = (n1[0] / n1n, n1[1] / n1n, n1[2] / n1n)
    n2u = (n2[0] / n2n, n2[1] / n2n, n2[2] / n2n)
    b2u = (b2[0] / b2n, b2[1] / b2n, b2[2] / b2n)
    x = _dot(n1u, n2u)
    y = _dot(_cross(n1u, n2u), b2u)
    x = max(-1.0, min(1.0, x))
    return math.degrees(math.atan2(y, x))


def parse_walltime_s(text: str) -> float | None:
    match = WALL_RE.search(text)
    if not match:
        return None
    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    return hours * 3600.0 + minutes * 60.0 + seconds


def parse_cartesian_tables(text: str) -> list[list[tuple[str, float, float, float, float]]]:
    tables = []
    for block in CART_HEADER_RE.finditer(text):
        atoms = []
        for line in block.group(1).splitlines():
            parsed = ATOM_LINE_RE.match(line)
            if not parsed:
                continue
            element = canon_el(parsed.group(1))
            x = float(parsed.group(2))
            y = float(parsed.group(3))
            z = float(parsed.group(4))
            mass = float(parsed.group(5))
            atoms.append((element, x, y, z, mass))
        if len(atoms) == NATOM:
            tables.append(atoms)
    return tables


def parse_charge_block(block: str, kind: str) -> list[tuple[str, float]]:
    """Return [(element, charge), ...] in file order."""
    rows = []
    pattern = LOWDIN_LINE_RE if kind == "lowdin" else MBIS_LINE_RE
    for line in block.splitlines():
        parsed = pattern.match(line)
        if not parsed:
            continue
        if kind == "lowdin":
            element = canon_el(parsed.group(2))
            charge = float(parsed.group(6))
        else:
            element = canon_el(parsed.group(2))
            charge = float(parsed.group(4))
        rows.append((element, charge))
    return rows


def parse_outputs(output_text: str) -> dict:
    tables = parse_cartesian_tables(output_text)
    energies = [float(x) for x in ENERGY_RE.findall(output_text)]
    lowdin_blocks = [m.group(1) for m in LOWDIN_RE.finditer(output_text)]
    mbis_blocks = [m.group(1) for m in MBIS_RE.finditer(output_text)]
    steps = STEP_RE.findall(output_text)
    return {
        "tables": tables,
        "energy": energies[-1] if energies else None,
        "lowdin": parse_charge_block(lowdin_blocks[-1], "lowdin") if lowdin_blocks else [],
        "mbis": parse_charge_block(mbis_blocks[-1], "mbis") if mbis_blocks else [],
        "n_opt_steps": len(steps),
        "optking": OPTKING_TRUE in output_text,
        "exit_ok": EXIT_OK in output_text,
        "walltime_s": parse_walltime_s(output_text),
    }


def derived(ion: str, parsed: dict) -> dict:
    """Geometry and charge aggregates from the last Cartesian / charge tables."""
    if not parsed["tables"]:
        raise ValueError(f"{ion}: no Cartesian table of {NATOM} atoms")
    atoms = parsed["tables"][-1]
    if len(atoms) != NATOM:
        raise ValueError(f"{ion}: expected {NATOM} atoms, got {len(atoms)}")
    xyz = [(a[1], a[2], a[3]) for a in atoms]
    elements = [a[0] for a in atoms]
    r_cc = _dist(xyz[0], xyz[3])
    cx_elements = elements[4:7]
    if ion in DELTA_BLANK or len(set(cx_elements)) != 1 or cx_elements[0] == "H":
        delta_cx = None
    else:
        d_ip = _dist(xyz[3], xyz[4])
        d_oop = 0.5 * (_dist(xyz[3], xyz[5]) + _dist(xyz[3], xyz[6]))
        delta_cx = d_oop - d_ip
    phi = dihedral_deg(xyz[4], xyz[3], xyz[0], xyz[1])

    def _agg(pairs: list[tuple[str, float]]) -> tuple[float | None, float | None]:
        if len(pairs) != NATOM:
            return None, None
        q_o = 0.5 * (pairs[1][1] + pairs[2][1])
        q_coo = pairs[0][1] + pairs[1][1] + pairs[2][1]
        return q_o, q_coo

    q_o_mbis, q_coo_mbis = _agg(parsed["mbis"])
    q_o_lowdin, q_coo_lowdin = _agg(parsed["lowdin"])
    return {
        "elements": elements,
        "xyz": xyz,
        "r_cc": r_cc,
        "delta_cx": delta_cx,
        "phi_5142": phi,
        "q_o_mbis": q_o_mbis,
        "q_coo_mbis": q_coo_mbis,
        "q_o_lowdin": q_o_lowdin,
        "q_coo_lowdin": q_coo_lowdin,
    }


def known_walltime(ion_dir: Path) -> float | None:
    done = ion_dir / "done.json"
    if not done.is_file():
        return None
    try:
        payload = json.loads(done.read_text())
    except json.JSONDecodeError:
        return None
    value = payload.get("walltime_s")
    if value is None:
        return None
    return float(value)


def record_complete(record: dict) -> bool:
    if not record.get("optking") or not record.get("exit_ok"):
        return False
    if record.get("energy") is None or record.get("r_cc") is None:
        return False
    if record.get("q_o_lowdin") is None or record.get("q_coo_lowdin") is None:
        return False
    if record["ion"] not in MBIS_BLANK:
        if record.get("q_o_mbis") is None or record.get("q_coo_mbis") is None:
            return False
        if record.get("delta_cx") is None:
            return False
    return True


def build_record(ion: str, parsed: dict, extras: dict | None = None) -> dict:
    geom = derived(ion, parsed)
    wall = parsed.get("walltime_s")
    if wall is None and extras:
        wall = extras.get("walltime_s")
    record = {
        "ion": ion,
        "short": SHORT[ion],
        "formula": FORMULA[ion],
        "energy": parsed["energy"],
        "optking": parsed["optking"],
        "exit_ok": parsed["exit_ok"],
        "n_opt_steps": parsed["n_opt_steps"],
        "walltime_s": wall,
        **geom,
    }
    return record


def write_xyz(ion: str, record: dict) -> Path:
    path = ROOT / "xyz" / f"{ion}.xyz"
    path.parent.mkdir(parents=True, exist_ok=True)
    energy = record["energy"]
    comment = f"{ion} energy={energy} charge=-1"
    lines = [str(NATOM), comment]
    for element, (x, y, z) in zip(record["elements"], record["xyz"], strict=True):
        lines.append(f"{element:2s} {x:17.10f} {y:17.10f} {z:17.10f}")
    path.write_text("\n".join(lines) + "\n")
    return path


def _csv_float(value: float | None, digits: int) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def write_summary(records: list[dict]) -> Path:
    path = ROOT / "rematch" / "summary.csv"
    fieldnames = [
        "ion",
        "formula",
        "r_cc",
        "delta_cx_oop_ip",
        "q_o_mbis",
        "q_coo_mbis",
        "q_o_lowdin",
        "q_coo_lowdin",
        "converged_optking",
        "converged_exit",
    ]
    by_ion = {row["ion"]: row for row in records}
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for ion in ORDER:
            record = by_ion[ion]
            mbis_blank = ion in MBIS_BLANK
            delta_blank = ion in DELTA_BLANK
            writer.writerow(
                {
                    "ion": record["short"],
                    "formula": record["formula"],
                    "r_cc": _csv_float(record["r_cc"], 5),
                    "delta_cx_oop_ip": "" if delta_blank else _csv_float(record["delta_cx"], 5),
                    "q_o_mbis": "" if mbis_blank else _csv_float(record["q_o_mbis"], 5),
                    "q_coo_mbis": "" if mbis_blank else _csv_float(record["q_coo_mbis"], 5),
                    "q_o_lowdin": _csv_float(record["q_o_lowdin"], 5),
                    "q_coo_lowdin": _csv_float(record["q_coo_lowdin"], 5),
                    "converged_optking": "true" if record["optking"] else "false",
                    "converged_exit": "true" if record["exit_ok"] else "false",
                }
            )
    return path


def write_results_jsonl(records: list[dict]) -> Path:
    path = ROOT / "rematch" / "results.jsonl"
    with path.open("w") as handle:
        for record in records:
            payload = {
                key: record[key]
                for key in (
                    "ion",
                    "short",
                    "formula",
                    "energy",
                    "r_cc",
                    "delta_cx",
                    "phi_5142",
                    "q_o_mbis",
                    "q_coo_mbis",
                    "q_o_lowdin",
                    "q_coo_lowdin",
                    "optking",
                    "exit_ok",
                    "n_opt_steps",
                    "walltime_s",
                )
            }
            handle.write(json.dumps(payload) + "\n")
    return path


def print_table(records: list[dict]) -> None:
    header = (
        f"{'ion':<12} {'r_cc':>10} {'dCX':>10} {'qO_m':>10} {'qCOO_m':>10} "
        f"{'qO_L':>10} {'qCOO_L':>10} {'ok':>5}"
    )
    print(header)
    print("-" * len(header))
    for record in records:
        ok = "yes" if record["optking"] and record["exit_ok"] else "no"
        d_cx = record["delta_cx"]
        print(
            f"{record['short']:<12} "
            f"{record['r_cc']:10.5f} "
            f"{(d_cx if d_cx is not None else float('nan')):10.5f} "
            f"{(record['q_o_mbis'] if record['q_o_mbis'] is not None else float('nan')):10.5f} "
            f"{(record['q_coo_mbis'] if record['q_coo_mbis'] is not None else float('nan')):10.5f} "
            f"{(record['q_o_lowdin'] if record['q_o_lowdin'] is not None else float('nan')):10.5f} "
            f"{(record['q_coo_lowdin'] if record['q_coo_lowdin'] is not None else float('nan')):10.5f} "
            f"{ok:>5}"
        )


def run_psi4(ion: str) -> dict:
    ion_dir = ROOT / "rematch" / ion
    input_dat = ion_dir / "input.dat"
    output_dat = ion_dir / "output.dat"
    if not input_dat.is_file():
        raise FileNotFoundError(f"missing {input_dat}")
    env = os.environ.copy()
    started = time.monotonic()
    proc = subprocess.run(
        [PSI4, str(input_dat.name), "-o", output_dat.name],
        cwd=ion_dir,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.monotonic() - started
    stdout_log = ion_dir / "stdout.log"
    stdout_log.write_text(proc.stdout + proc.stderr)
    if not output_dat.is_file():
        raise RuntimeError(f"{ion}: Psi4 produced no output.dat (exit {proc.returncode})")
    text = output_dat.read_text(errors="replace")
    parsed = parse_outputs(text)
    if parsed["walltime_s"] is None:
        parsed["walltime_s"] = elapsed
    (ion_dir / "done.json").write_text(
        json.dumps(
            {
                "ion": ion,
                "returncode": proc.returncode,
                "walltime_s": parsed["walltime_s"],
            },
            indent=2,
        )
        + "\n"
    )
    return parsed


def reparse_ion(ion: str) -> dict:
    ion_dir = ROOT / "rematch" / ion
    output_dat = ion_dir / "output.dat"
    if not output_dat.is_file():
        raise FileNotFoundError(
            f"{output_dat} is not in this checkout; --reparse needs the private log"
        )
    parsed = parse_outputs(output_dat.read_text(errors="replace"))
    wall = parsed["walltime_s"]
    if wall is None:
        wall = known_walltime(ion_dir)
        parsed["walltime_s"] = wall
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sequential rematch of CH3COO− / CF3COO− / CClF2COO− / CCl3COO−."
    )
    parser.add_argument(
        "--reparse",
        action="store_true",
        help="Parse existing private output.dat files; do not invoke Psi4.",
    )
    parser.add_argument(
        "--only",
        choices=ORDER,
        action="append",
        help="Restrict to one or more ions (repeatable).",
    )
    args = parser.parse_args(argv)
    ions = args.only if args.only else list(ORDER)
    records = []
    for ion in ions:
        if args.reparse:
            parsed = reparse_ion(ion)
        else:
            parsed = run_psi4(ion)
        record = build_record(ion, parsed)
        write_xyz(ion, record)
        records.append(record)
        print(
            f"{ion}: E={record['energy']} rCC={record['r_cc']:.5f} "
            f"optking={record['optking']} exit={record['exit_ok']}",
            file=sys.stderr,
        )
        if not record_complete(record):
            print(f"{ion}: record incomplete", file=sys.stderr)
    if set(ions) == set(ORDER):
        write_summary(records)
        write_results_jsonl(records)
        print_table(records)
    return 0 if all(record_complete(r) for r in records) else 1


if __name__ == "__main__":
    sys.exit(main())
