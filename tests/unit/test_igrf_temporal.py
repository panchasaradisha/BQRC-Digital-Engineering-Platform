"""Unit tests for IGRF-14 coefficient time evolution."""

from pathlib import Path

import pytest

from bqrc.environment.magnetic.igrf.coefficients import (
    CoefficientKind,
    IGRFCoefficient,
    IGRFCoefficientSet,
)
from bqrc.environment.magnetic.igrf.parser import (
    load_igrf14_2025,
)
from bqrc.environment.magnetic.igrf.temporal import (
    IGRFEpochError,
    predict_igrf14_coefficients,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IGRF14_DATASET = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "geomagnetic"
    / "igrf14"
    / "raw"
    / "igrf14coeffs.txt"
)


def test_epoch_2025_preserves_base_values() -> None:
    """Prediction at the base epoch should reproduce the base model."""

    base = load_igrf14_2025(IGRF14_DATASET)

    predicted = predict_igrf14_coefficients(
        base,
        2025.0,
    )

    assert predicted.epoch == 2025.0

    assert predicted.get(
        CoefficientKind.G,
        1,
        0,
    ).value_nt == pytest.approx(-29350.0)


def test_g10_prediction_at_2027() -> None:
    """g(1,0) should evolve using its predictive secular variation."""

    base = load_igrf14_2025(IGRF14_DATASET)

    predicted = predict_igrf14_coefficients(
        base,
        2027.0,
    )

    g10 = predicted.get(
        CoefficientKind.G,
        1,
        0,
    )

    expected = -29350.0 + 2.0 * 12.6

    assert g10.value_nt == pytest.approx(expected)


def test_fractional_epoch_prediction() -> None:
    """Decimal-year epochs should support fractional elapsed years."""

    base = load_igrf14_2025(IGRF14_DATASET)

    predicted = predict_igrf14_coefficients(
        base,
        2026.5,
    )

    g10 = predicted.get(
        CoefficientKind.G,
        1,
        0,
    )

    expected = -29350.0 + 1.5 * 12.6

    assert g10.value_nt == pytest.approx(expected)


def test_degree_above_sv_limit_remains_at_2025_value() -> None:
    """Coefficients without published SV must not invent time evolution."""

    base = load_igrf14_2025(IGRF14_DATASET)

    original = base.get(
        CoefficientKind.G,
        13,
        0,
    )

    predicted = predict_igrf14_coefficients(
        base,
        2029.0,
    )

    evolved = predicted.get(
        CoefficientKind.G,
        13,
        0,
    )

    assert original.secular_variation_nt_per_year is None
    assert evolved.secular_variation_nt_per_year is None
    assert evolved.value_nt == pytest.approx(
        original.value_nt
    )


@pytest.mark.parametrize(
    "epoch",
    [
        2024.999,
        2030.001,
        2032.0,
    ],
)
def test_out_of_range_epoch_is_rejected(
    epoch: float,
) -> None:
    """Unsupported predictive epochs must fail explicitly."""

    base = load_igrf14_2025(IGRF14_DATASET)

    with pytest.raises(IGRFEpochError):
        predict_igrf14_coefficients(
            base,
            epoch,
        )


def test_2030_boundary_is_allowed() -> None:
    """The declared prediction boundary should remain usable."""

    base = load_igrf14_2025(IGRF14_DATASET)

    predicted = predict_igrf14_coefficients(
        base,
        2030.0,
    )

    assert predicted.epoch == 2030.0


def test_non_finite_epoch_is_rejected() -> None:
    """Non-finite epochs must never enter scientific calculations."""

    base = load_igrf14_2025(IGRF14_DATASET)

    with pytest.raises(IGRFEpochError):
        predict_igrf14_coefficients(
            base,
            float("nan"),
        )


def test_wrong_model_is_rejected() -> None:
    """The IGRF-14 predictor must not accept another model silently."""

    base = IGRFCoefficientSet(
        model="OTHER-MODEL",
        epoch=2025.0,
        maximum_degree=1,
        coefficients=(
            IGRFCoefficient(
                kind=CoefficientKind.G,
                degree=1,
                order=0,
                epoch=2025.0,
                value_nt=-1.0,
            ),
        ),
    )

    with pytest.raises(ValueError):
        predict_igrf14_coefficients(
            base,
            2026.0,
        )


def test_wrong_base_epoch_is_rejected() -> None:
    """Prediction must start from the defined 2025.0 coefficient set."""

    base = IGRFCoefficientSet(
        model="IGRF-14",
        epoch=2024.0,
        maximum_degree=1,
        coefficients=(
            IGRFCoefficient(
                kind=CoefficientKind.G,
                degree=1,
                order=0,
                epoch=2024.0,
                value_nt=-1.0,
            ),
        ),
    )

    with pytest.raises(ValueError):
        predict_igrf14_coefficients(
            base,
            2026.0,
        )