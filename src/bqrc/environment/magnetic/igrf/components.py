"""Geomagnetic field component transformations and magnetic elements."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, degrees, hypot, isfinite, radians, sin

from bqrc.environment.earth.geodetic import GeodeticPosition
from bqrc.environment.magnetic.igrf.coordinates import (
    IGRFSphericalPosition,
)
from bqrc.environment.magnetic.igrf.field import (
    IGRFSphericalField,
)


@dataclass(frozen=True, slots=True)
class GeodeticMagneticField:
    """Magnetic field in the local geodetic North-East-Down frame.

    Components
    ----------
    north_nt:
        X component, positive toward geodetic north.
    east_nt:
        Y component, positive eastward.
    down_nt:
        Z component, positive downward relative to the local ellipsoid.
    """

    north_nt: float
    east_nt: float
    down_nt: float

    def __post_init__(self) -> None:
        """Require finite magnetic-field components."""

        for value in (
            self.north_nt,
            self.east_nt,
            self.down_nt,
        ):
            if not isfinite(value):
                raise ValueError(
                    "magnetic-field components must be finite"
                )

    @property
    def horizontal_intensity_nt(self) -> float:
        """Return horizontal magnetic intensity H."""

        return hypot(
            self.north_nt,
            self.east_nt,
        )

    @property
    def total_intensity_nt(self) -> float:
        """Return total magnetic intensity F."""

        return hypot(
            self.horizontal_intensity_nt,
            self.down_nt,
        )

    @property
    def declination_deg(self) -> float:
        """Return magnetic declination D in degrees.

        Positive values indicate east of geodetic north.
        """

        return degrees(
            atan2(
                self.east_nt,
                self.north_nt,
            )
        )

    @property
    def inclination_deg(self) -> float:
        """Return magnetic inclination I in degrees.

        Positive values indicate downward field.
        """

        return degrees(
            atan2(
                self.down_nt,
                self.horizontal_intensity_nt,
            )
        )


def spherical_to_geodetic_ned(
    field: IGRFSphericalField,
    geodetic_position: GeodeticPosition,
    spherical_position: IGRFSphericalPosition,
) -> GeodeticMagneticField:
    """Rotate a geocentric spherical field into geodetic NED.

    The geocentric spherical basis differs from the local geodetic basis
    because the WGS-84 ellipsoid normal does not generally point directly
    away from Earth's center.

    Parameters
    ----------
    field:
        Magnetic field expressed as radial, colatitudinal, east components.
    geodetic_position:
        Original WGS-84 geodetic position.
    spherical_position:
        Corresponding geocentric spherical position.

    Returns
    -------
    GeodeticMagneticField
        North, east, and down magnetic components in nanotesla.
    """

    geodetic_latitude = radians(
        geodetic_position.latitude_deg
    )

    geocentric_latitude = (
        spherical_position.geocentric_latitude_rad
    )

    latitude_difference = (
        geodetic_latitude
        - geocentric_latitude
    )

    cos_delta = cos(latitude_difference)
    sin_delta = sin(latitude_difference)

    geocentric_north = -field.colatitudinal_nt
    geocentric_down = -field.radial_nt

    north_nt = (
       geocentric_north * cos_delta
       + geocentric_down * sin_delta
    )

    down_nt = (
        -geocentric_north * sin_delta
        + geocentric_down * cos_delta
    )

    return GeodeticMagneticField(
        north_nt=north_nt,
        east_nt=field.east_nt,
        down_nt=down_nt,
    )