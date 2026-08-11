#!/usr/bin/env python3
"""How wide is the described SIREN convention's momentum recovery region in beta?

Follow-up to /posts/2026-07-19-the-momentum-control.html. Model, task, data,
seeds, initialization, and manual backprop are vendored from
downloads/siren-convention-momentum.py (2026-07-19) without algorithmic
change; unused code paths (probe outputs, group-isolated training, velocity
tracking) are removed, and the executed path is byte-identical in effect.

Protocol frozen in PREREGISTRATION.md (2026-08-11) before the canonical run.

Stage 1: beta in {0, 0.3, 0.6, 0.9, 0.99} x {described, official} x 35-point
grid logspace(1e-4, 10^-2.3, 0.05-decade spacing) x 3 reps.

Stage 2 (frozen refinement rule): per beta with at least one recovered stage-1
point (median test MSE over reps <= 1e-24), a 0.01-decade grid from 0.10
decades below the lowest recovered lr up to the lowest lr at which any
described rep diverged in stage 1 (inclusive; if no divergence was observed,
the window ends 0.15 decades above the lowest recovered point), both
conventions, same reps.

Run from this experiment's directory:
  python3 src/run_sweep.py

Writes results/stage1.json and results/stage2.json.
"""
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

OMEGA, C, WIDTH, NHID = 30.0, 6.0, 16, 3
EPOCHS = 20_000

BETAS = (0.0, 0.3, 0.6, 0.9, 0.99)
REPS = (0, 1, 2)
FLOOR_THRESHOLD = 1e-24
STAGE1_GRID = np.logspace(-4.0, -2.3, 35)  # 0.05-decade spacing
STAGE2_STEP = 0.01                          # decades
WORKERS = 8

HERE = Path(__file__).resolve().parent.parent
RESULTS = HERE / "results"


def json_number(value):
    if value is None:
        return None
    value = float(value)
    return value if np.isfinite(value) else None


# ---- K1, eq. (4) of Villatoro et al.
y_lo = lambda x: 0.5 * (6 * x - 2) ** 2 * np.sin(12 * x - 4) + 10 * x - 10
y_hi = lambda x: (6 * x - 2) ** 2 * np.sin(12 * x - 4)


def _y_norm_sq():
    q = np.linspace(0, 1, 2_000_001)
    return float(np.trapezoid(y_hi(q) ** 2, q))


Y_NORM_SQ = _y_norm_sq()
feats = lambda x: np.hstack([x, y_lo(x)])


def sobol1d(n, offset):
    out, f, i = np.zeros(n), 0.5, np.arange(offset, offset + n, dtype=np.uint64)
    while np.any(i > 0):
        out += f * (i & np.uint64(1)); i >>= np.uint64(1); f *= 0.5
    return out


def data(n_h, rep):
    rng = np.random.default_rng(1000 + 17 * n_h + rep)
    off = int(2 ** rng.integers(3, 12))
    x_tr = np.concatenate([sobol1d(n_h, off), [0.0, 1.0]])[:, None]
    return x_tr, rng.uniform(0, 1, n_h)[:, None]


def init_described(rng, d_in=2):
    P = {}
    a0 = 1.0 / d_in
    P["W0"] = rng.uniform(-a0, a0, (d_in, WIDTH)); P["b0"] = rng.uniform(-a0, a0, WIDTH)
    for l in range(1, NHID):
        a = np.sqrt(C / WIDTH)
        P[f"W{l}"] = rng.uniform(-a, a, (WIDTH, WIDTH)); P[f"b{l}"] = rng.uniform(-a, a, WIDTH)
    a = np.sqrt(C / WIDTH)
    P["Wo"] = rng.uniform(-a, a, (WIDTH, 1)); P["bo"] = np.zeros(1)
    b = np.sqrt(6.0 / (d_in + 1))
    P["Wlin"] = rng.uniform(-b, b, (d_in, 1)); P["blin"] = np.zeros(1)
    return P


def to_official(P):
    """Matched official parameterization; also scale biases for exact identity."""
    Q = {k: v.copy() for k, v in P.items()}
    for l in range(1, NHID):
        Q[f"W{l}"] = P[f"W{l}"] / OMEGA
        Q[f"b{l}"] = P[f"b{l}"] / OMEGA
    return Q


def forward(P, u, official, keep=False):
    s = OMEGA if official else 1.0
    cache = {"h0": u}
    z = OMEGA * (u @ P["W0"] + P["b0"]); h = np.sin(z)
    cache["z0"], cache["h1"] = z, h
    for l in range(1, NHID):
        z = s * (h @ P[f"W{l}"] + P[f"b{l}"]); h = np.sin(z)
        cache[f"z{l}"], cache[f"h{l+1}"] = z, h
    y = (h @ P["Wo"] + P["bo"] + u @ P["Wlin"] + P["blin"]).ravel()
    return (y, cache) if keep else y


def backward(P, cache, u, resid, official):
    s = OMEGA if official else 1.0
    g, d = {}, resid[:, None]
    g["Wlin"] = u.T @ d; g["blin"] = d.sum(0)
    g["Wo"] = cache[f"h{NHID}"].T @ d; g["bo"] = d.sum(0)
    dh = d @ P["Wo"].T
    for l in range(NHID - 1, 0, -1):
        da = dh * np.cos(cache[f"z{l}"]) * s
        g[f"W{l}"] = cache[f"h{l}"].T @ da; g[f"b{l}"] = da.sum(0)
        dh = da @ P[f"W{l}"].T
    da = dh * np.cos(cache["z0"]) * OMEGA
    g["W0"] = cache["h0"].T @ da; g["b0"] = da.sum(0)
    return g


def train(P, official, x_tr, x_te, lr, beta, epochs=EPOCHS):
    """Full-batch heavy-ball SGD: v <- beta v + g; theta <- theta - lr v.
    beta=0 reproduces siren-convention-sgd.py's plain-SGD update exactly.
    Returns the normalized test MSE, inf on any nonfinite value."""
    P = {k: v.copy() for k, v in P.items()}
    V = {k: np.zeros_like(v) for k, v in P.items()}
    u_tr, u_te = feats(x_tr), feats(x_te)
    t_tr, t_te = y_hi(x_tr).ravel(), y_hi(x_te).ravel()
    for _ in range(1, epochs + 1):
        yh, cache = forward(P, u_tr, official, keep=True)
        if not np.all(np.isfinite(yh)):
            return np.inf
        g = backward(P, cache, u_tr, 2.0 * (yh - t_tr), official)
        for k in P:
            gk = g[k].reshape(P[k].shape)
            V[k] = beta * V[k] + gk
            P[k] -= lr * V[k]
    yte = forward(P, u_te, official)
    if not np.all(np.isfinite(yte)):
        return np.inf
    return float(np.mean((yte - t_te) ** 2) / Y_NORM_SQ)


def run_cell(cell):
    beta, conv, lr, rep = cell
    x_tr, x_te = data(32, rep)
    Pd = init_described(np.random.default_rng(7000 + rep))
    P = Pd if conv == "described" else to_official(Pd)
    mse = train(P, conv == "official", x_tr, x_te, lr, beta)
    return dict(beta=beta, conv=conv, rep=rep, lr=float(lr),
                test=json_number(mse))


def run_grid(cells):
    rows = []
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        for i, row in enumerate(pool.map(run_cell, cells, chunksize=4), 1):
            rows.append(row)
            if i % 50 == 0 or i == len(cells):
                print(f"  {i}/{len(cells)} trainings done", flush=True)
    return rows


def median_test(rows, conv, lr):
    vals = [r["test"] for r in rows if r["conv"] == conv
            and abs(r["lr"] - lr) < 1e-15]
    if len(vals) != len(REPS) or any(v is None for v in vals):
        return None
    return float(np.median(vals))


def recovered_lrs(rows_b, lrs):
    """Lrs at which the described median test MSE is at or below the floor."""
    return [lr for lr in lrs
            if (m := median_test(rows_b, "described", lr)) is not None
            and m <= FLOOR_THRESHOLD]


def diverged_lrs(rows_b, lrs):
    """Lrs at which any described rep diverged."""
    return [lr for lr in lrs
            if any(r["test"] is None for r in rows_b
                   if r["conv"] == "described" and r["lr"] == lr)]


def main():
    t0 = time.time()
    env = dict(python=platform.python_version(), numpy=np.__version__,
               machine=platform.machine(), system=sys.platform)
    print("env:", env, flush=True)
    RESULTS.mkdir(exist_ok=True)

    cells = [(beta, conv, float(lr), rep)
             for beta in BETAS for conv in ("described", "official")
             for lr in STAGE1_GRID for rep in REPS]
    print(f"stage 1: {len(cells)} trainings", flush=True)
    stage1 = run_grid(cells)
    json.dump(dict(environment=env, protocol="stage1",
                   grid_decades=[-4.0, -2.3, 0.05], betas=list(BETAS),
                   reps=list(REPS), floor_threshold=FLOOR_THRESHOLD,
                   rows=stage1),
              open(RESULTS / "stage1.json", "w"))
    print(f"stage 1 done in {time.time()-t0:.0f}s", flush=True)

    # Stage 2, frozen refinement rule from PREREGISTRATION.md.
    cells2 = []
    windows = {}
    for beta in BETAS:
        rows_b = [r for r in stage1 if r["beta"] == beta]
        lrs = sorted({r["lr"] for r in rows_b})
        recovered = recovered_lrs(rows_b, lrs)
        if not recovered:
            windows[str(beta)] = None
            continue
        lo = np.log10(min(recovered)) - 0.10
        above = [lr for lr in diverged_lrs(rows_b, lrs) if np.log10(lr) > lo]
        # No divergence above: 0.15 decades above the lowest recovered point.
        hi = np.log10(min(above)) if above else np.log10(min(recovered)) + 0.15
        n = int(round((hi - lo) / STAGE2_STEP)) + 1
        grid = np.logspace(lo, hi, n)
        windows[str(beta)] = [float(lo), float(hi), len(grid)]
        for conv in ("described", "official"):
            for lr in grid:
                for rep in REPS:
                    cells2.append((beta, conv, float(lr), rep))
    print(f"stage 2: {len(cells2)} trainings, windows {windows}", flush=True)
    stage2 = run_grid(cells2)
    json.dump(dict(environment=env, protocol="stage2",
                   step_decades=STAGE2_STEP, windows=windows,
                   floor_threshold=FLOOR_THRESHOLD, rows=stage2),
              open(RESULTS / "stage2.json", "w"))
    print(f"stage 2 done in {time.time()-t0:.0f}s total", flush=True)

    # Console summary (analysis proper lives in generate-metrics.mjs).
    for beta in BETAS:
        rows_b = [r for r in stage1 if r["beta"] == beta]
        lrs = sorted({r["lr"] for r in rows_b})
        rec = recovered_lrs(rows_b, lrs)
        div = next(iter(diverged_lrs(rows_b, lrs)), None)
        print(f"beta={beta:<5} recovered={[f'{lr:.3e}' for lr in rec]} "
              f"first_divergence={div and f'{div:.3e}'}", flush=True)


if __name__ == "__main__":
    main()
