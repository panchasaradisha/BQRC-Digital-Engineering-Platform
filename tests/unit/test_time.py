"""Tests for the BQRC simulation time model."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from bqrc.core.time import SimulationTime


def test_simulation_time_starts_at_epoch() -> None:
    """Zero elapsed time should correspond to the simulation epoch."""
    epoch = datetime(2032, 7, 18, 10, 0, tzinfo=UTC)
    state = SimulationTime(epoch=epoch)

    assert state.current_datetime == epoch


def test_simulation_time_advances_normally() -> None:
    """A 1x simulation should advance one second per wall second."""
    epoch = datetime(2032, 7, 18, 10, 0, tzinfo=UTC)
    state = SimulationTime(epoch=epoch)

    advanced = state.advance(5.0)

    assert advanced.elapsed_seconds == 5.0
    assert advanced.current_datetime == epoch + timedelta(seconds=5)


def test_time_scale_accelerates_simulation() -> None:
    """Simulation time should respect the configured time scale."""
    epoch = datetime(2032, 7, 18, 10, 0, tzinfo=UTC)
    state = SimulationTime(epoch=epoch, time_scale=60.0)

    advanced = state.advance(2.0)

    assert advanced.elapsed_seconds == 120.0


def test_original_time_state_is_not_mutated() -> None:
    """Advancing time should create a new state."""
    epoch = datetime(2032, 7, 18, 10, 0, tzinfo=UTC)
    state = SimulationTime(epoch=epoch)

    advanced = state.advance(1.0)

    assert state.elapsed_seconds == 0.0
    assert advanced.elapsed_seconds == 1.0


def test_naive_epoch_is_rejected() -> None:
    """A timezone-free datetime is ambiguous and must be rejected."""
    naive_epoch = datetime(2032, 7, 18, 10, 0)

    with pytest.raises(ValidationError):
        SimulationTime(epoch=naive_epoch)


def test_non_utc_epoch_is_normalized_to_utc() -> None:
    """Timezone-aware epochs should be normalized to UTC."""
    india_timezone = timezone(timedelta(hours=5, minutes=30))
    epoch = datetime(2032, 7, 18, 15, 30, tzinfo=india_timezone)

    state = SimulationTime(epoch=epoch)

    assert state.epoch == datetime(2032, 7, 18, 10, 0, tzinfo=UTC)


def test_negative_wall_time_is_rejected() -> None:
    """The initial forward-time simulator should reject reverse stepping."""
    epoch = datetime(2032, 7, 18, 10, 0, tzinfo=UTC)
    state = SimulationTime(epoch=epoch)

    with pytest.raises(ValueError):
        state.advance(-1.0)


def test_microsecond_resolution_is_supported() -> None:
    """The core time representation should support microsecond-scale steps."""
    epoch = datetime(2032, 7, 18, 10, 0, tzinfo=UTC)
    state = SimulationTime(epoch=epoch)

    advanced = state.advance(0.000001)

    assert advanced.current_datetime == epoch + timedelta(microseconds=1)