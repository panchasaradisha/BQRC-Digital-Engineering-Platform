"""Tests for BQRC three-dimensional vector primitives."""

from math import isclose

from bqrc.frames.reference import ReferenceFrame
from bqrc.frames.vector import Vector3


def test_vector_preserves_reference_frame() -> None:
    """A vector should retain its reference-frame context."""
    vector = Vector3(
        x=1.0,
        y=2.0,
        z=3.0,
        unit="T",
        frame=ReferenceFrame.NV_SENSOR,
    )

    assert vector.frame == ReferenceFrame.NV_SENSOR


def test_vector_preserves_unit() -> None:
    """A vector should retain its physical unit."""
    vector = Vector3(
        x=1.0,
        y=2.0,
        z=3.0,
        unit="m/s^2",
        frame=ReferenceFrame.IMU_SENSOR,
    )

    assert vector.unit == "m/s^2"


def test_vector_magnitude() -> None:
    """Vector magnitude should follow the Euclidean norm."""
    vector = Vector3(
        x=3.0,
        y=4.0,
        z=12.0,
        unit="T",
        frame=ReferenceFrame.ECEF,
    )

    assert isclose(vector.magnitude, 13.0)


def test_zero_vector_has_zero_magnitude() -> None:
    """A zero vector should have zero magnitude."""
    vector = Vector3(
        x=0.0,
        y=0.0,
        z=0.0,
        unit="m/s^2",
        frame=ReferenceFrame.BQRC_BODY,
    )

    assert vector.magnitude == 0.0