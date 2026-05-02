"""
Analysis pipeline for the SLICE multi-microphone array.

Given multi-channel pressure recordings p_i(t) at known mic positions
x_i, we run two tests on every detected onset:

(A)  Slope test:  fit the late-time tail in log-log space.
        slope ~ -2  --> consistent with 4D Green's tail.
        slope no fit / exponential decay --> 3D source.

(B)  Hyperbolic-geometry test:  the onset times t_i satisfy
        t_i = sqrt(|x_i - x_s|^2 + w_0^2) / c
     for source 3-position x_s and offset w_0 perpendicular to our slice.
     Fit (x_s, w_0, t0) by nonlinear least-squares.  If the best-fit
     w_0 is significantly above the noise floor on x_s, that is direct
     evidence the source does not lie in our 3-slice.
"""

import numpy as np
from scipy.optimize import least_squares


def detect_onset(p: np.ndarray, fs: float, threshold_factor: float = 6.0,
                 search_window_s: float = 0.001,
                 peak_fraction: float = 0.5) -> int:
    """Two-stage onset detection.

    1) Find the global peak |p|_max and its index.
    2) Walk backwards from the peak to the LAST sample (before the
       peak) where |p| crosses peak_fraction * peak.  This is the
       peak-relative onset, which is invariant under additive noise
       reduction (stacking) -- a noise threshold method drifts as SNR
       improves; this one does not.

    A trace must also clear a noise gate -- if the peak is below
    threshold_factor * std(noise on leading 10%) the trace is rejected
    (returns -1)."""
    n_lead = max(10, int(0.10 * len(p)))
    noise_std = float(np.std(p[:n_lead])) + 1e-12
    peak_idx = int(np.argmax(np.abs(p)))
    peak_val = float(np.abs(p[peak_idx]))
    if peak_val < threshold_factor * noise_std:
        return -1
    thr = peak_fraction * peak_val
    walking = peak_idx
    while walking > 0 and abs(p[walking]) > thr:
        walking -= 1
    return walking


def fit_tail_slope(p: np.ndarray, fs: float, onset_idx: int,
                   tail_start_s: float = 0.0005,
                   tail_end_s: float = 0.020,
                   noise_floor_factor: float = 5.0) -> dict:
    """Fit log|p(t)| = slope * log(t - t_onset) + intercept.

    The fit window starts `tail_start_s` after the onset and extends
    until either `tail_end_s` OR the smoothed amplitude falls below
    `noise_floor_factor * noise_std` (whichever happens first).  This
    is the key fix that lets the test work at realistic SNR -- power-law
    fits over data buried in noise return a flat slope, false-negating
    real 4D sources.  Restricting to the high-SNR portion of the tail
    preserves the physical signal."""
    n_lead = max(10, int(0.05 * len(p)))
    noise_std = float(np.std(p[:n_lead])) + 1e-12
    n_start = onset_idx + int(tail_start_s * fs)
    n_end_full = min(onset_idx + int(tail_end_s * fs), len(p) - 1)
    if n_end_full - n_start < 20:
        return {"slope": np.nan, "intercept": np.nan, "R2": 0.0, "n": 0}
    seg = np.abs(p[n_start:n_end_full])
    # Smooth with a moving average to suppress single-sample noise spikes
    win = max(3, int(5e-5 * fs))
    seg_smooth = np.convolve(seg, np.ones(win) / win, mode="same")
    above = seg_smooth > noise_floor_factor * noise_std
    # Find where signal first falls below floor (stop the fit there)
    if not above.any():
        return {"slope": np.nan, "intercept": np.nan, "R2": 0.0, "n": 0}
    last_good = int(np.where(above)[0].max())
    n_end = n_start + last_good + 1
    if n_end - n_start < 20:
        return {"slope": np.nan, "intercept": np.nan, "R2": 0.0, "n": 0}
    t_rel = (np.arange(n_start, n_end) - onset_idx) / fs
    amp = np.abs(p[n_start:n_end])
    valid = (t_rel > 0) & (amp > 0)
    if valid.sum() < 10:
        return {"slope": np.nan, "intercept": np.nan, "R2": 0.0, "n": 0}
    log_t = np.log(t_rel[valid])
    log_p = np.log(amp[valid])
    slope, intercept = np.polyfit(log_t, log_p, 1)
    pred = slope * log_t + intercept
    ss_res = np.sum((log_p - pred) ** 2)
    ss_tot = np.sum((log_p - log_p.mean()) ** 2) + 1e-30
    r2 = 1.0 - ss_res / ss_tot
    return {"slope": float(slope), "intercept": float(intercept),
            "R2": float(r2), "n": int(valid.sum())}


def fit_hyperbolic_source(mic_positions: np.ndarray,
                          onset_times: np.ndarray,
                          c: float = 343.0,
                          x0_guess: np.ndarray = None) -> dict:
    """Fit (x_s, w_0, t0) so that  t_i - t0 = |(mic_i - x_s, w_0)| / c.

    Returns a dict with the source 3-position estimate, the offset
    w_0 (>= 0 by convention), the emission time t0, and residual.
    """
    M = len(mic_positions)
    if x0_guess is None:
        x0_guess = mic_positions.mean(axis=0)
    p0 = np.concatenate([x0_guess, [0.01, 0.0]])    # x_s, w_0, t0

    def residuals(params):
        xs = params[:3]
        w0 = params[3]
        t0 = params[4]
        d = mic_positions - xs
        r4 = np.sqrt(np.sum(d * d, axis=1) + w0 * w0)
        return (onset_times - t0) - r4 / c

    res = least_squares(residuals, p0,
                        bounds=([-100, -100, -100, 0.0, -1.0],
                                [+100, +100, +100, 100.0, +1.0]))
    xs = res.x[:3]
    w0 = float(res.x[3])
    t0 = float(res.x[4])
    return {"x_s": xs, "w_0": w0, "t_0": t0,
            "residual": float(np.linalg.norm(res.fun)),
            "residual_max_us": float(np.max(np.abs(res.fun)) * 1e6)}


def slice_signature(slope: float, R2: float, w_0: float,
                    w_0_uncertainty: float,
                    rotational_test: dict = None) -> dict:
    """Combine the available tests into a single SLICE flag.

    All tests must agree:
      - tail slope in [-2.5, -1.5] AND R^2 > 0.85    (slope_test)
      - |w_0| > 3 sigma_w0                            (geometry_test)
      - if rotational_test provided: std(w_0)/mean(w_0) < 0.20  (4D rigid)

    The rotational_test is the only criterion with no known 3D
    false-positive analog. When available it dominates the verdict.
    Pass it as: {"sigma_over_mean": float, "n_rotations": int}

    Returns a dict with the per-test booleans and a summary verdict."""
    slope_ok = (-2.5 <= slope <= -1.5) and (R2 > 0.85)
    geom_ok  = abs(w_0) > 3.0 * max(w_0_uncertainty, 1e-9)
    rot_ok   = (rotational_test is not None
                and rotational_test.get("n_rotations", 0) >= 4
                and rotational_test.get("sigma_over_mean", 1.0) < 0.20)
    rot_attempted = rotational_test is not None

    if rot_attempted:
        # Rotational test dominates when present
        if rot_ok and geom_ok:
            verdict = "SLICE_POSITIVE_RIGOROUS"        # the gold standard
        elif rot_ok and not geom_ok:
            verdict = "INVARIANT_BUT_BELOW_GEOM_THRESHOLD"
        elif not rot_ok and geom_ok:
            verdict = "GEOMETRY_LOOKS_4D_BUT_NOT_ROTATIONALLY_INVARIANT"
        else:
            verdict = "NULL"
    else:
        # Legacy single-orientation interpretation (less rigorous)
        if slope_ok and geom_ok:
            verdict = "SLICE_POSITIVE_PROVISIONAL"
        elif slope_ok and not geom_ok:
            verdict = "POWER_LAW_NO_OFFSET"
        elif geom_ok and not slope_ok:
            verdict = "OFFSET_NO_POWER_LAW"
        else:
            verdict = "NULL_3D_SOURCE"

    return {"slope_test_pass": slope_ok,
            "geometry_test_pass": geom_ok,
            "rotational_test_pass": rot_ok,
            "rotational_test_attempted": rot_attempted,
            "verdict": verdict}
