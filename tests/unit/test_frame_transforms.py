"""Tests for BQRC reference-frame transformations."""

from datetime import UTC, datetime
from math import isclose

import pytest

from bqrc.frames import ReferenceFrame, Vector3, eci_to_ecef


def test_eci_to_ecef_preserves_vector_magnitude() -> None:
    """A pure rotation must preserve vector magnitude."""

    vector = Vector3(
        x=6_771_000.0,
        y=1_000_000.0,
        z=500_000.0,
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    timestamp = datetime(
        2032,
        7,
        18,
        10,
        0,
        tzinfo=UTC,
    )

    transformed = eci_to_ecef(vector, timestamp)

    assert isclose(
        transformed.magnitude,
        vector.magnitude,
        rel_tol=1e-12,
    )


def test_eci_to_ecef_changes_frame_identity() -> None:
    """Transformed vectors should explicitly identify as ECEF."""

    vector = Vector3(
        x=6_771_000.0,
        y=0.0,
        z=0.0,
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    transformed = eci_to_ecef(
        vector,
        datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
    )

    assert transformed.frame == ReferenceFrame.ECEF


def test_eci_to_ecef_preserves_units() -> None:
    """Frame rotation should not change the physical vector unit."""

    vector = Vector3(
        x=1.0,
        y=2.0,
        z=3.0,
        unit="T",
        frame=ReferenceFrame.ECI,
    )

    transformed = eci_to_ecef(
        vector,
        datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
    )

    assert transformed.unit == "T"


def test_eci_to_ecef_preserves_z_component() -> None:
    """The V1 Earth rotation occurs about the Z-axis."""

    vector = Vector3(
        x=1.0,
        y=2.0,
        z=3.0,
        unit="m",
        frame=ReferenceFrame.ECI,
    )

    transformed = eci_to_ecef(
        vector,
        datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
    )

    assert transformed.z == vector.z


def test_eci_to_ecef_rejects_wrong_input_frame() -> None:
    """ECEF input must not silently pass through an ECI transformation."""

    vector = Vector3(
        x=1.0,
        y=2.0,
        z=3.0,
        unit="m",
        frame=ReferenceFrame.ECEF,
    )

    with pytest.raises(ValueError):
        eci_to_ecef(
            vector,
            datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
        )