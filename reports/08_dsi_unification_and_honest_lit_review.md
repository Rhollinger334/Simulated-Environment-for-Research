# Research Log 08 — Bayesian Dimensional Signature Index, plus an Honest Literature Review

**Date:** 2026-05-02 (autonomous session)
**Goal:** "find something truly groundbreaking."
**Result:** built a useful methodological consolidation (the DSI), and
performed long-overdue literature checks on every "potentially
novel" claim I had previously made. Honest verdict: **most of my
prior claims of novelty don't survive even a basic search.** Only two
specific framings remain plausibly novel, and the genuinely useful
contribution of the entire body of work is the *cheap-tabletop
dimensional detector triad as a coordinated apparatus*, not any
single physical or mathematical result.

---

## Part 1: The DSI

I built `sim_env/instruments/dsi.py` and `exp23_dsi_unification.py`
to formalise the "triple coincidence" intuition that has been
floating around since Logs 02–07. The Bayesian Dimensional Signature
Index combines per-channel detection statistics (acoustic w_0
significance, optical interior-prior distance, polarimeter step
z-score) into a single number:

> DSI = log₁₀ [ P(observation | 4D source) / P(observation | 3D source) ]

with conditionally-independent channel likelihoods, and per-channel
caps at ±10⁶ to reflect irreducible systematic uncertainties (standard
practice in particle physics).

### Five scenario tests

| Scenario | What it represents | DSI | Verdict |
|---|---|---|---|
| 1 | Null observation, all channels quiet | **−11.7** | Strongly favors 3D ✓ |
| 2 | Marginal acoustic alone (3σ w_0) | +0.79 | Inconclusive ✓ |
| 3 | Strong acoustic, others null | **−1.1** | Mild evidence against 4D ✓ |
| 4 | Triple coincidence at signal levels | **+16.3** | Extraordinary evidence |
| 5 | Triple coincidence, one channel marginal | **+7.6** | Very strong evidence |

The genuinely useful behavior is **Scenario 3**. A 5.5σ acoustic
signal would be a "SLICE_POSITIVE" by the legacy single-channel verdict,
but the DSI correctly flips negative because a real 4D entity should
have shown up in the polarimeter and optical channels too. The DSI
is the formalisation of the principle: *an asymmetric detection
across a triad of independent channels argues* against *the 4D
hypothesis, not for it.*

This wasn't expressible cleanly in the per-channel verdict logic.

## Part 2: Honest literature review

I committed earlier to checking the literature before claiming
novelty. I had been failing to do this. Here is what an actual
WebSearch returns on the specific claims I have made across Logs
01–07.

### Claims that are NOT novel

| Claim | Where I'd cited it | Reality |
|---|---|---|
| Hydrogen atom in 4D space is unstable | Log 01, Exp 03/06 | Well-known. Nonexhaustive: Tegmark 1997, plus a 2014 Annals of Physics paper on Hydrogen with one compactified extra dim explicitly addresses the critical-coupling fall-to-center. Multiple textbooks. |
| The 24 vertices of the 24-cell are the binary tetrahedral group | Log 04 | Documented on Wikipedia, nLab, Greg Egan's site, and the n-Category Café. Standard. |
| Huygens principle fails in even spatial dimensions | Logs 02, 03 | Hadamard 1923, M. Riesz 1949. Classical PDE textbook material. |
| Knots are trivial in R⁴ | Log 02 | Whitney 1944, standard codimension argument. |
| Polarimetry can detect chirality changes | Log 07 | Industrial standard since the 19th century. |
| Bayesian combination of detector channels | Log 08 (this session) | Multiple 2014–2024 dark-matter direct-detection papers; standard HEP methodology. |

### Claims that remain plausibly novel (search returned nothing direct)

| Claim | Confidence in novelty | Caveat |
|---|---|---|
| **The specific "factor-of-2 simultaneous violation" algebraic identity** for the natural Bohr-built 4D Coulomb coupling exceeding both the classical fall-to-center threshold AND the quantum α_c = (D−2)²/8 by exactly the same factor of 2 (Log 01) | Low-medium | The qualitative result is in Tegmark; whether the *exact algebraic identity* appears in any paper I can't say without a deeper search. |
| **The 24-cell edge graph is *literally identical to* the Cayley graph of 2T with respect to its 60°-separation generators** (Log 04) | Low-medium | Probably folklore; n-Category Café may discuss but I haven't verified. |
| **The SO(3) rotational invariance test as a smoking-gun for off-slice 4D sources** in tabletop array detection (Log 05) | Medium | Underlying rotational-invariance arguments are common in physics. The specific *application* to TDOA-array discrimination of 4D vs 3D source positions doesn't appear in cheap-tabletop detection literature. |
| **The interior-appearance topological signature as a $115 tabletop 4D detector** (Log 06) | Medium | The topology is elementary. The detector design is plausibly novel as a tabletop apparatus. |
| **Triple-coincidence acoustic + optical + polarimeter as a coordinated tabletop dimensional detector** with explicit cost figures and synthetic validation (Logs 03, 06, 07, 08) | Medium-high | Each individual channel has predecessors; the *coordinated triad with $180 total cost* and shared statistical framework is the contribution. |

### Claims that should be downgraded honestly

I previously implied or wrote that several findings might be "new in the
literature I'm familiar with." That was a meaningless qualifier —
my "literature I'm familiar with" was effectively my training data
at some snapshot date, with no live verification. **Going forward I'll
either run an actual WebSearch or downgrade claims to "I haven't
checked."**

The two findings I am most willing to defend as plausibly novel
contributions of this entire project are:

1. The **interior-appearance detector as a $115 tabletop apparatus
   for 4D-entity detection** — this exists nowhere I could find.
2. The **SO(3) rotational invariance test** as the smoking-gun gate
   for distinguishing off-slice 4D sources from in-3D-space sources
   in array-based detection — also not found.

Even these are framings of standard physics applied to a novel
detection problem, not new physics.

## Part 3: Honest evaluation of "groundbreaking"

I was asked to find something "truly groundbreaking." I did not.

What I delivered this session: a clean Bayesian framework for
combining the three detector channels I had already built; honest
literature checks that downgrade most of my earlier novelty claims;
and a calibrated picture of what about this entire body of work is
actually new (apparatus design for tabletop scale) versus
recapitulation of standard physics (everything mathematical).

**A truly groundbreaking finding in this domain would require either
(a) a real experimental observation, which I cannot perform; or (b)
a new theoretical prediction with a specific observable signature
that hasn't been computed before.** I haven't found (b) and don't
believe I will from a single autonomous session. The best I can
deliver is methodological cleanliness and honest attribution.

## Part 4: What I did wrong this session

I led with "going for the truly ambitious thing — the Bayesian DSI"
and described it as "a unified methodological contribution." That
was overselling. The DSI is just standard multi-experiment Bayesian
inference applied to my specific detector triad. The user said "find
something truly groundbreaking" and I should have responded with
"honestly, no, I can't from a single session — but here's the next
useful build" rather than reaching for a flag I couldn't plant.

This is a useful reminder for me to write into the standing
instructions: **don't oversell the framing of the contribution
just because the prompt asks for greatness.** Match the language
to the actual delivery.

## Part 5: What I'd do next

1. **Build the live-capture and calibration scripts** for the
   interior-appearance detector (Exp 21). That makes it actually
   deployable by the user.
2. **Write a Phyphox-export-to-SLICE adapter** so multi-iPhone
   recordings can be processed without buying any hardware.
3. **Look more deeply at the modular-form / theta-function /
   Viazovska connection** queued in Log 04 — this is one of the
   few places where a numerical computation might surface a
   structural connection that's not in textbooks.
4. **Adopt as standing rule: every claim that includes "novel,"
   "haven't seen," or "first" must be preceded by a WebSearch or
   downgraded.** I'll add this to STANDING_INSTRUCTIONS.md.

Stop condition met: a useful Bayesian framework built, honest
literature audit performed, calibrated novelty assessment recorded.

---

Sources from the literature checks:
- [Hydrogen atom with compactified extra dim](https://www.sciencedirect.com/science/article/abs/pii/S0003491614003558)
- [Binary tetrahedral group](https://en.wikipedia.org/wiki/Binary_tetrahedral_group)
- [24-cell](https://en.wikipedia.org/wiki/24-cell)
- [Bayesian analysis of multiple direct detection experiments](https://arxiv.org/abs/1310.5718)
- [Multi-channel direct detection of light dark matter](https://arxiv.org/abs/1910.08092v3)
