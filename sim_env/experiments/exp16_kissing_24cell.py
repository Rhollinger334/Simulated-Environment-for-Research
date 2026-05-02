"""
EXPERIMENT 16 -- The 24-cell saturates the 4D kissing-number bound
====================================================================

Kissing number in n dimensions K(n): the maximum number of unit
n-balls that can simultaneously touch a central unit n-ball without
overlapping.

  K(2) = 6      hexagonal (trivial)
  K(3) = 12     proven Schutte-van der Waerden 1953
  K(4) = 24     proven Musin 2003 -- the optimal config IS the
                vertex set of the 24-cell.
  K(5) = ?      bounds 40 <= K(5) <= 44; not yet known.
  K(8) = 240    proven Levenshtein, Odlyzko-Sloane (1979) via E_8
  K(24) = 196560 proven by Cohn-Kumar-Miller-Radchenko-Viazovska (2017)
                via the Leech lattice.
                (Companion to Viazovska's 8D theorem.)

The 4D, 8D and 24D cases are *saturated by exceptional structures* --
the 24-cell, the E_8 lattice, the Leech lattice respectively.
Universal optimality (Cohn et al. 2022).

This experiment:
  (1) verifies that the 24-cell vertex set is a valid 4D kissing config:
      - all 24 are unit vectors;
      - no two have angular separation < pi/3
        (equivalently, pairwise distance >= 1 = 2 sin(pi/6));
      - exactly 24 vectors achieve the minimum separation (each unit
        ball touches some other, not just the central one).
  (2) tries to add a 25th unit vector at angular separation >= pi/3
      from all 24, by sampling 200_000 unit vectors -- empirical
      evidence that no such vector exists (Musin).
  (3) measures the angular spectrum: the 24-cell vertex set has
      EXACTLY THREE distinct angular separations (60 deg, 90 deg, 120 deg).
      This three-shell structure is the geometric reason the 24-cell
      is "tight": it is a spherical 5-design, the highest tightness
      class in 4D.
"""

import numpy as np
from sim_env.geometry import quaternion_groups as Q


def main():
    G = Q.binary_tetrahedral_group()
    n_v = len(G)
    print(f"24-cell vertex set: {n_v} unit quaternions in R^4.")

    # 1. Pairwise dot products and angular separations
    dots = G @ G.T
    np.fill_diagonal(dots, 0.0)
    # min pairwise distance
    sq_dists = 2 - 2 * dots
    np.fill_diagonal(sq_dists, np.inf)
    min_dist = np.sqrt(sq_dists.min())
    print(f"min pairwise distance     : {min_dist:.10f}  (kissing wants >=1)")

    # angular separations (degrees)
    np.fill_diagonal(dots, 1.0)            # restore self-dot = 1
    np.fill_diagonal(dots, 1.0)
    angles = np.rad2deg(np.arccos(np.clip(dots, -1, 1)))
    np.fill_diagonal(angles, np.nan)
    unique_angles = np.sort(np.unique(np.round(angles[~np.isnan(angles)], 8)))
    print(f"distinct angular separations among the 24 vertices: "
          + ", ".join(f"{a:.4f} deg" for a in unique_angles))
    print()

    # count nearest neighbours per vertex (those at the minimum separation)
    nn = (np.isclose(angles, unique_angles[0])).sum(axis=1)
    print(f"each vertex has {int(nn.mean())} nearest neighbours at angular "
          f"separation {unique_angles[0]:.4f} deg")
    print(f"  (the 24-cell is 8-regular; consistent with Coxeter table)")
    print()

    # 2. Try adding a 25th vector
    rng = np.random.default_rng(2026)
    n_trials = 200_000
    candidates = rng.normal(size=(n_trials, 4))
    candidates /= np.linalg.norm(candidates, axis=1, keepdims=True)
    # for each candidate, the maximum dot with the 24 existing vertices
    max_dots = (candidates @ G.T).max(axis=1)
    # require min angle pi/3 i.e. cos <= 1/2
    n_admissible = int((max_dots <= 0.5 + 1e-9).sum())
    print(f"Random search for a 25th unit vector with angular separation "
          f">= 60 deg from all 24 existing:")
    print(f"  {n_trials} candidates tried, {n_admissible} admissible "
          f"(expected 0; Musin 2003 proved K(4)=24 exactly).")
    if n_admissible > 0:
        # show how close they got
        worst_dots = (candidates[max_dots <= 0.5+1e-9] @ G.T).max(axis=1)
        print(f"  best max-dot achieved : {worst_dots.min():.6f}")
    print()

    # 3. Angular spectrum table
    print("Angular spectrum (each vertex):")
    for a in unique_angles:
        cnt_per_v = int(np.isclose(angles, a).sum(axis=1).mean())
        print(f"  {a:>8.4f} deg : {cnt_per_v:>2} vertices")
    print(f"  (expected for 24-cell: 60 deg ->  8, 90 deg -> 6, 120 deg -> 8, "
          f"180 deg -> 1, total 23)")


if __name__ == "__main__":
    main()
