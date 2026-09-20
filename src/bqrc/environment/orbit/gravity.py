"""Two-body gravitational acceleration model for BQRC."""

from bqrc.environment.earth import EARTH_GRAVITATIONAL_PARAMETER_M3_S2
from bqrc.frames import ReferenceFrame, Vector3


def two_body_acceleration(position: Vector3) -> Vector3:
    """Calculate Earth two-body gravitational acceleration."""

    if position.unit != "m":
        raise ValueError("two-body position must use metres")

    if position.frame != ReferenceFrame.ECI:
        raise ValueError("two-body gravity currently requires the ECI frame")

    radius = position.magnitude

    if radius == 0.0:
        raise ValueError("position magnitude cannot be zero")

    factor = -EARTH_GRAVITATIONAL_PARAMETER_M3_S2 / radius**3

    return Vector3(
        x=factor * position.x,
        y=factor * position.y,
        z=factor * position.z,
        unit="m/s^2",
        frame=position.frame,
    )