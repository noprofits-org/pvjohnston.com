"""
Does the SIREN specification degeneracy cost accuracy on K1, once the
learning rate is tuned per configuration?

Next step from /posts/2026-07-17-the-siren-that-was-a-straight-line.html.

Setting: Villatoro, Geraci & Schiavazzi (J. Comput. Phys. 565 (2026) 115170)
test case K1 -- the Forrester pair, eq. (4) -- with the exact LF function,
no coordinate encoding, and a 3x16 nonlinear correlation subnetwork built as
a SIREN under each of three initialization schemes.

NumPy only; manual backprop; CPU.
"""

import numpy as np
import sys, platform, json

print("env:", platform.python_version(), platform.machine(), sys.platform,
      "| numpy", np.__version__)

W0_OMEGA = 30.0          # paper: omega_0 = 30
C = 6.0                  # paper: c = 6
WIDTH = 16               # paper: 3x16 nonlinear correlation subnetwork
NHID = 3
EPOCHS = 20_000
REPS = 4                 # paper: 4 independent repetitions
LRS = np.logspace(-5, -3, 9)   # paper Table 1: lr ~ loguniform(log([1e-5, 1e-3]))
NHS = (8, 16, 32)        # paper: HF Sobol' sets of size {8,16,32} + boundary points
SCHEMES = ("described", "official", "specified")


# ---------------------------------------------------------------- K1, eq. (4)
def y_lo(x):
    return 0.5 * (6 * x - 2) ** 2 * np.sin(12 * x - 4) + 10 * x - 10


def y_hi(x):
    return (6 * x - 2) ** 2 * np.sin(12 * x - 4)


# ||y_H||^2 over the input domain, by fine quadrature (normalizer for the MSE)
_q = np.linspace(0.0, 1.0, 2_000_001)
Y_NORM_SQ = np.trapezoid(y_hi(_q) ** 2, _q)


def sobol1d(n, offset):
    """1D Sobol' == van der Corput radical inverse, base 2, at a given offset."""
    idx = np.arange(offset, offset + n, dtype=np.uint64)
    out = np.zeros(n)
    f, i = 0.5, idx.copy()
    while np.any(i > 0):
        out += f * (i & np.uint64(1))
        i >>= np.uint64(1)
        f *= 0.5
    return out


def make_data(n_h, rep, rng):
    # "Repeated Sobol' sequences are extracted using randomized power-of-two offsets"
    offset = int(2 ** rng.integers(3, 12))
    xs = sobol1d(n_h, offset)
    x_tr = np.concatenate([xs, [0.0, 1.0]])          # "augmented with boundary points"
    x_te = rng.uniform(0, 1, n_h)                    # test: uniform, same size as train
    return x_tr[:, None], x_te[:, None]


def features(x):
    """Nonlinear-correlation input: (x, exact LF response). Exact LF => no LF loss term."""
    return np.hstack([x, y_lo(x)])


# ---------------------------------------------------------------- the network
def init(scheme, rng, d_in=2):
    """SIREN per Villatoro et al. eq. in 2.3.2:
         phi_0 = sin(omega_0 * (W_0 u + b_0)); phi_l = sin(W_l u + b_l)
       Schemes differ only in hidden/readout init and whether the forward pass
       multiplies by omega_0. The paper indexes its init rule l = 1..L-1, which
       includes the linear readout; that is followed here for all three schemes.
    """
    P = {}
    a0 = 1.0 / d_in
    P["W0"] = rng.uniform(-a0, a0, (d_in, WIDTH))
    P["b0"] = rng.uniform(-a0, a0, WIDTH)

    def scale(n_in):
        if scheme == "described":                       # Sitzmann text
            return np.sqrt(C / n_in)
        if scheme == "official":                        # Sitzmann repo
            return np.sqrt(C / n_in) / W0_OMEGA
        if scheme == "specified":                       # Villatoro text, as written
            return np.sqrt(C / (W0_OMEGA ** 2 * n_in))
        raise ValueError(scheme)

    for l in range(1, NHID):
        a = scale(WIDTH)
        P[f"W{l}"] = rng.uniform(-a, a, (WIDTH, WIDTH))
        P[f"b{l}"] = rng.uniform(-a, a, WIDTH)
    a = scale(WIDTH)
    P[f"W{NHID}"] = rng.uniform(-a, a, (WIDTH, 1))      # linear readout
    P[f"b{NHID}"] = np.zeros(1)

    # linear correlation branch F_l: affine, with bias (paper 2.1)
    b = np.sqrt(6.0 / (d_in + 1))
    P["Wlin"] = rng.uniform(-b, b, (d_in, 1))
    P["blin"] = np.zeros(1)
    return P


def forward(P, u, scheme, keep=False):
    s = W0_OMEGA if scheme == "official" else 1.0
    cache = {"h0": u}
    z = W0_OMEGA * (u @ P["W0"] + P["b0"])
    h = np.sin(z)
    cache["z0"], cache["h1"] = z, h
    for l in range(1, NHID):
        z = s * (h @ P[f"W{l}"] + P[f"b{l}"])
        h = np.sin(z)
        cache[f"z{l}"], cache[f"h{l+1}"] = z, h
    nl = h @ P[f"W{NHID}"] + P[f"b{NHID}"]
    lin = u @ P["Wlin"] + P["blin"]
    y = (nl + lin).ravel()
    return (y, cache) if keep else y


def backward(P, cache, u, resid, scheme):
    """resid = dL/dyhat for L = sum (yhat - y)^2, i.e. 2*(yhat - y)."""
    s = W0_OMEGA if scheme == "official" else 1.0
    g, d = {}, resid[:, None]
    g["Wlin"] = u.T @ d
    g["blin"] = d.sum(0)
    h_last = cache[f"h{NHID}"]
    g[f"W{NHID}"] = h_last.T @ d
    g[f"b{NHID}"] = d.sum(0)
    dh = d @ P[f"W{NHID}"].T
    for l in range(NHID - 1, 0, -1):
        dz = dh * np.cos(cache[f"z{l}"]) * s
        h_in = cache[f"h{l}"]
        g[f"W{l}"] = h_in.T @ dz
        g[f"b{l}"] = dz.sum(0)
        dh = dz @ P[f"W{l}"].T
    dz = dh * np.cos(cache["z0"]) * W0_OMEGA
    g["W0"] = cache["h0"].T @ dz
    g["b0"] = dz.sum(0)
    return g


def train(scheme, x_tr, x_te, lr, seed):
    rng = np.random.default_rng(seed)
    P = init(scheme, rng)
    u_tr, u_te = features(x_tr), features(x_te)
    t_tr, t_te = y_hi(x_tr).ravel(), y_hi(x_te).ravel()
    m = {k: np.zeros_like(v) for k, v in P.items()}
    v = {k: np.zeros_like(val) for k, val in P.items()}
    b1, b2, eps = 0.9, 0.999, 1e-8
    for t in range(1, EPOCHS + 1):
        yh, cache = forward(P, u_tr, scheme, keep=True)
        g = backward(P, cache, u_tr, 2.0 * (yh - t_tr), scheme)
        for k in P:
            gk = g[k].reshape(P[k].shape)
            m[k] = b1 * m[k] + (1 - b1) * gk
            v[k] = b2 * v[k] + (1 - b2) * gk * gk
            P[k] -= lr * (m[k] / (1 - b1 ** t)) / (np.sqrt(v[k] / (1 - b2 ** t)) + eps)
    yh_tr = forward(P, u_tr, scheme)
    yh_te, cache = forward(P, u_te, scheme, keep=True)
    if not np.all(np.isfinite(yh_te)):
        return np.inf, np.inf, np.nan
    return (float(np.mean((yh_tr - t_tr) ** 2) / Y_NORM_SQ),
            float(np.mean((yh_te - t_te) ** 2) / Y_NORM_SQ),
            float(cache["z1"].std()))


def jobs():
    for n_h in NHS:
        for scheme in SCHEMES:
            for rep in range(REPS):
                for lr in LRS:
                    yield dict(n_h=n_h, scheme=scheme, rep=rep, lr=float(lr))


def run_job(j):
    # data seed depends on (n_h, rep) only: all three schemes see identical data
    drng = np.random.default_rng(1000 + 17 * j["n_h"] + j["rep"])
    x_tr, x_te = make_data(j["n_h"], j["rep"], drng)
    # weight seed depends on (scheme, rep) only: independent of lr, so the lr
    # sweep for one configuration is a sweep over lr alone
    wseed = 7_000 + 100 * SCHEMES.index(j["scheme"]) + j["rep"]
    tr, te, zstd = train(j["scheme"], x_tr, x_te, j["lr"], seed=wseed)
    return dict(j, train=tr, test=te, zstd=zstd)


if __name__ == "__main__":
    import os
    OUT = "siren_accuracy_raw.json"
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 1e9   # seconds this invocation
    done = json.load(open(OUT)) if os.path.exists(OUT) else []
    seen = {(r["n_h"], r["scheme"], r["rep"], round(r["lr"], 12)) for r in done}
    todo = [j for j in jobs()
            if (j["n_h"], j["scheme"], j["rep"], round(j["lr"], 12)) not in seen]
    print(f"||y_H||^2 over [0,1] = {Y_NORM_SQ:.6f}")
    print(f"{len(done)} done, {len(todo)} remaining")

    import time
    t0 = time.time()
    for j in todo:
        if time.time() - t0 > budget:
            break
        r = run_job(j)
        done.append(r)
        print(f"{r['n_h']:>3} {r['scheme']:<10} rep{r['rep']} lr={r['lr']:.2e} "
              f"train={r['train']:.3e} test={r['test']:.3e} z1std={r['zstd']:.4g}",
              flush=True)
    json.dump(done, open(OUT, "w"))
    print(f"checkpoint: {len(done)} rows written to {OUT}")
