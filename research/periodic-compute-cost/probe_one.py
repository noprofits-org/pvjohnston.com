#!/usr/bin/env python3
"""Run one neutral-atom timing probe and emit exactly one JSON record."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import math
import os
import resource
import sys
import time
import traceback
from typing import Any


PROTOCOL_ID = "periodic-compute-cost-phase1-v1"
MAX_MEMORY_MB = 3000
SCF_CONV_TOL = 1e-9
CC_CONV_TOL = 1e-7
MAX_CYCLES = 80
TIERS = ("UHF", "PBE", "MP2", "CCSD(T)")


class JsonArgumentParser(argparse.ArgumentParser):
    """Turn command-line mistakes into the same JSON error path as run errors."""

    def error(self, message: str) -> None:
        raise ValueError(f"invalid arguments: {message}")


def _parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--z", required=True, type=int)
    parser.add_argument("--spin", required=True, type=int)
    parser.add_argument("--tier", required=True, choices=TIERS)
    parser.add_argument("--basis", required=True)
    parser.add_argument("--panel", required=True)
    parser.add_argument("--repeat", required=True, type=int)
    parser.add_argument("--phase", required=True)
    return parser


def _base_record() -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "phase": None,
        "panel": None,
        "repeat": None,
        "symbol": None,
        "z": None,
        "charge": 0,
        "spin": None,
        "multiplicity": None,
        "tier": None,
        "basis": None,
        "ecp": None,
        "ecp_core_electrons": None,
        "max_memory_mb": MAX_MEMORY_MB,
        "n_basis_functions": None,
        "n_electrons": None,
        "n_alpha": None,
        "n_beta": None,
        "energy": None,
        "energy_unit": "hartree",
        "scf_energy": None,
        "correlation_energy": None,
        "triples_energy": None,
        "scf_converged": None,
        "scf_cycles": None,
        "s2": None,
        "correlation_converged": None,
        "correlation_cycles": None,
        "wall_seconds": None,
        "cpu_seconds": None,
        "peak_rss_mb": None,
        "outcome": "error",
        "error": None,
    }


def _populate_arguments(record: dict[str, Any], args: argparse.Namespace) -> None:
    record.update(
        {
            "phase": args.phase,
            "panel": args.panel,
            "repeat": args.repeat,
            "symbol": args.symbol,
            "z": args.z,
            "spin": args.spin,
            "multiplicity": args.spin + 1,
            "tier": args.tier,
            "basis": args.basis,
            "ecp": "def2-svp" if args.z >= 37 else None,
        }
    )


def _configure_single_thread() -> None:
    for name in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "BLIS_NUM_THREADS",
    ):
        os.environ[name] = "1"


def _load_pyscf() -> dict[str, Any]:
    # Imports deliberately happen before the probe timer starts.
    _configure_single_thread()
    from pyscf import cc, dft, gto, lib, mp, scf  # type: ignore[import-not-found]

    lib.num_threads(1)
    return {"cc": cc, "dft": dft, "gto": gto, "mp": mp, "scf": scf}


def _peak_rss_mb() -> float:
    peak = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # Linux reports KiB; macOS and the BSDs report bytes.
    divisor = 1024.0 * 1024.0 if sys.platform == "darwin" else 1024.0
    return peak / divisor


def _finite_float(value: Any, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} is not finite: {result!r}")
    return result


def _cycles_from(obj: Any, callback_count: int) -> int:
    candidates = [callback_count]
    for name in ("cycles", "iterations"):
        value = getattr(obj, name, None)
        if isinstance(value, int) and not isinstance(value, bool):
            candidates.append(value)
    return max(candidates)


def _run_probe(record: dict[str, Any], args: argparse.Namespace, pyscf: dict[str, Any]) -> None:
    if args.basis.lower() != "def2-svp":
        raise ValueError(f"protocol requires def2-SVP, got {args.basis!r}")
    if args.z < 1:
        raise ValueError("atomic number must be positive")
    if args.spin < 0:
        raise ValueError("spin must be non-negative")
    if args.repeat < 0:
        raise ValueError("repeat must be non-negative")

    gto = pyscf["gto"]
    expected_z = int(gto.charge(args.symbol))
    if expected_z != args.z:
        raise ValueError(
            f"symbol/Z mismatch: {args.symbol!r} is Z={expected_z}, not Z={args.z}"
        )

    ecp = "def2-svp" if args.z >= 37 else None
    mol = gto.Mole()
    mol.atom = [(args.symbol, (0.0, 0.0, 0.0))]
    mol.charge = 0
    mol.spin = args.spin
    mol.basis = args.basis
    mol.cart = False
    mol.symmetry = False
    if ecp is not None:
        mol.ecp = ecp
    mol.max_memory = MAX_MEMORY_MB
    mol.verbose = 0
    mol.build()

    n_electrons = int(mol.nelectron)
    n_alpha, n_beta = (int(value) for value in mol.nelec)
    if args.spin > n_electrons or (n_electrons - args.spin) % 2:
        raise ValueError(
            f"invalid spin {args.spin} for {n_electrons} explicit electrons"
        )

    effective_nuclear_charge = int(mol.atom_charge(0))
    record.update(
        {
            "ecp_core_electrons": args.z - effective_nuclear_charge,
            "n_basis_functions": int(mol.nao_nr()),
            "n_electrons": n_electrons,
            "n_alpha": n_alpha,
            "n_beta": n_beta,
        }
    )

    scf_cycle_count = 0

    def count_scf_cycle(envs: dict[str, Any]) -> None:
        nonlocal scf_cycle_count
        cycle = envs.get("cycle")
        if isinstance(cycle, int):
            scf_cycle_count = max(scf_cycle_count, cycle + 1)

    if args.tier == "PBE":
        mean_field = pyscf["dft"].UKS(mol)
        mean_field.xc = "PBE"
        mean_field.grids.level = 3
    else:
        mean_field = pyscf["scf"].UHF(mol)

    mean_field.conv_tol = SCF_CONV_TOL
    mean_field.max_cycle = MAX_CYCLES
    mean_field.init_guess = "minao"
    mean_field.max_memory = MAX_MEMORY_MB
    mean_field.verbose = 0
    mean_field.callback = count_scf_cycle
    mean_field.kernel()

    record["scf_converged"] = bool(mean_field.converged)
    record["scf_cycles"] = _cycles_from(mean_field, scf_cycle_count)
    record["scf_energy"] = _finite_float(mean_field.e_tot, "SCF energy")
    record["s2"] = _finite_float(mean_field.spin_square()[0], "<S^2>")

    if not mean_field.converged:
        record["outcome"] = "unconverged"
        record["error"] = f"SCF did not converge within {MAX_CYCLES} cycles"
        return

    if args.tier in ("UHF", "PBE"):
        record["energy"] = record["scf_energy"]
        record["outcome"] = "ok"
        return

    if args.tier == "MP2":
        correlation = pyscf["mp"].UMP2(mean_field)
        correlation.max_memory = MAX_MEMORY_MB
        correlation.verbose = 0
        correlation.kernel()
        record["correlation_energy"] = _finite_float(
            correlation.e_corr, "UMP2 correlation energy"
        )
        # Canonical MP2 is non-iterative; successful return is its convergence test.
        record["correlation_converged"] = True
        record["correlation_cycles"] = 0
        record["energy"] = record["scf_energy"] + record["correlation_energy"]
        record["outcome"] = "ok"
        return

    correlation_cycle_count = 0

    def count_correlation_cycle(envs: dict[str, Any]) -> None:
        nonlocal correlation_cycle_count
        cycle = envs.get("istep", envs.get("cycle"))
        if isinstance(cycle, int):
            correlation_cycle_count = max(correlation_cycle_count, cycle + 1)

    correlation = pyscf["cc"].UCCSD(mean_field)
    correlation.conv_tol = CC_CONV_TOL
    correlation.max_cycle = MAX_CYCLES
    correlation.max_memory = MAX_MEMORY_MB
    correlation.verbose = 0
    correlation.callback = count_correlation_cycle
    correlation.kernel()
    record["correlation_converged"] = bool(correlation.converged)
    record["correlation_cycles"] = _cycles_from(
        correlation, correlation_cycle_count
    )
    record["correlation_energy"] = _finite_float(
        correlation.e_corr, "UCCSD correlation energy"
    )

    if not correlation.converged:
        record["outcome"] = "unconverged"
        record["error"] = f"UCCSD did not converge within {MAX_CYCLES} cycles"
        return

    record["triples_energy"] = _finite_float(
        correlation.ccsd_t(), "UCCSD(T) triples energy"
    )
    record["energy"] = (
        record["scf_energy"]
        + record["correlation_energy"]
        + record["triples_energy"]
    )
    record["outcome"] = "ok"


def _error_text(exc: Exception) -> str:
    detail = "".join(traceback.format_exception_only(type(exc), exc)).strip()
    return detail or type(exc).__name__


def main(argv: list[str] | None = None) -> int:
    record = _base_record()
    timer_started = False
    wall_start = 0.0
    cpu_start = 0.0

    try:
        args = _parser().parse_args(argv)
        _populate_arguments(record, args)
        with contextlib.redirect_stdout(sys.stderr):
            pyscf = _load_pyscf()

        wall_start = time.perf_counter()
        cpu_start = time.process_time()
        timer_started = True
        # Keep any library chatter off stdout; stdout is the JSON protocol channel.
        with contextlib.redirect_stdout(sys.stderr):
            _run_probe(record, args, pyscf)
    except MemoryError as exc:
        record["outcome"] = "oom"
        record["error"] = _error_text(exc)
    except Exception as exc:
        record["outcome"] = "error"
        record["error"] = _error_text(exc)
    finally:
        if timer_started:
            record["wall_seconds"] = time.perf_counter() - wall_start
            record["cpu_seconds"] = time.process_time() - cpu_start
        record["peak_rss_mb"] = _peak_rss_mb()

    sys.stdout.write(json.dumps(record, allow_nan=False, sort_keys=True) + "\n")
    # A reported scientific failure is still a successfully delivered record.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
