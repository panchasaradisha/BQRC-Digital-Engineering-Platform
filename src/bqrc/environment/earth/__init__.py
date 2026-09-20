"""Public Earth-environment interface for BQRC."""

from bqrc.environment.earth.constants import (
    EARTH_GRAVITATIONAL_PARAMETER_M3_S2,
    WGS84_FIRST_ECCENTRICITY_SQUARED,
    WGS84_FLATTENING,
    WGS84_INVERSE_FLATTENING,
    WGS84_SEMI_MAJOR_AXIS_M,
    WGS84_SEMI_MINOR_AXIS_M,
)
from bqrc.environment.earth.geodetic import (
    GeodeticPosition,
    ecef_to_geodetic,
    geodetic_to_ecef,
)
from bqrc.environment.earth.rotation import (
    earth_rotation_angle,
    julian_date_utc,
)

__all__ = [
    "EARTH_GRAVITATIONAL_PARAMETER_M3_S2",
    "WGS84_FIRST_ECCENTRICITY_SQUARED",
    "WGS84_FLATTENING",
    "WGS84_INVERSE_FLATTENING",
    "WGS84_SEMI_MAJOR_AXIS_M",
    "WGS84_SEMI_MINOR_AXIS_M",
    "earth_rotation_angle",
    "julian_date_utc",
    "GeodeticPosition",
    "ecef_to_geodetic",
    "geodetic_to_ecef",
]