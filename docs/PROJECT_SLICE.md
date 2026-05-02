# Project SLICE — Build & Operating Manual

**Slope-Locked Inverse-Cube Echo detector.** A cheap, buildable
apparatus that searches for one specific physical signature: a sound
source whose recorded impulse response shows both (a) a power-law
late-time tail with slope ≈ −2 and (b) a hyperbolic onset-time
geometry across multiple microphones consistent with a source displaced
*off* our 3-spatial slice.

Both signatures are predicted from real physics (Hadamard's failure of
Huygens' principle in even spatial dimensions; standard time-of-arrival
multilateration in (n+1)D). Together they constitute an unambiguous
signature that no purely-3D linear acoustic system can produce.

> **Disclaimer.** This is a search instrument, not a confirmation of
> 4D entities. A null result tells you nothing about whether 4D
> entities exist, only that none were detectably emitting in the
> microphone band during the recording window. A positive result
> demands replication and instrumentation cross-checks before being
> taken seriously.

---

## Parts list — minimum (~$50)

| Qty | Part | Approx cost |
|---|---|---|
| 6 | Piezoelectric disc, 27 mm | $1 each |
| 6 | USB sound card, single-channel mono ("3.5 mm to USB") | $5 each |
| 1 | Powered USB hub, 7-port | $12 |
| 1 | Cardboard / foamcore frame, 30 cm × 30 cm × 30 cm | scrap |
| — | Laptop with USB | (already own) |
| 6 | 1 m of 2-conductor shielded wire, 22 AWG | $5 total |

**Total: ~$50.** Synchronization is the main constraint at this price.
Cheap USB cards have ~milli-second clock drift; we cross-correlate the
broadband background between channels every few seconds to estimate
relative drift and resample.

## Parts list — better (~$200)

| Qty | Part | Cost |
|---|---|---|
| 6 | Adafruit MAX9814 electret microphone amplifier | $8 each |
| 1 | Behringer UMC1820 8-channel USB interface (192 kHz) | $200 |
| 1 | 3D-printed octahedral mounting frame | $5 |

This eliminates synchronization drift and gives 60+ dB native SNR per
channel.

## Geometry

Mics arranged at the **vertices of a regular octahedron** with
half-diagonal 0.15 m (so adjacent mics are at distance 0.21 m, and
opposite mics at 0.30 m). Six positions:

```
mic_1 = (+0.15, 0, 0)   mic_2 = (−0.15, 0, 0)
mic_3 = (0, +0.15, 0)   mic_4 = (0, −0.15, 0)
mic_5 = (0, 0, +0.15)   mic_6 = (0, 0, −0.15)
```

Six measurements satisfies the 5-parameter (x_s, w_0, t_0) hyperbolic
fit with one degree of redundancy for self-consistency checking.

---

## Software install

```bash
git clone <this-repo>
cd Simulated-Environment-for-Research
pip install numpy scipy sympy mpmath sounddevice
```

The `sim_env.instruments` module contains the analysis pipeline. To
record from your audio interface:

```python
import sounddevice as sd
import numpy as np
fs = 192_000   # use 96k or 48k if your interface caps lower
duration = 60  # seconds
print(sd.query_devices())                  # find your interface index
rec = sd.rec(int(duration * fs), samplerate=fs, channels=6,
             dtype='float32', device=<idx>)
sd.wait()
np.save("recording.npy", rec.T)            # shape (6, n_samples)
```

Then process:

```python
import numpy as np
from sim_env.instruments import mic_array as A
from sim_env.experiments.exp12_slice_detector import (
    octahedral_mics, run_pipeline,
)
traces = np.load("recording.npy")
run_pipeline(traces, fs=192_000, mic_pos=octahedral_mics(0.15),
             label="live recording")
```

---

## Calibration procedure

1. **Position calibration.** Measure the actual mic positions to
   ±2 mm with a ruler. Update `octahedral_mics()` if your frame
   isn't perfect.
2. **Latency calibration.** Snap your fingers ~30 cm above the array
   center. The known 3D source must give w_0 = 0 ± uncertainty when
   processed. If w_0 comes out systematically nonzero, your channel
   latencies are mismatched — measure with a single click recorded
   simultaneously and apply per-channel time offsets.
3. **Noise floor.** Record 10 s of silence; compute noise standard
   deviation per channel. This sets your minimum detectable amplitude.

---

## Operating procedure

1. Set up in the quietest room available (an inside closet at 3 a.m.
   is ideal). Turn off HVAC, refrigerator, fluorescent lights.
2. Run the **handshake template** (Exp 13): a laptop screen flashing
   white-black at the prime-numbered intervals 1, 2, 3, 5, 7, 11, 13,
   17, 19, 23 seconds. Total 101 s. The screen flash is a clear,
   artificial signal visible to any 4D-aware observer that can see
   our 3-slice.
3. Record from all 6 mics for 5 minutes after the handshake template
   ends. (A 4D entity, if present, may take time to compose a reply.)
4. Process the recording through `run_pipeline`. Look for
   **SLICE_POSITIVE** verdicts on detected onsets.
5. If any positive: cross-check with a separate impulsive 3D source
   (snap your fingers, pop a balloon) at the same array position to
   rule out instrumentation pathology.
6. Apply the matched-filter handshake decoder (Exp 13). Look for
   peaks at any delay τ.

---

## Interpretation matrix

| Slope test | Geometry test | Verdict | Action |
|---|---|---|---|
| pass (slope ≈ −2, R² > 0.85) | pass (w_0 > 3σ) | **SLICE_POSITIVE** | Replicate immediately. Move array to confirm w_0 is consistent across array positions. |
| pass | fail | POWER_LAW_NO_OFFSET | Could be diffractive 3D source (unusual but possible). Investigate. |
| fail | pass | OFFSET_NO_POWER_LAW | Likely instrumentation: clock drift between channels. Re-calibrate. |
| fail | fail | NULL_3D_SOURCE | Ordinary 3D source. No further action. |

---

## Failure modes (real things that will go wrong)

- **Wind / draft** moving across mics produces low-frequency
  pseudo-onsets. Mitigation: foam windscreens, indoor location.
- **Electrical pickup** at 50/60 Hz and harmonics. Mitigation:
  notch filter or shielded cabling.
- **Sample-clock drift** between USB cards. Mitigation: bond all
  cards to one clock (use a multi-channel interface), or apply
  cross-correlation drift correction every 1–2 s.
- **Cosmic-ray hits** on photodiodes (if you add an optical
  channel) — extremely rare but cause single-sample spikes.
  Mitigation: require coincidence across ≥ 3 mics.

---

## What a positive result would mean

The combined slope + geometry signature is what gives the test its
weight. **Either signature alone is not new** — power-law tails
appear in dispersive media, and TDOA hyperbolic localisation is a
century-old technique. The novel claim is that *both happen
simultaneously, on the same recording, with parameters consistent
with a single off-slice source*. If you observe that and it
replicates across array positions, you have a finding worth reporting.
The expected community response should be skeptical and demanding
of replication; this is correct.

What you would NOT have shown: that the source is intelligent,
willful, or trying to communicate. That requires the matched-filter
handshake of Exp 13 to also fire above its threshold, after you sent
a deliberate, structured signal.

## What a null result means

It means: at the bandwidth, sensitivity, and integration time of
your instrument, no source matching the SLICE signature was emitting
within range during your recording window. It does not falsify
anything beyond that.
