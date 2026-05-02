"""
Visualisation utilities -- write self-contained HTML files that the
user can open in any browser to interactively inspect 4D structures.

Plotly is the only dependency. All exports are single-file HTML
(no server, no external assets).
"""

import os
import numpy as np
import plotly.graph_objects as go


def write_html(fig: go.Figure, name: str, out_dir: str = "viz") -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name + ".html")
    fig.write_html(path, include_plotlyjs="cdn", full_html=True)
    return path


def project_R4_to_R3_stereographic(p4: np.ndarray,
                                    pole: np.ndarray = None) -> np.ndarray:
    """Stereographic projection of S^3 in R^4 to R^3 from a chosen pole."""
    if pole is None:
        pole = np.array([0.0, 0.0, 0.0, 1.0])
    p = p4 - pole
    # project onto the hyperplane perpendicular to `pole` through origin,
    # via the line from pole to p
    denom = 1.0 - p4 @ pole
    return (p4[:, :3] / denom[:, None]) if pole[3] == 1.0 else \
           (p4 - pole[None, :] * (p4 @ pole)[:, None] /
            (pole @ pole))[:, :3]
