"""Unit tests for IGRF coefficient data models."""

import pytest

from bqrc.environment.magnetic.igrf.coefficients import (
    CoefficientKind,
    IGRFCoefficient,
    IGRFCoefficientSet,
)


def test_valid_g_coefficient() -> None:
    """A valid g coefficient should preserve its scientific metadata."""

    coefficient = IGRFCoefficient(
        kind=CoefficientKind.G,
        degree=1,
        order=0,
        epoch=2025.0,
        value_nt=-29350.0,
        secular_variation_nt_per_year=12.6,
    )

    assert coefficient.kind is CoefficientKind.G
    assert coefficient.degree == 1
    assert coefficient.order == 0
    assert coefficient.epoch == 2025.0
    assert coefficient.value_nt == -29350.0
    assert coefficient.secular_variation_nt_per_year == 12.6


def test_valid_h_coefficient() -> None:
    """A valid h coefficient should allow order greater than zero."""

    coefficient = IGRFCoefficient(
        kind=CoefficientKind.H,
        degree=1,
        order=1,
        epoch=2025.0,
        value_nt=4545.5,
        secular_variation_nt_per_year=-21.5,
    )

    assert coefficient.key == (
        CoefficientKind.H,
        1,
        1,
    )


@pytest.mark.parametrize(
    ("degree", "order"),
    [
        (0, 0),
        (-1, 0),
        (2, -1),
        (2, 3),
    ],
)
def test_invalid_degree_order_combinations_are_rejected(
    degree: int,
    order: int,
) -> None:
    """Invalid spherical-harmonic indices must be rejected."""

    with pytest.raises(ValueError):
        IGRFCoefficient(
            kind=CoefficientKind.G,
            degree=degree,
            order=order,
            epoch=2025.0,
            value_nt=1.0,
        )


def test_h_coefficient_with_zero_order_is_rejected() -> None:
    """The h_n^0 coefficient is not part of the IGRF representation."""

    with pytest.raises(ValueError):
        IGRFCoefficient(
            kind=CoefficientKind.H,
            degree=1,
            order=0,
            epoch=2025.0,
            value_nt=1.0,
        )


def test_non_finite_coefficient_value_is_rejected() -> None:
    """Scientific coefficient values must be finite."""

    with pytest.raises(ValueError):
        IGRFCoefficient(
            kind=CoefficientKind.G,
            degree=1,
            order=0,
            epoch=2025.0,
            value_nt=float("nan"),
        )


def test_coefficient_set_lookup() -> None:
    """Coefficient sets should support explicit coefficient lookup."""

    coefficients = (
        IGRFCoefficient(
            kind=CoefficientKind.G,
            degree=1,
            order=0,
            epoch=2025.0,
            value_nt=-29350.0,
        ),
        IGRFCoefficient(
            kind=CoefficientKind.G,
            degree=1,
            order=1,
            epoch=2025.0,
            value_nt=-1410.3,
        ),
        IGRFCoefficient(
            kind=CoefficientKind.H,
            degree=1,
            order=1,
            epoch=2025.0,
            value_nt=4545.5,
        ),
    )

    coefficient_set = IGRFCoefficientSet(
        model="IGRF-14",
        epoch=2025.0,
        maximum_degree=1,
        coefficients=coefficients,
    )

    result = coefficient_set.get(
        CoefficientKind.G,
        1,
        0,
    )

    assert result.value_nt == -29350.0


def test_duplicate_coefficients_are_rejected() -> None:
    """A coefficient identity must occur only once in an epoch set."""

    coefficient = IGRFCoefficient(
        kind=CoefficientKind.G,
        degree=1,
        order=0,
        epoch=2025.0,
        value_nt=-29350.0,
    )

    with pytest.raises(ValueError):
        IGRFCoefficientSet(
            model="IGRF-14",
            epoch=2025.0,
            maximum_degree=1,
            coefficients=(
                coefficient,
                coefficient,
            ),
        )


def test_mixed_epochs_are_rejected() -> None:
    """One coefficient set must not silently mix model epochs."""

    coefficients = (
        IGRFCoefficient(
            kind=CoefficientKind.G,
            degree=1,
            order=0,
            epoch=2025.0,
            value_nt=-29350.0,
        ),
        IGRFCoefficient(
            kind=CoefficientKind.G,
            degree=1,
            order=1,
            epoch=2020.0,
            value_nt=-1450.9,
        ),
    )

    with pytest.raises(ValueError):
        IGRFCoefficientSet(
            model="IGRF-14",
            epoch=2025.0,
            maximum_degree=1,
            coefficients=coefficients,
        )


def test_missing_coefficient_raises_key_error() -> None:
    """Explicit lookup should fail clearly for an unavailable coefficient."""

    coefficient_set = IGRFCoefficientSet(
        model="IGRF-14",
        epoch=2025.0,
        maximum_degree=1,
        coefficients=(
            IGRFCoefficient(
                kind=CoefficientKind.G,
                degree=1,
                order=0,
                epoch=2025.0,
                value_nt=-29350.0,
            ),
        ),
    )

    with pytest.raises(KeyError):
        coefficient_set.get(
            CoefficientKind.H,
            1,
            1,
        )