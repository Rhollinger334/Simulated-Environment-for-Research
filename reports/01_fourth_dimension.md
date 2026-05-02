# Research Log 01 — The Fourth Dimension

**Date:** 2026-05-02
**Environment:** sim_env v0.1
**Mode:** Discovery-driven. Each experiment was designed in response to
findings of the previous one — none were planned ahead of time except the
first.

All numerical work uses real CODATA 2018 / 2019-SI constants
(`sim_env/core/constants.py`). No mock data was introduced anywhere.

---

## Scope

"Fourth dimension" can mean two distinct things in mainstream physics
and mathematics:

1. **A fourth spatial dimension** — Euclidean R⁴, the natural setting
   for higher-dimensional geometry.
2. **Time as the fourth dimension** — Minkowski spacetime R^{1,3}, the
   geometry of Special Relativity.

We attacked both.

---

## What was built (foundation)

| Module | Purpose |
| --- | --- |
| `sim_env/core/constants.py` | Real fundamental constants (CODATA 2018 + post-2019 SI exacts). |
| `sim_env/notation/symbols.py` | New mathematical notation introduced by this environment, with rigorous definitions. |
| `sim_env/geometry/polytopes_4d.py` | Exact vertex coordinates of the 6 regular convex 4-polytopes. |
| `sim_env/geometry/rotations_4d.py` | SO(4) toolbox: planar rotations, double rotations, quaternion-pair construction. |
| `sim_env/physics/nd_physics.py` | n-dimensional balls/spheres, Gauss-law potentials, hydrogenic energies in D dim. |
| `sim_env/physics/minkowski.py` | Lorentz boosts, proper time, invariant intervals. |

### New notation introduced

**Isoclinic Defect of an SO(4) rotation.**
For any R ∈ SO(4) decomposed into invariant 2-planes with rotation
angles (θ₁, θ₂),
> **𝔇(R) := |θ₁ − θ₂|** ∈ [0, π].

R is isoclinic ↔ 𝔇(R) = 0; R is "simple" (3D-like) ↔ min(|θ₁|,|θ₂|) = 0.
Implemented in `sim_env/notation/symbols.py` as `isoclinic_defect()`.
**Motivation:** no commonly used scalar in standard SO(4) literature
cleanly captures "how far a 4D rotation is from being isoclinic" — yet
this number gates a physical property (constant point-speed under the
rotation) that has no 3D analog.

---

## Findings

### Exp 01 — All six regular 4-polytopes constructed and verified

| Polytope | Verts | Edges | Circumrad | Edge len |
|---|---|---|---|---|
| 5-cell `{3,3,3}` | 5 | 10 | 0.6325 | 1.0000 |
| 8-cell (tesseract) `{4,3,3}` | 16 | 32 | 1.0000 | 1.0000 |
| 16-cell `{3,3,4}` | 8 | 24 | 1.0000 | √2 |
| **24-cell `{3,4,3}`** | **24** | **96** | **√2** | **√2** |
| 600-cell `{3,3,5}` | 120 | 720 | 1.0000 | 1/φ |
| 120-cell `{5,3,3}` | 600 | 1200 | 2√2 | ≈0.764 |

All counts match Coxeter (1973) Tables I–V. The **24-cell has no 3D
analog** — it is the unique self-dual regular polytope (besides the
simplex) and tiles R⁴ as a regular honeycomb (impossible in R³).

### Exp 02 — Double rotations & isoclinic defect

| R | (θ₁, θ₂) | 𝔇(R) | Point-displacement spread on S³ |
|---|---|---|---|
| Generic | (0.7, 1.3) | 0.600 | range [0.69, 1.21], σ = 0.150 |
| Simple | (0.7, 0)  | 0.700 | range [0.01, 0.69], σ = 0.161 |
| Isoclinic | (0.9, 0.9) | 0.000 | **σ = 7.5 × 10⁻¹⁷** |

The constant point-displacement of the isoclinic case (σ ~ machine
precision) is the unique-to-4D phenomenon. The SU(2)×SU(2) → SO(4)
double cover was confirmed by reconstructing R from a quaternion pair
to ‖RᵀR − I‖ = 3.7 × 10⁻¹⁶.

### Exp 03 → Exp 05 → Exp 06 — A surprise about 4D atoms

The natural 4D Coulomb-from-Gauss potential is V = −α/r². Its
classical fall-to-center threshold for L = ℏ is k_c = ℏ²/(2 mₑ).
Estimating the 4D coupling as k₄ = (e²/4πε₀)·a₀ gave the suspiciously
clean numerical result `k₄/k_c = 2.000`.

**Symbolic check (Exp 05) revealed it is exact**, not numerical luck.
Substituting the *definition* of the Bohr radius a₀ = 4πε₀ℏ²/(mₑe²):

> **k₄ = e²a₀/(4πε₀) ≡ ℏ²/mₑ**, so **k₄/k_c ≡ 2 identically**, free of
> all CODATA values.

That is, *any* dimensionally correct 4D Coulomb coupling built from
(e, ε₀, ℏ, mₑ) lands at exactly twice the classical collapse threshold.

**Self-correction of the quantum threshold.** I had originally quoted
α_c(D, l=0) = (D−2)²/4 (a convention error). Re-deriving cleanly with
the substitution u(r) = r^{(D−1)/2} ψ(r) and applying the 1-D Calogero
critical coefficient β_c = 1/8:

> **α_c(D, l=0) = (D−2)² / 8**

so in 4D, **α_c = 1/2** — and the natural Bohr-built coupling α = 1
again exceeds it by exactly factor 2. Classical and quantum critical
points are **simultaneously violated by the same factor**.

**Numerical confirmation (Exp 06).** Discretized the radial 4-D
Schrödinger equation and tracked the ground-state energy as the inner
cutoff r_min was driven from 10⁻² to 10⁻⁶:

| α | r_min=10⁻² | 10⁻³ | 10⁻⁴ | 10⁻⁵ | 10⁻⁶ |
|---|---|---|---|---|---|
| 0.30 | +8.65e-4 | +8.65e-4 | +8.65e-4 | +8.65e-4 | +8.65e-4 |
| 0.49 | +5.56e-4 | +5.48e-4 | +5.47e-4 | +5.46e-4 | +5.46e-4 |
| **0.50** | **+5.25e-4** | **+5.13e-4** | **+5.10e-4** | **+5.10e-4** | **+5.10e-4** |
| 0.55 | +2.11e-4 | −2.78e-4 | −5.69e-4 | −6.11e-4 | −6.16e-4 |
| 0.70 | −3.81e-1 | −5.07 | −7.62 | −7.96 | −7.99 |
| 1.00 | −19.0 | −156 | −203 | −209 | −209 |

The collapse for α > 1/2 is unambiguous. **A hydrogen atom cannot
exist in 4D space.** This is well-known qualitatively (Ehrenfest 1917,
Tegmark 1997), but the *factor-of-2 alignment* between the classical
and quantum threshold violations — and the fact that it is a
constants-independent algebraic identity — is, as far as I can tell, a
clean way to state the result that I have not seen made explicit in
the literature I'm aware of. (Worth a literature search next session.)

### Exp 04 — Time as the 4th dimension

All Lorentz boosts up to β = 0.999999 preserved the Minkowski metric
to ‖·‖ < 4 × 10⁻¹¹. Time-dilation predictions for real spacecraft and
particle accelerators (ISS, GPS, Voyager 1, LHC) computed exactly.

| Trip | β | Earth time | Ship time |
|---|---|---|---|
| Proxima Centauri (4.247 ly) | 0.99 | 4.29 yr | 0.61 yr |
| Proxima Centauri | 0.999 | 4.25 yr | 0.19 yr |

Twin paradox at β = 0.8 over T = 20 yr coordinate time:
τ_A = 20.000 yr, τ_B = 12.000 yr, ratio = 0.6000 = 1/γ exactly.

### Exp 07 — The Hopf fibration

A uniquely-4D structure: the only continuous map S³ → S² with
non-trivial Hopf invariant — provably impossible from S^{n−1} to S^k
except in the Adams dimensions (1, 2, 4, 8).

| Test | Result |
|---|---|
| h(S³) ⊆ S² | radius range [1.0000000000, 1.0000000000] over 2000 random pts |
| Linking of two distinct fibers (generic) | exactly +1 to 4 decimals |
| Left-isoclinic SO(4) preserves each fiber | image-spread 2.78 × 10⁻¹⁵, S²-displacement 0.000000 |

The third test confirms the SU(2)_L × SU(2)_R structure of SO(4):
the *left* factor moves points along Hopf fibers (preserving them
setwise), the *right* factor permutes the fibers. This is the
algebraic shadow of Hopf's geometric theorem.

---

## Open questions raised (queue for next sessions)

1. Is the "factor-of-2 simultaneous violation" of classical and quantum
   thresholds in 4D a known result? Literature search needed.
2. The marginal case α = 1/2 in 4D is the conformal-quantum-mechanics
   regime (de Alfaro–Fubini–Furlan 1976). The numerical drift in Exp 06
   row α=0.50 was small; with larger r_max we should see the
   logarithmic dependence resolved. Repeat with adaptive grid.
3. The S-pole / equator linking-number test in Exp 07 returned 0 — a
   numerical artifact from a coordinate singularity in my fiber
   parameterization plus stereographic projection. Replace with
   intrinsic-S³ linking integral to avoid both.
4. Can the isoclinic-defect 𝔇(R) be promoted to a Riemannian distance
   on the maximal-torus quotient SO(4)/T? If so, what is the geodesic
   structure?
