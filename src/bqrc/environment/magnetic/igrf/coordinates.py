"""Coordinate preparation for IGRF geomagnetic evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, degrees, hypot, isfinite, radians, sin

from bqrc.environment.earth import WGS84_SEMI_MAJOR_AXIS_M
from bqrc.environment.earth.geodetic import GeodeticPosition

IGRF_REFERENCE_RADIUS_M = 6_371_200.0


@dataclass(frozen=True, slots=True)
class IGRFSphericalPosition:
    """Geocentric spherical position used by the IGRF field equations.

    Parameters
    ----------
    radius_m:
        Distance from Earth's center in metres.
    geocentric_colatitude_rad:
        Angle measured from the positive geographic Z-axis in radians.
    longitude_rad:
        Earth-fixed longitude in radians.
    """

    radius_m: float
    geocentric_colatitude_rad: float
    longitude_rad: float

    def __post_init__(self) -> None:
        """Validate the spherical coordinate representation."""

        if not isfinite(self.radius_m):
            raise ValueError("radius must be finite")

        if self.radius_m <= 0.0:
            raise ValueError("radius must be positive")

        if not isfinite(self.geocentric_colatitude_rad):
            raise ValueError("geocentric colatitude must be finite")

        if not 0.0 <= self.geocentric_colatitude_rad <= radians(180.0):
            raise ValueError(
                "geocentric colatitude must be within 0 to pi radians"
            )

        if not isfinite(self.longitude_rad):
            raise ValueError("longitude must be finite")

        if not -radians(180.0) <= self.longitude_rad <= radians(180.0):
            raise ValueError(
                "longitude must be within -pi to pi radians"
            )

    @property
    def geocentric_latitude_rad(self) -> float:
        """Return geocentric latitude in radians."""

        return radians(90.0) - self.geocentric_colatitude_rad

    @property
    def geocentric_latitude_deg(self) -> float:
        """Return geocentric latitude in degrees."""

        return degrees(self.geocentric_latitude_rad)

    @property
    def longitude_deg(self) -> float:
        """Return longitude in degrees."""

        return degrees(self.longitude_rad)

    @property
    def normalized_radius(self) -> float:
        """Return radius normalized by the IGRF reference radius."""

        return self.radius_m / IGRF_REFERENCE_RADIUS_M


def geodetic_to_igrf_spherical(
    position: GeodeticPosition,
) -> IGRFSphericalPosition:
    """Convert WGS-84 geodetic position to IGRF spherical coordinates.

    The conversion deliberately uses the existing BQRC WGS-84 Earth
    geometry rather than treating geodetic latitude as geocentric latitude.

    Parameters
    ----------
    position:
        WGS-84 geodetic latitude, longitude, and ellipsoidal altitude.

    Returns
    -------
    IGRFSphericalPosition
        Geocentric radius, colatitude, and longitude.
    """

    latitude_rad = radians(position.latitude_deg)
    longitude_rad = radians(position.longitude_deg)

    flattening = 1.0 / 298.257223563
    eccentricity_squared = flattening * (2.0 - flattening)

    sin_latitude = sin(latitude_rad)
    cos_latitude = cos(latitude_rad)

    prime_vertical_radius = WGS84_SEMI_MAJOR_AXIS_M / (
        1.0 - eccentricity_squared * sin_latitude**2
    ) ** 0.5

    x = (
        prime_vertical_radius + position.altitude_m
    ) * cos_latitude * cos(longitude_rad)

    y = (
        prime_vertical_radius + position.altitude_m
    ) * cos_latitude * sin(longitude_rad)

    z = (
        prime_vertical_radius
        * (1.0 - eccentricity_squared)
        + position.altitude_m
    ) * sin_latitude

    horizontal_radius = hypot(x, y)
    radius_m = hypot(horizontal_radius, z)

    geocentric_latitude_rad = atan2(
        z,
        horizontal_radius,
    )

    geocentric_colatitude_rad = (
        radians(90.0) - geocentric_latitude_rad
    )

    return IGRFSphericalPosition(
        radius_m=radius_m,
        geocentric_colatitude_rad=geocentric_colatitude_rad,
        longitude_rad=longitude_rad,
    )