
"""Unit tests for spacecraft attitude transformations."""

from math import cos, pi, sin, sqrt

import pytest

from bqrc.frames import ReferenceFrame, Vector3
from bqrc.frames.attitude import (
    Quaternion,
    body_to_ned,
    ned_to_body,
)


def test_identity_quaternion() -> None:
    attitude = Quaternion(1.0, 0.0, 0.0, 0.0)

    result = attitude.rotate_components((1.0, 2.0, 3.0))

    assert result == pytest.approx((1.0, 2.0, 3.0))


def test_quaternion_normalization() -> None:
    attitude = Quaternion(2.0, 0.0, 0.0, 0.0)

    assert attitude.w == pytest.approx(1.0)
    assert attitude.x == pytest.approx(0.0)


def test_ninety_degree_rotation_about_z() -> None:
    angle = pi / 2.0
    attitude = Quaternion(cos(angle / 2.0), 0.0, 0.0, sin(angle / 2.0))

    result = attitude.rotate_components((1.0, 0.0, 0.0))

    assert result == pytest.approx((0.0, 1.0, 0.0), abs=1e-12)


def test_inverse_rotation() -> None:
    attitude = Quaternion(sqrt(0.5), 0.0, 0.0, sqrt(0.5))
    original = (2.0, 3.0, 4.0)

    rotated = attitude.rotate_components(original)
    restored = attitude.conjugate().rotate_components(rotated)

    assert restored == pytest.approx(original, abs=1e-12)


def test_rotation_preserves_vector_magnitude() -> None:
    attitude = Quaternion(0.5, 0.5, 0.5, 0.5)
    original = (3.0, 4.0, 12.0)

    rotated = attitude.rotate_components(original)

    original_magnitude = sqrt(sum(value**2 for value in original))
    rotated_magnitude = sqrt(sum(value**2 for value in rotated))

    assert rotated_magnitude == pytest.approx(original_magnitude)


def test_body_to_ned_identity() -> None:
    vector = Vector3(
        x=1.0,
        y=2.0,
        z=3.0,
        unit="nT",
        frame=ReferenceFrame.BQRC_BODY,
    )

    result = body_to_ned(vector, Quaternion(1.0, 0.0, 0.0, 0.0))

    assert result.frame == ReferenceFrame.LOCAL_NED
    assert result.unit == "nT"
    assert (result.x, result.y, result.z) == pytest.approx(
        (1.0, 2.0, 3.0)
    )


def test_body_to_ned_and_back() -> None:
    attitude = Quaternion(sqrt(0.5), 0.0, 0.0, sqrt(0.5))

    original = Vector3(
        x=1.0,
        y=2.0,
        z=3.0,
        unit="nT",
        frame=ReferenceFrame.BQRC_BODY,
    )

    ned_vector = body_to_ned(original, attitude)
    restored = ned_to_body(ned_vector, attitude)

    assert restored.frame == ReferenceFrame.BQRC_BODY
    assert restored.unit == original.unit
    assert (restored.x, restored.y, restored.z) == pytest.approx(
        (original.x, original.y, original.z),
        abs=1e-12,
    )


def test_body_to_ned_rejects_wrong_frame() -> None:
    vector = Vector3(
        x=1.0,
        y=0.0,
        z=0.0,
        unit="nT",
        frame=ReferenceFrame.ECI,
    )

    with pytest.raises(ValueError, match="BQRC_BODY"):
        body_to_ned(vector, Quaternion(1.0, 0.0, 0.0, 0.0))


def test_ned_to_body_rejects_wrong_frame() -> None:
    vector = Vector3(
        x=1.0,
        y=0.0,
        z=0.0,
        unit="nT",
        frame=ReferenceFrame.ECEF,
    )

    with pytest.raises(ValueError, match="LOCAL_NED"):
        ned_to_body(vector, Quaternion(1.0, 0.0, 0.0, 0.0))


@pytest.mark.parametrize(
    "components",
    [
        (0.0, 0.0, 0.0, 0.0),
        (float("nan"), 0.0, 0.0, 0.0),
        (float("inf"), 0.0, 0.0, 0.0),
    ],
)
def test_invalid_quaternion_rejected(
    components: tuple[float, float, float, float],
) -> None:
    with pytest.raises(ValueError):
        Quaternion(*components)


def test_nonfinite_vector_rejected() -> None:
    attitude = Quaternion(1.0, 0.0, 0.0, 0.0)

    with pytest.raises(ValueError):
        attitude.rotate_components((float("nan"), 0.0, 0.0))
