"""Tests for Earth constants used by BQRC."""

from math import isclose

from bqrc.environment.earth import (
    WGS84_FIRST_ECCENTRICITY_SQUARED,
    WGS84_FLATTENING,
    WGS84_SEMI_MAJOR_AXIS_M,
    WGS84_SEMI_MINOR_AXIS_M,
)


def test_wgs84_flattening_is_physically_valid() -> None:
    """WGS-84 flattening should represent an oblate ellipsoid."""

    assert 0.0 < WGS84_FLATTENING < 1.0


def test_wgs84_polar_axis_is_smaller_than_equatorial_axis() -> None:
    """Earth's WGS-84 polar semi-axis should be smaller than its equatorial one."""

    assert WGS84_SEMI_MINOR_AXIS_M < WGS84_SEMI_MAJOR_AXIS_M


def test_wgs84_derived_semi_minor_axis() -> None:
    """Derived WGS-84 semi-minor axis should match its expected value."""

    assert isclose(
        WGS84_SEMI_MINOR_AXIS_M,
        6_356_752.314245,
        abs_tol=1e-6,
    )


def test_wgs84_first_eccentricity_squared() -> None:
    """Derived first eccentricity squared should match WGS-84."""

    assert isclose(
        WGS84_FIRST_ECCENTRICITY_SQUARED,
        6.69437999014e-3,
        rel_tol=1e-12,
    )