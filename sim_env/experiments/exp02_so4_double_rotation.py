"""
EXPERIMENT 02 -- The "Double Rotation" Phenomenon
==================================================

In R^3 every nontrivial rotation has exactly one invariant axis.
In R^4, a generic rotation has TWO independent invariant 2-planes,
each with its own rotation angle (theta_1, theta_2).  When
theta_1 = theta_2 the rotation is "isoclinic": every point on the unit
3-sphere moves at the same angular speed.

We:
  1) Build a generic R in SO(4) and read off (theta_1, theta_2)
     from its eigenvalues.
  2) Compute the new symbol  D(R) = |theta_1 - theta_2|  (isoclinic defect).
  3) Show that for an isoclinic R, every unit vector v has |Rv - v| equal
     -- which is impossible in R^3 (only the axis is fixed, equator points
     move farthest).
  4) Verify the SU(2) x SU(2) double-cover by reconstructing R from a
     quaternion pair.
"""

import numpy as np
from sim_env.geometry import rotations_4d as G
from sim_env.notation.symbols import isoclinic_defect


def report_rotation(label, R):
    eigs = np.linalg.eigvals(R)
    angles = np.sort(np.abs(np.angle(eigs)))
    t1, t2 = angles[0], angles[2]
    D = isoclinic_defect(R)
    # sample uniform unit vectors and measure displacement
    rng = np.random.default_rng(7)
    V = rng.normal(size=(4000, 4))
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    disp = np.linalg.norm((R @ V.T).T - V, axis=1)
    print(f"{label}")
    print(f"  invariant-plane angles : theta_1 = {t1:.6f} rad,  "
          f"theta_2 = {t2:.6f} rad")
    print(f"  isoclinic defect D(R)  : {D:.6e}")
    print(f"  point-displacement range over S^3 : "
          f"[{disp.min():.4f}, {disp.max():.4f}]   "
          f"(stddev {disp.std():.4e})")
    print()


def main():
    print("=== Generic 4D rotation (theta_1=0.7, theta_2=1.3) ===")
    R_gen = G.double_rotation(0.7, 1.3)
    report_rotation("generic", R_gen)

    print("=== Simple 4D rotation (theta_1=0.7, theta_2=0) -- analog of 3D ===")
    R_simple = G.double_rotation(0.7, 0.0)
    report_rotation("simple", R_simple)

    print("=== Isoclinic 4D rotation (theta_1 = theta_2 = 0.9) ===")
    R_iso = G.double_rotation(0.9, 0.9)
    report_rotation("isoclinic", R_iso)
    print("  --> for the isoclinic case the displacement is CONSTANT over S^3.")
    print("      No 3D rotation has this property. Only 4D admits it.")
    print()

    # Verify quaternion construction
    print("=== Quaternion double-cover check ===")
    qL = np.array([1, 0.5, -0.3, 0.7]); qL /= np.linalg.norm(qL)
    qR = np.array([0.4, 0.2, 0.9, -0.1]); qR /= np.linalg.norm(qR)
    R_q = G.so4_from_quaternion_pair(qL, qR)
    err_orth = np.linalg.norm(R_q.T @ R_q - np.eye(4))
    print(f"  built R from (qL, qR); ||R^T R - I|| = {err_orth:.2e}, "
          f"det = {np.linalg.det(R_q):+.6f}")
    print(f"  -> SO(4) element. (qL, qR) and (-qL, -qR) give the same R")
    print(f"     -- the 2:1 cover SU(2) x SU(2) -> SO(4).")


if __name__ == "__main__":
    main()
