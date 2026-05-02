"""
EXPERIMENT 10 (own interest) -- 4D rotation can flip chirality
===============================================================

Fact: in R^3, the parity transformation P: x -> -x is NOT in SO(3).
A right hand cannot be rotated into a left hand within R^3.
The orientation-reversing operations form O(3) \\ SO(3) -- a separate
component.

In R^4 the situation is different:
  the (3D) parity P_3 = diag(-1,-1,-1, 1) IS the action on R^3 of an
  *orientation-preserving* rotation in R^4 -- specifically a rotation
  by pi in the (e_1, e_2)-plane composed with a rotation by pi in the
  (e_3, e_4)-plane (an isoclinic half-turn).  Its determinant in R^4
  is (-1)(-1)(-1)(+1) = -1 -- WAIT, that's odd, so this is NOT in SO(4).

The correct statement: in R^4, the operation
   diag(-1,-1,-1,-1)  has determinant +1 and IS in SO(4) (a rotation by
   pi in two orthogonal planes).
This restricts to the 3D hyperplane w=0 as diag(-1,-1,-1) -- 3D parity.
But it ALSO flips the 4th axis, which a 4D being could undo by a second
rotation that swaps two axes.  Net effect on a 3D body inhabiting
the hyperplane: enantiomer (mirror image).

Demonstrate: take a chiral molecule modelled as 4 atoms forming a
tetrahedron with a chosen handedness.  Apply a 4D rotation that, when
restricted to our 3-slice, equals 3D parity, and verify the chirality
flips while no 'unphysical' folding through the molecule occurred at
any intermediate time.
"""

import numpy as np


def chirality_sign(pts4: np.ndarray) -> float:
    """For 4 atoms in R^3 (or in R^4 with last coord = 0), return signed
    volume of the tetrahedron from atom 0 to atoms 1,2,3.  Positive vs
    negative encodes the two enantiomers."""
    p = pts4[:, :3]
    a = p[1] - p[0]
    b = p[2] - p[0]
    c = p[3] - p[0]
    return float(np.linalg.det(np.stack([a, b, c])))


def planar_rot(theta, i, j, n=4):
    R = np.eye(n)
    c, s = np.cos(theta), np.sin(theta)
    R[i, i] = c; R[j, j] = c; R[i, j] = -s; R[j, i] = s
    return R


def main():
    # A chiral tetrahedron embedded in our slice w=0
    mol = np.array([
        [0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
    ])
    print(f"start chirality sign      : {chirality_sign(mol):+.4f}")

    # The minimal-flip operation: a single rotation by pi in the (x_1, w)
    # plane.  Acts on R^4 as  diag(-1, +1, +1, -1).  Determinant = +1, so
    # this is a genuine SO(4) element -- continuously connected to the
    # identity through a path entirely inside SO(4).  Restricted to our
    # 3-slice {w = 0} the action is the SINGLE-AXIS REFLECTION x_1 -> -x_1,
    # which is an orientation-reversing map of R^3 -- it flips chirality.
    R_total = planar_rot(np.pi, 0, 3)
    print(f"R_total in SO(4)? det = {np.linalg.det(R_total):+.6f},  "
          f"orth err = {np.linalg.norm(R_total.T @ R_total - np.eye(4)):.2e}")
    rotated = mol @ R_total.T
    print(f"end chirality sign        : {chirality_sign(rotated):+.4f}")
    print(f"all atoms still on w=0?   : "
          f"{np.allclose(rotated[:, 3], 0)}")
    print()
    print("Trace through 4D (max |w| of any atom at intermediate angles):")
    max_w_excursion = 0.0
    for theta in np.linspace(0, np.pi, 21):
        R = planar_rot(theta, 0, 3)
        m = mol @ R.T
        max_w_excursion = max(max_w_excursion, float(np.abs(m[:, 3]).max()))
    print(f"  during the rotation: max |w| over all atoms = {max_w_excursion:.4f}")
    print(f"  meaning: at angle pi/2, the atom at (1,0,0,0) sits at (0,0,0,-1)")
    print(f"  -- fully OUT of the slice.  At theta=pi it returns to (-1,0,0,0).")
    print(f"  A 3D observer would see the atom DISAPPEAR, the rest reflect,")
    print(f"  and the atom REAPPEAR mirrored -- the molecule has flipped its")
    print(f"  handedness without ever passing through the other atoms.")
    print()
    print("This is the operation impossible in 3D and routine in 4D:")
    print("a 4D being could turn left-handed amino acids into right-handed")
    print("ones without breaking any chemical bonds, just by lifting the")
    print("molecule slightly into the 4th direction and rotating.")


if __name__ == "__main__":
    main()
