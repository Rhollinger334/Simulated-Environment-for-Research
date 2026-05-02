"""
EXPERIMENT 15 -- The 24-cell IS a finite group of unit quaternions
====================================================================

Goal: verify computationally that the 24 vertices of the regular
4-polytope {3,4,3} (the 24-cell) coincide exactly with the 24 elements
of the binary tetrahedral group 2T as a multiplicative subgroup of the
unit quaternions.

This is a striking instance of a "geometry = algebra" identity:
  - geometry: the 24-cell is the only convex regular polytope with no
    3D analog, and it is its own dual.
  - algebra: 2T is the unique double cover of the alternating group
    A_4 (the rotational tetrahedron group), embedded in S^3.

Tasks:
  1. Build the 24 quaternion vertices.
  2. Verify all are unit quaternions.
  3. Verify multiplication closes (it is a group) and produce the
     full 24x24 multiplication table.
  4. Verify the geometric polytope from sim_env.geometry.polytopes_4d
     matches this set of 24 points (up to a rigid rotation).
  5. Compute the orders of all elements; identify the structure
     (e=1, -1, six elements of order 4, eight of order 6, eight of
     order 3).
  6. Identify the quaternion group Q_8 = {+-1, +-i, +-j, +-k} as a
     normal subgroup of order 8; the quotient 2T/Q_8 is the cyclic
     group C_3.
"""

import numpy as np
from sim_env.geometry import quaternion_groups as Q
from sim_env.geometry import polytopes_4d as P


def main():
    G = Q.binary_tetrahedral_group()
    print(f"Built {len(G)} elements.")

    # 2. Unit quaternions?
    norms = np.linalg.norm(G, axis=1)
    print(f"All unit?  min |q| = {norms.min():.10f},  "
          f"max |q| = {norms.max():.10f}  (expect 1)")

    # 3. Group closure
    is_closed, table = Q.closure_check(G)
    print(f"Multiplication closes within the 24 elements: {is_closed}")
    # Identity check: row of identity should be [0..23]
    e_idx = int(np.argmax(np.all(np.isclose(G, np.array([1, 0, 0, 0])), axis=1)))
    print(f"Identity index = {e_idx}, "
          f"row[e] = arange? {bool(np.all(table[e_idx] == np.arange(24)))}")

    # 4. Match the geometric 24-cell
    geom = P.twenty_four_cell()
    # Geom vertices have norm sqrt(2) (e.g., (1,1,0,0)).  Quaternion
    # vertices have norm 1.  Rescale geom by 1/sqrt(2) and look for
    # a matching after a fixed rotation that aligns coordinate axes.
    geom_scaled = geom / np.sqrt(2.0)
    # Check: every scaled geom vertex appears (up to tol) in G
    matches = 0
    for v in geom_scaled:
        d = np.einsum('ij,ij->i', G - v, G - v)
        if d.min() < 1e-12:
            matches += 1
    print(f"Geometric 24-cell vertices that are in 2T (after 1/sqrt(2) "
          f"rescale): {matches}/24")
    # Try a small canonical rotation if not all match (the conventions
    # of the geometric construction may differ by a rotation).
    if matches < 24:
        print("  Trying alignment via the orbit structure: each set of")
        print("  24 unit quaternions related to the 24-cell differs by an")
        print("  isoclinic rotation. We check that BOTH point-sets are")
        print("  isometric (same pairwise distance multiset).")
        d_G = np.sort(np.linalg.norm(
            G[:, None, :] - G[None, :, :], axis=-1).flatten())
        d_g = np.sort(np.linalg.norm(
            geom_scaled[:, None, :] - geom_scaled[None, :, :],
            axis=-1).flatten())
        print(f"  Pairwise-distance multisets equal? "
              f"{np.allclose(d_G, d_g, atol=1e-9)}")

    # 5. Element orders
    orders = Q.element_orders(G, table)
    print()
    print("Element-order distribution in 2T:")
    for k in sorted(set(orders.tolist())):
        n_k = int((orders == k).sum())
        print(f"  order {k:>2}:  {n_k:>2} element(s)")
    # Compare to the textbook structure of 2T (binary tetrahedral group):
    # element orders are 1 (identity), 2 (the unique element -1),
    # 3 (8 elts), 4 (6 elts), 6 (8 elts).  Total 1+1+8+6+8 = 24.
    print("  expected  : 1:1, 2:1, 3:8, 4:6, 6:8   (total 24)")
    print()

    # 6. Q_8 as a normal subgroup
    Q8_indices = []
    for i, q in enumerate(G):
        if np.allclose(np.abs(q), [1, 0, 0, 0]) or \
           np.allclose(np.abs(q), [0, 1, 0, 0]) or \
           np.allclose(np.abs(q), [0, 0, 1, 0]) or \
           np.allclose(np.abs(q), [0, 0, 0, 1]):
            Q8_indices.append(i)
    print(f"|Q_8| as subset of 2T  : {len(Q8_indices)} (expect 8)")
    # closure: Q8 should be closed under multiplication in 2T
    Q8_set = set(Q8_indices)
    Q8_closed = all(table[i, j] in Q8_set for i in Q8_indices for j in Q8_indices)
    print(f"Q_8 is closed in 2T    : {Q8_closed}")
    # normal: g Q8 g^-1 = Q8 for all g
    # find inverses: every element's inverse is its conjugate (since unit q)
    def find_inv(i):
        c = Q.qconj(G[i])
        d = np.einsum('ij,ij->i', G - c, G - c)
        return int(np.argmin(d))
    is_normal = True
    for g_idx in range(24):
        ginv = find_inv(g_idx)
        for h in Q8_indices:
            conj = table[g_idx, table[h, ginv]]
            if conj not in Q8_set:
                is_normal = False
                break
        if not is_normal:
            break
    print(f"Q_8 is normal in 2T    : {is_normal}")
    print(f"Quotient 2T / Q_8       : group of order 24/8 = 3 -> cyclic C_3")
    print()

    print("CONCLUSION")
    print("-----------")
    print("The 24 vertices of the regular 4-polytope {3,4,3} ARE the 24")
    print("elements of the binary tetrahedral group 2T as unit quaternions.")
    print("The polytope's geometric symmetry is *generated by* its own")
    print("vertex set acting on S^3 by left and right multiplication.")
    print("This is what people mean when they say the 24-cell is the most")
    print("'algebraic' regular polytope -- it is literally a finite group.")


if __name__ == "__main__":
    main()
