"""Tests for the BQRC orbital-state contract."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from bqrc.environment.orbit import OrbitalState
from bqrc.frames import ReferenceFrame, Vector3


def test_valid_eci_orbital_state() -> None:
    """A consistent ECI position/velocity state should be accepted."""
    state = OrbitalState(
        timestamp=datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
        position=Vector3(
            x=6_771_000.0,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=7_670.0,
            z=0.0,
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )

    assert state.position.frame == ReferenceFrame.ECI
    assert state.velocity.frame == ReferenceFrame.ECI


def test_mixed_reference_frames_are_rejected() -> None:
    """Position and velocity cannot silently use different frames."""
    with pytest.raises(ValidationError):
        OrbitalState(
            timestamp=datetime(2032, 7, 18, 10, 0, tzinfo=UTC),
            position=Vector3(
                x=6_771_000.0,
                y=0.0,
                z=0.0,
                unit="m",
                frame=ReferenceFrame.ECI,
            ),
            velocity=Vector3(
                x=0.0,
                y=7_670.0,
                z=0.0,
                unit="m/s",
                frame=ReferenceFrame.ECEF,
            ),
        )


def test_naive_orbital_timestamp_is_rejected() -> None:
    """Orbital states must not contain ambiguous timestamps."""
    with pytest.raises(ValidationError):
        OrbitalState(
            timestamp=datetime(2032, 7, 18, 10, 0),
            position=Vector3(
                x=6_771_000.0,
                y=0.0,
                z=0.0,
                unit="m",
                frame=ReferenceFrame.ECI,
            ),
            velocity=Vector3(
                x=0.0,
                y=7_670.0,
                z=0.0,
                unit="m/s",
                frame=ReferenceFrame.ECI,
            ),
        )


def test_orbital_timestamp_is_normalized_to_utc() -> None:
    """Timezone-aware orbital timestamps should be normalized to UTC."""
    india_timezone = timezone(timedelta(hours=5, minutes=30))

    state = OrbitalState(
        timestamp=datetime(2032, 7, 18, 15, 30, tzinfo=india_timezone),
        position=Vector3(
            x=6_771_000.0,
            y=0.0,
            z=0.0,
            unit="m",
            frame=ReferenceFrame.ECI,
        ),
        velocity=Vector3(
            x=0.0,
            y=7_670.0,
            z=0.0,
            unit="m/s",
            frame=ReferenceFrame.ECI,
        ),
    )

    assert state.timestamp == datetime(2032, 7, 18, 10, 0, tzinfo=UTC)