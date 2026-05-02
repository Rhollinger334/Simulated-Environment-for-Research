"""
Physics in n spatial dimensions (with focus on n=4).

All formulas derived from first principles -- not numerical fits.
References for each result are noted inline.
"""

import numpy as np
from math import pi, gamma, sqrt
from sim_env.core import constants as C


# ---------------------------------------------------------------------------
# Geometry of the n-sphere
# ---------------------------------------------------------------------------

def n_ball_volume(n: int, R: float = 1.0) -> float:
    """Volume of a ball of radius R in R^n.  V_n(R) = pi^{n/2} / Gamma(n/2 + 1) * R^n.
    (Standard result; see e.g. Folland, "Real Analysis", App. A.)"""
    return pi**(n/2) / gamma(n/2 + 1) * R**n


def n_sphere_surface(n: int, R: float = 1.0) -> float:
    """Surface 'area' of S^{n-1} embedded in R^n (radius R).
    S_{n-1}(R) = 2 pi^{n/2} / Gamma(n/2) * R^{n-1}."""
    return 2.0 * pi**(n/2) / gamma(n/2) * R**(n-1)


# ---------------------------------------------------------------------------
# Gravitational / Coulomb potential by Gauss's law in n dimensions
# ---------------------------------------------------------------------------
# The flux of a 1/r^{n-1} field through S^{n-1} of radius r is
#    Phi = E(r) * S_{n-1}(r) = E(r) * (2 pi^{n/2}/Gamma(n/2)) r^{n-1}
# so for a point source enclosed, E(r) ~ 1/r^{n-1}, and the potential
# (its integral) goes as
#    n=2:  V ~ ln r
#    n=3:  V ~ -1/r
#    n=4:  V ~ -1/r^2
#    n>=4: V ~ -1/r^{n-2}.

def coulomb_potential_nd(r: float, n: int, k: float = 1.0) -> float:
    """Coulomb / Newton potential in n spatial dimensions, point source."""
    if n == 2:
        return k * np.log(r)
    return -k / r**(n-2)


# ---------------------------------------------------------------------------
# Effective radial potential for a particle of angular momentum L
#  V_eff(r) = V(r) + L^2 / (2 m r^2)
# In 4D Newtonian/Coulomb (V ~ -k/r^2) the centrifugal term and the attractive
# term BOTH go like 1/r^2.  This is the famous "fall to center" regime
# (Landau & Lifshitz, Vol. 3, Sec. 35).  Stable orbits/atoms do not exist
# for sufficiently strong attraction.
# ---------------------------------------------------------------------------

def fall_to_center_threshold(m: float, L: float) -> float:
    """In 4D with V = -k/r^2, the particle is captured when k > L^2/(2m).
    Returns the critical k_c = L^2 / (2 m)."""
    return L * L / (2.0 * m)


# ---------------------------------------------------------------------------
# Hydrogen-like atom in D spatial dimensions with V = -e^2/(4 pi eps_0 r)
# (i.e. keeping the 3D-form Coulomb potential, NOT the Gauss-law one).
# Exact bound-state energies (Nieto 1979; Yanez & Dehesa 1994):
#    E_{n,l} = -E_h * Z^2 / (2 * (n + (D - 3)/2)^2 )
# where n = n_r + l + 1 is the principal quantum number, E_h = Hartree.
# ---------------------------------------------------------------------------

def hydrogenic_energy(n: int, D: int = 3, Z: int = 1) -> float:
    """Hydrogen-like bound-state energy (Joules) in D spatial dimensions
    assuming a 1/r Coulomb law (i.e. the operator, not Gauss's law)."""
    nu = n + (D - 3) / 2.0
    return -C.E_h * Z * Z / (2.0 * nu * nu)
