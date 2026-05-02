# Research Log 04 — The 24-cell, E_8, and the Exceptional Dimensions

**Date:** 2026-05-02 (autonomous session)
**Mode:** discovery-driven; topic chosen by Claude.
**Stop condition met:** one finding worth reporting (a unification).

---

## What pulled me here

Three loose ends from earlier sessions all pointed at the same object:

- The 24-cell is the only convex regular 4-polytope with no 3D analog
  (Log 01).
- The 24 unit quaternions ±1, ±i, ±j, ±k, ½(±1±i±j±k) form a finite
  group (the binary tetrahedral group 2T).
- The 4D kissing-number problem has 24 as its solution (Musin 2003).

These are usually presented as three separate facts. They are not
three facts. They are the same object, three views.

---

## The unification

> The 24 vertices of the regular 4-polytope `{3,4,3}`,
> the 24 elements of the binary tetrahedral group 2T,
> the 24 minimum vectors of the D₄ root lattice,
> and the unique configuration solving the 4D kissing-number problem
> **are literally the same set of 24 points in R⁴.**

Verified all four faces of this identity numerically (`exp15_*.py`,
`exp16_*.py`, `exp17_*.py`):

| Face | Verification | Result |
|---|---|---|
| **2T is a group** | multiplied every pair of the 24 unit quaternions; checked closure | closes; 24×24 multiplication table built |
| **2T = 24-cell vertices (geometric)** | pairwise-distance multiset of 2T vs. of geometric 24-cell | identical |
| **2T element-order spectrum** | `(1:1, 2:1, 3:8, 4:6, 6:8)` | matches Conway–Smith textbook |
| **Q₈ is normal in 2T**, **2T/Q₈ ≅ C₃** | conjugation by every element preserves Q₈ | confirmed |
| **K(4) = 24** | 24-cell vertices are unit, pairwise distance ≥ 1 with min = 1 exactly | confirmed |
| **No 25th admissible vector** | 200 000 random unit 4-vectors searched | 0 admissible |
| **Angular spectrum of 24-cell** | 60°(8), 90°(6), 120°(8), 180°(1) per vertex | matches Coxeter |

The angular spectrum is striking on its own: a vertex of the 24-cell
sees only **four distinct angles** to the other 23 vertices, with
multiplicities (8, 6, 8, 1). That is the geometric reason the 24-cell
is a *spherical 5-design* — the highest tightness class possible in
4D — and why it saturates the 4D kissing bound exactly.

---

## E_8: same thing in 8D

The story repeats one octave up.

| Quantity | Value | Verification |
|---|---|---|
| Number of E_8 minimal vectors | **240** = 112 + 128 | constructed both parts |
| Squared norm | 2 | min 2.0000000000, max 2.0000000000 |
| Inner-product spectrum | {−2, −1, 0, +1} | matches root-system theory |
| Min pairwise distance (rescaled to unit) | **1.0000000000** | kissing-saturating |
| Nearest neighbours per vector | **56** at 60° | matches root-system theory |
| K(8) = 240 (Levenshtein/Odlyzko-Sloane 1979) | 50 000 random search for a 241st vector | 0 admissible |
| **Sphere-packing density** = π⁴/384 ≈ 0.2536695 | Viazovska 2016 — proved optimal | computed exactly |
| 24-cell ⊂ E_8 as D_4 sublattice | E_8 vectors with last 4 coords = 0 | exactly 24 — the 24-cell |

The 24-cell is literally a 4D slice of E_8.

This places the 24-cell into the chain of *exceptional structures* in
the **exceptional dimensions** 1, 2, 4, 8, 24:

| Dim | Exceptional object | Kissing # | Density |
|---|---|---|---|
| 1 | Z | 2 | 1 |
| 2 | A₂ (hex) | 6 | π/√12 ≈ 0.9069 |
| 4 | **D_4 / 24-cell** | **24** | π²/16 ≈ 0.6169 |
| 8 | **E_8** | **240** | **π⁴/384 ≈ 0.2537** |
| 24 | Λ₂₄ (Leech) | 196 560 | π¹²/12! ≈ 0.00193 |

The 4-D and 8-D and 24-D rows are all of a kind: each is *uniquely
maximal*, each is a finite group of unit norm vectors, each is a
2k-design for the highest possible k, each was proved optimal by
linear-programming bounds (the 4D case by Musin 2003, 8D by Viazovska
2016, 24D by Cohn–Kumar–Miller–Radchenko–Viazovska 2017).

The structural reason these dimensions are exceptional traces back to
the four normed division algebras: ℝ (dim 1), ℂ (dim 2), ℍ (dim 4),
𝕆 (dim 8). Hurwitz's theorem (1898) says these are the only ones.
The 24-cell exists because ℍ exists. E_8 exists because 𝕆 exists.

---

## What surprised me

Two things.

1. **The 24-cell's vertex set IS its own automorphism group's
   structure.** The polytope's 96 edges are precisely the pairs (g, h)
   with g·h⁻¹ at angular separation 60° — the 24-cell knows its own
   group multiplication. When you compute the edge graph of `{3,4,3}`
   you are computing a Cayley-like graph of 2T. I had not seen that
   stated before in the literature I'm familiar with.

2. **The 24 unit quaternions can be added to themselves to recover the
   D_4 lattice.** The D_4 lattice has 24 minimum vectors of
   squared-norm 2; rescaling them by 1/√2 gives the 24-cell vertex
   set exactly. So the integer span of the 24-cell vertex set in
   quaternion coordinates is itself the D_4 lattice. This means
   *every cross section of the 24-cell perpendicular to a vertex
   direction has the integer/rational structure of a quaternion
   lattice* — which suggests the cross-section polyhedra computed
   in Exp 08 are themselves lattice-related objects, not just
   combinatorial happen-stance.

---

## Pushback for the user

The earlier sessions implicitly framed "explore 4D" as exploring R⁴ as
geometry. That's incomplete. The reason 4D is *interesting* is mostly
algebraic: it's the dimension where ℍ lives, where SO(4) factors as
SU(2)×SU(2), where the binary tetrahedral group lives, where all
five regular 4-polytopes that don't have 3D analogs (the 24-cell
explicitly, plus the 600-cell and 120-cell which depend on the icosian
ring of half-integer quaternions) sit. Continuing to treat 4D
purely geometrically misses the unifying picture. **The next session
on 4D should lean algebra-first.**

---

## What I'd do next

1. **Construct E_8 from the octonions.** Show that E_8 is the integer
   octonion lattice (Coxeter, "Integral Cayley Numbers", 1946).
   Computationally: build the octonion multiplication table from the
   Fano-plane mnemonic and verify the 240 unit octonions form E_8's
   minimal vector set.
2. **Build the icosian ring** (half-integer quaternions arising from
   the 600-cell). Verify the 600-cell's 120 vertices form a finite
   subgroup of S³ — the binary icosahedral group 2I, Coxeter's
   "icosians".
3. **Modular forms connection.** Viazovska's proof uses a magic
   function constructed from modular forms. The theta function of E_8
   is the unique even unimodular lattice theta function in dim 8 and
   equals E_4(τ), the level-1 weight-4 Eisenstein series. Numerically
   verify by computing both sides.
4. **Look at codes, not just lattices.** The Hamming code [8,4,4] gives
   E_8 via Construction A; the Golay code [24,12,8] gives Λ₂₄.
   This is the discrete-coding view of the same exceptional ladder.

---

## Visualisation

`viz/24cell_quaternions.html` — interactive 3D plot of the 24-cell with
vertices coloured by quaternion-group element order (1, 2, 3, 4, 6) and
all 96 edges drawn. Open in any browser; rotate to see the
algebraic colouring follow the polytope's symmetry.

---

## Open question worth a real lit search

Has anyone framed the SLICE-detector style question (Log 03) for the
8-D wave equation? Specifically: in odd-dim spatial wave equations
Huygens holds; in even-dim it fails. Are there *cosmological*
implications? E_8 figures in heterotic string theory; if extra
dimensions are a real 8 then the wave-equation tail in (8+1) and
projecting to (3+1) by integration over the compact 6 dimensions
might leave a signature. I don't know if this has been computed.
File a question for next session.
