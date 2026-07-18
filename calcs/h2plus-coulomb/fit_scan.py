#!/usr/bin/env python3
"""Matched ANN fits of H2+ total and Coulomb-subtracted energies."""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import time
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SCAN = HERE / "h2plus-scan.csv"
HARTREE_TO_WAVENUMBER = 219_474.631_363_20
FOLD_SEED = 70_220
INIT_SEEDS = (11, 29, 47, 71, 101)
CUTOFFS_BOHR = (0.15, 0.25, 0.40, 0.70, 1.00, 1.50, 2.00, 3.00)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", type=Path, default=SCAN)
    parser.add_argument("--hidden", type=int, default=15)
    parser.add_argument("--steps", type=int, default=20_000)
    parser.add_argument("--learning-rate-start", type=float, default=1.0e-3)
    parser.add_argument("--learning-rate-end", type=float, default=1.0e-5)
    parser.add_argument("--input", choices=("raw", "log"), default="raw")
    parser.add_argument(
        "--target-scale", choices=("separate", "common-std"), default="separate"
    )
    parser.add_argument(
        "--selection", choices=("nested", "constant"), default="nested"
    )
    parser.add_argument("--tag", default="primary")
    return parser.parse_args()


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty table: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def stratified_folds(n_points: int) -> np.ndarray:
    """Assign one point per local five-point block to each fold."""
    rng = np.random.default_rng(FOLD_SEED)
    folds = np.empty(n_points, dtype=int)
    for start in range(0, n_points, 5):
        stop = min(start + 5, n_points)
        folds[start:stop] = rng.permutation(5)[: stop - start]
    return folds


def initialize(hidden: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    weights = []
    biases = []
    readouts = []
    offsets = []
    input_limit = math.sqrt(6.0 / (1 + hidden))
    output_limit = math.sqrt(6.0 / (hidden + 1))
    for seed in INIT_SEEDS:
        rng = np.random.default_rng(seed)
        weights.append(rng.uniform(-input_limit, input_limit, size=hidden))
        biases.append(np.zeros(hidden))
        readouts.append(rng.uniform(-output_limit, output_limit, size=hidden))
        offsets.append(0.0)

    base = (
        np.asarray(weights, dtype=np.float64),
        np.asarray(biases, dtype=np.float64),
        np.asarray(readouts, dtype=np.float64),
        np.asarray(offsets, dtype=np.float64),
    )
    # Scheme A and Scheme B start from bit-identical parameters for each seed.
    return tuple(np.concatenate((array, array), axis=0) for array in base)  # type: ignore[return-value]


def train_batch(
    x: np.ndarray,
    targets: np.ndarray,
    hidden: int,
    steps: int,
    learning_rate_start: float,
    learning_rate_end: float,
) -> tuple[tuple[np.ndarray, ...], np.ndarray, np.ndarray, np.ndarray]:
    """Train two targets x five seeds together with full-batch Adam."""
    weight, bias, readout, offset = initialize(hidden)
    params = [weight, bias, readout, offset]
    first_moments = [np.zeros_like(param) for param in params]
    second_moments = [np.zeros_like(param) for param in params]

    best_params = tuple(param.copy() for param in params)
    best_losses = np.full(targets.shape[0], np.inf)
    best_steps = np.zeros(targets.shape[0], dtype=int)
    final_losses = np.full(targets.shape[0], np.nan)

    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1.0e-8
    for step in range(1, steps + 1):
        weight, bias, readout, offset = params
        preactivation = x[None, :, None] * weight[:, None, :] + bias[:, None, :]
        activation = np.tanh(preactivation)
        prediction = np.einsum("bnh,bh->bn", activation, readout) + offset[:, None]
        error = prediction - targets
        losses = np.mean(error * error, axis=1)

        improved = losses < best_losses
        if np.any(improved):
            best_losses[improved] = losses[improved]
            best_steps[improved] = step
            for saved, current in zip(best_params, params):
                saved[improved] = current[improved]

        output_gradient = (2.0 / x.size) * error
        grad_readout = np.einsum("bn,bnh->bh", output_gradient, activation)
        grad_offset = np.sum(output_gradient, axis=1)
        grad_preactivation = (
            output_gradient[:, :, None]
            * readout[:, None, :]
            * (1.0 - activation * activation)
        )
        grad_weight = np.einsum("bnh,n->bh", grad_preactivation, x)
        grad_bias = np.sum(grad_preactivation, axis=1)
        gradients = [grad_weight, grad_bias, grad_readout, grad_offset]

        progress = (step - 1) / max(steps - 1, 1)
        learning_rate = learning_rate_end + 0.5 * (
            learning_rate_start - learning_rate_end
        ) * (1.0 + math.cos(math.pi * progress))

        for index, (param, gradient) in enumerate(zip(params, gradients)):
            first_moments[index] = (
                beta1 * first_moments[index] + (1.0 - beta1) * gradient
            )
            second_moments[index] = (
                beta2 * second_moments[index] + (1.0 - beta2) * gradient * gradient
            )
            first_unbiased = first_moments[index] / (1.0 - beta1**step)
            second_unbiased = second_moments[index] / (1.0 - beta2**step)
            param -= learning_rate * first_unbiased / (
                np.sqrt(second_unbiased) + epsilon
            )

        if not all(np.all(np.isfinite(param)) for param in params):
            raise FloatingPointError(f"non-finite parameter at training step {step}")

        if step == steps:
            final_losses = losses

    return best_params, best_losses, final_losses, best_steps


def predict(
    x: np.ndarray, params: tuple[np.ndarray, ...]
) -> np.ndarray:
    weight, bias, readout, offset = params
    activation = np.tanh(
        x[None, :, None] * weight[:, None, :] + bias[:, None, :]
    )
    return np.einsum("bnh,bh->bn", activation, readout) + offset[:, None]


def target_moments(
    total: np.ndarray, electronic: np.ndarray, mode: str
) -> tuple[float, float, float, float]:
    total_mean = float(np.mean(total))
    electronic_mean = float(np.mean(electronic))
    total_std = float(np.std(total))
    electronic_std = float(np.std(electronic))
    if min(total_std, electronic_std) <= 0.0:
        raise ValueError("constant target in a training fold")
    if mode == "common-std":
        electronic_std = total_std
    return total_mean, total_std, electronic_mean, electronic_std


def select_points(radius: np.ndarray, cutoff: float, mode: str) -> np.ndarray:
    eligible_indices = np.flatnonzero(radius >= cutoff - 1.0e-12)
    if mode == "nested":
        return radius >= cutoff - 1.0e-12

    constant_count = int(np.sum(radius >= max(CUTOFFS_BOHR) - 1.0e-12))
    local_indices = np.rint(
        np.linspace(0, eligible_indices.size - 1, constant_count)
    ).astype(int)
    chosen = eligible_indices[local_indices]
    if np.unique(chosen).size != constant_count:
        raise RuntimeError("constant-count selection produced duplicate points")
    mask = np.zeros(radius.size, dtype=bool)
    mask[chosen] = True
    return mask


def score_predictions(
    prediction_rows: list[dict[str, object]], cutoffs: tuple[float, ...]
) -> tuple[list[dict[str, object]], dict[str, object]]:
    metric_rows: list[dict[str, object]] = []
    lookup: dict[tuple[float, str, int], dict[str, float]] = {}

    for cutoff in cutoffs:
        for scheme in ("A", "B"):
            for seed in INIT_SEEDS:
                selected = [
                    row
                    for row in prediction_rows
                    if row["cutoff_bohr"] == cutoff
                    and row["scheme"] == scheme
                    and row["seed"] == seed
                ]
                selected.sort(key=lambda row: float(row["r_bohr"]))
                radius = np.asarray([row["r_bohr"] for row in selected], dtype=float)
                error = np.asarray([row["error_hartree"] for row in selected], dtype=float)
                absolute = np.abs(error)
                short_count = max(1, int(math.ceil(0.20 * error.size)))
                rmse_hartree = float(np.sqrt(np.mean(error * error)))
                weighted_rmse_hartree = float(
                    np.sqrt(np.trapezoid(error * error, radius) / (radius[-1] - radius[0]))
                )
                metrics = {
                    "cutoff_bohr": cutoff,
                    "scheme": scheme,
                    "seed": seed,
                    "n_points": error.size,
                    "rmse_cm-1": rmse_hartree * HARTREE_TO_WAVENUMBER,
                    "linear-r-weighted-rmse_cm-1": weighted_rmse_hartree
                    * HARTREE_TO_WAVENUMBER,
                    "mae_cm-1": float(np.mean(absolute)) * HARTREE_TO_WAVENUMBER,
                    "max-absolute-error_cm-1": float(np.max(absolute))
                    * HARTREE_TO_WAVENUMBER,
                    "shortest-quintile-rmse_cm-1": float(
                        np.sqrt(np.mean(error[:short_count] ** 2))
                    )
                    * HARTREE_TO_WAVENUMBER,
                }
                metric_rows.append(metrics)
                lookup[(cutoff, scheme, seed)] = metrics

    cutoff_summaries = []
    for cutoff in cutoffs:
        ratios = np.asarray(
            [
                lookup[(cutoff, "A", seed)]["rmse_cm-1"]
                / lookup[(cutoff, "B", seed)]["rmse_cm-1"]
                for seed in INIT_SEEDS
            ],
            dtype=float,
        )
        a_rmse = np.asarray(
            [lookup[(cutoff, "A", seed)]["rmse_cm-1"] for seed in INIT_SEEDS]
        )
        b_rmse = np.asarray(
            [lookup[(cutoff, "B", seed)]["rmse_cm-1"] for seed in INIT_SEEDS]
        )
        cutoff_summaries.append(
            {
                "cutoff_bohr": cutoff,
                "median_A_rmse_cm-1": float(np.median(a_rmse)),
                "median_B_rmse_cm-1": float(np.median(b_rmse)),
                "median_A_over_B": float(np.median(ratios)),
                "min_A_over_B": float(np.min(ratios)),
                "max_A_over_B": float(np.max(ratios)),
                "B_win_count": int(np.sum(ratios > 1.0)),
                "A_win_count": int(np.sum(ratios < 1.0)),
                "tie_count": int(np.sum(ratios == 1.0)),
            }
        )
    return metric_rows, {"cutoffs": cutoff_summaries}


def main() -> None:
    args = parse_args()
    data = np.genfromtxt(args.scan, delimiter=",", names=True)
    radius = np.asarray(data["r_bohr"], dtype=np.float64)
    total = np.asarray(data["total_hartree"], dtype=np.float64)
    repulsion = np.asarray(data["nuclear_repulsion_hartree"], dtype=np.float64)
    electronic = np.asarray(data["electronic_hartree"], dtype=np.float64)
    if not np.allclose(total, electronic + repulsion, rtol=0.0, atol=5.0e-15):
        raise RuntimeError("scan decomposition does not close at float64 precision")

    folds = stratified_folds(radius.size)
    fold_rows = [
        {"index": index, "r_bohr": point, "fold": int(folds[index])}
        for index, point in enumerate(radius)
    ]
    write_rows(HERE / "folds.csv", fold_rows)

    prediction_rows: list[dict[str, object]] = []
    training_rows: list[dict[str, object]] = []
    started = time.perf_counter()

    for cutoff in CUTOFFS_BOHR:
        eligible = select_points(radius, cutoff, args.selection)
        for fold in range(5):
            train_mask = eligible & (folds != fold)
            test_mask = eligible & (folds == fold)
            raw_train = radius[train_mask]
            raw_test = radius[test_mask]
            x_train_unscaled = np.log(raw_train) if args.input == "log" else raw_train
            x_test_unscaled = np.log(raw_test) if args.input == "log" else raw_test
            x_mean = float(np.mean(x_train_unscaled))
            x_std = float(np.std(x_train_unscaled))
            x_train = (x_train_unscaled - x_mean) / x_std
            x_test = (x_test_unscaled - x_mean) / x_std

            total_mean, total_std, electronic_mean, electronic_std = target_moments(
                total[train_mask], electronic[train_mask], args.target_scale
            )
            total_scaled = (total[train_mask] - total_mean) / total_std
            electronic_scaled = (
                electronic[train_mask] - electronic_mean
            ) / electronic_std
            targets = np.concatenate(
                (
                    np.repeat(total_scaled[None, :], len(INIT_SEEDS), axis=0),
                    np.repeat(electronic_scaled[None, :], len(INIT_SEEDS), axis=0),
                ),
                axis=0,
            )

            best_params, best_losses, final_losses, best_steps = train_batch(
                x_train,
                targets,
                args.hidden,
                args.steps,
                args.learning_rate_start,
                args.learning_rate_end,
            )
            scaled_prediction = predict(x_test, best_params)
            test_indices = np.flatnonzero(test_mask)

            for batch_index in range(2 * len(INIT_SEEDS)):
                scheme = "A" if batch_index < len(INIT_SEEDS) else "B"
                seed_index = batch_index % len(INIT_SEEDS)
                seed = INIT_SEEDS[seed_index]
                if scheme == "A":
                    reconstructed = (
                        scaled_prediction[batch_index] * total_std + total_mean
                    )
                else:
                    reconstructed = (
                        scaled_prediction[batch_index] * electronic_std
                        + electronic_mean
                        + repulsion[test_mask]
                    )

                for local_index, global_index in enumerate(test_indices):
                    error = float(reconstructed[local_index] - total[global_index])
                    prediction_rows.append(
                        {
                            "cutoff_bohr": cutoff,
                            "fold": fold,
                            "seed": seed,
                            "scheme": scheme,
                            "index": int(global_index),
                            "r_bohr": float(radius[global_index]),
                            "actual_total_hartree": float(total[global_index]),
                            "predicted_total_hartree": float(reconstructed[local_index]),
                            "error_hartree": error,
                        }
                    )
                training_rows.append(
                    {
                        "cutoff_bohr": cutoff,
                        "fold": fold,
                        "seed": seed,
                        "scheme": scheme,
                        "n_train": int(np.sum(train_mask)),
                        "n_test": int(np.sum(test_mask)),
                        "best_standardized_mse": float(best_losses[batch_index]),
                        "final_standardized_mse": float(final_losses[batch_index]),
                        "best_step": int(best_steps[batch_index]),
                    }
                )

        print(f"finished R_min={cutoff:.2f} a0", flush=True)

    metric_rows, summary = score_predictions(prediction_rows, CUTOFFS_BOHR)
    elapsed = time.perf_counter() - started
    summary["configuration"] = {
        "tag": args.tag,
        "scan": str(args.scan),
        "architecture": f"1-{args.hidden}-1 tanh MLP",
        "steps": args.steps,
        "optimizer": "full-batch Adam with cosine learning-rate decay",
        "learning_rate_start": args.learning_rate_start,
        "learning_rate_end": args.learning_rate_end,
        "input": args.input,
        "target_scale": args.target_scale,
        "selection": args.selection,
        "fold_seed": FOLD_SEED,
        "initialization_seeds": list(INIT_SEEDS),
        "cutoffs_bohr": list(CUTOFFS_BOHR),
        "numpy_version": np.__version__,
        "python_version": platform.python_version(),
        "machine": platform.machine(),
        "elapsed_seconds": elapsed,
    }

    write_rows(HERE / f"predictions-{args.tag}.csv", prediction_rows)
    write_rows(HERE / f"training-{args.tag}.csv", training_rows)
    write_rows(HERE / f"metrics-{args.tag}.csv", metric_rows)
    (HERE / f"summary-{args.tag}.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    print("R_min   RMSE A   RMSE B   median A/B   B wins")
    for row in summary["cutoffs"]:
        print(
            f"{row['cutoff_bohr']:5.2f}  "
            f"{row['median_A_rmse_cm-1']:7.2f}  "
            f"{row['median_B_rmse_cm-1']:7.2f}  "
            f"{row['median_A_over_B']:10.3f}   "
            f"{row['B_win_count']}/5"
        )
    print(f"elapsed: {elapsed:.1f} s")


if __name__ == "__main__":
    main()
