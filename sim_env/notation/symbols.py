"""
Extended notation introduced by this research environment.

Whenever existing math notation is awkward or missing for a concept we
need, we define a new symbol here with a precise mathematical
definition. Every symbol has: name, glyph, signature, definition,
motivation.

This file is the canonical registry. Code elsewhere imports operators
from here.
"""

import numpy as np


# ---------------------------------------------------------------------------
#  D[R]  --  "Isoclinic Defect" of a 4D rotation R in SO(4)
# ---------------------------------------------------------------------------
#
#  Glyph:        𝔇(R)        (Fraktur D)
#  Signature:    SO(4)  ->  R_{>=0}
#  Definition:   Any R in SO(4) decomposes uniquely (up to ordering) into a
#                pair of independent rotations through angles (theta_1, theta_2)
#                in two orthogonal invariant 2-planes. Define
#
#                    D(R) := | theta_1 - theta_2 |     (in radians, in [0, pi])
#
#                R is "isoclinic" iff D(R) = 0; "simple" iff min(|t1|,|t2|) = 0.
#  Motivation:   No commonly used scalar in the standard SO(4) literature
#                cleanly captures "how far a 4D rotation is from being
#                isoclinic". This single number is critical because isoclinic
#                rotations are the ones with constant point-speed under the
#                rotation -- a property genuinely unique to 4D, with no analog
#                in SO(3).

def isoclinic_defect(R: np.ndarray) -> float:
    """Compute D(R) for R in SO(4). See definition above."""
    if R.shape != (4, 4):
        raise ValueError("D(R) is defined only on SO(4)")
    # Eigenvalues of an SO(4) matrix come in two complex-conjugate pairs
    # e^{+/- i theta_1}, e^{+/- i theta_2}.
    eigs = np.linalg.eigvals(R)
    angles = np.sort(np.abs(np.angle(eigs)))   # 4 values, paired
    # take one representative from each conjugate pair
    t1 = angles[0]   # smallest |angle|
    t2 = angles[2]   # next distinct (after the pair)
    return float(abs(t1 - t2))


# ---------------------------------------------------------------------------
#  Hodge-like "lift" operator  L_n[v]:  R^3 -> R^n  with metadata trace
# ---------------------------------------------------------------------------
#  Just a convenience embedding -- not new math, but tagged so experiment
#  logs can show "this 3D vector was lifted into 4D at axis index k".

def lift(v3: np.ndarray, n: int = 4, axis: int = 3, value: float = 0.0) -> np.ndarray:
    out = np.zeros(n)
    j = 0
    for i in range(n):
        if i == axis:
            out[i] = value
        else:
            out[i] = v3[j]
            j += 1
    return out
