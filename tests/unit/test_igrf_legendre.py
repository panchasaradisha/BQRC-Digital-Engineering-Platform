"""Unit tests for IGRF associated Legendre calculations."""

from math import cos, pi, sin

import pytest

from bqrc.environment.magnetic.igrf.legendre import (
    associated_legendre,
)


def test_degree_zero() -> None:
    """P_0^0 must equal one."""

    table = associated_legendre(
        maximum_degree=0,
        colatitude_rad=1.0,
    )

    assert table.get(0, 0) == pytest.approx(1.0)
    assert table.derivative(0, 0) == pytest.approx(0.0)


def test_degree_one_zonal_term() -> None:
    """P_1^0 should equal cos(theta)."""

    theta = 0.7

    table = associated_legendre(
        maximum_degree=1,
        colatitude_rad=theta,
    )

    assert table.get(
        1,
        0,
    ) == pytest.approx(
        cos(theta)
    )

    assert table.derivative(
        1,
        0,
    ) == pytest.approx(
        -sin(theta)
    )


def test_degree_one_sectoral_term() -> None:
    """P_1^1 should equal sin(theta) in this recurrence convention."""

    theta = 0.7

    table = associated_legendre(
        maximum_degree=1,
        colatitude_rad=theta,
    )

    assert table.get(
        1,
        1,
    ) == pytest.approx(
        sin(theta)
    )

    assert table.derivative(
        1,
        1,
    ) == pytest.approx(
        cos(theta)
    )


def test_equator_degree_one() -> None:
    """Degree-one functions should have expected equatorial values."""

    table = associated_legendre(
        maximum_degree=1,
        colatitude_rad=pi / 2.0,
    )

    assert table.get(
        1,
        0,
    ) == pytest.approx(
        0.0,
        abs=1e-15,
    )

    assert table.get(
        1,
        1,
    ) == pytest.approx(
        1.0
    )


def test_north_pole_degree_one() -> None:
    """Sectoral degree-one term should vanish at the north pole."""

    table = associated_legendre(
        maximum_degree=1,
        colatitude_rad=0.0,
    )

    assert table.get(
        1,
        0,
    ) == pytest.approx(1.0)

    assert table.get(
        1,
        1,
    ) == pytest.approx(0.0)


def test_degree_two_zonal_term() -> None:
    """Check the degree-two zonal recurrence explicitly."""

    theta = 0.9

    table = associated_legendre(
        maximum_degree=2,
        colatitude_rad=theta,
    )

    expected = (
        cos(theta) ** 2
        - 1.0 / 3.0
    )

    assert table.get(
        2,
        0,
    ) == pytest.approx(expected)


def test_invalid_order_is_rejected() -> None:
    """Orders larger than degree are invalid."""

    table = associated_legendre(
        maximum_degree=3,
        colatitude_rad=1.0,
    )

    with pytest.raises(ValueError):
        table.get(
            2,
            3,
        )


def test_degree_beyond_table_is_rejected() -> None:
    """Lookup cannot exceed the generated table."""

    table = associated_legendre(
        maximum_degree=3,
        colatitude_rad=1.0,
    )

    with pytest.raises(ValueError):
        table.get(
            4,
            0,
        )


@pytest.mark.parametrize(
    "colatitude",
    [
        -0.001,
        pi + 0.001,
        float("nan"),
    ],
)
def test_invalid_colatitude_is_rejected(
    colatitude: float,
) -> None:
    """Invalid colatitudes must not enter harmonic calculations."""

    with pytest.raises(ValueError):
        associated_legendre(
            maximum_degree=3,
            colatitude_rad=colatitude,
        )