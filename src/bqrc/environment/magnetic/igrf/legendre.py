"""Associated Legendre functions used by the IGRF spherical harmonics."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, sin


@dataclass(frozen=True, slots=True)
class LegendreTable:
    """Associated Legendre values and colatitude derivatives.

    Arrays are indexed as::

        values[n][m]
        derivatives[n][m]

    where ``n`` is degree and ``m`` is order.

    Derivatives are with respect to geocentric colatitude theta.
    """

    maximum_degree: int
    values: tuple[tuple[float, ...], ...]
    derivatives: tuple[tuple[float, ...], ...]

    def get(self, degree: int, order: int) -> float:
        """Return P_n^m."""

        _validate_index(
            degree,
            order,
            self.maximum_degree,
        )

        return self.values[degree][order]

    def derivative(
        self,
        degree: int,
        order: int,
    ) -> float:
        """Return dP_n^m / dtheta."""

        _validate_index(
            degree,
            order,
            self.maximum_degree,
        )

        return self.derivatives[degree][order]


def _validate_index(
    degree: int,
    order: int,
    maximum_degree: int,
) -> None:
    """Validate an associated-Legendre table index."""

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


def associated_legendre(
    maximum_degree: int,
    colatitude_rad: float,
) -> LegendreTable:
    """Evaluate unnormalized associated Legendre functions.

    The implementation uses a recurrence in geocentric colatitude.

    Parameters
    ----------
    maximum_degree:
        Highest spherical-harmonic degree to evaluate.
    colatitude_rad:
        Geocentric colatitude theta in radians.

    Returns
    -------
    LegendreTable
        Unnormalized associated Legendre values and derivatives with
        respect to colatitude.
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

    if not isfinite(colatitude_rad):
        raise ValueError(
            "colatitude must be finite"
        )

    if not 0.0 <= colatitude_rad <= 3.141592653589793:
        raise ValueError(
            "colatitude must be within 0 to pi radians"
        )

    sin_theta = sin(colatitude_rad)
    cos_theta = cos(colatitude_rad)

    values = [
        [0.0 for _ in range(maximum_degree + 1)]
        for _ in range(maximum_degree + 1)
    ]

    derivatives = [
        [0.0 for _ in range(maximum_degree + 1)]
        for _ in range(maximum_degree + 1)
    ]

    values[0][0] = 1.0
    derivatives[0][0] = 0.0

    for degree in range(1, maximum_degree + 1):
        for order in range(0, degree + 1):
            if degree == order:
                values[degree][order] = (
                    sin_theta
                    * values[degree - 1][order - 1]
                )

                derivatives[degree][order] = (
                    sin_theta
                    * derivatives[degree - 1][order - 1]
                    + cos_theta
                    * values[degree - 1][order - 1]
                )

            elif degree == 1 and order == 0:
                values[degree][order] = (
                    cos_theta
                    * values[degree - 1][order]
                )

                derivatives[degree][order] = (
                    cos_theta
                    * derivatives[degree - 1][order]
                    - sin_theta
                    * values[degree - 1][order]
                )

            else:
                k = (
                    ((degree - 1) ** 2 - order**2)
                    / (
                        (2 * degree - 1)
                        * (2 * degree - 3)
                    )
                )

                values[degree][order] = (
                    cos_theta
                    * values[degree - 1][order]
                    - k
                    * values[degree - 2][order]
                )

                derivatives[degree][order] = (
                    cos_theta
                    * derivatives[degree - 1][order]
                    - sin_theta
                    * values[degree - 1][order]
                    - k
                    * derivatives[degree - 2][order]
                )

    return LegendreTable(
        maximum_degree=maximum_degree,
        values=tuple(
            tuple(row)
            for row in values
        ),
        derivatives=tuple(
            tuple(row)
            for row in derivatives
        ),
    )