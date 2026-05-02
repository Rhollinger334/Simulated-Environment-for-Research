"""
EXPERIMENT 17 -- The E_8 lattice: 8-D analog of the 24-cell
=============================================================

The exceptional dimensions are 1, 2, 4, 8, 24.  In each, sphere
packing is solved by an exceptional structure and the kissing number
is known exactly:
   K(2) = 6           hexagonal
   K(4) = 24          24-cell (Musin 2003)
   K(8) = 240         E_8 lattice (Levenshtein, Odlyzko-Sloane 1979)
   K(24) = 196560     Leech lattice (Cohn-Kumar-Miller-Radchenko-Viazovska
                       2017)

Maryna Viazovska won the Fields Medal (2022) for proving that E_8
gives the densest sphere packing in 8 dimensions (her 2016 result),
and was the lead author on the 24-D Leech result.

We construct the 240 minimal vectors of E_8 explicitly, verify:
  - their count (112 + 128 = 240),
  - their common length (sqrt(2)),
  - the kissing-config invariants,
  - the packing density pi^4 / 384  (= 0.2536695...).

Construction (Conway & Sloane "Sphere Packings, Lattices and Groups",
Sec. 4.8):
  Type D_8 vectors  : (+-1, +-1, 0, 0, 0, 0, 0, 0) and all permutations
                      (112 vectors).
  Half-integer       : (+-1/2, +-1/2, +-1/2, +-1/2, +-1/2, +-1/2, +-1/2,
                       +-1/2) with EVEN number of minus signs
                      (128 vectors).
  Total 240.
"""

from itertools import combinations, product
import numpy as np


def e8_minimal_vectors() -> np.ndarray:
    """Return the 240 minimal vectors of E_8 (the kissing config), each
    of squared norm 2."""
    out = []
    # Type-D8 part: pairs of +-1 at distinct positions
    for i, j in combinations(range(8), 2):
        for si, sj in product([-1, 1], repeat=2):
            v = np.zeros(8)
            v[i] = si; v[j] = sj
            out.append(v)
    # Half-integer part with even number of minus signs
    for signs in product([-1, 1], repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            out.append(np.array(signs, dtype=float) / 2.0)
    return np.array(out)


def main():
    R = e8_minimal_vectors()
    print(f"Constructed {len(R)} minimal vectors  (expected 240).")

    sq_norms = (R * R).sum(axis=1)
    print(f"All vectors squared-norm 2? min={sq_norms.min():.10f}, "
          f"max={sq_norms.max():.10f}")

    # Pairwise structure
    G = R @ R.T
    np.fill_diagonal(G, np.nan)
    distinct_inner_products = np.sort(np.unique(np.round(
        G[~np.isnan(G)], 8)))
    print(f"distinct inner products (off-diagonal): "
          + ", ".join(f"{x:+g}" for x in distinct_inner_products))
    print(f"  Theory: {{-2, -1, 0, +1, +2}}  (root system A1+A1+A1+...) ")
    print()

    # Kissing config: rescale so all vectors are unit -> kissing balls
    # have radius 1/2; require min pairwise distance >= 1.
    R_unit = R / np.sqrt(2.0)
    G2 = R_unit @ R_unit.T
    sq_dists = 2 - 2 * G2
    np.fill_diagonal(sq_dists, np.inf)
    min_dist = np.sqrt(sq_dists.min())
    print(f"After unit-rescaling: min pairwise distance = {min_dist:.10f}  "
          f"(kissing demands >= 1)")
    np.fill_diagonal(G2, 1.0)
    angles = np.rad2deg(np.arccos(np.clip(G2, -1, 1)))
    nn_per_vec = int(np.isclose(angles, 60.0).sum() / len(R))
    print(f"each vector has {nn_per_vec} nearest neighbours at 60 deg "
          f"(theory: 56)")
    print()

    # Empirical kissing-bound check: try to add a 241st vector
    rng = np.random.default_rng(2026)
    n_trials = 50_000
    cand = rng.normal(size=(n_trials, 8))
    cand /= np.linalg.norm(cand, axis=1, keepdims=True)
    max_dot = (cand @ R_unit.T).max(axis=1)
    n_ok = int((max_dot <= 0.5 + 1e-9).sum())
    print(f"Random search for a 241st unit 8-vector with min angle 60 deg "
          f"to all 240:")
    print(f"  {n_trials} candidates tried, {n_ok} admissible.")
    print(f"  (Theory: K(8) = 240 exactly, Viazovska 2016 + Cohn et al. 2017)")
    print()

    # Sphere-packing density of E_8.
    # E_8 is a unimodular even self-dual lattice with covolume 1, minimum
    # squared norm 2, so balls of radius sqrt(2)/2 give the packing.
    # Density = V_8(sqrt(2)/2) / 1
    #         = pi^4 (sqrt(2)/2)^8 / Gamma(5)
    #         = pi^4 / 16 / 24  =  pi^4 / 384.
    density_exact = np.pi**4 / 384.0
    print(f"E_8 sphere-packing density = pi^4 / 384")
    print(f"                            = {density_exact:.10f}")
    print(f"  Viazovska (2016) PROVED this is the maximum density in R^8.")
    print(f"  Compare with the best 3-D density: pi/(3*sqrt(2)) = "
          f"{np.pi/(3*np.sqrt(2)):.10f}")
    print()

    # The 24-cell sits inside E_8 -- the D_4 sublattice
    # (vectors whose first 4 coords lie in 24-cell pattern, last 4 are 0,
    #  scaled appropriately) is naturally embedded.  Easy check: do the
    # 24-cell vertices appear among the type-D8 part with nonzero only in
    # the first 4 coordinates?
    in_d4 = []
    for v in R:
        if (v[4:] == 0).all() and (v[:4] != 0).any():
            in_d4.append(v[:4])
    in_d4 = np.array(in_d4)
    print(f"E_8 vectors with nonzeros only in first 4 coords: {len(in_d4)}")
    norms = np.linalg.norm(in_d4, axis=1)
    print(f"all of squared-norm 2 (i.e. = 24-cell vertex set scaled): "
          f"{np.allclose(norms, np.sqrt(2))}")
    print(f"-> the 24-cell sits inside E_8 as the D_4 root system.")


if __name__ == "__main__":
    main()
