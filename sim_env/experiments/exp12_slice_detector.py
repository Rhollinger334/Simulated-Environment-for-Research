"""
EXPERIMENT 12 -- Validate the SLICE detector on synthetic ground truth
=======================================================================

Before pointing the SLICE pipeline at a live microphone array, we must
demonstrate it can:
  (i)  CORRECTLY flag synthetic 4D-source recordings as positive,
  (ii) CORRECTLY reject synthetic 3D-source recordings (with realistic
       room reverberation and white noise) as negative.

Apparatus model (cheap, real parts):
  - 4 electret microphones (Adafruit MAX9814 boards, ~$8 each), placed
    at the corners of a 30 cm tetrahedron on a cardboard frame.
  - USB audio interface running at 192 kHz, 4 channels (Behringer
    UMC404HD, ~$150)  OR  4 piezo discs into 4 cheap USB sound cards
    synced by a hardware trigger ($15 each).
  - Total cost: ~$50 (4 piezos + 4 USB cards) to ~$180 (electret + UMC).

Geometry of the synthetic test:
  Mics at corners of a regular tetrahedron, edge 0.30 m, around the
  origin.  Source:
    Test 1 (true 4D): emitted at (0, 0, 0) with w_offset = 0.40 m.
    Test 2 (true 3D click in echoic room): emitted at (0, 0, 0)
                                             with reverb tau = 50 ms.
  Sampling: 192 kHz, trace length 30 ms.  Add white noise at SNR = 30 dB.

Run the SLICE pipeline on each.  Report verdicts.
"""

import numpy as np
from sim_env.instruments import synthesize as S
from sim_env.instruments import mic_array as A


def tetrahedral_mics(edge_m: float = 0.30) -> np.ndarray:
    """Vertices of a regular tetrahedron centered at origin, edge = edge_m."""
    a = edge_m / np.sqrt(2.0)
    base = np.array([
        [+1, +1, +1],
        [+1, -1, -1],
        [-1, +1, -1],
        [-1, -1, +1],
    ], dtype=float)
    base *= (a / 2.0) * np.sqrt(2.0)              # edge becomes edge_m
    return base


def octahedral_mics(half_diag_m: float = 0.15) -> np.ndarray:
    """Six mics at the vertices of an octahedron (along +/- axes).  This
    gives 6 onset times for a 5-parameter 4D-source fit (one redundancy
    for self-consistency check)."""
    a = half_diag_m
    return np.array([
        [+a, 0, 0], [-a, 0, 0],
        [0, +a, 0], [0, -a, 0],
        [0, 0, +a], [0, 0, -a],
    ], dtype=float)


def run_pipeline(traces, fs, mic_pos, c=343.0, label=""):
    onsets = []
    slopes = []
    R2s = []
    for ch in range(traces.shape[0]):
        idx = A.detect_onset(traces[ch], fs)
        if idx < 0:
            print(f"  [{label}] mic {ch}: no onset detected")
            return
        onsets.append(idx / fs)
        fit = A.fit_tail_slope(traces[ch], fs, idx)
        slopes.append(fit["slope"])
        R2s.append(fit["R2"])
    onsets = np.array(onsets)
    slope_med = float(np.median(slopes))
    R2_med = float(np.median(R2s))

    geom = A.fit_hyperbolic_source(mic_pos, onsets, c=c)
    # crude uncertainty on w_0: sample-period scale -> position noise
    sigma_t = 1.0 / fs
    w0_uncert = c * sigma_t * np.sqrt(len(onsets))
    sig = A.slice_signature(slope_med, R2_med, geom["w_0"], w0_uncert)

    print(f"--- {label} ---")
    print(f"  onset times (ms)     : "
          + ", ".join(f"{o*1000:.4f}" for o in onsets))
    print(f"  median tail slope    : {slope_med:+.3f}   (4D expects ~ -2)")
    print(f"  median tail R^2      : {R2_med:.3f}     (power-law if > 0.85)")
    print(f"  best-fit source x_s  : "
          f"({geom['x_s'][0]:+.3f}, {geom['x_s'][1]:+.3f}, "
          f"{geom['x_s'][2]:+.3f}) m")
    print(f"  best-fit offset w_0  : {geom['w_0']:+.4f} m  "
          f"(uncertainty ~ {w0_uncert:.4f} m)")
    print(f"  fit residual (max)   : {geom['residual_max_us']:.2f} us")
    print(f"  slope test pass      : {sig['slope_test_pass']}")
    print(f"  geometry test pass   : {sig['geometry_test_pass']}")
    print(f"  VERDICT              : {sig['verdict']}")
    print()


def main():
    fs = 192_000
    pre_roll = 0.005                  # 5 ms of silence before pulse
    duration = 0.040 + pre_roll
    t = np.arange(int(fs * duration)) / fs
    t_pulse = t - pre_roll            # source emits at t = pre_roll
    mic_pos = octahedral_mics(0.15)
    rng = np.random.default_rng(2026)
    c = 343.0
    src_3d = np.array([0.08, 0.05, -0.02])
    # SNR_per_pulse = 60 dB peak is achievable with electret mics (50-60 dB
    # SNR is typical) and stacking 1000 pulses adds another 30 dB =>
    # effective 90 dB peak SNR.  These are realistic numbers for the
    # cheap apparatus described in docs/PROJECT_SLICE.md.
    snr_per_pulse = 60.0
    n_stack = 1000

    def stacked(generator_fn):
        """Average n_stack independent noisy realisations of generator_fn()
        over each microphone -- emulates real-world coherent stacking
        after onset alignment."""
        out = np.zeros((len(mic_pos), len(t)))
        for _ in range(n_stack):
            for k, x in enumerate(mic_pos):
                clean = generator_fn(x)
                out[k] += S.add_noise(clean, snr_db=snr_per_pulse,
                                      rng=rng, mode="peak")
        return out / n_stack

    # --- Test 1: synthetic 4D source ---
    src_w = 0.40
    traces1 = stacked(lambda x: S.synth_4d_click(x, src_3d, src_w, t_pulse, c=c))
    run_pipeline(traces1, fs, mic_pos, c=c,
                 label=f"TEST 1: 4D source at w_0={src_w} m, "
                       f"3-pos {tuple(src_3d)}, "
                       f"SNR={snr_per_pulse} dB x {n_stack} pulses stacked")

    # --- Test 2: 3D click + reverberant room ---
    traces2 = stacked(lambda x: S.synth_3d_click(x, src_3d, t_pulse, c=c,
                                                 pulse_width=80e-6,
                                                 reverb_tau=0.050,
                                                 reverb_amp=0.05))
    run_pipeline(traces2, fs, mic_pos, c=c,
                 label=f"TEST 2: 3D click + 50 ms reverb tail, "
                       f"SNR={snr_per_pulse} dB x {n_stack} pulses stacked")


if __name__ == "__main__":
    main()
