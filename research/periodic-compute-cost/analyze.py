#!/usr/bin/env python3
"""Validate, summarize, and plot the canonical periodic-compute-cost run."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUNS_PATH = HERE / "results" / "runs.jsonl"
SUMMARY_PATH = HERE / "results" / "summary.json"
FIGURE_PATH = ROOT / "images" / "2026-08-07-periodic-compute-cost-hero.png"
PROTOCOL_ID = "periodic-compute-cost-phase1-v1"

ATOM_SPECS = (
    ("halogens", "F", 9, 1),
    ("halogens", "Cl", 17, 1),
    ("halogens", "Br", 35, 1),
    ("halogens", "I", 53, 1),
    ("alkaline_earths", "Be", 4, 0),
    ("alkaline_earths", "Mg", 12, 0),
    ("alkaline_earths", "Ca", 20, 0),
    ("alkaline_earths", "Sr", 38, 0),
    ("transition_neighbors", "Cr", 24, 6),
    ("transition_neighbors", "Mn", 25, 5),
    ("transition_neighbors", "Fe", 26, 4),
    ("transition_neighbors", "Zn", 30, 0),
    ("ecp_boundary", "Kr", 36, 0),
    ("ecp_boundary", "Rb", 37, 1),
)
MP2_SYMBOLS = frozenset(("F", "Cl", "Br", "I", "Be", "Mg", "Ca", "Sr", "Kr", "Rb"))
CCSD_T_SYMBOLS = frozenset(("F", "Cl", "Be", "Mg"))
# These are canonical-output integrity checks, not preregistered predictions.
# A rerun that changes a scientific outcome requires review before it replaces
# the publication source rather than silently regenerating different prose.
CANONICAL_FAILURES = frozenset(
    (("survey", "I", "PBE", 0), ("survey", "I", "PBE", 1),
     ("survey", "Fe", "PBE", 0), ("survey", "Fe", "PBE", 1))
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_jobs() -> set[tuple[str, str, str, str, int]]:
    jobs: set[tuple[str, str, str, str, int]] = set()
    for panel, symbol, _z, _spin in ATOM_SPECS:
        for tier in ("UHF", "PBE"):
            for repeat in (0, 1):
                jobs.add(("survey", panel, symbol, tier, repeat))
        if symbol in MP2_SYMBOLS:
            jobs.add(("correlation", panel, symbol, "MP2", 0))
        if symbol in CCSD_T_SYMBOLS:
            jobs.add(("deep", panel, symbol, "CCSD(T)", 0))
    return jobs


def load_and_validate() -> list[dict]:
    rows = []
    for line_number, line in enumerate(RUNS_PATH.read_text(encoding="utf-8").splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON on line {line_number}: {error}") from error
        if not isinstance(row, dict):
            raise ValueError(f"line {line_number} is not a JSON object")
        rows.append(row)

    if len(rows) != 70:
        raise ValueError(f"expected 70 production rows, found {len(rows)}")
    if {row.get("protocol_id") for row in rows} != {PROTOCOL_ID}:
        raise ValueError("unexpected protocol identifier")

    actual_jobs = [
        (row["phase"], row["panel"], row["symbol"], row["tier"], row["repeat"])
        for row in rows
    ]
    if len(set(actual_jobs)) != len(actual_jobs):
        raise ValueError("duplicate production job key")
    if set(actual_jobs) != expected_jobs():
        missing = sorted(expected_jobs() - set(actual_jobs))
        extra = sorted(set(actual_jobs) - expected_jobs())
        raise ValueError(f"job matrix mismatch; missing={missing}, extra={extra}")

    specs = {symbol: (panel, z, spin) for panel, symbol, z, spin in ATOM_SPECS}
    for row in rows:
        panel, z, spin = specs[row["symbol"]]
        if (row["panel"], row["z"], row["spin"]) != (panel, z, spin):
            raise ValueError(f"atomic specification mismatch for {row['symbol']}")
        if not isinstance(row.get("wall_seconds"), (int, float)) or row["wall_seconds"] <= 0:
            raise ValueError("every child-reported attempt must have a positive wall time")

    failures = {
        (row["phase"], row["symbol"], row["tier"], row["repeat"])
        for row in rows
        if row["outcome"] != "ok"
    }
    if failures != CANONICAL_FAILURES:
        raise ValueError(f"canonical non-ok rows changed: {sorted(failures)}")
    for row in rows:
        if (row["phase"], row["symbol"], row["tier"], row["repeat"]) in failures:
            if row["outcome"] != "unconverged" or row["scf_cycles"] != 80:
                raise ValueError("canonical failures must be 80-cycle SCF nonconvergence")

    return rows


def summarize_tier(rows: list[dict]) -> dict:
    walls = [row["wall_seconds"] for row in rows]
    outcomes = sorted({row["outcome"] for row in rows})
    if len(outcomes) != 1:
        raise ValueError("mixed outcomes within a repeated atom/tier pair")
    cycles = sorted({row["scf_cycles"] for row in rows})
    if len(cycles) != 1:
        raise ValueError("SCF cycle count changed between fixed repeats")
    return {
        "attempts": len(rows),
        "outcome": outcomes[0],
        "median_wall_seconds": statistics.median(walls),
        "minimum_wall_seconds": min(walls),
        "maximum_wall_seconds": max(walls),
        "scf_cycles": cycles[0],
    }


def build_summary(rows: list[dict]) -> dict:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["symbol"], row["tier"]].append(row)

    atoms = []
    by_symbol = {}
    for panel, symbol, z, spin in ATOM_SPECS:
        atom_rows = [row for row in rows if row["symbol"] == symbol]
        dimensions = {
            (row["n_electrons"], row["n_basis_functions"], row["ecp_core_electrons"])
            for row in atom_rows
        }
        if len(dimensions) != 1:
            raise ValueError(f"representation changed between jobs for {symbol}")
        explicit_electrons, basis_functions, ecp_core_electrons = dimensions.pop()
        tier_names = ["UHF", "PBE"]
        if symbol in MP2_SYMBOLS:
            tier_names.append("MP2")
        if symbol in CCSD_T_SYMBOLS:
            tier_names.append("CCSD(T)")
        atom = {
            "panel": panel,
            "symbol": symbol,
            "atomic_number": z,
            "spin_2s": spin,
            "ecp_core_electrons": ecp_core_electrons,
            "explicit_electrons": explicit_electrons,
            "basis_functions": basis_functions,
            "tiers": {tier: summarize_tier(grouped[symbol, tier]) for tier in tier_names},
        }
        atoms.append(atom)
        by_symbol[symbol] = atom

    count_pairs = Counter((row["phase"], row["outcome"]) for row in rows)
    repeat_differences = []
    for (symbol, tier), pair in grouped.items():
        if tier not in ("UHF", "PBE") or len(pair) != 2:
            continue
        if any(row["outcome"] != "ok" for row in pair):
            continue
        walls = [row["wall_seconds"] for row in pair]
        repeat_differences.append(
            {
                "symbol": symbol,
                "tier": tier,
                "relative_range_percent": 100 * (max(walls) - min(walls)) / statistics.median(walls),
            }
        )
    max_repeat = max(repeat_differences, key=lambda record: record["relative_range_percent"])

    def time(symbol: str, tier: str) -> float:
        return by_symbol[symbol]["tiers"][tier]["median_wall_seconds"]

    ecp_time_decreases = {
        tier: 100 * (1 - time("Rb", tier) / time("Kr", tier))
        for tier in ("UHF", "PBE", "MP2")
    }
    transition_pbe = {
        symbol: {
            "median_wall_seconds": time(symbol, "PBE"),
            "scf_cycles": by_symbol[symbol]["tiers"]["PBE"]["scf_cycles"],
            "outcome": by_symbol[symbol]["tiers"]["PBE"]["outcome"],
        }
        for symbol in ("Cr", "Mn", "Fe", "Zn")
    }
    light_method_ratios = {}
    for symbol in ("F", "Cl", "Be", "Mg"):
        uhf = time(symbol, "UHF")
        light_method_ratios[symbol] = {
            "mp2_over_uhf": time(symbol, "MP2") / uhf,
            "ccsd_t_over_uhf": time(symbol, "CCSD(T)") / uhf,
            "pbe_over_uhf": time(symbol, "PBE") / uhf,
        }
    ccsd_ratios = [record["ccsd_t_over_uhf"] for record in light_method_ratios.values()]

    return {
        "schema_version": 1,
        "experiment": "periodic-compute-cost",
        "protocol_id": PROTOCOL_ID,
        "source": {
            "path": "research/periodic-compute-cost/results/runs.jsonl",
            "sha256": sha256(RUNS_PATH),
        },
        "aggregation": {
            "survey_wall_time": "median of the two fixed repeats",
            "correlation_and_deep_wall_time": "the single fixed attempt",
            "nonconvergence": "retained at the fixed 80-cycle boundary; not treated as a completed timing",
        },
        "counts": {
            "atoms": len(ATOM_SPECS),
            "jobs": len(rows),
            "ok": sum(row["outcome"] == "ok" for row in rows),
            "unconverged": sum(row["outcome"] == "unconverged" for row in rows),
            "survey_ok": count_pairs["survey", "ok"],
            "survey_unconverged": count_pairs["survey", "unconverged"],
            "correlation_ok": count_pairs["correlation", "ok"],
            "deep_ok": count_pairs["deep", "ok"],
        },
        "atoms": atoms,
        "contrasts": {
            "successful_survey_repeat_timing": {
                "median_relative_range_percent": statistics.median(
                    record["relative_range_percent"] for record in repeat_differences
                ),
                "maximum": max_repeat,
            },
            "kr_to_rb_ecp_boundary": {
                "atomic_number_change": 1,
                "ecp_core_electrons": by_symbol["Rb"]["ecp_core_electrons"],
                "explicit_electron_change": (
                    by_symbol["Rb"]["explicit_electrons"]
                    - by_symbol["Kr"]["explicit_electrons"]
                ),
                "basis_function_change": (
                    by_symbol["Rb"]["basis_functions"]
                    - by_symbol["Kr"]["basis_functions"]
                ),
                "wall_time_decrease_percent": ecp_time_decreases,
            },
            "transition_pbe": transition_pbe,
            "iodine_pbe": {
                "median_wall_seconds_at_cap": time("I", "PBE"),
                "scf_cycles": by_symbol["I"]["tiers"]["PBE"]["scf_cycles"],
                "outcome": by_symbol["I"]["tiers"]["PBE"]["outcome"],
            },
            "light_method_timing": {
                "atoms": light_method_ratios,
                "ccsd_t_over_uhf_minimum": min(ccsd_ratios),
                "ccsd_t_over_uhf_maximum": max(ccsd_ratios),
                "pbe_slower_than_ccsd_t_count": sum(
                    time(symbol, "PBE") > time(symbol, "CCSD(T)")
                    for symbol in ("F", "Cl", "Be", "Mg")
                ),
            },
        },
    }


def figure_bytes(summary: dict) -> bytes:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError as error:
        raise RuntimeError(
            "figure generation needs the packages in requirements-analysis.txt"
        ) from error

    # Ignore user matplotlibrc files so the pinned plotting environment owns
    # every style choice that can affect the byte-compared publication image.
    matplotlib.rcdefaults()
    matplotlib.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.sans-serif": ["DejaVu Sans"],
        "text.usetex": False,
    })

    ink = "#1a1d2b"
    indigo = "#465c9b"
    lift = "#8fa5e3"
    deep = "#2f417a"
    cream = "#f5f2ea"
    atoms = summary["atoms"]
    symbols = [atom["symbol"] for atom in atoms]
    x_values = list(range(len(atoms)))
    groups = (range(0, 4), range(4, 8), range(8, 12), range(12, 14))

    fig, (size_ax, time_ax) = plt.subplots(
        1,
        2,
        figsize=(12, 6.3),
        dpi=100,
        gridspec_kw={"width_ratios": [1, 1.08], "wspace": 0.22},
    )
    fig.patch.set_facecolor(cream)
    for axis in (size_ax, time_ax):
        axis.set_facecolor(cream)

    electrons = [atom["explicit_electrons"] for atom in atoms]
    basis = [atom["basis_functions"] for atom in atoms]
    for group_number, indices in enumerate(groups):
        indices = list(indices)
        size_ax.plot(
            indices,
            [electrons[index] for index in indices],
            marker="o",
            color=deep,
            lw=2.2,
            ms=7,
            label="explicit electrons" if group_number == 0 else None,
        )
        size_ax.plot(
            indices,
            [basis[index] for index in indices],
            marker="s",
            color=lift,
            markeredgecolor=ink,
            markeredgewidth=0.8,
            lw=2.2,
            ms=7,
            label="basis functions" if group_number == 0 else None,
        )
    size_ax.set_ylim(0, 40)
    size_ax.set_yticks((0, 10, 20, 30, 40))
    size_ax.set_ylabel("count in fixed representation", fontsize=12, color=ink)
    size_ax.legend(frameon=False, fontsize=10, loc="upper left", labelcolor=ink)
    size_ax.annotate(
        "A",
        xy=(13, electrons[13]),
        xytext=(-4, -27),
        textcoords="offset points",
        fontsize=16,
        fontweight="bold",
        color=ink,
    )

    uhf = [atom["tiers"]["UHF"]["median_wall_seconds"] for atom in atoms]
    pbe = [atom["tiers"]["PBE"]["median_wall_seconds"] for atom in atoms]
    pbe_ok = [atom["tiers"]["PBE"]["outcome"] == "ok" for atom in atoms]
    for indices in groups:
        indices = list(indices)
        time_ax.plot(indices, [uhf[index] for index in indices], color=deep, lw=2.0)
        time_ax.plot(indices, [pbe[index] for index in indices], color=indigo, lw=2.0)
    time_ax.scatter(x_values, uhf, marker="o", s=48, color=deep, zorder=3)
    time_ax.scatter(
        [index for index in x_values if pbe_ok[index]],
        [pbe[index] for index in x_values if pbe_ok[index]],
        marker="s",
        s=52,
        color=lift,
        edgecolor=ink,
        linewidth=0.8,
        zorder=3,
    )
    time_ax.scatter(
        [index for index in x_values if not pbe_ok[index]],
        [pbe[index] for index in x_values if not pbe_ok[index]],
        marker="^",
        s=80,
        facecolor=cream,
        edgecolor=ink,
        linewidth=1.7,
        zorder=4,
    )
    time_ax.set_yscale("log")
    time_ax.set_ylim(0.06, 5)
    time_ax.set_yticks((0.1, 0.2, 0.5, 1, 2, 4), ("0.1", "0.2", "0.5", "1", "2", "4"))
    time_ax.set_ylabel("calculation wall time (s, log scale)", fontsize=12, color=ink)
    time_ax.legend(
        handles=(
            Line2D([0], [0], marker="o", color=deep, markerfacecolor=deep,
                   markersize=7, label="UHF"),
            Line2D([0], [0], marker="s", color=indigo, markerfacecolor=lift,
                   markeredgecolor=ink, markersize=7, label="PBE"),
            Line2D([0], [0], marker="^", color="none", markerfacecolor=cream,
                   markeredgecolor=ink, markersize=8, label="PBE at cycle cap"),
        ),
        frameon=False,
        fontsize=10,
        loc="upper left",
        labelcolor=ink,
    )
    time_ax.annotate(
        "B",
        xy=(3, pbe[3]),
        xytext=(-18, 7),
        textcoords="offset points",
        fontsize=16,
        fontweight="bold",
        color=ink,
    )
    time_ax.annotate(
        "C",
        xy=(10, pbe[10]),
        xytext=(7, 7),
        textcoords="offset points",
        fontsize=16,
        fontweight="bold",
        color=ink,
    )

    for axis in (size_ax, time_ax):
        axis.set_xticks(x_values, symbols)
        axis.set_xlabel("atom, grouped by comparison", fontsize=12, color=ink)
        for boundary in (3.5, 7.5, 11.5):
            axis.axvline(boundary, color=ink, lw=0.8, alpha=0.18, zorder=0)
        axis.grid(axis="y", color=ink, alpha=0.10, lw=0.8)
        for spine in ("top", "right"):
            axis.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            axis.spines[spine].set_color(ink)
        axis.tick_params(colors=ink, labelsize=9)

    fig.subplots_adjust(left=0.065, right=0.98, top=0.95, bottom=0.14)
    output = io.BytesIO()
    fig.savefig(
        output,
        format="png",
        dpi=100,
        facecolor=cream,
        metadata={"Software": f"Matplotlib {matplotlib.__version__}"},
    )
    plt.close(fig)
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()

    try:
        summary = build_summary(load_and_validate())
        summary_text = json.dumps(summary, indent=2) + "\n"
        image = figure_bytes(summary)
    except (KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"periodic-compute-cost analysis failed: {error}", file=sys.stderr)
        return 1

    if arguments.check:
        stale = []
        if not SUMMARY_PATH.is_file() or SUMMARY_PATH.read_text(encoding="utf-8") != summary_text:
            stale.append(str(SUMMARY_PATH.relative_to(ROOT)))
        if not FIGURE_PATH.is_file() or FIGURE_PATH.read_bytes() != image:
            stale.append(str(FIGURE_PATH.relative_to(ROOT)))
        if stale:
            print(f"missing or stale analysis output: {', '.join(stale)}", file=sys.stderr)
            return 1
        print("periodic-compute-cost: summary and figure are reproducible")
        return 0

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(summary_text, encoding="utf-8")
    FIGURE_PATH.write_bytes(image)
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {FIGURE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
