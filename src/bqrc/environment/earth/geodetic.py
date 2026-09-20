"""Geodetic coordinate models and conversions for BQRC."""

from math import atan2, cos, degrees, hypot, radians, sin

from pydantic import BaseModel, field_validator

from bqrc.environment.earth.constants import (
    WGS84_FIRST_ECCENTRICITY_SQUARED,
    WGS84_SEMI_MAJOR_AXIS_M,
)
from bqrc.frames import ReferenceFrame, Vector3


class GeodeticPosition(BaseModel):
    """WGS-84 geodetic position."""

    latitude_deg: float
    longitude_deg: float
    altitude_m: float

    @field_validator("latitude_deg")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        """Require a physically valid geodetic latitude."""

        if not -90.0 <= value <= 90.0:
            raise ValueError("latitude must be between -90 and 90 degrees")

        return value

    @field_validator("longitude_deg")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        """Require normalized longitude."""

        if not -180.0 <= value <= 180.0:
            raise ValueError("longitude must be between -180 and 180 degrees")

        return value

def geodetic_to_ecef(position: GeodeticPosition) -> Vector3:
    """Convert WGS-84 geodetic coordinates to an ECEF position."""

    latitude = radians(position.latitude_deg)
    longitude = radians(position.longitude_deg)

    sin_latitude = sin(latitude)
    cos_latitude = cos(latitude)

    sin_longitude = sin(longitude)
    cos_longitude = cos(longitude)

    prime_vertical_radius = (
        WGS84_SEMI_MAJOR_AXIS_M
        / (
            1.0
            - WGS84_FIRST_ECCENTRICITY_SQUARED
            * sin_latitude**2
        )
        ** 0.5
    )

    x = (
        prime_vertical_radius + position.altitude_m
    ) * cos_latitude * cos_longitude

    y = (
        prime_vertical_radius + position.altitude_m
    ) * cos_latitude * sin_longitude

    z = (
        prime_vertical_radius
        * (1.0 - WGS84_FIRST_ECCENTRICITY_SQUARED)
        + position.altitude_m
    ) * sin_latitude

    return Vector3(
        x=x,
        y=y,
        z=z,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

def ecef_to_geodetic(
    position: Vector3,
    *,
    tolerance_rad: float = 1e-12,
    max_iterations: int = 20,
) -> GeodeticPosition:
    """Convert an ECEF position to WGS-84 geodetic coordinates."""

    if position.frame != ReferenceFrame.ECEF:
        raise ValueError("ECEF to geodetic conversion requires an ECEF vector")

    if position.unit != "m":
        raise ValueError("ECEF position must use metres")

    x = position.x
    y = position.y
    z = position.z

    horizontal_distance = hypot(x, y)

    if horizontal_distance == 0.0 and z == 0.0:
        raise ValueError("geodetic position is undefined at Earth's centre")

    longitude = atan2(y, x)

    if horizontal_distance == 0.0:
        latitude = (
            90.0 if z > 0.0 else -90.0
        )

        polar_radius = (
            WGS84_SEMI_MAJOR_AXIS_M
            * (
                1.0
                - WGS84_FIRST_ECCENTRICITY_SQUARED
            )
            ** 0.5
        )

        return GeodeticPosition(
            latitude_deg=latitude,
            longitude_deg=0.0,
            altitude_m=abs(z) - polar_radius,
        )

    latitude = atan2(
        z,
        horizontal_distance
        * (1.0 - WGS84_FIRST_ECCENTRICITY_SQUARED),
    )

    for _ in range(max_iterations):
        sin_latitude = sin(latitude)

        prime_vertical_radius = (
            WGS84_SEMI_MAJOR_AXIS_M
            / (
                1.0
                - WGS84_FIRST_ECCENTRICITY_SQUARED
                * sin_latitude**2
            )
            ** 0.5
        )

        altitude = (
            horizontal_distance / cos(latitude)
            - prime_vertical_radius
        )

        new_latitude = atan2(
            z,
            horizontal_distance
            * (
                1.0
                - (
                    WGS84_FIRST_ECCENTRICITY_SQUARED
                    * prime_vertical_radius
                    / (
                        prime_vertical_radius
                        + altitude
                    )
                )
            ),
        )

        if abs(new_latitude - latitude) < tolerance_rad:
            latitude = new_latitude
            break

        latitude = new_latitude
    else:
        raise RuntimeError("ECEF to geodetic conversion did not converge")

    sin_latitude = sin(latitude)

    prime_vertical_radius = (
        WGS84_SEMI_MAJOR_AXIS_M
        / (
            1.0
            - WGS84_FIRST_ECCENTRICITY_SQUARED
            * sin_latitude**2
        )
        ** 0.5
    )

    altitude = (
        horizontal_distance / cos(latitude)
        - prime_vertical_radius
    )

    return GeodeticPosition(
        latitude_deg=degrees(latitude),
        longitude_deg=degrees(longitude),
        altitude_m=altitude,
    )