"""Tests for the BQRC two-body gravity model."""

from math import isclose

import pytest

from bqrc.environment.earth import EARTH_GRAVITATIONAL_PARAMETER_M3_S2
from bqrc.environment.orbit import two_body_acceleration
from bqrc.frames import ReferenceFrame, Vector3


def test_gravity_points_toward_earth() -> None:
    """Gravity should oppose an outward positive x position."""
    position = Vector3(
        x=6_771_000.0,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    acceleration = two_body_acceleration(position)

    assert acceleration.x < 0.0
    assert acceleration.y == 0.0
    assert acceleration.z == 0.0


def test_gravity_magnitude_matches_two_body_equation() -> None:
    """Acceleration magnitude should equal mu divided by radius squared."""
    radius = 6_771_000.0

    position = Vector3(
        x=radius,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    acceleration = two_body_acceleration(position)

    expected = EARTH_GRAVITATIONAL_PARAMETER_M3_S2 / radius**2

    assert isclose(
        acceleration.magnitude,
        expected,
        rel_tol=1e-12,
    )


def test_gravity_preserves_reference_frame() -> None:
    """Acceleration should be expressed in the input ECI frame."""
    position = Vector3(
        x=6_771_000.0,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    acceleration = two_body_acceleration(position)

    assert acceleration.frame == ReferenceFrame.ECI
    assert acceleration.unit == "m/s^2"


def test_zero_position_is_rejected() -> None:
    """Gravity is undefined at zero radius in the point-mass model."""
    position = Vector3(
        x=0.0,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    with pytest.raises(ValueError):
        two_body_acceleration(position)


def test_wrong_position_unit_is_rejected() -> None:
    """The V1 gravity model requires SI position units."""
    position = Vector3(
        x=6771.0,
        y=0.0,
        z=0.0,
        unit="km",
        frame=ReferenceFrame.ECI,
    )

    with pytest.raises(ValueError):
        two_body_acceleration(position)


def test_non_eci_position_is_rejected() -> None:
    """The V1 gravity model should not silently accept another frame."""
    position = Vector3(
        x=6_771_000.0,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

    with pytest.raises(ValueError):
        two_body_acceleration(position)