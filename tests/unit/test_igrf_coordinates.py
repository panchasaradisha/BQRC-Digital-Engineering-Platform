"""Unit tests for IGRF coordinate preparation."""

from math import pi

import pytest

from bqrc.environment.earth.geodetic import GeodeticPosition
from bqrc.environment.magnetic.igrf.coordinates import (
    IGRF_REFERENCE_RADIUS_M,
    IGRFSphericalPosition,
    geodetic_to_igrf_spherical,
)


def test_equator_surface_conversion() -> None:
    """Equatorial WGS-84 position should remain geocentrically equatorial."""

    position = GeodeticPosition(
        latitude_deg=0.0,
        longitude_deg=0.0,
        altitude_m=0.0,
    )

    spherical = geodetic_to_igrf_spherical(position)

    assert spherical.geocentric_latitude_deg == pytest.approx(0.0)
    assert spherical.longitude_deg == pytest.approx(0.0)
    assert spherical.radius_m == pytest.approx(
        6_378_137.0,
        abs=1e-6,
    )


def test_north_pole_surface_conversion() -> None:
    """The WGS-84 north pole should map to zero geocentric colatitude."""

    position = GeodeticPosition(
        latitude_deg=90.0,
        longitude_deg=0.0,
        altitude_m=0.0,
    )

    spherical = geodetic_to_igrf_spherical(position)

    assert spherical.geocentric_colatitude_rad == pytest.approx(
        0.0,
        abs=1e-12,
    )

    assert spherical.radius_m == pytest.approx(
        6_356_752.314245,
        abs=1e-3,
    )


def test_midlatitude_geodetic_and_geocentric_latitude_differ() -> None:
    """Ellipsoidal geometry should distinguish latitude definitions."""

    position = GeodeticPosition(
        latitude_deg=45.0,
        longitude_deg=0.0,
        altitude_m=0.0,
    )

    spherical = geodetic_to_igrf_spherical(position)

    assert spherical.geocentric_latitude_deg != pytest.approx(
        45.0,
        abs=1e-3,
    )

    assert spherical.geocentric_latitude_deg == pytest.approx(
        44.8076,
        abs=1e-3,
    )


def test_longitude_is_preserved() -> None:
    """Geodetic and geocentric longitude share the Earth rotation axis."""

    position = GeodeticPosition(
        latitude_deg=20.0,
        longitude_deg=72.5,
        altitude_m=400_000.0,
    )

    spherical = geodetic_to_igrf_spherical(position)

    assert spherical.longitude_deg == pytest.approx(72.5)


def test_orbital_altitude_increases_geocentric_radius() -> None:
    """A positive orbital altitude should increase center distance."""

    surface = geodetic_to_igrf_spherical(
        GeodeticPosition(
            latitude_deg=0.0,
            longitude_deg=0.0,
            altitude_m=0.0,
        )
    )

    orbit = geodetic_to_igrf_spherical(
        GeodeticPosition(
            latitude_deg=0.0,
            longitude_deg=0.0,
            altitude_m=400_000.0,
        )
    )

    assert orbit.radius_m - surface.radius_m == pytest.approx(
        400_000.0
    )


def test_igrf_reference_radius_is_not_wgs84_equatorial_radius() -> None:
    """The magnetic reference radius must remain distinct from WGS-84."""

    assert IGRF_REFERENCE_RADIUS_M == pytest.approx(
        6_371_200.0
    )

    assert IGRF_REFERENCE_RADIUS_M != pytest.approx(
        6_378_137.0
    )


def test_normalized_radius() -> None:
    """Normalization should use the IGRF magnetic reference radius."""

    position = IGRFSphericalPosition(
        radius_m=IGRF_REFERENCE_RADIUS_M,
        geocentric_colatitude_rad=pi / 2.0,
        longitude_rad=0.0,
    )

    assert position.normalized_radius == pytest.approx(1.0)


def test_invalid_radius_is_rejected() -> None:
    """A geocentric position cannot have zero radius."""

    with pytest.raises(ValueError):
        IGRFSphericalPosition(
            radius_m=0.0,
            geocentric_colatitude_rad=pi / 2.0,
            longitude_rad=0.0,
        )