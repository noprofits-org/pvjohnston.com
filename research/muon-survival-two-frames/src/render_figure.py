#!/usr/bin/env python3
"""Render or byte-check the registered 1200x630 two-panel PNG."""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
from typing import Any, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from analyze import validate_analysis_result
from contract import EXPERIMENT_DIR, REPOSITORY_ROOT, ContractError, load_json, write_bytes_exclusive


WIDTH_PX = 1200
HEIGHT_PX = 630
DPI = 100


def _array(result: Mapping[str, Any], section: str, key: str, size: int) -> np.ndarray:
    array = np.asarray(result[section][key], dtype=np.float64)
    if array.shape != (size,) or not bool(np.all(np.isfinite(array))):
        raise ContractError(f"figure input {section}.{key} is invalid")
    return array


def render_png_bytes(result: Mapping[str, Any]) -> bytes:
    if result.get("experiment") != "muon-survival-two-frames" or result.get("post_type") != "understanding":
        raise ContractError("figure input identity mismatch")
    grid = np.asarray(result.get("grid_m"), dtype=np.float64)
    if grid.ndim != 1 or grid.size < 2 or not bool(np.all(np.isfinite(grid))):
        raise ContractError("figure grid is invalid")
    size = grid.size
    detector_survival = _array(result, "detector_frame", "survival_probability", size)
    muon_survival = _array(result, "muon_frame", "survival_probability", size)
    empirical = _array(result, "empirical", "survival_probability", size)
    counterfactual = result["same_speed_no_lifetime_dilation_counterfactual"]
    if counterfactual.get("label") != "same-speed, no-lifetime-dilation counterfactual":
        raise ContractError("counterfactual figure label mismatch")
    counter_survival = _array(result, "same_speed_no_lifetime_dilation_counterfactual", "survival_probability", size)
    focal_index = result.get("focal", {}).get("index")
    if not isinstance(focal_index, int) or not 0 <= focal_index < size:
        raise ContractError("figure focal index is invalid")
    detector_exponent = _array(result, "detector_frame", "decay_exponent", size)[focal_index]
    muon_exponent = _array(result, "muon_frame", "decay_exponent", size)[focal_index]

    with plt.rc_context({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.labelcolor": "#111111",
        "axes.edgecolor": "#111111",
        "xtick.color": "#111111",
        "ytick.color": "#111111",
        "text.color": "#111111",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    }):
        figure, axes = plt.subplots(1, 2, figsize=(WIDTH_PX / DPI, HEIGHT_PX / DPI), dpi=DPI)
        left, right = axes
        distance_km = grid / 1000.0
        left.plot(distance_km, detector_survival, color="#005ea8", linewidth=2.6, label="analytic: detector frame")
        left.plot(distance_km, muon_survival, color="#7a3db8", linewidth=1.4, linestyle=(0, (2, 2)), label="analytic: muon frame (coincident)")
        left.step(distance_km, empirical, where="post", color="#147d64", linewidth=1.4, alpha=0.9, label="empirical decay-law check")
        left.plot(distance_km, counter_survival, color="#b33a3a", linewidth=2.0, linestyle="--", label="same-speed, no-lifetime-dilation counterfactual")
        left.set_xlabel("Laboratory path (km)")
        left.set_ylabel("Survival probability")
        left.set_ylim(-0.02, 1.04)
        left.grid(True, color="#d9d9d9", linewidth=0.7)
        left.legend(loc="upper right", frameon=True, fontsize=8)
        left.text(0.02, 0.04, "A", transform=left.transAxes, fontweight="bold", fontsize=13)

        right.scatter([detector_exponent], [1.0], color="#005ea8", s=90, zorder=3)
        right.scatter([muon_exponent], [0.0], color="#7a3db8", marker="D", s=70, zorder=3)
        right.plot([detector_exponent, muon_exponent], [1.0, 0.0], color="#777777", linewidth=1.0)
        right.set_yticks([0.0, 1.0], ["muon: $t_M/\\tau_0$", "detector: $t_D/(\\gamma\\tau_0)$"])
        right.set_xlabel("Dimensionless decay exponent at the focal path")
        padding = max(abs(float(detector_exponent)), abs(float(muon_exponent)), 1e-12) * 0.12
        right.set_xlim(min(detector_exponent, muon_exponent) - padding, max(detector_exponent, muon_exponent) + padding)
        right.set_ylim(-0.55, 1.55)
        right.grid(True, axis="x", color="#d9d9d9", linewidth=0.7)
        right.text(0.03, 0.08, "B", transform=right.transAxes, fontweight="bold", fontsize=13)

        figure.subplots_adjust(left=0.075, right=0.98, bottom=0.15, top=0.96, wspace=0.34)
        buffer = BytesIO()
        figure.canvas.print_png(
            buffer,
            metadata={"Software": "Matplotlib 3.11.1", "Title": "One muon, two frames"},
        )
        plt.close(figure)
    payload = buffer.getvalue()
    with Image.open(BytesIO(payload)) as image:
        if image.size != (WIDTH_PX, HEIGHT_PX) or image.format != "PNG":
            raise ContractError("rendered figure dimensions or format mismatch")
    return payload


def write_or_check_png(path: Path, payload: bytes, *, check: bool) -> None:
    if check:
        if not path.is_file() or path.is_symlink() or path.read_bytes() != payload:
            raise ContractError("registered PNG is missing or stale")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        write_bytes_exclusive(path, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = load_json(EXPERIMENT_DIR / "results/summary.json")
    validate_analysis_result(result, verify_provenance=True, enforce_frozen_inputs=True)
    payload = render_png_bytes(result)
    output = REPOSITORY_ROOT / "images/muon-survival-two-frames-hero.png"
    write_or_check_png(output, payload, check=args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
