"""
Chiral-inversion polarimetry instrument for the SLICE family.

Premise.  Earlier we established (Experiment 10) that a continuous SO(4)
rotation can flip the chirality of a 3D body, while no SO(3) rotation
can.  Therefore, if a 4D entity manipulates 3D matter in our slice, an
unmistakable visible signature is the spontaneous CHIRAL INVERSION of
a chiral substance.

A polarimeter measures chirality directly: a chiral solution rotates
the polarization plane of transmitted light by an angle proportional
to the (D - L) enantiomer concentration.  D-glucose rotates by about
+52.7 deg/(dm * g/mL) at 20 C, the sodium D-line (CRC Handbook of
Chemistry and Physics, 102nd ed., Sec. 8).

Apparatus, $15:
  - green or red laser pointer                $5
  - 2x linear-polarizer sheet (Edmund/Amazon) $5
  - clear glass or acrylic test-tube (sealed) $1
  - food-grade dextrose (D-glucose) + water   $2
  - smartphone or photodiode for intensity    $0 (already owned)
  - lego/cardboard rig                        $2

Detection. Run laser through polarizer 1 -> chiral solution -> polarizer
2 -> photodetector.  Set the angle of polarizer 2 so transmitted
intensity is at the steepest part of Malus's law (45 deg from extinction).
Then any change in chirality of the solution shifts the effective
"angle" of polarization seen by P2, producing a measurable intensity
change.

False-positive sources we must control:
  - temperature drift (specific rotation of glucose: ~ -0.04 deg/C)
  - laser intensity drift (use a reference photodiode)
  - bacterial contamination (sterilize, seal, run < 24h)
  - bubbles, sediment in the tube (vertical orientation, settle 30 min)
  - pH change (negligible for pure glucose in distilled water)

These set the achievable noise floor, which we estimate.
"""

import numpy as np


# Specific rotations at 20 C, sodium D-line (589.3 nm).
# CRC Handbook of Chemistry and Physics, 102nd ed., Sec. 8 (Optical Rotations).
SPECIFIC_ROTATION_D_GLUCOSE = +52.7      # deg / (dm * g/mL)
SPECIFIC_ROTATION_L_GLUCOSE = -52.7
SPECIFIC_ROTATION_SUCROSE   = +66.37
TEMP_COEFF_D_GLUCOSE        = -0.04      # deg per C, approximate


def optical_rotation_deg(specific_rotation: float, length_dm: float,
                         concentration_g_mL: float) -> float:
    """Biot's law: alpha = [alpha] * L * c."""
    return specific_rotation * length_dm * concentration_g_mL


def malus_law(intensity_in: float, angle_diff_rad: float) -> float:
    """Transmitted intensity through crossed polarizers (perfect)."""
    return intensity_in * np.cos(angle_diff_rad) ** 2


def detector_response(I_laser: float, alpha_solution_rad: float,
                      polarizer2_angle_rad: float,
                      reference_polarizer1_angle_rad: float = 0.0,
                      polarizer_extinction: float = 1e-3) -> float:
    """Net intensity at the photodetector.  Real polarizers have a finite
    extinction ratio (1e-3 typical); we include it so the noise model
    isn't infinitely sharp at the null."""
    delta = polarizer2_angle_rad - (reference_polarizer1_angle_rad
                                    + alpha_solution_rad)
    perfect = np.cos(delta) ** 2
    return I_laser * (perfect + polarizer_extinction)


def chirality_to_alpha(d_fraction: float, total_concentration_g_mL: float,
                       length_dm: float, T_celsius: float = 20.0) -> float:
    """Given a D-glucose fraction d_fraction in [0, 1] (rest is L), return
    the optical rotation in radians.  Includes temperature correction."""
    f_D = d_fraction
    f_L = 1.0 - d_fraction
    sr = (f_D * SPECIFIC_ROTATION_D_GLUCOSE +
          f_L * SPECIFIC_ROTATION_L_GLUCOSE)
    sr += TEMP_COEFF_D_GLUCOSE * (T_celsius - 20.0)
    return np.deg2rad(sr * length_dm * total_concentration_g_mL)


def detect_chirality_step(intensities: np.ndarray, fs: float,
                          step_threshold_sigma: float = 5.0,
                          short_window_s: float = 30.0,
                          long_window_s:  float = 600.0,
                          guard_window_s: float = 60.0,
                          thermal_period_s: float = 3600.0) -> dict:
    """Two-window step detector that ignores slow drift.

    For each candidate time t, compute:
      - "before" mean over [t - long_window, t - guard_window]
      - "after"  mean over [t + guard_window, t + long_window]
      - sigma estimated from short-window detrended residual at start

    A genuine step shows  |after_mean - before_mean| >> sigma.
    Slow drift shifts both before and after by the SAME amount, so
    their difference stays small.  This kills the thermal-drift
    false positive that a naive single-baseline detector suffers.
    """
    n = len(intensities)
    nL = int(long_window_s * fs)
    nG = int(guard_window_s * fs)
    nS = int(short_window_s * fs)
    if n < 2 * (nL + nG):
        return {"step_time_s": None, "step_amplitude": 0.0,
                "noise_sigma": float(np.std(intensities))}

    # noise sigma estimate: detrend the first long window, take std
    leading = intensities[:nL]
    p = np.polyfit(np.arange(nL), leading, 1)
    resid = leading - (p[0] * np.arange(nL) + p[1])
    noise_sigma = float(np.std(resid)) + 1e-30

    best = {"step_time_s": None, "step_amplitude": 0.0,
            "noise_sigma": noise_sigma, "z_at_step": 0.0}
    best_abs_z = 0.0

    # Sweep candidate step times; cheap because we use cumulative sums
    cs = np.cumsum(intensities)
    def window_mean(a, b):
        a = max(a, 0); b = min(b, n)
        if a == 0:
            return cs[b - 1] / b
        return (cs[b - 1] - cs[a - 1]) / (b - a)

    stride = max(1, int(0.1 * fs))    # sample every 0.1 s
    for t in range(nL + nG, n - nL - nG, stride):
        before = window_mean(t - nL - nG, t - nG)
        after  = window_mean(t + nG, t + nG + nL)
        # noise on the difference: sigma * sqrt(2/nL) for each, combined
        sigma_diff = noise_sigma * np.sqrt(2.0 / nL)
        z = (after - before) / max(sigma_diff, 1e-30)
        if abs(z) > best_abs_z:
            best_abs_z = abs(z)
            best = {"step_time_s": float(t / fs),
                    "step_amplitude": float(after - before),
                    "noise_sigma": noise_sigma,
                    "z_at_step": float(z)}
    if best_abs_z < step_threshold_sigma:
        best["step_time_s"] = None
        return best

    # Discrimination: a true STEP shifts the mean over one thermal-period
    # window by ~ step_amplitude; periodic drift averages to zero over
    # an integer number of periods.  Compare windows of size
    # one thermal period on each side of the candidate step.
    if best["step_time_s"] is not None:
        n_period = int(thermal_period_s * fs)
        t_step = int(best["step_time_s"] * fs)
        before_start = max(0, t_step - n_period)
        after_end    = min(n, t_step + n_period)
        if (t_step - before_start) >= int(0.8 * n_period) and \
           (after_end - t_step) >= int(0.8 * n_period):
            before_period_mean = window_mean(before_start, t_step)
            after_period_mean  = window_mean(t_step, after_end)
            persistent = after_period_mean - before_period_mean
            ratio = abs(persistent) / (abs(best["step_amplitude"]) + 1e-30)
            best["persistence_ratio"] = float(ratio)
            best["persistent_amplitude"] = float(persistent)
            # A real step has ratio ~ 1; pure drift averaged over a full
            # period has ratio ~ 0 because the period mean is invariant
            # under temperature oscillations.
            if ratio < 0.3:
                best["step_time_s"] = None
                best["rejected_as_drift"] = True
            else:
                best["rejected_as_drift"] = False
    return best
