"""Kinematic attitude profile evaluation."""

from __future__ import annotations

from math import cos, sin, sqrt

from bqrc.frames.attitude import Quaternion
from bqrc.simulation.config import AttitudeProfile


def _multiply(a: Quaternion, b: Quaternion) -> Quaternion:
    """Hamilton product ``a * b`` (scalar-first)."""

    return Quaternion(
        w=a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
        x=a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
        y=a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
        z=a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w,
    )


def attitude_at(profile: AttitudeProfile, elapsed_s: float) -> Quaternion:
    """Body-to-NED quaternion at an elapsed time.

    Spinning composes the initial attitude with a rotation about a
    body-fixed axis: ``q(t) = q0 * q_spin(t)``.
    """

    q0 = Quaternion(*profile.initial_body_to_ned)

    if profile.rate_rad_s == 0.0:
        return q0

    ax, ay, az = profile.rate_axis_body
    norm = sqrt(ax * ax + ay * ay + az * az)
    half = 0.5 * profile.rate_rad_s * elapsed_s
    s = sin(half) / norm

    spin = Quaternion(w=cos(half), x=ax * s, y=ay * s, z=az * s)

    return _multiply(q0, spin)
