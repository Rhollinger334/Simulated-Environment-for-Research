"""
Quaternion algebra utilities and the binary tetrahedral group 2T.

A quaternion q = w + x*i + y*j + z*k is represented as a 4-vector
(w, x, y, z).  Multiplication is the usual Hamilton product; the
involution is q* = (w, -x, -y, -z); the norm is |q|^2 = w^2+x^2+y^2+z^2.

The "24 unit quaternions" -- equivalently the binary tetrahedral group
2T (also called the Coxeter group <2,3,3>) -- consist of:

    8 quaternions from the (Lipschitz) integer subset:
        +-1, +-i, +-j, +-k                 (the quaternion group Q_8)
   16 "Hurwitz" half-integer quaternions:
        (+-1 +- i +- j +- k) / 2

These 24 quaternions form a multiplicative group of order 24, and -- the
beautiful coincidence -- they are EXACTLY the 24 vertices of the regular
4-polytope {3,4,3}, the 24-cell.

Reference: Conway & Smith, "On Quaternions and Octonions" (2003),
Chapter 3 (the icosian and icosahedral groups), and the standard text
on Coxeter groups.
"""

from itertools import product
import numpy as np


def qmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Hamilton product of two quaternions a, b (each shape (4,))."""
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array([
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw,
    ])


def qconj(q: np.ndarray) -> np.ndarray:
    return np.array([q[0], -q[1], -q[2], -q[3]])


def qnorm2(q: np.ndarray) -> float:
    return float(q @ q)


def binary_tetrahedral_group() -> np.ndarray:
    """Return the 24 unit quaternions forming 2T, as a (24, 4) array.
    This is the vertex set of the 24-cell {3,4,3} (in the standard
    quaternion embedding)."""
    out = []
    # 8 "Lipschitz" units: +-1, +-i, +-j, +-k
    for axis in range(4):
        for sign in (-1, 1):
            v = np.zeros(4)
            v[axis] = sign
            out.append(v)
    # 16 "Hurwitz" half-integer units: (+-1 +- i +- j +- k)/2
    for s in product([-1, 1], repeat=4):
        out.append(np.array(s, dtype=float) / 2.0)
    return np.array(out)


def closure_check(group_elements: np.ndarray, tol: float = 1e-9) -> tuple:
    """Multiply every pair of elements; return whether the products all
    lie back in `group_elements` (up to tol).  Returns (is_closed,
    multiplication_table) where the table is a 24x24 array of indices
    into group_elements."""
    n = len(group_elements)
    G = group_elements
    table = np.full((n, n), -1, dtype=int)
    for i in range(n):
        for j in range(n):
            p = qmul(G[i], G[j])
            # find p in G
            diffs = G - p
            d = np.einsum('ij,ij->i', diffs, diffs)
            best = int(np.argmin(d))
            if d[best] < tol:
                table[i, j] = best
    return (table >= 0).all(), table


def element_orders(group_elements: np.ndarray, table: np.ndarray) -> np.ndarray:
    """Order of each element in the group: smallest k > 0 with g^k = e.
    Identity is assumed to be the unique element with [1,0,0,0]."""
    n = len(group_elements)
    e_idx = int(np.argmax(np.all(np.isclose(group_elements,
                                            np.array([1, 0, 0, 0])), axis=1)))
    orders = np.zeros(n, dtype=int)
    for i in range(n):
        cur = e_idx                       # start at identity
        for k in range(1, n + 1):
            cur = table[cur, i]           # cur now represents g^k
            if cur == e_idx:
                orders[i] = k
                break
    return orders
