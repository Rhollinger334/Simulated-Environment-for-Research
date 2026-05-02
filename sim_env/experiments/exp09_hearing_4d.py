"""
EXPERIMENT 09 -- "Hearing" a 4D entity (Huygens' principle failure)
====================================================================

Mathematical fact (Hadamard, M. Riesz):
   The wave equation u_tt = c^2 nabla^2 u  obeys Huygens' principle
   (sharp wavefront, NO reverberation tail) iff the spatial dimension n
   is ODD and >= 3.  In all EVEN n (and in n=1) there is a "tail":
   the disturbance lingers AFTER the leading wavefront passes.

Implication: if a 4D entity emitted a click in its native 4D space, a
3D microphone embedded in our 3-slice would record:

   (i) silence,
   (ii) a sudden ONSET when the spherical wavefront reaches us at
        t* = sqrt(r_3^2 + w_offset^2) / c,
   (iii) a DECAYING TAIL that NEVER cleanly cuts off
        (envelope ~ (c^2 t^2 - r_4^2)^{-3/2} times c t / (2 pi^2 c)).

No 3D source can produce that tail -- a 3D click has a sharp end.  This
gives an unambiguous acoustic test: if a microphone records a sound
whose envelope decays as the 4D Green's function predicts, the source
was 4-dimensional (or 4D propagation occurred).

We compute the actual recorded waveform for a click from a 4D source
1 metre "above" us, observed at 3D distance 0.5 m.
"""

import numpy as np
from sim_env.physics import wave_nd as W


def main():
    c = 343.0                                  # m/s, speed of sound (real)
    w_off = 1.0                                # source 1 m off our 3-slice
    obs   = np.array([0.5, 0, 0])              # microphone 0.5 m horizontally
    r3    = float(np.linalg.norm(obs))
    r4    = np.sqrt(r3 * r3 + w_off * w_off)
    t_arr = r4 / c
    print(f"Source: 4D point pulse at (0,0,0,{w_off}) m, t=0.")
    print(f"Mic   : 3D point at {obs.tolist()} m on our slice {{w=0}}.")
    print(f"Distance through 4D : r_4 = sqrt({r3}^2 + {w_off}^2) "
          f"= {r4:.6f} m")
    print(f"Onset time          : t*  = r_4 / c = {t_arr*1000:.4f} ms")
    print()

    # Sample the recorded pressure on a fine time grid covering 30 ms
    times = np.linspace(0, 0.030, 6001)        # 200 kHz sample rate
    p4 = W.signal_from_4d_source(obs, w_off, times, c=c)
    # Compare against an idealised 3D click (Gaussian smear of delta)
    sigma_t = 50e-6
    arg = times - r3 / c
    p3 = np.exp(-arg * arg / (2 * sigma_t * sigma_t)) \
         / (sigma_t * np.sqrt(2 * np.pi)) / (4 * np.pi * c * r3)

    print(f"{'t (ms)':>8}  {'p_4D (a.u.)':>14}  {'p_3D Gauss (a.u.)':>20}")
    for ms in (0, 1, 2, 2.9, 2.95, 3.0, 3.05, 3.5, 4, 5, 7, 10, 15, 20, 30):
        i = int(round(ms * 1e-3 * (len(times)-1) / times[-1]))
        i = max(0, min(i, len(times)-1))
        print(f"{times[i]*1000:>8.3f}  {p4[i]:>14.4e}  {p3[i]:>20.4e}")
    print()

    # Quantitative tail behaviour: late-time envelope of 4D signal should
    # decay as 1 / t^2 (since (c^2 t^2 - r_4^2)^{3/2} ~ (c t)^3 and the
    # numerator ~ c t  =>  total ~ 1 / (c^2 t^2)).
    late_mask = times > 0.005           # well past arrival
    t_late = times[late_mask]
    p_late = p4[late_mask]
    # fit log p_late = -k log t + b
    valid = p_late > 0
    log_t = np.log(t_late[valid])
    log_p = np.log(p_late[valid])
    slope, intercept = np.polyfit(log_t, log_p, 1)
    print(f"Late-time fit:  log p_4D(t)  = {slope:.4f} * log t  + const")
    print(f"  predicted slope = -2 (envelope ~ 1/t^2 in the asymptotic regime)")
    print()

    print("Acoustic detection rule for a 4D entity:")
    print("  Record pressure with > ~50 kHz bandwidth.  After every onset,")
    print("  measure the late-time decay slope on a log-log plot.  3D")
    print("  sources have no tail (or a tail set by room reverberation that")
    print("  decays exponentially); a genuine 4D source has a power-law")
    print("  decay of slope ~ -2.  The transition from onset to power-law")
    print("  tail happens within ~2 r_4 / c of the wavefront arrival.")


if __name__ == "__main__":
    main()
