"""
EXPERIMENT 04 -- Time as the 4th Dimension (Minkowski Spacetime)
================================================================

Real, exact special-relativistic computations.  We:
  1) verify the Lorentz boost preserves the Minkowski metric;
  2) compute time dilation at a few real-world velocities (ISS, GPS, LHC);
  3) compute the proper time experienced on a long-distance interstellar
     mission to Proxima Centauri at constant beta;
  4) demonstrate the twin-paradox arithmetic by adding proper times along
     two different worldlines between the same start and end events.
"""

import numpy as np
from sim_env.core import constants as C
from sim_env.physics import minkowski as M


def main():
    print("(1) Boost-preserves-metric check")
    for beta in (0.1, 0.5, 0.9, 0.999999):
        Lam = M.lorentz_boost_x(beta)
        err = np.linalg.norm(Lam.T @ M.ETA @ Lam - M.ETA)
        print(f"    beta = {beta:>10.6f}   gamma = {M.gamma_factor(beta):>14.6f}"
              f"    ||Lambda^T eta Lambda - eta|| = {err:.2e}")
    print()

    print("(2) Time dilation -- real spacecraft / particle accelerators")
    real_velocities = [
        ("ISS orbital speed",      7_660.0,           "m/s"),
        ("GPS satellite",          3_874.0,           "m/s"),
        ("Voyager 1 heliocentric", 17_000.0,          "m/s"),
        ("LHC proton (7 TeV)",     C.c * np.sqrt(1 - (938.272e6/7e12)**2),
                                                       "m/s"),
    ]
    for name, v, unit in real_velocities:
        beta = v / C.c
        gam = M.gamma_factor(beta)
        # seconds gained per year of moving-frame time relative to rest frame
        secs_per_year = 365.25 * 86400
        delta = (gam - 1.0) * secs_per_year
        print(f"    {name:<22}  beta = {beta:.6e}   gamma-1 = "
              f"{gam-1.0:.6e}   (rest gains {delta:+.6e} s / yr)")
    print()

    print("(3) Proper time to Proxima Centauri (4.2465 ly) at constant beta")
    distance_m = 4.2465 * 9.4607304725808e15   # ly -> m (IAU exact)
    for beta in (0.1, 0.5, 0.9, 0.99, 0.999):
        gam = M.gamma_factor(beta)
        t_earth = distance_m / (beta * C.c)            # coordinate time
        t_ship  = t_earth / gam                         # proper time
        print(f"    beta = {beta:<6}  Earth time = "
              f"{t_earth/secs_per_year:>9.4f} yr,  "
              f"ship time = {t_ship/secs_per_year:>9.4f} yr,  "
              f"gamma = {gam:.4f}")
    print()

    print("(4) Twin paradox -- add proper time along two worldlines")
    # Twin A stays at origin from event O=(0,0,0,0) to event Q=(T,0,0,0).
    # Twin B goes out at +beta to (T/2, beta c T/2, 0, 0), turns around,
    # arrives back at Q.
    T = 20.0 * 365.25 * 86400          # 20 years coordinate time
    beta = 0.8
    gam  = M.gamma_factor(beta)

    # Twin A
    O  = (0.0, np.array([0.0, 0.0, 0.0]))
    Q  = (C.c * T, np.array([0.0, 0.0, 0.0]))
    tau_A = M.proper_time(Q[0], Q[1], O[0], O[1])

    # Twin B: outbound segment then inbound segment
    mid_t  = C.c * T / 2.0
    mid_x  = np.array([beta * C.c * (T/2.0), 0.0, 0.0])
    tau_B  = M.proper_time(mid_t, mid_x, O[0], O[1]) + \
             M.proper_time(Q[0],  Q[1],  mid_t, mid_x)

    print(f"    coordinate time T          = {T/secs_per_year:.2f} yr")
    print(f"    twin A (stay-at-home) tau  = {tau_A/secs_per_year:.4f} yr")
    print(f"    twin B (beta=0.8, turn)tau = {tau_B/secs_per_year:.4f} yr")
    print(f"    twin B / twin A            = {tau_B/tau_A:.4f}  "
          f"(predicted 1/gamma = {1.0/gam:.4f})")


if __name__ == "__main__":
    main()
