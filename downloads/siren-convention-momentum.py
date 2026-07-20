"""
The momentum control: does heavy-ball momentum change the SIREN convention
picture measured under plain SGD?

Companion to /posts/2026-07-18-the-sgd-control-900-on-the-hidden-stack.html,
whose Conclusion queued this experiment. Model, task, data, seeds, and manual
backprop are those of siren-convention-sgd.py without change. The only new
ingredient is classical (heavy-ball) momentum:

    v <- beta * v + g
    theta <- theta - lr * v

PROTOCOL, FIXED BEFORE RUNNING (2026-07-19):

Hypothesis: momentum's update remains linear in the gradient and applies the
same accumulation to every parameter group, so (i) the isolated hidden-stack
convention factor stays omega_0^2 = 900 and the x900 hidden-rate
reparameterization stays exact at machine precision; (ii) the full-network
shared-to-hidden displacement balance and the common best tested global
learning rate carry over from plain SGD, with the stable window shifted down
by roughly the asymptotic amplification 1/(1-beta).

Falsifiers, any one of which rejects the corresponding clause:
  F1 (mechanism): the isolated-stack official/described displacement ratio
      after 200 steps at lr=1e-8, beta=0.9 lies outside [800, 1000]; or the
      described convention at hidden lr x900 departs from the official
      trajectory by more than 1e-10 relative over 200 isolated steps.
  F2 (balance): the described convention's shared-to-hidden max-displacement
      ratio after 200 steps at lr=1e-8 under beta=0.9 differs from the beta=0
      value at identical settings by more than a factor of 2.
  F3 (rate): the two conventions select different best tested learning rates
      on the momentum 0.05-decade refined grid (3 repetitions, same seeds as
      the SGD note).

Primary outcomes: the three quantities named in F1-F3. Secondary: velocity
max-norms by parameter group, beta in {0, 0.5, 0.9, 0.99} balance sensitivity,
broad-sweep stable-window location.

Commands:
  identity            initialization equivalence
  gradcheck           analytic-gradient finite-difference check
  ratio               declared and post-hoc displacement ratios, beta=0.9
  traj [lr]           200-step isolated-stack x900 reparameterization check
  decompose [lr] [n]  shared/hidden/full n-step decomposition at beta in
                      {0, 0.5, 0.9, 0.99}, with velocity group norms
  sweep[:reps]        nine-decade half-decade sweep, beta=0.9
  refine[:reps]       0.05-decade local sweep over the best broad decade

Exact invocations used, from the downloads directory:
  python3 siren-convention-momentum.py identity
  python3 siren-convention-momentum.py gradcheck
  python3 siren-convention-momentum.py ratio
  python3 siren-convention-momentum.py traj 1e-6
  python3 siren-convention-momentum.py traj 1e-8
  python3 siren-convention-momentum.py decompose 1e-8 200
  python3 siren-convention-momentum.py decompose 1e-12 200
  python3 siren-convention-momentum.py sweep:1
  python3 siren-convention-momentum.py refine:3 -3.5

JSON outputs are written to the current directory.
"""
import sys, json, platform
import numpy as np

print("env:", platform.python_version(), platform.machine(), sys.platform,
      "| numpy", np.__version__)

OMEGA, C, WIDTH, NHID = 30.0, 6.0, 16, 3
EPOCHS = 20_000
BETA = 0.9                      # primary momentum coefficient
OMEGA2 = OMEGA * OMEGA          # 900, the predicted hidden-layer factor


def json_number(value):
    if value is None:
        return None
    value = float(value)
    return value if np.isfinite(value) else None


# ---- K1, eq. (4) of Villatoro et al.
y_lo = lambda x: 0.5 * (6 * x - 2) ** 2 * np.sin(12 * x - 4) + 10 * x - 10
y_hi = lambda x: (6 * x - 2) ** 2 * np.sin(12 * x - 4)
_q = np.linspace(0, 1, 2_000_001)
Y_NORM_SQ = np.trapezoid(y_hi(_q) ** 2, _q)
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


def train(P, official, x_tr, x_te, lr, beta=BETA, hidden_lr=None, epochs=EPOCHS,
          probe=0, isolate=False, shared_only=False):
    """Full-batch heavy-ball SGD: v <- beta v + g; theta <- theta - lr v.
    beta=0 reproduces siren-convention-sgd.py's plain-SGD update exactly.
    hidden_lr, isolate, shared_only as in the SGD script. Returns
    (params, normalized test MSE, probe outputs, velocity dict)."""
    if isolate and shared_only:
        raise ValueError("isolate and shared_only are mutually exclusive")
    P = {k: v.copy() for k, v in P.items()}
    V = {k: np.zeros_like(v) for k, v in P.items()}
    u_tr, u_te = feats(x_tr), feats(x_te)
    t_tr, t_te = y_hi(x_tr).ravel(), y_hi(x_te).ravel()
    probe_out = []
    for t in range(1, epochs + 1):
        yh, cache = forward(P, u_tr, official, keep=True)
        if not np.all(np.isfinite(yh)):
            return P, np.inf, probe_out, V
        g = backward(P, cache, u_tr, 2.0 * (yh - t_tr), official)
        for k in P:
            if isolate and k not in HIDDEN:
                continue
            if shared_only and k in HIDDEN:
                continue
            gk = g[k].reshape(P[k].shape)
            V[k] = beta * V[k] + gk
            step = hidden_lr if (hidden_lr is not None and k in HIDDEN) else lr
            P[k] -= step * V[k]
        if probe and t <= probe:
            probe_out.append(forward(P, u_te, official).copy())
    yte = forward(P, u_te, official)
    if not np.all(np.isfinite(yte)):
        return P, np.inf, probe_out, V
    return P, float(np.mean((yte - t_te) ** 2) / Y_NORM_SQ), probe_out, V


def group_vmax(V):
    hid = max(np.abs(V[k]).max() for k in V if k in HIDDEN)
    sha = max(np.abs(V[k]).max() for k in V if k not in HIDDEN)
    return float(sha), float(hid)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python siren-convention-momentum.py COMMAND [ARG]")
    what = sys.argv[1]
    x_tr, x_te = data(32, 0)
    Pd = init_described(np.random.default_rng(7000))
    Po = to_official(Pd)

    if what == "identity":
        yd, yo = forward(Pd, feats(x_te), False), forward(Po, feats(x_te), True)
        print(f"A. init |y_described - y_official|_max = {np.abs(yd - yo).max():.3e}")
        print(f"   relative to |y|_max = {np.abs(yd).max():.6f} "
              f"-> {np.abs(yd - yo).max()/np.abs(yd).max():.3e}")

    if what == "gradcheck":
        u = feats(x_tr); t = y_hi(x_tr).ravel()
        for name, P, off in (("described", Pd, False), ("official", Po, True)):
            yh, cache = forward(P, u, off, keep=True)
            g = backward(P, cache, u, 2.0 * (yh - t), off)
            worst = 0.0
            rng = np.random.default_rng(3)
            for k in P:
                flat = P[k].ravel()
                for _ in range(min(8, flat.size)):
                    i = int(rng.integers(flat.size)); h = 1e-6 * max(1, abs(flat[i]))
                    old = flat[i]
                    flat[i] = old + h; lp = np.sum((forward(P, u, off) - t) ** 2)
                    flat[i] = old - h; lm = np.sum((forward(P, u, off) - t) ** 2)
                    flat[i] = old
                    fd = (lp - lm) / (2 * h); an = g[k].ravel()[i]
                    worst = max(worst, abs(fd - an) / (abs(fd) + abs(an) + 1e-30))
            print(f"gradcheck {name:<10} worst relative error = {worst:.3e}")

    if what == "ratio":
        # P1. displacement ratio official/described at a common lr, beta=0.9,
        # after 1 step (identical to plain SGD by construction: v_1 = g_1) and
        # after 200 steps (momentum active). Full network and isolated stack.
        u = feats(x_te)
        y0d = forward(Pd, u, False); y0o = forward(Po, u, True)
        out = []
        for lr in (1e-9, 1e-8, 1e-7, 1e-6):
            for steps in (1, 200):
                row = dict(lr=lr, steps=steps, beta=BETA)
                for tag, iso in (("full", False), ("iso", True)):
                    Qo, _, _, _ = train(Po, True, x_tr, x_te, lr, epochs=steps, isolate=iso)
                    Qd, _, _, _ = train(Pd, False, x_tr, x_te, lr, epochs=steps, isolate=iso)
                    do = np.abs(forward(Qo, u, True) - y0o).max()
                    dd = np.abs(forward(Qd, u, False) - y0d).max()
                    row[f"{tag}_ratio"] = float(do / dd)
                    row[f"{tag}_off"] = float(do); row[f"{tag}_desc"] = float(dd)
                print(f"P1. lr={lr:.0e} steps={steps:<3} | full ratio="
                      f"{row['full_ratio']:.4f} | isolated-hidden ratio="
                      f"{row['iso_ratio']:.4f}  (predict {OMEGA2:.0f})", flush=True)
                out.append(row)
        json.dump(out, open("momentum_ratio.json", "w"), indent=2)

        # Post-hoc regime check added after F1 fired: repeat the 200-step
        # isolated measurement where both output displacements remain small.
        posthoc = []
        for lr in (1e-12, 1e-11, 1e-10):
            Qo, _, _, _ = train(Po, True, x_tr, x_te, lr, epochs=200,
                                isolate=True)
            Qd, _, _, _ = train(Pd, False, x_tr, x_te, lr, epochs=200,
                                isolate=True)
            do = np.abs(forward(Qo, u, True) - y0o).max()
            dd = np.abs(forward(Qd, u, False) - y0d).max()
            row = dict(lr=lr, steps=200, beta=BETA,
                       iso_off=float(do), iso_desc=float(dd),
                       iso_ratio=float(do / dd), posthoc=True)
            print(f"P1 post hoc. lr={lr:.0e} steps=200 | isolated-hidden "
                  f"ratio={row['iso_ratio']:.4f}  (predict {OMEGA2:.0f})",
                  flush=True)
            posthoc.append(row)
        json.dump(posthoc, open("momentum_ratio_posthoc.json", "w"), indent=2)

    if what == "traj":
        # E. official@lr vs described@(hidden lr x900), beta=0.9, isolated
        # stack, 200 steps: per-step agreement of the two trajectories.
        lr = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-6
        n = 200
        _, _, po, _ = train(Po, True, x_tr, x_te, lr, epochs=n, probe=n, isolate=True)
        _, _, pd, _ = train(Pd, False, x_tr, x_te, lr, hidden_lr=OMEGA2 * lr,
                            epochs=n, probe=n, isolate=True)
        diffs = [float(np.abs(a - b).max()) for a, b in zip(po, pd)]
        scale = float(np.abs(po[-1]).max())
        print(f"E. lr={lr:.0e} beta={BETA} steps={n} isolated | "
              f"max|y_off - y_desc*| first={diffs[0]:.3e} last={diffs[-1]:.3e}"
              f" | rel_last={diffs[-1]/scale:.3e}")
        record = dict(lr=lr, beta=BETA, steps=n, diffs=diffs, scale=scale)
        runs = []
        try:
            existing = json.load(open("momentum_traj.json"))
            runs = existing.get("runs", []) if isinstance(existing, dict) else existing
        except Exception:
            pass
        runs = [run for run in runs if run.get("lr") != lr]
        runs.append(record); runs.sort(key=lambda run: run["lr"])
        json.dump({"runs": runs}, open("momentum_traj.json", "w"), indent=2)

    if what == "decompose":
        # D. n-step shared-only / hidden-only / full displacement magnitudes at
        # beta in {0, 0.5, 0.9, 0.99}, with per-group final velocity max-norms
        # for the full-network run. beta=0 is the plain-SGD reference measured
        # by the same code path.
        lr = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-8
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 200
        u = feats(x_te)

        def delta(P, official, beta, **groups):
            Q, _, _, V = train(P, official, x_tr, x_te, lr, beta=beta,
                               epochs=n, **groups)
            return forward(Q, u, official) - forward(P, u, official), V

        out = []
        for beta in (0.0, 0.5, 0.9, 0.99):
            sd, _ = delta(Pd, False, beta, shared_only=True)
            so, _ = delta(Po, True, beta, shared_only=True)
            hd, _ = delta(Pd, False, beta, isolate=True)
            ho, _ = delta(Po, True, beta, isolate=True)
            ad, Vd = delta(Pd, False, beta)
            ao, Vo = delta(Po, True, beta)
            vs_d, vh_d = group_vmax(Vd)
            vs_o, vh_o = group_vmax(Vo)
            row = {
                "beta": beta, "lr": lr, "steps": n,
                "shared_described_max": float(np.abs(sd).max()),
                "shared_official_max": float(np.abs(so).max()),
                "shared_match_max": float(np.abs(sd - so).max()),
                "hidden_described_max": float(np.abs(hd).max()),
                "hidden_official_max": float(np.abs(ho).max()),
                "hidden_factor_max": float(np.abs(ho).max() / np.abs(hd).max()),
                "shared_to_hidden_described_max": float(np.abs(sd).max() / np.abs(hd).max()),
                "shared_to_hidden_official_max": float(np.abs(so).max() / np.abs(ho).max()),
                "full_described_max": float(np.abs(ad).max()),
                "full_official_max": float(np.abs(ao).max()),
                "full_ratio_max": float(np.abs(ao).max() / np.abs(ad).max()),
                "reconstruction_described_max": float(np.abs(ad - sd - hd).max()),
                "reconstruction_official_max": float(np.abs(ao - so - ho).max()),
                "vel_shared_described": vs_d, "vel_hidden_described": vh_d,
                "vel_shared_official": vs_o, "vel_hidden_official": vh_o,
            }
            print(f"D. beta={beta:<4} lr={lr:.0e} n={n} | "
                  f"S/h desc={row['shared_to_hidden_described_max']:.2f} "
                  f"off={row['shared_to_hidden_official_max']:.4f} | "
                  f"hidden factor={row['hidden_factor_max']:.4f} | "
                  f"full ratio={row['full_ratio_max']:.6f}", flush=True)
            print(f"   velocity max: shared desc={vs_d:.6e} off={vs_o:.6e} | "
                  f"hidden desc={vh_d:.6e} off={vh_o:.6e}")
            out.append(row)
        if lr == 1e-8:
            output_name = "momentum_decomposition.json"
        elif lr == 1e-12:
            output_name = "momentum_decomposition_1e-12.json"
        else:
            lr_label = f"{lr:.0e}".replace("+", "")
            output_name = f"momentum_decomposition_{lr_label}.json"
        json.dump(out, open(output_name, "w"), indent=2)

    if what.startswith("sweep"):
        # C. wide lr grid under beta=0.9.
        reps = int(what.split(":")[1]) if ":" in what else 1
        grid = np.logspace(-8, 1, 19)
        rows = []
        try:
            rows = json.load(open("momentum_sweep.json"))
        except Exception:
            pass
        for row in rows:
            row["test"] = json_number(row["test"])
        seen = {(r["conv"], r["rep"], round(r["lr"], 14)) for r in rows}
        for rep in range(reps):
            xa, xb = data(32, rep)
            Pd_ = init_described(np.random.default_rng(7000 + rep))
            Po_ = to_official(Pd_)
            for lr in grid:
                for conv, P, off in (("described", Pd_, False), ("official", Po_, True)):
                    if (conv, rep, round(float(lr), 14)) in seen:
                        continue
                    _, mse, _, _ = train(P, off, xa, xb, float(lr))
                    rows.append(dict(conv=conv, rep=rep, lr=float(lr),
                                     test=json_number(mse)))
                    print(f"C. rep{rep} {conv:<10} lr={lr:.3e} test={mse:.4e}",
                          flush=True)
                    json.dump(rows, open("momentum_sweep.json", "w"))
        json.dump(rows, open("momentum_sweep.json", "w"))

    if what.startswith("refine"):
        # F. 0.05-decade local grid over the decade indicated by the broad
        # sweep, same repetition seeds as the SGD note's refined sweep.
        reps = int(what.split(":")[1]) if ":" in what else 1
        lo = float(sys.argv[2]) if len(sys.argv) > 2 else -5.0
        grid = np.logspace(lo, lo + 1.0, 21)
        rows = []
        try:
            rows = json.load(open("momentum_refined_sweep.json"))
        except Exception:
            pass
        for row in rows:
            row["test"] = json_number(row["test"])
        seen = {(r["conv"], r["rep"], round(r["lr"], 14)) for r in rows}
        for rep in range(reps):
            xa, xb = data(32, rep)
            Pd_ = init_described(np.random.default_rng(7000 + rep))
            Po_ = to_official(Pd_)
            for lr in grid:
                for conv, P, off in (("described", Pd_, False), ("official", Po_, True)):
                    if (conv, rep, round(float(lr), 14)) in seen:
                        continue
                    _, mse, _, _ = train(P, off, xa, xb, float(lr))
                    rows.append(dict(conv=conv, rep=rep, lr=float(lr),
                                     test=json_number(mse)))
                    print(f"F. rep{rep} {conv:<10} lr={lr:.6e} test={mse:.6e}",
                          flush=True)
                    json.dump(rows, open("momentum_refined_sweep.json", "w"))
        json.dump(rows, open("momentum_refined_sweep.json", "w"))
        for rep in range(reps):
            for conv in ("official", "described"):
                rr = [r for r in rows if r["rep"] == rep and r["conv"] == conv]
                finite = [r for r in rr if r["test"] is not None]
                best = min(finite, key=lambda r: r["test"])
                nonf = [r["lr"] for r in rr if r["test"] is None]
                first_nonfinite = min(nonf) if nonf else None
                print(f"F. summary rep{rep} {conv:<10} "
                      f"best_lr={best['lr']:.6e} test={best['test']:.6e} "
                      f"first_nonfinite="
                      f"{first_nonfinite if first_nonfinite else 'none'}")
