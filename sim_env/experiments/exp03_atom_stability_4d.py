"""
EXPERIMENT 03 -- Why Atoms (and Solar Systems) Cannot Exist in 4D
==================================================================

Two complementary derivations:

(A)  CLASSICAL  (Ehrenfest 1917).
     Gauss's law in n spatial dimensions forces the inverse-power
     gravitational/Coulomb force to be  F ~ 1/r^{n-1}, hence
     V(r) ~ -k/r^{n-2}.  In 4D this is V = -k/r^2.  The effective radial
     potential including the centrifugal barrier is
            V_eff(r) = -k/r^2 + L^2/(2 m r^2).
     Both terms scale identically.  Therefore:
        * if k <  L^2/(2m): V_eff is purely repulsive -- particle escapes.
        * if k >  L^2/(2m): V_eff is purely attractive -- particle spirals
                            inward to the origin (no minimum, no orbit).
        * if k == L^2/(2m): marginal case, no stable circular orbit.
     Hence no bound, stable, finite-radius orbits exist in 4D.

(B)  QUANTUM   (the "fall to the center"; Landau & Lifshitz Vol. 3, Sec.35).
     For V = -alpha / r^2 the Schrodinger equation has bound states only as
     a continuum reaching down to E = -infty when alpha exceeds a critical
     value -- no ground state.  Concretely, for spatial dimension D and
     attractive 1/r^2 with strength alpha (in units hbar=m=1), the radial
     equation has the centrifugal term
            l(l+D-2)/r^2 - alpha/r^2 = (l(l+D-2) - alpha)/r^2.
     Bound spectrum collapses (no normalizable ground state) when
            alpha > (D-2)^2 / 4 - l(l+D-2)            -- Landau-Lifshitz
     so even at l = 0, D = 4 it suffices that alpha > 1.  For an electron
     bound by the genuine 4D Coulomb law, alpha is determined by physical
     constants and easily exceeds this threshold => no stable atom.

We compute the numbers explicitly using CODATA values.
"""

import numpy as np
from sim_env.core import constants as C
from sim_env.physics import nd_physics as ND


def main():
    print("(A) CLASSICAL: critical coupling k_c for fall-to-center in 4D")
    print("    V_eff = (-k + L^2/(2m)) / r^2 ; collapse if k > L^2/(2m)")
    # Use a hydrogen-scale electron with L = hbar (l=1)
    L = C.hbar
    m = C.m_e
    kc = ND.fall_to_center_threshold(m, L)
    # The 4D Coulomb constant k_4 has units of energy * length^2.
    # In 3D the Coulomb constant is k_3 = e^2 / (4 pi eps_0)  [J*m].
    # In 4D Gauss's law gives V = -Q^2 / (4 pi^2 eps_0_4d r^2).
    # Lacking an experimentally measured 4D vacuum permittivity (it has
    # different SI units in 4D and no measurement exists), we ESTIMATE the
    # natural strength by analytic continuation: k_4 ~ k_3 * a_0,
    # which has the right units (J*m^2) and the right scale.
    k3 = C.e * C.e / (4 * np.pi * C.epsilon_0)
    k4_est = k3 * C.a_0
    print(f"    L  = hbar         = {L:.4e} J*s")
    print(f"    m  = m_e          = {m:.4e} kg")
    print(f"    k_c = L^2/(2m)    = {kc:.4e} J*m^2")
    print(f"    k_4 (est. e^2 a_0 / 4 pi eps_0) = {k4_est:.4e} J*m^2")
    print(f"    ratio k_4/k_c     = {k4_est/kc:.3f}")
    if k4_est > kc:
        print("    --> k_4 > k_c: classical trajectories COLLAPSE to r=0.")
    else:
        print("    --> k_4 < k_c: classical electron escapes; no bound orbits.")
    print()

    print("(B) QUANTUM: Landau-Lifshitz fall-to-center criterion")
    print("    For V = -alpha/r^2 in D spatial dim with l=0:")
    print("    bound spectrum collapses (no ground state) iff alpha > (D-2)^2/4.")
    for D in (3, 4, 5):
        thresh = (D - 2) ** 2 / 4.0
        print(f"      D = {D}:  threshold alpha_c = {thresh:.4f}")
    print()
    print("    In 4D, alpha_c = 1.  Any nonzero attractive 1/r^2 of strength")
    print("    alpha > 1 (in natural units hbar = m = 1) destroys the ground")
    print("    state.  Coulomb-strength binding satisfies this trivially.")
    print()

    print("(C) For comparison: hydrogenic energies if we KEEP 1/r operator")
    print("    in D dimensions (Nieto 1979).  Note: this is NOT the physical")
    print("    4D atom -- in true 4D the electrostatic potential is 1/r^2,")
    print("    not 1/r -- but it shows the dimensional dependence.")
    print(f"    {'D':>3}  {'E_1 (eV)':>14}  {'<r>_1 (a_0)':>14}")
    for D in (2, 3, 4, 5, 6):
        try:
            E1 = ND.hydrogenic_energy(1, D=D)
            n_eff = 1 + (D - 3) / 2.0
            r1 = n_eff * n_eff       # in units of a_0 for hydrogen
            print(f"    {D:>3}  {E1*C.J_to_eV:>14.6f}  {r1:>14.4f}")
        except Exception as ex:
            print(f"    {D:>3}  ERROR {ex}")
    print()
    print("CONCLUSION: in 4 spatial dimensions, neither classical Kepler")
    print("orbits nor quantum-mechanical bound states of the natural Gauss-")
    print("law potential are stable.  Atoms, planets, stars cannot persist.")
    print("(Tegmark 1997 cites this as an anthropic argument for D = 3.)")


if __name__ == "__main__":
    main()
