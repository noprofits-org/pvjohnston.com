"""
Newton solver + theta-continuation for instantaneous solitons of the
Tao/Wang/Xu discrete nonlinear model, and center-of-mass tracking.

Stationary problem (chi real, since H is real symmetric):
    F(chi, mu) = H chi + V(chi) o chi - mu chi = 0        (2L equations)
    G(chi)     = sum chi^2 - N = 0                        (1 equation)
with V_{sigma j} = g chi_{sigma j}^2 + g12 chi_{sigma-bar j}^2.
"""
import numpy as np
from soliton_model import h_real, h_k


def partner(L):
    """index of the other component in the same unit cell"""
    idx = np.arange(2 * L)
    return idx ^ 1          # 2j <-> 2j+1


def residual(chi, mu, H, g, g12, N, prt):
    V = g * chi**2 + g12 * chi[prt]**2
    F = H @ chi + V * chi - mu * chi
    G = chi @ chi - N
    return F, G


def jacobian(chi, mu, H, g, g12, prt):
    n = len(chi)
    J = H.copy()
    V = g * chi**2 + g12 * chi[prt]**2
    J[np.arange(n), np.arange(n)] += 3 * g * chi**2 + g12 * chi[prt]**2 - mu
    # cross term d/dchi_bar of (g12 chi_bar^2 chi)
    J[np.arange(n), prt] += 2 * g12 * chi[prt] * chi
    return J


def newton(chi0, mu0, theta, m0, g, g12, N, L, tol=1e-11, maxit=60):
    H = h_real(theta, m0, L)
    prt = partner(L)
    chi, mu = chi0.copy(), float(mu0)
    for it in range(maxit):
        F, G = residual(chi, mu, H, g, g12, N, prt)
        err = max(np.abs(F).max(), abs(G))
        if err < tol:
            return chi, mu, True, err
        J = jacobian(chi, mu, H, g, g12, prt)
        n = len(chi)
        M = np.zeros((n + 1, n + 1))
        M[:n, :n] = J
        M[:n, n] = -chi
        M[n, :n] = 2 * chi
        rhs = np.concatenate([-F, [-G]])
        try:
            d = np.linalg.solve(M, rhs)
        except np.linalg.LinAlgError:
            return chi, mu, False, err
        chi = chi + d[:n]
        mu = mu + d[n]
    F, G = residual(chi, mu, H, g, g12, N, prt)
    return chi, mu, False, max(np.abs(F).max(), abs(G))


def initial_guess(theta, m0, g, L, N, j0=None, w=2.0):
    """Localized guess built from the band-0 Bloch state at the bifurcation edge.

    g>0: soliton bifurcates from the TOP of band 0 (k=pi at theta=0) into the gap.
    g<0: from the BOTTOM of band 0 (k=0).
    """
    if j0 is None:
        j0 = L // 2
    kstar = np.pi if g > 0 else 0.0
    w_, v_ = np.linalg.eigh(h_k(kstar, theta, m0))
    u = v_[:, 0].real
    if np.abs(u).max() < 1e-12:
        u = v_[:, 0].imag
    u = u / np.linalg.norm(u)
    j = np.arange(L)
    env = np.cosh((j - j0) / w) ** -1
    phase = np.cos(kstar * j)
    chi = np.zeros(2 * L)
    chi[0::2] = env * phase * u[0]
    chi[1::2] = env * phase * u[1]
    chi *= np.sqrt(N / (chi @ chi))
    return chi, float(w_[0])


def band_edges(theta, m0, n=801):
    ks = np.linspace(-np.pi, np.pi, n)
    e = np.array([np.linalg.eigvalsh(h_k(k, theta, m0))[0] for k in ks])
    return e.min(), e.max(), ks[e.argmax()]


def envelope_seed(theta, m0, g, L, N, j0, width):
    """Localized seed built on the band-0 Bloch state at the bifurcating edge.

    g>0 (repulsive): the soliton bifurcates from the TOP of band 0 into the gap,
    which for this model is at k=pi -> a STAGGERED envelope.
    g<0 (attractive): from the BOTTOM (k=0) -> an unstaggered envelope.
    """
    kstar = band_edges(theta, m0)[2] if g > 0 else 0.0
    w_, v_ = np.linalg.eigh(h_k(kstar, theta, m0))
    u = v_[:, 0]
    u = u.real if np.abs(u.real).max() >= np.abs(u.imag).max() else u.imag
    u = u / np.linalg.norm(u)
    j = np.arange(L)
    env = np.cosh((j - j0) / width) ** -1 * np.cos(kstar * j)
    chi = np.zeros(2 * L)
    chi[0::2] = env * u[0]
    chi[1::2] = env * u[1]
    return chi * np.sqrt(N / (chi @ chi))


def is_localized(chi, L, thresh=0.5):
    rho = chi[0::2] ** 2 + chi[1::2] ** 2
    rho = rho / rho.sum()
    z = abs(np.sum(rho * np.exp(2j * np.pi * np.arange(L) / L)))
    return z > thresh


def solve_at(theta, m0, g, g12, N, L, target=None):
    """Find a localized soliton at one theta.

    NOTE: do not seed from the band edge and continue up in N -- at small N the
    solution is broader than the ring and Newton lands on the DELOCALIZED nonlinear
    Bloch branch (uniform density), which is a different solution at the same N and
    stays uniform under continuation. Seed localized, at full N, instead.
    """
    if target is None:
        target = L // 2
    lo, hi, _ = band_edges(theta, m0)
    mu_seeds = [hi + 0.14, hi + 0.5, hi + 0.02] if g > 0 else [lo - 0.5, lo - 0.15, lo - 1.5]
    for width in (1.5, 1.0, 2.5, 0.6, 4.0):
        for mu0 in mu_seeds:
            chi0 = envelope_seed(theta, m0, g, L, N, target, width)
            chi, mu, ok, err = newton(chi0, mu0, theta, m0, g, g12, N, L)
            if ok and is_localized(chi, L):
                return chi, mu, True
    return None, None, False


def com_resta(chi, L):
    """Center of mass on a ring via the Resta phase estimator, in unit cells."""
    rho = chi[0::2] ** 2 + chi[1::2] ** 2
    rho = rho / rho.sum()
    j = np.arange(L)
    z = np.sum(rho * np.exp(2j * np.pi * j / L))
    return (L / (2 * np.pi)) * np.angle(z)


def unwrap_step(x_new, x_prev, L):
    """Advance x_prev by the increment to x_new, taken mod L and chosen in [-L/2, L/2).

    com_resta returns a phase in [-L/2, L/2), so the raw values are NOT in [0, L);
    work with the increment only.
    """
    d = (x_new - x_prev) % L
    if d > L / 2:
        d -= L
    return x_prev + d


def track_cycle(m0, g, g12, N, L=60, nth=721, verbose=False):
    """Continue the soliton over theta in [0, 2pi]; return theta, x_c (unwrapped), mu."""
    thetas = np.linspace(0, 2 * np.pi, nth)
    chi, mu, ok = solve_at(0.0, m0, g, g12, N, L)
    if not ok:
        return None
    xs, mus, errs = [], [], []
    x = com_resta(chi, L)
    x0 = x
    for i, th in enumerate(thetas):
        chi, mu, ok, err = newton(chi, mu, th, m0, g, g12, N, L)
        if not ok:
            if verbose:
                print(f"    Newton failed at theta={th:.4f} (err={err:.2e})")
            return None
        xr = com_resta(chi, L)
        x = unwrap_step(xr, x, L) if i else xr
        xs.append(x); mus.append(mu); errs.append(err)
    xs = np.array(xs)
    return thetas, xs - xs[0], np.array(mus), max(errs)
