"""
The six convex regular 4-polytopes (the 4D analogs of the Platonic solids).

Schlafli enumeration -- Schlafli (1852), proven complete:
  5-cell    {3,3,3}     5-simplex / pentachoron
  8-cell    {4,3,3}     tesseract / hypercube
  16-cell   {3,3,4}     hyperoctahedron / orthoplex
  24-cell   {3,4,3}     -- no 3D analog --
  120-cell  {5,3,3}
  600-cell  {3,3,5}

Vertex coordinates are exact algebraic numbers, written here as the
numerical values they evaluate to. Sources: Coxeter, "Regular Polytopes"
(3rd ed., 1973) Tables I-V.
"""

import numpy as np
from itertools import permutations, product
from math import sqrt

PHI = (1.0 + sqrt(5.0)) / 2.0   # golden ratio


def _all_sign_perms(coords):
    """Return all coordinate vectors obtained from `coords` by independent
    sign flips of the nonzero entries followed by all coordinate
    permutations."""
    seen = set()
    out = []
    n = len(coords)
    nonzero_positions = [i for i, c in enumerate(coords) if c != 0]
    for perm in permutations(range(n)):
        for signs in product([1, -1], repeat=len(nonzero_positions)):
            v = [0.0] * n
            for src, dst in enumerate(perm):
                v[dst] = coords[src]
            for k, pos in enumerate(nonzero_positions):
                # apply sign to whichever permuted index now holds it
                v[perm[pos]] *= signs[k]
            t = tuple(round(x, 12) for x in v)
            if t not in seen:
                seen.add(t)
                out.append(np.array(v))
    return np.array(out)


# ---------- 5-cell {3,3,3} ----------
def five_cell():
    """5 vertices of a regular 4-simplex centered at origin, edge length sqrt(2)."""
    # Standard construction: 5 vertices in R^5 lying on the hyperplane sum=1,
    # then project. Equivalently use these explicit coordinates (Coxeter):
    s = 1.0 / sqrt(10.0)
    verts = np.array([
        [ 1,  1,  1, -s*0],   # placeholder
    ])
    # Cleaner: use the standard centered 4-simplex
    e = np.eye(5)
    centroid = np.full(5, 1.0/5.0)
    pts5 = e - centroid                         # 5 points in 4D affine subspace
    # Orthonormal basis of the hyperplane sum(x)=0 in R^5
    Q, _ = np.linalg.qr(np.random.RandomState(0).randn(5, 4))
    # Project pts5 onto the sum=0 hyperplane via known basis
    # Use Gram-Schmidt on differences of e_i
    basis = []
    for i in range(1, 5):
        v = e[i] - e[0]
        for b in basis:
            v = v - np.dot(v, b) * b
        v = v / np.linalg.norm(v)
        basis.append(v)
    B = np.stack(basis, axis=1)      # 5x4
    verts = pts5 @ B                 # 5x4
    # rescale to unit edge length
    edge = np.linalg.norm(verts[1] - verts[0])
    return verts / edge


# ---------- 8-cell (tesseract) {4,3,3} ----------
def tesseract():
    """16 vertices: (+/-1, +/-1, +/-1, +/-1)/2 (edge length 1)."""
    return np.array([list(s) for s in product([-0.5, 0.5], repeat=4)])


# ---------- 16-cell {3,3,4} ----------
def sixteen_cell():
    """8 vertices: all (+/-1, 0, 0, 0) permutations (edge length sqrt(2))."""
    verts = []
    for i in range(4):
        for s in (-1, 1):
            v = [0.0]*4
            v[i] = s
            verts.append(v)
    return np.array(verts)


# ---------- 24-cell {3,4,3} ----------
def twenty_four_cell():
    """24 vertices: all permutations of (+/-1, +/-1, 0, 0). Edge length sqrt(2).
    THIS POLYTOPE HAS NO 3D ANALOG -- it is genuinely unique to 4D."""
    verts = set()
    for i, j in permutations(range(4), 2):
        if i >= j:
            continue
        for si, sj in product([-1, 1], repeat=2):
            v = [0.0]*4
            v[i] = si
            v[j] = sj
            verts.add(tuple(v))
    return np.array(sorted(verts))


# ---------- 600-cell {3,3,5} ----------
def six_hundred_cell():
    """120 vertices. Construction (Coxeter):
        - 8 vertices of 16-cell:  (+/-1, 0, 0, 0) and permutations
        - 16 vertices of tesseract: (+/-1, +/-1, +/-1, +/-1)/2
        - 96 even permutations of (+/-phi, +/-1, +/-1/phi, 0)/2
    Total 120. Edge length = 1/phi.
    """
    verts = []
    # 8 from 16-cell scaled to lie on unit sphere
    for i in range(4):
        for s in (-1, 1):
            v = [0.0]*4
            v[i] = s
            verts.append(v)
    # 16 from tesseract
    for s in product([-0.5, 0.5], repeat=4):
        verts.append(list(s))
    # 96 even permutations of (+/-phi, +/-1, +/-1/phi, 0)/2
    base = [PHI/2, 0.5, 1/(2*PHI), 0.0]
    sign_targets = [0, 1, 2]  # nonzero indices when the 0 is in last slot
    # generate all permutations, keep even ones
    from itertools import permutations as perms
    for perm in perms(range(4)):
        # parity of permutation
        p = list(perm)
        inv = sum(1 for i in range(4) for j in range(i+1, 4) if p[i] > p[j])
        if inv % 2 != 0:
            continue
        permuted = [base[p.index(k)] for k in range(4)]
        # Actually: apply perm to base
        permuted = [base[perm[k]] for k in range(4)]
        nonzero_idx = [k for k in range(4) if permuted[k] != 0]
        for signs in product([-1, 1], repeat=len(nonzero_idx)):
            v = list(permuted)
            for k, idx in enumerate(nonzero_idx):
                v[idx] *= signs[k]
            verts.append(v)
    arr = np.array(verts)
    # Deduplicate
    rounded = np.round(arr, 10)
    _, uniq_idx = np.unique(rounded, axis=0, return_index=True)
    return arr[np.sort(uniq_idx)]


# ---------- 120-cell {5,3,3} ----------
def one_hundred_twenty_cell():
    """600 vertices. Construction by Coxeter; this is one of the most complex
    regular polytopes. Vertex set is the union of orbits of:
        (0, 0, +/-2, +/-2)             [24]
        (+/-1, +/-1, +/-1, +/-sqrt(5)) [64]
        (+/-phi^-2, +/-phi, +/-phi, +/-phi)  [64]
        (+/-phi^-1, +/-phi^-1, +/-phi^-1, +/-phi^2) [64]
        (0, +/-phi^-2, +/-1, +/-phi^2) [96]   (even perms)
        (0, +/-phi^-1, +/-phi, +/-sqrt(5)) [96]  (even perms)
        (+/-phi^-1, +/-1, +/-phi, +/-2)  [192]  (even perms)
    All under all sign changes; the perm-restricted ones only under even perms.
    Total: 24+64+64+64+96+96+192 = 600. (Coxeter, Reg. Polytopes Table V.)
    """
    from itertools import permutations as perms
    pm1 = PHI**-1
    pm2 = PHI**-2
    p1 = PHI
    p2 = PHI**2
    s5 = sqrt(5.0)
    verts = []

    def add_all_perms_all_signs(base):
        nonzero = [i for i, v in enumerate(base) if v != 0]
        for perm in perms(range(4)):
            permuted = [base[perm[k]] for k in range(4)]
            nz = [k for k in range(4) if permuted[k] != 0]
            for signs in product([-1, 1], repeat=len(nz)):
                v = list(permuted)
                for k, idx in enumerate(nz):
                    v[idx] *= signs[k]
                verts.append(v)

    def add_even_perms_all_signs(base):
        for perm in perms(range(4)):
            inv = sum(1 for i in range(4) for j in range(i+1, 4) if perm[i] > perm[j])
            if inv % 2 != 0:
                continue
            permuted = [base[perm[k]] for k in range(4)]
            nz = [k for k in range(4) if permuted[k] != 0]
            for signs in product([-1, 1], repeat=len(nz)):
                v = list(permuted)
                for k, idx in enumerate(nz):
                    v[idx] *= signs[k]
                verts.append(v)

    add_all_perms_all_signs([0, 0, 2, 2])
    add_all_perms_all_signs([1, 1, 1, s5])
    add_all_perms_all_signs([pm2, p1, p1, p1])
    add_all_perms_all_signs([pm1, pm1, pm1, p2])
    add_even_perms_all_signs([0, pm2, 1, p2])
    add_even_perms_all_signs([0, pm1, p1, s5])
    add_even_perms_all_signs([pm1, 1, p1, 2])

    arr = np.array(verts)
    rounded = np.round(arr, 9)
    _, uniq_idx = np.unique(rounded, axis=0, return_index=True)
    return arr[np.sort(uniq_idx)]


REGULAR_4_POLYTOPES = {
    "5-cell  {3,3,3}":   five_cell,
    "8-cell  {4,3,3}":   tesseract,
    "16-cell {3,3,4}":   sixteen_cell,
    "24-cell {3,4,3}":   twenty_four_cell,
    "600-cell {3,3,5}":  six_hundred_cell,
    "120-cell {5,3,3}":  one_hundred_twenty_cell,
}
