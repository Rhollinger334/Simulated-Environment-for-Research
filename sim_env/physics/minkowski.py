"""
Minkowski spacetime -- "time as the 4th dimension".

Signature convention: (-,+,+,+).  Coordinates: x = (ct, x, y, z).
Lorentz boosts and proper-time computations done from first principles.
"""

import numpy as np
from sim_env.core import constants as C


ETA = np.diag([-1.0, 1.0, 1.0, 1.0])    # metric tensor


def lorentz_boost_x(beta: float) -> np.ndarray:
    """Boost along +x with v = beta*c.  Acts on column 4-vector (ct,x,y,z)."""
    if not (-1.0 < beta < 1.0):
        raise ValueError("beta must be in (-1, 1)")
    g = 1.0 / np.sqrt(1.0 - beta * beta)
    return np.array([
        [    g, -g*beta, 0, 0],
        [-g*beta,    g,  0, 0],
        [   0,    0,    1, 0],
        [   0,    0,    0, 1],
    ])


def gamma_factor(beta: float) -> float:
    return 1.0 / np.sqrt(1.0 - beta * beta)


def proper_time(ct1: float, x1: np.ndarray, ct0: float, x0: np.ndarray) -> float:
    """Proper time elapsed along a straight worldline between two events.
    d tau = sqrt( -eta_{mu nu} dx^mu dx^nu ) / c."""
    dx = np.array([ct1 - ct0, *(x1 - x0)])
    s2 = -dx @ ETA @ dx     # = c^2 d tau^2 for a timelike interval
    if s2 < 0:
        raise ValueError("interval is spacelike, no proper time defined")
    return np.sqrt(s2) / C.c


def invariant_interval(dx: np.ndarray) -> float:
    """eta_{mu nu} dx^mu dx^nu  (sign indicates timelike < 0, lightlike == 0,
    spacelike > 0 in our convention)."""
    return float(dx @ ETA @ dx)
