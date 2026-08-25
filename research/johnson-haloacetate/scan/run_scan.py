#!/usr/bin/env python3
"""Relaxed CX3 scan of CF3COO− and CCl3COO−.

Canonical scan driver. Neighbor-starts from the rematch-optimized xyz,
freezes dihedral 5-4-1-2, and steps 0–120° by 15°. It is not a CI rerun.

Stdout is only: ion angle energy converged_optking walltime
Diagnostics go to stderr. Raw output.dat / timer.dat / stdout.log /
done.json stay local. Set PSI4 to the executable; it defaults to "psi4".

--reparse rebuilds summaries from private output.dat files and never
invokes Psi4. The publication scan CSVs under results/ are a separate
projection and are not overwritten here.
"""

from __future__ import annotations

import argparse
import copy
import csv
import importlib.util
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

PSI4 = os.environ.get("PSI4", "psi4")
ROOT = Path(__file__).resolve().parent.parent
SCAN = ROOT / "scan"
IONS = ["m1_cf3", "m3_ccl3"]
ANGLES = [0, 15, 30, 45, 60, 75, 90, 105, 120]
SEEDS = {
    "m1_cf3": ROOT / "xyz" / "m1_cf3.xyz",
    "m3_ccl3": ROOT / "xyz" / "m3_ccl3.xyz",
}
FROZEN_DIHEDRAL = "5 4 1 2"
# 1-based Psi4 indices for φ = X–Cα–C–O.
IDX_X, IDX_CA, IDX_C, IDX_O = 4, 3, 0, 1
# The three CX3 substituents, 0-based.
CX3 = (4, 5, 6)
NATOM = 7


def load_rematch():
    path = ROOT / "rematch" / "run_rematch.py"
    spec = importlib.util.spec_from_file_location(
        "johnson_haloacetate_rematch", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_rematch_patterns(rematch) -> None:
    cart = rematch.CART_HEADER_RE.pattern
    lowdin = rematch.LOWDIN_RE.pattern
    mbis = rematch.MBIS_RE.pattern
    if "Center" not in cart:
        raise AssertionError("CART_HEADER_RE must match a Center header")
    if "Lowdin" not in lowdin:
        raise AssertionError("LOWDIN_RE must match a Lowdin block")
    if "MBIS" not in mbis:
        raise AssertionError("MBIS_RE must match an MBIS block")
    if r"(?<!Valence )" not in mbis:
        raise AssertionError("MBIS_RE must skip Valence MBIS with (?<!Valence )")


def read_xyz(path: Path) -> tuple[list[str], list[list[float]]]:
    text = path.read_text()
    lines = text.splitlines()
    if len(lines) < 2 + NATOM:
        raise ValueError(f"{path}: expected {NATOM} atoms")
    n = int(lines[0].strip())
    if n != NATOM:
        raise ValueError(f"{path}: natom {n} != {NATOM}")
    elements = []
    xyz = []
    for line in lines[2:2 + NATOM]:
        parts = line.split()
        elements.append(parts[0])
        xyz.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return elements, xyz


def wrap180(deg: float) -> float:
    wrapped = (deg + 180.0) % 360.0 - 180.0
    if wrapped == -180.0:
        return 180.0
    return wrapped


def rotate_about_axis(point, origin, axis, deg: float):
    """Rodrigues rotation of point about origin+axis by deg."""
    rad = math.radians(deg)
    ax = axis[0]
    ay = axis[1]
    az = axis[2]
    norm = math.sqrt(ax * ax + ay * ay + az * az)
    if norm == 0.0:
        return [point[0], point[1], point[2]]
    ux, uy, uz = ax / norm, ay / norm, az / norm
    px = point[0] - origin[0]
    py = point[1] - origin[1]
    pz = point[2] - origin[2]
    cos_t = math.cos(rad)
    sin_t = math.sin(rad)
    dot = ux * px + uy * py + uz * pz
    cx = uy * pz - uz * py
    cy = uz * px - ux * pz
    cz = ux * py - uy * px
    return [
        origin[0] + px * cos_t + cx * sin_t + ux * dot * (1.0 - cos_t),
        origin[1] + py * cos_t + cy * sin_t + uy * dot * (1.0 - cos_t),
        origin[2] + pz * cos_t + cz * sin_t + uz * dot * (1.0 - cos_t),
    ]


def phi_of(xyz, dihedral_deg) -> float:
    """Signed φ of atoms 5-4-1-2 (X–Cα–C–O)."""
    return dihedral_deg(
        xyz[IDX_X], xyz[IDX_CA], xyz[IDX_C], xyz[IDX_O]
    )


def set_phi(xyz, target_deg: float, dihedral_deg) -> list[list[float]]:
    """Rotate the CX3 substituents about Cα–C so φ(5-4-1-2) is target_deg."""
    out = [list(p) for p in xyz]
    current = phi_of(out, dihedral_deg)
    delta = wrap180(target_deg - current)
    if abs(delta) < 1e-12:
        return out
    origin = out[IDX_CA]
    # Axis is Cα → C. The signed dihedral 5-4-1-2 increases when the
    # CX3 substituents rotate the opposite way about that axis.
    axis = [
        out[IDX_C][0] - origin[0],
        out[IDX_C][1] - origin[1],
        out[IDX_C][2] - origin[2],
    ]
    for index in CX3:
        out[index] = rotate_about_axis(out[index], origin, axis, -delta)
    return out


def workdir(ion: str, angle: int) -> Path:
    return SCAN / ion / f"{angle}"


def write_input(path: Path, elements: list[str], xyz: list[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "memory 8 GB",
        "",
        "molecule {",
        "-1 1",
    ]
    for element, (x, y, z) in zip(elements, xyz, strict=True):
        lines.append(f"{element:2s} {x:17.10f} {y:17.10f} {z:17.10f}")
    lines.extend(
        [
            "  symmetry c1",
            "}",
            "",
            "set {",
            "  basis aug-cc-pvdz",
            "  scf_type df",
            "  geom_maxiter 150",
            "}",
            "",
            "set optking {",
            f'  frozen_dihedral = ("{FROZEN_DIHEDRAL}")',
            "}",
            "",
            "e, wfn = optimize('b3lyp-d3bj', return_wfn=True)",
            "oeprop(wfn, 'MBIS_CHARGES', 'LOWDIN_CHARGES')",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def emit_stdout(ion: str, angle: int, energy, optking, walltime) -> None:
    energy_s = "" if energy is None else repr(energy)
    wall_s = "" if walltime is None else repr(walltime)
    opt_s = "true" if optking else "false"
    sys.stdout.write(f"{ion} {angle} {energy_s} {opt_s} {wall_s}\n")
    sys.stdout.flush()


def write_ion_summary(ion: str, records: list[dict]) -> Path:
    path = SCAN / ion / "summary.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ion",
        "angle",
        "energy_eh",
        "q_o_mbis",
        "q_coo_mbis",
        "q_o_lowdin",
        "q_coo_lowdin",
        "converged_optking",
        "converged_exit",
    ]

    def fmt(value, digits=None):
        if value is None:
            return ""
        if digits is None:
            return repr(value)
        return f"{value:.{digits}f}"

    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "ion": ion,
                    "angle": record["angle"],
                    "energy_eh": fmt(record.get("energy")),
                    "q_o_mbis": fmt(record.get("q_o_mbis"), 7),
                    "q_coo_mbis": fmt(record.get("q_coo_mbis"), 7),
                    "q_o_lowdin": fmt(record.get("q_o_lowdin"), 7),
                    "q_coo_lowdin": fmt(record.get("q_coo_lowdin"), 7),
                    "converged_optking": "true" if record.get("optking") else "false",
                    "converged_exit": "true" if record.get("exit_ok") else "false",
                }
            )
    return path


def write_scan_jsonl(ion: str, records: list[dict]) -> Path:
    """Private per-ion JSONL; not a publication file."""
    path = SCAN / ion / "results.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = (
        "ion",
        "angle",
        "energy",
        "phi_5142",
        "q_o_mbis",
        "q_coo_mbis",
        "q_o_lowdin",
        "q_coo_lowdin",
        "optking",
        "exit_ok",
        "walltime_s",
    )
    with path.open("w") as handle:
        for record in records:
            handle.write(json.dumps({key: record.get(key) for key in keys}) + "\n")
    return path


def neighbor_start_xyz(last_xyz, angle: int, dihedral_deg):
    """Take the previous optimized geometry and rotate CX3 onto `angle`."""
    if last_xyz is None:
        raise ValueError("neighbor-start has no previous geometry")
    return set_phi(last_xyz, float(angle), dihedral_deg)


def run_psi4(ion: str, angle: int, elements, xyz) -> dict:
    ion_dir = workdir(ion, angle)
    input_dat = ion_dir / "input.dat"
    output_dat = ion_dir / "output.dat"
    write_input(input_dat, elements, xyz)
    env = os.environ.copy()
    started = time.monotonic()
    proc = subprocess.run(
        [PSI4, input_dat.name, "-o", output_dat.name],
        cwd=ion_dir,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.monotonic() - started
    (ion_dir / "stdout.log").write_text(proc.stdout + proc.stderr)
    if not output_dat.is_file():
        raise RuntimeError(
            f"{ion} {angle}: Psi4 produced no output.dat (exit {proc.returncode})"
        )
    return {"elapsed": elapsed, "returncode": proc.returncode}


def reparse_or_read(ion: str, angle: int, rematch, extras: dict | None) -> dict:
    ion_dir = workdir(ion, angle)
    output_dat = ion_dir / "output.dat"
    if not output_dat.is_file():
        raise FileNotFoundError(
            f"{output_dat} is not in this checkout; --reparse needs the private log"
        )
    parsed = rematch.parse_outputs(output_dat.read_text(errors="replace"))
    if parsed.get("walltime_s") is None:
        wall = rematch.known_walltime(ion_dir)
        if wall is None and extras:
            wall = extras.get("elapsed")
        parsed["walltime_s"] = wall
    return parsed


def build_scan_record(ion: str, angle: int, parsed: dict, rematch) -> dict:
    geom = rematch.derived(ion, parsed)
    record = {
        "ion": ion,
        "angle": angle,
        "energy": parsed.get("energy"),
        "optking": parsed.get("optking"),
        "exit_ok": parsed.get("exit_ok"),
        "walltime_s": parsed.get("walltime_s"),
        **geom,
    }
    return record


def scan_ion(ion: str, rematch, reparse: bool) -> list[dict]:
    seed_path = SEEDS[ion]
    elements, seed_xyz = read_xyz(seed_path)
    last_xyz = copy.deepcopy(seed_xyz)
    records = []
    for angle in ANGLES:
        start_xyz = neighbor_start_xyz(last_xyz, angle, rematch.dihedral_deg)
        extras = None
        if reparse:
            parsed = reparse_or_read(ion, angle, rematch, None)
        else:
            extras = run_psi4(ion, angle, elements, start_xyz)
            parsed = reparse_or_read(ion, angle, rematch, extras)
            if parsed.get("walltime_s") is None:
                parsed["walltime_s"] = extras.get("elapsed")
            (workdir(ion, angle) / "done.json").write_text(
                json.dumps(
                    {
                        "ion": ion,
                        "angle": angle,
                        "returncode": extras["returncode"],
                        "walltime_s": parsed["walltime_s"],
                    },
                    indent=2,
                )
                + "\n"
            )
        record = build_scan_record(ion, angle, parsed, rematch)
        emit_stdout(
            ion,
            angle,
            record.get("energy"),
            bool(record.get("optking")),
            record.get("walltime_s"),
        )
        if record.get("xyz") is not None:
            last_xyz = [list(p) for p in record["xyz"]]
        else:
            last_xyz = start_xyz
        if not rematch.record_complete(record):
            print(f"{ion} {angle}: record incomplete", file=sys.stderr)
        records.append(record)
    write_ion_summary(ion, records)
    write_scan_jsonl(ion, records)
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Relaxed φ = X–Cα–C–O scan of CF3COO− and CCl3COO−."
    )
    parser.add_argument(
        "--reparse",
        action="store_true",
        help="Parse existing private output.dat files; do not invoke Psi4.",
    )
    parser.add_argument(
        "--only",
        choices=IONS,
        action="append",
        help="Restrict to one ion (repeatable).",
    )
    args = parser.parse_args(argv)
    rematch = load_rematch()
    assert_rematch_patterns(rematch)
    _ = rematch.CART_HEADER_RE
    _ = rematch.LOWDIN_RE
    _ = rematch.MBIS_RE
    _ = rematch.parse_outputs
    _ = rematch.record_complete
    rematch_derived = rematch.derived
    _ = rematch_derived
    _ = rematch.dihedral_deg
    _ = rematch.canon_el
    _ = rematch.known_walltime
    ions = args.only if args.only else list(IONS)
    status = 0
    for ion in ions:
        records = scan_ion(ion, rematch, args.reparse)
        if not all(rematch.record_complete(r) for r in records):
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
