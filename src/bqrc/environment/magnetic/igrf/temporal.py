"""Time evolution of IGRF-14 geomagnetic coefficients."""

from __future__ import annotations

from math import isfinite

from bqrc.environment.magnetic.igrf.coefficients import (
    IGRFCoefficient,
    IGRFCoefficientSet,
)

IGRF14_PREDICTION_START_YEAR = 2025.0
IGRF14_PREDICTION_END_YEAR = 2030.0


class IGRFEpochError(ValueError):
    """Raised when an epoch is outside the supported prediction interval."""


def predict_igrf14_coefficients(
    base: IGRFCoefficientSet,
    epoch: float,
) -> IGRFCoefficientSet:
    """Predict IGRF-14 coefficients for an epoch from 2025.0 to 2030.0.

    Coefficients with published predictive secular variation are evolved
    linearly from epoch 2025.0.

    Coefficients without published predictive secular variation retain their
    2025.0 main-field value. No secular variation is invented for those
    coefficients.

    Parameters
    ----------
    base:
        IGRF-14 coefficient set at epoch 2025.0.
    epoch:
        Requested decimal year.

    Returns
    -------
    IGRFCoefficientSet
        Coefficients represented at the requested epoch.

    Raises
    ------
    IGRFEpochError
        If the requested epoch is outside 2025.0 through 2030.0.
    ValueError
        If the supplied base coefficient set is not the expected IGRF-14
        2025.0 model.
    """

    if not isfinite(epoch):
        raise IGRFEpochError("requested epoch must be finite")

    if not (
        IGRF14_PREDICTION_START_YEAR
        <= epoch
        <= IGRF14_PREDICTION_END_YEAR
    ):
        raise IGRFEpochError(
            "IGRF-14 predictive epoch must be within "
            "2025.0 through 2030.0"
        )

    if base.model != "IGRF-14":
        raise ValueError(
            "base coefficient set must use model IGRF-14"
        )

    if base.epoch != IGRF14_PREDICTION_START_YEAR:
        raise ValueError(
            "base coefficient set must represent epoch 2025.0"
        )

    elapsed_years = epoch - base.epoch

    predicted: list[IGRFCoefficient] = []

    for coefficient in base.coefficients:
        secular_variation = (
            coefficient.secular_variation_nt_per_year
        )

        if secular_variation is None:
            value_nt = coefficient.value_nt
        else:
            value_nt = (
                coefficient.value_nt
                + elapsed_years * secular_variation
            )

        predicted.append(
            IGRFCoefficient(
                kind=coefficient.kind,
                degree=coefficient.degree,
                order=coefficient.order,
                epoch=epoch,
                value_nt=value_nt,
                secular_variation_nt_per_year=secular_variation,
            )
        )

    return IGRFCoefficientSet(
        model=base.model,
        epoch=epoch,
        maximum_degree=base.maximum_degree,
        coefficients=tuple(predicted),
    )