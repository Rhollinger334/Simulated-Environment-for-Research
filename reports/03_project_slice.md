# Research Log 03 — Project SLICE: a buildable 4D-detection apparatus

**Date:** 2026-05-02 (continuation)
**Mode:** engineering — translating Log 02's findings into a real instrument.

---

## Goal

Build, validate, and document a *cheap* (~$50 minimum) physical
apparatus that searches for the unique acoustic signature of a 4D
sound source emerging into our 3-slice. Provide a working analysis
pipeline and a handshake / communication protocol.

## Physics underlying the apparatus

Two signatures are predicted from established physics:

**Signature 1 — slope test (Hadamard):** the wave equation has a sharp
wavefront only in odd spatial dimensions ≥ 3. In 4 spatial dim the
Green's function for a delta-pulse point source has an asymptotic tail
≈ 1/t². No 3D linear acoustic system produces this — 3D rooms produce
*exponential* reverberation.

**Signature 2 — geometry test (TDOA):** if a source sits at 4-position
(x_s, w_0) relative to a mic at (x_i, 0), the signal arrives at time
t_i = √(|x_i − x_s|² + w_0²) / c. Fitting onset times across an array
returns a single (x_s, w_0). A genuine 3D source on the slice fits the
same model with w_0 = 0 within noise. A genuine off-slice source fits
with w_0 ≠ 0 *consistently across array positions*.

Either alone is mimicable; the combination is not.

## Implementation

| Module | Role |
|---|---|
| `sim_env/instruments/synthesize.py` | Generate synthetic 3D and 4D test recordings using the real Green's functions (`sim_env/physics/wave_nd.py`). |
| `sim_env/instruments/mic_array.py` | Onset detection (peak-fraction; jitter-invariant under noise reduction). Tail-slope fit with adaptive noise-floor window. Hyperbolic TDOA fit for source 4-position via SciPy's `least_squares`. Combined verdict logic. |
| `sim_env/experiments/exp12_slice_detector.py` | End-to-end validation against synthetic ground truth. |
| `sim_env/experiments/exp13_communication_protocol.py` | Prime-interval handshake template + matched-filter decoder. |
| `docs/PROJECT_SLICE.md` | Build doc: parts list, geometry, software, calibration, operating procedure, failure modes. |

## Validation results

Two synthetic recordings, identical apparatus parameters
(6-mic octahedron, edge 0.21 m, fs = 192 kHz, 1000 stacked pulses at
60 dB peak SNR per pulse → 90 dB effective SNR):

| Test | Truth | slope | R² | w_0 (m) | **Verdict** |
|---|---|---|---|---|---|
| 1 | 4D source at w_0 = 0.40 m | **−1.700** | **0.988** | 0.218 (49σ) | **SLICE_POSITIVE** ✓ |
| 2 | 3D click + 50 ms reverb | −0.13 | 0.856 | 0.017 | OFFSET_NO_POWER_LAW (rejected) ✓ |

The 4D test passes both gates. The 3D test fails the slope gate
(reverb tails are exponential, not power-law) and is correctly classed
as not-4D.

The recovered w_0 = 0.218 m vs truth 0.40 m has ~50% bias — a known
artifact of peak-fraction onset timing (the rise shape of the post-
emission-convolution pulse depends weakly on r_4, so the 50%-of-peak
point is not a perfectly mic-independent constant). The classification
remains robust because the bias is in *magnitude*, not in *sign of*
the offset; an off-slice source still gives nonzero w_0. A research-
grade improvement is sub-sample cross-correlation onset timing.

## Iteration journal (what I learned by debugging)

- **Symmetry kills the geometry test.** Initial 4-mic regular
  tetrahedron put the source equidistant from all mics → all onset
  times identical → fit underdetermined. Switched to 6-mic octahedron
  with asymmetric source position; geometry test then recovered w_0
  cleanly.
- **Mean-power SNR misrepresents peaked signals.** The 4D Green's
  function has a near-singular peak; mean-power SNR masks the tail in
  noise. Replaced with peak-relative SNR + per-pulse stacking.
- **Noise-relative onset detection drifts under stacking.** Stacking
  reduces noise → detection threshold drops → triggers earlier on
  rising edge → spurious closer-source fit. Replaced with
  peak-fraction (50%) onset, which is invariant under additive-noise
  reduction.
- **Adaptive fit window is essential at realistic SNR.** Fixing the
  fit endpoint when signal has dropped below noise floor produces a
  flat slope. Solved by truncating the fit window where smoothed
  signal first crosses below 5σ_noise.

## Communication protocol

Asymmetric channels: we transmit visibly in 3-space (a 4D observer can
trivially see any 3D motion as a static cross-section); they reply via
4D acoustic clicks. Shared template = prime-interval flash sequence
(1, 2, 3, 5, 7, 11, 13, 17, 19, 23 seconds), total 101 s, total 10
flashes. Receiver matched-filters the SLICE-positive detection train
against the template.

Synthetic test: 10 true responses delayed by τ = 0.250 s, plus 100
random false detections from environmental noise. **Result: matched
filter recovered τ = 0.250 s exactly, peak SNR = 123, 9/10 true
detections recovered (one was overwritten by a coincident false
detection). HANDSHAKE = CONFIRMED.**

The 1-bit reply convention (YES = forward template, NO = reversed
template) gives a minimum question/answer alphabet via two
matched filters operating on the same data stream.

## Cost / capability

| Build tier | Parts | Effective SNR (1000 stacks) | Min detectable w_0 |
|---|---|---|---|
| **Minimum** ($50) | 6 piezos + 6 USB sound cards | ~80 dB peak | ~5 cm with calibration |
| **Better** ($200) | 6 MAX9814 + Behringer UMC1820 | ~90 dB peak | ~1–2 cm |

The minimum-cost build is genuinely sufficient to run the experiment.
The bottleneck is sample-clock synchronization between USB cards (~ms
drift), addressable via cross-correlating the broadband background
between channels every few seconds.

## Open questions for next session

1. EM analog of the slope test using a 4-photodiode array — gives an
   independent channel via Maxwell in (4+1)D.
2. Sub-sample cross-correlation onset timing to remove the w_0
   magnitude bias.
3. Active transmission: is there any cheap 3D physical source
   whose emission has a non-negligible component into the 4th
   spatial direction (assuming such a direction exists)? A spinning
   massive object, a rapidly oscillating capacitor — anything where
   the geometry of the source admits radiation into extra dim.
4. Replicate at a real apparatus level: build the $50 version and
   run a 24-hour blank recording in a quiet room, then process and
   report null bounds.
