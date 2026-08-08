#!/usr/bin/env python3
"""Run the bounded periodic-compute-cost experiment matrix.

The child process (``probe_one.py``) owns the chemistry.  This parent owns
the preregistered panels, repetitions, process isolation, failure recording,
and append-only/resumable JSONL output.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable, Mapping, Sequence


PROTOCOL_ID = "periodic-compute-cost-phase1-v1"
BASIS = "def2-svp"
DEFAULT_TIMEOUT_SECONDS = 180.0
MAX_MEMORY_MB = 3000
EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = EXPERIMENT_DIR / "results" / "runs.jsonl"
PROBE = EXPERIMENT_DIR / "probe_one.py"

SINGLE_THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "BLIS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}


@dataclass(frozen=True)
class Element:
    symbol: str
    z: int
    spin: int


@dataclass(frozen=True)
class RunSpec:
    phase: str
    panel: str
    element: Element
    tier: str
    repeat: int

    @property
    def key(self) -> tuple[str, str, str, str, int]:
        """The durable identity used to resume an interrupted sweep."""

        return (PROTOCOL_ID, self.panel, self.element.symbol, self.tier, self.repeat)

    def metadata(self) -> dict[str, Any]:
        return {
            "protocol_id": PROTOCOL_ID,
            "phase": self.phase,
            "panel": self.panel,
            "symbol": self.element.symbol,
            "z": self.element.z,
            "spin": self.element.spin,
            "tier": self.tier,
            "basis": BASIS,
            "repeat": self.repeat,
        }


PANELS: dict[str, tuple[Element, ...]] = {
    "halogens": (
        Element("F", 9, 1),
        Element("Cl", 17, 1),
        Element("Br", 35, 1),
        Element("I", 53, 1),
    ),
    "alkaline_earths": (
        Element("Be", 4, 0),
        Element("Mg", 12, 0),
        Element("Ca", 20, 0),
        Element("Sr", 38, 0),
    ),
    "transition_neighbors": (
        Element("Cr", 24, 6),
        Element("Mn", 25, 5),
        Element("Fe", 26, 4),
        Element("Zn", 30, 0),
    ),
    "ecp_boundary": (
        Element("Kr", 36, 0),
        Element("Rb", 37, 1),
    ),
}

CORRELATION_PANELS = (
    "halogens",
    "alkaline_earths",
    "ecp_boundary",
)

DEEP_ELEMENTS: dict[str, tuple[str, ...]] = {
    "halogens": ("F", "Cl"),
    "alkaline_earths": ("Be", "Mg"),
}

EXPECTED_RUN_COUNTS = {"survey": 56, "correlation": 10, "deep": 4, "all": 70}


def explicit_electrons(element: Element) -> int:
    """Return electrons represented explicitly by the def2-SVP calculation."""

    return element.z - (28 if element.z >= 37 else 0)


def validate_panels() -> None:
    """Reject accidental panel duplication or impossible spin assignments."""

    seen_symbols: set[str] = set()
    for panel, elements in PANELS.items():
        if not elements:
            raise ValueError(f"panel {panel!r} is empty")
        for element in elements:
            if element.symbol in seen_symbols:
                raise ValueError(f"duplicate element across panels: {element.symbol}")
            seen_symbols.add(element.symbol)

            electrons = explicit_electrons(element)
            if electrons < element.spin or (electrons - element.spin) % 2:
                raise ValueError(
                    "invalid electron/spin parity for "
                    f"{element.symbol}: {electrons} explicit electrons, spin={element.spin}"
                )

    boundary = {
        element.symbol: explicit_electrons(element)
        for element in PANELS["ecp_boundary"]
    }
    if boundary != {"Kr": 36, "Rb": 9}:
        raise ValueError(f"unexpected Kr/Rb ECP boundary electron counts: {boundary!r}")


def _specs_for_phase(phase: str) -> Iterable[RunSpec]:
    if phase == "survey":
        for panel, elements in PANELS.items():
            for tier in ("UHF", "PBE"):
                for repeat in range(2):
                    for element in elements:
                        yield RunSpec(phase, panel, element, tier, repeat)
        return

    if phase == "correlation":
        for panel in CORRELATION_PANELS:
            for element in PANELS[panel]:
                yield RunSpec(phase, panel, element, "MP2", 0)
        return

    if phase == "deep":
        for panel, symbols in DEEP_ELEMENTS.items():
            elements_by_symbol = {element.symbol: element for element in PANELS[panel]}
            for symbol in symbols:
                yield RunSpec(phase, panel, elements_by_symbol[symbol], "CCSD(T)", 0)
        return

    raise ValueError(f"unknown phase: {phase}")


def build_plan(phase: str) -> list[RunSpec]:
    phases = ("survey", "correlation", "deep") if phase == "all" else (phase,)
    plan = [spec for selected in phases for spec in _specs_for_phase(selected)]

    seen: set[tuple[str, str, str, str, int]] = set()
    for spec in plan:
        if spec.key in seen:
            raise ValueError(f"duplicate planned run key: {spec.key!r}")
        seen.add(spec.key)
    if len(plan) != EXPECTED_RUN_COUNTS[phase]:
        raise ValueError(
            f"{phase} plan has {len(plan)} runs; expected {EXPECTED_RUN_COUNTS[phase]}"
        )
    return plan


def row_key(row: Mapping[str, Any], *, source: str) -> tuple[str, str, str, str, int]:
    fields = ("protocol_id", "panel", "symbol", "tier", "repeat")
    missing = [field for field in fields if field not in row]
    if missing:
        raise ValueError(f"{source} lacks resume-key fields: {', '.join(missing)}")
    repeat = row["repeat"]
    if isinstance(repeat, bool) or not isinstance(repeat, int):
        raise ValueError(f"{source} has a non-integer repeat: {repeat!r}")
    return (
        str(row["protocol_id"]),
        str(row["panel"]),
        str(row["symbol"]),
        str(row["tier"]),
        repeat,
    )


def load_completed(output: Path) -> set[tuple[str, str, str, str, int]]:
    """Load and validate durable run identities already in the JSONL file."""

    completed: set[tuple[str, str, str, str, int]] = set()
    if not output.exists():
        return completed

    with output.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise ValueError(f"{output}:{line_number} is blank")
            try:
                row = json.loads(line, parse_constant=_reject_nonstandard_json)
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"invalid JSON at {output}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{output}:{line_number} is not a JSON object")
            key = row_key(row, source=f"{output}:{line_number}")
            if key in completed:
                raise ValueError(f"duplicate run key at {output}:{line_number}: {key!r}")
            completed.add(key)
    return completed


def _reject_nonstandard_json(value: str) -> None:
    raise ValueError(f"non-standard JSON value {value}")


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _excerpt(value: str | bytes | None, limit: int = 4000) -> str | None:
    text = _as_text(value).strip()
    if not text:
        return None
    if len(text) <= limit:
        return text
    return text[:limit] + "...[truncated]"


def _failure_row(
    spec: RunSpec,
    *,
    outcome: str,
    elapsed: float,
    error: str,
    returncode: int | None = None,
    stdout: str | bytes | None = None,
    stderr: str | bytes | None = None,
) -> dict[str, Any]:
    electrons = explicit_electrons(spec.element)
    row = {
        **spec.metadata(),
        "charge": 0,
        "multiplicity": spec.element.spin + 1,
        "ecp": BASIS if spec.element.z >= 37 else None,
        "ecp_core_electrons": 28 if spec.element.z >= 37 else 0,
        "max_memory_mb": MAX_MEMORY_MB,
        "n_basis_functions": None,
        "n_electrons": electrons,
        "n_alpha": (electrons + spec.element.spin) // 2,
        "n_beta": (electrons - spec.element.spin) // 2,
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
        "wall_seconds": elapsed,
        "cpu_seconds": None,
        "peak_rss_mb": None,
        "timestamp": _utc_timestamp(),
        "outcome": outcome,
        "runner_wall_seconds": elapsed,
        "returncode": returncode,
        "error": error,
    }
    stdout_excerpt = _excerpt(stdout)
    stderr_excerpt = _excerpt(stderr)
    if stdout_excerpt is not None:
        row["stdout"] = stdout_excerpt
    if stderr_excerpt is not None:
        row["stderr"] = stderr_excerpt
    return row


def _probe_command(spec: RunSpec) -> list[str]:
    return [
        sys.executable,
        str(PROBE),
        "--symbol",
        spec.element.symbol,
        "--z",
        str(spec.element.z),
        "--spin",
        str(spec.element.spin),
        "--tier",
        spec.tier,
        "--basis",
        BASIS,
        "--panel",
        spec.panel,
        "--repeat",
        str(spec.repeat),
        "--phase",
        spec.phase,
    ]


def run_probe(spec: RunSpec, timeout: float) -> dict[str, Any]:
    env = os.environ.copy()
    env.update(SINGLE_THREAD_ENV)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            _probe_command(spec),
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - started
        return _failure_row(
            spec,
            outcome="timeout",
            elapsed=elapsed,
            error=f"probe exceeded {timeout:g} second timeout",
            stdout=exc.stdout,
            stderr=exc.stderr,
        )

    elapsed = time.monotonic() - started
    try:
        child_row = json.loads(completed.stdout, parse_constant=_reject_nonstandard_json)
    except (json.JSONDecodeError, ValueError) as exc:
        outcome = "crash" if completed.returncode != 0 else "malformed"
        return _failure_row(
            spec,
            outcome=outcome,
            elapsed=elapsed,
            error=(
                f"probe exited with status {completed.returncode}; stdout was not "
                f"exactly one JSON value: {exc}"
                if completed.returncode != 0
                else f"probe stdout was not exactly one JSON value: {exc}"
            ),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    if not isinstance(child_row, dict):
        outcome = "crash" if completed.returncode != 0 else "malformed"
        return _failure_row(
            spec,
            outcome=outcome,
            elapsed=elapsed,
            error=(
                f"probe exited with status {completed.returncode}; "
                "stdout JSON value was not an object"
                if completed.returncode != 0
                else "probe stdout JSON value was not an object"
            ),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    expected_metadata = spec.metadata()
    mismatches = {
        field: {"expected": expected, "reported": child_row.get(field)}
        for field, expected in expected_metadata.items()
        if child_row.get(field) != expected
    }
    reported_electrons = child_row.get("n_electrons")
    expected_electrons = explicit_electrons(spec.element)
    if reported_electrons is not None and reported_electrons != expected_electrons:
        mismatches["n_electrons"] = {
            "expected": expected_electrons,
            "reported": reported_electrons,
        }
    expected_ecp_core = 28 if spec.element.z >= 37 else 0
    reported_ecp_core = child_row.get("ecp_core_electrons")
    if reported_ecp_core is not None and reported_ecp_core != expected_ecp_core:
        mismatches["ecp_core_electrons"] = {
            "expected": expected_ecp_core,
            "reported": reported_ecp_core,
        }
    if not isinstance(child_row.get("outcome"), str):
        mismatches["outcome"] = {
            "expected": "string",
            "reported": child_row.get("outcome"),
        }
    if mismatches:
        return _failure_row(
            spec,
            outcome="malformed",
            elapsed=elapsed,
            error=f"probe record metadata mismatch: {mismatches!r}",
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    if completed.returncode != 0:
        return _failure_row(
            spec,
            outcome="crash",
            elapsed=elapsed,
            error=f"probe exited with status {completed.returncode}",
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    # The parent is authoritative for experimental identity; the child cannot
    # accidentally relabel a result and corrupt resumability.
    row = dict(child_row)
    row.update(spec.metadata())
    row["runner_wall_seconds"] = elapsed
    row["returncode"] = completed.returncode
    if "timestamp" not in row:
        row["timestamp"] = _utc_timestamp()
    stderr_excerpt = _excerpt(completed.stderr)
    if stderr_excerpt is not None:
        row["stderr"] = stderr_excerpt
    return row


def append_row(handle: Any, row: Mapping[str, Any]) -> None:
    handle.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=("survey", "correlation", "deep", "all"),
        default="all",
        help="bounded phase to run (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print pending run specifications without starting probes or writing output",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"append-only JSONL path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"per-probe timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS:g})",
    )
    args = parser.parse_args(argv)
    if not args.timeout > 0:
        parser.error("--timeout must be greater than zero")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    validate_panels()
    output = args.output.expanduser().resolve()
    completed = load_completed(output)
    plan = build_plan(args.phase)
    pending = [spec for spec in plan if spec.key not in completed]

    if args.dry_run:
        for spec in pending:
            print(json.dumps(spec.metadata(), sort_keys=True))
        print(
            f"dry run: {len(pending)} pending, {len(plan) - len(pending)} already recorded",
            file=sys.stderr,
        )
        return 0

    if not PROBE.is_file():
        raise FileNotFoundError(f"probe script not found: {PROBE}")
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("a", encoding="utf-8") as handle:
        for index, spec in enumerate(pending, start=1):
            print(
                f"[{index}/{len(pending)}] {spec.phase}/{spec.panel} "
                f"{spec.element.symbol} {spec.tier} repeat={spec.repeat}",
                file=sys.stderr,
                flush=True,
            )
            row = run_probe(spec, args.timeout)
            append_row(handle, row)

    print(
        f"complete: wrote {len(pending)} rows; "
        f"skipped {len(plan) - len(pending)} existing rows; output={output}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
