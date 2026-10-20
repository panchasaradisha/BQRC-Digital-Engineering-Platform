
"""Public reference-frame interface for the BQRC platform."""

from __future__ import annotations

from datetime import datetime

from bqrc.frames.reference import ReferenceFrame
from bqrc.frames.vector import Vector3


def eci_to_ecef(
    vector: Vector3,
    timestamp: datetime,
) -> Vector3:
    """Transform an ECI vector to ECEF using the existing implementation."""

    from bqrc.frames.transforms import eci_to_ecef as transform

    return transform(vector, timestamp)


__all__ = [
    "ReferenceFrame",
    "Vector3",
    "eci_to_ecef",
]
