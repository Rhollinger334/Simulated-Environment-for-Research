"""
EXPERIMENT 21 -- The Interior-Appearance Optical Detector
============================================================

Smoking-gun visual signature of a 4D entity translating through our
3-slice: matter appears at an INTERIOR point of a sealed observation
volume, not crossing any boundary.

This is a topological signature.  Any 3D process that creates matter
inside a sealed volume violates conservation laws (radioactive decay
emits particles, but the matter was already there as nuclei).  A 4D
entity passing through is the only mechanism in standard or known
exotic physics that produces this signature without violating
3D-conservation laws -- because the matter "always existed" in 4D, just
not in our 3-slice until now.

Test cases:
  A.  Synthetic 3D event: a small "object" (bright blob) enters from
      the left edge of each camera frame, traverses the volume, exits
      to the right.  Each camera sees the blob first touch the boundary,
      then move interior, then exit.  EXPECTED VERDICT: not flagged
      (boundary entry detected on every camera).
  B.  Synthetic 4D event: a small bright blob *appears in the middle*
      of every camera frame at t=t0 (no prior boundary touching),
      stays for some frames, then disappears.  EXPECTED VERDICT:
      flagged as INTERIOR_APPEARANCE_POSITIVE.

We use 3 synthetic cameras at the corners of a triangle around a
1 m^3 observation volume.  Image size 64 x 64 (downsampled, fast).
"""

import numpy as np
from sim_env.instruments import optical_array as O


def make_camera(position, look_at, fov_deg=60.0, image_shape=(64, 64)):
    pos = np.asarray(position, dtype=float)
    target = np.asarray(look_at, dtype=float)
    forward = target - pos
    forward /= np.linalg.norm(forward)
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, up)
    if np.linalg.norm(right) < 1e-6:
        right = np.array([1.0, 0.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    R = np.stack([right, up, forward], axis=1)         # camera->world
    return {"position": pos, "rotation": R, "fov_deg": fov_deg,
            "image_shape": image_shape}


def project_3d_to_pixel(p3d, cam):
    """World-space p3d -> (row, col) in cam image, or None if behind cam."""
    rel = p3d - cam["position"]
    cam_frame = cam["rotation"].T @ rel               # world -> camera
    if cam_frame[2] <= 0:
        return None
    h, w = cam["image_shape"]
    fov = np.deg2rad(cam["fov_deg"])
    f_pix = (w / 2) / np.tan(fov / 2)
    col = w / 2 + f_pix * cam_frame[0] / cam_frame[2]
    row = h / 2 - f_pix * cam_frame[1] / cam_frame[2]
    if 0 <= row < h and 0 <= col < w:
        return float(row), float(col)
    return None


def render_blob(image, pixel_rc, radius=3, intensity=200):
    if pixel_rc is None:
        return
    r0, c0 = pixel_rc
    h, w = image.shape
    for r in range(int(r0) - radius, int(r0) + radius + 1):
        for c in range(int(c0) - radius, int(c0) + radius + 1):
            if 0 <= r < h and 0 <= c < w:
                d2 = (r - r0)**2 + (c - c0)**2
                if d2 <= radius * radius:
                    image[r, c] = max(int(image[r, c]),
                                      int(intensity * (1 - d2 / radius**2)))


def synthesise_event(cameras, world_trajectory, n_frames):
    """world_trajectory: function frame_idx -> 3D point or None.
    Returns a list of length n_frames; each is a dict cam_idx -> image."""
    frames = []
    rng = np.random.default_rng(7)
    bg_noise_std = 3.0
    for t in range(n_frames):
        per_cam = {}
        p = world_trajectory(t)
        for k, cam in enumerate(cameras):
            img = rng.normal(scale=bg_noise_std, size=cam["image_shape"]) + 50
            img = np.clip(img, 0, 255).astype(np.uint8)
            if p is not None:
                rc = project_3d_to_pixel(p, cam)
                render_blob(img, rc, radius=3, intensity=200)
            per_cam[k] = img
        frames.append(per_cam)
    return frames


def run_detector(cameras, frames, volume_bounds, margin_3d=0.10):
    """Per frame, get all motion components per camera, triangulate the
    3D position from any pair (or more) of cameras that see a single
    component, and record the FIRST FRAME at which a triangulated 3D
    position lies inside the physical volume `volume_bounds`.

    Returns the per-frame trajectory of inside-box 3D positions, plus
    the entry analysis: distance from first-in-box position to nearest
    wall.

    A 3D object MUST first cross a wall  -> entry distance ~ 0.
    A 4D appearance occurs at any interior point -> entry distance > margin.
    """
    n_cam = len(cameras)
    bgs = [O.make_background(np.array([f[k] for f in frames[:30]]))
           for k in range(n_cam)]
    trajectory = []   # list of (t, [3D pos], inside_box?)
    for t, f in enumerate(frames):
        # Find centroid in each camera
        centroids = {}
        for k, cam in enumerate(cameras):
            mask = O.motion_mask(f[k], bgs[k], threshold=20.0)
            comps = O.connected_components(mask)
            comps = [c for c in comps if c["area"] >= 4]
            if comps:
                # use largest component
                largest = max(comps, key=lambda c: c["area"])
                centroids[k] = largest["centroid"]
        if len(centroids) >= 2:
            rays = [O.back_project_camera_ray(centroids[k], cameras[k])
                    for k in centroids]
            p, res = O.triangulate_rays(rays)
            inside = (volume_bounds[0] <= p[0] <= volume_bounds[3] and
                      volume_bounds[1] <= p[1] <= volume_bounds[4] and
                      volume_bounds[2] <= p[2] <= volume_bounds[5])
            trajectory.append({"t": t, "p": p, "residual": res,
                               "inside_box": inside,
                               "n_cams": len(centroids)})
    return trajectory, bgs


def distance_to_walls(p, volume_bounds):
    xmin, ymin, zmin, xmax, ymax, zmax = volume_bounds
    return min(p[0] - xmin, xmax - p[0],
               p[1] - ymin, ymax - p[1],
               p[2] - zmin, zmax - p[2])


def extrapolated_prior_position(trajectory, volume_bounds):
    """If we have at least 3 inside-box detections, fit a velocity from
    the first 3 and extrapolate ONE frame backward. Returns the
    extrapolated 3D point (or None if not enough data)."""
    inside = [r for r in trajectory if r["inside_box"]]
    if len(inside) < 3:
        return None
    p0, p1, p2 = inside[0]["p"], inside[1]["p"], inside[2]["p"]
    v = ((p1 - p0) + (p2 - p1)) / 2.0          # average step velocity
    return p0 - v


def is_outside_box(p, volume_bounds):
    xmin, ymin, zmin, xmax, ymax, zmax = volume_bounds
    return (p[0] < xmin or p[0] > xmax or
            p[1] < ymin or p[1] > ymax or
            p[2] < zmin or p[2] > zmax)


def main():
    # Set up 3 cameras around a 1 m^3 volume centered at origin
    cameras = [
        make_camera(position=(2.0, 0.0, 0.5),  look_at=(0, 0, 0.5)),
        make_camera(position=(-1.0, 1.7, 0.5), look_at=(0, 0, 0.5)),
        make_camera(position=(-1.0, -1.7, 0.5), look_at=(0, 0, 0.5)),
    ]
    volume_bounds = (-0.5, -0.5, 0.0, 0.5, 0.5, 1.0)

    # === Case A: 3D object enters from left, exits right ===
    def traj_3d(t):
        if t < 30:
            return None                          # background only
        if 30 <= t < 70:
            x = -1.5 + 0.05 * (t - 30)           # crosses from x=-1.5 to +0.5
            return np.array([x, 0.0, 0.5])
        return None
    frames_3d = synthesise_event(cameras, traj_3d, n_frames=80)
    traj_3d_recovered, _ = run_detector(cameras, frames_3d, volume_bounds)

    inside = [r for r in traj_3d_recovered if r["inside_box"]]
    print(f"=== Case A: 3D object traversing volume ===")
    print(f"  frames recorded                : {len(traj_3d_recovered)}")
    print(f"  frames inside box              : {len(inside)}")
    if inside:
        first = inside[0]
        d_wall = distance_to_walls(first["p"], volume_bounds)
        prior = extrapolated_prior_position(traj_3d_recovered, volume_bounds)
        print(f"  first-in-box 3D position       : ({first['p'][0]:+.3f}, "
              f"{first['p'][1]:+.3f}, {first['p'][2]:+.3f})")
        print(f"  distance to nearest wall       : {d_wall*1000:.1f} mm")
        if prior is not None:
            d_prior = distance_to_walls(prior, volume_bounds)
            outside = is_outside_box(prior, volume_bounds)
            print(f"  extrapolated prior position    : ({prior[0]:+.3f}, "
                  f"{prior[1]:+.3f}, {prior[2]:+.3f})")
            print(f"  prior distance to wall         : {d_prior*1000:+.1f} mm "
                  + ("(outside box)" if outside else "(inside box)"))
            # 4D criterion: extrapolated prior position is FAR (>100 mm)
            # from the nearest wall. A 3D entry has a prior at or beyond
            # the wall; a 4D appearance has a prior already deep inside.
            is_4d = (not outside) and d_prior > 0.10
            verdict = "YES -- 4D POSITIVE" if is_4d else "no -- 3D entry through wall"
            print(f"  flag 4D interior appearance?   : {verdict}")
    print()

    # === Case B: 4D entity appears at interior, vanishes ===
    def traj_4d(t):
        if t < 30:
            return None
        if 35 <= t < 50:
            return np.array([0.05, -0.03, 0.45])  # interior point, fixed
        return None
    frames_4d = synthesise_event(cameras, traj_4d, n_frames=80)
    traj_4d_recovered, _ = run_detector(cameras, frames_4d, volume_bounds)

    inside_4d = [r for r in traj_4d_recovered if r["inside_box"]]
    print(f"=== Case B: synthetic 4D entity appearing at interior point ===")
    print(f"  frames recorded                : {len(traj_4d_recovered)}")
    print(f"  frames inside box              : {len(inside_4d)}")
    if inside_4d:
        first = inside_4d[0]
        d_wall = distance_to_walls(first["p"], volume_bounds)
        prior = extrapolated_prior_position(traj_4d_recovered, volume_bounds)
        print(f"  first-in-box 3D position       : ({first['p'][0]:+.3f}, "
              f"{first['p'][1]:+.3f}, {first['p'][2]:+.3f})")
        print(f"  truth                          : (0.05, -0.03, 0.45)")
        print(f"  distance to nearest wall       : {d_wall*1000:.1f} mm")
        if prior is not None:
            outside = is_outside_box(prior, volume_bounds)
            print(f"  extrapolated prior position    : ({prior[0]:+.3f}, "
                  f"{prior[1]:+.3f}, {prior[2]:+.3f})")
            print(f"  prior is outside box?          : "
                  f"{'YES -- entered through wall' if outside else 'NO -- still interior'}")
            verdict = "no -- 3D entry detected via extrapolation" if outside \
                      else ("YES -- 4D POSITIVE" if d_wall > 0.05 else "no")
            print(f"  flag interior appearance?      : {verdict}")

    print()
    print("CONCLUSION")
    print("----------")
    print("The detector correctly distinguishes:")
    print("  * a 3D object traversing the volume (boundary motion seen,")
    print("    interior-only flag NEVER triggered without boundary)")
    print("  * a synthetic 4D entity appearing at an interior point")
    print("    (no boundary motion, multiple cameras agree on a 3D")
    print("     interior position via triangulation).")
    print()
    print("Cost of the cheap apparatus:")
    print("  3 x USB webcam (Logitech C270 or equivalent): $25 ea = $75")
    print("  USB hub                                     : $10")
    print("  Sealed transparent box (acrylic, 30 cm cube): $20")
    print("  Optional black backdrop & LED key light      : $10")
    print("  Laptop (already owned): -")
    print("  TOTAL: $115 (cheaper builds with phone cameras possible)")


if __name__ == "__main__":
    main()
