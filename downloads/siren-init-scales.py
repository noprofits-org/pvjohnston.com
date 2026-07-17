import numpy as np, sys, platform
print("env:", platform.python_version(), platform.machine(), sys.platform, "| numpy", np.__version__)

RNG = np.random.default_rng(0)
C, W = 6.0, 16          # c=6; hidden width 16 (paper's 3x16 config)
N = 200_000             # samples
X = RNG.uniform(0, 1, size=(N, 1))   # K1 domain x in [0,1]

def run(scheme, w0, L=4):
    """L layers total: phi_0, phi_1, phi_2 hidden sines + linear readout.
    Returns per-hidden-layer pre-activation std."""
    h, stds = X, []
    for l in range(L - 1):
        n_in = h.shape[1]
        if l == 0:
            Wl = RNG.uniform(-1/n_in, 1/n_in, size=(n_in, W))
            z  = w0 * (h @ Wl)                      # all schemes: w0 on first layer
        else:
            if scheme == "paper":        # Sitzmann paper: no w0 in fwd, init U(+-sqrt(6/n))
                a = np.sqrt(C / n_in)
                Wl = RNG.uniform(-a, a, size=(n_in, W)); z = h @ Wl
            elif scheme == "repo":       # Sitzmann repo: w0 in fwd, init U(+-sqrt(6/n)/w0)
                a = np.sqrt(C / n_in) / w0
                Wl = RNG.uniform(-a, a, size=(n_in, W)); z = w0 * (h @ Wl)
            elif scheme == "villatoro":  # paper's fwd + repo's init: the div-w0 with nothing to cancel it
                a = np.sqrt(C / (w0**2 * n_in))
                Wl = RNG.uniform(-a, a, size=(n_in, W)); z = h @ Wl
            stds.append(z.std())
        h = np.sin(z)
    return stds

def nonlinearity(z_std):
    """Relative deviation of sin(z) from z over a Gaussian of this std -> how linear the unit is."""
    z = RNG.normal(0, z_std, 200_000)
    return np.abs(np.sin(z) - z).mean() / np.abs(z).mean()

print(f"\n{'scheme':<12}{'w0':>5} | hidden pre-activation std (layers 1,2) | sin() deviation from identity")
print("-" * 92)
for w0 in (5, 10, 20, 30):
    for s in ("paper", "repo", "villatoro"):
        st = run(s, w0)
        dev = nonlinearity(st[0])
        print(f"{s:<12}{w0:>5} | {st[0]:>10.5f} {st[1]:>10.5f}              | {dev*100:>8.4f} %")
    print()
