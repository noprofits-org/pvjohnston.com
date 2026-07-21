"""Force-training sweep on the H2+ Coulomb-subtraction crossover.

Frozen protocol (declared before any result was viewed):

System        : minimal-basis LCAO H2+ curve from h2plus_model.py, 401 points
                geometrically spaced over R in [0.15, 20] bohr.
Two schemes   : A fits the total potential V(R) directly; B fits the electronic
                energy E_el(R) = V - 1/R and restores the exact 1/R (and its
                exact 1/R^2 force) before scoring.
Two losses    : energy-only  L = MSE(value);
                energy+force L = MSE(value) + LAMBDA * MSE(slope), both in the
                scheme's own standardised space, LAMBDA = 1.0.
Network       : one hidden layer, 15 tanh units, linear readout, float64,
                Xavier-uniform weights, zero biases.
Optimiser     : full-batch Adam (0.9, 0.999, 1e-8), 20000 steps, cosine learning
                rate 1e-3 -> 1e-5, no regularisation. The checkpoint with the
                lowest training objective is retained.
Folds/seeds   : 5 stratified folds fixed once on the full ordered grid with a
                seed-70220 permutation inside each consecutive 5-point block;
                initialisation seeds 11, 29, 47, 71, 101. Within a fold and seed,
                schemes A and B start from bit-identical weights, and the two
                losses reuse those same weights.
Cutoffs       : retain points with R >= R_min for R_min in
                {0.15,0.25,0.40,0.70,1.00,1.50,2.00,3.00} bohr; folds preserved.
Metric        : pooled out-of-fold energy RMSE (cm^-1) per seed; A/B ratio per
                seed = RMSE_A / RMSE_B; median over the 5 seeds. The crossover
                cutoff is the smallest R_min whose median A/B ratio <= 1.
Hypothesis    : under energy+force training the crossover cutoff is LARGER than
                under energy-only training.
Falsifier     : the first cutoff with median A/B <= 1 is unchanged or smaller
                under the energy+force loss.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

import h2plus_model as h2

HARTREE_TO_CM = 219474.6313632  # CODATA hartree -> cm^-1

HIDDEN = 15
STEPS = 20000
LR_HIGH = 1e-3
LR_LOW = 1e-5
LAMBDA = 1.0
FOLD_SEED = 70220
INIT_SEEDS = [11, 29, 47, 71, 101]
CUTOFFS = [0.15, 0.25, 0.40, 0.70, 1.00, 1.50, 2.00, 3.00]
N_POINTS = 401
R_MIN_GRID = 0.15
R_MAX_GRID = 20.0
N_FOLDS = 5


def build_grid():
    R = np.geomspace(R_MIN_GRID, R_MAX_GRID, N_POINTS)
    V = h2.potential(R)
    E_el = h2.electronic_energy(R)
    dV = h2.d_potential(R)
    dE_el = h2.d_electronic_energy(R)
    return R, V, E_el, dV, dE_el


def assign_folds():
    rng = np.random.default_rng(FOLD_SEED)
    folds = np.empty(N_POINTS, dtype=int)
    for start in range(0, N_POINTS, N_FOLDS):
        block = np.arange(start, min(start + N_FOLDS, N_POINTS))
        perm = rng.permutation(N_FOLDS)
        for j, idx in enumerate(block):
            folds[idx] = perm[j]
    return folds


def init_params(seed):
    rng = np.random.default_rng(seed)
    limit1 = np.sqrt(6.0 / (1 + HIDDEN))
    limit2 = np.sqrt(6.0 / (HIDDEN + 1))
    W1 = rng.uniform(-limit1, limit1, size=HIDDEN)
    b1 = np.zeros(HIDDEN)
    w2 = rng.uniform(-limit2, limit2, size=HIDDEN)
    b2 = 0.0
    return {"W1": W1, "b1": b1, "w2": w2, "b2": b2}


def forward(params, u):
    """Return value g(u), slope g'(u), and cached activations for a batch u."""
    z = np.outer(u, params["W1"]) + params["b1"]  # (N,H)
    a = np.tanh(z)
    d = 1.0 - a * a
    g = a @ params["w2"] + params["b2"]  # (N,)
    gp = (d * params["W1"]) @ params["w2"]  # (N,)
    return g, gp, a, d


def loss_and_grad(params, u, t_std, s_target, lam):
    """Objective L = mean(rv^2) + lam*mean(rs^2) with analytic gradients."""
    N = u.shape[0]
    g, gp, a, d = forward(params, u)
    rv = g - t_std
    rs = gp - s_target
    loss = float(np.mean(rv * rv) + lam * np.mean(rs * rs))

    W1, w2 = params["W1"], params["w2"]
    # value-term parameter gradients
    cv = (2.0 / N) * rv  # (N,)
    gW1_v = cv[:, None] * (w2 * d) * u[:, None]
    gb1_v = cv[:, None] * (w2 * d)
    gw2_v = cv[:, None] * a
    gb2_v = cv.sum()

    grad = {
        "W1": gW1_v.sum(0),
        "b1": gb1_v.sum(0),
        "w2": gw2_v.sum(0),
        "b2": gb2_v,
    }

    if lam != 0.0:
        cs = (2.0 * lam / N) * rs  # (N,)
        # dgp/dW1_h = w2_h d_h (1 - 2 W1_h a_h u)
        dgp_W1 = (w2 * d) * (1.0 - 2.0 * (W1 * a) * u[:, None])
        # dgp/db1_h = -2 w2_h W1_h a_h d_h
        dgp_b1 = -2.0 * (w2 * W1) * a * d
        # dgp/dw2_h = W1_h d_h
        dgp_w2 = W1 * d
        grad["W1"] += (cs[:, None] * dgp_W1).sum(0)
        grad["b1"] += (cs[:, None] * dgp_b1).sum(0)
        grad["w2"] += (cs[:, None] * dgp_w2).sum(0)
        # dgp/db2 = 0

    return loss, grad


def _finite_diff_check():
    """Verify analytic gradients against central finite differences."""
    rng = np.random.default_rng(0)
    params = {
        "W1": rng.normal(size=HIDDEN),
        "b1": rng.normal(size=HIDDEN),
        "w2": rng.normal(size=HIDDEN),
        "b2": float(rng.normal()),
    }
    u = rng.uniform(-1.5, 1.5, size=17)
    t_std = rng.normal(size=17)
    s_target = rng.normal(size=17)
    for lam in (0.0, 1.0):
        _, grad = loss_and_grad(params, u, t_std, s_target, lam)
        eps = 1e-6
        max_rel = 0.0
        for key in ("W1", "b1", "w2", "b2"):
            arr = np.atleast_1d(params[key]).astype(float)
            for i in range(arr.size):
                orig = arr[i]
                arr[i] = orig + eps
                p2 = dict(params)
                p2[key] = arr.copy() if key != "b2" else float(arr[0])
                lp, _ = loss_and_grad(p2, u, t_std, s_target, lam)
                arr[i] = orig - eps
                p2[key] = arr.copy() if key != "b2" else float(arr[0])
                lm, _ = loss_and_grad(p2, u, t_std, s_target, lam)
                arr[i] = orig
                num = (lp - lm) / (2 * eps)
                ana = grad[key] if key == "b2" else grad[key][i]
                rel = abs(num - ana) / (abs(num) + 1e-9)
                max_rel = max(max_rel, rel)
        assert max_rel < 1e-5, f"gradient check failed (lam={lam}): {max_rel:.2e}"
    return True


def adam_train(params0, u, t_std, s_target, lam):
    p = {k: (np.array(v, dtype=float) if k != "b2" else float(v))
         for k, v in params0.items()}
    m = {k: np.zeros_like(np.atleast_1d(p[k]).astype(float)) for k in p}
    v = {k: np.zeros_like(np.atleast_1d(p[k]).astype(float)) for k in p}
    b1c, b2c, eps = 0.9, 0.999, 1e-8
    best_loss, best_p = np.inf, None
    for step in range(1, STEPS + 1):
        lr = LR_LOW + 0.5 * (LR_HIGH - LR_LOW) * (1 + np.cos(np.pi * (step - 1) / (STEPS - 1)))
        loss, grad = loss_and_grad(p, u, t_std, s_target, lam)
        if loss < best_loss:
            best_loss = loss
            best_p = {k: (p[k].copy() if k != "b2" else p[k]) for k in p}
        for k in p:
            gk = np.atleast_1d(grad[k]).astype(float)
            m[k] = b1c * m[k] + (1 - b1c) * gk
            v[k] = b2c * v[k] + (1 - b2c) * (gk * gk)
            mhat = m[k] / (1 - b1c ** step)
            vhat = v[k] / (1 - b2c ** step)
            upd = lr * mhat / (np.sqrt(vhat) + eps)
            if k == "b2":
                p[k] = p[k] - float(upd[0])
            else:
                p[k] = p[k] - upd
    return best_p


# ---- batched trainer over N independent networks (seed x fold) -------------
# Each network n has its own weights, its own standardisation, and a weight
# mask selecting its training points. The per-network gradients are identical
# in form to loss_and_grad above (cross-checked in _batched_consistency_check).

def _bvm(c, Tn):
    """Batched vector-matrix product: c (N,M), Tn (N,M,H) -> (N,H)."""
    return np.matmul(c[:, None, :], Tn)[:, 0, :]


def batched_forward(P, U):
    """P: dict of (N,H) arrays and (N,) b2; U: (N,M). Returns g,gp,a,d."""
    z = U[:, :, None] * P["W1"][:, None, :] + P["b1"][:, None, :]  # (N,M,H)
    a = np.tanh(z)
    d = 1.0 - a * a
    g = np.matmul(a, P["w2"][:, :, None])[:, :, 0] + P["b2"][:, None]
    gp = np.matmul(d, (P["w2"] * P["W1"])[:, :, None])[:, :, 0]
    return g, gp, a, d


def batched_loss_grad(P, U, T, S, W, lam):
    """Weighted objective per network; W (N,M) sums to 1 per network row."""
    g, gp, a, d = batched_forward(P, U)
    rv = g - T
    rs = gp - S
    loss = np.sum(W * (rv * rv + lam * rs * rs), axis=1)  # (N,)
    W1, w2 = P["W1"], P["w2"]
    w2d = w2[:, None, :] * d  # (N,M,H)
    cv = 2.0 * W * rv  # (N,M)
    gW1 = _bvm(cv, w2d * U[:, :, None])
    gb1 = _bvm(cv, w2d)
    gw2 = _bvm(cv, a)
    gb2 = np.sum(cv, axis=1)
    if lam != 0.0:
        cs = 2.0 * lam * W * rs  # (N,M)
        term_W1 = w2d * (1.0 - 2.0 * (W1[:, None, :] * a) * U[:, :, None])
        gW1 = gW1 + _bvm(cs, term_W1)
        gb1 = gb1 + _bvm(cs, -2.0 * (w2 * W1)[:, None, :] * a * d)
        gw2 = gw2 + _bvm(cs, d * W1[:, None, :])
    return loss, {"W1": gW1, "b1": gb1, "w2": gw2, "b2": gb2}


def batched_adam(P0, U, T, S, W, lam):
    P = {k: np.array(v, dtype=float) for k, v in P0.items()}
    m = {k: np.zeros_like(P[k]) for k in P}
    v = {k: np.zeros_like(P[k]) for k in P}
    b1c, b2c, eps = 0.9, 0.999, 1e-8
    best_loss = np.full(P["W1"].shape[0], np.inf)
    best_P = {k: P[k].copy() for k in P}
    for step in range(1, STEPS + 1):
        lr = LR_LOW + 0.5 * (LR_HIGH - LR_LOW) * (1 + np.cos(np.pi * (step - 1) / (STEPS - 1)))
        loss, grad = batched_loss_grad(P, U, T, S, W, lam)
        improved = loss < best_loss
        if improved.any():
            best_loss = np.where(improved, loss, best_loss)
            for k in P:
                idx = improved
                if P[k].ndim == 2:
                    best_P[k][idx, :] = P[k][idx, :]
                else:
                    best_P[k][idx] = P[k][idx]
        for k in P:
            gk = grad[k]
            m[k] = b1c * m[k] + (1 - b1c) * gk
            v[k] = b2c * v[k] + (1 - b2c) * (gk * gk)
            mhat = m[k] / (1 - b1c ** step)
            vhat = v[k] / (1 - b2c ** step)
            P[k] = P[k] - lr * mhat / (np.sqrt(vhat) + eps)
    return best_P


def run_cutoff(scheme, lam, cutoff, folds, R, targets, slopes):
    """Return {seed: pooled out-of-fold energy RMSE cm^-1} for one cutoff."""
    elig = R >= cutoff
    Rc, fc = R[elig], folds[elig]
    tc, sc = targets[elig], slopes[elig]
    Vtrue = h2.potential(Rc)
    M = Rc.shape[0]
    seeds = INIT_SEEDS
    nets = [(si, f) for si in range(len(seeds)) for f in range(N_FOLDS)]
    Nn = len(nets)
    W1 = np.empty((Nn, HIDDEN)); b1 = np.zeros((Nn, HIDDEN))
    w2 = np.empty((Nn, HIDDEN)); b2 = np.zeros(Nn)
    U = np.empty((Nn, M)); T = np.empty((Nn, M))
    S = np.empty((Nn, M)); Wt = np.zeros((Nn, M))
    meta = []
    for n, (si, f) in enumerate(nets):
        p0 = init_params(seeds[si])  # init depends on seed only
        W1[n], b1[n], w2[n], b2[n] = p0["W1"], p0["b1"], p0["w2"], p0["b2"]
        train = fc != f
        mux, sigx = Rc[train].mean(), Rc[train].std()
        mut, sigt = tc[train].mean(), tc[train].std()
        U[n] = (Rc - mux) / sigx
        T[n] = (tc - mut) / sigt
        S[n] = sc * sigx / sigt
        Wt[n, train] = 1.0 / train.sum()
        meta.append((si, f, mut, sigt))
    P0 = {"W1": W1, "b1": b1, "w2": w2, "b2": b2}
    P = batched_adam(P0, U, T, S, Wt, lam)
    g, _, _, _ = batched_forward(P, U)
    preds = {si: np.full(M, np.nan) for si in range(len(seeds))}
    for n, (si, f, mut, sigt) in enumerate(meta):
        test = fc == f
        t_pred = g[n, test] * sigt + mut
        V_pred = t_pred if scheme == "A" else t_pred + 1.0 / Rc[test]
        preds[si][test] = V_pred
    out = {}
    for si, seed in enumerate(seeds):
        rmse_ha = float(np.sqrt(np.mean((preds[si] - Vtrue) ** 2)))
        out[seed] = rmse_ha * HARTREE_TO_CM
    return out


def _batched_consistency_check():
    """Batched forward/grad must match the verified unbatched loss_and_grad."""
    rng = np.random.default_rng(3)
    N, M = 4, 11
    P = {"W1": rng.normal(size=(N, HIDDEN)), "b1": rng.normal(size=(N, HIDDEN)),
         "w2": rng.normal(size=(N, HIDDEN)), "b2": rng.normal(size=N)}
    U = rng.uniform(-1.5, 1.5, size=(N, M))
    T = rng.normal(size=(N, M)); S = rng.normal(size=(N, M))
    W = np.abs(rng.normal(size=(N, M))); W /= W.sum(1, keepdims=True)
    for lam in (0.0, 1.0):
        bl, bg = batched_loss_grad(P, U, T, S, W, lam)
        for n in range(N):
            pn = {"W1": P["W1"][n], "b1": P["b1"][n], "w2": P["w2"][n], "b2": float(P["b2"][n])}
            # replicate weighted objective with an equivalent unbatched form
            g, gp, a, d = forward(pn, U[n])
            rv, rs = g - T[n], gp - S[n]
            loss_n = float(np.sum(W[n] * (rv * rv + lam * rs * rs)))
            assert abs(loss_n - bl[n]) < 1e-9, (loss_n, bl[n])
        # finite-difference the batched gradient for net 0
        eps = 1e-6
        for k in ("W1", "b1", "w2", "b2"):
            arr = np.atleast_1d(P[k][0]).astype(float)
            for i in range(arr.size):
                P2 = {kk: P[kk].copy() for kk in P}
                orig = P2[k][0][i] if P[k].ndim == 2 else P2[k][0]
                if P[k].ndim == 2:
                    P2[k][0][i] = orig + eps
                    lp = batched_loss_grad(P2, U, T, S, W, lam)[0][0]
                    P2[k][0][i] = orig - eps
                    lm = batched_loss_grad(P2, U, T, S, W, lam)[0][0]
                    ana = bg[k][0][i]
                else:
                    P2[k][0] = orig + eps
                    lp = batched_loss_grad(P2, U, T, S, W, lam)[0][0]
                    P2[k][0] = orig - eps
                    lm = batched_loss_grad(P2, U, T, S, W, lam)[0][0]
                    ana = bg[k][0]
                num = (lp - lm) / (2 * eps)
                assert abs(num - ana) < 1e-5 * (abs(num) + 1e-6), (k, i, num, ana)
    return True


def main(argv):
    check = "--check" in argv
    if check:
        assert h2._self_test()
        assert _finite_diff_check()
        assert _batched_consistency_check()
        print("run_experiment self-tests passed")
        return 0

    # verification gates before the sweep
    h2._self_test()
    _finite_diff_check()
    _batched_consistency_check()

    R, V, E_el, dV, dE_el = build_grid()
    folds = assign_folds()
    scheme_targets = {"A": (V, dV), "B": (E_el, dE_el)}

    t0 = time.time()
    rmse = {}  # rmse[loss][scheme][seed][cutoff]
    for loss_name, lam in (("energy", 0.0), ("energy_force", LAMBDA)):
        rmse[loss_name] = {}
        for scheme in ("A", "B"):
            targets, slopes = scheme_targets[scheme]
            rmse[loss_name][scheme] = {seed: {} for seed in INIT_SEEDS}
            for cutoff in CUTOFFS:
                per_seed = run_cutoff(scheme, lam, cutoff, folds, R, targets, slopes)
                for seed in INIT_SEEDS:
                    rmse[loss_name][scheme][seed][cutoff] = per_seed[seed]
                print(f"[{time.time()-t0:6.1f}s] {loss_name} scheme {scheme} "
                      f"cutoff {cutoff:.2f} done", flush=True)

    # derive per-cutoff median A/B ratios and crossover cutoffs
    derived = {}
    for loss_name in rmse:
        per_cutoff = {}
        for cutoff in CUTOFFS:
            ratios = []
            rmse_a_list, rmse_b_list = [], []
            for seed in INIT_SEEDS:
                a = rmse[loss_name]["A"][seed][cutoff]
                b = rmse[loss_name]["B"][seed][cutoff]
                ratios.append(a / b)
                rmse_a_list.append(a)
                rmse_b_list.append(b)
            per_cutoff[cutoff] = {
                "median_ab_ratio": float(np.median(ratios)),
                "median_rmse_a_cm": float(np.median(rmse_a_list)),
                "median_rmse_b_cm": float(np.median(rmse_b_list)),
                "ratios": [float(x) for x in ratios],
            }
        crossover = None
        for cutoff in CUTOFFS:
            if per_cutoff[cutoff]["median_ab_ratio"] <= 1.0:
                crossover = cutoff
                break
        derived[loss_name] = {"per_cutoff": per_cutoff, "crossover_cutoff": crossover}

    out = {
        "protocol": {
            "model": "minimal-basis LCAO H2+ (zeta=1)",
            "hidden_units": HIDDEN,
            "activation": "tanh",
            "steps": STEPS,
            "lr_high": LR_HIGH,
            "lr_low": LR_LOW,
            "lambda_force": LAMBDA,
            "fold_seed": FOLD_SEED,
            "init_seeds": INIT_SEEDS,
            "cutoffs_bohr": CUTOFFS,
            "n_points": N_POINTS,
            "r_grid_bohr": [R_MIN_GRID, R_MAX_GRID],
            "n_folds": N_FOLDS,
            "hartree_to_cm": HARTREE_TO_CM,
            "hypothesis": "energy+force crossover cutoff is larger than energy-only",
            "falsifier": "energy+force crossover unchanged or smaller",
        },
        "rmse_cm": {
            ln: {sc: {str(sd): {f"{c:.2f}": rmse[ln][sc][sd][c] for c in CUTOFFS}
                     for sd in INIT_SEEDS}
                 for sc in ("A", "B")}
            for ln in rmse
        },
        "derived": {
            ln: {
                "crossover_cutoff": derived[ln]["crossover_cutoff"],
                "per_cutoff": {f"{c:.2f}": derived[ln]["per_cutoff"][c] for c in CUTOFFS},
            }
            for ln in derived
        },
    }
    out_path = Path(__file__).parent / "results.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out_path} in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
