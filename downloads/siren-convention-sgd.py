"""
The SGD control: do the two Sitzmann SIREN conventions differ by omega_0^2?

Companion to /posts/2026-07-17-why-the-two-siren-conventions-train-differently.html,
whose Conclusion queued this experiment. Under Adam the two conventions differ by
a per-layer factor of omega_0 on the hidden layers, because Adam's step size is
almost independent of the gradient magnitude. Plain SGD's step IS proportional to
the gradient: the official convention's stored hidden weights are omega_0 times
smaller, so their gradient is omega_0 times larger, and the step lands on a weight
the forward pass multiplies by omega_0 again. Predicted function-space factor:
omega_0^2 = 900, exact per step with no epsilon caveat.

"Official" below means the matched-function parameterization used by the note:
both hidden weights and hidden biases are divided by omega_0. The official
repository initializes only the weights this way and leaves biases at the
framework default, so this is an exact reparameterization control rather than a
literal replay of the repository's initialization.

NumPy only; manual backprop; CPU. Same model as siren-convention-adam.py.

Commands used by the note:
  identity            initialization equivalence
  gradcheck           analytic-gradient finite-difference check
  ratio               common-rate single-step ratios (Table 1)
  decompose [lr]      shared/hidden/full one-step decomposition (Table 2)
  traj [lr]           200-step isolated-stack reparameterization check
  sweep[:reps]        nine-decade half-decade sweep
  refine[:reps]       0.05-decade local sweep (Table 3)

JSON outputs are written to the current directory.
"""
import sys, json, platform
import numpy as np

print("env:", platform.python_version(), platform.machine(), sys.platform,
      "| numpy", np.__version__)

OMEGA, C, WIDTH, NHID = 30.0, 6.0, 16, 3
EPOCHS = 20_000
OMEGA2 = OMEGA * OMEGA          # 900, the predicted hidden-layer factor under SGD


def json_number(value):
    """Return a strict-JSON number, or None for NaN and either infinity."""
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


def train(P, official, x_tr, x_te, lr, hidden_lr=None, epochs=EPOCHS, probe=0,
          isolate=False, shared_only=False):
    """Plain full-batch SGD. hidden_lr, if given, is applied to hidden W,b only.
    isolate=True: freeze everything except the hidden layers (the shared first
    layer, readout, and affine branch), so only the hidden stack trains.
    shared_only=True: freeze the hidden layers, so only those shared parameters
    train. isolate and shared_only are mutually exclusive.
    probe>0: also return the first `probe` steps' test-set outputs."""
    if isolate and shared_only:
        raise ValueError("isolate and shared_only are mutually exclusive")
    P = {k: v.copy() for k, v in P.items()}
    u_tr, u_te = feats(x_tr), feats(x_te)
    t_tr, t_te = y_hi(x_tr).ravel(), y_hi(x_te).ravel()
    probe_out = []
    for t in range(1, epochs + 1):
        yh, cache = forward(P, u_tr, official, keep=True)
        if not np.all(np.isfinite(yh)):
            return P, np.inf, probe_out
        g = backward(P, cache, u_tr, 2.0 * (yh - t_tr), official)
        for k in P:
            if isolate and k not in HIDDEN:
                continue
            if shared_only and k in HIDDEN:
                continue
            gk = g[k].reshape(P[k].shape)
            step = hidden_lr if (hidden_lr is not None and k in HIDDEN) else lr
            P[k] -= step * gk
        if probe and t <= probe:
            probe_out.append(forward(P, u_te, official).copy())
    yte = forward(P, u_te, official)
    if not np.all(np.isfinite(yte)):
        return P, np.inf, probe_out
    return P, float(np.mean((yte - t_te) ** 2) / Y_NORM_SQ), probe_out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python siren-convention-sgd.py COMMAND [ARG]")
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
        # central finite differences vs analytic SGD gradient, both conventions
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
        # P1. single-step function-space displacement ratio, official vs described
        # (both at the SAME lr, unscaled) as lr -> 0. Predicted limit: omega_0^2.
        # Measured two ways: full network, and isolated hidden stack (shared
        # first layer, readout, affine branch frozen).
        u = feats(x_te)
        y0d = forward(Pd, u, False); y0o = forward(Po, u, True)
        out = []
        for lr in (1e-8, 1e-7, 1e-6, 1e-5, 1e-4):
            row = dict(lr=lr)
            for tag, iso in (("full", False), ("iso", True)):
                Qo, _, _ = train(Po, True, x_tr, x_te, lr, epochs=1, isolate=iso)
                Qd, _, _ = train(Pd, False, x_tr, x_te, lr, epochs=1, isolate=iso)
                do = np.abs(forward(Qo, u, True) - y0o).max()
                dd = np.abs(forward(Qd, u, False) - y0d).max()
                row[f"{tag}_ratio"] = float(do / dd)
                row[f"{tag}_off"] = float(do); row[f"{tag}_desc"] = float(dd)
            print(f"P1. lr={lr:.0e} | full ratio={row['full_ratio']:.4f}"
                  f" | isolated-hidden ratio={row['iso_ratio']:.4f}"
                  f"  (predict {OMEGA2:.0f})", flush=True)
            out.append(row)
        json.dump(out, open("sgd_ratio.json", "w"), indent=2)

    if what == "decompose":
        # D. Directly measure the hidden-only and shared-only contributions to a
        # one-step full-network displacement. Besides their magnitudes, report
        # vector alignment and the finite-step residual in
        #     delta_all = delta_shared + delta_hidden + residual.
        # This avoids inferring a scalar S/h ratio from a ratio of max norms.
        lr = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-8
        u = feats(x_te)

        def delta(P, official, **groups):
            Q, _, _ = train(P, official, x_tr, x_te, lr, epochs=1, **groups)
            return forward(Q, u, official) - forward(P, u, official)

        def rms(v):
            return float(np.sqrt(np.mean(v * v)))

        def cosine(a, b):
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

        sd = delta(Pd, False, shared_only=True)
        so = delta(Po, True, shared_only=True)
        hd = delta(Pd, False, isolate=True)
        ho = delta(Po, True, isolate=True)
        ad = delta(Pd, False)
        ao = delta(Po, True)
        rd = ad - sd - hd
        ro = ao - so - ho

        out = {
            "lr": lr,
            "shared_described_max": float(np.abs(sd).max()),
            "shared_official_max": float(np.abs(so).max()),
            "shared_match_max": float(np.abs(sd - so).max()),
            "hidden_described_max": float(np.abs(hd).max()),
            "hidden_official_max": float(np.abs(ho).max()),
            "hidden_factor_max": float(np.abs(ho).max() / np.abs(hd).max()),
            "shared_to_hidden_described_max": float(np.abs(sd).max() / np.abs(hd).max()),
            "shared_to_hidden_official_max": float(np.abs(so).max() / np.abs(ho).max()),
            "shared_described_rms": rms(sd),
            "shared_official_rms": rms(so),
            "hidden_described_rms": rms(hd),
            "hidden_official_rms": rms(ho),
            "hidden_factor_rms": rms(ho) / rms(hd),
            "shared_to_hidden_described_rms": rms(sd) / rms(hd),
            "shared_to_hidden_official_rms": rms(so) / rms(ho),
            "shared_hidden_cosine_described": cosine(sd, hd),
            "shared_hidden_cosine_official": cosine(so, ho),
            "full_described_max": float(np.abs(ad).max()),
            "full_official_max": float(np.abs(ao).max()),
            "full_ratio_max": float(np.abs(ao).max() / np.abs(ad).max()),
            "reconstruction_described_max": float(np.abs(rd).max()),
            "reconstruction_official_max": float(np.abs(ro).max()),
        }
        print(f"D. lr={lr:.0e} shared max={out['shared_described_max']:.6e} "
              f"(convention mismatch {out['shared_match_max']:.3e})")
        print(f"   hidden max: described={out['hidden_described_max']:.6e} "
              f"official={out['hidden_official_max']:.6e} "
              f"factor={out['hidden_factor_max']:.4f}")
        print(f"   shared/hidden max: described={out['shared_to_hidden_described_max']:.2f} "
              f"official={out['shared_to_hidden_official_max']:.4f}")
        print(f"   shared-hidden cosine: described="
              f"{out['shared_hidden_cosine_described']:.6f} "
              f"official={out['shared_hidden_cosine_official']:.6f}")
        print(f"   full max: described={out['full_described_max']:.6e} "
              f"official={out['full_official_max']:.6e} "
              f"ratio={out['full_ratio_max']:.6f}")
        print(f"   reconstruction max: described="
              f"{out['reconstruction_described_max']:.3e} "
              f"official={out['reconstruction_official_max']:.3e}")
        json.dump(out, open("sgd_decomposition.json", "w"), indent=2)

    if what == "traj":
        # E. per-step equivalence: official@lr vs described@(hidden lr x900), N steps,
        # on the isolated hidden stack (shared params frozen so the two are the same
        # trainable problem). Shows machine-precision agreement and its decay.
        lr = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-6
        n = 200
        _, _, po = train(Po, True, x_tr, x_te, lr, epochs=n, probe=n, isolate=True)
        _, _, pd = train(Pd, False, x_tr, x_te, lr, hidden_lr=OMEGA2 * lr,
                         epochs=n, probe=n, isolate=True)
        diffs = [float(np.abs(a - b).max()) for a, b in zip(po, pd)]
        scale = float(np.abs(po[-1]).max())
        print(f"E. lr={lr:.0e} steps={n} isolated | max|y_off - y_desc*|"
              f" first={diffs[0]:.3e} last={diffs[-1]:.3e}"
              f" | rel_last={diffs[-1]/scale:.3e}")
        record = dict(lr=lr, steps=n, diffs=diffs, scale=scale)
        runs = []
        try:
            existing = json.load(open("sgd_traj.json"))
            if isinstance(existing, dict) and "runs" in existing:
                runs = existing["runs"]
            elif isinstance(existing, dict) and "lr" in existing:
                runs = [existing]
            elif isinstance(existing, list):
                runs = existing
        except Exception:
            pass
        runs = [run for run in runs if run.get("lr") != lr]
        runs.append(record)
        runs.sort(key=lambda run: run["lr"])
        json.dump({"runs": runs}, open("sgd_traj.json", "w"), indent=2)

    if what == "equiv":
        # B. official@lr vs described@lr vs described@(hidden lr x900), full run
        out = []
        for lr in (1e-6, 1e-5, 1e-4, 1e-3):
            _, mo, _ = train(Po, True, x_tr, x_te, lr)
            _, md, _ = train(Pd, False, x_tr, x_te, lr)
            _, mp, _ = train(Pd, False, x_tr, x_te, lr, hidden_lr=OMEGA2 * lr)
            rel = abs(mp - mo) / mo if np.isfinite(mo) and mo > 0 else float("nan")
            print(f"B. lr={lr:.0e} | official={mo:.6e}  described={md:.6e}  "
                  f"described(hidden lr x{OMEGA2:.0f})={mp:.6e}  "
                  f"| rel|desc*-off| = {rel:.3e}", flush=True)
            out.append(dict(lr=lr, official=json_number(mo),
                            described=json_number(md),
                            described_scaled=json_number(mp),
                            relative_difference=json_number(rel)))
        json.dump(out, open("sgd_equiv.json", "w"))

    if what.startswith("sweep"):
        # C. wide lr grid; where does each convention's optimum sit?
        reps = int(what.split(":")[1]) if ":" in what else 1
        grid = np.logspace(-8, 1, 19)      # step sqrt(10), spans 9 decades
        rows = []
        try:
            rows = json.load(open("sgd_sweep.json"))
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
                    _, mse, _ = train(P, off, xa, xb, float(lr))
                    rows.append(dict(conv=conv, rep=rep, lr=float(lr),
                                     test=json_number(mse)))
                    print(f"C. rep{rep} {conv:<10} lr={lr:.3e} test={mse:.4e}", flush=True)
                    json.dump(rows, open("sgd_sweep.json", "w"))   # checkpoint each run
        json.dump(rows, open("sgd_sweep.json", "w"))

    if what.startswith("refine"):
        # F. Resolve the common half-decade optimum with a 0.05-decade local
        # grid from 1e-4 through 1e-3, using the same repetitions and seeds.
        reps = int(what.split(":")[1]) if ":" in what else 1
        grid = np.logspace(-4, -3, 21)
        rows = []
        try:
            rows = json.load(open("sgd_refined_sweep.json"))
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
                    _, mse, _ = train(P, off, xa, xb, float(lr))
                    stored_mse = json_number(mse)
                    rows.append(dict(conv=conv, rep=rep, lr=float(lr), test=stored_mse))
                    print(f"F. rep{rep} {conv:<10} lr={lr:.6e} "
                          f"test={mse:.6e}", flush=True)
                    json.dump(rows, open("sgd_refined_sweep.json", "w"))
        json.dump(rows, open("sgd_refined_sweep.json", "w"))
        for rep in range(reps):
            for conv in ("official", "described"):
                rr = [r for r in rows if r["rep"] == rep and r["conv"] == conv]
                finite = [r for r in rr if r["test"] is not None]
                best = min(finite, key=lambda r: r["test"])
                first_nonfinite = min(r["lr"] for r in rr if r["test"] is None)
                print(f"F. summary rep{rep} {conv:<10} "
                      f"best_lr={best['lr']:.6e} test={best['test']:.6e} "
                      f"first_nonfinite={first_nonfinite:.6e}")
