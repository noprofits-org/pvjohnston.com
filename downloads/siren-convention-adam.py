"""
Are the two Sitzmann SIREN conventions equivalent under Adam?

They are the same function at initialization -- the official implementation's
division by omega_0 cancels its own multiplication by omega_0. This script asks
whether that equivalence survives training, and if not, what the mismatch is.

Companion to /posts/2026-07-17-why-the-two-siren-conventions-train-differently.html.
NumPy only; manual backprop; CPU.
"""
import sys, json, platform
import numpy as np

print("env:", platform.python_version(), platform.machine(), sys.platform,
      "| numpy", np.__version__)

OMEGA, C, WIDTH, NHID = 30.0, 6.0, 16, 3
EPOCHS = 20_000

# ---- K1, eq. (4) of Villatoro et al.
y_lo = lambda x: 0.5 * (6 * x - 2) ** 2 * np.sin(12 * x - 4) + 10 * x - 10
y_hi = lambda x: (6 * x - 2) ** 2 * np.sin(12 * x - 4)
_q = np.linspace(0, 1, 2_000_001)
Y_NORM_SQ = np.trapezoid(y_hi(_q) ** 2, _q)
feats = lambda x: np.hstack([x, y_lo(x)])


def sobol1d(n, offset):
    idx = np.arange(offset, offset + n, dtype=np.uint64)
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
    """Sitzmann as described: phi_l = sin(W_l h + b_l), W_l,b_l ~ U(+-sqrt(6/n))."""
    P = {}
    a0 = 1.0 / d_in
    P["W0"] = rng.uniform(-a0, a0, (d_in, WIDTH)); P["b0"] = rng.uniform(-a0, a0, WIDTH)
    for l in range(1, NHID):
        a = np.sqrt(C / WIDTH)
        P[f"W{l}"] = rng.uniform(-a, a, (WIDTH, WIDTH)); P[f"b{l}"] = rng.uniform(-a, a, WIDTH)
    a = np.sqrt(C / WIDTH)                       # readout: identical in both conventions
    P["Wo"] = rng.uniform(-a, a, (WIDTH, 1)); P["bo"] = np.zeros(1)
    b = np.sqrt(6.0 / (d_in + 1))
    P["Wlin"] = rng.uniform(-b, b, (d_in, 1)); P["blin"] = np.zeros(1)
    return P


def to_official(P):
    """Same function, official parameterization: hidden W,b divided by omega_0,
    forward multiplies by omega_0. Everything else is untouched."""
    Q = {k: v.copy() for k, v in P.items()}
    for l in range(1, NHID):
        Q[f"W{l}"] = P[f"W{l}"] / OMEGA
        Q[f"b{l}"] = P[f"b{l}"] / OMEGA
    return Q


HIDDEN = [f"{p}{l}" for l in range(1, NHID) for p in ("W", "b")]


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


def train(P, official, x_tr, x_te, lr, hidden_lr=None, epochs=EPOCHS):
    """hidden_lr: if given, applied to hidden W,b only; lr applied elsewhere."""
    P = {k: v.copy() for k, v in P.items()}
    u_tr, u_te = feats(x_tr), feats(x_te)
    t_tr, t_te = y_hi(x_tr).ravel(), y_hi(x_te).ravel()
    m = {k: np.zeros_like(v) for k, v in P.items()}
    v = {k: np.zeros_like(val) for k, val in P.items()}
    b1, b2, eps = 0.9, 0.999, 1e-8
    for t in range(1, epochs + 1):
        yh, cache = forward(P, u_tr, official, keep=True)
        g = backward(P, cache, u_tr, 2.0 * (yh - t_tr), official)
        for k in P:
            gk = g[k].reshape(P[k].shape)
            m[k] = b1 * m[k] + (1 - b1) * gk
            v[k] = b2 * v[k] + (1 - b2) * gk * gk
            step = hidden_lr if (hidden_lr is not None and k in HIDDEN) else lr
            P[k] -= step * (m[k] / (1 - b1 ** t)) / (np.sqrt(v[k] / (1 - b2 ** t)) + eps)
    yte = forward(P, u_te, official)
    if not np.all(np.isfinite(yte)):
        return P, np.inf
    return P, float(np.mean((yte - t_te) ** 2) / Y_NORM_SQ)


def effective(P, official):
    """The hidden weights in function space: what actually multiplies the input."""
    s = OMEGA if official else 1.0
    return np.concatenate([(s * P[k]).ravel() for k in HIDDEN])


if __name__ == "__main__":
    what = sys.argv[1]
    x_tr, x_te = data(32, 0)
    Pd = init_described(np.random.default_rng(7000))
    Po = to_official(Pd)

    if what == "identity":
        # A. the two parameterizations are the same function at initialization
        yd, yo = forward(Pd, feats(x_te), False), forward(Po, feats(x_te), True)
        print(f"A. init |y_described - y_official|_max = {np.abs(yd - yo).max():.3e}")
        print(f"   relative to |y|_max = {np.abs(yd).max():.6f} "
              f"-> {np.abs(yd - yo).max()/np.abs(yd).max():.3e}")

    if what == "equiv":
        # B. is official@lr equal to described@lr with hidden lr scaled by omega_0?
        out = []
        for lr in (1e-5, 1e-4, 1e-3):
            _, mo = train(Po, True, x_tr, x_te, lr)
            _, md = train(Pd, False, x_tr, x_te, lr)                    # same global lr
            _, mp = train(Pd, False, x_tr, x_te, lr, hidden_lr=OMEGA * lr)  # per-layer
            print(f"B. lr={lr:.0e} | official={mo:.6e}  described={md:.6e}  "
                  f"described(hidden lr x{OMEGA:.0f})={mp:.6e}  "
                  f"| rel|desc*-off| = {abs(mp-mo)/mo:.3e}", flush=True)
            out.append(dict(lr=lr, official=mo, described=md, described_scaled=mp))
        json.dump(out, open("conv_equiv.json", "w"))

    if what.startswith("range"):
        # D. multi-seed: best test MSE inside the paper's lr range vs above it
        import time
        budget = float(what.split(":")[1])
        t0 = time.time()
        grid = [1e-5, 3.16e-5, 1e-4, 3.16e-4, 1e-3,        # inside  [1e-5, 1e-3]
                3.16e-3, 1e-2, 3.16e-2, 1e-1]              # above
        try:
            rows = json.load(open("conv_range.json"))
        except Exception:
            rows = []
        seen = {(r["conv"], r["rep"], round(r["lr"], 12)) for r in rows}
        cells = [(rep, lr) for rep in range(4) for lr in grid]
        for rep, lr in cells:
            if time.time() - t0 > budget:
                break
            xa, xb = data(32, rep)
            Pd_ = init_described(np.random.default_rng(7000 + rep))
            Po_ = to_official(Pd_)
            for conv, P, off in (("described", Pd_, False), ("official", Po_, True)):
                if (conv, rep, round(float(lr), 12)) in seen:
                    continue
                _, mse = train(P, off, xa, xb, float(lr))
                rows.append(dict(conv=conv, rep=rep, lr=float(lr), test=mse))
                print(f"D. rep{rep} {conv:<10} lr={lr:.3e} test={mse:.4e}", flush=True)
        json.dump(rows, open("conv_range.json", "w"))

    if what.startswith("sweep"):
        # C. where does each convention's optimum lr sit vs the paper's range?
        lo, hi = int(what.split(":")[1]), int(what.split(":")[2])
        grid = np.logspace(-5, -1, 17)[lo:hi]
        try:
            rows = json.load(open("conv_sweep.json"))
        except Exception:
            rows = []
        seen = {(r["conv"], round(r["lr"], 12)) for r in rows}
        for lr in grid:
            for conv, P, off in (("described", Pd, False), ("official", Po, True)):
                if (conv, round(float(lr), 12)) in seen:
                    continue
                _, mse = train(P, off, x_tr, x_te, float(lr))
                rows.append(dict(conv=conv, lr=float(lr), test=mse))
                print(f"C. {conv:<10} lr={lr:.3e} test={mse:.4e}", flush=True)
        json.dump(rows, open("conv_sweep.json", "w"))
