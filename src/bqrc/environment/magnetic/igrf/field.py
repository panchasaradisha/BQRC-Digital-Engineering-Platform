"""IGRF spherical-harmonic magnetic-field evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, isfinite, sin

from bqrc.environment.magnetic.igrf.coefficients import (
    CoefficientKind,
    IGRFCoefficientSet,
)
from bqrc.environment.magnetic.igrf.coordinates import (
    IGRF_REFERENCE_RADIUS_M,
    IGRFSphericalPosition,
)
from bqrc.environment.magnetic.igrf.legendre import (
    associated_legendre,
)
from bqrc.environment.magnetic.igrf.normalization import (
    apply_schmidt_normalization,
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
    """Evaluate an IGRF coefficient set at a geocentric position.

    Parameters
    ----------
    coefficients:
        Complete IGRF coefficient set for the requested epoch.
    position:
        Geocentric spherical position.

    Returns
    -------
    IGRFSphericalField
        Radial, colatitudinal, and eastward magnetic-field components
        in nanotesla.

    Notes
    -----
    This evaluator operates in geocentric spherical coordinates.

    Conversion to geodetic north/east/down components is deliberately
    performed by a separate transformation layer.
    """

    maximum_degree = coefficients.maximum_degree

    raw_legendre = associated_legendre(
        maximum_degree=maximum_degree,
        colatitude_rad=position.geocentric_colatitude_rad,
    )

    legendre = apply_schmidt_normalization(
        raw_legendre
    )

   
    theta = position.geocentric_colatitude_rad
    longitude = position.longitude_rad

    sin_theta = sin(theta)

    radial_nt = 0.0
    colatitudinal_nt = 0.0
    east_nt = 0.0

    radius_ratio = (
        IGRF_REFERENCE_RADIUS_M
        / position.radius_m
    )

    for degree in range(
        1,
        maximum_degree + 1,
    ):
        radial_scale = radius_ratio ** (
            degree + 2
        )

        for order in range(
            0,
            degree + 1,
        ):
            g = _coefficient_value(
                coefficients,
                CoefficientKind.G,
                degree,
                order,
            )

            h = _coefficient_value(
                coefficients,
                CoefficientKind.H,
                degree,
                order,
            )

            angle = order * longitude

            cos_m_longitude = cos(angle)
            sin_m_longitude = sin(angle)

            harmonic = (
                g * cos_m_longitude
                + h * sin_m_longitude
            )

            p_nm = legendre.get(
                degree,
                order,
            )

            dp_nm = legendre.derivative(
                degree,
                order,
            )

            radial_nt += (
                (degree + 1)
                * radial_scale
                * harmonic
                * p_nm
            )

            colatitudinal_nt -= (
                radial_scale
                * harmonic
                * dp_nm
            )

            if order != 0:
                azimuthal_numerator = (
                    order
                    * (
                        g * sin_m_longitude
                        - h * cos_m_longitude
                    )
                    * p_nm
                )

                if abs(sin_theta) > 1e-12:
                    east_nt += (
                        radial_scale
                        * azimuthal_numerator
                        / sin_theta
                    )

    return IGRFSphericalField(
        radial_nt=radial_nt,
        colatitudinal_nt=colatitudinal_nt,
        east_nt=east_nt,
    )


def _coefficient_value(
    coefficients: IGRFCoefficientSet,
    kind: CoefficientKind,
    degree: int,
    order: int,
) -> float:
    """Return a coefficient value, treating structural h(n,0) as zero."""

    if kind is CoefficientKind.H and order == 0:
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