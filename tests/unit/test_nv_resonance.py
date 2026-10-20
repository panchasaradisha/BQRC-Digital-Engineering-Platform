
"""Unit tests for the first-order NV-center resonance model."""

from __future__ import annotations

from math import nan

import pytest

from bqrc.sensors.nv.resonance import (
    ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T,
    ZERO_FIELD_SPLITTING_MHZ,
    calculate_nv_resonance,
    project_magnetic_field,
)


def test_zero_magnetic_field() -> None:
    """Both transitions coincide at the zero-field splitting."""

    result = calculate_nv_resonance(
        magnetic_field_nt=(0.0, 0.0, 0.0),
        nv_axis=(0.0, 0.0, 1.0),
    )

    assert result.lower_mhz == pytest.approx(
        ZERO_FIELD_SPLITTING_MHZ
    )
    assert result.upper_mhz == pytest.approx(
        ZERO_FIELD_SPLITTING_MHZ
    )
    assert result.projected_field_nt == pytest.approx(0.0)


def test_aligned_magnetic_field() -> None:
    """An axial magnetic field produces symmetric Zeeman splitting."""

    result = calculate_nv_resonance(
        magnetic_field_nt=(30_000.0, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )

    expected_shift_mhz = (
        ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T
        * 30_000.0
        / 1_000_000_000.0
    )

    assert result.lower_mhz == pytest.approx(
        ZERO_FIELD_SPLITTING_MHZ - expected_shift_mhz
    )
    assert result.upper_mhz == pytest.approx(
        ZERO_FIELD_SPLITTING_MHZ + expected_shift_mhz
    )
    assert result.projected_field_nt == pytest.approx(30_000.0)


def test_perpendicular_magnetic_field() -> None:
    """The first-order axial model has no perpendicular-field shift."""

    result = calculate_nv_resonance(
        magnetic_field_nt=(30_000.0, 0.0, 0.0),
        nv_axis=(0.0, 0.0, 1.0),
    )

    assert result.projected_field_nt == pytest.approx(0.0)
    assert result.lower_mhz == pytest.approx(
        ZERO_FIELD_SPLITTING_MHZ
    )
    assert result.upper_mhz == pytest.approx(
        ZERO_FIELD_SPLITTING_MHZ
    )


def test_negative_axial_field() -> None:
    """Reversing the field preserves splitting and reverses projection."""

    positive = calculate_nv_resonance(
        magnetic_field_nt=(30_000.0, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )

    negative = calculate_nv_resonance(
        magnetic_field_nt=(-30_000.0, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )

    assert negative.projected_field_nt == pytest.approx(-30_000.0)
    assert negative.lower_mhz == pytest.approx(positive.lower_mhz)
    assert negative.upper_mhz == pytest.approx(positive.upper_mhz)


def test_nv_axis_is_normalized() -> None:
    """Scaling the NV-axis vector must not change the projection."""

    projection = project_magnetic_field(
        magnetic_field_nt=(30_000.0, 0.0, 0.0),
        nv_axis=(5.0, 0.0, 0.0),
    )

    assert projection == pytest.approx(30_000.0)


@pytest.mark.parametrize(
    ("magnetic_field_nt", "nv_axis"),
    [
        ((30_000.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        ((nan, 0.0, 0.0), (1.0, 0.0, 0.0)),
        ((30_000.0, 0.0, 0.0), (nan, 0.0, 0.0)),
    ],
)
def test_invalid_vectors_are_rejected(
    magnetic_field_nt: tuple[float, float, float],
    nv_axis: tuple[float, float, float],
) -> None:
    """Invalid vectors must raise ValueError."""

    with pytest.raises(ValueError):
        calculate_nv_resonance(
            magnetic_field_nt=magnetic_field_nt,
            nv_axis=nv_axis,
        )


def test_invalid_zero_field_splitting_is_rejected() -> None:
    """Zero-field splitting must be finite and positive."""

    with pytest.raises(ValueError):
        calculate_nv_resonance(
            magnetic_field_nt=(30_000.0, 0.0, 0.0),
            nv_axis=(1.0, 0.0, 0.0),
            zero_field_splitting_mhz=-1.0,
        )
