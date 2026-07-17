"""
Model of Tao, Wang & Xu, Nat. Commun. (2026), doi:10.1038/s41467-026-73460-y.

Discrete nonlinear model, their Eq. (2):
    H_lin(k) = (m_z + J1 cos k) sigma_z + J1p sin k sigma_y + J2 sigma_x
    m_z = m0 + cos(theta),  J1 = J1p = 1,  J2 = sin(theta)

Their Eq. (1), DNLS:
    i dpsi_{sigma j}/dt = sum H_lin psi + V_{sigma j} psi_{sigma j}
    V_{sigma j} = g |psi_{sigma j}|^2 + g12 |psi_{sigma-bar j}|^2

Stationary solitons: psi = exp(-i mu t) chi  ->  H chi + V(chi) chi = mu chi.

numpy only. No scipy.
"""
import numpy as np

SX = np.array([[0, 1], [1, 0]], dtype=float)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=float)


# ---------------------------------------------------------------- k-space
def h_k(k, theta, m0, J1=1.0, J1p=1.0):
    mz = m0 + np.cos(theta)
    J2 = np.sin(theta)
    return (mz + J1 * np.cos(k)) * SZ + J1p * np.sin(k) * SY + J2 * SX


def chern_lowest(m0, n=60, J1=1.0, J1p=1.0):
    """Fukui-Hatsugai-Suzuki Chern number of the lowest band over the (k, theta) torus."""
    ks = np.linspace(0, 2 * np.pi, n, endpoint=False)
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    u = np.empty((n, n, 2), dtype=complex)
    for a, k in enumerate(ks):
        for b, t in enumerate(th):
            w, v = np.linalg.eigh(h_k(k, t, m0, J1, J1p))
            u[a, b] = v[:, 0]                      # lowest band

    def link(x, y):
        z = np.vdot(x, y)
        return z / abs(z)

    F = 0.0
    for a in range(n):
        for b in range(n):
            a1, b1 = (a + 1) % n, (b + 1) % n
            U1 = link(u[a, b],  u[a1, b])
            U2 = link(u[a1, b], u[a1, b1])
            U3 = link(u[a1, b1], u[a, b1])
            U4 = link(u[a, b1], u[a, b])
            F += np.angle(U1 * U2 * U3 * U4)
    return F / (2 * np.pi)


def gap_lowest(theta, m0, n=400):
    """Min gap between band 0 and band 1 over k, and the band-0 edges."""
    ks = np.linspace(-np.pi, np.pi, n)
    e = np.array([np.linalg.eigvalsh(h_k(k, theta, m0)) for k in ks])
    return (e[:, 1] - e[:, 0]).min(), e[:, 0].min(), e[:, 0].max()


# ---------------------------------------------------------------- real space
def h_real(theta, m0, L, J1=1.0, J1p=1.0, pbc=True):
    """Real-space H. Ordering: index = 2*j + (sigma-1), sigma in {1,2}.

    H(k) = A + B e^{ik} + B^dag e^{-ik} with
      A = J2 sx + mz sz,  B = (J1/2) sz - (i J1p/2) sy
    Both A and B are REAL, so H is real symmetric and solitons can be taken real.
    """
    mz = m0 + np.cos(theta)
    J2 = np.sin(theta)
    A = J2 * SX + mz * SZ
    B = (J1 / 2) * SZ - (1j * J1p / 2) * SY
    assert np.allclose(B.imag, 0), "B should be real"
    B = B.real
    H = np.zeros((2 * L, 2 * L))
    for j in range(L):
        H[2 * j:2 * j + 2, 2 * j:2 * j + 2] += A
        jp = (j + 1) % L
        if jp == 0 and not pbc:
            continue
        H[2 * j:2 * j + 2, 2 * jp:2 * jp + 2] += B
        H[2 * jp:2 * jp + 2, 2 * j:2 * j + 2] += B.T
    return H


def verify_real_space(theta, m0, L=64):
    """Check real-space spectrum (PBC) matches the k-space bands."""
    ev = np.linalg.eigvalsh(h_real(theta, m0, L))
    ks = 2 * np.pi * np.arange(L) / L
    ek = np.sort(np.concatenate([np.linalg.eigvalsh(h_k(k, theta, m0)) for k in ks]))
    return np.abs(ev - ek).max()


if __name__ == "__main__":
    import sys, platform
    print(f"env: CPython {platform.python_version()} {platform.machine()} {sys.platform} | numpy {np.__version__}\n")

    print("Real-space vs k-space spectrum (max |diff|, PBC, L=64):")
    for th in (0.0, 1.0, np.pi, 4.0):
        for m0 in (1.0, 1.3):
            print(f"  theta={th:5.2f} m0={m0}: {verify_real_space(th, m0):.3e}")

    print("\nChern number of the lowest band over the (k,theta) torus")
    print("  paper: C=1 for -2<m0<0;  C=-1 for 0<m0<2;  C=0 otherwise")
    for m0 in (-2.5, -1.0, -0.5, 0.5, 1.0, 1.3, 1.9, 2.5):
        print(f"  m0={m0:5.1f} -> C = {chern_lowest(m0):+.6f}")

    print("\nBand-0/1 gap over the pump cycle (m0=1):")
    for th in np.linspace(0, 2 * np.pi, 9):
        g, lo, hi = gap_lowest(th, 1.0)
        print(f"  theta={th:5.2f}: min gap={g:7.4f}   band0 in [{lo:7.4f}, {hi:7.4f}]")
