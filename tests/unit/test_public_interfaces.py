"""Tests for the public BQRC package interfaces."""

from bqrc.core import (
    DataSource,
    Measurement,
    Parameter,
    ParameterSource,
    QualityFlag,
    SimulationTime,
    Uncertainty,
    UncertaintyType,
)
from bqrc.frames import ReferenceFrame, Vector3


def test_core_public_interface_is_importable() -> None:
    """Core scientific contracts should be available from bqrc.core."""
    assert Measurement is not None
    assert SimulationTime is not None
    assert DataSource is not None
    assert QualityFlag is not None
    assert Uncertainty is not None
    assert UncertaintyType is not None
    assert Parameter is not None
    assert ParameterSource is not None


def test_frames_public_interface_is_importable() -> None:
    """Frame primitives should be available from bqrc.frames."""
    assert ReferenceFrame is not None
    assert Vector3 is not None