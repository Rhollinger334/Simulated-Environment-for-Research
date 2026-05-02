"""
Slicing 4D convex bodies by a 3D hyperplane.

Given a convex 4-polytope as a vertex set V (and its convex hull), and a
hyperplane  H = { x in R^4 : a . x = b },  the cross section H ∩ P is a
convex 3-polytope. Its vertices are precisely the intersections of edges
of P with H (plus any vertices of P lying exactly on H).

We compute these intersections and return the 3D vertex set (in the
hyperplane's local coordinates) plus its 3-volume.
"""

import numpy as np
from scipy.spatial import ConvexHull


def edges_of_convex_polytope(verts: np.ndarray, tol: float = 1e-7) -> list:
    """Return list of (i, j) index pairs of edges of conv(verts). Method:
    take all 1-faces of the convex hull. SciPy's ConvexHull on a 4D point
    cloud returns 3-simplex facets; their edges form a superset of the
    polytope's edges. For convex polytopes whose 1-skeleton equals the
    edge graph of the convex hull, this is exact."""
    hull = ConvexHull(verts)
    edges = set()
    for simplex in hull.simplices:           # each is a 4-tuple in 4D
        m = len(simplex)
        for i in range(m):
            for j in range(i+1, m):
                a, b = sorted((int(simplex[i]), int(simplex[j])))
                edges.add((a, b))
    return sorted(edges)


def slice_polytope(verts: np.ndarray, normal: np.ndarray, offset: float):
    """Intersect conv(verts) with hyperplane { n . x = offset }.
    Returns (cross_section_points_in_R3, volume_3D).
    `normal` need not be unit. Output points lie in R^3 in the 2 onb basis
    of the orthogonal complement of `normal`."""
    n = normal / np.linalg.norm(normal)
    s = verts @ n - offset                    # signed distance per vertex
    pts = []
    # vertices on the plane
    for i, si in enumerate(s):
        if abs(si) < 1e-12:
            pts.append(verts[i])
    # edge intersections
    for i, j in edges_of_convex_polytope(verts):
        if s[i] * s[j] < 0:
            t = s[i] / (s[i] - s[j])
            pts.append(verts[i] + t * (verts[j] - verts[i]))
    if len(pts) < 4:
        return np.zeros((0, 3)), 0.0
    P = np.array(pts)
    # build orthonormal basis of plane (3D subspace)
    # pick any 3 vectors orthogonal to n
    M = np.eye(4) - np.outer(n, n)
    u, sv, vt = np.linalg.svd(M)
    basis = u[:, :3]                          # 4x3 orthonormal basis of plane
    P3 = (P - offset * n) @ basis             # Nx3
    # Compute 3D volume of the cross-section convex hull
    try:
        hull3 = ConvexHull(P3)
        return P3, float(hull3.volume)
    except Exception:
        return P3, 0.0
