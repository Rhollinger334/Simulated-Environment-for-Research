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
```

## Research logs

- [`reports/01_fourth_dimension.md`](reports/01_fourth_dimension.md)
  — six 4-polytopes, SO(4) double rotations, why 4D atoms are unstable,
  Lorentz boosts & twin paradox, and the Hopf fibration.
