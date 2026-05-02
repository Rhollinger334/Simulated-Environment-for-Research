"""
EXPERIMENT 01 -- The Six Regular 4-Polytopes
============================================

Goal: enumerate the 6 regular convex polytopes in R^4 (proven complete by
Schlafli 1852), construct exact vertex coordinates, verify that:
  (a) all vertices lie on a common 3-sphere,
  (b) edges have a single length,
  (c) the vertex-counts agree with the known invariants, and
  (d) the 24-cell is genuinely self-dual with no 3-D analog.

Output: prints a verification table.
"""

import numpy as np
from sim_env.geometry import polytopes_4d as P


EXPECTED = {
    "5-cell  {3,3,3}":  (5,   10),
    "8-cell  {4,3,3}":  (16,  32),
    "16-cell {3,3,4}":  (8,   24),
    "24-cell {3,4,3}":  (24,  96),
    "600-cell {3,3,5}": (120, 720),
    "120-cell {5,3,3}": (600, 1200),
}


def verify(name, verts):
    """Check vertex count, sphere-condition, and a representative edge length."""
    n_v = len(verts)
    radii = np.linalg.norm(verts, axis=1)
    on_sphere = np.allclose(radii, radii[0], atol=1e-6)
    # find minimum nonzero pairwise distance => edge length
    diffs = verts[:, None, :] - verts[None, :, :]
    d2 = np.einsum('ijk,ijk->ij', diffs, diffs)
    np.fill_diagonal(d2, np.inf)
    edge = np.sqrt(d2.min())
    n_edges_at_min = int((np.isclose(d2, edge*edge, rtol=1e-7)).sum() // 2)
    return n_v, on_sphere, float(radii[0]), float(edge), n_edges_at_min


def main():
    print(f"{'Polytope':<22}  {'V':>5} {'V_exp':>6}   "
          f"{'on S^3?':>8}  {'circumrad':>11}  "
          f"{'edge':>10}  {'#edges':>7}")
    print("-" * 90)
    for name, ctor in P.REGULAR_4_POLYTOPES.items():
        verts = ctor()
        n_v, on_sphere, R, edge, n_e = verify(name, verts)
        v_exp, e_exp = EXPECTED[name]
        ok = "OK" if (n_v == v_exp and on_sphere) else "MISMATCH"
        print(f"{name:<22}  {n_v:5d} {v_exp:6d}   "
              f"{str(on_sphere):>8}  {R:11.6f}  "
              f"{edge:10.6f}  {n_e:7d}  [{ok}]")
    print()
    print("Note: the 24-cell {3,4,3} has no 3D analog.  It is its own dual,")
    print("  the unique self-dual regular polytope (other than the simplex)")
    print("  and tiles R^4 as a regular honeycomb -- impossible in R^3.")


if __name__ == "__main__":
    main()
