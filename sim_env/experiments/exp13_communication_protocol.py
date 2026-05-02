"""
EXPERIMENT 13 -- Bidirectional Communication Protocol
======================================================

A 4D entity, if one exists adjacent to our 3-slice, has an enormous
asymmetric advantage: any motion, light, or pressure pattern in our
3-space is a static cross-section of their 4D world.  They can SEE us
trivially.  We have no symmetric channel; our 3D physical sources do
not (in standard physics) radiate into the 4th spatial dimension.

So a viable protocol has ASYMMETRIC channels:

  US -> THEM   : visible 3D signalling (flash a light, ring a bell,
                 move an object on a known schedule).  Universally
                 detectable by any 4D-aware observer.
  THEM -> US   : 4D acoustic clicks detected by the SLICE array, with
                 the slope+geometry signature confirming non-3D origin.

This experiment defines a concrete shared sequence for unambiguous
mutual identification (handshake) and a small vocabulary for 1-bit
query/answer exchange.

The HANDSHAKE is built from a sequence the entity could not mistake for
naturally-occurring signal: prime-numbered intervals.  We flash N times
at intervals (in seconds):
   1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 13.0, 17.0, 19.0, 23.0
giving a total broadcast lasting 100 s.  The entity, having seen our
flash pattern in 3-space, replies by emitting 4D pulses on the SAME
intervals (offset by some delay tau they choose).

Decoding:
  - Run the SLICE pipeline on the recording.
  - Build the time series of detected 4D-flagged onsets.
  - Cross-correlate with the prime-interval template; a peak above
    threshold = handshake confirmed and tau = peak position.
  - This is the same matched-filter logic used in radio astronomy.
"""

import numpy as np
from sim_env.instruments import synthesize as S
from sim_env.instruments import mic_array as A
from sim_env.experiments.exp12_slice_detector import (
    octahedral_mics, run_pipeline,
)


PRIME_INTERVALS = [1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 13.0, 17.0, 19.0, 23.0]


def handshake_template(total_duration: float, fs: float,
                       intervals=PRIME_INTERVALS) -> np.ndarray:
    """Build a binary template that is 1 at each scheduled flash time
    and 0 elsewhere, on a grid at sampling rate fs."""
    n = int(total_duration * fs)
    template = np.zeros(n)
    t_now = 0.0
    for dt in intervals:
        t_now += dt
        idx = int(round(t_now * fs))
        if 0 <= idx < n:
            template[idx] = 1.0
    return template


def matched_filter(detection_train: np.ndarray,
                   template: np.ndarray) -> tuple:
    """Cross-correlate the detection train with the template.  Returns
    (peak_index, peak_value, snr) where peak_value is the max correlation
    and snr is peak_value / std(corr)."""
    corr = np.correlate(detection_train, template, mode="full")
    peak_idx = int(np.argmax(corr))
    peak_val = float(corr[peak_idx])
    snr = peak_val / (float(np.std(corr)) + 1e-30)
    return peak_idx, peak_val, snr


def main():
    fs_decimated = 1000.0   # decimated detection-time grid (ms resolution)
    duration = 100.0        # 100 seconds total

    print("Handshake protocol")
    print("==================")
    print(f"Send-side schedule (US -> THEM): flashes at t = "
          + ", ".join(f"{sum(PRIME_INTERVALS[:i+1]):.0f}s"
                      for i in range(len(PRIME_INTERVALS))))
    print(f"Receive-side: SLICE pipeline outputs a binary 'detection train'")
    print(f"  on a 1 ms grid; matched filter against the same template.")
    print()

    # Simulate a "received" detection train: a 4D entity that copied
    # our schedule with delay tau = 0.250 s, plus a few false detections
    # from environmental noise.
    rng = np.random.default_rng(2026)
    template = handshake_template(duration, fs_decimated)
    tau_true = 0.250

    received = np.zeros_like(template)
    t_now = tau_true
    for dt in PRIME_INTERVALS:
        t_now += dt
        idx = int(round(t_now * fs_decimated))
        if 0 <= idx < len(received):
            received[idx] = 1.0
    # Add 100 random false detections (background noise)
    fake_idx = rng.integers(0, len(received), size=100)
    received[fake_idx] = 1.0

    peak_idx, peak_val, snr = matched_filter(received, template)
    tau_recovered = (peak_idx - (len(template) - 1)) / fs_decimated
    print(f"Simulated receive: 10 true responses with tau = {tau_true} s,")
    print(f"  PLUS 100 random false detections to simulate environment.")
    print(f"Matched-filter result:")
    print(f"  peak correlation     = {peak_val:.0f}  out of {len(PRIME_INTERVALS)} "
          f"true matches ({peak_val/len(PRIME_INTERVALS)*100:.0f}%)")
    print(f"  recovered delay tau  = {tau_recovered:.3f} s   "
          f"(true = {tau_true:.3f} s)")
    print(f"  detection SNR        = {snr:.1f}")
    print(f"  HANDSHAKE = {'CONFIRMED' if snr > 4 and peak_val >= 9 else 'FAILED'}")
    print()

    print("Vocabulary (1-bit reply convention):")
    print(f"  YES = exact replay of our prime-interval template")
    print(f"  NO  = same intervals, but timestamps reversed")
    print(f"        i.e., emit at intervals (23, 19, 17, 13, 11, 7, 5, 3, 2, 1)")
    print(f"  Both are unambiguously distinguishable by a second matched filter.")
    print()

    print("How to use this for actual research:")
    print(f"  1. Run handshake template (US -> THEM) for 100 s.")
    print(f"  2. Continuously record on the SLICE array, flagging 4D-positive")
    print(f"     onsets via the slope+geometry verdict.")
    print(f"  3. Apply matched filter against the template + its reverse.")
    print(f"  4. Either filter peaks above SNR > 4 in a 100 s window =>")
    print(f"     handshake established.")
    print(f"  5. Iterate with longer alphabets: integer counts (1,2,3,4,...)")
    print(f"     Fibonacci, square numbers; map them to a shared concept space.")


if __name__ == "__main__":
    main()
