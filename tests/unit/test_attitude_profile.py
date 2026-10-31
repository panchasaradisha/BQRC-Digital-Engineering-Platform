"""Tests for kinematic attitude profiles."""

from math import cos, pi, radians, sin

import pytest

from bqrc.simulation.attitude import attitude_at
from bqrc.simulation.config import AttitudeProfile


def test_fixed_profile_is_time_independent() -> None:
    profile = AttitudeProfile(initial_body_to_ned=(0.9, 0.1, 0.2, 0.3))

    assert attitude_at(profile, 0.0) == attitude_at(profile, 1234.0)


def test_spin_about_z_rotates_x_axis() -> None:
    profile = AttitudeProfile(rate_axis_body=(0, 0, 1), rate_rad_s=pi / 2)

    x, y, z = attitude_at(profile, 1.0).rotate_components((1.0, 0.0, 0.0))

    assert (x, y, z) == pytest.approx((cos(pi / 2), sin(pi / 2), 0.0), abs=1e-12)


def test_spin_about_a_vector_leaves_it_unchanged() -> None:
    axis = (1.0, 2.0, 2.0)
    profile = AttitudeProfile(rate_axis_body=axis, rate_rad_s=radians(7.0))

    rotated = attitude_at(profile, 41.0).rotate_components(axis)

    assert rotated == pytest.approx(axis, abs=1e-12)


def test_initial_attitude_applied_after_spin() -> None:
    # q0: 90 deg about z. Spin 90 deg about body x. Body y -> after spin -> z, then q0 keeps z.
    q0 = (cos(pi / 4), 0.0, 0.0, sin(pi / 4))
    profile = AttitudeProfile(
        initial_body_to_ned=q0, rate_axis_body=(1, 0, 0), rate_rad_s=pi / 2
    )

    out = attitude_at(profile, 1.0).rotate_components((0.0, 1.0, 0.0))

    assert out == pytest.approx((0.0, 0.0, 1.0), abs=1e-12)


def test_zero_quaternion_rejected() -> None:
    with pytest.raises(ValueError):
        AttitudeProfile(initial_body_to_ned=(0, 0, 0, 0))
