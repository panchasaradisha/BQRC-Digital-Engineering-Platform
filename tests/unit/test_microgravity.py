"""Unit tests for the BQRC residual-microgravity model."""

from datetime import UTC, datetime

import pytest

from bqrc.environment.microgravity import (
    MicrogravityModel,
    MicrogravityState,
)
from bqrc.environment.orbit import OrbitalState
from bqrc.frames import ReferenceFrame, Vector3


def create_orbital_state() -> OrbitalState:
    """Create a representative low-Earth-orbit state."""

    return OrbitalState(
        timestamp=datetime(
            2027,
            7,
            18,
            10,
            0,
            tzinfo=UTC,
        ),
        position=Vector3(
            x=6_771_000.0,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=4_800.0,
            z=6_000.0,
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )


def test_ideal_free_fall_has_zero_residual_acceleration() -> None:
    """Ideal two-body free fall should have zero residual acceleration."""

    model = MicrogravityModel()

    state = model.evaluate(
        create_orbital_state()
    )

    assert state.residual_acceleration.x == 0.0
    assert state.residual_acceleration.y == 0.0
    assert state.residual_acceleration.z == 0.0

    assert state.magnitude_m_s2 == 0.0
    assert state.magnitude_micro_g == 0.0


def test_microgravity_state_rejects_wrong_frame() -> None:
    """Residual acceleration must currently be represented in ECI."""

    with pytest.raises(
        ValueError,
        match="ECI frame",
    ):
        MicrogravityState(
            residual_acceleration=Vector3(
                x=0.0,
                y=0.0,
                z=0.0,
                unit="m/s^2",
                frame=ReferenceFrame.ECEF,
            )
        )


def test_microgravity_state_rejects_wrong_unit() -> None:
    """Residual acceleration must use SI acceleration units."""

    with pytest.raises(
        ValueError,
        match="m/s\\^2",
    ):
        MicrogravityState(
            residual_acceleration=Vector3(
                x=0.0,
                y=0.0,
                z=0.0,
                unit="m/s",
                frame=ReferenceFrame.ECI,
            )
        )


def test_microgravity_micro_g_conversion() -> None:
    """One micro-g should convert correctly from SI acceleration."""

    state = MicrogravityState(
        residual_acceleration=Vector3(
            x=9.80665e-6,
            y=0.0,
            z=0.0,
            unit="m/s^2",
            frame=ReferenceFrame.ECI,
        )
    )

    assert state.magnitude_micro_g == pytest.approx(
        1.0,
        abs=1e-12,
    )