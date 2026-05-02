"""
EXPERIMENT 18 -- 3D viz of the 24-cell coloured by quaternion order
====================================================================

Generate a single-file interactive HTML showing the 24-cell vertices
in R^3 (projected from R^4), colour-coded by element order in the
binary tetrahedral group 2T:
   order 1 (identity, =1)             1 vertex     yellow
   order 2 (-1)                       1 vertex     black
   order 3 (Hurwitz units, half-int)  8 vertices   green
   order 4 (+-i, +-j, +-k)            6 vertices   red
   order 6 (other Hurwitz units)      8 vertices   blue

This is the VISUAL CORRESPONDENCE: the 24-cell's vertex set as a
group, with edges = adjacency in the polytope (60-degree angular
separation in 4D).
"""

import numpy as np
import plotly.graph_objects as go
from sim_env.geometry import quaternion_groups as Q
from sim_env.viz import write_html


def main():
    G = Q.binary_tetrahedral_group()
    _, table = Q.closure_check(G)
    orders = Q.element_orders(G, table)

    # Project R^4 -> R^3 along a generic direction so no two vertices
    # coincide in the projection.  Use a random 4D rotation (fixed seed)
    # then drop the 4th coordinate.
    rng = np.random.default_rng(1234567)
    A = rng.normal(size=(4, 4))
    B = (A - A.T) / 2.0                                # antisymmetric
    from scipy.linalg import expm
    R = expm(B)                                         # unitary 4D rotation
    G_rot = G @ R.T
    P = G_rot[:, :3]                                    # drop 4th coord
    # Verify no two projected points coincide
    diffs = P[:, None, :] - P[None, :, :]
    d2 = (diffs * diffs).sum(axis=-1)
    np.fill_diagonal(d2, np.inf)
    print(f"projection min pairwise distance: {np.sqrt(d2.min()):.4f}  (>0 OK)")

    color_by_order = {1: "yellow", 2: "black",
                      3: "green",  4: "red", 6: "blue"}

    traces = []
    # vertices, colour-coded
    for order_val, col in color_by_order.items():
        mask = orders == order_val
        if not mask.any():
            continue
        pts = P[mask]
        traces.append(go.Scatter3d(
            x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
            mode="markers",
            marker=dict(size=10, color=col,
                        line=dict(color="white", width=1)),
            name=f"order {order_val} ({mask.sum()} vert)",
            text=[f"q = ({q[0]:+.2f}, {q[1]:+.2f}, {q[2]:+.2f}, {q[3]:+.2f}), "
                  f"order {order_val}" for q in G[mask]],
            hovertemplate="%{text}<extra></extra>",
        ))

    # edges: pairs at angular separation 60 deg (the 24-cell's edge graph)
    dots = G @ G.T
    np.fill_diagonal(dots, 0.0)
    edge_threshold = 0.5 + 1e-6                         # cos 60 deg
    edges = np.argwhere((dots >= 0.5 - 1e-6) & (dots <= edge_threshold))
    edges = edges[edges[:, 0] < edges[:, 1]]
    edge_x, edge_y, edge_z = [], [], []
    for i, j in edges:
        edge_x += [P[i, 0], P[j, 0], None]
        edge_y += [P[i, 1], P[j, 1], None]
        edge_z += [P[i, 2], P[j, 2], None]
    traces.append(go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z, mode="lines",
        line=dict(color="rgba(200,200,200,0.35)", width=1.5),
        name=f"edges ({len(edges)})", showlegend=True,
        hoverinfo="skip",
    ))

    fig = go.Figure(traces)
    fig.update_layout(
        title="The 24-cell as the binary tetrahedral group 2T<br>"
              "<sub>vertices = 24 unit quaternions  ;  "
              f"edges = 96 adjacencies (60 deg separation)  ;  "
              "colour = element order in 2T</sub>",
        scene=dict(
            xaxis=dict(title=""), yaxis=dict(title=""), zaxis=dict(title=""),
            aspectmode="cube", bgcolor="#0a0a0a",
        ),
        paper_bgcolor="#0a0a0a", font=dict(color="white"),
        legend=dict(bgcolor="rgba(0,0,0,0.5)"),
    )
    path = write_html(fig, "24cell_quaternions")
    print(f"Wrote {path}  ({len(edges)} edges, {len(G)} vertices)")


if __name__ == "__main__":
    main()
