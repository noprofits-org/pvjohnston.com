"""
Single-band Wannier functions on a ring via the projected Resta position operator.

Z = P U P with U = diag(exp(2i pi j / L)) (x) I_2, P = projector onto band 0.
Eigenvectors of Z restricted to band 0 are the Wannier functions; the phases of
its eigenvalues give the Wannier centers, (L/2pi) arg(z_n).
"""
import numpy as np
from soliton_model import h_real


def band0_projector_states(theta, m0, L):
    """The L lowest eigenvectors (band 0) of the PBC real-space Hamiltonian."""
    H = h_real(theta, m0, L)
    w, v = np.linalg.eigh(H)
    return w[:L], v[:, :L]          # (L,), (2L, L)


def wannier(theta, m0, L):
    """Return (centers, W) with centers sorted ascending and W[:, n] the nth Wannier fn."""
    _, V = band0_projector_states(theta, m0, L)
    j = np.arange(L)
    phase = np.exp(2j * np.pi * j / L)
    u = np.repeat(phase, 2)                      # site index = 2j + sigma
    Z = V.conj().T @ (u[:, None] * V)            # L x L
    z, S = np.linalg.eig(Z)
    centers = (L / (2 * np.pi)) * np.angle(z) % L
    order = np.argsort(centers)
    centers = centers[order]
    W = V @ S[:, order]                          # (2L, L)
    # fix gauge: make each Wannier function real up to a global phase, unit norm
    out = np.zeros((2 * L, L))
    imag_res = 0.0
    for n in range(L):
        w_ = W[:, n]
        k = np.argmax(np.abs(w_))
        w_ = w_ * np.exp(-1j * np.angle(w_[k]))
        # Residual imaginary part is an O(1/L) artifact of the Resta operator, not
        # an error: these seed Newton, they are not the final answer. Record it.
        imag_res = max(imag_res, np.abs(w_.imag).max() / max(np.abs(w_).max(), 1e-300))
        w_ = w_.real
        out[:, n] = w_ / np.linalg.norm(w_)
    return centers, out, imag_res


def wannier_spread(W, L, n):
    """participation ratio of Wannier function n, in unit cells"""
    rho = W[0::2, n] ** 2 + W[1::2, n] ** 2
    rho = rho / rho.sum()
    return 1.0 / (rho ** 2).sum()


if __name__ == "__main__":
    L = 60
    for m0 in (1.0, 1.3):
        print(f"\nm0 = {m0}")
        print(f"  {'theta':>6} {'center spacing':>15} {'spread (cells)':>15} {'center of W_0':>14} {'imag res':>12}")
        for th in (0.0, np.pi / 2, np.pi, 3 * np.pi / 2):
            c, W, ir = wannier(th, m0, L)
            sp = np.diff(c)
            print(f"  {th:6.3f} {sp.mean():15.6f} {wannier_spread(W, L, 0):15.4f} {c[0]:14.6f} {ir:12.2e}")
    # At theta=pi both bands are flat -> Wannier functions should be maximally compact
    print("\ntheta=pi, m0=1 (flat band): density of W_0 on each cell")
    c, W, ir = wannier(np.pi, 1.0, 60)
    rho = W[0::2, 0] ** 2 + W[1::2, 0] ** 2
    nz = np.where(rho > 1e-10)[0]
    print(f"  nonzero on cells {nz}, weights {np.array2string(rho[nz], precision=6)}")
