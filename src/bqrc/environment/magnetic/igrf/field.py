"""IGRF spherical-harmonic magnetic-field evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, isfinite, sin, sqrt

from bqrc.environment.magnetic.igrf.coefficients import (
    CoefficientKind,
    IGRFCoefficientSet,
)
from bqrc.environment.magnetic.igrf.coordinates import (
    IGRF_REFERENCE_RADIUS_M,
    IGRFSphericalPosition,
)


@dataclass(frozen=True, slots=True)
class IGRFSphericalField:
    """Magnetic-field vector in geocentric spherical coordinates.

    Sign conventions
    ----------------
    radial_nt:
        Positive outward from Earth's center.

    colatitudinal_nt:
        Positive in the direction of increasing geocentric colatitude,
        approximately southward.

    east_nt:
        Positive toward increasing longitude, i.e. eastward.
    """

    radial_nt: float
    colatitudinal_nt: float
    east_nt: float

    def __post_init__(self) -> None:
        """Require finite physical field components."""

        for value in (
            self.radial_nt,
            self.colatitudinal_nt,
            self.east_nt,
        ):
            if not isfinite(value):
                raise ValueError(
                    "magnetic-field components must be finite"
                )

    @property
    def magnitude_nt(self) -> float:
        """Return total magnetic-field magnitude in nanotesla."""

        return hypot(
            hypot(
                self.radial_nt,
                self.colatitudinal_nt,
            ),
            self.east_nt,
        )


def evaluate_igrf_spherical(
    coefficients: IGRFCoefficientSet,
    position: IGRFSphericalPosition,
) -> IGRFSphericalField:
    """Evaluate IGRF at a geocentric spherical position.

    This implementation uses the recurrence convention independently
    validated against the official Geomag IGRF reference implementation.

    The result remains in geocentric spherical coordinates. Conversion
    into the local geodetic North-East-Down frame is intentionally
    performed separately by the component-transformation layer.
    """

    maximum_degree = coefficients.maximum_degree

    geocentric_latitude = (
        position.geocentric_latitude_rad
    )

    slat = sin(geocentric_latitude)
    clat = cos(geocentric_latitude)

    longitude = position.longitude_rad

    # Longitude harmonics.
    sl = [0.0] * (maximum_degree + 1)
    cl = [0.0] * (maximum_degree + 1)

    if maximum_degree >= 1:
        sl[1] = sin(longitude)
        cl[1] = cos(longitude)

    for order in range(
        2,
        maximum_degree + 1,
    ):
        sl[order] = (
            sl[1] * cl[order - 1]
            + cl[1] * sl[order - 1]
        )

        cl[order] = (
            cl[1] * cl[order - 1]
            - sl[1] * sl[order - 1]
        )

    # Build the coefficient ordering used by the validated recurrence.
    gh = _build_gh_array(coefficients)

    npq = (
        maximum_degree
        * (maximum_degree + 3)
    ) // 2

    # One-based indexing is retained here because the validated recurrence
    # is naturally expressed using this triangular harmonic indexing.
    p = [0.0] * (npq + 1)
    q = [0.0] * (npq + 1)

    sqrt_three = sqrt(3.0)

    p[1] = 2.0 * slat
    p[2] = 2.0 * clat

    if npq >= 3:
        p[3] = (
            4.5 * slat * slat
            - 1.5
        )

        q[3] = (
            -3.0
            * clat
            * slat
        )

    if npq >= 4:
        p[4] = (
            3.0
            * sqrt_three
            * clat
            * slat
        )

        q[4] = (
            sqrt_three
            * (
                slat * slat
                - clat * clat
            )
        )

    q[1] = -clat
    q[2] = slat

    radius_ratio = (
        IGRF_REFERENCE_RADIUS_M
        / position.radius_m
    )

    coefficient_index = 1

    degree = 0
    order = 1

    radial_inward_nt = 0.0
    north_nt = 0.0
    east_nt = 0.0

    radial_scale = 0.0
    degree_float = 0.0

    for harmonic_index in range(
        1,
        npq + 1,
    ):
        if degree < order:
            order = 0
            degree += 1

            radial_scale = (
                radius_ratio
                ** (degree + 2)
            )

            degree_float = float(degree)

        order_float = float(order)

        if harmonic_index >= 5:
            if order == degree:
                recurrence_scale = sqrt(
                    1.0
                    - 0.5 / order_float
                )

                previous_index = (
                    harmonic_index
                    - degree
                    - 1
                )

                p[harmonic_index] = (
                    (1.0 + 1.0 / order_float)
                    * recurrence_scale
                    * clat
                    * p[previous_index]
                )

                q[harmonic_index] = (
                    recurrence_scale
                    * (
                        clat
                        * q[previous_index]
                        + slat
                        / order_float
                        * p[previous_index]
                    )
                )

            else:
                recurrence_denominator = sqrt(
                    degree_float * degree_float
                    - order_float * order_float
                )

                previous_degree_scale = (
                    sqrt(
                        (degree_float - 1.0) ** 2
                        - order_float * order_float
                    )
                    / recurrence_denominator
                )

                current_degree_scale = (
                    (2.0 * degree_float - 1.0)
                    / recurrence_denominator
                )

                previous_index = (
                    harmonic_index
                    - degree
                )

                previous_previous_index = (
                    harmonic_index
                    - 2 * degree
                    + 1
                )

                p[harmonic_index] = (
                    (degree_float + 1.0)
                    * (
                        current_degree_scale
                        * slat
                        / degree_float
                        * p[previous_index]
                        - previous_degree_scale
                        / (degree_float - 1.0)
                        * p[previous_previous_index]
                    )
                )

                q[harmonic_index] = (
                    current_degree_scale
                    * (
                        slat
                        * q[previous_index]
                        - clat
                        / degree_float
                        * p[previous_index]
                    )
                    - previous_degree_scale
                    * q[previous_previous_index]
                )

        g_term = (
            radial_scale
            * gh[coefficient_index]
        )

        if order == 0:
            north_nt += (
                g_term
                * q[harmonic_index]
            )

            radial_inward_nt -= (
                g_term
                * p[harmonic_index]
            )

            coefficient_index += 1

        else:
            h_term = (
                radial_scale
                * gh[coefficient_index + 1]
            )

            combined_term = (
                g_term * cl[order]
                + h_term * sl[order]
            )

            north_nt += (
                combined_term
                * q[harmonic_index]
            )

            radial_inward_nt -= (
                combined_term
                * p[harmonic_index]
            )

            if abs(clat) > 1e-12:
                east_nt += (
                    (
                        g_term * sl[order]
                        - h_term * cl[order]
                    )
                    * order_float
                    * p[harmonic_index]
                    / (
                        (degree_float + 1.0)
                        * clat
                    )
                )

            else:
                east_nt += (
                    (
                        g_term * sl[order]
                        - h_term * cl[order]
                    )
                    * q[harmonic_index]
                    * slat
                )

            coefficient_index += 2

        order += 1

    # The validated recurrence internally produces geocentric north and
    # inward-radial components. Convert those into the public spherical
    # convention used by BQRC:
    #
    # colatitudinal = -north
    # radial outward = -radial inward
    return IGRFSphericalField(
        radial_nt=-radial_inward_nt,
        colatitudinal_nt=-north_nt,
        east_nt=east_nt,
    )


def _build_gh_array(
    coefficients: IGRFCoefficientSet,
) -> list[float]:
    """Build one-based Gauss-coefficient ordering for the recurrence."""

    gh = [0.0]

    for degree in range(
        1,
        coefficients.maximum_degree + 1,
    ):
        for order in range(
            0,
            degree + 1,
        ):
            gh.append(
                _coefficient_value(
                    coefficients,
                    CoefficientKind.G,
                    degree,
                    order,
                )
            )

            if order != 0:
                gh.append(
                    _coefficient_value(
                        coefficients,
                        CoefficientKind.H,
                        degree,
                        order,
                    )
                )

    return gh


def _coefficient_value(
    coefficients: IGRFCoefficientSet,
    kind: CoefficientKind,
    degree: int,
    order: int,
) -> float:
    """Return a coefficient value, treating structural h(n,0) as zero."""

    if (
        kind is CoefficientKind.H
        and order == 0
    ):
        return 0.0

    try:
        return coefficients.get(
            kind,
            degree,
            order,
        ).value_nt

    except KeyError as exc:
        raise ValueError(
            "IGRF coefficient set is incomplete: "
            f"{kind.value}({degree}, {order})"
        ) from exc