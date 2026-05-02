# Simulated Environment for Research

A theoretical-science research environment. Conducts rigorous *thought
experiments* using established physics, mathematics, and chemistry —
real constants (CODATA 2018 / 2019 SI), real derivations, real
numerical simulation. **No mock data, ever.**

When real values are unknown for a quantity, the environment says so
and reasons from first principles, marking confidence levels.

## Layout

```
sim_env/
  core/         fundamental constants, units
  notation/     extended math notation (custom symbols defined here)
  geometry/     polytopes, group representations, fibrations
  physics/      n-D physics, Minkowski spacetime
  experiments/  numbered, discovery-driven experiment scripts
reports/        research logs (markdown)
```

## Running

```bash
pip install numpy scipy sympy mpmath
python -m sim_env.experiments.exp01_regular_4polytopes
python -m sim_env.experiments.exp02_so4_double_rotation
python -m sim_env.experiments.exp03_atom_stability_4d
python -m sim_env.experiments.exp04_minkowski
python -m sim_env.experiments.exp05_natural_coupling
python -m sim_env.experiments.exp06_marginal_atom
python -m sim_env.experiments.exp07_hopf
python -m sim_env.experiments.exp08_seeing_slices
python -m sim_env.experiments.exp09_hearing_4d
python -m sim_env.experiments.exp10_chirality_flip_4d
python -m sim_env.experiments.exp11_unknot_in_4d
python -m sim_env.experiments.exp12_slice_detector
python -m sim_env.experiments.exp13_communication_protocol
python -m sim_env.experiments.exp14_viz_hopf
python -m sim_env.experiments.exp15_24cell_quaternions
python -m sim_env.experiments.exp16_kissing_24cell
python -m sim_env.experiments.exp17_E8_lattice
python -m sim_env.experiments.exp18_viz_24cell
```

## Visualisations

Open in any browser (no server needed):
- `viz/hopf_fibration.html` — interactive Hopf fibration
- `viz/tesseract_slice.html` — slider-animated tesseract cross-sections
- `viz/24cell_quaternions.html` — the 24-cell coloured by binary-tetrahedral-group element order

## Standing instructions

See [`docs/STANDING_INSTRUCTIONS.md`](docs/STANDING_INSTRUCTIONS.md) for
the persistent rules of engagement and the prompt patterns that produce
the highest-throughput sessions. [`docs/QUESTIONS.md`](docs/QUESTIONS.md)
collects ambiguous decisions for batch resolution.

## Project SLICE

A buildable cheap (~$50) acoustic detector for 4D-source signatures.
See [`docs/PROJECT_SLICE.md`](docs/PROJECT_SLICE.md) for the build
manual and operating procedure.

## Research logs

- [`reports/01_fourth_dimension.md`](reports/01_fourth_dimension.md)
  — six 4-polytopes, SO(4) double rotations, why 4D atoms are unstable,
  Lorentz boosts & twin paradox, and the Hopf fibration.
- [`reports/02_seeing_hearing_4d.md`](reports/02_seeing_hearing_4d.md)
  — visual & auditory signatures of a 4D entity from a 3D observer's
  perspective, plus chirality flipping and the failure of knots in 4D.
- [`reports/03_project_slice.md`](reports/03_project_slice.md)
  — design, validation, and protocol for the cheap detector apparatus.
- [`reports/04_24cell_E8_exceptional.md`](reports/04_24cell_E8_exceptional.md)
  — the 24-cell as the binary tetrahedral group of unit quaternions,
  K(4)=24 saturation, and E_8 in 8D as the natural sequel.
