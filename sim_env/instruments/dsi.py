"""
The Bayesian Dimensional Signature Index (DSI).

Definition:
    DSI(event)  =  log10  P(event | 4D source)  /  P(event | 3D source)

where the joint likelihood factorises across independent detection
channels.  Three channels are implemented here:

  1. Acoustic SLICE        (sim_env/instruments/mic_array.py)
       statistic = | w_0 | / sigma(w_0)  from the hyperbolic TDOA fit
  2. Optical interior      (sim_env/instruments/optical_array.py)
       statistic = distance-to-wall of extrapolated prior 3D position
  3. Chiral polarimeter    (sim_env/instruments/polarimeter.py)
       statistic = | step z-score |

For each, we model:
  - the NULL distribution (3D-source / no-event), giving false-positive
    rate as a function of statistic value
  - the SIGNAL distribution (4D source at some plausible amplitude)

The log-likelihood ratio per channel is computed; channels add.

Interpretation: DSI = +1 means a 10:1 odds ratio in favor of 4D.
DSI = +6 (one part in a million null probability) is "extraordinary
evidence"; DSI = +20 is unambiguous.
"""

import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Per-channel models.  These are calibrated to the null distributions we
# observed in synthetic ground truth from earlier experiments.
# ---------------------------------------------------------------------------


def acoustic_log_likelihood_ratio(w0_sigma_significance: float,
                                  signal_amplitude_sigma: float = 5.0) -> float:
    """Acoustic SLICE channel.  Null model: |w_0|/sigma is half-normal
    (folded gaussian, mean 0, var 1).  Signal model: |w_0|/sigma is
    half-normal centered at signal_amplitude_sigma.

    Returns log10 P(s | 4D) / P(s | 3D)."""
    s = max(0.0, w0_sigma_significance)
    log_p_null = stats.halfnorm.logpdf(s, loc=0.0, scale=1.0)
    log_p_4d   = stats.norm.logpdf(s, loc=signal_amplitude_sigma, scale=1.0)
    return float((log_p_4d - log_p_null) / np.log(10))


def optical_log_likelihood_ratio(prior_dist_mm: float,
                                 box_inradius_mm: float = 150.0,
                                 motion_noise_mm: float = 5.0) -> float:
    """Optical interior-appearance channel.  Null model: a 3D object
    entering at a wall has prior_dist ~ |Normal(0, motion_noise)|.
    Signal model: a 4D entity appears uniformly within the box, so its
    distance to the nearest wall is uniform on [0, box_inradius_mm].
    box_inradius_mm = half the smallest box edge (max interior depth)."""
    s = max(0.0, prior_dist_mm)
    log_p_null = stats.halfnorm.logpdf(s, scale=motion_noise_mm)
    # Clip to allowed range; if s exceeds inradius, that's a calibration
    # error -- treat as inradius (signal model "saturated").
    s_clipped = min(s, box_inradius_mm)
    log_p_4d = np.log(1.0 / box_inradius_mm)
    # Apply ratio at clipped position
    log_p_null_at_clipped = stats.halfnorm.logpdf(s_clipped, scale=motion_noise_mm)
    return float((log_p_4d - log_p_null_at_clipped) / np.log(10))


def polarimeter_log_likelihood_ratio(step_zscore: float,
                                     signal_z: float = 50.0,
                                     null_sigma: float = 1.0) -> float:
    """Chiral polarimeter channel.  Null: |z| ~ half-normal with sigma
    inflated by the search-over-time look-elsewhere effect (~ 10x).
    Signal: a real chirality-inversion event gives |z| approximately
    centered at signal_z."""
    z = abs(step_zscore)
    log_p_null = stats.halfnorm.logpdf(z, scale=10.0 * null_sigma)
    log_p_4d   = stats.norm.logpdf(z, loc=signal_z, scale=signal_z * 0.2)
    return float((log_p_4d - log_p_null) / np.log(10))


# ---------------------------------------------------------------------------
# Combined DSI
# ---------------------------------------------------------------------------


# Per-channel evidence cap reflecting irreducible systematic uncertainty
# (instrumentation glitches, calibration drift).  Standard in HEP analyses.
PER_CHANNEL_LOG10LR_CAP = 6.0    # max +/- 10^6 odds per channel


def _cap(x):
    return max(-PER_CHANNEL_LOG10LR_CAP, min(PER_CHANNEL_LOG10LR_CAP, x))


def compute_dsi(channels: dict) -> dict:
    """channels: a dict like
        {"acoustic":   {"w0_significance": 3.5},
         "optical":    {"prior_dist_mm": 250.0, "box_size_mm": 300.0},
         "polarimeter":{"z": 8.0}}
    Any subset of the three is allowed.  Returns dict with per-channel
    log10 LR and total DSI.
    """
    out = {}
    total = 0.0
    if "acoustic" in channels:
        v = _cap(acoustic_log_likelihood_ratio(channels["acoustic"]["w0_significance"]))
        out["acoustic_log10LR"] = v
        total += v
    if "optical" in channels:
        # Accept either box_inradius_mm or legacy box_size_mm = edge length
        opt = channels["optical"]
        if "box_inradius_mm" in opt:
            inradius = opt["box_inradius_mm"]
        else:
            inradius = opt.get("box_size_mm", 300.0) / 2.0
        v = _cap(optical_log_likelihood_ratio(opt["prior_dist_mm"], inradius))
        out["optical_log10LR"] = v
        total += v
    if "polarimeter" in channels:
        v = _cap(polarimeter_log_likelihood_ratio(channels["polarimeter"]["z"]))
        out["polarimeter_log10LR"] = v
        total += v
    out["DSI"] = float(total)
    try:
        out["odds_4D_to_3D"] = float(10 ** total) if total < 300 else float("inf")
    except OverflowError:
        out["odds_4D_to_3D"] = float("inf")
    out["interpretation"] = _interpret(total)
    return out


def _interpret(dsi: float) -> str:
    if dsi < -3:
        return "Strongly favors 3D (null)."
    if dsi < 0:
        return "Mild evidence for 3D / null."
    if dsi < 1:
        return "Inconclusive."
    if dsi < 3:
        return "Suggestive of 4D event."
    if dsi < 6:
        return "Strong evidence for 4D event."
    if dsi < 12:
        return "Very strong evidence for 4D event."
    return "Extraordinary evidence -- demands replication."
