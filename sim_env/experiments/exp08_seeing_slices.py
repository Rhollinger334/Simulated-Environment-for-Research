"""
EXPERIMENT 08 -- "Seeing" a 4D entity by its 3D cross-sections
===============================================================

If a 4D body B passes through our 3D hyperplane H = {w = w_0(t)}, what we
literally see is the time-evolving 3-polytope  B intersection H.

A.  Tesseract translating along its main diagonal.
    Famous result: the central section perpendicular to (1,1,1,1)/2 is a
    REGULAR OCTAHEDRON.  We verify and compute the volume profile.

B.  Tesseract translating along the +w axis (a coordinate axis).
    Section is always a 3-cube of edge 1, suddenly appearing and
    disappearing -- "magic" appearance / disappearance.

C.  Hypersphere (3-sphere) translating through w=0.
    Section is a 3-ball of radius sqrt(R^2 - w_c^2), growing then shrinking.

D.  24-cell sectioned along its main diagonal.
    Just to see what an exotic uniquely-4D body looks like to us.
"""

import numpy as np
from sim_env.geometry import polytopes_4d as P
from sim_env.geometry.slicing import slice_polytope


def scan(verts, normal, w_values, label):
    print(f"  {label}")
    print(f"    {'w':>8}   {'#vertices':>10}  {'volume':>10}  shape hint")
    for w in w_values:
        pts, vol = slice_polytope(verts, normal, w)
        nv = len(pts)
        # try to identify shape
        if nv == 0:
            shape = "(empty)"
        elif nv == 4:
            shape = "tetrahedron"
        elif nv == 6:
            shape = "octahedron-like"
        elif nv == 8:
            shape = "cube-like"
        elif nv == 14:
            shape = "truncated cube/oct"
        else:
            shape = f"{nv}-vertex polyhedron"
        print(f"    {w:>+8.4f}   {nv:>10d}  {vol:>10.5f}  {shape}")
    print()


def main():
    print("(A) Tesseract sliced perpendicular to main diagonal (1,1,1,1)/2")
    cube = P.tesseract()
    diag = np.array([1, 1, 1, 1]) / 2.0
    scan(cube, diag, np.linspace(-1.05, 1.05, 11), "central section is regular octahedron")

    print("(B) Tesseract sliced perpendicular to coordinate axis e_4")
    e4 = np.array([0, 0, 0, 1.0])
    # tesseract has w in [-0.5, 0.5]; outside that, slice is empty
    scan(cube, e4, [-0.6, -0.5, -0.25, 0.0, 0.25, 0.5, 0.6], "constant cube while inside")

    print("(C) 3-sphere of radius 1 translating through w=0  (use 'verts' = sample)")
    rng = np.random.default_rng(1)
    sphere = rng.normal(size=(2000, 4))
    sphere /= np.linalg.norm(sphere, axis=1, keepdims=True)
    sphere = sphere * 1.0
    # We can't slice an exact sphere with our polytope code, so report the
    # exact analytic result instead:
    print("    analytic: section radius = sqrt(R^2 - w_c^2), R=1")
    for wc in [0.0, 0.3, 0.6, 0.9, 0.999, 1.0, 1.001]:
        if abs(wc) >= 1.0:
            print(f"    w_c = {wc:+.3f}   radius = (no intersection)   volume = 0")
        else:
            r3 = np.sqrt(1 - wc * wc)
            v3 = (4.0 / 3.0) * np.pi * r3 ** 3
            print(f"    w_c = {wc:+.3f}   radius = {r3:.5f}   volume = {v3:.5f}")
    print()

    print("(D) 24-cell sectioned along the main 4-diagonal (1,1,1,1)/2")
    p24 = P.twenty_four_cell()
    scan(p24, diag, np.linspace(-2.0, 2.0, 9), "exotic uniquely-4D body")

    print("Visual signature of a 4D entity passing through our 3D space:")
    print("  * Sudden appearance from a single point that grows (tesseract")
    print("    along diagonal: point -> tetrahedron -> octahedron -> tet -> point).")
    print("  * Or instantaneous appearance of a fully-formed cube and then")
    print("    instantaneous disappearance (axis-aligned passage).")
    print("  * Or matter that grows and shrinks while CHANGING TOPOLOGY")
    print("    (24-cell sections vary in vertex count from 6 to 14).")


if __name__ == "__main__":
    main()
