"""
Fundamental physical constants.

All values from CODATA 2018 recommended values and the SI redefinition
(2019). Constants marked EXACT have defined values in the post-2019 SI.
No approximations, no mock data.

Reference: P.J. Mohr, D.B. Newell, B.N. Taylor, Rev. Mod. Phys. 88, 035009 (2016)
           and the 2019 SI redefinition.
"""

from math import pi

# --- Exact (defined) SI constants (post 2019 redefinition) ---
c = 299_792_458.0                    # speed of light in vacuum, m/s  (EXACT)
h = 6.626_070_15e-34                 # Planck constant, J*s            (EXACT)
hbar = h / (2.0 * pi)                # reduced Planck, J*s
e = 1.602_176_634e-19                # elementary charge, C            (EXACT)
k_B = 1.380_649e-23                  # Boltzmann, J/K                  (EXACT)
N_A = 6.022_140_76e23                # Avogadro, /mol                  (EXACT)

# --- CODATA 2018 measured constants ---
G = 6.674_30e-11                     # Newtonian gravitation, m^3/(kg*s^2)
m_e = 9.109_383_7015e-31             # electron rest mass, kg
m_p = 1.672_621_923_69e-27           # proton rest mass, kg
m_n = 1.674_927_498_04e-27           # neutron rest mass, kg
alpha = 7.297_352_5693e-3            # fine-structure constant (dimensionless)
R_inf = 1.097_373_156_8160e7         # Rydberg constant, /m

# Vacuum electric permittivity (CODATA 2018, no longer exact post 2019)
epsilon_0 = 8.854_187_8128e-12       # F/m
mu_0 = 1.256_637_062_12e-6           # N/A^2

# Derived atomic units (CODATA 2018)
a_0 = 5.291_772_109_03e-11           # Bohr radius, m
E_h = 4.359_744_722_2071e-18         # Hartree energy, J
Ry = E_h / 2.0                       # Rydberg energy, J  (= 13.605693122994 eV)

# Conversions
eV = e                               # 1 eV in joules
J_to_eV = 1.0 / e

# Mathematical constants
PHI = (1.0 + 5.0**0.5) / 2.0         # golden ratio
TAU = 2.0 * pi
