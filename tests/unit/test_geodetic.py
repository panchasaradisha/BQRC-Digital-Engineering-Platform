"""Tests for BQRC WGS-84 geodetic conversion."""

from math import isclose

import pytest

from bqrc.environment.earth import (
    WGS84_SEMI_MAJOR_AXIS_M,
    WGS84_SEMI_MINOR_AXIS_M,
    GeodeticPosition,
    ecef_to_geodetic,
    geodetic_to_ecef,
)
from bqrc.frames import ReferenceFrame, Vector3


def test_equator_prime_meridian_surface() -> None:
    """Equatorial WGS-84 surface point should map to zero coordinates."""

    position = Vector3(
        x=WGS84_SEMI_MAJOR_AXIS_M,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

    geodetic = ecef_to_geodetic(position)

    assert isclose(geodetic.latitude_deg, 0.0, abs_tol=1e-12)
    assert isclose(geodetic.longitude_deg, 0.0, abs_tol=1e-12)
    assert isclose(geodetic.altitude_m, 0.0, abs_tol=1e-6)


def test_equator_ninety_degrees_east() -> None:
    """Positive ECEF Y-axis should correspond to 90 degrees east."""

    position = Vector3(
        x=0.0,
        y=WGS84_SEMI_MAJOR_AXIS_M,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

    geodetic = ecef_to_geodetic(position)

    assert isclose(geodetic.latitude_deg, 0.0, abs_tol=1e-12)
    assert isclose(geodetic.longitude_deg, 90.0, abs_tol=1e-12)
    assert isclose(geodetic.altitude_m, 0.0, abs_tol=1e-6)


def test_north_pole_surface() -> None:
    """WGS-84 north pole should map to +90 degree latitude."""

    position = Vector3(
        x=0.0,
        y=0.0,
        z=WGS84_SEMI_MINOR_AXIS_M,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

    geodetic = ecef_to_geodetic(position)

    assert isclose(geodetic.latitude_deg, 90.0, abs_tol=1e-12)
    assert isclose(geodetic.altitude_m, 0.0, abs_tol=1e-6)


def test_equatorial_altitude() -> None:
    """Radial displacement at the equator should produce expected altitude."""

    expected_altitude = 400_000.0

    position = Vector3(
        x=WGS84_SEMI_MAJOR_AXIS_M + expected_altitude,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

    geodetic = ecef_to_geodetic(position)

    assert isclose(
        geodetic.altitude_m,
        expected_altitude,
        abs_tol=1e-6,
    )


def test_wrong_reference_frame_is_rejected() -> None:
    """Geodetic conversion must not accept an ECI vector."""

    position = Vector3(
        x=WGS84_SEMI_MAJOR_AXIS_M,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    with pytest.raises(ValueError):
        ecef_to_geodetic(position)


def test_wrong_unit_is_rejected() -> None:
    """Geodetic conversion currently requires metres."""

    position = Vector3(
        x=6378.137,
        y=0.0,
        z=0.0,
        unit="km",
        frame=ReferenceFrame.ECEF,
    )

    with pytest.raises(ValueError):
        ecef_to_geodetic(position)


def test_earth_centre_is_rejected() -> None:
    """Geodetic coordinates are undefined at Earth's exact centre."""

    position = Vector3(
        x=0.0,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

    with pytest.raises(ValueError):
        ecef_to_geodetic(position)

def test_geodetic_equator_to_ecef() -> None:
    """Zero latitude, longitude and altitude should lie on +ECEF X."""

    geodetic = GeodeticPosition(
        latitude_deg=0.0,
        longitude_deg=0.0,
        altitude_m=0.0,
    )

    position = geodetic_to_ecef(geodetic)

    assert isclose(
        position.x,
        WGS84_SEMI_MAJOR_AXIS_M,
        abs_tol=1e-6,
    )
    assert isclose(position.y, 0.0, abs_tol=1e-6)
    assert isclose(position.z, 0.0, abs_tol=1e-6)

    assert position.frame == ReferenceFrame.ECEF
    assert position.unit == "m"


def test_geodetic_north_pole_to_ecef() -> None:
    """North-pole geodetic coordinates should map to the polar axis."""

    geodetic = GeodeticPosition(
        latitude_deg=90.0,
        longitude_deg=0.0,
        altitude_m=0.0,
    )

    position = geodetic_to_ecef(geodetic)

    assert isclose(position.x, 0.0, abs_tol=1e-6)
    assert isclose(position.y, 0.0, abs_tol=1e-6)

    assert isclose(
        position.z,
        WGS84_SEMI_MINOR_AXIS_M,
        abs_tol=1e-6,
    )


def test_geodetic_round_trip_mid_latitude() -> None:
    """An arbitrary Earth location should survive a coordinate round trip."""

    original = GeodeticPosition(
        latitude_deg=23.0225,
        longitude_deg=72.5714,
        altitude_m=53.0,
    )

    ecef = geodetic_to_ecef(original)
    recovered = ecef_to_geodetic(ecef)

    assert isclose(
        recovered.latitude_deg,
        original.latitude_deg,
        abs_tol=1e-9,
    )

    assert isclose(
        recovered.longitude_deg,
        original.longitude_deg,
        abs_tol=1e-9,
    )

    assert isclose(
        recovered.altitude_m,
        original.altitude_m,
        abs_tol=1e-5,
    )


def test_geodetic_round_trip_orbital_altitude() -> None:
    """The conversion should remain stable at representative orbital altitude."""

    original = GeodeticPosition(
        latitude_deg=-35.0,
        longitude_deg=120.0,
        altitude_m=400_000.0,
    )

    ecef = geodetic_to_ecef(original)
    recovered = ecef_to_geodetic(ecef)

    assert isclose(
        recovered.latitude_deg,
        original.latitude_deg,
        abs_tol=1e-9,
    )

    assert isclose(
        recovered.longitude_deg,
        original.longitude_deg,
        abs_tol=1e-9,
    )

    assert isclose(
        recovered.altitude_m,
        original.altitude_m,
        abs_tol=1e-5,
    )


def test_geodetic_position_rejects_invalid_latitude() -> None:
    """Latitude outside the physical range should be rejected."""

    with pytest.raises(ValueError):
        GeodeticPosition(
            latitude_deg=91.0,
            longitude_deg=0.0,
            altitude_m=0.0,
        )


def test_geodetic_position_rejects_invalid_longitude() -> None:
    """Longitude outside the normalized range should be rejected."""

    with pytest.raises(ValueError):
        GeodeticPosition(
            latitude_deg=0.0,
            longitude_deg=181.0,
            altitude_m=0.0,
        )