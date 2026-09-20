"""Reference-frame transformations for the BQRC platform."""

from datetime import datetime
from math import cos, sin

from bqrc.environment.earth.rotation import earth_rotation_angle
from bqrc.frames.reference import ReferenceFrame
from bqrc.frames.vector import Vector3


def eci_to_ecef(
    vector: Vector3,
    timestamp: datetime,
) -> Vector3:
    """Rotate an ECI vector into the Earth-fixed frame."""

    if vector.frame != ReferenceFrame.ECI:
        raise ValueError("ECI to ECEF transformation requires an ECI vector")

    theta = earth_rotation_angle(timestamp)

    cosine = cos(theta)
    sine = sin(theta)

    return Vector3(
        x=cosine * vector.x + sine * vector.y,
        y=-sine * vector.x + cosine * vector.y,
        z=vector.z,
        unit=vector.unit,
        frame=ReferenceFrame.ECEF,
    )