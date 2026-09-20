"""Tests for BQRC reference-frame definitions."""

from bqrc.frames.reference import ReferenceFrame


def test_reference_frame_serialization() -> None:
    """Reference frames should expose stable serialized identifiers."""
    assert ReferenceFrame.ECI == "eci"
    assert ReferenceFrame.ECEF == "ecef"
    assert ReferenceFrame.BQRC_BODY == "bqrc_body"
    assert ReferenceFrame.NV_SENSOR == "nv_sensor"