"""
EXPERIMENT 23 -- Unifying the SLICE detectors via the DSI
============================================================

Until now, our three cheap detectors (acoustic SLICE, optical
interior-appearance, chiral polarimeter) each output their own
verdict in isolation.  The "triple coincidence" intuition has been
qualitative.

This experiment formalises the joint inference:

    DSI = log10  P(observation | 4D source) / P(observation | 3D source)

with channels assumed conditionally independent given the source type
(reasonable: their noise sources -- acoustic, optical, photometric -- are
physically uncoupled).

We compute DSI for several plausible event scenarios:

  Scenario 1:  null observation -- nothing detected on any channel.
  Scenario 2:  marginal acoustic (w_0 = 3 sigma), nothing else.
  Scenario 3:  acoustic confirms but optical and polarimeter null.
  Scenario 4:  triple coincidence: all three fire at "real signal" levels.
  Scenario 5:  triple coincidence with one channel marginal.

The point: the same individual statistics that look "maybe positive"
in isolation become *decisive* (or *decisively null*) when combined
properly.
"""

from sim_env.instruments import dsi


def show(scenario_name, channels):
    print(f"--- {scenario_name} ---")
    for k, v in channels.items():
        print(f"  {k:>12}: {v}")
    result = dsi.compute_dsi(channels)
    print(f"  channel DSIs   :")
    for k, v in result.items():
        if k.endswith("_log10LR"):
            print(f"    {k:>14} = {v:+.3f}")
    print(f"  TOTAL DSI      : {result['DSI']:+.3f}")
    print(f"  odds 4D vs 3D  : {result['odds_4D_to_3D']:+.4e}")
    print(f"  interpretation : {result['interpretation']}")
    print()


def main():
    print("Bayesian Dimensional Signature Index per scenario\n" + "=" * 50 + "\n")

    show("Scenario 1: null observation",
         {"acoustic":   {"w0_significance": 0.5},
          "optical":    {"prior_dist_mm": 3.0, "box_inradius_mm": 300.0},
          "polarimeter":{"z": 1.2}})

    show("Scenario 2: marginal acoustic alone (3 sigma w_0)",
         {"acoustic": {"w0_significance": 3.0}})

    show("Scenario 3: acoustic strong, others null",
         {"acoustic":   {"w0_significance": 5.5},
          "optical":    {"prior_dist_mm": 4.0, "box_inradius_mm": 300.0},
          "polarimeter":{"z": 0.8}})

    show("Scenario 4: triple coincidence at signal levels",
         {"acoustic":   {"w0_significance": 5.0},
          "optical":    {"prior_dist_mm": 250.0, "box_inradius_mm": 300.0},
          "polarimeter":{"z": 50.0}})

    show("Scenario 5: triple coincidence, one channel marginal",
         {"acoustic":   {"w0_significance": 3.5},
          "optical":    {"prior_dist_mm": 200.0, "box_inradius_mm": 300.0},
          "polarimeter":{"z": 25.0}})

    print("KEY OBSERVATIONS")
    print("-----------------")
    print("- Scenario 2 alone (acoustic marginal) is INDETERMINATE -- a")
    print("  single 3-sigma detection in one channel happens at rate ~ 0.3%")
    print("  per observation; not enough to conclude anything.")
    print("- Scenario 3 (acoustic strong, others null) actually argues")
    print("  AGAINST a 4D event, because a real 4D entity should have")
    print("  showed up in the polarimeter and optical channels too.")
    print("  The DSI correctly flips negative.")
    print("- Scenarios 4 and 5 reach DSI levels (10s of orders of magnitude)")
    print("  that no single 3D physics phenomenon can produce by chance.")
    print()
    print("This is the Bayesian formalisation of what triple coincidence")
    print("buys us: the same observation that's marginal on each channel")
    print("becomes overwhelming when joined.")


if __name__ == "__main__":
    main()
