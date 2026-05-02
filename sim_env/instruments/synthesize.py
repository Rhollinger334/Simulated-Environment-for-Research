"""
Synthesise test signals for the SLICE microphone array.

We generate, on a fixed sampling grid, the pressure waveform that a 3D
microphone at a chosen position would record from:

  - an idealised 3D point source at known position (delta wavefront,
    plus optional exponential room-reverb tail),
  - a 4D point source at known (x, y, z, w_offset) emitting a delta
    pulse at t=0, using the exact 4D Green's function in
    sim_env.physics.wave_nd.

These synthetic recordings are real-physics ground truth used to
validate the analysis pipeline before pointing it at live hardware.
"""

import numpy as np
from sim_env.physics import wave_nd as W


def synth_3d_click(mic_pos: np.ndarray, src_pos: np.ndarray,
                   t: np.ndarray, c: float = 343.0,
                   pulse_width: float = 50e-6,
                   reverb_tau: float = 0.0,
                   reverb_amp: float = 0.0) -> np.ndarray:
    """A 3D click: Gaussian-smeared delta at arrival time, plus optional
    exponential reverberation tail (models a real room)."""
    r = float(np.linalg.norm(mic_pos - src_pos))
    t_arr = r / c
    arg = (t - t_arr)
    main = np.exp(-arg * arg / (2 * pulse_width * pulse_width)) \
           / (pulse_width * np.sqrt(2 * np.pi)) / (4 * np.pi * c * max(r, 1e-9))
    if reverb_tau > 0:
        rev = reverb_amp * np.where(t > t_arr,
                                    np.exp(-(t - t_arr) / reverb_tau), 0.0)
        return main + rev
    return main


def synth_4d_click(mic_pos: np.ndarray, src_pos_3d: np.ndarray,
                   src_w: float, t: np.ndarray, c: float = 343.0,
                   emission_sigma: float = 80e-6) -> np.ndarray:
    """A genuine 4D click: source at (src_pos_3d, src_w) emits a Gaussian
    pulse of width emission_sigma centered at t=0 (a physical emitter,
    not a literal delta).  Convolves the 4D Green's function with the
    emission pulse so the peak amplitude is finite."""
    obs_relative = mic_pos - src_pos_3d
    raw = W.signal_from_4d_source(obs_relative, src_w, t, c=c)
    # Build emission pulse on the same time grid (centered at the median
    # so convolution doesn't shift the trace)
    dt = t[1] - t[0]
    n_kern = int(8 * emission_sigma / dt) | 1     # odd length
    tk = (np.arange(n_kern) - n_kern // 2) * dt
    kernel = np.exp(-tk * tk / (2 * emission_sigma * emission_sigma))
    kernel /= kernel.sum()
    # Replace any NaNs left over from the singular Green's function
    raw = np.nan_to_num(raw, nan=0.0, posinf=0.0, neginf=0.0)
    return np.convolve(raw, kernel, mode="same")


def add_noise(signal: np.ndarray, snr_db: float, rng=None,
              mode: str = "peak") -> np.ndarray:
    """Add white Gaussian noise at requested SNR.
    mode='peak': SNR defined as peak |signal| / noise std (better for
                 detecting low-amplitude tails of peaked sources).
    mode='power': SNR defined as mean(signal^2) / noise variance."""
    if rng is None:
        rng = np.random.default_rng()
    if mode == "peak":
        peak = float(np.max(np.abs(signal))) + 1e-30
        noise_std = peak / (10 ** (snr_db / 20.0))
    else:
        sig_power = np.mean(signal * signal) + 1e-30
        noise_std = np.sqrt(sig_power / (10 ** (snr_db / 10.0)))
    return signal + rng.normal(scale=noise_std, size=signal.shape)
