"""
Optical "interior appearance" detector for the SLICE family.

Premise.  A sealed transparent observation volume V is monitored by
N webcams.  Any 3D object entering V must cross the boundary partial-V.
A 4D entity translating through our 3-slice can *appear at any
interior point* without crossing the boundary -- this is a topological
signature with NO 3D analog.

Detection algorithm.

  1. Per-camera motion mask: M_k(t, u, v) = 1 iff |frame_k(t) - bg_k| >
     threshold. Background = pre-recorded empty-volume frame averaged
     over many seconds.
  2. For each frame, find the connected components of M_k.
  3. For each component, check whether any of its pixels lie within
     `boundary_pixels` of the image edge.  If YES, the object entered
     through the visible boundary -- a normal 3D event, ignore.
  4. If NO (component lies entirely interior), this is an INTERIOR
     APPEARANCE candidate.  Check coincidence across cameras: at
     least 2 cameras must report an interior component within Delta t,
     with image rays consistent with a single 3D point.

The geometry test then triangulates a 3D position from the 2+ camera
rays. If onset positions across multiple cameras consistently
back-project to a 3D point that is NOT near the volume boundary
(more than `boundary_3d_margin` from any wall), the candidate is
ELEVATED to a positive interior-appearance event.

This is independent of the acoustic SLICE pipeline; can run alongside
for triple-coincidence.

Real implementation note: replace synthetic frames with cv2.VideoCapture
in production.  cv2 is in the cheap pip stack.
"""

import numpy as np


def make_background(frames: np.ndarray) -> np.ndarray:
    """Robust background = median over many frames."""
    return np.median(frames, axis=0)


def motion_mask(frame: np.ndarray, background: np.ndarray,
                threshold: float) -> np.ndarray:
    """Pixel-wise abs difference > threshold."""
    return np.abs(frame.astype(float) - background.astype(float)) > threshold


def connected_components(mask: np.ndarray) -> list:
    """4-connected components.  Returns list of dicts with 'pixels' (Nx2
    array of (row, col)) and 'bbox' (rmin, cmin, rmax, cmax)."""
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    out = []
    for i in range(h):
        for j in range(w):
            if mask[i, j] and not visited[i, j]:
                stack = [(i, j)]
                pixels = []
                while stack:
                    r, c = stack.pop()
                    if (0 <= r < h and 0 <= c < w
                            and mask[r, c] and not visited[r, c]):
                        visited[r, c] = True
                        pixels.append((r, c))
                        stack.extend([(r+1, c), (r-1, c),
                                      (r, c+1), (r, c-1)])
                if pixels:
                    pix = np.array(pixels)
                    out.append({
                        "pixels": pix,
                        "bbox": (pix[:, 0].min(), pix[:, 1].min(),
                                 pix[:, 0].max(), pix[:, 1].max()),
                        "centroid": pix.mean(axis=0),
                        "area": len(pix),
                    })
    return out


def is_interior_component(comp: dict, image_shape: tuple,
                          boundary_pixels: int = 3) -> bool:
    """True if component is fully interior to the image, with margin
    `boundary_pixels` from all edges.  A component touching any edge
    indicates an object that *entered through the boundary*."""
    h, w = image_shape
    rmin, cmin, rmax, cmax = comp["bbox"]
    return (rmin >= boundary_pixels and
            cmin >= boundary_pixels and
            rmax < h - boundary_pixels and
            cmax < w - boundary_pixels)


def back_project_camera_ray(centroid_pixel: tuple, camera_pose: dict) -> tuple:
    """Given (row, col) of a centroid in a camera, return (origin, direction)
    of the 3D ray.

    camera_pose: {"position": (x,y,z), "rotation": 3x3 R, "fov_deg": ...,
                  "image_shape": (h, w)}.
    """
    h, w = camera_pose["image_shape"]
    fov = np.deg2rad(camera_pose["fov_deg"])
    f_pix = (w / 2) / np.tan(fov / 2)            # focal length in pixels
    r, c = centroid_pixel
    # convert to centered camera-frame direction
    dx = (c - w / 2) / f_pix
    dy = -(r - h / 2) / f_pix
    dz = 1.0
    d_cam = np.array([dx, dy, dz])
    d_cam = d_cam / np.linalg.norm(d_cam)
    R = np.asarray(camera_pose["rotation"])
    direction = R @ d_cam
    return np.asarray(camera_pose["position"], dtype=float), direction


def triangulate_rays(rays: list) -> tuple:
    """Least-squares intersection of 3D rays.  Each ray is (origin,
    direction).  Returns (point, residual)."""
    A = np.zeros((3, 3))
    b = np.zeros(3)
    for o, d in rays:
        d = d / np.linalg.norm(d)
        I_minus_ddT = np.eye(3) - np.outer(d, d)
        A += I_minus_ddT
        b += I_minus_ddT @ np.asarray(o)
    p = np.linalg.solve(A, b)
    res = float(np.sqrt(sum(np.linalg.norm(np.cross(p - o, d / np.linalg.norm(d))) ** 2
                            for o, d in rays) / len(rays)))
    return p, res


def event_is_interior_in_3d(p: np.ndarray, volume_bounds: tuple,
                            margin: float) -> bool:
    """Volume_bounds = (xmin, ymin, zmin, xmax, ymax, zmax).
    True if p is more than `margin` from every face."""
    xmin, ymin, zmin, xmax, ymax, zmax = volume_bounds
    return (p[0] >= xmin + margin and p[0] <= xmax - margin and
            p[1] >= ymin + margin and p[1] <= ymax - margin and
            p[2] >= zmin + margin and p[2] <= zmax - margin)
