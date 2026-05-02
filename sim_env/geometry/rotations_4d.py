"""
SO(4) -- the rotation group in four dimensions.

Key fact distinguishing 4D from all other dimensions:
  SO(4) has rank 2 (Cartan rank), so a generic rotation has TWO
  independent invariant 2-planes with their own rotation angles.
  No 3D analog exists. SO(4) is double-covered by SU(2) x SU(2),
  i.e. by *pairs* of unit quaternions acting as (q_L, q_R) -> q_L x q_R.
"""

import numpy as np


def planar_rotation(theta, axis_a, axis_b, n=4):
    """Rotation in the (axis_a, axis_b)-plane through angle theta. Identity
    on the orthogonal complement."""
    R = np.eye(n)
    c, s = np.cos(theta), np.sin(theta)
    R[axis_a, axis_a] =  c
    R[axis_b, axis_b] =  c
    R[axis_a, axis_b] = -s
    R[axis_b, axis_a] =  s
    return R


def double_rotation(theta1, theta2):
    """Generic SO(4) element in canonical form: rotate (e0,e1)-plane by
    theta1 and (e2,e3)-plane by theta2 simultaneously.

    theta1 == theta2  ->  isoclinic (left-isoclinic if same sign)
    theta2 == 0       ->  simple rotation (single invariant plane)
    """
    R1 = planar_rotation(theta1, 0, 1)
    R2 = planar_rotation(theta2, 2, 3)
    return R1 @ R2


def quaternion_to_left_iso(q):
    """Left-isoclinic SO(4) matrix corresponding to quaternion q = (w,x,y,z).
    Action on a 4-vector v (interpreted as quaternion) is q*v."""
    w, x, y, z = q
    return np.array([
        [w, -x, -y, -z],
        [x,  w, -z,  y],
        [y,  z,  w, -x],
        [z, -y,  x,  w],
    ])


def quaternion_to_right_iso(q):
    """Right-isoclinic SO(4) matrix: action v -> v*q_conjugate? Standard
    convention: right multiplication v*q (with appropriate quaternion
    embedding)."""
    w, x, y, z = q
    return np.array([
        [w, -x, -y, -z],
        [x,  w,  z, -y],
        [y, -z,  w,  x],
        [z,  y, -x,  w],
    ])


def so4_from_quaternion_pair(qL, qR):
    """Every R in SO(4) can be written R(v) = qL * v * qR (quaternion
    product, v identified with a quaternion). Returns the 4x4 matrix."""
    L = quaternion_to_left_iso(qL)
    R = quaternion_to_right_iso(qR)
    return L @ R
