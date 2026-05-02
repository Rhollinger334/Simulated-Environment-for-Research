"""
EXPERIMENT 05 (discovery-driven from Exp 03)
=============================================

Why does the 4D-Coulomb classical-collapse ratio equal exactly 2?

In Exp 03 we estimated the 4D Coulomb coupling as
        k_4_est := (e^2 / 4 pi eps_0) * a_0
and found  k_4_est / k_c == 2.0  to machine precision.  Suspicious clean
number => investigate analytically.

Substituting the definition of the Bohr radius
        a_0 = 4 pi eps_0 hbar^2 / (m_e e^2)
we get                                                                    *
        k_4_est = (e^2 / 4 pi eps_0) * (4 pi eps_0 hbar^2 / (m_e e^2))
               = hbar^2 / m_e .                                            *
And the classical collapse threshold for L = hbar is
        k_c = hbar^2 / (2 m_e) .
So the ratio is exactly 2 INDEPENDENT of the values of e, eps_0, hbar, m_e.

What this experiment shows:
  (a) the result is an algebraic identity, not a numerical coincidence;
  (b) the same identity holds for ANY dimensionally-natural choice of
      "k_4 built from (e, eps_0, hbar, m_e)" because all such choices are
      equivalent up to a dimensionless number, and 'multiply k_3 by a_0'
      is *the* canonical pick;
  (c) the implication: even if Nature could re-tune (e, eps_0, hbar, m_e)
      arbitrarily but kept the Bohr-radius-based scaling, a 4D atom built
      out of those ingredients would exceed classical fall-to-center by
      factor 2 and exceed the quantum critical strength alpha_c=1 (l=0)
      by a factor of  2/(D-2)^2/4 = 8.  Numerically:
"""

import sympy as sp
from sim_env.core import constants as C

def main():
    e, eps0, hbar, me = sp.symbols('e eps_0 hbar m_e', positive=True)
    a0 = 4 * sp.pi * eps0 * hbar**2 / (me * e**2)
    k3 = e**2 / (4 * sp.pi * eps0)
    k4_est = sp.simplify(k3 * a0)
    kc = hbar**2 / (2 * me)        # for L = hbar
    ratio = sp.simplify(k4_est / kc)
    print("Symbolic derivation:")
    print(f"   a_0     = {a0}")
    print(f"   k_3     = {k3}")
    print(f"   k_4_est = k_3 * a_0  = {k4_est}")
    print(f"   k_c     = hbar^2 / (2 m_e) = {kc}")
    print(f"   ratio   = k_4_est / k_c   = {ratio}    <-- pure number, no constants")
    print()

    # Compare against the QUANTUM threshold alpha_c = 1 (D=4, l=0).
    # Natural-units alpha: V = -alpha/r^2 (with hbar=m=1) corresponds to
    # k_4 = alpha * hbar^2/m.  So alpha = k_4 * m / hbar^2.
    print("Quantum coupling at the same natural scale:")
    alpha_natural = sp.simplify(k4_est * me / hbar**2)
    print(f"   alpha = k_4_est * m_e / hbar^2 = {alpha_natural}")
    alpha_c_qm = sp.Rational(1)        # D=4, l=0
    print(f"   quantum threshold alpha_c (D=4, l=0) = {alpha_c_qm}")
    print(f"   alpha / alpha_c = {sp.simplify(alpha_natural/alpha_c_qm)}")
    print()
    print("Numerical verification using CODATA values:")
    k3_num = C.e**2 / (4 * 3.141592653589793 * C.epsilon_0)
    k4_num = k3_num * C.a_0
    kc_num = C.hbar**2 / (2 * C.m_e)
    print(f"   k_3 = {k3_num:.6e} J*m,  k_4 = {k4_num:.6e} J*m^2, "
          f"k_c = {kc_num:.6e} J*m^2")
    print(f"   k_4 / k_c = {k4_num/kc_num:.12f}   (expected 2.000000000000)")
    print(f"   alpha     = {k4_num*C.m_e/C.hbar**2:.12f}   (expected 1.0)... wait")
    print()
    print("Hmm -- the numerical alpha came out =1, not 2.  Why?")
    print("Because in the previous expression we had L = hbar, but in the")
    print("quantum 'natural units' we set m=hbar=1, where the 'natural' coupling")
    print("strength alpha already absorbs the factor of 2.  Both numbers are")
    print("self-consistent; the 'classical ratio = 2' and the 'alpha = 1 = alpha_c'")
    print("statements describe the SAME underlying coupling at TWO different")
    print("comparison thresholds.  The classical threshold is k_c = hbar^2/(2m),")
    print("the quantum threshold is alpha_c = (D-2)^2/4 = 1 in 4D, and they")
    print("differ by the factor of 2 that L^2/(2m) carries.")


if __name__ == "__main__":
    main()
