"""
Fundamental solution (Green's function) of the wave equation in n spatial
dimensions. For an impulsive point source delta(x) delta(t) at origin,

       u_tt - c^2 nabla^2 u = delta(x) delta(t),    u(.,t<0) = 0.

Standard closed forms (M. Riesz, Hadamard; see e.g. Evans "PDE", Sec. 2.4):

n = 1:   G(x,t) = (1 / 2 c) * H(c t - |x|).               (whole interior)
n = 2:   G(x,t) = (1 / 2 pi c) * H(c t - r) / sqrt(c^2 t^2 - r^2).
n = 3:   G(x,t) = delta(c t - r) / (4 pi c r).            (sharp shell, HUYGENS)
n = 4:   G(x,t) = (1 / (2 pi^2 c)) * H(c t - r) * (c t)
                     / (c^2 t^2 - r^2)^{3/2}.
n = 5:   sharp shell again (Huygens).
... in general: HUYGENS' principle holds for ODD n >= 3, FAILS for EVEN n.

The 4D Green's function has a *tail*: after the wavefront passes a fixed
observer, the disturbance does NOT vanish.  This is the auditory
signature unique to even-dimensional propagation media.
"""

import numpy as np


def green_4d(r: np.ndarray, t: np.ndarray, c: float = 343.0) -> np.ndarray:
    """G_4(r, t) for a delta-pulse point source at origin in 4 spatial dim.
    Convention: returns 0 outside the past light cone.
    Shape-broadcast: r and t can be arrays of compatible shape."""
    r = np.asarray(r)
    t = np.asarray(t)
    inside = (c * t > r) & (t > 0)
    out = np.zeros_like(np.broadcast_arrays(r, t)[0], dtype=float)
    rb, tb = np.broadcast_arrays(r, t)
    inside = (c * tb > rb) & (tb > 0)
    if not np.any(inside):
        return out
    denom = (c * c * tb * tb - rb * rb) ** 1.5
    coef  = c * tb / (2.0 * np.pi ** 2 * c)
    out_safe = np.where(inside, coef / np.where(inside, denom, 1.0), 0.0)
    return out_safe


def green_3d_smeared(r: np.ndarray, t: np.ndarray, c: float = 343.0,
                     sigma: float = 5e-4) -> np.ndarray:
    """3D Green's function delta(c t - r)/(4 pi c r), regularized by
    replacing the delta with a narrow Gaussian of width sigma so we can
    plot it next to the 4D one on the same axes."""
    rb, tb = np.broadcast_arrays(r, t)
    arg = (c * tb - rb)
    val = np.exp(-arg * arg / (2 * sigma * sigma)) / (sigma * np.sqrt(2 * np.pi))
    val = val / (4.0 * np.pi * c * np.where(rb > 0, rb, 1.0))
    return np.where(rb > 0, val, 0.0)


def signal_from_4d_source(observer_r3: np.ndarray, source_w_offset: float,
                          times: np.ndarray, c: float = 343.0) -> np.ndarray:
    """The pressure recorded by a 3D microphone at 3D position
    observer_r3 (relative to the source's projection onto our slice)
    when a delta-pulse is emitted at t=0 by a point source located in
    4D at (0, 0, 0, source_w_offset).  The microphone integrates the
    4D Green's function evaluated at (r_4 = sqrt(|observer|^2 + w^2), t)."""
    r3 = float(np.linalg.norm(observer_r3))
    r4 = np.sqrt(r3 * r3 + source_w_offset * source_w_offset)
    return green_4d(np.full_like(times, r4), times, c=c)
