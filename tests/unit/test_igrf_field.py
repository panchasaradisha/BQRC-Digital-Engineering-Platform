"""Unit tests for IGRF spherical magnetic-field evaluation."""

from math import pi

import pytest

from bqrc.environment.magnetic.igrf.coefficients import (
    CoefficientKind,
    IGRFCoefficient,
    IGRFCoefficientSet,
)
from bqrc.environment.magnetic.igrf.coordinates import (
    IGRF_REFERENCE_RADIUS_M,
    IGRFSphericalPosition,
)
from bqrc.environment.magnetic.igrf.field import (
    IGRFSphericalField,
    evaluate_igrf_spherical,
)


def _degree_one_zonal_model(
    g10_nt: float,
) -> IGRFCoefficientSet:
    """Create a simple axial degree-one test model."""

    return IGRFCoefficientSet(
        model="TEST",
        epoch=2025.0,
        maximum_degree=1,
        coefficients=(
            IGRFCoefficient(
                kind=CoefficientKind.G,
                degree=1,
                order=0,
                epoch=2025.0,
                value_nt=g10_nt,
            ),
            IGRFCoefficient(
                kind=CoefficientKind.G,
                degree=1,
                order=1,
                epoch=2025.0,
                value_nt=0.0,
            ),
            IGRFCoefficient(
                kind=CoefficientKind.H,
                degree=1,
                order=1,
                epoch=2025.0,
                value_nt=0.0,
            ),
        ),
    )


def test_field_magnitude() -> None:
    """Magnitude should use all three orthogonal components."""

    field = IGRFSphericalField(
        radial_nt=3.0,
        colatitudinal_nt=4.0,
        east_nt=12.0,
    )

    assert field.magnitude_nt == pytest.approx(13.0)


def test_axial_dipole_equator() -> None:
    """An axial degree-one field has no radial component at the equator."""

    coefficients = _degree_one_zonal_model(
        g10_nt=-30_000.0,
    )

    position = IGRFSphericalPosition(
        radius_m=IGRF_REFERENCE_RADIUS_M,
        geocentric_colatitude_rad=pi / 2.0,
        longitude_rad=0.0,
    )

    field = evaluate_igrf_spherical(
        coefficients,
        position,
    )

    assert field.radial_nt == pytest.approx(
        0.0,
        abs=1e-9,
    )

    assert field.colatitudinal_nt == pytest.approx(
        -30_000.0
    )

    assert field.east_nt == pytest.approx(0.0)


def test_axial_dipole_northern_midlatitude() -> None:
    """Check the analytical degree-one zonal solution."""

    coefficients = _degree_one_zonal_model(
        g10_nt=-30_000.0,
    )

    theta = pi / 3.0

    position = IGRFSphericalPosition(
        radius_m=IGRF_REFERENCE_RADIUS_M,
        geocentric_colatitude_rad=theta,
        longitude_rad=0.0,
    )

    field = evaluate_igrf_spherical(
        coefficients,
        position,
    )

    expected_radial = (
        2.0
        * -30_000.0
        * 0.5
    )

    expected_colatitudinal = (
        -30_000.0
        * (3.0**0.5 / 2.0)
    )

    assert field.radial_nt == pytest.approx(
        expected_radial
    )

    assert field.colatitudinal_nt == pytest.approx(
        expected_colatitudinal
    )

    assert field.east_nt == pytest.approx(0.0)


def test_degree_one_field_decays_as_inverse_cube() -> None:
    """Degree-one magnetic field should scale as r^-3."""

    coefficients = _degree_one_zonal_model(
        g10_nt=-30_000.0,
    )

    surface = IGRFSphericalPosition(
        radius_m=IGRF_REFERENCE_RADIUS_M,
        geocentric_colatitude_rad=pi / 2.0,
        longitude_rad=0.0,
    )

    doubled_radius = IGRFSphericalPosition(
        radius_m=2.0 * IGRF_REFERENCE_RADIUS_M,
        geocentric_colatitude_rad=pi / 2.0,
        longitude_rad=0.0,
    )

    surface_field = evaluate_igrf_spherical(
        coefficients,
        surface,
    )

    distant_field = evaluate_igrf_spherical(
        coefficients,
        doubled_radius,
    )

    assert distant_field.colatitudinal_nt == pytest.approx(
        surface_field.colatitudinal_nt / 8.0
    )


def test_nonzero_harmonic_can_generate_east_component() -> None:
    """Non-zonal coefficients should support an eastward component."""

    coefficients = IGRFCoefficientSet(
        model="TEST",
        epoch=2025.0,
        maximum_degree=1,
        coefficients=(
            IGRFCoefficient(
                kind=CoefficientKind.G,
                degree=1,
                order=0,
                epoch=2025.0,
                value_nt=0.0,
            ),
            IGRFCoefficient(
                kind=CoefficientKind.G,
                degree=1,
                order=1,
                epoch=2025.0,
                value_nt=0.0,
            ),
            IGRFCoefficient(
                kind=CoefficientKind.H,
                degree=1,
                order=1,
                epoch=2025.0,
                value_nt=10_000.0,
            ),
        ),
    )

    position = IGRFSphericalPosition(
        radius_m=IGRF_REFERENCE_RADIUS_M,
        geocentric_colatitude_rad=pi / 2.0,
        longitude_rad=0.0,
    )

    field = evaluate_igrf_spherical(
        coefficients,
        position,
    )

    assert field.east_nt == pytest.approx(
        -10_000.0
    )


def test_incomplete_coefficient_set_is_rejected() -> None:
    """Missing non-structural coefficients must fail explicitly."""

    coefficients = IGRFCoefficientSet(
        model="TEST",
        epoch=2025.0,
        maximum_degree=1,
        coefficients=(
            IGRFCoefficient(
                kind=CoefficientKind.G,
                degree=1,
                order=0,
                epoch=2025.0,
                value_nt=-30_000.0,
            ),
        ),
    )

    position = IGRFSphericalPosition(
        radius_m=IGRF_REFERENCE_RADIUS_M,
        geocentric_colatitude_rad=pi / 2.0,
        longitude_rad=0.0,
    )

    with pytest.raises(
        ValueError,
        match="incomplete",
    ):
        evaluate_igrf_spherical(
            coefficients,
            position,
        )