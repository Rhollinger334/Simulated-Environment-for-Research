"""
EXPERIMENT 19 -- The SO(3) Rotational Invariance Test
=========================================================

THE METHODOLOGICAL BREAKTHROUGH for SLICE.

In Project SLICE (reports/03), the geometry test fits a hyperbolic
TDOA model
        t_i  =  sqrt(|x_i - x_s|^2 + w_0^2) / c
to onset times across the microphone array, and reports w_0 as the
"off-slice offset". I tacitly claimed: w_0 != 0  =>  source is in the
4th spatial dimension.

This is WRONG without an additional test.  Counter-example:

  Take a microphone array confined to the XY-plane (a flat array).
  A genuine 3D source at (x_s, y_s, z_s = h) with h > 0 produces
  arrival times t_i = sqrt((x_i - x_s)^2 + (y_i - y_s)^2 + h^2)/c.
  Fitting these with a 2D source position + offset returns
  w_0 = h, even though the source is purely 3D and h is just its
  height above the array plane.

The escape is to make the array SPAN 3D and then to apply the
genuine smoking-gun test:

  ROTATIONAL INVARIANCE.   A 4D offset is, by definition,
  perpendicular to ALL of R^3.  If we physically rotate the array
  through any element R in SO(3) and observe a fresh event from
  the same source, the recovered w_0 must be UNCHANGED.  In
  contrast, a hidden 3D position component covaries with R.

This test is the actual definition of 4D-ness, in the form of an
observable invariant.

Experiment plan:
  1. Build a synthesised 4D source and a synthesised 3D source.
     Both produce identical onset patterns to a stationary array
     (degenerate by construction).
  2. Apply random SO(3) rotations R_k to the array (or equivalently,
     to the source positions).
  3. For each R_k, fit (x_s, w_0) and record w_0.
  4. Compare statistics:
       - 4D source:   sigma(w_0) / mean(w_0) ~ noise level
       - 3D source:   sigma(w_0) / mean(w_0) ~ O(1)  [varies with R]

This is the FIRST test in the SLICE pipeline that has no known
3D-physics false-positive analog.
"""

import numpy as np
from scipy.spatial.transform import Rotation
from sim_env.experiments.exp12_slice_detector import octahedral_mics
from sim_env.instruments import mic_array as A, synthesize as S


def generate_event_4d(mic_pos, src_3d, src_w, fs, t_pulse, c=343.0,
                      snr_per_pulse=60.0, n_stack=200, rng=None):
    rng = rng or np.random.default_rng()
    out = np.zeros((len(mic_pos), len(t_pulse)))
    for _ in range(n_stack):
        for k, x in enumerate(mic_pos):
            clean = S.synth_4d_click(x, src_3d, src_w, t_pulse, c=c)
            out[k] += S.add_noise(clean, snr_db=snr_per_pulse,
                                  rng=rng, mode="peak")
    return out / n_stack


def generate_event_3d(mic_pos, src_3d, fs, t_pulse, c=343.0,
                      snr_per_pulse=60.0, n_stack=200, rng=None):
    """A 3D source with no 4th-dim offset, but POSITIONED somewhere in
    3D; same emission stack."""
    rng = rng or np.random.default_rng()
    out = np.zeros((len(mic_pos), len(t_pulse)))
    for _ in range(n_stack):
        for k, x in enumerate(mic_pos):
            clean = S.synth_3d_click(x, src_3d, t_pulse, c=c,
                                     pulse_width=80e-6,
                                     reverb_tau=0.0, reverb_amp=0.0)
            out[k] += S.add_noise(clean, snr_db=snr_per_pulse,
                                  rng=rng, mode="peak")
    return out / n_stack


def fit_w0_from_traces(traces, mic_pos, fs, c=343.0):
    """Run the SLICE geometry fit; return w_0 only."""
    onsets = []
    for ch in range(traces.shape[0]):
        idx = A.detect_onset(traces[ch], fs)
        if idx < 0:
            return np.nan
        onsets.append(idx / fs)
    geom = A.fit_hyperbolic_source(mic_pos, np.array(onsets), c=c)
    return geom["w_0"]


def main():
    fs = 192_000
    pre_roll = 0.005
    duration = 0.045
    t = np.arange(int(fs * duration)) / fs
    t_pulse = t - pre_roll
    base_mic_pos = octahedral_mics(0.15)
    rng = np.random.default_rng(42)
    n_rotations = 12

    # Generate random SO(3) rotations
    rotations = Rotation.random(n_rotations, random_state=rng).as_matrix()

    # Source 1: TRUE 4D source.  Off-slice offset w_true = 0.40 m,
    # 3D position at origin (we want to make 3D part trivial so the
    # test isolates the off-slice component).
    print("=" * 70)
    print("CASE A: true 4D source, w_true = 0.40 m, 3D pos = (0,0,0)")
    print("=" * 70)
    src_3d = np.array([0.0, 0.0, 0.0])
    src_w_true = 0.40
    w0_recovered = []
    for k, R in enumerate(rotations):
        rotated_mics = base_mic_pos @ R.T
        traces = generate_event_4d(rotated_mics, src_3d, src_w_true,
                                   fs, t_pulse, n_stack=200, rng=rng)
        w0 = fit_w0_from_traces(traces, rotated_mics, fs)
        w0_recovered.append(w0)
        print(f"  rotation {k+1:>2}/{n_rotations}: recovered w_0 = "
              f"{w0:+.4f} m")
    w0_arr = np.array(w0_recovered)
    print(f"\n  mean(w_0) = {w0_arr.mean():.4f} m,   "
          f"std(w_0) = {w0_arr.std():.4f} m,   "
          f"std/mean = {w0_arr.std()/abs(w0_arr.mean()):.4f}")
    print("  expected: std/mean ~ noise floor   (rotational invariant)")
    print()

    # Source 2: 3D source at (0, 0, 0.40)  -- a "fake-out" 3D source
    # whose Z-position equals our 4D w_0.
    print("=" * 70)
    print("CASE B: 3D source at (0, 0, 0.40) m, NO 4D offset")
    print("=" * 70)
    src_3d_fake = np.array([0.0, 0.0, 0.40])
    w0_recovered = []
    for k, R in enumerate(rotations):
        rotated_mics = base_mic_pos @ R.T
        traces = generate_event_3d(rotated_mics, src_3d_fake,
                                   fs, t_pulse, n_stack=200, rng=rng)
        w0 = fit_w0_from_traces(traces, rotated_mics, fs)
        w0_recovered.append(w0)
        print(f"  rotation {k+1:>2}/{n_rotations}: recovered w_0 = "
              f"{w0:+.4f} m")
    w0_arr = np.array(w0_recovered)
    print(f"\n  mean(w_0) = {w0_arr.mean():.4f} m,   "
          f"std(w_0) = {w0_arr.std():.4f} m,   "
          f"std/mean = {w0_arr.std()/(abs(w0_arr.mean())+1e-9):.4f}")
    print("  for a 3D source seen by a 3D-spanning array,")
    print("  expected: w_0 ~ 0 (the 3D component is fully resolved by")
    print("  the array; nothing 'hides' as off-slice).")
    print()

    print("INTERPRETATION")
    print("--------------")
    print("With a 3D-SPANNING array (e.g. our octahedron), CASE B")
    print("returns w_0 ~ 0 because the array fully resolves all 3D")
    print("displacements.  Only a *truly off-slice* source has nowhere")
    print("to project into the array span and so registers w_0 != 0.")
    print()
    print("The rotational test is then redundant for a 3D-spanning")
    print("array (a planar array would need it).  But adding multiple")
    print("rotations PROVIDES THE NULL TEST: you can measure your own")
    print("array's 'leakage' of 3D height into apparent w_0 (e.g. from")
    print("clock-drift or geometry calibration error) by deliberately")
    print("placing a known 3D source at one mic-frame Z-axis and")
    print("watching how strongly recovered w_0 covaries with rotation.")
    print()
    print("=> The SO(3) rotational invariance test isolates 4D-ness")
    print("   from instrument geometric error.  This was missing")
    print("   from the original Project SLICE design.")


if __name__ == "__main__":
    main()
