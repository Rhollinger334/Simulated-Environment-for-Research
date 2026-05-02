"""
EXPERIMENT 14 -- Interactive 3D visualisation of the Hopf fibration
====================================================================

Generates a standalone HTML file the user can open in any browser.
Each curve drawn is a Hopf fibre (preimage in S^3 of a single point on
S^2) after stereographic projection to R^3.  Fibres are colour-coded
by their image point on S^2 -- a continuous mapping from S^2 to colour
makes the fibration's structure visible.

Two parallel scenes are written:
  viz/hopf_fibration.html   -- many fibres, colour-by-S^2-image
  viz/tesseract_slice.html  -- 4D tesseract sliced through the main
                                diagonal at varying offsets, animated.
"""

import numpy as np
import plotly.graph_objects as go
from sim_env.experiments.exp07_hopf import hopf_fiber, stereographic_R4_to_R3
from sim_env.geometry.polytopes_4d import tesseract
from sim_env.geometry.slicing import slice_polytope
from sim_env.viz import write_html


def s2_to_color(p):
    """Map a unit-sphere point (a, b, c) to an RGB colour by treating
    (lat, lon) as (hue, saturation)."""
    a, b, c = p
    # azimuthal angle -> hue
    phi = np.arctan2(b, a)              # in [-pi, pi]
    h = (phi / (2 * np.pi) + 0.5)
    s = np.sqrt(1 - c * c)              # 0 at poles, 1 at equator
    v = 0.5 + 0.5 * c                   # poles bright/dark
    # HSV -> RGB
    import colorsys
    r, g, bl = colorsys.hsv_to_rgb(h, max(s, 0.4), max(v, 0.5))
    return f"rgb({int(r*255)},{int(g*255)},{int(bl*255)})"


def hopf_viz():
    # Sample a uniform-ish set of points on S^2 (fibonacci sphere)
    N = 80
    indices = np.arange(N) + 0.5
    phi = np.arccos(1 - 2 * indices / N)
    theta = np.pi * (1 + 5 ** 0.5) * indices
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(phi)
    base_pts = np.stack([x, y, z], axis=1)

    traces = []
    for p in base_pts:
        if p[2] < -0.95:
            continue                                    # avoid singular fibre
        fibre4 = hopf_fiber(p, n_pts=300)
        fibre3 = stereographic_R4_to_R3(fibre4)
        # clip extreme stereographic blow-ups so plot scale stays reasonable
        norms = np.linalg.norm(fibre3, axis=1)
        if norms.max() > 30:
            continue
        col = s2_to_color(p)
        traces.append(go.Scatter3d(
            x=fibre3[:, 0], y=fibre3[:, 1], z=fibre3[:, 2],
            mode="lines",
            line=dict(color=col, width=3),
            name=f"S^2 pt ({p[0]:+.2f},{p[1]:+.2f},{p[2]:+.2f})",
            hovertemplate=f"S^2 image: ({p[0]:+.3f},{p[1]:+.3f},{p[2]:+.3f})"
                           "<extra></extra>",
            showlegend=False,
        ))
    fig = go.Figure(traces)
    fig.update_layout(
        title="Hopf fibration: each circle is a fibre h^-1(p) "
              "in S^3, stereographically projected to R^3. "
              "Colour = position of p on S^2.  Any two distinct fibres "
              "have linking number 1.",
        scene=dict(
            xaxis=dict(range=[-4, 4], title="x"),
            yaxis=dict(range=[-4, 4], title="y"),
            zaxis=dict(range=[-4, 4], title="z"),
            aspectmode="cube",
            bgcolor="black",
        ),
        paper_bgcolor="black",
        font=dict(color="white"),
    )
    path = write_html(fig, "hopf_fibration")
    print(f"Wrote {path}  ({len(traces)} fibres rendered)")


def tesseract_slice_viz():
    cube = tesseract()
    diag = np.array([1, 1, 1, 1]) / 2.0
    offsets = np.linspace(-1.0, 1.0, 21)

    frames = []
    init_pts = None
    for w in offsets:
        pts, vol = slice_polytope(cube, diag, w)
        if len(pts) < 4:
            pts = np.zeros((1, 3))
        scatter = go.Scatter3d(
            x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
            mode="markers",
            marker=dict(size=4, color=f"hsl({int(180*(w+1))},80%,55%)"),
            name=f"w = {w:+.3f},  vol = {vol:.4f}",
        )
        frames.append(go.Frame(data=[scatter],
                               name=f"{w:+.3f}",
                               layout=go.Layout(
                                   title=f"Tesseract sliced perp to "
                                         f"(1,1,1,1)/2 at w = {w:+.3f}"
                                         f"  (3D volume = {vol:.5f})")))
        if init_pts is None:
            init_pts = scatter

    fig = go.Figure(
        data=[init_pts],
        frames=frames,
        layout=go.Layout(
            title="Slicing a tesseract through its main diagonal "
                  "(scrub the slider to translate)",
            scene=dict(
                xaxis=dict(range=[-1, 1]),
                yaxis=dict(range=[-1, 1]),
                zaxis=dict(range=[-1, 1]),
                aspectmode="cube",
            ),
            updatemenus=[dict(type="buttons", showactive=False,
                              buttons=[
                                  dict(label="Play", method="animate",
                                       args=[None, {"frame":{"duration":150}}]),
                                  dict(label="Pause", method="animate",
                                       args=[[None], {"mode":"immediate"}])])],
            sliders=[dict(steps=[dict(method="animate",
                                       args=[[f.name],
                                             {"mode":"immediate",
                                              "frame":{"duration":0}}],
                                       label=f.name) for f in frames])],
        ),
    )
    path = write_html(fig, "tesseract_slice")
    print(f"Wrote {path}  ({len(frames)} frames)")


def main():
    hopf_viz()
    tesseract_slice_viz()


if __name__ == "__main__":
    main()
