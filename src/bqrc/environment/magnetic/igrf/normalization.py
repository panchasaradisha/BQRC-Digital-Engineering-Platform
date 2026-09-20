"""Schmidt quasi-normalization utilities for IGRF harmonics."""

from __future__ import annotations

from dataclasses import dataclass
from math import factorial, isfinite, sqrt

from bqrc.environment.magnetic.igrf.legendre import LegendreTable


@dataclass(frozen=True, slots=True)
class SchmidtNormalizationTable:
    """Schmidt quasi-normalization factors indexed by degree and order."""

    maximum_degree: int
    factors: tuple[tuple[float, ...], ...]

    def get(
        self,
        degree: int,
        order: int,
    ) -> float:
        """Return the Schmidt normalization factor S_n^m."""

        _validate_index(
            degree,
            order,
            self.maximum_degree,
        )

        return self.factors[degree][order]


def _validate_index(
    degree: int,
    order: int,
    maximum_degree: int,
) -> None:
    """Validate a spherical-harmonic degree/order index."""

    if degree < 0:
        raise ValueError("degree must be non-negative")

    if order < 0:
        raise ValueError("order must be non-negative")

    if order > degree:
        raise ValueError("order cannot exceed degree")

    if degree > maximum_degree:
        raise ValueError(
            "degree exceeds table maximum degree"
        )


def schmidt_quasi_normalization(
    maximum_degree: int,
) -> SchmidtNormalizationTable:
    """Generate Schmidt quasi-normalization factors.

    The factor used here is

        S_n^m =
            sqrt(
                (2 - delta_m0)
                * (n - m)! / (n + m)!
            )

    where delta_m0 equals one for m = 0 and zero otherwise.

    Parameters
    ----------
    maximum_degree:
        Highest spherical-harmonic degree required.

    Returns
    -------
    SchmidtNormalizationTable
        Normalization factors for all valid degree/order pairs.
    """

    if isinstance(maximum_degree, bool) or not isinstance(
        maximum_degree,
        int,
    ):
        raise TypeError(
            "maximum_degree must be an integer"
        )

    if maximum_degree < 0:
        raise ValueError(
            "maximum_degree must be non-negative"
        )

    factors = [
        [0.0 for _ in range(maximum_degree + 1)]
        for _ in range(maximum_degree + 1)
    ]

    for degree in range(maximum_degree + 1):
        for order in range(degree + 1):
            order_factor = 1.0 if order == 0 else 2.0

            numerator = (
                order_factor
                * factorial(degree - order)
            )

            denominator = factorial(
                degree + order
            )

            factors[degree][order] = sqrt(
                numerator / denominator
            )

    return SchmidtNormalizationTable(
        maximum_degree=maximum_degree,
        factors=tuple(
            tuple(row)
            for row in factors
        ),
    )


def apply_schmidt_normalization(
    table: LegendreTable,
) -> LegendreTable:
    """Apply Schmidt quasi-normalization to a Legendre table.

    The same normalization factor is applied to both the function and its
    colatitude derivative because the factor depends only on degree/order,
    not on colatitude.
    """

    normalization = schmidt_quasi_normalization(
        table.maximum_degree
    )

    values: list[list[float]] = []
    derivatives: list[list[float]] = []

    for degree in range(
        table.maximum_degree + 1
    ):
        value_row: list[float] = []
        derivative_row: list[float] = []

        for order in range(
            table.maximum_degree + 1
        ):
            if order > degree:
                value_row.append(0.0)
                derivative_row.append(0.0)
                continue

            factor = normalization.get(
                degree,
                order,
            )

            normalized_value = (
                table.values[degree][order]
                * factor
            )

            normalized_derivative = (
                table.derivatives[degree][order]
                * factor
            )

            if not isfinite(normalized_value):
                raise ValueError(
                    "normalized Legendre value must be finite"
                )

            if not isfinite(normalized_derivative):
                raise ValueError(
                    "normalized Legendre derivative must be finite"
                )

            value_row.append(normalized_value)
            derivative_row.append(
                normalized_derivative
            )

        values.append(value_row)
        derivatives.append(derivative_row)

    return LegendreTable(
        maximum_degree=table.maximum_degree,
        values=tuple(
            tuple(row)
            for row in values
        ),
        derivatives=tuple(
            tuple(row)
            for row in derivatives
        ),
    )