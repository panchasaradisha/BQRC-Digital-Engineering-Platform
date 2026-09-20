"""Unit tests for geomagnetic component transformations."""

import pytest

from bqrc.environment.earth.geodetic import GeodeticPosition
from bqrc.environment.magnetic.igrf.components import (
    GeodeticMagneticField,
    spherical_to_geodetic_ned,
)
from bqrc.environment.magnetic.igrf.coordinates import (
    geodetic_to_igrf_spherical,
)
from bqrc.environment.magnetic.igrf.field import (
    IGRFSphericalField,
)


def test_equator_component_conversion() -> None:
    """Geodetic and geocentric axes coincide at the equator."""

    geodetic = GeodeticPosition(
        latitude_deg=0.0,
        longitude_deg=0.0,
        altitude_m=0.0,
    )

    spherical = geodetic_to_igrf_spherical(
        geodetic
    )

    field = IGRFSphericalField(
        radial_nt=100.0,
        colatitudinal_nt=-200.0,
        east_nt=50.0,
    )

    ned = spherical_to_geodetic_ned(
        field,
        geodetic,
        spherical,
    )

    assert ned.north_nt == pytest.approx(200.0)
    assert ned.east_nt == pytest.approx(50.0)
    assert ned.down_nt == pytest.approx(-100.0)


def test_midlatitude_rotation_changes_north_and_down() -> None:
    """Ellipsoidal latitude difference must rotate north/down components."""

    geodetic = GeodeticPosition(
        latitude_deg=45.0,
        longitude_deg=0.0,
        altitude_m=0.0,
    )

    spherical = geodetic_to_igrf_spherical(
        geodetic
    )

    field = IGRFSphericalField(
        radial_nt=-40_000.0,
        colatitudinal_nt=-20_000.0,
        east_nt=1_000.0,
    )

    ned = spherical_to_geodetic_ned(
        field,
        geodetic,
        spherical,
    )

    assert ned.north_nt != pytest.approx(
        20_000.0,
        abs=1e-6,
    )

    assert ned.down_nt != pytest.approx(
        40_000.0,
        abs=1e-6,
    )

    assert ned.east_nt == pytest.approx(
        1_000.0
    )


def test_rotation_preserves_total_magnitude() -> None:
    """An orthogonal basis rotation must preserve vector magnitude."""

    geodetic = GeodeticPosition(
        latitude_deg=45.0,
        longitude_deg=72.0,
        altitude_m=400_000.0,
    )

    spherical = geodetic_to_igrf_spherical(
        geodetic
    )

    field = IGRFSphericalField(
        radial_nt=-30_000.0,
        colatitudinal_nt=-20_000.0,
        east_nt=3_000.0,
    )

    ned = spherical_to_geodetic_ned(
        field,
        geodetic,
        spherical,
    )

    assert ned.total_intensity_nt == pytest.approx(
        field.magnitude_nt
    )


def test_horizontal_intensity() -> None:
    """H should be the magnitude of north/east components."""

    field = GeodeticMagneticField(
        north_nt=3.0,
        east_nt=4.0,
        down_nt=12.0,
    )

    assert field.horizontal_intensity_nt == pytest.approx(
        5.0
    )


def test_total_intensity() -> None:
    """F should include horizontal and vertical components."""

    field = GeodeticMagneticField(
        north_nt=3.0,
        east_nt=4.0,
        down_nt=12.0,
    )

    assert field.total_intensity_nt == pytest.approx(
        13.0
    )


def test_declination() -> None:
    """Declination should be measured eastward from north."""

    field = GeodeticMagneticField(
        north_nt=1.0,
        east_nt=1.0,
        down_nt=0.0,
    )

    assert field.declination_deg == pytest.approx(
        45.0
    )


def test_positive_down_inclination() -> None:
    """Downward fields should produce positive inclination."""

    field = GeodeticMagneticField(
        north_nt=1.0,
        east_nt=0.0,
        down_nt=1.0,
    )

    assert field.inclination_deg == pytest.approx(
        45.0
    )


def test_upward_field_has_negative_inclination() -> None:
    """Upward fields should produce negative inclination."""

    field = GeodeticMagneticField(
        north_nt=1.0,
        east_nt=0.0,
        down_nt=-1.0,
    )

    assert field.inclination_deg == pytest.approx(
        -45.0
    )