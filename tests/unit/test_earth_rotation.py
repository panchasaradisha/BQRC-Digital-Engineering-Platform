"""Tests for BQRC Earth-rotation calculations."""

from datetime import UTC, datetime
from math import isclose, pi

import pytest

from bqrc.environment.earth import (
    earth_rotation_angle,
    julian_date_utc,
)


def test_unix_epoch_julian_date() -> None:
    """Unix epoch should correspond to its standard Julian Date."""

    timestamp = datetime(1970, 1, 1, tzinfo=UTC)

    assert julian_date_utc(timestamp) == 2_440_587.5


def test_j2000_julian_date() -> None:
    """J2000 noon UTC should map to Julian Date 2451545.0."""

    timestamp = datetime(
        2000,
        1,
        1,
        12,
        0,
        tzinfo=UTC,
    )

    assert julian_date_utc(timestamp) == 2_451_545.0


def test_naive_datetime_is_rejected() -> None:
    """Earth-rotation calculations require unambiguous timestamps."""

    timestamp = datetime(2032, 7, 18, 10, 0)

    with pytest.raises(ValueError):
        julian_date_utc(timestamp)


def test_earth_rotation_angle_is_normalized() -> None:
    """Earth Rotation Angle should remain within one complete revolution."""

    timestamp = datetime(
        2032,
        7,
        18,
        10,
        0,
        tzinfo=UTC,
    )

    angle = earth_rotation_angle(timestamp)

    assert 0.0 <= angle < 2.0 * pi


def test_earth_rotation_angle_at_j2000() -> None:
    """ERA at the J2000 reference Julian Date should match the formula."""

    timestamp = datetime(
        2000,
        1,
        1,
        12,
        0,
        tzinfo=UTC,
    )

    expected = 2.0 * pi * 0.7790572732640

    assert isclose(
        earth_rotation_angle(timestamp),
        expected,
        rel_tol=1e-12,
    )