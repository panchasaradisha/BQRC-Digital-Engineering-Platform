"""Unit tests for IGRF Schmidt quasi-normalization."""

from math import pi, sqrt

import pytest

from bqrc.environment.magnetic.igrf.legendre import (
    associated_legendre,
)
from bqrc.environment.magnetic.igrf.normalization import (
    apply_schmidt_normalization,
    schmidt_quasi_normalization,
)


def test_degree_zero_factor() -> None:
    """The degree-zero normalization factor must equal one."""

    factors = schmidt_quasi_normalization(0)

    assert factors.get(
        0,
        0,
    ) == pytest.approx(1.0)


def test_zonal_factors_equal_one() -> None:
    """All m=0 Schmidt factors should equal one."""

    factors = schmidt_quasi_normalization(13)

    for degree in range(14):
        assert factors.get(
            degree,
            0,
        ) == pytest.approx(1.0)


def test_degree_one_order_one_factor() -> None:
    """S_1^1 should equal one."""

    factors = schmidt_quasi_normalization(1)

    assert factors.get(
        1,
        1,
    ) == pytest.approx(1.0)


def test_degree_two_order_one_factor() -> None:
    """S_2^1 should equal sqrt(1/3)."""

    factors = schmidt_quasi_normalization(2)

    assert factors.get(
        2,
        1,
    ) == pytest.approx(
        sqrt(1.0 / 3.0)
    )


def test_degree_two_order_two_factor() -> None:
    """S_2^2 should equal sqrt(1/12)."""

    factors = schmidt_quasi_normalization(2)

    assert factors.get(
        2,
        2,
    ) == pytest.approx(
        sqrt(1.0 / 12.0)
    )


def test_normalization_preserves_zonal_term() -> None:
    """m=0 terms should remain unchanged."""

    raw = associated_legendre(
        maximum_degree=2,
        colatitude_rad=0.8,
    )

    normalized = apply_schmidt_normalization(
        raw
    )

    assert normalized.get(
        2,
        0,
    ) == pytest.approx(
        raw.get(2, 0)
    )

    assert normalized.derivative(
        2,
        0,
    ) == pytest.approx(
        raw.derivative(2, 0)
    )


def test_normalization_scales_degree_two_order_one() -> None:
    """P_2^1 should receive the expected Schmidt factor."""

    raw = associated_legendre(
        maximum_degree=2,
        colatitude_rad=0.8,
    )

    normalized = apply_schmidt_normalization(
        raw
    )

    factor = sqrt(1.0 / 3.0)

    assert normalized.get(
        2,
        1,
    ) == pytest.approx(
        raw.get(2, 1) * factor
    )

    assert normalized.derivative(
        2,
        1,
    ) == pytest.approx(
        raw.derivative(2, 1) * factor
    )


def test_equatorial_degree_one_values() -> None:
    """Low-degree normalized values should retain expected behavior."""

    raw = associated_legendre(
        maximum_degree=1,
        colatitude_rad=pi / 2.0,
    )

    normalized = apply_schmidt_normalization(
        raw
    )

    assert normalized.get(
        1,
        0,
    ) == pytest.approx(
        0.0,
        abs=1e-15,
    )

    assert normalized.get(
        1,
        1,
    ) == pytest.approx(1.0)


def test_invalid_order_lookup_is_rejected() -> None:
    """Orders larger than degree must be rejected."""

    factors = schmidt_quasi_normalization(3)

    with pytest.raises(ValueError):
        factors.get(
            2,
            3,
        )


def test_degree_beyond_table_is_rejected() -> None:
    """Lookup beyond the generated degree must fail."""

    factors = schmidt_quasi_normalization(3)

    with pytest.raises(ValueError):
        factors.get(
            4,
            0,
        )


def test_negative_maximum_degree_is_rejected() -> None:
    """Negative maximum degree is invalid."""

    with pytest.raises(ValueError):
        schmidt_quasi_normalization(-1)


def test_boolean_maximum_degree_is_rejected() -> None:
    """Boolean values must not masquerade as integer degrees."""

    with pytest.raises(TypeError):
        schmidt_quasi_normalization(True)