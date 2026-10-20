
"""Spacecraft attitude transformations using unit quaternions.

Quaternions are scalar-first (w, x, y, z).

A body-to-NED quaternion actively rotates vector components
from the spacecraft body frame into the local NED frame.

Rotations are right-handed.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt

from bqrc.frames.reference import ReferenceFrame
from bqrc.frames.vector import Vector3


@dataclass(frozen=True, slots=True)
class Quaternion:
    """Normalized scalar-first attitude quaternion."""

    w: float
    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        components = (self.w, self.x, self.y, self.z)

        if not all(isfinite(component) for component in components):
            raise ValueError("quaternion components must be finite")

        norm = sqrt(sum(component**2 for component in components))

        if not isfinite(norm) or norm == 0.0:
            raise ValueError("quaternion must have a finite nonzero norm")

        object.__setattr__(self, "w", self.w / norm)
        object.__setattr__(self, "x", self.x / norm)
        object.__setattr__(self, "y", self.y / norm)
        object.__setattr__(self, "z", self.z / norm)

    def conjugate(self) -> Quaternion:
        """Return the inverse of this unit quaternion."""

        return Quaternion(
            w=self.w,
            x=-self.x,
            y=-self.y,
            z=-self.z,
        )

    def rotate_components(
        self,
        components: tuple[float, float, float],
    ) -> tuple[float, float, float]:
        """Actively rotate a three-component vector."""

        if len(components) != 3 or not all(
            isfinite(component) for component in components
        ):
            raise ValueError("vector must contain three finite components")

        vx, vy, vz = components
        qx, qy, qz = self.x, self.y, self.z
        qw = self.w

        # Efficient unit-quaternion vector rotation:
        # t = 2 * (q_vector cross v)
        tx = 2.0 * (qy * vz - qz * vy)
        ty = 2.0 * (qz * vx - qx * vz)
        tz = 2.0 * (qx * vy - qy * vx)

        return (
            vx + qw * tx + (qy * tz - qz * ty),
            vy + qw * ty + (qz * tx - qx * tz),
            vz + qw * tz + (qx * ty - qy * tx),
        )


def body_to_ned(
    vector: Vector3,
    attitude: Quaternion,
) -> Vector3:
    """Transform a spacecraft body-frame vector into local NED."""

    if vector.frame != ReferenceFrame.BQRC_BODY:
        raise ValueError("body_to_ned requires a BQRC_BODY vector")

    north, east, down = attitude.rotate_components(
        (vector.x, vector.y, vector.z)
    )

    return Vector3(
        x=north,
        y=east,
        z=down,
        unit=vector.unit,
        frame=ReferenceFrame.LOCAL_NED,
    )


def ned_to_body(
    vector: Vector3,
    attitude: Quaternion,
) -> Vector3:
    """Transform a local NED vector into the spacecraft body frame."""

    if vector.frame != ReferenceFrame.LOCAL_NED:
        raise ValueError("ned_to_body requires a LOCAL_NED vector")

    x, y, z = attitude.conjugate().rotate_components(
        (vector.x, vector.y, vector.z)
    )

    return Vector3(
        x=x,
        y=y,
        z=z,
        unit=vector.unit,
        frame=ReferenceFrame.BQRC_BODY,
    )
