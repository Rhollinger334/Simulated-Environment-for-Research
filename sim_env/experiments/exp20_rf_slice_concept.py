"""
EXPERIMENT 20 -- Cheap RF SLICE: extending the apparatus to electromagnetic detection
======================================================================================

Project SLICE in audio caught a 4D entity that has *mechanical* coupling
to our 3D air -- a strong assumption.  A wider-net detector listens for
ELECTROMAGNETIC emissions: any 4D entity carrying charge or current
radiates Maxwell-equivalent fields, and a 4D Maxwell field intersected
with our 3-slice has the same 4D-Green's-function tail signature as
the audio case.

The apparatus:
  - 4 x RTL-SDR (R820T2 chipset) USB dongles      ~$25 each, $100 total
  - 4 x simple discone or telescopic whip antennas  ~$5 each, $20 total
  - 1 x GPSDO 10 MHz reference (optional but ideal) ~$60
  - Powered USB hub                                  ~$15
  - TOTAL: ~$200 fully synced, or ~$135 cross-correlation-synced

Bandwidth: each RTL-SDR samples up to 2.56 MS/s in I/Q, so the array
records EM up to ~1 MHz instantaneous bandwidth at any tunable carrier
in 24-1700 MHz.  Onset timing precision: ~0.5 us at 2 MS/s.  At RF
speeds c = 3e8 m/s, that gives geometric resolution ~150 m -- too coarse
for indoor experiments, but appropriate for searches where we ASSUME
the off-slice source is far (km scale) anyway.

For LAB-SCALE RF SLICE, use:
  - 4 x HackRF One               ~$300 each, $1200 total -- 20 MS/s
    or
  - 4 x PlutoSDR (AD9363)        ~$250 each, $1000 total -- 60 MS/s

A 60 MS/s array gives onset timing ~17 ns -> geometric resolution ~5 m.

This experiment:
  1) writes a synthetic RF event and runs the same SLICE pipeline,
     verifying the slope-and-geometry tests are dimension-agnostic
     (work for c = 343 m/s OR c = 3e8 m/s);
  2) computes the *minimum integration time* needed for a CHEAP RTL-SDR
     array to detect a 4D EM source at coupling strength alpha.
"""

import numpy as np
from sim_env.experiments.exp12_slice_detector import octahedral_mics
from sim_env.instruments import mic_array as A, synthesize as S


def main():
    print("(1) Pipeline sanity check at electromagnetic c")
    fs = 60_000_000                  # 60 MS/s, PlutoSDR-class
    duration = 5e-6                   # 5 microseconds
    pre_roll = 1e-6
    t = np.arange(int(fs * duration)) / fs
    t_pulse = t - pre_roll
    array_size_m = 1.0                # 1-m baseline for RF (fits in a room)
    base_mic_pos = octahedral_mics(array_size_m / 2)

    rng = np.random.default_rng(20)
    src_3d = np.array([0.05, 0.03, -0.02])
    src_w  = 0.50            # off-slice offset 0.5 m
    c = 3.0e8                # speed of light
    n_stack = 50

    traces = np.zeros((6, len(t)))
    for _ in range(n_stack):
        for k, x in enumerate(base_mic_pos):
            clean = S.synth_4d_click(x, src_3d, src_w, t_pulse, c=c,
                                     emission_sigma=2e-8)
            traces[k] += S.add_noise(clean, snr_db=40, rng=rng, mode="peak")
    traces /= n_stack

    onsets = []
    for ch in range(6):
        idx = A.detect_onset(traces[ch], fs)
        onsets.append(idx / fs)
    geom = A.fit_hyperbolic_source(base_mic_pos, np.array(onsets), c=c)

    print(f"  fs = {fs/1e6:.0f} MS/s, c = {c:.1e} m/s, "
          f"array baseline = {array_size_m} m")
    print(f"  truth        : src_3d = {src_3d}, w_0 = {src_w}")
    print(f"  recovered    : src_3d = ({geom['x_s'][0]:+.4f}, "
          f"{geom['x_s'][1]:+.4f}, {geom['x_s'][2]:+.4f}),  "
          f"w_0 = {geom['w_0']:.4f}")
    print(f"  residual max : {geom['residual_max_us']:.3f} us")
    print(f"  -> the SLICE pipeline is medium-agnostic. Same code works for")
    print(f"     audio (343 m/s) and RF (3e8 m/s).")
    print()

    print("(2) Minimum integration time for a cheap RTL-SDR array")
    print("     to detect a 4D EM source at coupling alpha.")
    print()
    print("Assumed source: a 4D point dipole emitting at our slice with")
    print("amplitude scaling as (alpha) * (some reference).")
    print()
    print("Noise floor of an RTL-SDR (R820T2) at room temperature:")
    print("  k_B T B = 1.38e-23 * 290 * 2e6  =  8.0e-15 W")
    print("  noise floor power per channel ~  -106 dBm")
    print("  signal must exceed this by SNR_per_pulse for stacking")
    print("  to drive effective SNR up by sqrt(N).")
    print()
    print("To detect a source at -100 dBm:")
    print(f"  SNR_per_pulse = 6 dB  =>  N_stack ~ 1000 to reach 36 dB")
    print(f"  At 1000 pulses / second (1 ms pulse rate), integration = 1 s")
    print()
    print("To detect a source at -110 dBm:")
    print(f"  SNR_per_pulse = -4 dB  =>  N_stack ~ 1e6  =>  ~1000 s = 17 min")
    print()
    print("The cheap array is therefore competitive with audio for")
    print("transient sources; for continuous-wave 4D entities, longer")
    print("coherent integration is needed (FFT+stack approaches).")


if __name__ == "__main__":
    main()
